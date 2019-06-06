"""
Edited version of coref.py

Writes the features for pleonastic pronouns to a csv
"""

import io
import os
import re
import sys
import tempfile
import functools
import subprocess
from collections import defaultdict
from itertools import islice
from bisect import bisect
from getopt import gnu_getopt
from datetime import datetime
from glob import glob
from html import escape
from lxml import etree
from jinja2 import Template
import colorama
import ansi2html
import pandas as pd


from pleonastic.feature_dict import *
from development.old_pleonastic import *


STOPWORDS = (
		# List of Dutch Stop words (http://www.ranks.nl/stopwords/dutch)
		'aan af al als bij dan dat de die dit een en er had heb hem het hij '
		'hoe hun ik in is je kan me men met mij nog nu of ons ook te tot uit '
		'van was wat we wel wij zal ze zei zij zo zou '
		# titles
		'dr. drs. ing. ir. mr. lic. prof. mevr. mw. bacc. kand. dr.h.c. ds. '
		'bc. dr drs ing ir mr lic prof mevr mw bacc kand dr.h.c ds bc '
		'mevrouw meneer heer doctor professor').split()

VERBOSE = False
DEBUGFILE = sys.stdout

class Mention:
	"""A span referring to an entity.

	:ivar clusterid: cluster (entity) ID this mention is in.
	:ivar prohibit: do not link this mention to these mention IDs.
	:ivar filter: if True, do not include this mention in output.
	:ivar relaxedtokens: list of tokens without postnominal modifiers.
	:ivar head: node corresponding to head word.
	:ivar type: one of ('name', 'noun', 'pronoun')
	:ivar mainmod: list of string tokens that modify the head noun
	:ivar features: dict with following keys and possible values:
		:number: ('sg', 'pl', both, None); None means unknown.
		:gender: ('m', 'f', 'n', 'fm', 'nm', 'fn', None)
		:human: (0, 1, None)
		:person: (1, 2, 3, None); only for pronouns.
	:ivar antecedent: mention ID of antecedent of this mention, or None.
	:ivar sieve: name of sieve responsible for linking this mention, or None.
	"""
	def __init__(self, mentionid, sentno, tree, node, begin, end, headidx,
			tokens, ngdata, gadata):
		"""Create a new mention.

		:param mentionid: unique integer for this mention.
		:param sentno: global sentence index (ignoring paragraphs, 0-indexed)
			this mention occurs in.
		:param tree: lxml.ElementTree with Alpino XML parse tree of sentence
		:param node: node in tree covering this mention
		:param begin: start index in sentence of mention (0-indexed)
		:param end: end index in sentence of mention (exclusive)
		:param headidx: index in sentence of head word of mention
		:param tokens: list of tokens in mention as strings
		:param ngdata: look up table with number and gender data
		:param gadata:: look up table with gender and animacy data
		"""
		self.id = mentionid
		self.sentno = sentno
		self.node = node
		self.begin = begin
		self.end = end
		self.tokens = tokens
		self.clusterid = mentionid
		self.prohibit = set()
		self.filter = False
		self.antecedent = self.sieve = None
		removeids = {n for rng in
				(range(int(child.get('begin')), int(child.get('end')))
				for child in node.findall('.//node[@rel="app"]')
						+ node.findall('.//node[@rel="mod"]'))
					for n in rng if n > headidx}
		# without mod/app constituents after head
		self.relaxedtokens = [token.get('word') for token
				in sorted((token for token in tree.findall('.//node[@word]')
					if begin <= int(token.get('begin')) < end
					and int(token.get('begin')) not in removeids),
				key=lambda x: int(x.get('begin')))]
		if not self.relaxedtokens:
			self.relaxedtokens = self.tokens
		self.head = (node.find('.//node[@begin="%d"]' % headidx)
				if len(node) else node)
		if node.get('pdtype') == 'pron' or node.get('vwtype') == 'bez':
			self.type = 'pronoun'
		elif (self.head.get('ntype') == 'eigen'
				or self.head.get('pt') == 'spec'):
			self.type = 'name'
		else:
			self.type = 'noun'
		self.mainmod = [a.get('word') for a
				in (node.findall('.//node[@word]') if len(node) else (node, ))
				if a.get('rel') == 'mod' or a.get('pt') in ('adj', 'n')
				and begin <= int(a.get('begin')) < end]
		self.features = {
				'human': None, 'gender': None,
				'number': None, 'person': None}
		self._detectfeatures(ngdata, gadata)

	def _detectfeatures(self, ngdata, gadata):
		"""Set features for this mention based on linguistic features or
		external dataset."""
		self.features['number'] = self.head.get(
				'rnum', self.head.get('num'))
		if self.features['number'] is None and 'getal' in self.head.keys():
			self.features['number'] = {
					'ev': 'sg', 'mv': 'pl', 'getal': 'both'
					}[self.head.get('getal')]

		if self.head.get('genus') in ('masc', 'fem'):
			self.features['gender'] = self.head.get('genus')[0]
			self.features['human'] = 1
		elif (self.head.get('genus') == 'onz'
				or self.head.get('gen') == 'het'):
			self.features['gender'] = 'n'
			self.features['human'] = 0

		if self.type == 'pronoun':  # pronouns: rules
			if self.head.get('persoon')[0] in '123':
				self.features['person'] = self.head.get('persoon')[0]
			if self.features['person'] in ('1', '2'):
				self.features['gender'] = 'fm'
				self.features['human'] = 1
			elif self.head.get('persoon') == '3p':
				self.features['gender'] = 'fm'
				self.features['human'] = 1
			elif self.head.get('persoon') == '3o':
				self.features['gender'] = 'n'
				self.features['human'] = 0
			if self.head.get('lemma') == 'haar':
				self.features['gender'] = 'fn'
			elif self.head.get('lemma') == 'zijn':
				self.features['gender'] = 'nm'
			elif (self.head.get('lemma') in ('hun', 'hen')
					and self.head.get('vwtype') == 'pers'):
				self.features['human'] = 1
		# nouns: use lexical resource
		elif self.head.get('lemma', '').replace('_', '') in gadata:
			gender, animacy = gadata[self.head.get(
					'lemma', '').replace('_', '')]
			if animacy == 'human':
				self.features['human'] = 1
				self.features['gender'] = 'fm'
				if gender in ('m', 'f'):
					self.features['gender'] = gender
			else:
				self.features['human'] = 0
				self.features['gender'] = 'n'
		else:  # names: dict
			if self.head.get('neclass') == 'PER':
				self.features['human'] = 1
				self.features['gender'] = 'fm'
			elif self.head.get('neclass') is not None:
				self.features['human'] = 0
				self.features['gender'] = 'n'
			result = nglookup(' '.join(self.tokens), ngdata)
			if result:
				self.features.update(result)
			elif (self.head.get('neclass') == 'PER'
					and self.tokens[0] not in STOPWORDS):
				# Assume first token is first name.
				self.features.update(nglookup(self.tokens[0], ngdata))

	def featrepr(self, extended=False):
		"""String representations of features."""
		result = ' '.join('%s=%s' % (a, '?' if b is None else b)
					for a, b in self.features.items())
		result += ' inquote=%d' % int(self.head.get('quotelabel') == 'I')
		if extended:
			result += ' neclass=%s head=%s' % (
					self.head.get('neclass'), self.head.get('word'))
		return result

	def __str__(self):
		return "'%s'" % color(' '.join(self.tokens), 'green')

	def __repr__(self):
		return "Mention('%s', ...)" % ' '.join(self.tokens)


