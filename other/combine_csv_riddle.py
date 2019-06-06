import os
import pandas as pd

data = []

#path = "data/sonar/csv/"
path = "data/riddlecoref/csv/"

#out = "data/sonar/csv/all.csv"
out = "data/riddlecoref/csv/all.csv"

if os.path.isfile(out):
    print("The file all.csv already exists. Delete it first before running.")
else:
    for filename in os.listdir(path):
        try:
            csv = pd.read_csv(path + filename, sep = ";")
            data.append(csv)
    
        except pd.errors.EmptyDataError:
            pass
    
    df = pd.concat(data, sort=True)
    
    cols = list(df.columns.values)
    cols.pop(cols.index("old"))
    cols.pop(cols.index("pleonastic"))
    cols.append("old")
    cols.append("pleonastic")
    
    ndf = df[cols]
    ndf = ndf.fillna("None")

    print("Number of words in the dataset: {}".format(len(ndf)))
    ndf.to_csv(out, sep = ";", encoding = "utf-8", index = False)
    
