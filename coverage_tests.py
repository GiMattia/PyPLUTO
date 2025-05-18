import os
import re
import subprocess
import sys

cov_errs = 50
cov_warn = 75

RED = "\033[31m"
YELLOW = "\033[33m"
GREEN = "\033[32m"
RESET = "\033[0m"

globscore = 0

commands = [
    {
        "name": "pytest",
        "cmd": ["pytest", "--cov=pyPLUTO", "--cov-report=term-missing"],
        "output": "pytest_output.txt",
    },
    {
        "name": "mypy",
        "cmd": ["mypy", "--strict", "@mypy_files.txt"],
        "output": "mypy_output.txt",
    },
    {
        "name": "pylint",
        "cmd": None,  # We'll fill this dynamically based on mypy_files.txt
        "output": "pylint_output.txt",
    },
    {
        "name": "interrogate",
        "cmd": ["interrogate", "Src/pyPLUTO/"],
        "output": "interrogate_output.txt",
    },
]


def read_mypy_files_list(file_path: str = "mypy_files.txt") -> list[str]:
    with open(file_path) as f:
        return [
            line.strip()
            for line in f
            if line.strip() and not line.startswith("#")
        ]


def run_command(cmd: list[str], output_file: str):
    try:
        result = subprocess.run(
            cmd,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            check=False,  # Let it continue even on failures
        )
        with open(output_file, "w") as f:
            f.write(result.stdout)
    except Exception as e:
        with open(output_file, "w") as f:
            f.write(f"Error running command: {' '.join(cmd)}\n{e}")


def colorize_test(score: float, summary: str) -> str:

    global globscore

    if score < cov_errs:  # 1 error every 2 files or more
        color = RED
        globscore += 0
    elif score < cov_warn:  # 1 error every 4 files or more
        color = YELLOW
        globscore += 1
    else:
        color = GREEN
        globscore += 2

    return f"{color}{summary}{RESET}"


def extract_score(tool_name: str, output_file: str) -> str:
    with open(output_file) as f:
        content = f.read()

    if tool_name == "pytest":

        errors_match = re.search(r"=+\s*(\d+)\s+errors? in [\d\.]+s", content)
        errors_count = int(errors_match.group(1)) if errors_match else 0

        # Extract coverage percentage from TOTAL line
        coverage_match = re.search(
            r"TOTAL\s+\d+\s+\d+\s+\d+\s+\d+\s+(\d+)%", content
        )
        coverage = float(coverage_match.group(1)) if coverage_match else 0

        passed_match = re.search(
            r"=+\s*(\d+\s+passed[^i]*)\s+in\s+[\d\.]+s", content
        )
        passed_text = (
            passed_match.group(1).strip()
            if passed_match
            else f"{errors_count} errors, "
        )

        summary = f"{passed_text} (coverage {coverage}%)"

        coverage = (
            cov_errs - 1
            if "error" in passed_text or "errors" in passed_text
            else coverage
        )
        coverage = (
            cov_warn - 1
            if "warning" in passed_text or "warnings" in passed_text
            else coverage
        )

        return colorize_test(float(coverage), summary)

    elif tool_name == "mypy":
        # Match success line (no errors)
        match_success = re.search(
            r"Success: no issues found in (\d+) source files", content
        )
        if match_success:
            files = int(match_success.group(1))
            summary = f"Errors: 0 in {files} files"
            return colorize_test(cov_warn + 1, summary)

        # Match error line, e.g. "Found 1 error in 1 file (checked 4 source files)"
        match_error = re.search(
            r"Found (\d+) errors? in \d+ files? \(checked (\d+) source files\)",
            content,
        )
        if match_error:
            errors = int(match_error.group(1))
            files = int(match_error.group(2))
            summary = f"Errors: {errors} in {files} files"
            score = max(0, 100 * (1 - float(errors) / float(files)))
            print(score)
            return colorize_test(score, summary)

        # Fallback if neither pattern matches
        return "mypy output info not found"

    elif tool_name == "pylint":
        # Look for pylint score line like:
        # "Your code has been rated at 8.50/10"
        match = re.search(r"rated at ([0-9\.]+)/10", content)
        if match:
            score = float(match.group(1))
            summary = f"Score: {score}/10"
            return colorize_test(score * 10, summary)
        else:
            return "Score: Not found"

    elif tool_name == "interrogate":
        # Look for coverage percentage line like:
        # "Coverage: 98.2%"
        match = re.search(r"actual:\s*([0-9\.]+)%", content)
        if match:
            score = float(match.group(1))
            summary = f"Coverage: {score}%"
            return colorize_test(score, summary)
        else:
            return "Coverage: Not found"

    else:
        return "No score extraction available"


def check_globscore():
    if globscore <= 5:
        color = RED
    elif globscore <= 7:
        color = YELLOW
    else:
        color = GREEN
    summary = f"\nGlobal score: {globscore}/8"
    print(f"{color}{summary}{RESET}")


def main():
    if sys.platform.startswith("win"):
        os.system("")
    files = read_mypy_files_list()

    for entry in commands:
        if entry["name"] == "pylint":
            entry["cmd"] = ["pylint"] + files
        print(f"Running {entry['name']}...")
        run_command(entry["cmd"], entry["output"])
        score = extract_score(entry["name"], entry["output"])
        print(f"→ {entry['name']} score: {score}")


if __name__ == "__main__":
    main()
