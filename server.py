from flask import Flask, render_template, request, redirect, url_for, flash
from werkzeug.utils import secure_filename
import time, calendar, os, uuid
from datetime import datetime
import data_manager as dmg
import connection as con
import util as utl

web_pages = {"home_page": "home.html", "question_page": "question.html", "add_question_page": "add_question.html", 
            "new_answer_page": "new_answer.html", "show_image_page": "show_image.html"
            }

answer_file = "sample_data/answer.csv"
question_file = "sample_data/question.csv"

answer_fieldnames = ["id", "submission_time",
                      "vote_number", "question_id", "message", "image"]
                      
questions_fieldnames = ["id", "submission_time", "view_number",
                      "vote_number", "title", "message", "image"]

UPLOAD_FOLDER = "static" 

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

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
        table_heading = ["id", "submission time", "views", "votes", "title", "question", "image"]
        return render_template(web_pages["home_page"], questions=all_questions, table_heading=table_heading, 
                                empty=False, default_sort_by=sort_info["sort_by"], default_order=sort_info["order"])
    if con.get_all(question_file) is False: return render_template(web_pages["home_page"], questions="", table_heading="", empty=True)
    else:
        all_questions = utl.convert_unix_time_to_readable_format(dmg.sort_questions("submission_time", "descending"))
        for question in all_questions:
            question['vote_number'] = "{0}%".format(dmg.vote_percentage(question['id']))
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
    empty = False
    question = dmg.get_question_by_id(question_id)
    question['submission_time'] = datetime.utcfromtimestamp(int(question['submission_time'])).strftime('%Y-%m-%d %H:%M:%S')
    question['image'] = url_for('static', filename=question['image'])
    question['vote_number'] = "{0}%".format(dmg.vote_percentage(question_id))
    answers_for_question = utl.convert_unix_time_to_readable_format(dmg.find_answers_by_question_id(question_id))
    if answers_for_question == None:
        empty = True
    if empty == False:
        for answer in answers_for_question:
            answer['vote_number'] = dmg.vote_percentage_answer(answer['id'], question_id)
            if answer['image'] != '':
                answer['image'] = url_for('static', filename=answer['image'])
    return render_template(web_pages["question_page"], question=question, answers=answers_for_question, 
                            empty=empty, question_id=question_id)


@app.route("/list/add-question", methods=["GET", "POST"])
def add_question():
    '''
    "GET": Displays the "Add question" page
    "POST": Gets the new question's info, sends it to data_manager and redirects to the home page.
    '''
    if request.method == "POST":
        file = request.files['image']
        if file.filename != '':
            if file and utl.allowed_file(file.filename):
                filename = secure_filename(file.filename)
                f = utl.transform_image_title(filename)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], f))
        else:
            f = ""
        question_id = con.find_next_index(question_file)
        submission_time = int(calendar.timegm(time.gmtime())) + 7200
        question_info = {"id": question_id, "submission_time": submission_time, "view_number": "0", "vote_number": "0-0", 
                        "title": request.form["title"], "message": request.form["message"], "image": f}
        dmg.add(question_info, question_file, questions_fieldnames)
        return redirect("/question/{0}".format(question_id))
    return render_template(web_pages["add_question_page"])


@app.route("/question/<question_id>/new-answer", methods=["GET", "POST"])
def new_answer(question_id):
    '''
    "GET": Displays the "Add answer for question" page.
    "POST": Gets the new answer's info, sends it to data_manager and redirects to the home page
    '''
    if request.method == "POST":
        question = dmg.get_question_by_id(question_id)
        file = request.files['image']
        if file.filename != '':
            if file and utl.allowed_file(file.filename):
                filename = secure_filename(file.filename)
                f = utl.transform_image_title(file.filename)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], f))
        else: f = ""
        answer_id = con.find_next_index(answer_file)
        submission_time = int(calendar.timegm(time.gmtime())) + 7200
        answer_info = {"id": answer_id, "submission_time": str(submission_time), 
                        "vote_number": "0-0", "question_id": question_id, "message": request.form['answer'], "image": f}
        dmg.add(answer_info, answer_file, answer_fieldnames)
        return redirect("/question/{0}".format(question_id))
    question = dmg.get_question_by_id(question_id)
    return render_template(web_pages["new_answer_page"], question=question)


# ROUTES FOR QUESTIONS: edit, delete, vote, show image, add view

@app.route("/question/<question_id>/edit", methods=["GET", "POST"])
def edit_question(question_id):
    '''
    "GET": Displays the "Edit question" page.
    "POST": Gets the new info for the question and sends it to data_manager, then it redirects back to the question page
    '''
    if request.method == "POST":
        edited_question_info = dict(request.form)
        edited_question_info['title'] = edited_question_info['title'] + " (Edited)"
        edited_question_info['submission_time'] = calendar.timegm(time.gmtime())
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


@app.route("/question/<question_id>/show/<image_path>")
def show_image_for_question(question_id, image_path):
    '''
    Special route for focusing on the image of the question. Similar with the question page, but with no answers and bigger image.
    '''
    question = dmg.get_question_by_id(question_id)
    image = url_for('static', filename=image_path)
    return render_template(web_pages['show_image_page'], question=question, image=image, question_id=question_id)


@app.route("/question/<question_id>/view/add")
def add_view_for_question(question_id):
    '''
    Adds a view to the respective question ONLY when clicked from home page.
    '''
    dmg.add_view(question_id)
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