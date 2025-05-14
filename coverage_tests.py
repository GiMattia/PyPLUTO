import shutil
import subprocess
from pathlib import Path

# Set paths
source_dir = Path(__file__).resolve().parent / "Src" / "pyPLUTO"
output_dir = Path(__file__).resolve().parent / "Docs" / "Badges"
output_dir.mkdir(parents=True, exist_ok=True)

# Define tasks
tasks = {
    "coverage": [
        ["coverage", "erase"],  # Erase previous coverage data
        [
            "pytest",
            "--cov=Src/pyPLUTO",  # Use pytest-cov to track coverage
            "--cov-report=xml",  # Generate XML coverage report
            "--cov-report=term",  # Show coverage in the terminal
        ],  # Run pytest with coverage
    ],
    "pylint": [
        [
            "pylint",
            str(source_dir),
            "--exit-zero",
        ],  # Run pylint without failing the build on issues
    ],
    "interrogate": [
        [
            "interrogate",
            str(source_dir),
            "--verbose",
            "--fail-under=40.0",
        ],  # Set docstring coverage threshold to 40%
    ],
}

# Output destinations
output_files = {
    "pylint": output_dir / "pylint.txt",
    "interrogate": output_dir / "interrogate.txt",
    "coverage": output_dir / "coverage.xml",  # Coverage report destination
}

# Run tasks
for tool, commands in tasks.items():
    print(f"\nRunning {tool}...")
    for cmd in commands:
        try:
            if tool == "coverage":
                # Run pytest with coverage
                subprocess.run(cmd, check=True)
                # After pytest completes, move the coverage.xml file
                coverage_report_path = Path("coverage.xml")
                if coverage_report_path.exists():
                    shutil.move(coverage_report_path, output_files["coverage"])
                    print(
                        f"Coverage report moved to: {output_files['coverage']}"
                    )
            elif tool in output_files and cmd == commands[-1]:
                # For pylint and interrogate, save output to a file
                with open(output_files[tool], "w") as f:
                    subprocess.run(
                        cmd, check=True, stdout=f, stderr=subprocess.STDOUT
                    )
            else:
                subprocess.run(cmd, check=True)
        except subprocess.CalledProcessError as e:
            if tool == "interrogate" and e.returncode == 1:
                # Missing docstrings — not fatal
                print(
                    "Interrogate found missing docstrings (exit code 1). Output saved."
                )
            else:
                print(f"Error running {tool} step: {e}")
