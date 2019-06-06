from collections import OrderedDict
from pleonastic.feature_extractor import *


def featureDict(node, tree):
	d = OrderedDict()

	# numerical features
	adj = tree.getroot().findall('.//node[@pos="adj"]')
	adv = tree.getroot().findall('.//node[@pos="adv"]')
	comp = tree.getroot().findall('.//node[@pos="comp"]')
	comparative = tree.getroot().findall('.//node[@pos="comparative"]')
	det = tree.getroot().findall('.//node[@pos="det"]')
	fixed = tree.getroot().findall('.//node[@pos="fixed"]')
	name = tree.getroot().findall('.//node[@pos="name"]')
	noun = tree.getroot().findall('.//node[@pos="noun"]')
	num = tree.getroot().findall('.//node[@pos="num"]')
	part = tree.getroot().findall('.//node[@pos="part"]')
	pp = tree.getroot().findall('.//node[@pos"pp"]')
	prefix = tree.getroot().findall('.//node[@pos="prefix"]')
	prep = tree.getroot().findall('.//node[@pos="prep"]')
	pron = tree.getroot().findall('.//node[@pos="pron"]')
	punct = tree.getroot().findall('.//node[@pos="punct"]')
	tag = tree.getroot().findall('.//node[@pos="tag"]')
	verb = tree.getroot().findall('.//node[@pos"verb"]')
	vg = tree.getroot().findall('.//node[@pos="vg"]')
	
	lid = tree.getroot().findall('.//node[@pt="lid"]')
	spec = tree.getroot().findall('.//node[@pt="spec"]')
	tsw = tree.getroot().findall('.//node[@pt="tsw"]')
	
	het = tree.getroot().findall('.//node[@lemma="het"]')
	iemand = tree.getroot().findall('.//node[@lemma="iemand"]')
	niemand = tree.getroot().findall('.//node[@lemma="niemand"]')
	
	inf = tree.getroot().findall('.//node[@postag="WW(inf,nom,zonder,zonder-n)"]')
	if inf == []:
		inf = tree.getroot().findall('.//node[@postag="WW(inf,prenom,met-e)"]')
		if inf == []:
			inf = tree.getroot().findall('.//node[@postag="WW(inf,vrij,zonder)"]')

	# previous next attributes
	d["previous_pos"],\
	d["previous_lemma"],\
	d["previous_previous_pos"],\
	d["previous_previous_lemma"] = pnAttrib(node, tree, "previous")

	d["next_pos"],\
	d["next_lemma"],\
	d["next_next_pos"],\
	d["next_next_lemma"] = pnAttrib(node, tree, "next")

	d["nxt_adj"], d["prv_adj"] = posAttrib(adj, node)
	d["nxt_adv"], d["prv_adv"] = posAttrib(adv, node)
	d["nxt_comp"], d["prv_comp"] = posAttrib(comp, node)
	d["nxt_comparative"], d["prv_comparative"] = posAttrib(comparative, node)
	d["nxt_det"], d["prv_det"] = posAttrib(det, node)
	d["nxt_fixed"], d["prv_fixed"] = posAttrib(fixed, node)
	d["nxt_name"], d["prv_name"] = posAttrib(name, node)
	d["nxt_noun"], d["prv_noun"] = posAttrib(noun, node)
	d["nxt_num"], d["prv_num"] = posAttrib(num, node)
	d["nxt_part"], d["prv_part"] = posAttrib(part, node)
	d["nxt_pp"], d["prv_pp"] = posAttrib(pp, node)
	d["nxt_prefix"], d["prv_prefix"] = posAttrib(prefix, node)
	d["nxt_prep"], d["prv_prep"] = posAttrib(prep, node)
	d["nxt_pron"], d["prv_pron"] = posAttrib(pron, node)
	d["nxt_punct"], d["prv_punct"] = posAttrib(punct, node)
	d["nxt_tag"], d["prv_tag"] = posAttrib(tag, node)
	d["nxt_verb"], d["prv_verb"] = posAttrib(verb, node)
	d["nxt_vg"], d["prv_vg"] = posAttrib(vg, node)
	d["nxt_lid"], d["prv_lid"] = posAttrib(lid, node)
	d["nxt_spec"], d["prv_spec"] = posAttrib(spec, node)
	d["nxt_tsw"], d["prv_tsw"] = posAttrib(tsw, node)
	d["nxt_het"], d["prv_het"] = posAttrib(het, node)
	d["nxt_iemand"], d["prv_iemand"] = posAttrib(iemand, node)
	d["nxt_niemand"], d["prv_niemand"] = posAttrib(niemand, node)
	d["nxt_inf"], d["prv_inf"] = posAttrib(inf, node)

	"""
	d["rule0"],\
	d["rule1"],\
	d["rule2"],\
	d["rule3"],\
	d["rule4"],\
	d["rule5"],\
	d["rule6"],\
	d["rule7"],\
	d["rule8"] = ruleExtractor(node)
	"""

	d["sub_verb"],\
	d["obj"],\
	d["ind_obj"],\
	d["obj_verb"],\
	d["app"],\
	d["cnj"],\
	d["comp"],\
	d["crd"],\
	d["det"],\
	d["mod"],\
	d["predc"],\
	d["prep"],\
	d["rhd"],\
	d["su"],\
	d["sup"],\
	d["svp"],\
	d["whd"]  = lexicalExtractor(node)
	
	d["gaan"],\
	d["ontbreken"],\
	d["werken"],\
	d["zijn0"],\
	d["zijn1"],\
	d["zijn2"],\
	d["hebben"],\
	d["erover_hebben"],\
	d["rooien"],\
	d["munten"],\
	d["lopen"],\
	d["vinden"],\
	d["blijken0"],\
	d["blijken1"],\
	d["schijnen0"],\
	d["schijnen1"] = patternMatch(node)

	d["weer"],\
	d["onbep"],\
	d["first"] = otherFeatures(node)

	#node_dict = dict(node.attrib)

	#combined = {**d, **node_dict}
	combined = d

	return combined
