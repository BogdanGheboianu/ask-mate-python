from flask import *
from werkzeug.utils import secure_filename
import os, uuid
import data_manager as dmg
import connection as con
import util as utl
from flask_ngrok import run_with_ngrok

WEB_PAGES = {"home_page": "home.html", "question_page": "question.html", "add_question_page": "add_question.html",
             "new_answer_page": "new_answer.html", "show_image_page": "show_image.html", 'search': 'search.html',
             'add_comm': 'add_comm.html', 'edit_q': 'edit_question.html', 'edit_ans': 'edit_answer.html'
             }
UPLOAD_FOLDER = "static"

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.secret_key = os.urandom(16) 
# run_with_ngrok(app)


#===================================================================================================================================================

# DISPLAY ROUTES: index, question, show_image, search

def is_logged_in():
    if 'username' in session:
        return True
    else:
        return False
        


@app.route('/', methods=['GET', 'POST'])
@app.route('/list', methods=['GET', 'POST'])
def index():
    if is_logged_in():
        username = escape(session['username'])
        account_type = con.get_user(username)['role']
        userid = con.get_user(username)['id']
        app_theme = con.get_user(username)['app_theme']
        user_tags = con.get_user_tags(con.get_user(username)['id'])
    else:
        username = None
        account_type = None
        userid = None
        app_theme = 'black_orange'
        user_tags = 'all'
    table_heading = ['Title', 'Question', 'Votes', 'Views', 'Posted', 'ID', 'Image']
    sort_options = {"none": "Choose option", "title": "title", "message": "question",
                    "submission_time": "submission time", "vote_number": "votes", "view_number": "views"}
    order_options = {"none": "Choose order", "ascending": "ascending", "descending": "descending"}
    # Display question list after sorting
    if request.method == 'POST':
        sort_factor = request.form.get('sort_by')
        sort_order = request.form.get('order')
        if sort_factor != 'none' and sort_order != 'none':
            show_all_questions = False
            first_q = utl.check_questions_for_edit(con.get_latest_questions(sort_factor, sort_order))
            first_questions = dmg.custom_questions(user_tags, first_q)
            # if first_questions != False: num_all_questions = len(dmg.custom_questions(user_tags, con.get_questions(sort_factor, sort_order)))
            # if num_all_questions > 5: show_all_questions = True
            empty = False
            if len(first_questions) == 0: empty = True
            return render_template(WEB_PAGES['home_page'],
                                    questions=first_questions,
                                    table_heading=table_heading,
                                    sort_options=sort_options,
                                    order_options=order_options,
                                    default_sort=sort_factor,
                                    default_order=sort_order,
                                    show_all_questions=show_all_questions,
                                    empty=empty,
                                    username=username,
                                    account_type=account_type,
                                    app_theme=app_theme)
    # Check if there are questions in the database
    if con.get_questions('id', 'ascending') is False: 
        return render_template(WEB_PAGES['home_page'],
                                questions='',
                                table_heading='',
                                empty=True,
                                username=username,
                                account_type=account_type,
                                app_theme=app_theme)
    # Check for sort and for how many questions to display
    if request.args.get('sort-factor') == 'none' or request.args.get('sort-factor') == None:
        if request.args.get('show-all') == 'all':
            questions = dmg.custom_questions(user_tags, utl.check_questions_for_edit(con.get_questions('submission_time', 'descending')))
        elif request.args.get('show-all') != 'all' or request.args.get('show-all') != None:
            questions = dmg.custom_questions(user_tags, utl.check_questions_for_edit(con.get_latest_questions('submission_time', 'descending')))
        sort_factor = 'none'
        sort_order = 'none'
    elif request.args.get('sort-factor') != 'none' or request.args.get('sort-factor') != None:
        sort_factor = request.args.get('sort-factor')
        sort_order = request.args.get('sort-order')
        if request.args.get('show-all') == 'all':
            questions = dmg.custom_questions(user_tags, utl.check_questions_for_edit(con.get_questions(sort_factor, sort_order)))
        elif request.args.get('show-all') != 'all' or request.args.get('show-all') != None:
            questions = dmg.custom_questions(user_tags, utl.check_questions_for_edit(con.get_latest_questions(sort_factor, sort_order)))
    all_questions = dmg.custom_questions(user_tags, con.get_questions('id', 'ascending'))
    if all_questions != False: num_all_questions = len(all_questions)
    show_all_questions = False
    if num_all_questions > 5 and request.args.get('show-all') != 'all': show_all_questions = True
    empty = False
    if len(questions) == 0: empty = True
    return render_template(WEB_PAGES['home_page'],
                            questions=questions,
                            empty=empty,
                            table_heading=table_heading,
                            sort_options=sort_options,
                            order_options=order_options,
                            default_sort=sort_factor,
                            default_order=sort_order,
                            show_all_questions=show_all_questions,
                            username=username,
                            account_type=account_type,
                            app_theme=app_theme)
    

