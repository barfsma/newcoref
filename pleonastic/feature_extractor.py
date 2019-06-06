from lxml import etree


def posAttrib(pos, node):
	nb = float(node.attrib["begin"])

	nxt = 0.0
	prv = 0.0

	for i in pos:
		ib = float(i.attrib["begin"])
		if ib > nb:
			nxt = ib-nb
		else:
			prv = nb-ib
	
	return nxt, prv


def pnAttrib(node, tree, pn):
	find_pos, find_lemma, find_find_pos, find_find_lemma = None, None, None, None

	begin_id = node.get("begin")
	end_id = node.get("end")

	if pn == "previous":
		find0, find1, find2 = begin_id, "@end", "begin"

	if pn == "next":
		find0, find1, find2 = end_id, "@begin", "end"

	try:
		find = tree.getroot().findall('.//node['+ find1 + '="{}"]'.format(find0))[0]
		find_pos = find.get("pos")
		find_lemma = find.get("lemma")
		
		find_find = tree.getroot().findall('.//node['+ find1 + '="{}"]'.format(find.attrib[find2]))[0]
		find_find = dict(find_find.attrib)

		try:
			# get features of word before previous word
			find_find_pos = find_find["pos"]
			find_find_lemma = find_find["lemma"]
		except KeyError:
			pass

	except IndexError:
		pass

	return find_pos, find_lemma, find_find_pos, find_find_lemma


def lexicalExtractor(node):
	sub_verb, obj, ind_obj, obj_verb, app, cnj, comp, crd, det, mod,\
		predc, prep, rhd, su, sup, svp, whd = None, None, None, None,\
		None, None, None, None, None, None, None, None, None, None,\
		None, None, None

	if node.get("rel") == "su":
		sub_verb = findLex(node, "hd", 1)
		obj = findLex(node, "obj1", 1)
		ind_obj = findLex(node, "obj2", 1)
	if node.get("rel") == "obj1":
		obj_verb = findLex(node, "hd", 1)

	app = findLex(node, "app", 2)
	cnj = findLex(node, "cnj", 2)
	comp = findLex(node, "cmp", 2)
	crd = findLex(node, "crd", 2)
	det = findLex(node, "det", 2)
	mod = findLex(node, "mod", 1)
	predc = findLex(node, "predc", 1)
	rhd = findLex(node, "rhd", 2)
	su = findLex(node, "su", 1)
	sup = findLex(node, "sup", 1)
	svp = findLex(node, "svp", 1)
	whd = findLex(node, "whd", 2)

	prep = node.find('..{}node[@pos="{prep}"]')
	if prep is not None:
		prep = prep.get("lemma")

	return sub_verb, obj, ind_obj, obj_verb, app, cnj, comp, crd, det,\
			mod, predc, prep, rhd, su, sup, svp, whd


def findLex(node, cat, level):
	f = node.find('..{}node[@rel="{}"]'.format(level * "/", cat))
	if f is not None:
		f = f.get("lemma")
	return f

def patternMatch(node):
	gaan, ontbreken, werken, zijn0, zijn1, zijn2, hebben, erover_hebben,\
	rooien,	munten, lopen, vinden, blijken0, blijken1,\
	schijnen0, schijnen1 = 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0

	head = node.find('../node[@rel="hd"]')
	if head is not None:
		head = head.get("lemma")

	if node.get("rel") == "su":
		if head == "gaan":
			gaan = 1
		if (head == 'ontbreken'
			and node.find('../node[@rel="pc"]'
				'/node[@rel="hd"][@lemma="aan"]') is not None):
			ontbreken = 1
		if head == "werken" and node.find('../node[@rel="mod"]') is not None:
			werken = 1
		if head == "zijn" and node.find('../node[@rel="predc"]') is not None:
			zijn0 = 1
		if head == "blijken":
			blijken0 = 1
		if head == "schijnen":
			schijnen0 = 1

	if node.get("rel") == "obj1":
		if head == "hebben" and node.find('../node[@rel="predc"]') is not None:
			hebben = 1
		if (head == 'hebben'
				and (node.find('../node[@word="erover"]') is not None
					or (node.find('..//node[@word="er"]') is not None
						and node.find('..//node[@word="over"]') is not None))):
			erover_hebben = 1
		if head == "rooien":
			rooien = 1
		if head == "munten" and node.find('..//node[@word="op"]') is not None:
			munten = 1
		if (head == "zetten" and node.find('../node[@rel="svp"]/'
			'node[@word="lopen"]') is not None):
			lopen = 1
		if head == "vinden" and node.find('../node[@rel="predc"]') is not None:
			vinden = 1
	if node.get("rel") == "sup":
		if head == "blijken":
			blijken1 = 1
		if head == "schijnen":
			schijnen = 1
	if node.get("rel") == "predc":
		if head == "zijn":
			zijn1 = 1
	if node.get("rel") == "hd":
		head = node.find('..//node[@rel="hd"]')
		head = head.get("lemma")
		if head == "zijn" and node.find('..//node[@rel="predc"]') is not None:
			zijn2 = 1

	return gaan, ontbreken, werken, zijn0, zijn1, zijn2, hebben,\
	erover_hebben, rooien,	munten, lopen, vinden, blijken0,\
	blijken1, schijnen0, schijnen1