class Quotation:
	def __init__(self, start, end, sentno, parno, text, sentbounds):
		self.start, self.end = start, end
		self.sentno = sentno
		self.parno = parno
		self.sentbounds = sentbounds
		self.speaker = None
		self.addressee = None
		self.mentions = []
		self.text = text


def getmentions(gold, trees, ngdata, gadata):
	"""Collect mentions."""
	debug(color('mention detection', 'yellow'))
	mentionlist = list()
	for sentno, (_, tree) in enumerate(trees):
		candidates = []
		candidates.extend(tree.xpath('.//node[@cat="np"]'))
		# candidates.extend(tree.xpath(
		# 		'.//node[@cat="conj"]/node[@cat="np" or @pt="n"]/..'))
		candidates.extend(tree.xpath(
				'.//node[@cat="mwu"]/node[@pt="spec"]/..'))
		candidates.extend(tree.xpath('.//node[@pt="n"]'
				'[@ntype="eigen" or @rel="su" or @rel="obj1" or @rel="body"]'))
		candidates.extend(tree.xpath(
				'.//node[@pdtype="pron" or @vwtype="bez"]'))
		candidates.extend(tree.xpath(
				'.//node[@pt="num" and @rel!="det" and @rel!="mod"]'))
		candidates.extend(tree.xpath('.//node[@pt="det" and @rel!="det"]'))
		covered = set()
		for candidate in candidates:
			mentiondict = considermention(gold, candidate, tree, sentno, covered,
					ngdata, gadata)
			if mentiondict is not None:
				mentionlist.append(mentiondict)
	return mentionlist


