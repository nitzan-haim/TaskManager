# main driver of the TaskManager program. #

from program_initial_setup import *
from task_management import *
from calendar_management import *


def main():
    """
    manage google tasks and google calendar according to user's pereferences.
    """
    print("welcome to your study time planner!")

    set_settings()
    all_tasks = get_user_tasks()
    start = get_start_time()

    # calendar management
    free_busy = get_next_free_busy()
    future_events = get_writing_calendar_next_events()
    plan_time_period(all_tasks, free_busy, start)
    delete_future_events(future_events)

    print("done planning all tasks! Bye!")


def get_start_time():
    """
    get the time from the user that they would like to start planning from.
    :return: start time, :type: datetime object
    """
    start_time = datetime.now()
    if not util.get_boolean_answer("start planning from now on? "):
        start_time = maya.parse(input("what date and time would"
                                      " you like to start planning "
                                      "from? ")).datetime(to_timezone=util.TIME_ZONE,
                                                          naive=True)

    print("please note that the planning will delete all the events in the "
          "study calendar from the time you specified and on.")

    if not util.get_boolean_answer("would you like to continue?"):
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