def otherFeatures(node):
	weer, onbep, first = 0, 0, 0

	# from the original pleonastic pronoun function
	WEATHERVERBS = ("dooien gieten hagelen miezeren misten motregenen onweren "
		"plenzen regenen sneeuwen stormen stortregenen ijzelen vriezen "
		"weerlichten winteren zomeren").split()
		
	if node.get("rel") == "su":
		head = node.find('../node[@rel="hd"]')
		if head.get("lemma") in WEATHERVERBS:
			weer = 1

	if node.attrib["postag"][4:9] == "onbep":
		onbep = 1

	if node.get("begin") == "0":
		first = 1

	return weer, onbep, first


def ruleExtractor(node):
	"""This is the original pleonastic pronoun module from DutchCoref"""
	WEATHERVERBS = ('dooien gieten hagelen miezeren misten motregenen onweren '
		'plenzen regenen sneeuwen stormen stortregenen ijzelen vriezen '
		'weerlichten winteren zomeren').split()
		
	rule0, rule1, rule2, rule3, rule4, rule5, rule6, rule7, rule8 = \
	0, 0, 0, 0, 0, 0, 0, 0, 0
	# Examples from Lassy syntactic annotation manual.
	if node.get('rel') in ('sup', 'pobj1'):
		rule0 = 1
	if node.get('rel') == 'su' and node.get('lemma') == 'het':
		head = node.find('../node[@rel="hd"]')
		# het regent. / hoe gaat het?
		if head.get('lemma') in WEATHERVERBS or head.get('lemma') == 'gaan':
			rule1 = 1
		if (head.get('lemma') == 'ontbreken'
				and node.find('../node[@rel="pc"]'
					'/node[@rel="hd"][@lemma="aan"]') is not None):
			rule2 = 1
		# het kan voorkomen dat ...
		if (node.get('index') and node.get('index')
				in node.xpath('../node//node[@rel="sup"]/@index')):
			rule3 = 1
	if node.get('rel') == 'obj1' and node.get('lemma') == 'het':
		head = node.find('../node[@rel="hd"]')
		head = '' if head is None else head.get('lemma')
		# (60) de presidente had het warm
		if head == 'hebben' and node.find('../node[@rel="predc"]') is not None:
			rule4 = 1
		# (61) samen zullen we het wel rooien.
		if head == 'rooien':
			rule5 = 1
		# (62) hij zette het op een lopen
		if (head == 'zetten' and node.find('../node[@rel="svp"]/'
				'node[@word="lopen"]') is not None):
			rule6 = 1
		# (63) had het op mij gemunt.
		if head == 'munten' and node.find('..//node[@word="op"]') is not None:
			rule7 = 1
		# (64) het erover hebben
		if (head == 'hebben'
				and (node.find('../node[@word="erover"]') is not None
					or (node.find('..//node[@word="er"]') is not None
						and node.find('..//node[@word="over"]') is not None))):
			rule8 = 1

	return rule0, rule1, rule2, rule3, rule4, rule5, rule6, rule7, rule8