def considermention(gold, node, tree, sentno, covered, ngdata, gadata):
	"""Decide whether a candidate mention should be added."""
	if len(node) == 0 and 'word' not in node.keys():
		return
	headidx = getheadidx(node)
	indices = sorted(int(token.get('begin')) for token
			in (node.findall('.//node[@word]') if len(node) else [node]))
	a, b = min(indices), max(indices) + 1
	# allow comma when preceded by conjunct, adjective, or location.
	for punct in tree.getroot().findall('./node/node[@pt="let"]'):
		i = int(punct.get('begin'))
		if (a <= i < b
			and (node.find('.//node[@begin="%d"][@rel="cnj"]' % (i - 1))
					is not None
				or node.find('.//node[@begin="%d"][@pt="adj"]' % (i - 1))
					is not None
				or node.find('.//node[@begin="%d"][@neclass="LOC"]' % (i - 1))
					is not None)):
			indices.append(i)
	indices.sort()
	# if span is interrupted by a discontinuity from other words or
	# punctuation, cut off mention before it; avoids weird long mentions.
	if indices != list(range(a, b)):
		b = min(n for n in range(a, b) if n not in indices)
		if headidx > b:
			headidx = max(int(a.get('begin')) for a
					in node.findall('.//node[@word]')
					if int(a.get('begin')) < b)
	# Relative clauses: [de man] [die] ik eerder had gezien.
	relpronoun = node.find('./node[@cat="rel"]/node[@wh="rel"]')
	if relpronoun is not None and int(relpronoun.get('begin')) < b:
		b = int(relpronoun.get('begin'))
		if headidx > b:
			headidx = max(int(a.get('begin')) for a
					in node.findall('.//node[@word]')
					if int(a.get('begin')) < b)
	# Appositives: "[Jan], [de schilder]"
	# but: "[acteur John Cleese]"
	if (len(node) > 1 and node[1].get('rel') == 'app'
			and node[1].get('ntype') != 'eigen'
			and node[1].get('pt') != 'spec'):
		node = node[0]
		b = int(node.get('end'))
	tokens = gettokens(tree, a, b)
	# Trim punctuation
	if tokens[0] in ',\'"()':
		tokens = tokens[1:]
		a += 1
	if tokens[-1] in ',\'"()':
		tokens = tokens[:-1]
		b -= 1
	head = (node.find('.//node[@begin="%d"]' % headidx)
			if len(node) else node)
	# various
	if head.get('lemma') in ('aantal', 'keer', 'toekomst', 'manier'):
		return
		
	mentiondict = pleonasticpronoun(node, sentno, gold, tree)
	
	return mentiondict

########################################################################

