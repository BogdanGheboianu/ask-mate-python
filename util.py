import uuid
from datetime import datetime
import data_manager as dmg
from flask import url_for

def convert_unix_time_to_readable_format(list_of_dicts):
    '''
    Converts and returns the given unix time to a readable format: date and time
    '''
    try:
        for _dict in list_of_dicts:
            _dict['submission_time'] = datetime.utcfromtimestamp(int(_dict['submission_time'])).strftime('%Y-%m-%d %H:%M:%S')
        return list_of_dicts
    except TypeError:
        return None


def transform_image_title(filename):
    '''
    Converts an image name to an uuid4 id and returns it.
    '''
    filename_splited = filename.split(".")
    filename_splited[0] = str(uuid.uuid4())
    unique_filename = ".".join(filename_splited)
    return unique_filename


def allowed_file(filename):
    '''
    Verifies if the uploaded file has a valid file extension.
    '''
    ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}  
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def prepare_answers_for_hmtl(answers, question_id):
    for answer in answers:
        answer['vote_number'] = dmg.vote_percentage_answer(answer['id'], question_id)
        if answer['image'] != '':
            answer['image'] = url_for('static', filename=answer['image'])
    return answers


def prepare_questions_for_html(sort_info):
    all_questions = convert_unix_time_to_readable_format(dmg.sort_questions(sort_info["sort_by"], sort_info["order"]))
    for question in all_questions:
        question['vote_number'] = "{0}%".format(dmg.vote_percentage(question['id']))
    return all_questions