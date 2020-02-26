import database_common
import datetime
import util as utl
f = '%Y-%m-%d %H:%M:%S'


@database_common.connection_handler
def get_questions(cursor, sort_factor, sort_order):
    if sort_order == 'ascending':
        cursor.execute(
            """ SELECT * FROM question ORDER BY {0} ASC; """.format(sort_factor))
    elif sort_order == 'descending':
        cursor.execute(
            """ SELECT * FROM question ORDER BY {0} DESC; """.format(sort_factor))
    questions = cursor.fetchall()
    if len(questions) == 0:
        return False
    else:
        return questions


@database_common.connection_handler
def display_latest_questions(cursor, sort_factor, sort_order):
    if sort_order == 'ascending':
        cursor.execute("""
        SELECT * from question ORDER BY {0} ASC LIMIT 5;""".format(sort_factor))
    elif sort_order == 'descending':
        cursor.execute(
            """SELECT * FROM question ORDER BY {0} DESC LIMIT 5;""".format(sort_factor))
    questions = cursor.fetchall()
    if len(questions) == 0:
        return False
    else:
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
def get_comments(cursor):
    cursor.execute(""" SELECT * FROM comment ORDER BY submission_time DESC; """)
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
    cursor.execute(""" UPDATE question set view_number={0} where id={1} """.format(
        view_number+1, question_id))


@database_common.connection_handler
def get_next_id(cursor, table):
    cursor.execute(
        """ SELECT id FROM {0} ORDER BY id DESC LIMIT 1; """.format(table))
    next_id_tuple = cursor.fetchall()
    try:
        next_id = next_id_tuple[0]['id'] + 1
    except IndexError:
        next_id = 0
    return next_id


@database_common.connection_handler
def add_answer(cursor, answer_info):
    cursor.execute(""" INSERT INTO answer VALUES ({0}, '{1}', {2}, {3}, '{4}', '{5}');
                    """.format(answer_info['id'], answer_info['submission_time'], answer_info['vote_number'], answer_info['question_id'],
                               answer_info['message'], answer_info['image']))
    with open('sample_data/answer_votes.csv', "a") as file:
        data = '{0}??0-0'.format(answer_info['id'])
        file.write('{0}\n'.format(data))
        file.close


@database_common.connection_handler
def add_question(cursor, info):
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
    with open('sample_data/question_votes.csv', "a") as file:
        data = '{0}??0-0'.format(next_id)
        file.write('{0}\n'.format(data))
        file.close


@database_common.connection_handler
def vote_answer(cursor, answer_id, vote_name):
    with open('sample_data/answer_votes.csv', "r") as file:
        content = file.readlines()
        file.close()
    votes = [vote.replace("\n", '') for vote in content]
    updated_content = []
    for vote in votes:
        vote_updated = ''
        vote_list = vote.split('??')
        if int(vote_list[0]) == int(answer_id):
            up_down_votes = vote_list[1].split('-')
            if vote_name == 'vote-up':
                up_down_votes[0] = str(int(up_down_votes[0]) + 1)
            elif vote_name == 'vote-down':
                up_down_votes[1] = str(int(up_down_votes[1]) + 1)
            up_down_votes = '-'.join(up_down_votes)
            transform_vote_to_percentage_and_update_answer(
                answer_id, up_down_votes)
            vote_list[1] = up_down_votes
            vote_updated = '??'.join(vote_list)
            updated_content.append(vote_updated)
        else:
            updated_content.append(vote)
    with open('sample_data/answer_votes.csv', 'w') as file:
        for vote in updated_content:
            file.write('{0}\n'.format(vote))
        file.close()


UPVOTES = 0
DOWNVOTES = 1
@database_common.connection_handler
def transform_vote_to_percentage_and_update_answer(cursor, answer_id, up_down_votes):
    votes = up_down_votes.split('-')
    total_votes = int(votes[UPVOTES]) + int(votes[DOWNVOTES])
    try:
        up_votes_percentage = float(
            int(votes[UPVOTES]) / int(total_votes)) * 100
    except ZeroDivisionError:
        up_votes_percentage = 0
    cursor.execute(""" UPDATE answer SET vote_number={0} where id={1}; """.format(
        int(up_votes_percentage), answer_id))


@database_common.connection_handler
def vote_question(cursor, question_id, vote_name):
    with open('sample_data/question_votes.csv', "r") as file:
        content = file.readlines()
        file.close()
    votes = [vote.replace("\n", '') for vote in content]
    updated_content = []
    for vote in votes:
        vote_updated = ''
        vote_list = vote.split('??')
        if int(vote_list[0]) == int(question_id):
            up_down_votes = vote_list[1].split('-')
            if vote_name == 'vote-up':
                up_down_votes[0] = str(int(up_down_votes[0]) + 1)
            elif vote_name == 'vote-down':
                up_down_votes[1] = str(int(up_down_votes[1]) + 1)
            up_down_votes = '-'.join(up_down_votes)
            transform_vote_to_percentage_and_update_question(
                question_id, up_down_votes)
            vote_list[1] = up_down_votes
            vote_updated = '??'.join(vote_list)
            updated_content.append(vote_updated)
        else:
            updated_content.append(vote)
    with open('sample_data/question_votes.csv', 'w') as file:
        for vote in updated_content:
            file.write('{0}\n'.format(vote))
        file.close()


