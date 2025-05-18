import subprocess

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


def main():
    files = read_mypy_files_list()

    for entry in commands:
        if entry["name"] == "pylint":
            entry["cmd"] = ["pylint"] + files
        print(f"Running {entry['name']}...")
        run_command(entry["cmd"], entry["output"])
        print(f"→ Output written to {entry['output']}")


if __name__ == "__main__":
    main()
