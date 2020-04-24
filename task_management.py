# file to be used for modifying the user's task list on this program
# and manage all communication with google tasks. #

from datetime import timedelta
import pickle
import settings_and_utility as util
import maya
import os.path

# constants
TASKS_FILE_PATH = "tasks.pkl"

# messages
NO_TASKS_MSG = "you have no saved tasks."

EXISTING_TASKS_MSG = "lets go over your existing tasks."

# questions

NEW_TASK_DURATION_Q = "how long will it take you to finish it (in minutes)?"

NEW_TASK_DUE_Q = "what is the due date?"

NEW_TASKS_TITLE_Q = "what is the title of the new task?"

NEW_TASK_Q = "would you like to add a new task?"

NEW_DURATION_Q = "what is the new duration in minutes? "

NEW_DATE_Q = "what is the new due date?"

NEW_NAME_Q = "what is the new name you would like to give it?"

CHANGE_NAME_Q = "would you like to give this task a different name?"

TASK_CHANGES_Q = "did anything about this task change since last time?"

DELET_TASK_WARNING_Q = "are you sure you want to delete this task?"

EDIT_DURATION_Q = "the current duration of this task is {duration} would you like to edit it?"

KEEP_TASK_Q = "would you like to keep the task: {task} ?"

EDIT_DUE_DATE_Q = "the current due date is {due} has it changes since last time?"


def get_user_tasks():
    """
    update existing tasks and / or get new tasks from the user.
    :return: a list of tasks sorted by due date. each task is a list of the form:
    [summary, due_date, duration, task_id].
    summary :type: string, the title of the task
    due_date :type: datetime object
    duration :type: timedelta object
    task_id :type: string, the id of the task in the google tasks app
    """
    if not os.path.exists(TASKS_FILE_PATH):
        tasks = []
    else:
        with open(TASKS_FILE_PATH, "rb") as tasks_file:
            tasks = pickle.load(tasks_file)

    tasks = manage_existing_tasks(tasks) + get_new_tasks()
    with open(TASKS_FILE_PATH, "wb") as tasks_file:
        pickle.dump(tasks, tasks_file)

    return sorted(tasks, key=lambda t: t[1])  # sort by due date


def manage_existing_tasks(existing_tasks):
    """
    for each task of the given tasks, checks if the user wants to modify or delete it.
    returns a new list with the updated tasks and updates google tasks list accordingly.
    :param existing_tasks: the tasks to manage
    :return: list with updated tasks.
    """
    updated_tasks = []
    if not len(existing_tasks):
        print(NO_TASKS_MSG)
        return []
    else:
        print(EXISTING_TASKS_MSG)
    for t in existing_tasks:
        [summary, due_time, duration, task_id] = t
        keep_task = util.get_boolean_answer(KEEP_TASK_Q.format(task=summary))
        if keep_task or not util.get_boolean_answer(DELET_TASK_WARNING_Q):
            if util.get_boolean_answer(TASK_CHANGES_Q):
                t = edit_task(t)
            updated_tasks.append(t)
        else:
            util.services['tasks'].tasks().delete(tasklist=util.task_list_id, task=task_id).execute()

    google_tasks_update(updated_tasks)
    return updated_tasks


def edit_task(task):
    """
    edits the different task components according to the user's preferences.
    :param task: the task to edit. list of the form: [summary, due_time, duration, task_id].
    summary - name of the task :type string
    due_time - due time of the task :type datetime object
    duration - duration of the task :type timedelta object
    task_id - id of the task in google calendar :type string
    :return: list of the form [summary, due_time, duration, task_id] with the new task components.
    """
    [summary, due_time, duration, task_id] = task
    if util.get_boolean_answer(CHANGE_NAME_Q):
        summary = input(NEW_NAME_Q)
    if util.get_boolean_answer(EDIT_DUE_DATE_Q.format(due=util.datetime_to_string(due_time))):
        due_time = maya.parse(input(NEW_DATE_Q)).datetime(to_timezone=util.TIME_ZONE,
                                                          naive=True)
        due_time = due_time.replace(hour=23, minute=59)
    if util.get_boolean_answer(EDIT_DURATION_Q.format(duration=duration)):
        duration = float(input(NEW_DURATION_Q))
    return [summary, due_time, duration, task_id]


def google_tasks_update(modified_tasks):
    """
    update the due date of the tasks given in google tasks.
    assumes they already exist in the tasks list.
    :param modified_tasks: tasks to modify
    """
    for t in modified_tasks:
        [summary, due_time, duration, task_id] = t
        g_task = util.services['tasks'].tasks().get(tasklist=util.task_list_id,
                                                    task=task_id).execute()
        g_task['due'] = util.datetime_to_string(due_time)
        g_task['summary'] = summary
        util.services['tasks'].tasks().update(tasklist=util.task_list_id,
                                      task=task_id, body=g_task).execute()


def get_new_tasks():
    """
    gets new tasks from the user and adds them to google tasks.
    :return: list with the new tasks
    """
    new_tasks = []
    while util.get_boolean_answer(NEW_TASK_Q):
        summary = input(NEW_TASKS_TITLE_Q)
        due_time = maya.parse(input(NEW_TASK_DUE_Q)).datetime(to_timezone=util.TIME_ZONE, naive=True)
        duration = timedelta(minutes=float(input(NEW_TASK_DURATION_Q)))
        task_id = create_task(summary, "", due_time)
        new_tasks.append([summary, due_time, duration, task_id])

    return new_tasks


def create_task(title, notes, due):
    """
    insert a new task into the task list (task_list_id).
    :param title: title of the task :type string
    :param notes: any notes that will be added needed for this task :type string
    :param due: when is this task due. :type: datetime object
    :return:
    """
    body = {
        'title': title,
        'notes': notes,
        'due': util.datetime_to_string(due)
    }
    new_t = util.services['tasks'].tasks().insert(tasklist=util.task_list_id, body=body).execute()
    return new_t['id']
