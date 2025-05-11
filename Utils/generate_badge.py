import argparse
import re
import subprocess
import sys
from pathlib import Path

BADGE_TEMPLATE = """<badge>
  <label>{label}</label>
  <message>{message}</message>
  <color>{color}</color>
</badge>
"""


COLORS = {
    "coverage": lambda p: "red" if p < 50 else "orange" if p < 80 else "green",
    "pylint": lambda p: "red" if p < 5 else "orange" if p < 8 else "green",
    "interrogate": lambda p: (
        "red" if p < 50 else "orange" if p < 80 else "green"
    ),
}


def run_cmd(cmd, capture=False):
    print(f">>> {cmd}")
    if capture:
        result = subprocess.run(
            cmd, shell=True, capture_output=True, text=True, check=False
        )
        if result.returncode != 0:
            print(result.stderr)
            sys.exit(result.returncode)
        return result.stdout
    else:
        result = subprocess.run(cmd, shell=True, check=False)
        if result.returncode != 0:
            sys.exit(result.returncode)


def get_coverage():
    run_cmd("coverage run -m pytest")
    out = run_cmd("coverage report", capture=True)
    for line in out.splitlines():
        if "TOTAL" in line:
            percent = int(line.strip().split()[-1].replace("%", ""))
            return percent
    raise ValueError("Could not find coverage percent")


def get_pylint():
    out = run_cmd("pylint .", capture=True)
    match = re.search(r"Your code has been rated at ([0-9.]+)/10", out)
    if match:
        score = float(match.group(1))
        return int(score * 10)
    raise ValueError("Could not parse pylint score")


def get_interrogate():
    out = run_cmd("interrogate -q -c pyproject.toml .", capture=True)
    match = re.search(r"([0-9]+)% documentation coverage", out)
    if match:
        return int(match.group(1))
    raise ValueError("Could not find interrogate percent")


def write_badge(tool, value):
    label = tool
    message = f"{value}%"
    color = COLORS[tool](value)
    xml = BADGE_TEMPLATE.format(label=label, message=message, color=color)
    Path(f"Utils/{tool}.xml").write_text(xml)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--tool", choices=["coverage", "pylint", "interrogate"])
    args = parser.parse_args()

    Path("Utils").mkdir(exist_ok=True)

    if args.tool == "coverage":
        val = get_coverage()
    elif args.tool == "pylint":
        val = get_pylint()
    elif args.tool == "interrogate":
        val = get_interrogate()

    write_badge(args.tool, val)
