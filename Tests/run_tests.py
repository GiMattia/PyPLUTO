import os, sys
import pyPLUTO as pp

os.environ["CALLED_FROM_AUTOMATION"] = "1"
for file in (f for f in os.listdir(".") if f != sys.argv[0]):
    print(file)
    exec(open(file).read())
