import pandas as pd


from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.pipeline import FeatureUnion, Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler


class DataFrameselector(BaseEstimator, TransformerMixin):
	def __init__(self, attribute_names):
		self.attribute_names = attribute_names
	def fit(self, X, y = None):
		return self
	def transform(self, X):
		return X[self.attribute_names].values


cat_attribs = ["next_pos", "next_next_pos", "next_lemma",
			   "next_next_lemma", "previous_pos",
			   "previous_previous_pos", "previous_lemma",
			   "previous_previous_lemma", "sub_verb",
			   "obj", "ind_obj", "obj_verb", "app", "cnj",
			   "comp", "crd", "det", "mod", "predc", "prep", 
			   "rhd", "su", "sup", "svp", "whd"]

num_attribs = ["nxt_adj", "prv_adj", "nxt_adv", "prv_adv",
			   "nxt_comp", "prv_comp", "nxt_comparative", "prv_comparative",
			   "nxt_det", "prv_det", "nxt_fixed", "prv_fixed",
			   "nxt_name", "prv_name", "nxt_noun", "prv_noun",
			   "nxt_num", "prv_num", "nxt_part", "prv_part",
			   "nxt_pp", "prv_pp", "nxt_prefix", "prv_prefix",
			   "nxt_prep", "prv_prep", "nxt_pron", "prv_pron",
			   "nxt_punct", "prv_punct", "nxt_tag", "prv_tag",
			   "nxt_verb", "prv_verb", "nxt_vg", "prv_vg",
			   "nxt_lid", "prv_lid", "nxt_spec", "prv_spec",
			   "nxt_tsw", "prv_tsw", "nxt_het", "prv_het",
			   "nxt_iemand", "prv_iemand", "nxt_niemand", "prv_niemand",
			   "nxt_inf", "prv_inf"]


bin_attribs = ["first", "onbep", "gaan", "ontbreken", "werken",
               "zijn0",  "zijn1", "zijn2", "hebben", "erover_hebben",
               "rooien", "munten", "schijnen0", "schijnen1"]

num_pipeline = Pipeline([
		("selector", DataFrameselector(num_attribs)),
		("scaler", StandardScaler()),
	])

cat_pipeline = Pipeline([
		("selector", DataFrameselector(cat_attribs)),
		("cat_encoder", OneHotEncoder(categories = "auto", 
			handle_unknown = "ignore")),
	])

bin_pipeline = Pipeline([
		("selector", DataFrameselector(bin_attribs)),
	])

full_pipeline = FeatureUnion(transformer_list = [
		("num_pupeline", num_pipeline),
		("cat_pipeline", cat_pipeline),
		("bin_pipeline", bin_pipeline),
	])
