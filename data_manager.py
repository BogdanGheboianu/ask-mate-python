from csv import DictReader, DictWriter
import connection as con

answer_file = "sample_data/answer.csv"
question_file = "sample_data/question.csv"

answer_fieldnames = ["id", "submission_time",
                      "vote_number", "question_id", "message", "image"]
                      
questions_fieldnames = ["id", "submission_time", "view_number",
                      "vote_number", "title", "message", "image"]


def add(info, data_file, fieldnames):
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
    Returns a dictionary with the questions sorted by a requested factor and by order
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
    original_questions = con.get_all(question_file)
    updated_questions = []
    for question in original_questions:
        if int(question['id']) == int(question_id):
            if vote == "vote-up":
                question['vote_number'] = int(question['vote_number']) + 1
                updated_questions.append(question)
            elif vote == "vote-down":
                question['vote_number'] = int(question['vote_number']) - 1
                updated_questions.append(question)
        else:
            updated_questions.append(question)
    con.write_data_to_file(updated_questions, question_file, questions_fieldnames)


# ANSWERS FUNCTIONS: 

def find_answers_by_question_id(question_id):
    all_answers = con.get_all(answer_file)
    answers_for_question = []
    for answer in all_answers:
        if int(answer['question_id']) == int(question_id):
            answers_for_question.append(answer)
    if len(answers_for_question) == 0: return None
    else: return answers_for_question


def vote_answer(question_id, answer_id, vote):
    original_answers = con.get_all(answer_file)
    updated_answers = []
    for answer in original_answers:
        if int(answer["id"]) == int(answer_id) and int(answer['question_id']) == int(question_id):
            if vote == "vote-up":
                answer['vote_number'] = int(answer['vote_number']) + 1
            elif vote == "vote-down":
                answer['vote_number'] = int(answer['vote_number']) - 1
            updated_answers.append(answer)
        else:
            updated_answers.append(answer)
    con.write_data_to_file(updated_answers, answer_file, answer_fieldnames)


def delete_answer(answer_id):
    original_answers = con.get_all(answer_file)
    updated_answers = []
    for answer in original_answers:
        if int(answer['id']) != int(answer_id):
            updated_answers.append(answer)
    con.write_data_to_file(updated_answers, answer_file, answer_fieldnames)