def pleonasticpronoun(node, sentno, gold, tree):
	if node.get("lemma") == "het":
		f_dict = featureDict(node, tree)
		pleonastic = True
		for i in gold:
			if (int(sentno), int(node.attrib["begin"]), 
				int(node.attrib["end"]), node.attrib["word"]) in gold[i]:
					pleonastic = False
					#if len(gold[i]) > 1:
					#	pleonastic = False
		if pleonastic == False:
			f_dict["pleonastic"] = 0
		else:
			f_dict["pleonastic"] = 1
	
		if oldpleonasticpronoun(node) == True:
			f_dict["old"] = 1
		else:
			f_dict["old"] = 0

		return f_dict

########################################################################

def resolvecoreference(gold, trees, ngdata, gadata, mentions=None):
	"""Get mentions and apply coreference sieves."""
	if mentions is None:
		mentionlist = getmentions(gold, trees, ngdata, gadata)
	return mentionlist


def parsesentid(path):
	"""Given a filename, return tuple with numeric components for sorting."""
	filename = os.path.basename(path)
	x = tuple(map(int, re.findall('[0-9]+', filename.rsplit('.', 1)[0])))
	if len(x) == 1:
		return 0, x[0]
	elif len(x) == 2:
		return x
	else:
		raise ValueError('expected sentence ID of the form sentno.xml '
				'or parno-sentno.xml. Got: %s' % filename)


def gettokens(tree, begin, end):
	"""Return tokens of span in tree as list of strings."""
	return [token.get('word') for token
			in sorted((token for token
				in tree.findall('.//node[@word]')
				if begin <= int(token.get('begin')) < end),
			key=lambda x: int(x.get('begin')))]


def getheadidx(node):
	"""Return head word index given constituent."""
	if len(node) == 0:
		return int(node.get('begin'))
	for child in node:
		if child.get('rel') in ('hd', 'whd', 'rhd', 'crd', 'cmp'):
			return getheadidx(child)
	# default to last child as head
	return getheadidx(node[-1])


def prohibited(mention1, mention2, clusters):
	"""Check if there is a constraint against merging mention1 and mention2."""
	if (mention1.clusterid == mention2.clusterid
			or not clusters[mention1.clusterid].isdisjoint(mention2.prohibit)
			or not clusters[mention2.clusterid].isdisjoint(mention1.prohibit)):
		return True
	return False


def merge(mention1, mention2, sieve, mentions, clusters):
	"""Merge cluster1 & cluster2, delete cluster with highest ID."""
	if mention1 is mention2:
		raise ValueError
	if mention1.clusterid == mention2.clusterid:
		return
	if mention1.clusterid > mention2.clusterid:
		mention1, mention2 = mention2, mention1
	mergefeatures(mention1, mention2)
	mention1.prohibit.update(mention2.prohibit)
	cluster1 = clusters[mention1.clusterid]
	cluster2 = clusters[mention2.clusterid]
	clusters[mention2.clusterid] = None
	cluster1.update(cluster2)
	for m in cluster2:
		mentions[m].clusterid = mention1.clusterid
	mention2.antecedent = mention1.id
	mention2.sieve = sieve
	debug('Linked  %d %d %s %s\n\t%d %d %s %s' % (
			mention1.sentno, mention1.begin, mention1, mention1.featrepr(),
			mention2.sentno, mention2.begin, mention2, mention2.featrepr()))


def mergefeatures(mention, other):
	"""Update the features of the first mention with those of second.
	In case one is more specific than the other, keep specific value.
	In case of conflict, keep both values."""
	for key in mention.features:
		if (key == 'person' or mention.features[key] == other.features[key]
				or other.features[key] in (None, 'both')):
			pass
		elif mention.features[key] in (None, 'both'):
			mention.features[key] = other.features[key]
		elif key == 'human':
			mention.features[key] = None
		elif key == 'number':
			mention.features[key] = 'both'
		elif key == 'gender':
			if other.features[key] in mention.features[key]:  # (fm, m) => m
				mention.features[key] = other.features[key]
			elif mention.features[key] in other.features[key]:  # (m, fm) => m
				pass
			elif (len(other.features[key]) == len(mention.features[key])
					== 1):  # (f, m) => fm
				mention.features[key] = ''.join(sorted((
						other.features[key], mention.features[key])))
			else:  # e.g. (fm, n) => unknown
				mention.features[key] = None
	other.features.update((a, b) for a, b in mention.features.items()
			if a != 'person')


