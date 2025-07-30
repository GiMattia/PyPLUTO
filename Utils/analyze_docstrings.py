import csv
import json
import re
from collections import defaultdict
from pathlib import Path

IN_FILE = Path(__file__).parent / "exposed_kwargs.json"
OUT_FILE = Path(__file__).parent / "docstring_report.csv"
CONFLICT_FILE = Path(__file__).parent / "docstring_conflicts.csv"


def extract_doc_params(docstring: str) -> dict[str, str]:
    """Extract parameter descriptions from a Numpy-style docstring.
    Supports leading dashes, newline after type, and multi-line descriptions.
    """
    if not docstring:
        return {}

    param_docs = {}
    lines = docstring.splitlines()
    in_params = False
    current_param = None
    type_line = ""
    desc_lines = []

    for line in lines:
        stripped = line.strip()

        if not in_params:
            if stripped.lower() == "parameters":
                in_params = True
            continue

        # Stop at next section
        if in_params and re.match(r"^[A-Z][A-Za-z0-9_ ]+$", stripped):
            break

        # Match parameter line, support leading '-'
        match = re.match(r"^-?\s*([a-zA-Z_][\w]*)\s*:\s*(.*)", stripped)
        if match:
            if current_param and type_line:
                full_desc = f"{type_line}\n{' '.join(desc_lines).strip()}"
                param_docs[current_param] = full_desc.strip()
            current_param = match.group(1)
            type_line = f"{current_param} : {match.group(2).strip()}"
            desc_lines = []
        elif current_param and stripped:
            desc_lines.append(stripped)

    # Save last param
    if current_param and type_line:
        full_desc = f"{type_line}\n{' '.join(desc_lines).strip()}"
        param_docs[current_param] = full_desc.strip()

    return param_docs


def analyze_full_param_coverage():
    with open(IN_FILE, encoding="utf-8") as f:
        data = json.load(f)

    # Track all declared params and docstring matches
    global_param_status = defaultdict(lambda: {"ok": 0, "missing": 0})
    param_descriptions = defaultdict(set)

    for entry in data:
        declared_params = set(entry.get("args", []) + entry.get("kwargs", []))
        doc_params = extract_doc_params(entry.get("docstring", ""))
        for param in declared_params:
            if param in doc_params:
                global_param_status[param]["ok"] += 1
                param_descriptions[param].add(doc_params[param])
            else:
                global_param_status[param]["missing"] += 1

    # Write status report
    with open(OUT_FILE, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["param", "status", "description"])
        for param, counts in sorted(global_param_status.items()):
            descs = param_descriptions.get(param, set())
            if counts["ok"] == 0:
                writer.writerow([param, "missing", ""])
            elif len(descs) == 1:
                writer.writerow([param, "ok", list(descs)[0]])
            else:
                writer.writerow([param, "conflict", ""])

    # Write conflicts separately
    with open(CONFLICT_FILE, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["param", "conflicting_descriptions"])
        for param, descriptions in sorted(param_descriptions.items()):
            if len(descriptions) > 1:
                joined = " ||| ".join(sorted(descriptions))
                writer.writerow([param, joined])


if __name__ == "__main__":
    analyze_full_param_coverage()
