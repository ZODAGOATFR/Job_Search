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
    
def scrape_fake_jobs_to_csv(out_path: Path) -> int:
    """
    Scrape fake job postings and write to CSV with header:
    Job Title, Company, Location, Date Posted
    """
    url = "https://realpython.github.io/fake-jobs/"
    resp = requests.get(url, headers=HEADERS, timeout=TIMEOUT)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")

    cards = soup.select("div.card-content")  # find-by-class example
    rows = []
    for c in cards:
        title = (c.select_one("h2.title") or {}).get_text(strip=True) if c.select_one("h2.title") else ""
        company = (c.select_one("h3.subtitle") or {}).get_text(strip=True) if c.select_one("h3.subtitle") else ""
        location = (c.select_one("p.location") or {}).get_text(strip=True) if c.select_one("p.location") else ""
        date_posted = (c.select_one("time") or {}).get_text(strip=True) if c.select_one("time") else ""
        rows.append([title, company, location, date_posted])

    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["Job Title", "Company", "Location", "Date Posted"])
        w.writerows(rows)

    return len(rows)


def main():
    parser = argparse.ArgumentParser(description="Job Search helper CLI")
    sub = parser.add_subparsers(dest="cmd")

    # Welcome (ASCII art + purpose)
    sub.add_parser("welcome", help="Show banner and explain purpose")

    # XULA mission
    sub.add_parser("xula", help="Print XULA mission statement")

    # Morehouse mission
    sub.add_parser("morehouse", help="Print Morehouse mission statement")

    # Fake jobs -> CSV
    pj = sub.add_parser("fakejobs", help="Scrape fake jobs to CSV")
    pj.add_argument("--out", default="fake_jobs.csv", help="Output CSV path")

    args = parser.parse_args()

    # Default: show banner/purpose if no subcommand
    if not args.cmd or args.cmd == "welcome":
        welcome_and_purpose()
        parser.print_help()
        return

    if args.cmd == "xula":
        print(scrape_xula_mission())
        return

    if args.cmd == "morehouse":
        print(scrape_morehouse_mission())
        return

    if args.cmd == "fakejobs":
        count = scrape_fake_jobs_to_csv(Path(args.out))
        print(f"Wrote {count} rows to {args.out}")
        return

if __name__ == "__main__":
    main()