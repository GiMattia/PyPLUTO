import re
from collections import defaultdict


def extract_doc_params(docstring: str) -> dict[str, str]:

    if not docstring:
        return {}

    lines = docstring.strip().splitlines()
    lines = [line.rstrip() for line in lines]

    param_docs = {}
    in_params = False
    i = 0

    # Step 1: Locate the Parameters section
    while i < len(lines):
        if lines[i].strip().lower() == "parameters":
            i += 1
            while i < len(lines) and re.match(r"^\s*-{3,}", lines[i]):
                i += 1
            in_params = True
            break
        i += 1

    # Step 2: Extract param blocks
    current_param = None
    current_desc = []

    while in_params and i < len(lines):
        line = lines[i]

        # Match: param : type (e.g. "verbose : bool | None")
        param_match = re.match(r"^\s*(\w+)\s*:\s*(.+)", line)
        if param_match:
            # Save the previous param before starting a new one
            if current_param and current_desc:
                param_docs[current_param] = " ".join(current_desc).strip()

            current_param = param_match.group(1)
            current_desc = []
            i += 1
            continue

        # If line is indented, it's part of description
        if line.startswith(" ") or line.startswith("\t"):
            current_desc.append(line.strip())
        elif line.strip() == "":
            pass  # blank line, skip
        else:
            # Stop when something that’s not a param or indentation shows up
            if current_param and current_desc:
                param_docs[current_param] = " ".join(current_desc).strip()
            break  # exit param block

        i += 1

    # Catch last param at EOF
    if current_param and current_desc:
        param_docs[current_param] = " ".join(current_desc).strip()

    return param_docs


# === TEST ===

example_docstrings = [
    """
    Parameters
    ----------
    verbose : bool | None
        something something
        something else
    limit : int
        Maximum number of items.
    pippo : int
        Pippo
    """,
    """
    Parameters
    ----------
    verbose : bool | None
        Whether to enable output messages.
    limit : int
        Maximum number of elements in the result.
    pippo : int
        Pippo
    """,
]

param_explanations = defaultdict(set)
for i, doc in enumerate(example_docstrings):
    print(f"\n🔍 Docstring {i+1}")
    params = extract_doc_params(doc)
    for name, description in params.items():
        print(f"  - {name}: {description}")
        param_explanations[name].add(description)

conflict_found = False
for param, explanations in param_explanations.items():
    if len(explanations) > 1:
        conflict_found = True
        print(f"\n⚠️ Conflict for parameter '{param}':")
        for desc in explanations:
            print(f"  - {desc}")

if not conflict_found:
    print("\n✅ No conflicting docstrings found.")
