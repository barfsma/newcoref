import pandas as pd


from joblib import dump, load
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score

print("Trained on SoNaR1")

clf = load("pleonastic/data.joblib")
pipeline = load("pleonastic/pipeline.joblib")

riddle = True
sonar = True

if riddle:
	print("Riddlecoref")

	csv = "data/riddlecoref/csv/all.csv"
	df = pd.read_csv(csv, sep = ";")

	n = len(df.columns)

	X = df.iloc[:, 0: n-2]
	x = df.iloc[:, n-2]
	y = df.iloc[:, n-1]

	X_prep = pipeline.transform(X)
	pred = clf.predict(X_prep)	

	print("RandomForestClassifier")
	print("Confusion matrix:")
	print(confusion_matrix(y, pred))
	print("Performance:")
	print(classification_report(y, pred))
	print("Overall accuracy:")
	print(accuracy_score(y, pred))

	print("\n")
	print("Original pleonastic pronoun function:")
	print("Confusion matrix:")
	print(confusion_matrix(y, x))
	print("Performance:")
	print(classification_report(y, x))
	print("Overall accuracy:")
	print(accuracy_score(y, x))
	print("\n")

if sonar:
	print("Sonar")
	csv = "data/sonar/csv/all.csv"
	df = pd.read_csv(csv, sep = ";")

	n = len(df.columns)

	X = df.iloc[:, 0: n-2]
	x = df.iloc[:, n-2]
	y = df.iloc[:, n-1]

	X_prep = pipeline.transform(X)
	pred = clf.predict(X_prep)	

	print("RandomForestClassifier")
	print("Confusion matrix:")
	print(confusion_matrix(y, pred))
	print("Performance:")
	print(classification_report(y, pred))
	print("Overall accuracy:")
	print(accuracy_score(y, pred))
	print("\n")
	print("Original pleonastic pronoun function:")
	print("Confusion matrix:")
	print(confusion_matrix(y, x))
	print("Performance:")
	print(classification_report(y, x))
	print("Overall accuracy:")
	print(accuracy_score(y, x))
	print("\n")

print("Trained on riddlecoref")


clf = load("pleonastic/data_riddle.joblib")
pipeline = load("pleonastic/pipeline_riddle.joblib")

riddle = True
sonar = True

if riddle:
	print("Riddlecoref")

	csv = "data/riddlecoref/csv/all.csv"
	df = pd.read_csv(csv, sep = ";")

	n = len(df.columns)

	X = df.iloc[:, 0: n-2]
	x = df.iloc[:, n-2]
	y = df.iloc[:, n-1]

	X_prep = pipeline.transform(X)
	pred = clf.predict(X_prep)	

	print("RandomForestClassifier")
	print("Confusion matrix:")
	print(confusion_matrix(y, pred))
	print("Performance:")
	print(classification_report(y, pred))
	print("Overall accuracy:")
	print(accuracy_score(y, pred))
	print("\n")
	print("Original pleonastic pronoun function:")
	print("Confusion matrix:")
	print(confusion_matrix(y, x))
	print("Performance:")
	print(classification_report(y, x))
	print("Overall accuracy:")
	print(accuracy_score(y, x))
	print("\n")

if sonar:
	print("Sonar")
	csv = "data/sonar/csv/all.csv"
	df = pd.read_csv(csv, sep = ";")

	n = len(df.columns)

	X = df.iloc[:, 0: n-2]
	x = df.iloc[:, n-2]
	y = df.iloc[:, n-1]

	X_prep = pipeline.transform(X)
	pred = clf.predict(X_prep)	

	print("RandomForestClassifier")
	print("Confusion matrix:")
	print(confusion_matrix(y, pred))
	print("Performance:")
	print(classification_report(y, pred))
	print("Overall accuracy:")
	print(accuracy_score(y, pred))
	print("\n")
	print("Original pleonastic pronoun function:")
	print("Confusion matrix:")
	print(confusion_matrix(y, x))
	print("Performance:")
	print(classification_report(y, x))
	print("Overall accuracy:")
	print(accuracy_score(y, x))
	print("\n")