@app.route("/question/<question_id>")
def question(question_id):
    if is_logged_in():
        username = escape(session['username'])
        account_type = con.get_user(username)['role']
        userid = con.get_user(username)['id']
        app_theme = con.get_user(username)['app_theme']
    else:
        username = None
        account_type = None
        userid = None
        app_theme = 'black_orange'
    if request.args.get('view') == 'add': con.add_view(question_id)
    empty = False
    num_answers = 0
    question = utl.check_specific_question_for_edit(dmg.get_question_by_id(question_id))
    question.update({'username': con.get_user_by_id(question['userid'])['username']})
    question['image'] = url_for('static', filename=question['image'])
    answers_for_question = utl.check_answers_for_edit(dmg.get_answers_for_question(question_id))
    if request.args.get('show_more_com_for_q') == 'yes':
        comments_for_question = utl.check_comments_for_edit(dmg.get_comments_for_question(question_id, 'no-limit'))
    else:
        comments_for_question = utl.check_comments_for_edit(dmg.get_comments_for_question(question_id, 'limit'))
    try:
        num_comments_for_question = len(utl.check_comments_for_edit(dmg.get_comments_for_question(question_id, 'no-limit')))
        for comm in comments_for_question:
            comm_username = con.get_user_by_id(comm['userid'])['username']
            comm.update({'username': comm_username})
    except TypeError: 
        num_comments_for_question = 0
    tags_for_question = dmg.get_tags_for_question(question_id)
    comments_for_answers = utl.check_comments_for_edit(dmg.get_answers_for_question_comments(question_id))
    if comments_for_answers != None:
        for comm in comments_for_answers:
            comm_username = con.get_user_by_id(comm['userid'])['username']
            comm.update({'username': comm_username})
    if comments_for_question is not None:
        comment_id = comments_for_question[0]['id']
    else:
        comment_id = None
    if answers_for_question == None: empty = True
    if empty == False:
        answers_for_question = utl.link_answer_with_image(answers_for_question, question_id)
        for ans in answers_for_question:
            ans_username = con.get_user_by_id(ans['userid'])['username']
            ans.update({'username': ans_username, 'voted': False, 'vote_type': ''})
        num_answers = len(answers_for_question)
    show_more_com_for_q = request.args.get('show_more_com_for_q')
    show_more_com_for_ans = request.args.get('show_more_com_for_ans')
    question_voted = False
    vote_type = None
    user_votes = None
    if userid != None:
        user_votes = con.get_user_votes(userid)
        for uv in user_votes:
            if uv['questionid'] == question['id']:
                question_voted = True
                vote_type = uv['vote_type']
            if empty is False:
                for ans in answers_for_question:
                    if ans['id'] == uv['answerid']:
                        ans['voted'] = True
                        ans['vote_type'] = uv['vote_type']
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
        comment_id=comment_id,
        username=username,
        account_type=account_type,
        user_votes=user_votes,
        userid=userid,
        question_voted=question_voted,
        vote_type=vote_type,
        app_theme=app_theme)


@app.route("/question/<question_id>/show/<image_path>")
def show_image_for_question(question_id, image_path):
    if is_logged_in():
        username = escape(session['username'])
        account_type = con.get_user(username)['role']
        userid = con.get_user(username)['id']
        app_theme = con.get_user(username)['app_theme']
    else:
        username = None
        account_type = None
        userid = None
        app_theme = 'black_orange'
    question = utl.check_specific_question_for_edit(dmg.get_question_by_id(question_id))
    question.update({'username': con.get_user_by_id(question['userid'])['username']})
    image = url_for('static', filename=question['image'])
    comments_for_question = dmg.get_comments_for_question(question_id, 'no-limit')
    tags_for_question = dmg.get_tags_for_question(question_id)
    return render_template(WEB_PAGES['show_image_page'],
                           question=question,
                           image=image,
                           question_id=question_id,
                           comments_for_question=comments_for_question,
                           tags_for_question=tags_for_question,
                           username=username,
                           account_type=account_type,
                           app_theme=app_theme)


