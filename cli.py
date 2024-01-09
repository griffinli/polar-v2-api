import requests
import requests_cache
from urllib.parse import quote
from bs4 import BeautifulSoup
from solutions import get_solutions
import os

requests_cache.install_cache('circle_cache')

query = input("What's your question? ")

q = quote(query)

x = requests.get(f"https://customsearch.googleapis.com/customsearch/v1?cx={os.environ['GOOGLE_CX']}&key={os.environ['GOOGLE_KEY']}&q={q}").json()

links = []
for i in x["items"]:
    # removes ?tstart=0 which doesn't break out the loop
    links.append(i["link"].split('?')[0])

links = links[:5]

titles = []

for link in links:
    page = requests.get(link)
    soup = BeautifulSoup(page.content, "html.parser")
    title = soup.find("span", {"data-action":"content-post-title-text"}).get_text()

    titles.append(title)

print("Which of these best corresponds to your question?")
for i in range(len(titles)):
    print(str(i + 1) + ": " + titles[i])

print()

# gets index
x = int(input()) - 1
print()


results, links = get_solutions(titles[x])

for i in results:
    print(i)
print(links)



