import requests
from urllib.parse import quote
from concurrent.futures import as_completed
from requests_futures.sessions import FuturesSession
from bs4 import BeautifulSoup
import math
import joblib
import os

classifier = joblib.load('solution-model.pkl')

def get_solutions(question):
    
    q = quote(question)
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.71 Safari/537.36"}
    x = requests.get(f"https://customsearch.googleapis.com/customsearch/v1?cx={os.environ['GOOGLE_CX']}&key={os.environ['GOOGLE_KEY']}&q={q}", headers = headers).json()
    urls = []
    for i in x["items"]:
        # remove ?tstart=0 which causes infinite loop
        urls.append(i["link"].split('?')[0])
    new_urls = urls[:5]

    post_htmls = []
    post_texts = []
    post_helpfuls = []

    long_forums = []

    rate_limited = []

    with FuturesSession() as session:
        futures = [session.get(url, headers = headers) for url in new_urls]
        for future in as_completed(futures):
            resp = future.result()
            soup = BeautifulSoup(resp.content, "lxml")

            replies = soup.find("div", class_="all-replies-content")

            for post in replies.find_all("article"):
                post_html = post.find(class_="content-post-body-content")
                post_text = post_html.get_text()
                post_helpful = post.find("span", attrs={"data-action": "content-helpful-vote"})["data-helpful-count"]
                if post_helpful == "":
                    post_helpful = 0
                else:
                    post_helpful = int(post_helpful)

                post_htmls.append(str(post_html))
                post_texts.append(post_text)
                post_helpfuls.append(post_helpful)
            
            num_posts = int(soup.find("main")["data-analytics-replies-count"])
            if num_posts > 15:
                long_forums.append([num_posts, resp.request.url])

        # for forums with multiple pages
        for forum in long_forums:
            num_posts = forum[0]
            url = forum[1]
            forum_futures = [session.get(f"{url}?page={i}", headers = headers) for i in range(2, math.ceil(num_posts / 15))]
            for forum_future in as_completed(forum_futures):
                resp = forum_future.result()


                if resp.status_code == 200:
                    soup = BeautifulSoup(resp.content, "lxml")



                    replies = soup.find("div", class_="all-replies-content")

                    for post in replies.find_all("article"):
                        post_html = post.find(class_="content-post-body-content")
                        post_text = post_html.get_text()
                        post_helpful = post.find("span", attrs={"data-action": "content-helpful-vote"})["data-helpful-count"]
                        if post_helpful == "":
                            post_helpful = 0
                        else:
                            post_helpful = int(post_helpful)

                        post_htmls.append(str(post_html))
                        post_texts.append(post_text)
                        post_helpfuls.append(post_helpful)
                # else:
                #     rate_limited.append(resp.request.url)

        # rate_limited_futures = [session.get(url, headers = headers) for url in rate_limited]
        # for rate_limited_future in as_completed(rate_limited_futures):
        #     resp = rate_limited_future.result()

        #     if resp.status_code == 200:
        #         soup = BeautifulSoup(resp.content, "lxml")

        #         replies = soup.find(class_="all-replies-content")

        #         for post in replies.find_all("article"):
        #             post_html = post.find(class_="content-post-body-content")
        #             post_text = post_html.get_text()
        #             post_helpful = post.find(class_="button-white").get_text()[9:][:-1]
        #             if post_helpful == "":
        #                 post_helpful = 0
        #             else:
        #                 post_helpful = int(post_helpful)

        #             post_htmls.append(str(post_html))
        #             post_texts.append(post_text)
        #             post_helpfuls.append(post_helpful)

            
        


    predictions = classifier.predict(post_texts)
    solutions = []

    # for logging
    solutions_text = []

    for i in range(len(predictions)):
        if predictions[i] == 1:
            solutions.append([post_helpfuls[i], post_htmls[i]])
            solutions_text.append([post_helpfuls[i], post_texts[i]])

    solutions.sort(key=lambda x: x[0], reverse = True)
    solutions_text.sort(key=lambda x: x[0], reverse = True)

    return (solutions, solutions_text, urls)