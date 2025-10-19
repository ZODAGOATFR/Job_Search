from datetime import datetime
from typing import List, Tuple, Iterable


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

def _parse_date(s: str) -> datetime | None:
    """Best-effort date parser; extend formats as needed."""
    for fmt in ("%Y-%m-%d", "%b %d, %Y", "%B %d, %Y"):
        try:
            return datetime.strptime(s, fmt)
        except ValueError:
            continue
    return None

def _passes_filters(
    row: Tuple[str, str, str, str],
    include: Iterable[str],
    exclude: Iterable[str],
    location: str | None,
    since: datetime | None,
) -> bool:
    title, company, loc, date_str = row
    blob = f"{title} {company} {loc}".lower()

    if include and not all(term.lower() in blob for term in include):
        return False
    if exclude and any(term.lower() in blob for term in exclude):
        return False
    if location and location.lower() not in loc.lower():
        return False
    if since is not None:
        d = _parse_date(date_str)
        if not d or d < since:
            return False
    return True

    
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
    
def scrape_fake_jobs_to_csv(
    out_path: Path,
    include: List[str] | None = None,
    exclude: List[str] | None = None,
    location: str | None = None,
    since_str: str | None = None,
    dedupe: bool = False,
    sort_by: str | None = None,  # 'date' | 'title' | 'company' | 'location'
    limit: int | None = None,
) -> int:
    """
    Scrape fake job postings and write to CSV with header:
    Job Title, Company, Location, Date Posted

    Bonus:
      - include/exclude keyword filters (case-insensitive)
      - location contains filter
      - since (YYYY-MM-DD) date cutoff
      - dedupe by (title, company, location)
      - sort by date/title/company/location
      - limit N rows after sort
    """
    url = "https://realpython.github.io/fake-jobs/"
    resp = requests.get(url, headers=HEADERS, timeout=TIMEOUT)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")

    cards = soup.select("div.card-content")
    rows: List[Tuple[str, str, str, str]] = []
    for c in cards:
        title = _txt(c.select_one("h2.title"))
        company = _txt(c.select_one("h3.subtitle"))
        loc = _txt(c.select_one("p.location"))
        date_posted = _txt(c.select_one("time"))
        rows.append((title, company, loc, date_posted))

    # Filters
    since_dt = None
    if since_str:
        try:
            since_dt = datetime.strptime(since_str, "%Y-%m-%d")
        except ValueError:
            raise ValueError("Invalid --since format. Use YYYY-MM-DD.")

    rows = [r for r in rows if _passes_filters(
        r, include or [], exclude or [], location, since_dt
    )]

    # Dedupe by (title, company, location)
    if dedupe:
        seen = set()
        new_rows = []
        for r in rows:
            key = (r[0].lower(), r[1].lower(), r[2].lower())
            if key not in seen:
                seen.add(key)
                new_rows.append(r)
        rows = new_rows

    # Sort
    if sort_by:
        idx_map = {"title": 0, "company": 1, "location": 2, "date": 3}
        if sort_by not in idx_map:
            raise ValueError("Invalid --sort. Choose: date, title, company, location")
        idx = idx_map[sort_by]
        if sort_by == "date":
            rows.sort(key=lambda r: (_parse_date(r[3]) or datetime.min), reverse=True)
        else:
            rows.sort(key=lambda r: (r[idx] or "").lower())

    # Limit
    if isinstance(limit, int) and limit > 0:
        rows = rows[:limit]

    # Write CSV
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["Job Title", "Company", "Location", "Date Posted"])
        for r in rows:
            w.writerow(list(r))

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
    pj = sub.add_parser("fakejobs", help="Scrape fake jobs to CSV (with filters)")
    pj.add_argument("--out", default="fake_jobs.csv", help="Output CSV path")
    pj.add_argument("--include", nargs="*", default=[], help="Require these terms in title/company/location")
    pj.add_argument("--exclude", nargs="*", default=[], help="Exclude rows containing these terms")
    pj.add_argument("--location", default=None, help="Only keep rows whose location contains this text")
    pj.add_argument("--since", dest="since_str", default=None, help="Only keep rows with Date Posted >= YYYY-MM-DD")
    pj.add_argument("--dedupe", action="store_true", help="Remove duplicates by (title, company, location)")
    pj.add_argument("--sort", dest="sort_by", choices=["date", "title", "company", "location"], default=None, help="Sort rows by this column")
    pj.add_argument("--limit", type=int, default=None, help="Keep only the first N rows after sort")


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