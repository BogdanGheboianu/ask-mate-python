from csv import DictReader, DictWriter

answer_file = "sample_data/answer.csv"
question_file = "sample_data/question.csv"


def write_data_to_file(data):
    with open(question_file, "w") as file:
        fieldnames = ["id", "submission_time", "view_number", "vote_number", "title", "message", "image"]
        writer = DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        for question in data:
            writer.writerow(question)
        file.close()