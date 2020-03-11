import uuid, calendar, time
from datetime import datetime
import data_manager as dmg
from flask import url_for


def check_specific_question_for_edit(question):
    """
    Looks through the title of the requested question for the phrase '(Edited)'. 
    If found, it takes it out and inserts '(edited)' after the submission time.
    """
    if "(Edited)" in question['title']:
        question['submission_time'] = str(
            question['submission_time']) + " (edited)"
        question['title'] = question['title'].replace("(Edited)", "")
    return question


def check_questions_for_edit(questions):
    """
    Does the same thing as the function above, but for a list of questions.
    """
    if questions != None:
        for question in questions:
            if "(Edited)" in question['title']:
                question['submission_time'] = str(
                    question['submission_time']) + " (edited)"
                question['title'] = question['title'].replace("(Edited)", "")
        return questions


def link_answer_with_image(answers, question_id):
    for answer in answers:
        if answer['image'] != '':
            answer['image'] = url_for('static', filename=answer['image'])
    return answers


def allowed_file(filename):
    '''
    Verifies if the uploaded file has a valid file extension.
    '''
    ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def transform_image_title(filename):
    '''
    Converts an image name to an uuid4 id and returns it.
    '''
    filename_splited = filename.split(".")
    filename_splited[0] = str(uuid.uuid4())
    unique_filename = ".".join(filename_splited)
    return unique_filename


def check_answers_for_edit(answers):
    """
    Same as the 'check_questions_for_edit()' function
    """
    if answers != None:
        for answer in answers:
            if "(Edited)" in answer['message']:
                answer['submission_time'] = str(
                    answer['submission_time']) + " (edited)"
                answer['message'] = answer['message'].replace("(Edited)", "")
        return answers


def check_comments_for_edit(comments):
    """
    Same as the 'check_questions_for_edit()' function
    """
    if comments != None:
        for com in comments:
            if "(Edited)" in com['message']:
                com['submission_time'] = str(
                    com['submission_time']) + " (edited)"
                com['message'] = com['message'].replace("(Edited)", "")
        return comments


def calculate_vote_percentage(votes_up, votes_down):
    total_votes = votes_up + votes_down
    try:
        vote_percentage = float(votes_up/total_votes) * 100
    except ZeroDivisionError:
        vote_percentage = 0
    return vote_percentage


def highlight(text, search_phrase):
    """
    Looks for the search phrase and/or search terms in a given text and prepares the results to be highlighted in HTML
    """
    if search_phrase in text.lower():
        text = text.lower().replace(search_phrase, "<span style='color: white; background-color: seagreen;'>{0}</span>".format(search_phrase))
    else:
        for search_term in search_phrase.split(" "):
            text = text.lower().replace(search_term, "<span style='color: white; background-color: seagreen;'>{0}</span>".format(search_term))
    return text


def escape_characters(text):
    """
    Allows for special char: ' to be inserted in every string that goes into sql tables
    """
    if '\'' in text:
        text = text.replace('\'', '\'\'')
    return text


def get_current_time():
    return datetime.utcfromtimestamp(int(calendar.timegm(time.gmtime())) + 7200).strftime('%Y-%m-%d %H:%M:%S')


def rearrange_order_of_keys_for_questions(questions):
    questions_modified_keys_order = []
    for question in questions:
        modified_question = {
            'title': question['title'],
            'message': question['message'],
            'vote_number': question['vote_number'],
            'view_number': question['view_number'],
            'submission_time': question['submission_time'],
            'id': question['id'],
            'image': question['image'],
            'votes_up': question['votes_up'],
            'votes_down': question['votes_down'],
            'code_snippet': question['code_snippet'],
            'userid': question['userid'],
            'acptd_answerid': question['acptd_answerid']}
        questions_modified_keys_order.append(modified_question)
    return questions_modified_keys_order