@app.route('/search')
def search():
    if is_logged_in():
        username = escape(session['username'])
        account_type = con.get_user(username)['role']
        userid = con.get_user(username)['id']
        app_theme = con.get_user(username)['app_theme']
    else:
        username = None
        account_type = None
        userid = None
        app_theme = 'black_orange'
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
                                check_edit=utl.check_specific_question_for_edit,
                                username=username,
                                account_type=account_type,
                                app_theme=app_theme)
    else: return render_template(WEB_PAGES['search'], search_results=search_results, search_term=search_term, username=username, app_theme=app_theme)


@app.route('/user/<_username_>', methods=['GET', 'POST'])
def user(_username_):
    if is_logged_in():
        username = escape(session['username'])
        account_type = con.get_user(username)['role']
        userid = con.get_user(username)['id']
        app_theme = con.get_user(username)['app_theme']
    else:
        username = None
        account_type = None
        userid = None
        app_theme = 'black_orange'
    if request.method == "POST":
        app_theme = request.form.get('app_theme')
        con.update_user_app_theme(userid, app_theme)
        return redirect(f'/user/{_username_}')
    user = con.get_user(_username_)
    if user['profile_pic'] != None:
        user['profile_pic'] = url_for('static', filename=user['profile_pic'])
    else:
        user['profile_pic'] = url_for('static', filename='no_profile_pic.png')
    contributions = con.get_user_contributions(_username_)
    user_tags = con.get_user_tags(con.get_user(_username_)['id'])
    user_followers = con.get_user_followers(con.get_user(_username_)['id'])
    user_num_followers = len(user_followers)
    following_user = False
    for f in user_followers:
        if userid == f['id']:
            following_user = True
    return render_template('user.html', user=user, username=username, account_type=account_type, contributions=contributions, 
                            user_tags=user_tags, on_page_username=user['username'], user_followers=user_followers, user_num_followers=user_num_followers, following_user=following_user,
                            app_theme=app_theme)


@app.route('/user/<_username_>/choose-interests')
def list_interests(_username_):
    if is_logged_in():
        username = escape(session['username'])
        account_type = con.get_user(username)['role']
        userid = con.get_user(username)['id']
        app_theme = con.get_user(username)['app_theme']
    else:
        username = None
        account_type = None
        userid = None
        app_theme = 'black_orange'
    new_tags = con.get_new_tags_for_user(con.get_user(_username_)['id'])
    return render_template('show_tags.html', username=_username_, account_type=account_type, new_tags=new_tags, app_theme=app_theme)


@app.route('/user/<_username_>/followers')
def followers(_username_):
    if is_logged_in():
        username = escape(session['username'])
        account_type = con.get_user(username)['role']
        userid = con.get_user(username)['id']
        app_theme = con.get_user(username)['app_theme']
    else:
        username = None
        account_type = None
        userid = None
        app_theme = 'black_orange'
    user_followers = con.get_user_followers(con.get_user(_username_)['id'])
    user_num_followers = len(user_followers)
    return render_template('followers.html', _username_=_username_, user_followers=user_followers, user_num_followers=user_num_followers, username=username, app_theme=app_theme)

@app.route('/list-users')
def list_all_users():
    if is_logged_in():
        username = escape(session['username'])
        account_type = con.get_user(username)['role']
        userid = con.get_user(username)['id']
        app_theme = con.get_user(username)['app_theme']
    else:
        username = None
        account_type = None
        userid = None
        app_theme = 'black_orange'
    USERS_TABLE_HEADERS = ['Username', 'Email', 'ID', 'Date Created', 'User Role', 'Profile Photo', 'Rank', 'Theme']
    all_users = con.get_all_users()
    return render_template('list_users.html', all_users=all_users,
    app_theme=app_theme,
    users_table_headers=USERS_TABLE_HEADERS,
    username=username)



#===================================================================================================================================================

# ADDING ROUTES: add question, add answer, add comment for question, add comment for answer, add view for question

