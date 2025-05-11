import argparse
import subprocess
import sys


def run(cmd):
    print(f">>> {cmd}")
    result = subprocess.run(cmd, shell=True, check=False)
    if result.returncode != 0:
        sys.exit(result.returncode)


def generate_coverage():
    run("coverage run -m pytest")
    run("coverage report")
    run("coverage-badge -o Utils/coverage.svg -f")


def generate_pylint():
    run("pylint 'Src/pyPLUTO' --exit-zero > pylint.log")
    with open("pylint.log") as f:
        score_line = [
            line for line in f if "Your code has been rated at" in line
        ]
    print(score_line)
    if score_line:
        score = float(score_line[0].split("at ")[1].split("/")[0])
    else:
        score = 0.0
    color = "red" if score < 5 else "orange" if score < 8 else "green"
    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="120" height="20">
<rect width="60" height="20" fill="#555"/>
<rect x="60" width="60" height="20" fill="{color}"/>
<text x="30" y="14" fill="#fff" font-family="Verdana" font-size="11">pylint</text>
<text x="90" y="14" fill="#fff" font-family="Verdana" font-size="11">{score:.1f}/10</text>
</svg>"""
    with open("Utils/pylint.svg", "w") as f:
        f.write(svg)


def generate_interrogate():
    run("interrogate -q -f 100 your_module_name_here > interrogate.log")
    with open("interrogate.log") as f:
        line = f.readline()
        percent = float(line.strip().rstrip("%"))
    color = "red" if percent < 50 else "orange" if percent < 80 else "green"
    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="150" height="20">
<rect width="80" height="20" fill="#555"/>
<rect x="80" width="70" height="20" fill="{color}"/>
<text x="40" y="14" fill="#fff" font-family="Verdana" font-size="11">interrogate</text>
<text x="115" y="14" fill="#fff" font-family="Verdana" font-size="11">{percent:.1f}%</text>
</svg>"""
    with open("Utils/interrogate.svg", "w") as f:
        f.write(svg)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--tool", choices=["coverage", "pylint", "interrogate"], required=True
    )
    args = parser.parse_args()

    if args.tool == "coverage":
        generate_coverage()
    elif args.tool == "pylint":
        generate_pylint()
    elif args.tool == "interrogate":
        generate_interrogate()
