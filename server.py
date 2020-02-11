from flask import Flask, render_template, request, redirect
import data_manager as dmg
import time, calendar

app = Flask(__name__)

web_pages = {"home_page": "home.html", "question_page": "question.html", "add_question_page": "add_question.html", 
            "new_answer_page": "new_answer.html"
            }


@app.route("/", methods=["GET", "POST"])
@app.route("/list", methods=["GET", "POST"])
def home():
    if request.method == "POST":
        sort_info = dict(request.form)
        all_questions = dmg.sort_questions(sort_info["sort_by"], sort_info["order"])
        table_heading = ["ID", "SUBMISSION TIME", "VIEWS", "VOTES", "TITLE", "QUESTION", "IMAGE"]
        return render_template(web_pages["home_page"], questions=all_questions, table_heading=table_heading, empty=False, default_sort_by=sort_info["sort_by"], default_order=sort_info["order"])
    if dmg.get_all_questions() is False: return render_template(web_pages["home_page"], questions="", table_heading="", empty=True)
    else:
        all_questions = dmg.sort_questions("submission_time", "descending")
        table_heading = ["ID", "SUBMISSION TIME", "VIEWS", "VOTES", "TITLE", "QUESTION", "IMAGE"]
        return render_template(web_pages["home_page"], questions=all_questions, table_heading=table_heading, empty=False, default_sort_by="submission time", default_order="descending")


@app.route("/question/<question_id>")
def question(question_id):
    dmg.add_view(question_id)
    empty = False
    question = dmg.get_question_by_id(question_id)
    answers_for_question = dmg.find_answers_by_question_id(question_id)
    if answers_for_question == None:
        empty = True
    return render_template(web_pages["question_page"], question=question, answers=answers_for_question, empty=empty, question_id=question_id)


@app.route("/list/add-question", methods=["GET", "POST"])
def add_question():
    if request.method == "POST":
        question_id = dmg.find_next_question_index()
        question_info = {"id": question_id, "submission_time": calendar.timegm(time.gmtime()), "view_number": "0", "vote_number": "0", 
                        "title": request.form["title"], "message": request.form["message"], "image": ""}
        dmg.add_question_to_file(question_info)
        return redirect("/question/{0}".format(question_id))
    return render_template(web_pages["add_question_page"])


@app.route("/question/<question_id>/new-answer", methods=["GET", "POST"])
def new_answer(question_id):
    question = dmg.get_question_by_id(question_id)
    if request.method == "POST":
        answer_id = dmg.find_next_answer_index()
        answer_info = {"id": answer_id, "submission_time": calendar.timegm(time.gmtime()), 
                        "vote_number": "0", "question_id": question_id, "message": request.form['answer'], "image": ""}
        dmg.add_answer_to_question(answer_info)
        return redirect("/question/{0}".format(question_id))
    return render_template(web_pages["new_answer_page"], question=question)


@app.route("/question/<question_id>/edit", methods=["GET", "POST"])
def edit_question(question_id):
    if request.method == "POST":
        edited_question_info = dict(request.form)
        dmg.edit_question(question_id, edited_question_info)
        return redirect("/question/{0}".format(question_id))
    question_info = dmg.get_question_by_id(question_id)
    return render_template("edit_question.html", question_info=question_info)


@app.route("/question/<question_id>/delete")
def delete_question(question_id):
    dmg.delete_question(question_id)
    return redirect("/")


if __name__ == "__main__":
    app.run(port=5000, debug=True)