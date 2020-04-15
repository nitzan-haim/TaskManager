# file to be used in the first running of the program to set get credentials
# and preferences from the user. #

import pickle
import os.path
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
import settings_and_utility as util

# constants
SETUP_PKL_PATH = "initial_setup.pkl"
CALENDAR_CRED_PKL_PATH = "token.pkl"
TASKS_CRED_PKL_PATH = "token_tasks.pkl"


def initial_setup():
    """
    set the programs' settings on the first use.
    """
    print("first we will set your preferences.")
    initial_credentials_setup()
    set_services()
    util.write_calendar_id, util.reading_calendars_id = get_writing_reading_calendars()
    task_list = get_main_task_lst_id()
    with open(SETUP_PKL_PATH, "wb") as initial_setup_file:
        dump_dict = {"write calendar": util.write_calendar_id,
                     "reading calendars": util.reading_calendars_id,
                     "task list id": task_list}
        pickle.dump(dump_dict, initial_setup_file)
    print("great! we are done with the initial setup.")


def initial_credentials_setup():
    """
    get the credentials of the google calendar and google task and dump them into pickle.
    :return:
    """
    if not os.path.exists(CALENDAR_CRED_PKL_PATH):
        scopes = ['https://www.googleapis.com/auth/calendar']
        flow = InstalledAppFlow.from_client_secrets_file("client_secret.json",
                                                         scopes=scopes)
        credentials = flow.run_console()
        with open(CALENDAR_CRED_PKL_PATH, "wb") as token:
            pickle.dump(credentials, token)

    if not os.path.exists(TASKS_CRED_PKL_PATH):
        scopes = ['https://www.googleapis.com/auth/tasks']
        flow = InstalledAppFlow.from_client_secrets_file("credentials.json",
                                                         scopes=scopes)
        credentials = flow.run_console()
        with open(TASKS_CRED_PKL_PATH, "wb") as token_tasks:
            pickle.dump(credentials, token_tasks)


def get_writing_reading_calendars():
    """
    get the writing calendar id and reading calendars ids from the user.
    wither use existing ones or create a new writing calendar.
    :return:
     writing calendar id :type string
     reading calendars ids :type: list of strings.
    """
    print("now you will choose the calendar that this app will manage.")
    existing_calendars = util.services['calendar'].calendarList().list().execute()
    if util.get_boolean_answer("do you have a google calendar that is dedicated for study time planning?"):
        write_calendar = None
        reading_calendars = []
        while not write_calendar:
            for i in range(len(existing_calendars['items'])):
                cal_id = existing_calendars['items'][i]['id']
                name = existing_calendars['items'][i]['summary']

                if not write_calendar:  # choose the write calendar
                    if util.get_boolean_answer("would you like to set " + name +
                                               " to be the calendar that this app "
                                               "will manage?"):
                        write_calendar = cal_id

                else:   # write calendar already chosen
                    reading_calendars.append(cal_id)

            if not write_calendar:
                print("you did not answer positively for any calendar.")
    else:
        print("lets create a new calendar for that purpose.")
        summary = input("what whould you like to name this calendar?")
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
    print("now you will choose which task list you would like to manage using this app.")
    result = util.services['tasks'].tasklists().list().execute()
    if util.get_boolean_answer("do you wish to use an existing task list?"):
        main_task_lst_id = None

        while not main_task_lst_id:
            for taskList in result['items']:

                if main_task_lst_id:
                    break

                if util.get_boolean_answer("would you like to manage the " + taskList['title'] + " list?"):
                        main_task_lst_id = taskList['id']

            if not main_task_lst_id:
                print("you did not answer positively for any task list.")
    else:
        print("lets create a new task list then.")
        title = input("what would you like to call this list?")
        new_task_lst = {'title': title}
        main_task_lst_id = util.services['tasks'].tasklists().insert(body=new_task_lst).execute()['id']

    return main_task_lst_id


def set_services():
    """
    get the services for all needed api's.
    :return: a calendar with the app title and the service object as value.
    for example "calendar": service_calendar
    """
    with open(CALENDAR_CRED_PKL_PATH, "rb") as calender_creds:
        credentials_calendar = pickle.load(calender_creds)
        service_calendar = build("calendar", "v3", credentials=credentials_calendar)

    with open(TASKS_CRED_PKL_PATH, "rb") as tasks_creds:
        credentials_tasks = pickle.load(tasks_creds)
        service_tasks = build("tasks", "v1", credentials=credentials_tasks)

        util.services = {'calendar': service_calendar, 'tasks': service_tasks}