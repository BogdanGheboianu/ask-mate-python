from flask import Flask, render_template, request, redirect, url_for
from werkzeug.utils import secure_filename
import os, uuid
import data_manager as dmg
import connection as con
import util as utl

WEB_PAGES = {"home_page": "home.html", "question_page": "question.html", "add_question_page": "add_question.html",
             "new_answer_page": "new_answer.html", "show_image_page": "show_image.html", 'search': 'search.html',
             'add_comm': 'add_comm.html', 'edit_q': 'edit_question.html', 'edit_ans': 'edit_answer.html'
             }
UPLOAD_FOLDER = "static"

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

#===================================================================================================================================================

# DISPLAY ROUTES: index, question, show_image, search

@app.route('/', methods=['GET', 'POST'])
@app.route('/list', methods=['GET', 'POST'])
def index():
    table_heading = ["ID", "Submission Time", "Views", "Votes", "Title", "Question", "Image"]
    sort_options = {"none": "Choose option", "title": "title", "message": "question",
                    "submission_time": "submission time", "vote_number": "votes", "view_number": "views"}
    order_options = {"none": "Choose order", "ascending": "ascending", "descending": "descending"}
    # Display question list after sorting
    if request.method == 'POST':
        sort_factor = request.form.get('sort_by')
        sort_order = request.form.get('order')
        if sort_factor != 'none' and sort_order != 'none':
            show_all_questions = False
            first_questions = utl.check_questions_for_edit(con.get_latest_questions(sort_factor, sort_order))
            if first_questions != False: num_all_questions = len(con.get_questions(sort_factor, sort_order))
            if num_all_questions > 5: show_all_questions = True
            return render_template(WEB_PAGES['home_page'],
                                    questions=first_questions,
                                    table_heading=table_heading,
                                    sort_options=sort_options,
                                    order_options=order_options,
                                    default_sort=sort_factor,
                                    default_order=sort_order,
                                    show_all_questions=show_all_questions,
                                    empty=False)
    # Check if there are questions in the database
    if con.get_questions('id', 'ascending') is False: 
        return render_template(WEB_PAGES['home_page'],
                                questions='',
                                table_heading='',
                                empty=True)
    # Check for sort and for how many questions to display
    if request.args.get('sort-factor') == 'none' or request.args.get('sort-factor') == None:
        if request.args.get('show-all') == 'all':
            questions = utl.check_questions_for_edit(con.get_questions('submission_time', 'descending'))
        elif request.args.get('show-all') != 'all' or request.args.get('show-all') != None:
            questions = utl.check_questions_for_edit(con.get_latest_questions('submission_time', 'descending'))
        sort_factor = 'none'
        sort_order = 'none'
    elif request.args.get('sort-factor') != 'none' or request.args.get('sort-factor') != None:
        sort_factor = request.args.get('sort-factor')
        sort_order = request.args.get('sort-order')
        if request.args.get('show-all') == 'all':
            questions = utl.check_questions_for_edit(con.get_questions(sort_factor, sort_order))
        elif request.args.get('show-all') != 'all' or request.args.get('show-all') != None:
            questions = utl.check_questions_for_edit(con.get_latest_questions(sort_factor, sort_order))
    all_questions = con.get_questions('id', 'ascending')
    if all_questions != False: num_all_questions = len(all_questions)
    show_all_questions = False
    if num_all_questions > 5 and request.args.get('show-all') != 'all': show_all_questions = True
    
    return render_template(WEB_PAGES['home_page'],
                            questions=questions,
                            empty=False,
                            table_heading=table_heading,
                            sort_options=sort_options,
                            order_options=order_options,
                            default_sort=sort_factor,
                            default_order=sort_order,
                            show_all_questions=show_all_questions)
    

@app.route("/question/<question_id>")
def question(question_id):
    empty = False
    num_answers = 0
    question = utl.check_specific_question_for_edit(dmg.get_question_by_id(question_id))
    question['image'] = url_for('static', filename=question['image'])
    answers_for_question = utl.check_answers_for_edit(dmg.get_answers_for_question(question_id))
    if request.args.get('show_more_com_for_q') == 'yes':
        comments_for_question = utl.check_comments_for_edit(dmg.get_comments_for_question(question_id, 'no-limit'))
    else:
        comments_for_question = utl.check_comments_for_edit(dmg.get_comments_for_question(question_id, 'limit'))
    try:
        num_comments_for_question = len(utl.check_comments_for_edit(dmg.get_comments_for_question(question_id, 'no-limit')))
    except TypeError: 
        num_comments_for_question = 0
    tags_for_question = dmg.get_tags_for_question(question_id)
    comments_for_answers = utl.check_comments_for_edit(dmg.get_answers_for_question_comments(question_id))
    if comments_for_question is not None:
        comment_id = comments_for_question[0]['id']
    else:
        comment_id = None
    if answers_for_question == None: empty = True
    if empty == False:
        answers_for_question = utl.link_answer_with_image(answers_for_question, question_id)
        num_answers = len(answers_for_question)
    show_more_com_for_q = request.args.get('show_more_com_for_q')
    show_more_com_for_ans = request.args.get('show_more_com_for_ans')
    return render_template(WEB_PAGES["question_page"],
        question=question,
        answers=answers_for_question,
        empty=empty,
        question_id=question_id,
        num_answers=num_answers,
        num_comments_for_question=num_comments_for_question,
        comments_for_question=comments_for_question,
        comments_for_answers=comments_for_answers,
        tags_for_question=tags_for_question,
        show_more_com_for_q=show_more_com_for_q,
        show_more_com_for_ans=show_more_com_for_ans,
        comment_id=comment_id)


