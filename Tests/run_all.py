import sys
from pathlib import Path
import pytest

yes = "\033[32mENABLED\033[0m"
no = "\033[31mDISABLED\033[0m"

options = {
    f'{"Loading":<8} check': (no if "noload" in sys.argv else yes, "lf"),
    f'{"LoadPart":<8} check': (no if "noloadpart" in sys.argv else yes, "lp"),
    f'{"Image":<8} check': (no if "noimage" in sys.argv else yes, "im"),
    f'{"Examples":<8} check': (no if "notests" in sys.argv else yes, "te"),
}


def run_pytest(file_path):
    # Use pytest.main with the '-q' flag to suppress default output
    result = pytest.main([str(file_path), "-q"])
    return result == 0  # pytest returns 0 if tests pass


if __name__ == "__main__":
    print(
        f"Running tests with keywords: {', '.join(sys.argv[1:]) if len(sys.argv[1:]) > 0 else 'None'}"
    )

    # Determine which test files to run based on the options
    index = []
    for option, status in options.items():
        print(f"{option}: {status[0]}")
        if status[0] == yes:
            index.append(status[1])

    # Collect test files based on the index (i.e., those that match the options)
    files = sorted(
        f for f in Path(".").glob("*.py") if f.name != Path(sys.argv[0]).name
    )

    # Run tests for each selected file
    for file_path in files:
        if str(file_path)[:2] in index:
            print(file_path)
            if run_pytest(file_path):
                print(" ---> \033[32mPASSED!\033[0m")
            else:
                print(" ---> \033[31mFAILED!\033[0m")