def compatible(mention, other):
	"""Return True if all features are compatible."""
	return all(
			mention.features[key] == other.features[key]
			or None in (mention.features[key], other.features[key])
			or (key == 'gender'
				and 'fm' in (mention.features[key], other.features[key])
				and 'n' not in (mention.features[key], other.features[key]))
			or (key == 'gender'
				and 'nm' in (mention.features[key], other.features[key])
				and 'f' not in (mention.features[key], other.features[key]))
			or (key == 'gender'
				and 'fn' in (mention.features[key], other.features[key])
				and 'm' not in (mention.features[key], other.features[key]))
			or (key == 'number'
				and 'both' in (mention.features[key], other.features[key]))
			for key in mention.features)


def iwithini(mention, other):
	"""Check whether spans overlap."""
	return (mention.sentno == other.sentno
			and (mention.begin <= other.begin <= mention.end
				or mention.begin <= other.end <= mention.end
				or other.begin <= mention.begin <= other.end
				or other.begin <= mention.end <= other.end))


def checkconstraints(mention, clusters):
	"""Block coreference for first mention of indefinite NP or bare plural."""
	if len(clusters[mention.clusterid]) > 1:
		return True
	# indefinite pronoun/article
	if (mention.node.get('cat') == 'np'
			and (mention.node[0].get('def') == 'indef'
				or mention.node[0].get('vwtype') == 'onbep')):
		return False
	# bare plural
	if (mention.node.get('ntype') == 'soort'
			and mention.features['number'] == 'pl'):
		return False
	return True


def sortmentions(mentions):
	"""Sort mentions by start position, then from small to large span length.
	"""
	return sorted(mentions,
			key=lambda x: (x.sentno, x.begin, x.end))


def representativementions(mentions, clusters):
	"""Yield the representative mention (here the first) for each cluster."""
	for cluster in clusters:
		if cluster is not None:
			n = min(cluster)
			yield n, mentions[n]


def sameclause(node1, node2):
	"""Return true if nodes are arguments in the same clause."""
	clausecats = ('smain', 'ssub', 'sv1', 'inf')
	index = node1.get('index')
	while (node1 is not None and node1.get('cat') not in clausecats):
		node1 = node1.getparent()
	while node2 is not None and node2.get('cat') not in clausecats:
		node2 = node2.getparent()
	# if there is a coindexed node referring to node1,
	# node1 and node2 are coarguments.
	if node2 is None:
		return False
	elif index and node2.find('./node[@index="%s"]' % index) is not None:
		return True
	return node1 is node2


def readngdata():
	"""Read noun phrase number-gender counts."""
	# For faster loading, do not decode and parse into dict:
	with open('../groref/ngdata', 'rb') as inp:
		ngdata = inp.read()
	gadata = {}  # Format: {noun: (gender, animacy)}
	with open('data/gadata', encoding='utf8') as inp:
		for line in inp:
			a, b, c = line.rstrip('\n').split('\t')
			gadata[a] = b, c
	# https://www.meertens.knaw.nl/nvb/
	with open('data/Top_eerste_voornamen_NL_2010.csv',
			encoding='latin1') as inp:
		for line in islice(inp, 2, None):
			fields = line.split(';')
			if fields[1]:
				gadata[fields[1]] = ('f', 'human')
			if fields[3]:
				gadata[fields[3]] = ('m', 'human')
	return ngdata, gadata


