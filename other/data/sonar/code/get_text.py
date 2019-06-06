# get text from iob for conll

import argparse
import os
from pathlib import Path

# start arguments #
parser = argparse.ArgumentParser(add_help=True)

parser.add_argument(
    "-p0",
    help="Set CONLL path",
    type=Path,
    required=False,
    default=Path.cwd())
    
parser.add_argument(
    "-p1",
    help="Set IOB path",
    type=Path,
    required=True)

args = parser.parse_args()
p0 = args.p0
p1 = args.p1


# end arguments #

for filename in os.listdir(p0):
    
    f = str(filename[:-6])
    
    iobfile = f + ".iob"
    try:
        with open(p1 / iobfile)as iob:
            out = open("txt/"+ f + ".txt","w") 
            text = str()
            for line in iob.readlines():
                text += (line.split("\t")[0] + " ")
            out.write(text)
            out.close()
    except FileNotFoundError:
        iobfile1 = "wiki-" + iobfile[4:]
        with open(p1 / iobfile1)as iob:
            out = open("txt/"+ f + ".txt","w") 
            text = str()
            for line in iob.readlines():
                text += (line.split("\t")[0] + " ")
            out.write(text)
            out.close()
