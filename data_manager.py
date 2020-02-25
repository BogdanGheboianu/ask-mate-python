import connection as con
import os


def get_question_by_id(question_id):
    questions = con.get_questions('id', 'ascending')
    for question in questions:
        if question['id'] == int(question_id): return question


def get_answers_for_question(question_id):
    answers = con.get_answers()
    answers_for_question = []
    for answer in answers:
        if answer['question_id'] == int(question_id):
            answers_for_question.append(answer)
    if len(answers_for_question) == 0: return None
    else:
        return answers_for_question


def get_comments_for_question(question_id):
    comments = con.get_comments()
    comments_for_question = []
    for comment in comments:
        if comment['question_id'] != None and comment['question_id'] == int(question_id):
            comments_for_question.append(comment)
    if len(comments_for_question) == 0: return None
    else: return comments_for_question


def get_answers_for_question_comments(question_id):
    answers_for_question = get_answers_for_question(int(question_id))
    comments = con.get_comments()
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


    







# def add(info, data_file, fieldnames):
#     '''
#     Adds new question or new answer to the specific file.
#     '''
#     with open(data_file, "a") as file:
#         writer = DictWriter(file, fieldnames=fieldnames)
#         if con.get_all(data_file) is False:
#             writer.writeheader()
#         writer.writerow(info)
#         file.close()


# # QUESTIONS FUNCTIONS: get_question_by_id, add_view, sort_questions, edit_question, delete_question, vote_question

# def get_question_by_id(question_id):
#     '''
#     Searches in all questions and returns the questions whose id matches the requested id.
#     Returns None if no matching id was found.
#     '''
#     for question in con.get_all(question_file):
#         if int(question['id']) == int(question_id): return question
#     return None





# def sort_questions(sort_factor, order):
#     all_questions = con.get_all()
#     if order == "ascending": return sorted(all_questions, key=lambda i: int(i[sort_factor]))
#     else: return sorted(all_questions, key=lambda i: i[sort_factor], reverse=True)
    

# def edit_question(question_id, edited_question_info, new_submission_time):
#     '''
#     Edits the title and the message of the requested question.
#     '''
#     original_questions_data = con.get_all(question_file)
#     updated_questions_data = []
#     for question in original_questions_data:
#         if int(question['id']) == int(question_id):
#             question["title"] = edited_question_info['title']
#             question['message'] = edited_question_info['message']
#             question['submission_time'] = str(new_submission_time)
#             updated_questions_data.append(question)
#         else:
#             updated_questions_data.append(question)
#     con.write_data_to_file(updated_questions_data, question_file, questions_fieldnames)


# def delete_question(question_id):
#     '''
#     Deletes the requested question and its answers.
#     '''
#     original_questions_data = con.get_all(question_file)
#     updated_questions_data = []
#     for question in original_questions_data:
#         if int(question['id']) != int(question_id):
#             updated_questions_data.append(question)
#     con.write_data_to_file(updated_questions_data, question_file, questions_fieldnames)
#     original_answers = con.get_all(answer_file)
#     updated_answers = []
#     for answer in original_answers:
#         if int(answer['question_id']) != int(question_id):
#             updated_answers.append(answer)
#     con.write_data_to_file(updated_answers, answer_file, answer_fieldnames)

# UPVOTES = 0
# DOWNVOTES = 1

# def vote_question(question_id, vote):
#     '''
#     Adds 1 to the vote_number (x-y) key of a question (depending on the request).
#     '''
#     original_questions = con.get_all(question_file)
#     updated_questions = []
#     for question in original_questions:
#         if int(question['id']) == int(question_id):
#             votes = question['vote_number'].split('-')
#             if vote == "vote-up":
#                 votes[0] = str(int(votes[UPVOTES]) + 1)
#             elif vote == "vote-down":
#                 votes[1] = str(int(votes[DOWNVOTES]) + 1)
#             vote_number = "-".join(votes)
#             question['vote_number'] = vote_number
#             updated_questions.append(question)
#         else:
#             updated_questions.append(question)
#     con.write_data_to_file(updated_questions, question_file, questions_fieldnames)
    

# def vote_percentage(question_id):
#     '''
#     Calculates and returns the percantage voting for the requested question.
#     '''
#     question = get_question_by_id(question_id)
#     votes = question['vote_number'].split('-')
#     total_votes = int(votes[UPVOTES]) + int(votes[DOWNVOTES])
#     try:
#         up_votes_percentage = float(int(votes[UPVOTES]) / int(total_votes)) * 100
#     except ZeroDivisionError:
#         return "0"
#     return int(up_votes_percentage)


# # ANSWERS FUNCTIONS: find_answers_by_question_id, get_answer_by_id, vote_answer, delete_answer

# def find_answers_by_question_id(question_id):
#     '''
#     Searches the answer file and extracts the answers for a specific question_id.
#     '''
#     all_answers = con.get_all(answer_file)
#     answers_for_question = []
#     for answer in all_answers:
#         if int(answer['question_id']) == int(question_id):
#             answers_for_question.append(answer)
#     if len(answers_for_question) == 0: return None
#     else: return answers_for_question


# def get_answer_by_id(answer_id, question_id):
#     '''
#     Returns the answer that has the exact id as the requested one.
#     '''
#     answers = find_answers_by_question_id(question_id)
#     for answer in answers:
#         if int(answer['id']) == int(answer_id):
#             return answer

# def vote_percentage_answer(answer_id, question_id):
#     '''
#     Calculates and returns the percentage of a specific answer voting.
#     '''
#     answer = get_answer_by_id(answer_id, question_id)
#     votes = answer['vote_number'].split('-')
#     total_votes = int(votes[UPVOTES]) + int(votes[DOWNVOTES])
#     try:
#         up_votes_percentage = float(int(votes[UPVOTES]) / int(total_votes)) * 100
#     except ZeroDivisionError:
#         return "0"
#     return int(up_votes_percentage)



# def vote_answer(question_id, answer_id, vote):
#     '''
#     Adds 1 to the vote_number (x-y) key of a question (depending on the request).
#     '''
#     original_answers = con.get_all(answer_file)
#     updated_answers = []
#     for answer in original_answers:
#         if int(answer["id"]) == int(answer_id) and int(answer['question_id']) == int(question_id):
#             votes = answer['vote_number'].split('-')
#             if vote == "vote-up":
#                 votes[UPVOTES] = str(int(votes[UPVOTES]) + 1)
#             elif vote == "vote-down":
#                 votes[DOWNVOTES] = str(int(votes[DOWNVOTES]) + 1)
#             vote_number = "-".join(votes)
#             answer['vote_number'] = vote_number
#             updated_answers.append(answer)
#         else:
#             updated_answers.append(answer)
#     con.write_data_to_file(updated_answers, answer_file, answer_fieldnames)


# def delete_answer(answer_id):
#     '''
#     Deletes requested answer.
#     '''
#     original_answers = con.get_all(answer_file)
#     updated_answers = []
#     for answer in original_answers:
#         if int(answer['id']) != int(answer_id):
#             updated_answers.append(answer)
#     con.write_data_to_file(updated_answers, answer_file, answer_fieldnames)
