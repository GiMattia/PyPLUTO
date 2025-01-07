import os
import sys
import re
from pathlib import Path
from unittest.mock import patch
from PIL import Image, ImageChops
import pyPLUTO as pp
import matplotlib.pyplot as plt
from te_examples import *

options = {
    "Loading check":  ("DISABLED" if "noload"     in sys.argv else "ENABLED", "lf"),
    "LoadPart check": ("DISABLED" if "noloadpart" in sys.argv else "ENABLED", "lp"),
    "Image check":    ("DISABLED" if "noimage"    in sys.argv else "ENABLED", "im"),
    "Examples check": ("DISABLED" if "noexamples" in sys.argv else "ENABLED", "te")}

def single_test(file_path):
    exec(open(file_path).read())

if __name__ == "__main__":
    print(f"Running tests with keywords: {', '.join(sys.argv[1:])}")
    index = []
    for option, status in options.items():
        print(f"{option:<15}: {status[0]}")
        if status[0] == "ENABLED": index.append(status[1])
    files = sorted(f for f in Path(".").glob("*.py") if f.name != Path(sys.argv[0]).name)
    for file_path in files:
        if str(file_path)[:2] in index: single_test(file_path)