@app.route("/list/add-question", methods=["GET", "POST"])
def add_question():
    if is_logged_in():
        username = escape(session['username'])
        account_type = con.get_user(username)['role']
        userid = con.get_user(username)['id']
        app_theme = con.get_user(username)['app_theme']
    else:
        return redirect('/registration/login')
    if request.method == "POST":
        question_id = con.get_next_id('question')
        f = save_image(request.files['image'])
        code_snippet = request.form.get('code_snippet')
        if code_snippet == None: code_snippet = ''
        userid = con.get_user(username)['id']
        question_info = {'id': question_id, 
                        "submission_time": utl.get_current_time(), 
                        "view_number": 0,
                         "vote_number": 0, 
                         "title": request.form["title"],
                         "message": request.form["message"], 
                         "image": f,
                         'votes_up': 0, 'votes_down': 0,
                         'code_snippet': code_snippet,
                         'userid': userid}
        tags_for_question = {'existing_tag': request.form.get('existing_tag'),
                            'new_tags': request.form.get('tags')}
        con.add_question(question_info)
        con.add_tags_for_question(tags_for_question, question_id)
        return redirect("/question/{0}".format(question_id))
    all_tags = con.get_tags()
    return render_template(WEB_PAGES["add_question_page"], all_tags=all_tags, username=username, account_type=account_type, app_theme=app_theme)


@app.route("/question/<question_id>/add-answer", methods=["GET", "POST"])
def add_answer(question_id):
    if is_logged_in():
        username = escape(session['username'])
        account_type = con.get_user(username)['role']
        userid = con.get_user(username)['id']
        app_theme = con.get_user(username)['app_theme']
    else:
        return redirect('/registration/login')
    question = utl.check_specific_question_for_edit(dmg.get_question_by_id(question_id))
    code_snippet = request.form.get('code_snippet')
    if code_snippet == None: code_snippet = ''
    if request.method == "POST":
        f = save_image(request.files['image'])
        userid = con.get_user(username)['id']
        answer_info = {"id": con.get_next_id('answer'), 
                        "submission_time": utl.get_current_time(),
                        "vote_number": 0, 
                        "question_id": question_id, 
                        "message": request.form['answer'], 
                        "image": f,
                        'votes_up': 0, 'votes_down': 0,
                        'code_snippet': code_snippet,
                        'userid': userid}
        con.add_answer(answer_info)
        return redirect("/question/{0}".format(question_id))
    return render_template(WEB_PAGES["new_answer_page"], question=question, username=username, account_type=account_type, app_theme=app_theme)


@app.route('/question/<question_id>/add-comment', methods=['GET', 'POST'])
def add_comment_for_question(question_id):
    if is_logged_in():
        username = escape(session['username'])
        account_type = con.get_user(username)['role']
        userid = con.get_user(username)['id']
        app_theme = con.get_user(username)['app_theme']
    else:
        return redirect('/registration/login')
    if request.method == 'POST':
        userid = con.get_user(username)['id']
        comment_info = {'id': con.get_next_id('comment'), 
                        'question_id': question_id,
                        'message': request.form['comment'], 
                        'submission_time': utl.get_current_time(),
                        'userid': userid}
        con.add_comment_for_question(comment_info)
        return redirect('/question/{0}'.format(question_id))
    return render_template(WEB_PAGES['add_comm'], question_id=question_id, username=username, account_type=account_type, app_theme=app_theme)


@app.route('/<question_id>/answer/<answer_id>/new-comment', methods=['GET', 'POST'])
def add_comment_for_answer(question_id, answer_id):
    if is_logged_in():
        username = escape(session['username'])
        account_type = con.get_user(username)['role']
        userid = con.get_user(username)['id']
        app_theme = con.get_user(username)['app_theme']
    else:
        return redirect('/registration/login')
    if request.method == 'POST':
        userid = con.get_user(username)['id']
        comment_info = {'id': con.get_next_id('comment'), 
                        'answer_id': answer_id,
                        'submission_time': utl.get_current_time(), 
                        'message': request.form['comment'],
                        'userid': userid}
        con.add_comment_for_answer(comment_info)
        return redirect('/question/{0}'.format(question_id))
    return render_template(WEB_PAGES['add_comm'], question_id=question_id, username=username, account_type=account_type, app_theme=app_theme)


@app.route('/user/<_username_>/<tagid>/add-interest-to-user')
def add_interest_to_user(_username_, tagid):
    if is_logged_in():
        username = escape(session['username'])
        account_type = con.get_user(username)['role']
        userid = con.get_user(username)['id']
        app_theme = con.get_user(username)['app_theme']
    else:
        return redirect('/registration/login')
    con.add_interest_to_user(con.get_user(_username_)['id'], tagid)
    return redirect(f'/user/{_username_}/choose-interests')


