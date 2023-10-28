from flask import Flask, request
from flask_cors import CORS, cross_origin
import json

from solutions import get_solutions
from questions import get_questions

import airtablelog


app = Flask(__name__)
cors = CORS(app)


@app.route("/")
def home():
    return "Polar"


@app.route("/questions", methods=["POST"])
@cross_origin()
def questions():
    data = request.get_json()

    question = data["question"]
    uuid = data["uuid"]
    questions, urls = get_questions(question)
    
    record = airtablelog.log_questions(uuid, question, questions, urls)

    return_json = {"questions": questions, "sessionId": record["id"]}
    return json.dumps(return_json)



@app.route("/solutions", methods=["POST"])
@cross_origin()
def solutions():
    data = request.get_json()

    question = data["question"]
    session_id = data["sessionId"]
    solutions_html, solutions_text, urls = get_solutions(question)
    return_json = {"solutions": solutions_html}

    airtablelog.log_solutions(session_id, question, urls, solutions_text, solutions_html)

    return json.dumps(return_json)
