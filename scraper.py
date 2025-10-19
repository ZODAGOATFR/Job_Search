import argparse, csv, sys, textwrap
from pathlib import Path

import requests
from bs4 import BeautifulSoup

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
}
TIMEOUT = 30

ASCII = r"""
__        __   _                                        
\ \      / /__| | ___ ___  _ __ ___   ___    
 \ \ /\ / / _ \ |/ __/ _ \| '_ ` _ \ / _ \  
  \ V  V /  __/ | (_| (_) | | | | | |  __/   
   \_/\_/ \___|_|\___\___/|_| |_| |_|\___|  
                                                          
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
    
def _txt(el) -> str:
    return el.get_text(strip=True) if el else ""
    
def scrape_xula_mission():
    """Fetch and return XULA's mission statement text."""
    URL = "https://www.xula.edu/about/mission-values.html"
    response = requests.get(URL, headers=HEADERS, timeout=TIMEOUT)
    response.raise_for_status()  # raises an error if request fails
    soup = BeautifulSoup(response.content, 'html.parser')
    
    container = soup.find("div", class_="editorarea")
    if not container:
        return "Mission statement not found."

    # Prefer a paragraph that includes the hint substring if present.
    for p in container.find_all("p"):
        t = _txt(p)
        if "founded by Saint" in t or "mission" in t.lower():
            return t

    return _txt(container)
    
def scrape_morehouse_mission():
    """Fetch and return Morehouse College's mission statement text."""
    URL = "https://morehouse.edu/about/mission-and-values"
    response = requests.get(URL, headers=HEADERS, timeout=TIMEOUT)
    response.raise_for_status()  # raise error if request fails
    soup = BeautifulSoup(response.content, 'html.parser')
    
    paras = soup.select("p.paragraph")
    if paras:
        return " ".join(_txt(p) for p in paras if _txt(p))
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

    cards = soup.select("div.card-content")
    rows = []
    for c in cards:
        title = _txt(c.select_one("h2.title"))
        company = _txt(c.select_one("h3.subtitle"))
        location = _txt(c.select_one("p.location"))
        date_posted = _txt(c.select_one("time"))
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

    try:
        if args.cmd == "xula":
            print(scrape_xula_mission())
        elif args.cmd == "morehouse":
            print(scrape_morehouse_mission())
        elif args.cmd == "fakejobs":
            count = scrape_fake_jobs_to_csv(Path(args.out))
            print(f"Wrote {count} rows to {args.out}")
        else:
            parser.print_help()
    except requests.HTTPError as e:
        print(f"HTTP error: {e}", file=sys.stderr)
        sys.exit(2)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()