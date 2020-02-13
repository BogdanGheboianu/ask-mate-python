from csv import DictReader, DictWriter
import connection as con
import os

answer_file = "sample_data/answer.csv"
question_file = "sample_data/question.csv"

answer_fieldnames = ["id", "submission_time",
                      "vote_number", "question_id", "message", "image"]
                      
questions_fieldnames = ["id", "submission_time", "view_number",
                      "vote_number", "title", "message", "image"]


def add(info, data_file, fieldnames):
    '''
    Adds new question or new answer to the specific file.
    '''
    with open(data_file, "a") as file:
        writer = DictWriter(file, fieldnames=fieldnames)
        if con.get_all(data_file) is False:
            writer.writeheader()
        writer.writerow(info)
        file.close()


# QUESTIONS FUNCTIONS: get_question_by_id

def get_question_by_id(question_id):
    '''
    Searches in all questions and returns the questions whose id matches the requested id.
    Returns None if no matching id was found.
    '''
    all_questions = con.get_all(question_file)
    for question in all_questions:
        if int(question['id']) == int(question_id):
            return question
    return None


def add_view(question_id):
    '''
    Adds +1 to the view_number key of the requested question whenever the question is accessed.
    '''
    original_questions_data = con.get_all(question_file)
    updated_questions_data = []
    for question in original_questions_data:
        if int(question['id']) == int(question_id):
            question["view_number"] = str(int(question['view_number']) + 1)
            updated_questions_data.append(question)
        else:
            updated_questions_data.append(question)
    con.write_data_to_file(updated_questions_data, question_file, questions_fieldnames)



def sort_questions(sort_factor, order):
    ''' 
    Returns a list of dicts with the questions sorted by a requested factor and by order.
    '''
    sort_factor_occurences = []
    all_questions = con.get_all(question_file)
    for question in all_questions:
        if sort_factor == "view_number" or sort_factor == "vote_number":
            sort_factor_occurences.append(int(question[sort_factor]))
        else:
            sort_factor_occurences.append(question[sort_factor])
    if order == "descending":
        sorted_factor_occurrences = sorted(sort_factor_occurences, reverse=True)
    else:
        sorted_factor_occurrences = sorted(sort_factor_occurences, reverse=False)
    sorted_questions = []
    for factor_occurrence in sorted_factor_occurrences:
        for question in all_questions:
            if sort_factor == "view_number" or sort_factor == "vote_number":
                if int(question[sort_factor]) == int(factor_occurrence):
                    if question not in sorted_questions:
                        sorted_questions.append(question)
            else:
                if question[sort_factor] == factor_occurrence:
                    if question not in sorted_questions:
                        sorted_questions.append(question)
    return sorted_questions


def edit_question(question_id, edited_question_info):
    '''
    Edits the title and the message of the requested question.
    '''
    original_questions_data = con.get_all(question_file)
    updated_questions_data = []
    for question in original_questions_data:
        if int(question['id']) == int(question_id):
            question["title"] = edited_question_info['title']
            question['message'] = edited_question_info['message']
            updated_questions_data.append(question)
        else:
            updated_questions_data.append(question)
    con.write_data_to_file(updated_questions_data, question_file, questions_fieldnames)


def delete_question(question_id):
    '''
    Deletes the requested question and its answers.
    '''
    original_questions_data = con.get_all(question_file)
    updated_questions_data = []
    for question in original_questions_data:
        if int(question['id']) != int(question_id):
            updated_questions_data.append(question)
    con.write_data_to_file(updated_questions_data, question_file, questions_fieldnames)
    original_answers = con.get_all(answer_file)
    updated_answers = []
    for answer in original_answers:
        if int(answer['question_id']) != int(question_id):
            updated_answers.append(answer)
    con.write_data_to_file(updated_answers, answer_file, answer_fieldnames)



def vote_question(question_id, vote):
    '''
    Adds 1 or substratcs 1 (depending on the request) from the vote_number key of a question.
    '''
    original_questions = con.get_all(question_file)
    updated_questions = []
    for question in original_questions:
        if int(question['id']) == int(question_id):
            votes = question['vote_number'].split('-')
            if vote == "vote-up":
                votes[0] = str(int(votes[0]) + 1)
            elif vote == "vote-down":
                votes[1] = str(int(votes[1]) + 1)
            vote_number = "-".join(votes)
            question['vote_number'] = vote_number
            updated_questions.append(question)
        else:
            updated_questions.append(question)
    con.write_data_to_file(updated_questions, question_file, questions_fieldnames)
    

def vote_percentage(question_id):
    question = get_question_by_id(question_id)
    votes = question['vote_number'].split('-')
    total_votes = int(votes[0]) + int(votes[1])
    up_votes_percentage = float(int(votes[0]) / int(total_votes)) * 100
    return int(up_votes_percentage)


# ANSWERS FUNCTIONS: 

def find_answers_by_question_id(question_id):
    '''
    Searches the answer file and extracts the answers for a specific question_id.
    '''
    all_answers = con.get_all(answer_file)
    answers_for_question = []
    for answer in all_answers:
        if int(answer['question_id']) == int(question_id):
            answers_for_question.append(answer)
    if len(answers_for_question) == 0: return None
    else: return answers_for_question


def get_answer_by_id(answer_id, question_id):
    answers = find_answers_by_question_id(question_id)
    for answer in answers:
        if int(answer['id']) == int(answer_id):
            return answer

def vote_percentage_answer(answer_id, question_id):
    answer = get_answer_by_id(answer_id, question_id)
    votes = answer['vote_number'].split('-')
    total_votes = int(votes[0]) + int(votes[1])
    up_votes_percentage = float(int(votes[0]) / int(total_votes)) * 100
    return int(up_votes_percentage)



def vote_answer(question_id, answer_id, vote):
    '''
    Adds 1 or substratcs 1 (depending on the request) from the vote_number key of an answer.
    '''
    original_answers = con.get_all(answer_file)
    updated_answers = []
    for answer in original_answers:
        if int(answer["id"]) == int(answer_id) and int(answer['question_id']) == int(question_id):
            votes = answer['vote_number'].split('-')
            if vote == "vote-up":
                votes[0] = str(int(votes[0]) + 1)
            elif vote == "vote-down":
                votes[1] = str(int(votes[1]) + 1)
            vote_number = "-".join(votes)
            answer['vote_number'] = vote_number
            updated_answers.append(answer)
        else:
            updated_answers.append(answer)
    con.write_data_to_file(updated_answers, answer_file, answer_fieldnames)


def delete_answer(answer_id):
    '''
    Deletes requested answer.
    '''
    original_answers = con.get_all(answer_file)
    updated_answers = []
    for answer in original_answers:
        if int(answer['id']) != int(answer_id):
            updated_answers.append(answer)
    con.write_data_to_file(updated_answers, answer_file, answer_fieldnames)
