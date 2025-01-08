import os
import sys
import re
import shutil
from pathlib import Path
from unittest.mock import patch
from PIL import Image, ImageChops
import pyPLUTO as pp
import matplotlib.pyplot as plt


# Change temporarily the PLUTO_DIR environment
#os.environ['PLUTO_OLD'] = os.environ['PLUTO_DIR']
#os.environ['PLUTO_DIR'] = "."

yes = "\033[32mENABLED\033[0m"
no  = "\033[31mDISABLED\033[0m"

options = {
    "File copy from PLUTO": yes if "copy"      in sys.argv else no,
    "Plotting the tests":   no  if "noplot"    in sys.argv else yes,
    "Plot comparison":      no  if "nocompare" in sys.argv else yes,
    "Folder cleaning":      yes if "clean"     in sys.argv else no}

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
            return image_path
        print(f" ---> FAILED: Images do not match.")
    elif len(image_files) + len(ref_image_files) > 2:
        print(f" ---> FAILED: Multiple images found.")
    else:
        print(f" ---> FAILED: No image found.")
    return AssertionError(f"\033[31m{source} test failed!\033[0m")

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

def copy_files(file_path):
    test_path = extract_path_from_file(file_path).lstrip("/")
    src_dir = Path(os.environ.get('PLUTO_DIR')) / test_path
    dest_dir = Path("../Examples") / test_path
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
def single_example(ind, file_path, lenfiles):
    source = file_path.stem
    print(f"Test {ind:02}/{lenfiles}: {source.split('_')[1]:<11}", end="")

    if "copy" in sys.argv:
        print(f" ---> COPYING", end="")
        copy_files(file_path)


    if "noplot" not in sys.argv:
        print(f" ---> PLOTTING", end="")
        with open(os.devnull, 'w') as devnull, patch('sys.stdout', devnull), patch('matplotlib.pyplot.show', no_op):
            exec(file_path.read_text())
    else:
        pass

    if "nocompare" not in sys.argv:
        result = check_images(source)
        if isinstance(result,Path):
            print(" ---> \033[32mPASSED!\033[0m", end="")
        else:
            print(" ---> \033[31mFAILED!\033[0m")
    else:
        print(source)
        result = None

    if "clean" in sys.argv:
        if isinstance(result,Path) or result is None:
            results = list(Path(".").glob(f"{source}.*"))
            results = [str(f) for f in results if f.suffix != '.py']
            for result in results:
                try:
                    os.remove(f"./{result}")

                except:
                    pass
        else:
            return
        print(f" ---> CLEANED", end="")

    print("")

if __name__ == "__main__":
    print(f"Running Examples")
    for option, status in options.items():
        print(f"{option:<21}: {status}")
    files = sorted(f for f in Path("../Examples").glob("*.py") if f.name != Path(sys.argv[0]).name)
    for ind, file_path in enumerate(files, 1):
        single_example(ind, file_path, len(files))
