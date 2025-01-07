import os
import sys
from pathlib import Path
from unittest.mock import patch
from PIL import Image, ImageChops
import pyPLUTO as pp
import matplotlib.pyplot as plt
import re

# Change temporarily the PLUTO_DIR environment
os.environ['PLUTO_OLD'] = os.environ['PLUTO_DIR']
os.environ['PLUTO_DIR'] = "."

def extract_path_from_file(file_path):
    with open(file_path, 'r') as f:
        for line in f:
            match = re.search(r"wdir\s*=\s*[^']*'([^']+)'", line)
            if match:
                return match.group(1)
    return None

# Find, check and compare the image files
def check_images(source):
    image_files, ref_image_files = find_imagefiles(source)
    if len(image_files) == 1 and len(ref_image_files) == 1:
        image_path = image_files[0]
        ref_image_path = ref_image_files[0]
        if compare_images(image_path, ref_image_path):
            return True
        print(f" ---> FAILED: Images do not match.")
    elif len(image_files) + len(ref_image_files) > 2:
        print(f" ---> FAILED: Multiple images found.")
    else:
        print(f" ---> FAILED: No image found.")
    return AssertionError(f"{source} test failed!")

# Find the image files for comparison within the folder
def find_imagefiles(source):
    image_files = list(Path(".").glob(f"{source}.*"))
    ref_image_files = list(Path("Ref_figs").glob(f"{source}.*"))

    image_files = [f for f in image_files if f.suffix != '.py']
    ref_image_files = [f for f in ref_image_files if f.suffix != '.py']
    return image_files, ref_image_files

# Method to compare two images or GIFs
def compare_images(image1_path, image2_path):
    with Image.open(image1_path) as img1, Image.open(image2_path) as img2:
        if img1.size != img2.size or ImageChops.difference(img1, img2).getbbox():
            return False
    return True

# Suppress `plt.show()` when running through this script
def no_op(*args, **kwargs):
    pass

import os
from pathlib import Path
import shutil

def copy_files(file_path):
    test_path = extract_path_from_file(file_path).lstrip("/")
    src_dir = Path(os.environ.get('PLUTO_OLD')) / test_path
    dest_dir = Path(os.environ.get('PLUTO_DIR')) / test_path
    if not src_dir.exists():
        print(f"Source directory does not exist: {src_dir}")
        return
    dest_dir.mkdir(parents=True, exist_ok=True)
    extensions = ['out', 'dbl', 'vtk', 'flt', 'h5', 'hdf5', 'dat']
    for ext in extensions:
        for src_file in src_dir.glob(f"*.{ext}"):
            dest_file = dest_dir / src_file.name
            shutil.copy(src_file, dest_file)

# Main function to load and run the tests
def single_test(ind, file_path):
    source = file_path.stem
    print(f"Test {ind:02}/{len(files)}: {source.split('_')[1]:<11}", end="")

    if "copy" in sys.argv:
        copy_files(file_path)
        print(f" ---> COPYING", end="")

    if "noplot" not in sys.argv:
        with open(os.devnull, 'w') as devnull, patch('sys.stdout', devnull), patch('matplotlib.pyplot.show', no_op):
            exec(file_path.read_text())
        print(f" ---> PLOTTING", end="")

    if "nocompare" not in sys.argv:
        result = check_images(source)
        print(f" ---> {"PASSED!" if result is True else result}", end="")
        
    print("")

if __name__ == "__main__":
    files = sorted(f for f in Path(".").glob("*.py") if f.name != Path(sys.argv[0]).name)
    for ind, file_path in enumerate(files, 1):
        single_test(ind, file_path)