@app.route("/question/<question_id>/show/<image_path>")
def show_image_for_question(question_id, image_path):
    question = utl.check_specific_question_for_edit(
        dmg.get_question_by_id(question_id))
    image = url_for('static', filename=question['image'])
    comments_for_question = dmg.get_comments_for_question(question_id, 'no-limit')
    tags_for_question = dmg.get_tags_for_question(question_id)
    return render_template(WEB_PAGES['show_image_page'],
                           question=question,
                           image=image,
                           question_id=question_id,
                           comments_for_question=comments_for_question,
                           tags_for_question=tags_for_question)


@app.route('/search')
def search():
    search_term = request.args.get('q')
    search_results = dmg.search(search_term)
    if search_results != None:
        return render_template(WEB_PAGES['search'], 
                                search_term=search_term, 
                                search_results=search_results,
                                in_question_title=search_results['question_title'],
                                in_question_message=search_results['question_message'],
                                in_answers=search_results['answers'],
                                in_tags=search_results['tags'],
                                in_comments=search_results['comments'],
                                highlight=utl.highlight,
                                check_edit=utl.check_specific_question_for_edit)
    else: return render_template(WEB_PAGES['search'], search_results=search_results, search_term=search_term)

#===================================================================================================================================================

# ADDING ROUTES: add question, add answer, add comment for question, add comment for answer, add view for question

@app.route("/list/add-question", methods=["GET", "POST"])
def add_question():
    if request.method == "POST":
        question_id = con.get_next_id('question')
        f = save_image(request.files['image'])
        question_info = {'id': question_id, 
                        "submission_time": utl.get_current_time(), 
                        "view_number": 0,
                         "vote_number": 0, 
                         "title": request.form["title"],
                         "message": request.form["message"], 
                         "image": f,
                         'votes_up': 0, 'votes_down': 0}
        tags_for_question = {'existing_tag': request.form.get('existing_tag'),
                            'new_tags': request.form.get('tags')}
        con.add_question(question_info)
        con.add_tags_for_question(tags_for_question, question_id)
        return redirect("/question/{0}".format(question_id))
    all_tags = con.get_tags()
    return render_template(WEB_PAGES["add_question_page"], all_tags=all_tags)


@app.route("/question/<question_id>/add-answer", methods=["GET", "POST"])
def add_answer(question_id):
    question = utl.check_specific_question_for_edit(dmg.get_question_by_id(question_id))
    if request.method == "POST":
        f = save_image(request.files['image'])
        answer_info = {"id": con.get_next_id('answer'), 
                        "submission_time": utl.get_current_time(),
                        "vote_number": 0, 
                        "question_id": question_id, 
                        "message": request.form['answer'], 
                        "image": f,
                        'votes_up': 0, 'votes_down': 0}
        con.add_answer(answer_info)
        return redirect("/question/{0}".format(question_id))
    return render_template(WEB_PAGES["new_answer_page"], question=question)


@app.route('/question/<question_id>/add-comment', methods=['GET', 'POST'])
def add_comment_for_question(question_id):
    if request.method == 'POST':
        comment_info = {'id': con.get_next_id('comment'), 
                        'question_id': question_id,
                        'message': request.form['comment'], 
                        'submission_time': utl.get_current_time()}
        con.add_comment_for_question(comment_info)
        return redirect('/question/{0}'.format(question_id))
    return render_template(WEB_PAGES['add_comm'], question_id=question_id)


@app.route('/<question_id>/answer/<answer_id>/new-comment', methods=['GET', 'POST'])
def add_comment_for_answer(question_id, answer_id):
    if request.method == 'POST':
        comment_info = {'id': con.get_next_id('comment'), 
                        'answer_id': answer_id,
                        'submission_time': utl.get_current_time(), 
                        'message': request.form['comment']}
        con.add_comment_for_answer(comment_info)
        return redirect('/question/{0}'.format(question_id))
    return render_template(WEB_PAGES['add_comm'], question_id=question_id)


