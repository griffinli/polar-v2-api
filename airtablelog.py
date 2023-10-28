import json
import os
from dotenv import load_dotenv
from pyairtable import Table
import requests
from time import gmtime, strftime

load_dotenv()

airtable_api_key = os.environ["AIRTABLE_API_KEY"]
airtable_base_id = os.environ["AIRTABLE_BASE_ID"]

table = Table(airtable_api_key, airtable_base_id, '0.1.0')


def log_questions(uuid, user_question, questions, urls):

    current_time = strftime('%Y-%m-%dT%H:%M:%SZ', gmtime())

    record = table.create({
        "Time": current_time,
        "UUID": uuid,
        "User question": user_question,
        "Questions": json.dumps(questions),
        "Question URLs": json.dumps(urls)
    })

    return record

def log_solutions(session_id, question, solution_urls, solutions_text, solutions_html):

    
    record = table.update(session_id, {
        "User selection": question,
        "Solution URLs": json.dumps(solution_urls),
        "Solutions Text": json.dumps(solutions_text),
        "Solutions HTML": json.dumps(solutions_html)
    })

    return record
