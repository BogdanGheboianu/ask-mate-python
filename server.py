from flask import Flask, render_template, request, redirect
import data_manager as dmg
import connection as con
import time, calendar

app = Flask(__name__)

web_pages = {"home_page": "home.html", "question_page": "question.html", "add_question_page": "add_question.html", 
            "new_answer_page": "new_answer.html"
            }

answer_file = "sample_data/answer.csv"
question_file = "sample_data/question.csv"

answer_fieldnames = ["id", "submission_time",
                      "vote_number", "question_id", "message", "image"]
                      
questions_fieldnames = ["id", "submission_time", "view_number",
                      "vote_number", "title", "message", "image"]

# MAIN ROUTES: home, question, add question, add answer            

@app.route("/", methods=["GET", "POST"])
@app.route("/list", methods=["GET", "POST"])
def home():
    '''
    "GET": displays the table with all the questions, the "ASK" button and the sorting functionality.
    "POST": gets the sorting criteria, sends it to data manager to execute the sorting and displays the home page based on the new result.
    '''
    if request.method == "POST":
        sort_info = dict(request.form)
        all_questions = dmg.sort_questions(sort_info["sort_by"], sort_info["order"])
        table_heading = ["ID", "SUBMISSION TIME", "VIEWS", "VOTES", "TITLE", "QUESTION", "IMAGE"]
        return render_template(web_pages["home_page"], questions=all_questions, table_heading=table_heading, 
                                empty=False, default_sort_by=sort_info["sort_by"], default_order=sort_info["order"])
    if con.get_all(question_file) is False: return render_template(web_pages["home_page"], questions="", table_heading="", empty=True)
    else:
        all_questions = dmg.sort_questions("submission_time", "descending")
        table_heading = ["ID", "SUBMISSION TIME", "VIEWS", "VOTES", "TITLE", "QUESTION", "IMAGE"]
        return render_template(web_pages["home_page"], questions=all_questions, table_heading=table_heading, 
                                empty=False, default_sort_by="submission time", default_order="descending")


@app.route("/question/<question_id>")
def question(question_id):
    '''
    Displays the question page with title, question, its answers and all the functionalities and info for question and answers.
    Displays a "No answers for this question" message if there is the case.
    Every time this route is accessed, the view_number of the respective question gets modified.
    '''
    dmg.add_view(question_id)
    empty = False
    question = dmg.get_question_by_id(question_id)
    answers_for_question = dmg.find_answers_by_question_id(question_id)
    if answers_for_question == None:
        empty = True
    return render_template(web_pages["question_page"], question=question, answers=answers_for_question, empty=empty, question_id=question_id)


@app.route("/list/add-question", methods=["GET", "POST"])
def add_question():
    '''
    "GET": Displays the "Add question" page
    "POST": Gets the new question's info, sends it to data_manager and redirects to the home page.
    '''
    if request.method == "POST":

        question_id = con.find_next_index(question_file)
        question_info = {"id": question_id, "submission_time": calendar.timegm(time.gmtime()), "view_number": "0", "vote_number": "0", 
                        "title": request.form["title"], "message": request.form["message"], "image": request.form['image']}
        dmg.add(question_info, question_file, questions_fieldnames)
        return redirect("/question/{0}".format(question_id))
    return render_template(web_pages["add_question_page"])


@app.route("/question/<question_id>/new-answer", methods=["GET", "POST"])
def new_answer(question_id):
    '''
    "GET": Displays the "Add answer for question" page.
    "POST": Gets the new answer's info, sends it to data_manager and redirects to the home page
    '''
    question = dmg.get_question_by_id(question_id)
    if request.method == "POST":
        answer_id = con.find_next_index(answer_file)
        answer_info = {"id": answer_id, "submission_time": calendar.timegm(time.gmtime()), 
                        "vote_number": "0", "question_id": question_id, "message": request.form['answer'], "image": request.form['image']}
        dmg.add(answer_info, answer_file, answer_fieldnames)
        return redirect("/question/{0}".format(question_id))
    return render_template(web_pages["new_answer_page"], question=question)


# ROUTES FOR QUESTIONS: edit, delete, vote    

@app.route("/question/<question_id>/edit", methods=["GET", "POST"])
def edit_question(question_id):
    '''
    "GET": Displays the "Edit question" page.
    "POST": Gets the new info for the question and sends it to data_manager, then it redirects back to the question page
    '''
    if request.method == "POST":
        edited_question_info = dict(request.form)
        dmg.edit_question(question_id, edited_question_info)
        return redirect("/question/{0}".format(question_id))
    question_info = dmg.get_question_by_id(question_id)
    return render_template("edit_question.html", question_info=question_info)


@app.route("/question/<question_id>/delete")
def delete_question(question_id):
    '''
    Sends the respective's question id to data_manager to delete it and redirects to home page.
    '''
    dmg.delete_question(question_id)
    return redirect("/")


@app.route("/question/<question_id>/<vote>")
def vote_question(question_id, vote):
    '''
    Sends the respective question's id and the voting type to data_manager and redirects back to the question page
    '''
    dmg.vote_question(question_id, vote)
    return redirect("/question/{0}".format(question_id))


# ROUTES FOR ANSWERS: delete, vote

@app.route("/answer/<question_id>/<answer_id>/<vote>")
def vote_answer(question_id, answer_id, vote):
    '''
    Sends the respective answer's id and the voting type to data_manager and redirects back to the question page
    '''
    dmg.vote_answer(question_id, answer_id, vote)
    return redirect("/question/{0}".format(question_id))


@app.route("/answer/<question_id>/<answer_id>/delete")
def delete_answer(question_id, answer_id):
    '''
    Sends the respective answer's id to data_manager to delete it and redirects to the question page
    '''
    dmg.delete_answer(answer_id)
    return redirect("/question/{0}".format(question_id))


# MAIN

if __name__ == "__main__":
    app.run(port=5000, debug=True)