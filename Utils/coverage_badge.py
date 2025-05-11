import requests


def generate_badge(coverage_percentage):
    """This function will generate a badge with coverage info.

    :param coverage_percentage: Coverage percentage as a float (e.g., 85.5)

    """
    badge_url = f"https://img.shields.io/badge/coverage-{coverage_percentage}%25-brightgreen"
    badge_file = "coverage_badge.svg"

    # Download and save the badge
    response = requests.get(badge_url)
    if response.status_code == 200:
        with open(badge_file, "wb") as file:
            file.write(response.content)
        print(f"Badge saved as {badge_file}")
    else:
        print("Failed to generate badge")


if __name__ == "__main__":
    # Example: Generate a badge for 90% coverage
    generate_badge(90.0)
