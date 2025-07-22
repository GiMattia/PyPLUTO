# run_pipeline.py
import argparse
import subprocess
from pathlib import Path

UTILS_DIR = Path(__file__).parent


def run_step(script: str, name: str, skip: bool):
    if skip:
        print(f"⏭️ Skipping {name}")
    else:
        print(f"🚀 Running {name}...")
        result = subprocess.run(
            ["python", str(UTILS_DIR / script)], check=False
        )
        if result.returncode != 0:
            print(f"❌ {name} failed.")
            exit(1)
        print(f"✅ {name} complete.\n")


def main():
    parser = argparse.ArgumentParser(description="Run docstring pipeline")
    parser.add_argument(
        "--noscan", action="store_true", help="Skip scan_exposed.py"
    )
    parser.add_argument(
        "--nocheck", action="store_true", help="Skip analyze_docstrings.py"
    )
    parser.add_argument(
        "--nowrite", action="store_true", help="Skip rewrite_docstrings.py"
    )

    args = parser.parse_args()

    run_step("scan_exposed.py", "Scan Source", args.noscan)
    run_step("analyze_docstrings.py", "Analyze Docstrings", args.nocheck)
    run_step("rewrite_docstrings.py", "Rewrite Docstrings", args.nowrite)


if __name__ == "__main__":
    main()