@app.route('/user/<on_page_username>/follow')
def follow_user(on_page_username):
    if is_logged_in():
        username = escape(session['username'])
        account_type = con.get_user(username)['role']
        userid = con.get_user(username)['id']
        app_theme = con.get_user(username)['app_theme']
    else:
        return redirect('/registration/login')
    con.follow_user(con.get_user(username)['id'], con.get_user(on_page_username)['id'])
    return redirect(f'/user/{on_page_username}')

#=====================================================================================================================================================

# EDITING ROUTES: edit question, edit answer, edit comment for question, edit comment for answer

@app.route("/question/<question_id>/edit", methods=["GET", "POST"])
def edit_question(question_id):
    if is_logged_in():
        username = escape(session['username'])
        account_type = con.get_user(username)['role']
        userid = con.get_user(username)['id']
        app_theme = con.get_user(username)['app_theme']
    else:
        return redirect('/registration/login')
    question = utl.check_specific_question_for_edit(dmg.get_question_by_id(question_id))
    question.update({'username': con.get_user_by_id(question['userid'])['username']})
    question['image'] = url_for('static', filename=question['image'])
    if request.method == "POST":
        edited_question_info = dict(request.form)
        if request.files['image'].filename != '':
            edited_question_info['image'] = save_image(request.files['image'])
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
    return render_template(WEB_PAGES['edit_q'], question_info=question_info, 
                                        all_tags=all_tags, tags_for_question=tags_for_question, 
                                        username=username, account_type=account_type, question=question, app_theme=app_theme)


@app.route('/answer/<question_id>/<answer_id>/edit', methods=['GET', 'POST'])
def edit_answer(question_id, answer_id):
    if is_logged_in():
        username = escape(session['username'])
        account_type = con.get_user(username)['role']
        userid = con.get_user(username)['id']
        app_theme = con.get_user(username)['app_theme']
    else:
        return redirect('/registration/login')
    answer = dmg.get_answer_by_id(answer_id)
    answer['image'] = url_for('static', filename=answer['image'])
    if request.method == "POST":
        edited_answer_info = dict(request.form)
        edited_answer_info['image'] = save_image(request.files['image'])
        edited_answer_info['message'] = edited_answer_info['message'] + ' (Edited)'
        new_submission_time = utl.get_current_time()
        con.edit_answer(answer_id, edited_answer_info, new_submission_time)
        return redirect('/question/{0}'.format(question_id))
    answers = con.get_answers()
    return render_template(WEB_PAGES['edit_ans'], selected_answer=answer, username=username, account_type=account_type, app_theme=app_theme)



@app.route('/question/<question_id>/<comment_id>/edit-comment', methods=['GET', 'POST'])
def edit_comment_for_question(question_id, comment_id):
    if is_logged_in():
        username = escape(session['username'])
        account_type = con.get_user(username)['role']
        userid = con.get_user(username)['id']
        app_theme = con.get_user(username)['app_theme']
    else:
        return redirect('/registration/login')
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
    return render_template('edit_comment.html', comment=comment, username=username, account_type=account_type, app_theme=app_theme)


@app.route('/answer/<answer_id>/<question_id>/<comment_id>/edit-comment', methods=['GET', 'POST'])
def edit_comment_for_answer(answer_id, question_id, comment_id):
    if is_logged_in():
        username = escape(session['username'])
        account_type = con.get_user(username)['role']
        userid = con.get_user(username)['id']
        app_theme = con.get_user(username)['app_theme']
    else:
        return redirect('/registration/login')
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
    return render_template('edit_comment.html', comment=comment, username=username, account_type=account_type, app_theme=app_theme)


@app.route('/answer/<question_id>/<answer_id>/mark-accepted')
def mark_answer_accepted(question_id, answer_id):
    if is_logged_in():
        username = escape(session['username'])
        account_type = con.get_user(username)['role']
        userid = con.get_user(username)['id']
        app_theme = con.get_user(username)['app_theme']
    else:
        return redirect('/registration/login')
    con.mark_answer_accepted(question_id, answer_id)
    answer_userid = dmg.get_answer_by_id(answer_id)['userid']
    con.increase_rank(answer_id, 15)
    return redirect(f'/question/{question_id}')

#====================================================================================================================================================

# DELETING ROUTES: delete question, delete answer, delete comment, delete tag

