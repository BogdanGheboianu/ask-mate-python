import database_common
import util as utl

# EXTRACT DATA FROM TABLES: questions, latest questions, questions for search, 
# answers, tags, comments, connection between questions and tags, next id from any table

@database_common.connection_handler
def get_questions(cursor, sort_factor, sort_order):
    if sort_order == 'ascending': cursor.execute(""" SELECT * FROM question ORDER BY {0} ASC; """.format(sort_factor))
    elif sort_order == 'descending': cursor.execute(""" SELECT * FROM question ORDER BY {0} DESC; """.format(sort_factor))
    questions = cursor.fetchall()
    if len(questions) == 0: return False
    else: return utl.rearrange_order_of_keys_for_questions(questions)


@database_common.connection_handler
def get_latest_questions(cursor, sort_factor, sort_order):
    if sort_order == 'ascending': cursor.execute("""SELECT * from question ORDER BY {0} ASC LIMIT 5;""".format(sort_factor))
    elif sort_order == 'descending': cursor.execute("""SELECT * FROM question ORDER BY {0} DESC LIMIT 5;""".format(sort_factor))
    questions = cursor.fetchall()
    if len(questions) == 0: return False
    else: return utl.rearrange_order_of_keys_for_questions(questions)


@database_common.connection_handler
def get_questions_for_search(cursor):
    cursor.execute(""" SELECT * FROM question ORDER BY vote_number DESC; """)
    questions = cursor.fetchall()
    return questions


@database_common.connection_handler
def get_answers(cursor):
    cursor.execute(""" SELECT * FROM answer ORDER BY submission_time DESC; """)
    answers = cursor.fetchall()
    return answers


@database_common.connection_handler
def get_tags(cursor):
    cursor.execute(""" SELECT * FROM tag; """)
    tags = cursor.fetchall()
    return tags


@database_common.connection_handler
def get_comments(cursor, limit):
    if limit == 'no-limit': cursor.execute(""" SELECT * FROM comment ORDER BY submission_time DESC; """)
    elif limit == 'limit': cursor.execute(""" SELECT * FROM comment ORDER BY submission_time DESC LIMIT 3; """)
    comments = cursor.fetchall()
    return comments


@database_common.connection_handler
def get_question_tags(cursor):
    cursor.execute(""" SELECT * FROM question_tag; """)
    question_tags = cursor.fetchall()
    return question_tags


@database_common.connection_handler
def get_next_id(cursor, table):
    cursor.execute(""" SELECT id FROM {0} ORDER BY id DESC LIMIT 1; """.format(table))
    next_id_tuple = cursor.fetchall()
    try: next_id = next_id_tuple[0]['id'] + 1
    except IndexError: next_id = 0
    return next_id


@database_common.connection_handler
def get_hashed_pass(cursor, username):
    cursor.execute(f""" SELECT password FROM user_info WHERE username='{username}'; """)
    try:
        password = cursor.fetchone()['password']
        return password
    except TypeError:
        return None


@database_common.connection_handler
def get_user(cursor, username):
    cursor.execute(f""" SELECT * FROM user_info WHERE username='{username}'; """)
    user = cursor.fetchone()
    return user


@database_common.connection_handler
def get_user_by_id(cursor, userid):
    cursor.execute(f""" SELECT * FROM user_info WHERE id={userid}; """)
    user = cursor.fetchone()
    return user


@database_common.connection_handler
def get_all_users(cursor):
    cursor.execute(""" SELECT * FROM user_info; """)
    users = cursor.fetchall()
    return users


@database_common.connection_handler
def get_user_votes(cursor, userid):
    cursor.execute(f""" SELECT * FROM user_vote WHERE userid={userid}; """)
    user_votes = cursor.fetchall()
    return user_votes


#=============================================================================================================================================

# ADDING DATA TO TABLES: question, answer, comm for question and for answer, tags for question

