import os
import sys
import re
from pathlib import Path
from unittest.mock import patch
from PIL import Image, ImageChops
import pyPLUTO as pp
import matplotlib.pyplot as plt
from te_examples import *

yes = "\033[32mENABLED\033[0m"
no  = "\033[31mDISABLED\033[0m"

options = {
    f"{"Loading":<8} check":  (no if "noload"     in sys.argv else yes, "lf"),
    f"{"LoadPart":<8} check": (no if "noloadpart" in sys.argv else yes, "lp"),
    f"{"Image":<8} check":    (no if "noimage"    in sys.argv else yes, "im"),
    f"{"Examples":<8} check": (no if "notests" in sys.argv else yes, "te")}

def single_test(file_path):
    try:
        with open(file_path, 'r') as f:
            exec(f.read())
        return True
    except:
        if not str(file_path).startswith("te"):
            print(" ---> \033[31mFAILED!\033[0m")
        return False

if __name__ == "__main__":
    print(f"Running tests with keywords: {', '.join(sys.argv[1:]) if len(sys.argv[1:])> 0 else "None"}")
    tot_tests, pas_tests = 0, 0
    index = []
    for option, status in options.items():
        print(f"{option}: {status[0]}")
        if status[0] == yes: index.append(status[1])
    files = sorted(f for f in Path(".").glob("*.py") if f.name != Path(sys.argv[0]).name)
    for file_path in files:
        if str(file_path)[:2] in index:
            tot_tests += 1
            res = single_test(file_path)
            pas_tests = pas_tests + 1 if res is True else pas_tests
    print(f"Tests passed: {pas_tests}/{tot_tests}")