@functools.lru_cache()
def nglookup(key, ngdata):
	"""Search through tab-separated file stored as bytestring.

	:returns: a dictionary with features."""  # FIXME: speed up
	if not key:
		return {}
	i = ngdata.find(('\n%s\t' % key.lower()).encode('utf8'))
	if i == -1:
		return {}
	j = ngdata.find('\n'.encode('utf8'), i + 1)
	match = ngdata[i + len(key) + 2:j].decode('utf8')
	genderdata = [int(x) for x in match.split(' ')]
	if (genderdata[0] > sum(genderdata) / 3
			and genderdata[1] > sum(genderdata) / 3):
		return {'number': 'sg', 'gender': 'fm', 'human': 1}
	elif genderdata[0] > sum(genderdata) / 3:
		return {'number': 'sg', 'gender': 'm', 'human': 1}
	elif genderdata[1] > sum(genderdata) / 3:
		return {'number': 'sg', 'gender': 'f', 'human': 1}
	elif genderdata[2] > sum(genderdata) / 3:
		return {'number': 'sg', 'gender': 'n', 'human': 0}
	elif genderdata[3] > sum(genderdata) / 3:
		return {'number': 'pl', 'gender': 'n'}
	return {}

def readconll(conllfile, docname='-'):
	"""Read conll data as list of lists: conlldata[sentno][tokenno][col].

	If multiple "#begin document docname" lines are found,
	only return chunks with matching docname; otherwise, return all chunks.
	"""
	conlldata = [[]]
	with open(conllfile) as inp:
		if inp.read().count('#begin document') == 1:
			docname = '-'
		inp.seek(0)
		while True:
			line = inp.readline()
			if (line.startswith('#begin document') and (docname == '-'
					or line.split()[2].strip('();') == docname)):
				while True:
					line = inp.readline()
					if line.startswith('#end document') or line == '':
						break
					if line.startswith('#'):
						pass
					elif line.strip():
						conlldata[-1].append(line.strip().split())
					else:
						conlldata.append([])
				break
			elif line == '':
				break
	if not conlldata[-1]:  # remove empty sentence if applicable
		conlldata.pop()
	if not conlldata[0]:
		raise ValueError('Could not read gold data from %r with docname %r' % (
				conllfile, docname))
	return conlldata

def conllclusterdict(conlldata):
	"""Extract dict from CoNLL file mapping gold cluster IDs to spans."""
	spansforcluster = {}
	spans = {}
	lineno = 1
	for sentno, chunk in enumerate(conlldata):
		scratch = {}
		for idx, fields in enumerate(chunk):
			lineno += 1
			labels = fields[-1]
			for a in labels.split('|'):
				if a == '-' or a == '_':
					continue
				try:
					clusterid = int(a.strip('()'))
				except ValueError:
					raise ValueError('Cannot parse cluster %r at line %d'
							% (a.strip('()'), lineno))
				if a.startswith('('):
					scratch.setdefault(clusterid, []).append(
							(sentno, idx, lineno))
				if a.endswith(')'):
					try:
						sentno, begin, _ = scratch[int(a.strip('()'))].pop()
					except KeyError:
						raise ValueError(
								'No opening paren for cluster %s at line %d'
								% (a.strip('()'), lineno))
					text = ' '.join(line[3] for line in chunk[begin:idx + 1])
					span = (sentno, begin, idx + 1, text)
					if span in spans:
						debug('Warning: duplicate span %r '
								'in cluster %d and %d, sent %d, line %d'
								% (span[3], clusterid, spans[span],
									sentno + 1, lineno))
					spans[span] = clusterid
					spansforcluster.setdefault(clusterid, set()).add(span)
		lineno += 1
		for a, b in scratch.items():
			if b:
				raise ValueError('Unclosed paren for cluster %d at line %d'
						% (a, b[0][2]))
	return spansforcluster

def debug(*args, **kwargs):
	"""Print debug information if global variable VERBOSE is True;
	send output to file (or stdout) DEBUGFILE."""
	if VERBOSE:
		print(*args, **kwargs, file=DEBUGFILE)


