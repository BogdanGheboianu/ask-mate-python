import connection as con
import os

# REQUESTS FROM connection.py
def get_question_by_id(question_id):
    questions = con.get_questions('id', 'ascending')
    for question in questions:
        if question['id'] == int(question_id): return question

def get_answer_by_id(answer_id):
    answers = con.get_answers()
    for answer in answers:
        if answer['id'] == int(answer_id): return answer


def get_answers_for_question(question_id):
    answers = con.get_answers()
    answers_for_question = []
    for answer in answers:
        if answer['question_id'] == int(question_id):
            answers_for_question.append(answer)
    if len(answers_for_question) == 0: return None
    else: return answers_for_question


def get_comments_for_question(question_id, limit):
    if limit == 'no-limit':
        comments = con.get_comments('no-limit')
    elif limit == 'limit':
        comments = con.get_comments('limit')
    comments_for_question = []
    for comment in comments:
        if comment['question_id'] != None and comment['question_id'] == int(question_id):
            comments_for_question.append(comment)
    if len(comments_for_question) == 0: return None
    else: return comments_for_question


def get_answers_for_question_comments(question_id):
    answers_for_question = get_answers_for_question(int(question_id))
    comments = con.get_comments('no-limit')
    comments_for_answers = []
    if answers_for_question != None:
        for answer in answers_for_question:
            for comment in comments:
                if comment['answer_id'] != None and comment['answer_id'] == answer['id']:
                    comments_for_answers.append(comment)
    if len(comments_for_answers) == 0: return None
    else: return comments_for_answers


def get_tags_for_question(question_id):
    tags = con.get_tags()
    question_tags = con.get_question_tags()
    tags_ids_for_question = []
    for question_tag in question_tags:
        if question_tag['question_id'] == int(question_id):
            tags_ids_for_question.append(question_tag['tag_id'])
    tags_for_question = []
    for tag_id in tags_ids_for_question:
        for tag in tags:
            if tag['id'] == tag_id:
                tags_for_question.append(tag['name'])
    if len(tags_for_question) == 0: return None
    else: return tags_for_question

#===================================================================================================================================================

# SEARCH FUNCTIONS

def search(search_phrase):
    TITLES = 1
    MESSAGES = 0
    search_phrase_list_of_words = search_phrase.split(' ')
    search_results_in_question_titles = search_in_questions(search_phrase_list_of_words)[TITLES]
    search_results_in_question_messages = search_in_questions(search_phrase_list_of_words)[MESSAGES]
    search_results_in_tags = search_in_tags(search_phrase_list_of_words)
    search_results_in_answers = search_in_answers(search_phrase_list_of_words)
    search_results_in_comments = search_in_comments(search_phrase_list_of_words)
    search_results = {
        'question_title': search_results_in_question_titles,
        'question_message': search_results_in_question_messages,
        'tags': search_results_in_tags,
        'answers': search_results_in_answers,
        'comments': search_results_in_comments}
    for result in search_results.values():
        if result:
            return search_results


def search_in_questions(search_phrase_list_of_words):
    search_results_in_question_titles = []
    search_results_in_question_messages = []
    for search_term in search_phrase_list_of_words:
        questions = con.get_questions_for_search()
        for question in questions:
            if search_term in question['title'].lower():
                if question not in search_results_in_question_titles:
                    search_results_in_question_titles.append(question)
            if search_term in question['message'].lower():
                if question not in search_results_in_question_messages:
                    search_results_in_question_messages.append(question)
    return search_results_in_question_messages, search_results_in_question_titles


def search_in_answers(search_phrase_list_of_words):
    search_results_in_answers = []
    for search_term in search_phrase_list_of_words:
        answers = con.get_answers()
        for answer in answers:
            if search_term in answer['message'].lower():
                if answer not in search_results_in_answers:
                    search_results_in_answers.append(answer)
    return search_results_in_answers


def search_in_tags(search_phrase_list_of_words):
    search_results_in_tags = []
    for search_term in search_phrase_list_of_words:
        tags = con.get_tags()
        question_tags = con.get_question_tags()
        tags_ids = []
        for tag in tags:
            if search_term in tag['name'].lower():
                if tag['id'] not in tags_ids:
                    tags_ids.append(tag['id'])
        questions_ids = []
        for tag_id in tags_ids:
            for question_tag in question_tags:
                if tag_id == question_tag['tag_id']:
                    if question_tag['tag_id'] not in questions_ids:
                        questions_ids.append(question_tag['question_id'])
        questions = con.get_questions_for_search()
        for question_id in questions_ids:
            for question in questions:
                if question_id == question['id']:
                    if question not in search_results_in_tags:
                        search_results_in_tags.append(question)
        for question in search_results_in_tags:
            tags_to_add = []
            for question_tag in question_tags:
                if question['id'] == question_tag['question_id']:
                    for tag in tags:
                        if question_tag['tag_id'] == tag['id']:
                            tags_to_add.append(tag['name'])
            question.update({'tags': tags_to_add})
    return search_results_in_tags


def search_in_comments(search_phrase_list_of_words):
    search_results_in_comments = []
    for search_term in search_phrase_list_of_words:
        comments = con.get_comments('no-limit')
        for com in comments:
            if search_term in com['message'].lower():
                if com not in search_results_in_comments:
                    search_results_in_comments.append(com)
    return search_results_in_comments


def check_for_unique_username(username):
    unique = True
    all_users = con.get_all_users()
    for user in all_users:
        if username == user['username']:
            unique = False
    return unique


def check_for_unique_email(email):
    unique = True
    all_users = con.get_all_users()
    for user in all_users:
        if email == user['email']:
            unique = False
    return unique