@database_common.connection_handler
def add_question(cursor, info):
    title = utl.escape_characters(info['title'])
    message = utl.escape_characters(info['message'])
    code_snippet = utl.escape_characters(info['code_snippet'])
    cursor.execute("""INSERT INTO question (id, submission_time, view_number, title, message, image, votes_up, votes_down, code_snippet, userid)
                    VALUES ({0}, '{1}', {2}, '{3}', '{4}', '{5}', {6}, {7}, '{8}', {9});
                    """.format(info['id'], info['submission_time'], info['view_number'],
                            title, message, info['image'], info['votes_up'], info['votes_down'], code_snippet, info['userid']))


@database_common.connection_handler
def add_answer(cursor, answer_info):
    message = utl.escape_characters(answer_info['message'])
    code_snippet = utl.escape_characters(answer_info['code_snippet'])
    cursor.execute(""" INSERT INTO answer (id, submission_time, question_id, message, image, votes_up, votes_down, code_snippet, userid)
                    VALUES ({0}, '{1}', {2}, '{3}', '{4}', {5}, {6}, '{7}', {8});
                    """.format(answer_info['id'], answer_info['submission_time'], answer_info['question_id'],
                               message, answer_info['image'], answer_info['votes_up'], answer_info['votes_down'], code_snippet, answer_info['userid']))



@database_common.connection_handler
def add_comment_for_question(cursor, comment_info):
    message = utl.escape_characters(comment_info['message'])
    cursor.execute(""" INSERT INTO comment (id, question_id, message, submission_time, userid) VALUES ({0}, {1}, '{2}', '{3}', {4});
                    """.format(comment_info['id'],
                                comment_info['question_id'],
                                message,
                                comment_info['submission_time'],
                                comment_info['userid']))


@database_common.connection_handler
def add_comment_for_answer(cursor, comment_info):
    message = utl.escape_characters(comment_info['message'])
    cursor.execute(""" INSERT INTO comment (id, answer_id, message, submission_time, userid) VALUES ({0}, {1}, '{2}', '{3}', {4});
                    """.format(comment_info['id'],
                                comment_info['answer_id'],
                                message,
                                comment_info['submission_time'],
                                comment_info['userid']))


@database_common.connection_handler
def add_tags_for_question(cursor, tags, question_id):
    ready_tags = []
    all_tags = get_tags()
    if tags['existing_tag'] != 'none': ready_tags.append(tags['existing_tag'])
    if tags['new_tags'] != '': 
        new_tags_list = tags['new_tags'].split(',')
        for tag in new_tags_list:
            clean_tag = tag.lstrip()
            if clean_tag != tags['existing_tag'] and clean_tag not in ready_tags: 
                ready_tags.append(clean_tag)    
    for tag in ready_tags:
        found = False
        for existing_tag in all_tags:
            if tag == existing_tag['name']:
                cursor.execute(""" INSERT INTO question_tag VALUES ({0}, {1}); """.format(question_id, existing_tag['id']))
                found = True
                break
        if not found:
            tag_id = get_next_id('tag')
            tag_name = utl.escape_characters(tag)
            cursor.execute(""" INSERT INTO tag VALUES({0}, '{1}'); """.format(tag_id, tag_name))
            cursor.execute(""" INSERT INTO question_tag VALUES ({0}, {1}); """.format(question_id, tag_id))


@database_common.connection_handler
def add_new_user(cursor, user):
    cursor.execute(f""" INSERT INTO user_info (username, email, password, created, role, rank)
                        VALUES ('{user['username']}', '{user['email']}', '{user['password']}', '{user['created']}', '{user['role']}', {user['rank']}); """)

#===============================================================================================================================================

# UPDATE DATA FROM TABLES: question, views for question, answer, votes for questions, votes for answers, comm for question, comm for answer

@database_common.connection_handler
def edit_question(cursor, question_id, edited_question_info, new_submission_time):
    title = utl.escape_characters(edited_question_info['title'])
    message = utl.escape_characters(edited_question_info['message'])
    code_snippet = edited_question_info['code_snippet']
    image = edited_question_info['image']
    cursor.execute(""" UPDATE question SET title='{0}', message='{1}', submission_time='{2}', code_snippet='{3}', image='{4}' where id={5};
                    """.format(title, message, new_submission_time, code_snippet, image, question_id))


