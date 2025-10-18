import requests
from bs4 import BeautifulSoup
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