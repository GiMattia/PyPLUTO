from .libraries import *


def _convert_value(value):
    value_upper = value.upper()
    if value_upper in {"YES", "TRUE"}:
        return True
    if value_upper in {"NO", "FALSE"}:
        return False
    try:
        return float(value) if "." in value else int(value)
    except ValueError:
        return value  # return original string if not convertible


def _read_defh(self, filepath):
    with open(filepath) as file:
        return {
            key: _convert_value(value)
            for line in file
            if line.strip().startswith("#define")
            for _, key, value in [re.split(r"\s+", line.strip(), maxsplit=2)]
        }


def _read_plini(self, path):
    wanted_sections = {"Solver", "Parameters", "Boundary", "Time"}
    plini = {}

    section_re = re.compile(r"\[(.+)]")
    entry_re = re.compile(r"^(\w[\w\-\d]*)\s+(.*)$")

    current_sec = None

    with open(path, "r") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue

            if section_match := section_re.match(line):
                section = section_match.group(1)
                current_sec = section if section in wanted_sections else None
                continue

            if not current_sec:
                continue

            if entry_match := entry_re.match(line):
                key, value = entry_match.groups()
                plini[key] = _convert_value(value.strip())

    return plini
