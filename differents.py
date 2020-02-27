   answers_for_question = dmg.get_answers_for_question(question_id)
       comments_for_question = dmg.get_comments_for_question(question_id)
           if comments_for_question is not None:
                comment_id = comments_for_question[0]['id']
            else:
                comment_id = None
            tags_for_question = dmg.get_tags_for_question(question_id)
            comments_for_answers = dmg.get_answers_for_question_comments(
                question_id)
            if answers_for_question == None:
                empty = True
            if empty == False:
                answers_for_question = utl.prepare_answers_for_hmtl(
                    answers_for_question, question_id)
                num_answers = len(answers_for_question)
            return render_template(WEB_PAGES["question_page"],
                                   question=question,
                                   answers=answers_for_question,
                                   empty=empty,
                                   question_id=question_id,
                                   num_answers=num_answers,
                                   comments_for_question=comments_for_question,
                                   comments_for_answers=comments_for_answers,
                                   comment_id=comment_id,
                                   tags_for_question=tags_for_question)
