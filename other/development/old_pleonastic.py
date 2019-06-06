def oldpleonasticpronoun(node):
	
	WEATHERVERBS = ('dooien gieten hagelen miezeren misten motregenen onweren '
		'plenzen regenen sneeuwen stormen stortregenen ijzelen vriezen '
		'weerlichten winteren zomeren').split()
	
	"""Return True if node is a pleonastic (non-referential) pronoun."""
	# Examples from Lassy syntactic annotation manual.
	if node.get('rel') in ('sup', 'pobj1'):
		return True
	if node.get('rel') == 'su' and node.get('lemma') == 'het':
		head = node.find('../node[@rel="hd"]')
		# het regent. / hoe gaat het?
		if head.get('lemma') in WEATHERVERBS or head.get('lemma') == 'gaan':
			return True
		if (head.get('lemma') == 'ontbreken'
				and node.find('../node[@rel="pc"]'
					'/node[@rel="hd"][@lemma="aan"]') is not None):
			return True
		# het kan voorkomen dat ...
		if (node.get('index') and node.get('index')
				in node.xpath('../node//node[@rel="sup"]/@index')):
			return True
	if node.get('rel') == 'obj1' and node.get('lemma') == 'het':
		head = node.find('../node[@rel="hd"]')
		head = '' if head is None else head.get('lemma')
		# (60) de presidente had het warm
		if head == 'hebben' and node.find('../node[@rel="predc"]') is not None:
			return True
		# (61) samen zullen we het wel rooien.
		if head == 'rooien':
			return True
		# (62) hij zette het op een lopen
		if (head == 'zetten' and node.find('../node[@rel="svp"]/'
				'node[@word="lopen"]') is not None):
			return True
		# (63) had het op mij gemunt.
		if head == 'munten' and node.find('..//node[@word="op"]') is not None:
			return True
		# (64) het erover hebben
		if (head == 'hebben'
				and (node.find('../node[@word="erover"]') is not None
					or (node.find('..//node[@word="er"]') is not None
						and node.find('..//node[@word="over"]') is not None))):
			return True
	return False
