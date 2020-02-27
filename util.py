import uuid
from datetime import datetime
import data_manager as dmg
from flask import url_for


def check_specific_question_for_edit(question):
    print(question)
    if "(Edited)" in question['title']:
        question['submission_time'] = str(
            question['submission_time']) + " (edited)"
        question['title'] = question['title'].replace("(Edited)", "")
    return question


def check_questions_for_edit(questions):
    for question in questions:
        if "(Edited)" in question['title']:
            question['submission_time'] = str(
                question['submission_time']) + " (edited)"
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

# def convert_unix_time_to_readable_format(list_of_dicts):
#     '''
#     Converts and returns the given unix time to a readable format: date and time
#     '''
#     try:
#         for _dict in list_of_dicts:
#             _dict['submission_time'] = datetime.utcfromtimestamp(int(_dict['submission_time'])).strftime('%Y-%m-%d %H:%M:%S')
#         return list_of_dicts
#     except TypeError:
#         return None


# def prepare_questions_for_html(sort_info):
#     all_questions = convert_unix_time_to_readable_format(dmg.sort_questions(sort_info["sort_by"], sort_info["order"]))
#     for question in all_questions: question['vote_number'] = "{0}%".format(dmg.vote_percentage(question['id']))
#     all_questions = check_questions_for_edit(all_questions)
#     return all_questions
