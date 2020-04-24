# main driver of the TaskManager program. #

from program_initial_setup import *
from task_management import *
from calendar_management import *

# messages
WELCOME_MSG = "welcome to your study time planner!"

BYE_MSG = "done planning all tasks! Bye!"

# questions
WARNING_q = "please note that the planning will delete all the events in the " \
              "study calendar from the time you specified and on." \
            " \nwould you like to continue?"

PLAN_FROM_NOW_Q = "start planning from now on? "

START_TIME_Q = "what date and time would you like to start planning from? "


def main():
    """
    manage google tasks and google calendar according to user's pereferences.
    """
    print(WELCOME_MSG)

    set_settings()
    all_tasks = get_user_tasks()
    start = get_start_time()

    # calendar management
    free_busy = get_next_free_busy()
    future_events = get_writing_calendar_next_events()
    plan_time_period(all_tasks, free_busy, start)
    delete_future_events(future_events)

    print(BYE_MSG)


def get_start_time():
    """
    get the time from the user that they would like to start planning from.
    :return: start time, :type: datetime object
    """
    start_time = datetime.now()
    if not util.get_boolean_answer(PLAN_FROM_NOW_Q):
        start_time = maya.parse(input(START_TIME_Q)).datetime(to_timezone=util.TIME_ZONE,
                                                              naive=True)

    if not util.get_boolean_answer(WARNING_q):
        exit()

    return start_time


def set_settings():
    """
    set the current settings from previous running of the program or create new
     one.
    """
    if not os.path.exists(SETUP_PKL_PATH):
        initial_setup()
    else:
        set_services()

    with open(SETUP_PKL_PATH, "rb") as setup_file:
        setup_d = pickle.load(setup_file)

    util.write_calendar_id = setup_d["write calendar"]
    util.reading_calendars_id = setup_d["reading calendars"]
    util.task_list_id = setup_d["task list id"]


if __name__ == '__main__':
    main()
