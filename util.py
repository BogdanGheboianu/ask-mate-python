import uuid
from datetime import datetime
import data_manager as dmg
from flask import url_for


def check_specific_question_for_edit(question):
    if "(Edited)" in question['title']:
        question['submission_time'] = str(question['submission_time']) + " (edited)"
        question['title'] = question['title'].replace("(Edited)", "")
    return question

def check_questions_for_edit(questions):
    if questions != None:
        for question in questions:
            if "(Edited)" in question['title']:
                question['submission_time'] = str(question['submission_time']) + " (edited)"
                question['title'] = question['title'].replace("(Edited)", "")
        return questions


def prepare_answers_for_hmtl(answers, question_id):
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
    if answers != None:
        for answer in answers:
            if "(Edited)" in answer['message']:
                answer['submission_time'] = str(answer['submission_time']) + " (edited)"
                answer['message'] = answer['message'].replace("(Edited)", "")
        return answers


def check_comments_for_edit(comments):
    if comments != None:
        for com in comments:
            if "(Edited)" in com['message']:
                com['submission_time'] = str(com['submission_time']) + " (edited)"
                com['message'] = com['message'].replace("(Edited)", "")
        return comments