@app.route("/question/<question_id>/delete")
def delete_question(question_id):
    if is_logged_in():
        username = escape(session['username'])
        account_type = con.get_user(username)['role']
        userid = con.get_user(username)['id']
        app_theme = con.get_user(username)['app_theme']
    else:
        return redirect('/registration/login')
    con.delete_question(question_id)
    return redirect("/")


@app.route("/answer/<question_id>/<answer_id>/delete")
def delete_answer(question_id, answer_id):
    if is_logged_in():
        username = escape(session['username'])
        account_type = con.get_user(username)['role']
        userid = con.get_user(username)['id']
        app_theme = con.get_user(username)['app_theme']
    else:
        return redirect('/registration/login')
    con.delete_answer(answer_id)
    return redirect("/question/{0}".format(question_id))


@app.route('/comments/<comment_id>/delete')
def delete_comments(comment_id):
    if is_logged_in():
        username = escape(session['username'])
        account_type = con.get_user(username)['role']
        userid = con.get_user(username)['id']
        app_theme = con.get_user(username)['app_theme']
    else:
        return redirect('/registration/login')
    question_id = con.delete_comment(comment_id)['question_id']
    return redirect('/question/{0}'.format(question_id))


@app.route('/question/<question_id>/<tag_name>/delete-tag')
def delete_tag(question_id, tag_name):
    if is_logged_in():
        username = escape(session['username'])
        account_type = con.get_user(username)['role']
        userid = con.get_user(username)['id']
        app_theme = con.get_user(username)['app_theme']
    else:
        return redirect('/registration/login')
    con.delete_question_tag(question_id, tag_name)
    return redirect('/question/{0}/edit'.format(question_id))


@app.route('/user/<_username_>/<tagid>/remove-tag')
def remove_tag_from_user(_username_, tagid):
    if is_logged_in():
        username = escape(session['username'])
        account_type = con.get_user(username)['role']
        userid = con.get_user(username)['id']
        app_theme = con.get_user(username)['app_theme']
    else:
        return redirect('/registration/login')
    con.remove_tag_from_user(con.get_user(_username_)['id'], tagid)
    return redirect(f'/user/{_username_}')


@app.route('/user/<on_page_username>/unfollow')
def unfollow_user(on_page_username):
    if is_logged_in():
        username = escape(session['username'])
        account_type = con.get_user(username)['role']
        userid = con.get_user(username)['id']
        app_theme = con.get_user(username)['app_theme']
    else:
        return redirect('/registration/login')
    con.unfollow_user(con.get_user(username)['id'], con.get_user(on_page_username)['id'])
    return redirect(f'/user/{on_page_username}')

#==================================================================================================================================================

# VOTING ROUTES: vote question, vote answer

@app.route("/question/<question_id>/<vote>")
def vote_question(question_id, vote):
    if is_logged_in():
        username = escape(session['username'])
        account_type = con.get_user(username)['role']
        userid = con.get_user(username)['id']
        app_theme = con.get_user(username)['app_theme']
    else:
        return redirect('/registration/login')
    con.vote_question(question_id, vote)
    userid = con.get_user(username)['id']
    con.user_vote_question(question_id, userid, vote)
    question_userid = dmg.get_question_by_id(question_id)['userid']
    if vote == 'vote-up': con.increase_rank(question_userid, 5)
    elif vote == 'vote-down': con.decrease_rank(question_userid, 2)
    return redirect("/question/{0}".format(question_id))


@app.route('/question/<question_id>/<vote>/unvote-question')
def unvote_question(question_id, vote):
    if is_logged_in():
        username = escape(session['username'])
        account_type = con.get_user(username)['role']
        userid = con.get_user(username)['id']
        app_theme = con.get_user(username)['app_theme']
    else:
        return redirect('/registration/login')
    con.unvote_question(question_id, vote)
    con.user_unvote_question(question_id, userid)
    question_userid = dmg.get_question_by_id(question_id)['userid']
    if vote == 'vote-up': con.decrease_rank(question_userid, 5)
    elif vote == 'vote-down': con.increase_rank(question_userid, 2)
    return redirect("/question/{0}".format(question_id))


