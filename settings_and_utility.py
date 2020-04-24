# file to be shared with all program files. contains utility functions,
# globals and constants. #

from distutils.util import strtobool
from datetime import datetime, timedelta

# constants #
INVALID_ANSWER_MSG = "your answer is unclear."

TIME_FORMAT = "%Y-%m-%dT%H:%M:%S"
PLANNING_TIME_PERIOD = 10  # the time period in days that this program is planning for
MIN_WORK_TIME = 60  # the minimal time in minutes for a creation of an event
TIMEZONE_TIME_STAMP = "+03:00"
TIME_ZONE = 'Israel'
UTC_TIME_STAMP = 'Z'
MIN_WORK_DELTA = timedelta(minutes=45)

# global variables #

services = {}
write_calendar_id = ""
reading_calendars_id = []
task_list_id = ""


# utility funcs #

def get_boolean_answer(question):
    """
    ask the user for a boolean answer until their answer makes sense.
    :param question: the question to ask the user.
    :return: the answer of the user, :type boolean
    """
    answer_valid = False
    while not answer_valid:
        try:
            answer = strtobool(input(question))
            answer_valid = True
        except ValueError:
            print(INVALID_ANSWER_MSG)

    return answer


def datetime_to_string(datetime_obj):
    """
    converts datetime object and converts it to a string to be given to the
    calender api command.
    :param datetime_obj: obj to convert
    :return: string
    """
    return datetime_obj.strftime(TIME_FORMAT) + UTC_TIME_STAMP


def string_to_datetime(event_time):
    """
    convert string taken from the calendar's event, containing a timezone
     stamp, to a datetime object.
    :param event_time: string representing the time
    :return: datetime object
    """

    if TIMEZONE_TIME_STAMP in event_time:
        return datetime.strptime(event_time, TIME_FORMAT + TIMEZONE_TIME_STAMP)
    else:
        return datetime.strptime(event_time, TIME_FORMAT + UTC_TIME_STAMP)
