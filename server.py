from flask import Flask, render_template, request, redirect
import data_manager as dmg
import time, calendar

app = Flask(__name__)

web_pages = {"home_page": "home.html", "question_page": "question.html", "add_question_page": "add_question.html", 
            "new_answer_page": "new_answer.html"
            }


@app.route("/")
@app.route("/list")
def home():
    if dmg.get_all_questions() is False: return render_template(web_pages["home_page"], questions="", table_heading="", empty=True)
    else:
        all_questions = dmg.get_all_questions()
        print(all_questions)
        table_heading = ["ID", "SUBMISSION TIME", "VIEWS", "VOTES", "TITLE", "QUESTION", "IMAGE"]
        return render_template(web_pages["home_page"], questions=all_questions, table_heading=table_heading, empty=False)


@app.route("/question/<question_id>")
def question(question_id):
    question = dmg.get_question_by_id(question_id)
    answers_for_question = dmg.find_answers_by_id(question_id)
    return render_template(web_pages["question_page"], question=question)


@app.route("/list/add-question", methods=["GET", "POST"])
def add_question():
    if request.method == "POST":
        question_id = dmg.find_next_question_index()
        question_info = {"id": question_id, "submission_time": calendar.timegm(time.gmtime()), "view_number": "0", "vote_number": "0", 
                        "title": request.form["title"], "message": request.form["message"], "image": ""}
        dmg.add_question_to_file(question_info)
        return redirect("/question/{0}".format(question_id))
    return render_template(web_pages["add_question_page"])


@app.route("/question/<question_id>/new-answer")
def new_answer(question_id):
    return render_template(web_pages["new_answer_page"])


if __name__ == "__main__":
    app.run(port=5000, debug=True)