UPVOTES = 0
DOWNVOTES = 1
@database_common.connection_handler
def transform_vote_to_percentage_and_update_question(cursor, question_id, up_down_votes):
    votes = up_down_votes.split('-')
    total_votes = int(votes[UPVOTES]) + int(votes[DOWNVOTES])
    try:
        up_votes_percentage = float(
            int(votes[UPVOTES]) / int(total_votes)) * 100
    except ZeroDivisionError:
        up_votes_percentage = 0
    cursor.execute(""" UPDATE question SET vote_number={0} where id={1}; """.format(
        int(up_votes_percentage), question_id))


@database_common.connection_handler
def edit_question(cursor, question_id, edited_question_info, new_submission_time):
    cursor.execute(""" UPDATE question SET title='{0}', message='{1}', submission_time='{2}' where id={3}; 
                    """.format(edited_question_info['title'], edited_question_info['message'],
                               new_submission_time, question_id))


@database_common.connection_handler
def delete_question(cursor, question_id):
    answers = get_answers()
    answers_for_question_ids = []
    for answer in answers:
        if answer['question_id'] == int(question_id):
            answers_for_question_ids.append(answer['id'])
    for ans_id in answers_for_question_ids:
        cursor.execute(
            """  DELETE FROM comment WHERE id={0}; """.format(ans_id))

    cursor.execute(
        """  DELETE FROM answer WHERE question_id={0}; """.format(question_id))
    cursor.execute(
        """  DELETE FROM comment WHERE question_id={0}; """.format(question_id))
    cursor.execute(
        """ DELETE FROM question_tag WHERE question_id={0}; """.format(question_id))
    cursor.execute(
        """ DELETE FROM question WHERE id={0}; """.format(question_id))
    with open('sample_data/question_votes.csv', 'r') as file:
        content = file.readlines()
        file.close()
    new_data = []
    for item in content:
        item_list = item.split('??')
        if int(item_list[0]) != int(question_id):
            new_data.append(item)
    with open('sample_data/question_votes.csv', 'w') as file:
        for item in new_data:
            file.write(item)
        file.close()


@database_common.connection_handler
def delete_answer(cursor, answer_id):
    cursor.execute(
        """ DELETE FROM comment WHERE answer_id={0}; """.format(answer_id))
    cursor.execute(""" DELETE FROM answer WHERE id={0};""".format(answer_id))

    with open('sample_data/answer_votes.csv', 'r') as file:
        content = file.readlines()
        file.close()
    new_data = []
    for item in content:
        item_list = item.split('??')
        print(item_list)
        if int(item_list[0]) != int(answer_id):
            new_data.append(item)
    with open('sample_data/answer_votes.csv', 'w') as file:
        for item in new_data:
            file.write(item)
        file.close()


@database_common.connection_handler
def add_comment_for_question(cursor, comment_info):
    cursor.execute(""" INSERT INTO comment (id, question_id, message, submission_time)
                        VALUES ({0}, {1}, '{2}', '{3}'); 
                    """.format(
        comment_info['id'],
        comment_info['question_id'],
        comment_info['message'],
        comment_info['submission_time']
    ))


@database_common.connection_handler
def add_comment_for_answer(cursor, comment_info):
    cursor.execute(""" INSERT INTO comment (id, answer_id, message, submission_time)
                        VALUES ({0}, {1}, '{2}', '{3}'); 
                    """.format(
                        comment_info['id'],
                        comment_info['answer_id'],
                        comment_info['message'],
                        comment_info['submission_time']
                    ))


@database_common.connection_handler
def edit_answer(cursor, answer_new_info):
    cursor.execute(""" UPDATE answer SET message='{0}', submission_time='{1}' WHERE id={2};
                     """.format(answer_new_info['message'], answer_new_info['submission_time'], answer_new_info['id']))


@database_common.connection_handler
def edit_comment_for_question(cursor, new_comment_info):
    cursor.execute(""" UPDATE comment SET message='{0}', submission_time='{1}' WHERE id={2}; 
                    """.format(new_comment_info['message'], new_comment_info['submission_time'], new_comment_info['id']))


@database_common.connection_handler
def edit_comment_for_answer(cursor, new_comment_info):
    cursor.execute(""" UPDATE comment SET message='{0}', submission_time='{1}' WHERE id={2}; 
                    """.format(new_comment_info['message'], new_comment_info['submission_time'], new_comment_info['id']))


@database_common.connection_handler
def get_questions_for_search(cursor):
    cursor.execute(""" SELECT * FROM question ORDER BY vote_number  DESC; """)
    questions = cursor.fetchall()
    return questions
