import pandas as pd

from joblib import dump, load
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split

from pleonastic.pipeline import *

csv = "data/sonar/csv/all.csv"
#csv = "data/riddlecoref/csv/all.csv"
df = pd.read_csv(csv, sep = ";")

n = len(df.columns)

X = df.iloc[:, 0: n-2]
y = df.iloc[:, n-1]

pipeline = full_pipeline
X_prep = pipeline.fit_transform(X)

X_train, X_test, y_train, y_test = train_test_split(X_prep, y)

classifier = RandomForestClassifier(n_estimators = 500,
									max_leaf_nodes = 16,
									n_jobs = -1, max_features = None,
									class_weight = {0:8, 1:1})
classifier.fit(X_train, y_train)

y_pred = classifier.predict(X_test)  

dump(classifier, "pleonastic/data.joblib")
#dump(classifier, "pleonastic/data_riddle.joblib")
dump(pipeline, "pleonastic/pipeline.joblib")
#dump(pipeline, "pleonastic/pipeline_riddle.joblib")
