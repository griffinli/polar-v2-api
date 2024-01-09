import requests
from concurrent.futures import as_completed
from requests_futures.sessions import FuturesSession
from bs4 import BeautifulSoup
from urllib.parse import quote
import os


def get_questions(question):

    q = quote(question)
    x = requests.get(f"https://customsearch.googleapis.com/customsearch/v1?cx={os.environ['GOOGLE_CX']}&key={os.environ['GOOGLE_KEY']}&q={q}").json()

    # if response.status_code == 200:
    urls = []
    for i in x["items"]:
        # remove ?tstart=0 which causes infinite loop
        urls.append(i["link"].split('?')[0])

    new_urls = urls[:5]

    questions = []

    with FuturesSession() as session:
        futures = [session.get(url) for url in new_urls]
        for future in as_completed(futures):
            resp = future.result()
            soup = BeautifulSoup(resp.content, "lxml")
            title = soup.find("span", {"data-action":"content-post-title-text"}).get_text()
            questions.append(title)
    
    return (questions, urls)