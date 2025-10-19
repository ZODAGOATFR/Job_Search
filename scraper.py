import argparse, csv, sys, textwrap
from pathlib import Path

import requests
from bs4 import BeautifulSoup

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
}
TIMEOUT = 30

ASCII = r"""
   __        _     _           _                 _
  /__\  ___ | | __| | ___  ___| |__   ___   ___ | |_
 / \// / _ \| |/ _` |/ _ \/ __| '_ \ / _ \ / _ \| __|
/ _  \| (_) | | (_| |  __/\__ \ | | | (_) | (_) | |_
\/ \_/ \___/|_|\__,_|\___||___/_| |_|\___/ \___/ \__|

"""

def welcome_and_purpose():
    """TODO 3 + TODO 4: Pretty banner + explain app purpose"""
    print(ASCII)
    print("Welcome to the Job Search helper!\n")
    print(textwrap.fill(
        "This CLI shows how to: (1) scrape university mission statements "
        "with BeautifulSoup, (2) learn find-by-class selectors, and "
        "(3) scrape fake job postings and save them into a CSV "
        "file named fake_jobs.csv with the required columns.",
        width=78
    ))
    print()
    
def scrape_xula_mission():
    """Fetch and return XULA's mission statement text."""
    URL = "https://www.xula.edu/about/mission-values.html"
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
    response = requests.get(URL, headers=headers)
    response.raise_for_status()  # raises an error if request fails

    soup = BeautifulSoup(response.content, 'html.parser')
    mission_div = soup.find('div', class_='editorarea')

    if mission_div:
        return mission_div.get_text(strip=True)
    else:
        return "Mission statement not found."
    
def scrape_morehouse_mission():
    """Fetch and return Morehouse College's mission statement text."""
    URL = "https://morehouse.edu/about/mission-and-values"
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
    response = requests.get(URL, headers=headers)
    response.raise_for_status()  # raise error if request fails

    soup = BeautifulSoup(response.content, 'html.parser')
    mission_paragraph = soup.find('p', class_='paragraph')

    if mission_paragraph:
        return mission_paragraph.get_text(strip=True)
    else:
        return "Mission statement not found."


def main():
    print("\n\nHello, World from scraper.py!\n\n")
    URL = "https://www.xula.edu/about/mission-values.html"
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
    response = requests.get(URL, headers= headers)
    html_content = response.content
    soup = BeautifulSoup(html_content, 'html.parser')
    missionStatement = soup.find('div', class_ = 'editorarea')
    print(missionStatement.text)
    URL2 = "https://morehouse.edu/about/mission-and-values"
    response2 = requests.get(URL2, headers= headers)
    html_content2 = response2.content
    soup2 = BeautifulSoup(html_content2, 'html.parser')
    missionStatement2 = soup2.find('p', class_ = 'paragraph')
    print(missionStatement2.text)


if __name__ == "__main__":
    main()