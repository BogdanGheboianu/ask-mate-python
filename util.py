import uuid
from datetime import datetime

def convert_unix_time_to_readable_format(list_of_dicts):
    '''
    Converts and returns the given unix time to a readable format: date and time
    '''
    try:
        for _dict in list_of_dicts:
            _dict['submission_time'] = datetime.utcfromtimestamp(int(_dict['submission_time'])).strftime('%Y-%m-%d %H:%M:%S')
        return list_of_dicts
    except TypeError:
        return None


def transform_image_title(filename):
    '''
    Converts an image name to an uuid4 id and returns it.
    '''
    filename_splited = filename.split(".")
    filename_splited[0] = str(uuid.uuid4())
    unique_filename = ".".join(filename_splited)
    return unique_filename


def allowed_file(filename):
    '''
    Verifies if the uploaded file has a valid file extension.
    '''
    ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}  
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS