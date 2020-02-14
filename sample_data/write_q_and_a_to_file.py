import csv
from csv import DictReader, DictWriter
from datetime import datetime
import time, calendar

QA_FILE = 'sample_data/sample_q_and_a.txt'
QUESTIONS_FILE = 'question.csv'
ANSWER_FILE = 'answer.csv'

def extract_data():
    '''
    Returns list with strings (question + answer).
    '''
    file = open(QA_FILE, encoding="utf8")
    content = file.readlines()
    file.close()
    qas = [item.replace("\n", "") for item in content]
    return qas


def organize_qas(qas):
    '''
    Returns a dict with question as key and answer as value.
    '''
    QUESTION = 0
    ANSWER = 1
    qas_dict = {}
    for pair in qas:
        pair_list = pair.split("?")
        try:
            qas_dict.update({pair_list[QUESTION]: pair_list[ANSWER]})
        except IndexError:
            pass
    return qas_dict


def create_list_of_dicts_info(qas_dict):
    all_questions = []
    all_answers = []
    question_count = 5
    answer_count = 12
    for question, answer in qas_dict.items():
        # for questions:
        question_dict = {}
        question_id = question_count
        question_splitted = question.split()
        question_title = question_splitted[0] + question_splitted[1] + "..."
        question_message = question
        question_submission_time = int(calendar.timegm(time.gmtime())) + 7200
        question_vote_number = "0-0"
        question_view_number = "0"
        question_image = ""
        question_dict.update({"id": question_id, "submission_time": question_submission_time, "view_number": question_view_number, 
                                "vote_number": question_vote_number, "title": question_title, "message": question_message, "image": question_image})
        # for answers:
        answer_dict = {}
        answer_id = answer_count
        answer_submission_time = int(calendar.timegm(time.gmtime())) + 7200000
        answer_vote_number = "0-0"
        answer_question_id = question_id
        answer_message = answer
        answer_image = ""
        answer_dict.update({"id": answer_id, "submission_time": answer_submission_time, "vote_number": answer_vote_number, 
                                "question_id": answer_question_id, "message": answer_message, "image": answer_image})

        all_questions.append(question_dict)
        all_answers.append(answer_dict)
        answer_count += 1
        question_count += 1

    return all_questions, all_answers


def write_questions_to_file(all_questions):
    fieldnames = ["id", "submission_time", "view_number", "vote_number", "title", "message", "image"]
    with open(QUESTIONS_FILE, "a") as file:
        writer = DictWriter(file, fieldnames=fieldnames)
        for question in all_questions:
            writer.writerow(question)
        file.close()


def write_answers_to_file(all_answers):
    fieldnames = ["id", "submission_time", "vote_number", "question_id", "message", "image"]
    with open(ANSWER_FILE, "a") as file:
        writer = DictWriter(file, fieldnames=fieldnames)
        for question in all_answers:
            writer.writerow(question)
        file.close()


create_list_of_dicts_info(organize_qas(extract_data()))
    

def main():
    ALL_QUESTIONS = 0
    ALL_ANSWERS = 1
    write_questions_to_file(create_list_of_dicts_info(organize_qas(extract_data()))[ALL_QUESTIONS])
    write_answers_to_file(create_list_of_dicts_info(organize_qas(extract_data()))[ALL_ANSWERS])


if __name__ == "__main__":
    main()