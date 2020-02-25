import database_common
from datetime import datetime
import util as utl


@database_common.connection_handler
def get_questions(cursor, sort_factor, sort_order):
    if sort_order == 'ascending':
        cursor.execute(""" SELECT * FROM question ORDER BY {0} ASC; """.format(sort_factor))
    elif sort_order == 'descending':
        cursor.execute(""" SELECT * FROM question ORDER BY {0} DESC; """.format(sort_factor))
    questions = cursor.fetchall()
    if len(questions) == 0: return False
    else: return questions


@database_common.connection_handler
def get_answers(cursor):
    cursor.execute(""" SELECT * FROM answer; """)
    answers = cursor.fetchall()
    return answers


@database_common.connection_handler
def get_tags(cursor):
    cursor.execute(""" SELECT * FROM tag; """)
    tags = cursor.fetchall()
    return tags


@database_common.connection_handler
def get_comments(cursor):
    cursor.execute(""" SELECT * FROM comment; """)
    comments = cursor.fetchall()
    return comments


@database_common.connection_handler
def get_question_tags(cursor):
    cursor.execute(""" SELECT * FROM question_tag; """)
    question_tags = cursor.fetchall()
    return question_tags


@database_common.connection_handler
def add_view(cursor, question_id):
    '''
    Adds +1 to the view_number key of the requested question whenever the question is accessed.
    '''
    questions = get_questions('id', 'ascending')
    for question in questions:
        if question['id'] == int(question_id):
            view_number = question['view_number']
    cursor.execute(""" UPDATE question set view_number={0} where id={1} """.format(view_number+1, question_id))


@database_common.connection_handler
def get_next_id(cursor, table):
    cursor.execute(""" SELECT id FROM {0} ORDER BY id DESC LIMIT 1; """.format(table))
    next_id_tuple = cursor.fetchall()
    next_id = next_id_tuple[0]['id'] + 1
    return next_id


@database_common.connection_handler
def add(cursor,info):
    '''
    Adds a new question
    '''
    next_id = get_next_id('question')
    cursor.execute("""
    INSERT INTO question
    (id, submission_time, view_number, vote_number, title, message, image)
    VALUES ({0}, '{1}', {2}, {3}, '{4}', '{5}', '{6}');
    """.format(next_id, info['submission_time'], info['view_number'],
               info['vote_number'], info['title'], info['message'], info['image']))





























# def get_all_and_sort(cursor, sort_factor, sort_order):
#     """
#     Returns list of dictionaries with all the questions(+properties, comments and answers(+properties, comments))
#     """
#     data = []
#     # Add questions: id, submission_time, view_number, vote_number, title, message, image
#     if sort_order == 'ascending':
#         cursor.execute(""" select * from question order by {0} asc; """.format(sort_factor))
#     elif sort_order == 'descending':
#         cursor.execute(""" select * from question order by {0} desc; """.format(sort_factor))
#     questions = cursor.fetchall()
#     for question in questions:
#         data.append({'id': question['id'], 
#                     'submission_time': question['submission_time'].strftime(f),
#                     'view_number': question['view_number'],
#                     'vote_number': utl.vote_percentage(question['vote_number']),
#                     'title': question['title'],
#                     'message': question['message'],
#                     'image': question['image']})
#     # Add question tags
#     cursor.execute(""" select * from tag; """)
#     tags = cursor.fetchall()
#     cursor.execute(""" select * from question_tag; """)
#     question_tags = cursor.fetchall()
#     for question_tag in question_tags:
#         tags_to_add = []
#         for question in data:
#             if question['id'] == question_tag['question_id']:
#                 for tag in tags:
#                     if tag['id'] == question_tag['tag_id']:
#                         tags_to_add.append((tag['id'], tag['name']))
#                 question.update({'tags': tags_to_add})
#     # Add question comments
#     cursor.execute(""" select * from comment; """)
#     comments = cursor.fetchall()
#     for question in data:
#         comments_to_add = []
#         for comment in comments:
#             if comment['question_id'] != None and comment['question_id'] == question['id']:
#                 comments_to_add.append({'id': comment['id'],
#                                             'question_id': comment['question_id'],
#                                             'message': comment['message'],
#                                             'submission_time': comment['submission_time'].strftime(f),
#                                             'edited_count': comment['edited_count']})
#         question.update({'comments': comments_to_add})
#     # Add answers
#     cursor.execute(""" select * from answer; """)
#     answers = cursor.fetchall()
#     all_answers = []
#     for answer in answers:
#         comments_to_add = []
#         for comment in comments:
#             if comment['answer_id'] != None and comment['answer_id'] == answer['id']:
#                 comments_to_add.append({'id': comment['id'],
#                                             'answer_id': comment['answer_id'],
#                                             'message': comment['message'],
#                                             'submission_time': comment['submission_time'].strftime(f),
#                                             'edited_count': comment['edited_count']})
#         answer_to_add = {
#             'id': answer['id'],
#             'question_id': answer['question_id'],
#             'message': answer['message'],
#             'submission_time': answer['submission_time'].strftime(f),
#             'vote_number': utl.vote_percentage(answer['vote_number']),
#             'image': answer['image'],
#             'comments': comments_to_add
#         }
#         all_answers.append(answer_to_add)
#     for question in data:
#         answers_to_add = []
#         for answer in all_answers:
#             if question['id'] == answer['question_id']:
#                 answers_to_add.append(answer)
#         question.update({'answers': answers_to_add})

#     if len(data) == 0: return False
#     else: return data

# print(get_all_and_sort('id', 'ascending'))