# file to be used in the first running of the program to set get credentials
# and preferences from the user. #

import pickle
import os.path
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
import settings_and_utility as util

# constants
SET_PREFERENCES_MSG = "first we will set your preferences."
CLIENT_SECRET_JSON = "client_secret.json"
TASKS_SCOPE = 'https://www.googleapis.com/auth/tasks'
CALENDAR_SCOPE = 'https://www.googleapis.com/auth/calendar'
SETUP_PKL_PATH = "initial_setup.pkl"
CRED_PKL_PATH = "token.pkl"

# messages
CHOOSE_TASKLIST_MSG = "now you will choose which task list you would like to manage using this app."
CREATE_NEW_CALENDAT_MSG = "lets create a new calendar for that purpose."
ANSWER_INVALID_MSG = "you did not answer positively for any option."
DONE_INITIAL_SETUP_MSG = "great! we are done with the initial setup."
CHOOSE_CALENDAT_MSG = "now you will choose the calendar that this app will manage."
CREATE_NEW_TASKLST_MSG = "lets create a new task list then."

# questions
NEW_CALENDAR_NAME_Q = "what whould you like to name this calendar?"
EXISTING_CALENDAR_Q = "do you have a google calendar that is dedicated for study time planning?"
NEW_TASKLST_NAME_Q = "what would you like to call this list?"
USE_EXISTING_TASKLST_Q = "do you wish to use an existing task list?"
MANAGE_THIS_LST_Q = "would you like to manage the {list_title} list?"
MANAGE_THIS_CALENDAR_Q = "would you like to set {calendar_name}to be the calendar that this app will manage?"


def initial_setup():
    """
    set the programs' settings on the first use.
    """
    print(SET_PREFERENCES_MSG)
    initial_credentials_setup()
    set_services()
    util.write_calendar_id, util.reading_calendars_id = get_writing_reading_calendars()
    task_list = get_main_task_lst_id()
    with open(SETUP_PKL_PATH, "wb") as initial_setup_file:
        dump_dict = {"write calendar": util.write_calendar_id,
                     "reading calendars": util.reading_calendars_id,
                     "task list id": task_list}
        pickle.dump(dump_dict, initial_setup_file)
    print(DONE_INITIAL_SETUP_MSG)


def initial_credentials_setup():
    """
    get the credentials of the google calendar and google task and dump them into pickle.
    """
# changes
    if not os.path.exists(CRED_PKL_PATH):
        scopes = [CALENDAR_SCOPE, TASKS_SCOPE]
        flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRET_JSON,
                                                         scopes=scopes)
        credentials = flow.run_console()
        with open(CRED_PKL_PATH, "wb") as token:
            pickle.dump(credentials, token)


def get_writing_reading_calendars():
    """
    get the writing calendar id and reading calendars ids from the user.
    wither use existing ones or create a new writing calendar.
    :return:
     writing calendar id :type string
     reading calendars ids :type: list of strings.
    """
    print(CHOOSE_CALENDAT_MSG)
    existing_calendars = util.services['calendar'].calendarList().list().execute()
    if util.get_boolean_answer(EXISTING_CALENDAR_Q):
        write_calendar = None
        reading_calendars = []
        while not write_calendar:
            for i in range(len(existing_calendars['items'])):
                cal_id = existing_calendars['items'][i]['id']
                name = existing_calendars['items'][i]['summary']

                if not write_calendar:  # choose the write calendar
                    if util.get_boolean_answer(MANAGE_THIS_CALENDAR_Q.format(calendar_name=name)):
                        write_calendar = cal_id

                else:   # write calendar already chosen
                    reading_calendars.append(cal_id)

            if not write_calendar:
                print(ANSWER_INVALID_MSG)
    else:
        print(CREATE_NEW_CALENDAT_MSG)
        summary = input(NEW_CALENDAR_NAME_Q)
        new_calendar = {
            'summary': summary,
            'timeZone': util.TIME_ZONE
        }
        write_calendar = util.services['calendar'].calendars().insert(body=new_calendar).execute()['id']
        reading_calendars = [existing_calendars['items'][i]['id']
                             for i in range(len(existing_calendars['items']))]

    return write_calendar, reading_calendars


def get_main_task_lst_id():
    """
    get the task list id. wither use an existing one or create a new one.
    :return:
    """
    print(CHOOSE_TASKLIST_MSG)
    result = util.services['tasks'].tasklists().list().execute()
    if util.get_boolean_answer(USE_EXISTING_TASKLST_Q):
        main_task_lst_id = None

        while not main_task_lst_id:
            for taskList in result['items']:

                if main_task_lst_id:
                    break
                if util.get_boolean_answer(MANAGE_THIS_LST_Q.format(list_title=taskList['title'])):
                        main_task_lst_id = taskList['id']

            if not main_task_lst_id:
                print(ANSWER_INVALID_MSG)
    else:
        print(CREATE_NEW_TASKLST_MSG)
        title = input(NEW_TASKLST_NAME_Q)
        new_task_lst = {'title': title}
        main_task_lst_id = util.services['tasks'].tasklists().insert(body=new_task_lst).execute()['id']

    return main_task_lst_id


def set_services():
    """
    get the services for all needed api's.
    :return: a calendar with the app title and the service object as value.
    for example "calendar": service_calendar
    """
    # changes
    with open(CRED_PKL_PATH, "rb") as creds:
        credentials = pickle.load(creds)
        service_calendar = build("calendar", "v3", credentials=credentials)
        service_tasks = build("tasks", "v1", credentials=credentials)
        util.services = {'calendar': service_calendar, 'tasks': service_tasks}