@app.route("/answer/<question_id>/<answer_id>/<vote>")
def vote_answer(question_id, answer_id, vote):
    if is_logged_in():
        username = escape(session['username'])
        account_type = con.get_user(username)['role']
        userid = con.get_user(username)['id']
        app_theme = con.get_user(username)['app_theme']
    else:
        return redirect('/registration/login')
    con.vote_answer(answer_id, vote)
    userid = con.get_user(username)['id']
    con.user_vote_answer(answer_id, userid, vote)
    answer_userid = dmg.get_answer_by_id(answer_id)['userid']
    if vote == 'vote-up': con.increase_rank(answer_userid, 10)
    elif vote == 'vote-down': con.decrease_rank(answer_userid, 2)
    return redirect("/question/{0}".format(question_id))


@app.route("/answer/<question_id>/<answer_id>/<vote>/unvote-answer")
def unvote_answer(question_id, answer_id, vote):
    if is_logged_in():
        username = escape(session['username'])
        account_type = con.get_user(username)['role']
        userid = con.get_user(username)['id']
        app_theme = con.get_user(username)['app_theme']
    else:
        return redirect('/registration/login')
    con.unvote_answer(answer_id, vote)
    con.user_unvote_answer(answer_id, userid)
    answer_userid = dmg.get_answer_by_id(answer_id)['userid']
    if vote == 'vote-up': con.decrease_rank(answer_userid, 10)
    elif vote == 'vote-down': con.increase_rank(answer_userid, 2)
    return redirect("/question/{0}".format(question_id))


#=====================================================================================================================================================

# REGISTRATION
import authentication as athn

@app.route('/registration/signup', methods=['GET', 'POST'])
def signup():
    if is_logged_in():
        username = escape(session['username'])
        account_type = con.get_user(username)['role']
        userid = con.get_user(username)['id']
        app_theme = con.get_user(username)['app_theme']
    else:
        username = None
        account_type = None
        userid = None
        app_theme = 'black_orange'
    username_error = False
    email_error = False
    password_match_error = False
    if request.method == 'POST':
        _username_ = request.form.get('username')
        email = request.form.get('email')
        if not dmg.check_for_unique_username(_username_): username_error = True
        if not dmg.check_for_unique_email(email): email_error = True
        if username_error == True or email_error == True:
            return render_template('signup.html', username=username, account_type=account_type, 
                                    username_error=username_error, email_error=email_error, password_match_error=password_match_error, app_theme=app_theme)
        plain_text_password = request.form.get('password')
        repeat_password = request.form.get('repeat_password')
        if plain_text_password != repeat_password:
            password_match_error = True
            return render_template('signup.html', username=username, account_type=account_type, 
                                        username_error=username_error, email_error=email_error, password_match_error=password_match_error, app_theme=app_theme)
        password = athn.hash_password(plain_text_password)
        created = utl.get_current_time()
        user = {'username': _username_, 'email': email, 'password': password, 'role': 'normal_user', 'created': created, 'rank': 0, 'app_theme': 'black_orange'}
        con.add_new_user(user)
        return redirect('/registration/login')
    return render_template('signup.html', username=username, account_type=account_type, 
                            username_error=username_error, email_error=email_error, password_match_error=password_match_error, app_theme=app_theme)


@app.route('/registration/login', methods=['GET', 'POST'])
def login():
    if is_logged_in():
        username = escape(session['username'])
        account_type = con.get_user(username)['role']
        userid = con.get_user(username)['id']
        app_theme = con.get_user(username)['app_theme']
    else:
        username = None
        account_type = None
        userid = None
        app_theme = 'black_orange'
    login_error = False
    if request.method == 'POST':
        username = request.form.get('username')
        plain_text_password = request.form.get('password')
        db_hashed_password = con.get_hashed_pass(username)
        if db_hashed_password == None:
            login_error = True
            return render_template('login.html', login_error=login_error, username=username, account_type=account_type, app_theme=app_theme)
        is_matching = athn.verify_password(plain_text_password, db_hashed_password)
        if is_matching:
            session['username'] = username
            return redirect('/')
        else:
            login_error = True
            return render_template('login.html', login_error=login_error, username=username, account_type=account_type, app_theme=app_theme)
    return render_template('login.html', login_error=login_error, username=username, account_type=account_type, app_theme=app_theme)


@app.route('/logout')
def logout():
    if is_logged_in():
        username = escape(session['username'])
        account_type = con.get_user(username)['role']
        userid = con.get_user(username)['id']
        app_theme = con.get_user(username)['app_theme']
    else:
        return redirect('/registration/login')
    session.pop('username', None)
    username = None
    return redirect('/')

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
    app.run(debug=True)