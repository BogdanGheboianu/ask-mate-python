from csv import DictReader, DictWriter


def write_data_to_file(data, data_file, fieldnames):
    '''
    Removes data from the requested file and writes the new recieved list of dicts.
    '''
    with open(data_file, "w") as file:
        writer = DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        for question in data:
            writer.writerow(question)
        file.close()


def get_all(data_file):
    '''
    Reads the requested data file (answers, questions) and extracts the info.
    Returns a list of dicts with all the questions/answers or returns False if there are none.
    '''
    elements = []
    with open(data_file, "r") as file:
        for dictionary in DictReader(file):
            elements.append(dictionary)
        file.close()
    if len(elements) == 0: return False
    else: return elements


def find_next_index(data_file):
    '''
    Finds the biggest count index in a file.
    Return that count index + one to be used for the input data to come.
    '''
    return max([int(story['id']) for story in get_all(data_file)]) + 1
