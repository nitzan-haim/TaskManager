from googleapiclient.discovery import build
import httplib2
from google_auth_oauthlib.flow import InstalledAppFlow
import pickle
from datetime import datetime, timedelta, time
import datefinder
import maya
from distutils.util import strtobool

##### constants #####
TIME_FORMAT = "%Y-%m-%dT%H:%M:%S"
calendars_for_reading = ['nitzanhaim@gmail.com', 'School Schedule']
PLANNING_TIME_PERIOD = 10  # the time period in days that this program is planning for
MIN_WORK_TIME = 60  # the minimal time in minutes for a creation of an event
TIMEZONE_TIME_STAMP = "+03:00"
UTC_TIME_STAMP = 'Z'
MIN_WORK_DELTA = timedelta(minutes=45)
####################


################ not in use at the moment ##################

# def schedule_week(tasks, events):
#     i = 0  # events idx
#     j = 0  # tasks idx
#     cur_time = datetime.now()
#     period_end = cur_time + timedelta(days=PLANNING_TIME_PERIOD)
#     done_with_cur_event = True
#     while cur_time < period_end:
#
#         # define the available time delta
#         if i < len(events):
#             event_start_time = event_time_to_datetime(events[i]['start']['dateTime'])
#             event_end_time = event_time_to_datetime(events[i]['end']['dateTime'])
#             print("event start time: ", event_start_time)
#             print("cur time: ", cur_time)
#             print("event end time: ", event_end_time)
#             if event_start_time < cur_time < event_end_time:
#                 cur_time = event_end_time
#                 i += 1
#                 continue
#
#             available_delta = event_start_time - cur_time
#         else:
#             available_delta = period_end - cur_time
#
#         # check whether delta is long enough for an event
#         if available_delta.seconds/60 < MIN_WORK_TIME:
#             if i < len(events):
#                 cur_time = event_time_to_datetime(events[i]['start']['dateTime'])
#             else:
#                 cur_time = period_end
#             continue
#         else:
#             [summary, due_date, wanted_duration] = tasks[j]
#             duration = available_delta
#
#             # if there is at least 30 mins time left
#             if wanted_duration - available_delta > timedelta(minutes=30):
#                 duration = wanted_duration
#                 done_with_cur_event = False
#
#             create_event(summary, cur_time.day, cur_time.hour, cur_time.minute, duration=int(duration.seconds/60))
#
#             # update task
#             if wanted_duration - duration <= timedelta():  # finished task
#                 if j + 1 == len(tasks):  # done inserting all tasks
#                     break
#                 else:
#                     j += 1
#             else:  # change the wanted duration of the task to be what is left
#                 tasks[j][2] = wanted_duration - duration
#
#         if i < len(events):
#             cur_time = event_time_to_datetime(events[i]['end']['dateTime'])
#         else:
#             cur_time += duration
#
#         if done_with_cur_event:
#             i += 1
#             done_with_cur_event = True
#


def get_next_events():
    now = datetime.now()
    time_min = datetime(now.year, now.month, now.day, 0, 0, 0)  # start reading from the beginning of today
    time_max = time_min + timedelta(days=PLANNING_TIME_PERIOD)

    events = []
    for i in range(len(calendars['items'])):
        if calendars['items'][i]['summary'] in calendars_for_reading:
            calendar_id = calendars['items'][i]['id']
            calender_events = service.events().list(calendarId=calendar_id,
                                                    maxResults=1000,
                                                    singleEvents=True,
                                                    timeMin=datetime_to_string(time_min),
                                                    timeMax=datetime_to_string(time_max)).execute()

            # keep only the events that have specific hours (leave out whole-day events):
            for e in calender_events['items']:
                if 'dateTime' in e['start']:
                    events.append(e)

    return sorted(events, key=lambda eve: eve['start']['dateTime']) # sort the events by the start time

#################################

#################### utility functions ###################################

def datetime_to_string(datetime_obj):
    """
    converts datetime object and converts it to a string to be given to the
    calender api command.
    :param datetime_obj: obj to convert
    :return: string
    """
    return datetime_obj.strftime(TIME_FORMAT)+UTC_TIME_STAMP


def string_to_datetime(event_time):
    """
    convert string taken from the calendar's event, containing a timezone
     stamp, to a datetime object.
    :param event_time: string representing the time
    :return: datetime object
    """

    if TIMEZONE_TIME_STAMP in event_time:
        return datetime.strptime(event_time, TIME_FORMAT+TIMEZONE_TIME_STAMP)
    else:
        return datetime.strptime(event_time, TIME_FORMAT+UTC_TIME_STAMP)


def create_event(summary, day, hour, minutes, sec=0, duration=timedelta(minutes=60),
                 month=datetime.today().month, year=datetime.today().year):

    """
    create an event in the writing calendar with the given characteristic.
    :param summary:
    :param day:
    :param hour:
    :param minutes:
    :param sec:
    :param duration: duration of activity, :type: timedelta object
    :param month:
    :param year:
    :return:
    """
    start_time = datetime(year, month, day, hour, minutes, sec)
    end_time = start_time + duration
    time_zone = 'Israel'

    event = {
      'summary': summary,
      'start': {
        'dateTime': start_time.strftime(TIME_FORMAT),
        'timeZone': time_zone,
      },
      'end': {
        'dateTime': end_time.strftime("%Y-%m-%dT%H:%M:%S"),
        'timeZone': time_zone,
      },

      'reminders': {
        'useDefault': False,
        'overrides': [
          {'method': 'email', 'minutes': 60},
          {'method': 'popup', 'minutes': 30},
        ],
      },
    }

    service.events().insert(calendarId=write_calendar_id, body=event).execute()

##################################################################

################# main functions ############################

def get_tasks():
    """
    gets the tasks from the user.
    :return: list containing lists of length 3, each inner list represents a task.

    the inner lists are of the form: [summary, due_date, duration].
    summary :type: string
    due_date :type: datetime object
    duration :type: timedelta object

    the output is ordered by due-date.
    """
    print("to stop entering tasks type 'q' as the task title")
    tasks = []
    summary = input("task title: ")

    while summary != 'q':
        duration = timedelta(minutes=float(input("how long will this task take to complete in minutes? ")))

        # get task due date
        matches = list(datefinder.find_dates(input("what is the due date of this task?")))
        while not len(matches) or matches[0] <= datetime.now():
            print("ERROR: due date invalid. make sure the date is stated clearly and is in the future.")
            matches = list(datefinder.find_dates(input("what is the due date of this task?")))
        due_date = matches[0]

        tasks.append([summary, due_date, duration])

        summary = input("task title: ")

    return sorted(tasks, key=lambda t: t[1])

# TODO: sort the tasks by due date and then by priority


def get_next_free_busy():
    """
    get busy information for reading calendars for the next time period.
    :return: list of busy times sorted by the start time.
     each element is of the form: {'start': X, 'end': Y}.
    X and Y :type: datetime
    """

    now = datetime.now()
    time_min = datetime(now.year, now.month, now.day, 0, 0, 0)  # start reading from the beginning of today
    time_max = datetime(now.year, now.month, now.day + PLANNING_TIME_PERIOD+1, 0, 0, 0)

    body = {
        "timeMin": time_min.strftime(TIME_FORMAT + '+03:00'),
        "timeMax": time_max.strftime(TIME_FORMAT + '+03:00'),
        "timeZone": "Israel",
        "items": [{"id": cal_id} for cal_id in reading_calendars_id]
    }
    events_result = service.freebusy().query(body=body).execute()
    cal_dict = events_result['calendars']
    return process_busy_info(cal_dict)


def process_busy_info(cal_dict):
    """
    process the busy information to represent the busy times neatly.
    1. convert values from strings to datetime objects
    2. sort by start time
    3. combine overlapping and adjacent busy times. two events are considered
     adjacent if the time between them is less than 45 minutes.

    :param cal_dict: dictionary of the form {calendar_id: {'busy':[{'start': X, 'end': Y}...]}}
    where X and Y are :type string.
    :return: list of busy times sorted by the start time.
     each element is of the form: {'start': X, 'end': Y}.
    X and Y :type: datetime
    """

    times_not_combined = []
    now = datetime.now()
    for calendar_id in cal_dict:
        busy_times = cal_dict[calendar_id]['busy']
        for b_t in busy_times:
            if now > string_to_datetime(b_t['end']):  # skip past events
                continue
            times_not_combined.append({'start': string_to_datetime(b_t['start']),
                                       'end': string_to_datetime(b_t['end'])})

    times_not_combined.sort(key=lambda elem: elem['start'])

    result = []
    # combine busy times
    i = 0
    n = len(times_not_combined)
    while i < n-1:
        s1 = times_not_combined[i]['start']
        e1 = times_not_combined[i]['end']
        s2 = times_not_combined[i+1]['start']
        e2 = times_not_combined[i+1]['end']
        if e1 <= s2 and s2-e1 >= MIN_WORK_DELTA:
            # no overlap between busy times i and i+1 and there is a long
            # enough break between them
            result.append(times_not_combined[i])
        else:
            # either there is overlap or the break between them is not long
            # enough
            result.append({'start': min(s1, s2), 'end': max(e1, e2)})
            i += 1  # skip the next busy time

        i += 1

    return result


def get_writing_calendar_next_events():
    """
    get all the events in the writing calendar for the next PLANNING_TIME_PERIOD days.
    :return a list with all the events ids (strings)
    """
    now = datetime.now()
    time_min = datetime(now.year, now.month, now.day, 0, 0, 0)  # start reading from the beginning of today
    time_max = time_min + timedelta(days=PLANNING_TIME_PERIOD)

    calendar_events = service.events().list(calendarId=write_calendar_id,
                                            maxResults=1000,
                                            singleEvents=True,
                                            timeMin=datetime_to_string(time_min),
                                            timeMax=datetime_to_string(time_max)).execute()
    # keep only the events that have specific hours (leave out whole-day events):
    now = datetime.now()
    result = []

    for e in calendar_events['items']:
        if 'dateTime' in e['start'] and now <=  string_to_datetime(e['end']['dateTime']):
            result.append(e['id'])

    return result