@app.route("/question/<question_id>/view/add")
def add_view_for_question(question_id):
    con.add_view(question_id)
    return redirect("/question/{0}".format(question_id))

#=====================================================================================================================================================

# EDITING ROUTES: edit question, edit answer, edit comment for question, edit comment for answer

@app.route("/question/<question_id>/edit", methods=["GET", "POST"])
def edit_question(question_id):
    if request.method == "POST":
        edited_question_info = dict(request.form)
        edited_question_info['title'] = edited_question_info['title'] + "(Edited)"
        new_submission_time = utl.get_current_time()
        con.edit_question(question_id, edited_question_info, new_submission_time)
        tags_for_question = {'existing_tag': request.form.get('existing_tag'),
                                'new_tags': request.form.get('tags')}
        con.add_tags_for_question(tags_for_question, question_id)
        return redirect("/question/{0}".format(question_id))
    question_info = utl.check_specific_question_for_edit(dmg.get_question_by_id(question_id))
    all_tags = con.get_tags()
    tags_for_question = dmg.get_tags_for_question(question_id)
    return render_template(WEB_PAGES['edit_q'], question_info=question_info, all_tags=all_tags, tags_for_question=tags_for_question)


@app.route('/answer/<question_id>/<answer_id>/edit', methods=['GET', 'POST'])
def edit_answer(question_id, answer_id):
    if request.method == "POST":
        new_answer = request.form['message'] + ' (Edited)'
        new_submission_time = utl.get_current_time()
        edited_answer = {'id': answer_id, 'message': new_answer, 'submission_time': new_submission_time}
        con.edit_answer(edited_answer)
        return redirect('/question/{0}'.format(question_id))
    answers = con.get_answers()
    for answer in answers:
        if answer['id'] == int(answer_id): selected_answer = answer
    return render_template(WEB_PAGES['edit_ans'], selected_answer=selected_answer)



@app.route('/question/<question_id>/<comment_id>/edit-comment', methods=['GET', 'POST'])
def edit_comment_for_question(question_id, comment_id):
    if request.method == 'POST':
        new_comment_info = {'id': comment_id, 
                            'question_id': question_id, 
                            'message': request.form['message'] + ' (Edited)', 
                            'submission_time': utl.get_current_time()}
        con.edit_comment_for_question(new_comment_info)
        return redirect('/question/{0}'.format(question_id))
    comments = con.get_comments('no-limit')
    for com in comments:
        if com['id'] == int(comment_id): comment = com
    return render_template('edit_comment.html', comment=comment)


@app.route('/answer/<answer_id>/<question_id>/<comment_id>/edit-comment', methods=['GET', 'POST'])
def edit_comment_for_answer(answer_id, question_id, comment_id):
    if request.method == 'POST':
        new_comment_info = {'id': comment_id, 
                            'answer_id': answer_id, 
                            'message': request.form['message'] + ' (Edited)', 
                            'submission_time': utl.get_current_time()}
        con.edit_comment_for_answer(new_comment_info)
        return redirect('/question/{0}'.format(question_id))
    comments = con.get_comments()
    for com in comments:
        if com['id'] == int(comment_id): comment = com
    return render_template('edit_comment.html', comment=comment)

#====================================================================================================================================================

# DELETING ROUTES: delete question, delete answer, delete comment, delete tag

@app.route("/question/<question_id>/delete")
def delete_question(question_id):
    con.delete_question(question_id)
    return redirect("/")


@app.route("/answer/<question_id>/<answer_id>/delete")
def delete_answer(question_id, answer_id):
    con.delete_answer(answer_id)
    return redirect("/question/{0}".format(question_id))


@app.route('/comments/<comment_id>/delete')
def delete_comments(comment_id):
    question_id = con.delete_comment(comment_id)['question_id']
    return redirect('/question/{0}'.format(question_id))


@app.route('/question/<question_id>/<tag_name>/delete-tag')
def delete_tag(question_id, tag_name):
    con.delete_question_tag(question_id, tag_name)
    return redirect('/question/{0}/edit'.format(question_id))

#==================================================================================================================================================

# VOTING ROUTES: vote question, vote answer

@app.route("/question/<question_id>/<vote>")
def vote_question(question_id, vote):
    con.vote_question(question_id, vote)
    return redirect("/question/{0}".format(question_id))


@app.route("/answer/<question_id>/<answer_id>/<vote>")
def vote_answer(question_id, answer_id, vote):
    con.vote_answer(answer_id, vote)
    return redirect("/question/{0}".format(question_id))

#==================================================================================================================================================

# AUXILIARY FUNCTIONS

def save_image(file):
    if file.filename != '':
        if file and utl.allowed_file(file.filename):
            f = utl.transform_image_title(secure_filename(file.filename))
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], f))
    else: f = ""
    return f

#=================================================================================================================================================

if __name__ == "__main__":
    app.run(port=5000, debug=True)