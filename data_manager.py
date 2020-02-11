from csv import DictReader, DictWriter

answer_file = "sample_data/answer.csv"
question_file = "sample_data/question.csv"


def get_all_questions():
    '''
    Reads questions file and extracts all the questions.
    Returns a list with all the questions or returns False if there are no questions.
    '''
    questions = []
    with open(question_file, "r") as file:
        for dictionary in DictReader(file):
            questions.append(dictionary)
        file.close()
    if len(questions) == 0:
        return False
    else:
        return questions


def get_all_answers():
    answers = []
    with open(answer_file, "r") as file:
        for dictionary in DictReader(file):
            answers.append(dictionary)
        file.close()
    if len(answers) == 0:
        return False
    else:
        return answers


def get_question_by_id(question_id):
    '''
    Searches in all questions and returns the questions whose id matches the requested id.
    Returns None if no matching id was found.
    '''
    all_questions = get_all_questions()
    for question in all_questions:
        if int(question['id']) == int(question_id):
            return question
    return None


def find_next_question_index():
    '''
    Finds the biggest count index in a project file.
    Return that count index + one to be used for the next story to come.
    '''
    return max([int(story['id']) for story in get_all_questions()]) + 1


def find_next_answer_index():
    return max([int(story['id']) for story in get_all_answers()]) + 1


def add_question_to_file(question_info):
    with open(question_file, "a") as file:
        fieldnames = ["id", "submission_factor_occurrence", "view_number",
                      "vote_number", "title", "message", "image"]
        writer = DictWriter(file, fieldnames=fieldnames)
        if get_all_questions() is False:
            writer.writeheader()
        writer.writerow(question_info)
        file.close()


def find_answers_by_question_id(question_id):
    all_answers = get_all_answers()
    answers_for_question = []
    for answer in all_answers:
        if int(answer['question_id']) == int(question_id):
            answers_for_question.append(answer)
    if len(answers_for_question) == 0:
        return None
    else:
        return answers_for_question


def add_answer_to_question(answer_info):
    with open(answer_file, "a") as file:
        fieldnames = ["id", "submission_time",
                      "vote_number", "question_id", "message", "image"]
        writer = DictWriter(file, fieldnames=fieldnames)
        if get_all_answers() is False:
            writer.writeheader()
        writer.writerow(answer_info)
        file.close()


def add_view(question_id):
    original_questions_data = get_all_questions()
    updated_questions_data = []
    for question in original_questions_data:
        if int(question['id']) == int(question_id):
            question["view_number"] = str(int(question['view_number']) + 1)
            updated_questions_data.append(question)
        else:
            updated_questions_data.append(question)
    with open(question_file, "w") as file:
        fieldnames = ["id", "submission_time", "view_number", "vote_number", "title", "message", "image"]
        writer = DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        for question in updated_questions_data:
            writer.writerow(question)
        file.close()

        
def sort_questions(sort_factor, order):
    ''' 
    Returns a dictionary with the questions sorted by a requested factor and by order
    '''
    sort_factor_occurences = []
    all_questions = get_all_questions()
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
