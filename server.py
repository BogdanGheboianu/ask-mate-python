from flask import Flask
import data_manager as dmg

app = Flask(__name__)


@app.route("/")
@app.route("/list")
def home():
    pass


@app.route("/question/<question_id>")
def question(question_id):
    pass


@app.route("/list/add-question")
def add_question():
    pass


@app.route("/question/<question_id>/new-answer")
def new_answer(question_id):
    pass


if __name__ == "__main__":
    app.run(port=5000, debug=True)