@database_common.connection_handler
def add_view(cursor, question_id):
    questions = get_questions('id', 'ascending')
    for question in questions:
        if question['id'] == int(question_id): view_number = question['view_number']
    cursor.execute(""" UPDATE question set view_number={0} where id={1} """.format(view_number+1, question_id))



@database_common.connection_handler
def vote_question(cursor, question_id, vote_name):
    if vote_name == 'vote-up': cursor.execute(""" UPDATE question SET votes_up=votes_up + 1 WHERE id={0}; """.format(question_id))
    elif vote_name == 'vote-down': cursor.execute(""" UPDATE question SET votes_down=votes_down + 1 WHERE id={0}; """.format(question_id))
    cursor.execute(""" SELECT votes_up, votes_down FROM question WHERE id={0}; """.format(question_id))
    votes = cursor.fetchall()
    vote_percentage = utl.calculate_vote_percentage(votes[0]['votes_up'], votes[0]['votes_down'])
    cursor.execute(""" UPDATE question SET vote_number={0} WHERE id={1}; """.format(vote_percentage, question_id))


@database_common.connection_handler
def unvote_question(cursor, question_id, vote_name):
    if vote_name == 'vote-up': cursor.execute(""" UPDATE question SET votes_up=votes_up - 1 WHERE id={0}; """.format(question_id))
    elif vote_name == 'vote-down': cursor.execute(""" UPDATE question SET votes_down=votes_down - 1 WHERE id={0}; """.format(question_id))
    cursor.execute(""" SELECT votes_up, votes_down FROM question WHERE id={0}; """.format(question_id))
    votes = cursor.fetchall()
    vote_percentage = utl.calculate_vote_percentage(votes[0]['votes_up'], votes[0]['votes_down'])
    cursor.execute(""" UPDATE question SET vote_number={0} WHERE id={1}; """.format(vote_percentage, question_id))


@database_common.connection_handler
def user_vote_question(cursor, question_id, userid, vote_type):
    cursor.execute(f""" INSERT INTO user_vote (userid, questionid, vote_type)
                        VALUES ({userid}, {question_id}, '{vote_type}'); """)


@database_common.connection_handler
def user_unvote_question(cursor, question_id, userid):
    cursor.execute(f""" DELETE FROM user_vote WHERE userid={userid} AND questionid={question_id}; """)


@database_common.connection_handler
def edit_comment_for_question(cursor, new_comment_info):
    message = utl.escape_characters(new_comment_info['message'])
    cursor.execute(""" UPDATE comment SET message='{0}', submission_time='{1}' WHERE id={2}; 
                    """.format(message, new_comment_info['submission_time'], new_comment_info['id']))


@database_common.connection_handler
def edit_answer(cursor, answer_id, answer_new_info, new_submission_time):
    message = utl.escape_characters(answer_new_info['message'])
    cursor.execute(""" UPDATE answer SET message='{0}', submission_time='{1}', code_snippet='{2}', image='{3}' WHERE id={4};
                     """.format(message, new_submission_time, answer_new_info['code-snippet'], answer_new_info['image'], answer_id))


@database_common.connection_handler
def vote_answer(cursor, answer_id, vote_name):
    if vote_name == 'vote-up': cursor.execute(""" UPDATE answer SET votes_up=votes_up + 1 WHERE id={0}; """.format(answer_id))
    elif vote_name == 'vote-down': cursor.execute(""" UPDATE answer SET votes_down=votes_down + 1 WHERE id={0}; """.format(answer_id))
    cursor.execute(""" SELECT votes_up, votes_down FROM answer WHERE id={0}; """.format(answer_id))
    votes = cursor.fetchall()
    vote_percentage = utl.calculate_vote_percentage(votes[0]['votes_up'], votes[0]['votes_down'])
    cursor.execute(""" UPDATE answer SET vote_number={0}; """.format(vote_percentage))


