import re

import requests

# Read the coverage.txt file
with open("coverage.txt") as file:
    coverage_data = file.read()

# Use regex to extract the coverage percentage (assuming it's in this format)
coverage_match = re.search(r"TOTAL\s+(\d+\.\d+)%", coverage_data)

if coverage_match:
    coverage_percentage = coverage_match.group(1)
    print(f"Coverage: {coverage_percentage}%")

    # Create a badge using the Shields.io API
    badge_url = f"https://img.shields.io/badge/coverage-{coverage_percentage}%25-brightgreen"

    # Optionally, download the badge image
    response = requests.get(badge_url)
    with open("coverage-badge.svg", "wb") as badge_file:
        badge_file.write(response.content)

    print("Badge created and saved as coverage-badge.svg")
else:
    print("Could not find coverage percentage in coverage.txt")
