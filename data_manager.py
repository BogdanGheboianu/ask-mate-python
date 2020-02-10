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
    if len(questions) == 0: return False
    else: return questions


def get_all_answers():
    answers = []
    with open(answer_file, "r") as file:
        for dictionary in DictReader(file):
            answers.append(dictionary)
        file.close()
    if len(answers) == 0: return False
    else: return answers


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


def add_question_to_file(question_info):
    with open(question_file, "a") as file:
        print(question_info)
        fieldnames = ["id", "submission_time", "view_number", "vote_number", "title", "message", "image"]
        writer = DictWriter(file, fieldnames=fieldnames)
        if get_all_questions() is False:
            writer.writeheader()
        else:
            question_info["id"] = find_next_question_index()
        writer.writerow(question_info)
        file.close()


def find_answers_by_id(question_id):
    all_answers = get_all_answers()
    answers_for_question = []
    for answer in all_answers:
        if int(answer['id']) == int(question_id):
            answers_for_question.append(answer)
    if len(answers_for_question) == 0: return None
    else: return answers_for_question