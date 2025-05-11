import subprocess
from pathlib import Path

# Set paths
source_dir = Path(__file__).resolve().parent / "Src" / "pyPLUTO"
output_dir = Path(__file__).resolve().parent / "Docs" / "Badges"
output_dir.mkdir(parents=True, exist_ok=True)

# Define tasks
tasks = {
    "coverage": [
        ["coverage", "run", "--source", str(source_dir), "-m", "pytest"],
        ["coverage", "report"],
        ["coverage", "xml", "-o", str(output_dir / "coverage.xml")],
    ],
    "pylint": [
        ["pylint", str(source_dir), "--exit-zero"],
    ],
    "interrogate": [
        ["interrogate", str(source_dir), "--verbose"],
    ],
}

# Output destinations
output_files = {
    "pylint": output_dir / "pylint.txt",
    "interrogate": output_dir / "interrogate.txt",
}

# Run tasks
for tool, commands in tasks.items():
    print(f"\nRunning {tool}...")
    for cmd in commands:
        try:
            if tool in output_files and cmd == commands[-1]:
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