@database_common.connection_handler
def unvote_answer(cursor, answer_id, vote_name):
    if vote_name == 'vote-up': cursor.execute(""" UPDATE answer SET votes_up=votes_up - 1 WHERE id={0}; """.format(answer_id))
    elif vote_name == 'vote-down': cursor.execute(""" UPDATE answer SET votes_down=votes_down - 1 WHERE id={0}; """.format(answer_id))
    cursor.execute(""" SELECT votes_up, votes_down FROM answer WHERE id={0}; """.format(answer_id))
    votes = cursor.fetchall()
    vote_percentage = utl.calculate_vote_percentage(votes[0]['votes_up'], votes[0]['votes_down'])
    cursor.execute(""" UPDATE answer SET vote_number={0}; """.format(vote_percentage))


@database_common.connection_handler
def user_vote_answer(cursor, answer_id, userid, vote_type):
    cursor.execute(f""" INSERT INTO user_vote (userid, answerid, vote_type)
                        VALUES ({userid}, {answer_id}, '{vote_type}'); """)


@database_common.connection_handler
def user_unvote_answer(cursor, answer_id, userid):
    cursor.execute(f""" DELETE FROM user_vote WHERE userid={userid} AND answerid={answer_id}; """)


@database_common.connection_handler
def edit_comment_for_answer(cursor, new_comment_info):
    message = utl.escape_characters(new_comment_info['message'])
    cursor.execute(""" UPDATE comment SET message='{0}', submission_time='{1}' WHERE id={2}; 
                    """.format(message, new_comment_info['submission_time'], new_comment_info['id']))

#=================================================================================================================================================

# DELETE DATA FROM TABLES: question, answer, comment, question tag

@database_common.connection_handler
def delete_question(cursor, question_id):
    answers = get_answers()
    answers_for_question_ids = []
    for answer in answers:
        if answer['question_id'] == int(question_id):
            answers_for_question_ids.append(answer['id'])
    for ans_id in answers_for_question_ids:
        cursor.execute("""  DELETE FROM comment WHERE answer_id={0}; """.format(ans_id))
    cursor.execute("""  DELETE FROM answer WHERE question_id={0}; """.format(question_id))
    cursor.execute("""  DELETE FROM comment WHERE question_id={0}; """.format(question_id))
    cursor.execute(""" DELETE FROM question_tag WHERE question_id={0}; """.format(question_id))
    cursor.execute(""" DELETE FROM question WHERE id={0}; """.format(question_id))


@database_common.connection_handler
def delete_answer(cursor, answer_id):
    cursor.execute(""" DELETE FROM comment WHERE answer_id={0}; """.format(answer_id))
    cursor.execute(""" DELETE FROM answer WHERE id={0};""".format(answer_id))


@database_common.connection_handler
def delete_comment(cursor, comment_id):
    cursor.execute("""SELECT question_id from comment WHERE id={0};""".format(comment_id))
    question_id = cursor.fetchone()['question_id']
    q_id = {'question_id': question_id}
    cursor.execute("""SELECT answer_id from comment WHERE id={0};""".format(comment_id))
    answer_id = cursor.fetchone()['answer_id']
    if question_id is not None:
        cursor.execute("""DELETE FROM comment WHERE id={0};""".format(comment_id))
        return q_id
    else:
        cursor.execute("""SELECT question_id from answer WHERE id={0};""".format(answer_id))
        question_id = cursor.fetchone()['question_id']
        q_a_id = {"question_id": question_id, "answer_id": answer_id}
        cursor.execute("""DELETE FROM comment WHERE id={0};""".format(comment_id))
        return q_a_id


@database_common.connection_handler
def delete_question_tag(cursor, question_id, tag_name):
    all_tags = get_tags()
    for tag in all_tags:
        if tag_name == tag['name']:
            tag_id_to_del = tag['id']
    cursor.execute(""" DELETE FROM question_tag WHERE question_id={0} AND tag_id={1}; """.format(question_id, tag_id_to_del))