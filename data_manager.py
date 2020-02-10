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