def delete_future_events(event_ids):
    for id in event_ids:
        service.events().delete(calendarId=write_calendar_id, eventId=id).execute()


def get_start_time():
    print("welcome to your study time planner!")

    start_time = datetime.now()
    done = False
    while not done:
        try:
            if not strtobool(input("start planning from now on?")):
                start_time = maya.parse(input("what date and time would"
                                              " you like to start planning "
                                              "from? ")).datetime(to_timezone='Israel',
                                                                  naive=True)
            done = True

        except ValueError:
            print("your answer is not clear.")

    done = False
    print("please note that the planning will delete all the events in the "
          "study calendar from the time you specified and on.")

    while not done:
        try:
            if not strtobool(input("would you like to continue?")):
                exit()
            else:
                done = True
        except ValueError:
            print("your answer is not clear.")
    return start_time


def plan_time_period(tasks, busy_times_lst, start_time):
    """
    plan the following time period and insert events in the writing calendar accordingly.
    the events inserted will not override the existing events in the reading calendars.
    :param tasks: list containing lists of length 3, each inner list represents a task.
    the inner lists are of the form: [summary, due_date, duration].
    summary :type: string
    due_date :type: datetime object
    duration :type: timedelta object
    the outer list is sorted by due-date.
    :param busy_times_lst: list of busy times sorted by the start time.
     each element is of the form: {'start': X, 'end': Y}.
    X and Y :type: datetime
    between each two busy time intervals there is at least 45 mins.
    """
    planning_period_end = datetime(start_time.year, start_time.month, start_time.day+PLANNING_TIME_PERIOD, 21, 0, 0)
    done_planning = False
    i = 0  # idx of busy_times_lst

    for task in tasks:

        if done_planning:
            break

        [summary, due_date, task_duration] = task

        actual_duration = timedelta()

        while actual_duration < task_duration and not done_planning:
            if start_time >= planning_period_end:
                done_planning = True
                break

            daily_earliest_work_time = datetime(start_time.year, start_time.month, start_time.day, 10, 0, 0)
            daily_latest_work_time = datetime(start_time.year, start_time.month, start_time.day, 20, 0, 0)
            if start_time < daily_earliest_work_time:
                # start planning from this day at 10 a.m
                start_time = daily_earliest_work_time
            elif start_time >= daily_latest_work_time:
                # start planning from 10 a.m the next day
                start_time = daily_earliest_work_time + timedelta(days=1)
                continue

            if i < len(busy_times_lst):  # check the busy times lst
                available_time = min(busy_times_lst[i]['start'],
                                     daily_latest_work_time) - start_time
                if available_time < MIN_WORK_DELTA:
                    start_time = busy_times_lst[i]['end']
                    i += 1
                    continue

            else:  # done with busy times lst
                available_time = planning_period_end - start_time
                if available_time < MIN_WORK_DELTA:
                    done_planning = True
                    break

            # we have enough time to work on the task:

            event_duration = min(available_time, task_duration-actual_duration)

            if start_time+event_duration > daily_latest_work_time:
                start_time = daily_earliest_work_time + timedelta(days=1)
                continue

            create_event(summary, start_time.day, start_time.hour, start_time.minute, duration=event_duration)
            actual_duration += event_duration
            start_time += event_duration

    print("done planning all tasks! Bye!")


if __name__ == '__main__':
    # get the calendar's credentials and pickle:
    # scopes = ['https://www.googleapis.com/auth/calendar']
    # flow = InstalledAppFlow.from_client_secrets_file("client_secret.json",
    #                                                                 scopes=scopes)
    # credentials = flow.run_console()
    # pickle.dump(credentials, open("token.pkl", "wb"))

    credentials = pickle.load(open("token.pkl", "rb"))
    service = build("calendar", "v3", credentials=credentials)
    calendars = service.calendarList().list().execute()
    write_calendar_id = calendars['items'][1]['id']
    reading_calendars_id = [calendars['items'][i]['id']
                            for i in range(len(calendars['items']))
                            if calendars['items'][i]['summary']
                            in calendars_for_reading]


    # all_events = get_next_events()


    free_busy = get_next_free_busy()
    # print("busy times: ")
    # for t in free_busy:
    #     print(datetime_to_string(t['start']), " - ", datetime_to_string(t['end']))
    # print()
    future_events = get_writing_calendar_next_events()
    start = get_start_time()
    all_tasks = get_tasks()
    plan_time_period(all_tasks, free_busy, start)
    delete_future_events(future_events)