def color(text, c):
	"""Returns colored text."""
	if c == 'red':
		return colorama.Fore.RED + text + colorama.Fore.RESET
	elif c == 'green':
		return colorama.Fore.GREEN + text + colorama.Fore.RESET
	elif c == 'yellow':
		return colorama.Fore.YELLOW + text + colorama.Fore.RESET
	raise ValueError
	
def conllclusterdict(conlldata):
	"""Extract dict from CoNLL file mapping gold cluster IDs to spans."""
	spansforcluster = {}
	spans = {}
	lineno = 1
	for sentno, chunk in enumerate(conlldata):
		scratch = {}
		for idx, fields in enumerate(chunk):
			lineno += 1
			labels = fields[-1]
			for a in labels.split('|'):
				if a == '-' or a == '_':
					continue
				try:
					clusterid = int(a.strip('()'))
				except ValueError:
					raise ValueError('Cannot parse cluster %r at line %d'
							% (a.strip('()'), lineno))
				if a.startswith('('):
					scratch.setdefault(clusterid, []).append(
							(sentno, idx, lineno))
				if a.endswith(')'):
					try:
						sentno, begin, _ = scratch[int(a.strip('()'))].pop()
					except KeyError:
						raise ValueError(
								'No opening paren for cluster %s at line %d'
								% (a.strip('()'), lineno))
					text = ' '.join(line[3] for line in chunk[begin:idx + 1])
					span = (sentno, begin, idx + 1, text)
					if span in spans:
						debug('Warning: duplicate span %r '
								'in cluster %d and %d, sent %d, line %d'
								% (span[3], clusterid, spans[span],
									sentno + 1, lineno))
					spans[span] = clusterid
					spansforcluster.setdefault(clusterid, set()).add(span)
		lineno += 1
		for a, b in scratch.items():
			if b:
				raise ValueError('Unclosed paren for cluster %d at line %d'
						% (a, b[0][2]))
	return spansforcluster

def process(gold, path, output, ngdata, gadata,
		docname='-', conllfile=None, fmt=None,
		start=None, end=None, startcluster=0,
		goldmentions=False, exclude=(), outputprefix=None):
	"""Process a single directory with Alpino XML parses."""
	if os.path.isdir(path):
		path = os.path.join(path, '*.xml')
	debug('processing:', path)
	filenames = sorted(glob(path), key=parsesentid)[start:end]
	trees = [(parsesentid(filename), etree.parse(filename))
			for filename in filenames]
	mentions = None
	mentionlist = resolvecoreference(gold, trees, ngdata, gadata, mentions)

	return mentionlist

def main():
	"""CLI"""
	opts, args = gnu_getopt(sys.argv[1:], '', [
		'help', 'verbose', 'clindev', 'semeval', 'test', 'goldmentions',
		'fmt=', 'slice=', 'gold=', 'exclude=', 'outputprefix='])
	opts = dict(opts)
	ngdata, gadata = readngdata()
	start, end = opts.get('--slice', ':').split(':')
	start = int(start) if start else None
	end = int(end) if end else None
	path = args[0]
	exclude = [a for a in opts.get('--exclude', '').split(',') if a]
	
	filename = str(path.split("/")[-1:]).strip("[']")
	#new_path = "data/sonar/conll/" + filename + ".conll"
	new_path = "data/riddlecoref/coref/" + filename + ".conll"

	conll = readconll(new_path)
	gold = conllclusterdict(conll)
	
	print("Working on {}".format(filename))
	p = process(gold, path, sys.stdout, ngdata, gadata,
			fmt=opts.get('--fmt'), start=start, end=end,
			docname=os.path.basename(path.rstrip('/')),
			conllfile=opts.get('--gold'),
			goldmentions='--goldmentions' in opts,
			exclude=exclude)

	print("Creating csv")
	df = pd.DataFrame(p)

	#df.to_csv("data/sonar/csv/" + filename + ".csv", sep = ";", encoding = "utf-8", index = False)
	df.to_csv("data/riddlecoref/csv/" + filename + ".csv", sep = ";", encoding = "utf-8", index = False)

if __name__ == '__main__':
	main()
