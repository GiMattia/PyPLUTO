import re


def _convert_value(value):
    """Convert a string value to its appropriate type. This function
    attempts to convert a string value into a boolean, integer, float,
    or leave it as a string if it cannot be converted.

    Returns
    -------
    bool | int | float | str
        The converted value, which can be a boolean, integer, float, or the
        original string if conversion is not possible.

    Parameters
    ----------
    value : str
        The string value to convert.

    """
    # Convert the value to uppercase to handle case-insensitive comparisons
    value_upper = value.upper()

    # Check for boolean values first
    if value_upper in {"YES", "TRUE"}:
        return True
    if value_upper in {"NO", "FALSE"}:
        return False

    # Try to convert to an integer or float, if possible
    try:
        return float(value) if "." in value or "e" in value else int(value)
    except ValueError:
        return value


def _read_defh(self, filepath):
    """Read a header file and extract definitions.

    This function reads a header file, extracts lines that start with
    '#define', and converts the values to their appropriate types (boolean,
    integer, float, or string).

    Returns
    -------
    dict
        A dictionary where keys are the defined names and values are the
        converted values.

    Parameters
    ----------
    filepath : str
        The path to the header file to read.

    """
    # Read the file, check if a line starts with '#define',
    # and split the line into key and value.
    # Convert the value using _convert_value function.
    with open(filepath) as file:
        # Return a dictionary comprehension that processes each line
        return {
            key: _convert_value(value)
            for line in file
            if line.strip().startswith("#define")
            for _, key, value in [re.split(r"\s+", line.strip(), maxsplit=2)]
        }


def _read_plini(self, path):
    """Read the pluto.ini file and extract relevant sections.

    This function reads the pluto.ini file, extracts sections that are of
    interest (Solver, Parameters, Boundary, Time), and converts the values to
    their appropriate types (boolean, integer, float, or string).

    Returns
    -------
    dict
        A dictionary where keys are the parameter names and values are the
        converted values.

    Parameters
    ----------
    path : str
        The path to the pluto.ini file to read.

    """
    # Define the sections we are interested in
    wanted_sections = {"Solver", "Parameters", "Boundary", "Time"}
    plini = {}

    # Regular expressions to match sections and entries in the pluto.ini file
    section_re = re.compile(r"\[(.+)]")
    entry_re = re.compile(r"^(\w[\w\-\d]*)\s+(.*)$")

    current_sec = None

    # Open the file and read it line by line
    with open(path) as f:
        for line in f:
            line = line.strip()

            if not line or line.startswith("#"):
                continue

            # Check if the line is a section header or an entry
            if section_match := section_re.match(line):
                section = section_match.group(1)
                current_sec = section if section in wanted_sections else None
                continue

            # If we are not in a wanted section, skip the line
            if not current_sec:
                continue

            # If we are in a wanted section, check for entries
            # and convert the values using _convert_value function
            if entry_match := entry_re.match(line):
                key, value = entry_match.groups()
                plini[key] = _convert_value(value.strip())

    # Return the dictionary containing the extracted parameters
    return plini
