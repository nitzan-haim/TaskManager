# file to be used for planning the user's schedule and manage all communication
# with google calendar. #

import settings_and_utility as util
from datetime import datetime, timedelta


def create_event(summary, day, hour, minutes, sec=0,
                 duration=util.timedelta(minutes=60),
                 month=datetime.today().month,
                 year=datetime.today().year):
    """
    create an event in the writing calendar with the given characteristic.
    :param summary: title for this event
    :param day: the day in the month that this event will take place.
        :type: int, 1 <= day <= 31/30/29/28
    :param hour: the hour of the day that this event will take place.
        :type: int 0 <= hour <= 23
    :param minutes: the minute of the hour that this event will take place.
        :type: int, 0 <= minutes <= 59
    :param sec: the seconds of the minute that this event will take place.
        :type: int, 0 <= sec <= 59
    :param duration: duration of activity.
        :type: timedelta object
    :param month: the month in the year that this event will take place.
        :type: int, 1 <= month <= 12
    :param year: the year that this event will take place.
        :type: int.
    """
    start_time = datetime(year, month, day, hour, minutes, sec)
    end_time = start_time + duration

    event = {
        'summary': summary,
        'start': {
            'dateTime': start_time.strftime(util.TIME_FORMAT),
            'timeZone': util.TIME_ZONE,
        },
        'end': {
            'dateTime': end_time.strftime("%Y-%m-%dT%H:%M:%S"),
            'timeZone': util.TIME_ZONE,
        },

        'reminders': {
            'useDefault': False,
            'overrides': [
                {'method': 'email', 'minutes': 60},
                {'method': 'popup', 'minutes': 30},
            ],
        },
    }

    util.services['calendar'].events().insert(calendarId=util.write_calendar_id, body=event).execute()


def get_next_free_busy():
    """
    get busy information for reading calendars for the next time period.
    :return: list of busy times sorted by the start time.
     each element is of the form: {'start': X, 'end': Y}.
    X and Y :type: datetime
    """

    now = datetime.now()
    time_min = datetime(now.year, now.month, now.day, 0, 0, 0)  # start reading from the beginning of today
    time_max = datetime(now.year, now.month, now.day + util.PLANNING_TIME_PERIOD + 1, 0, 0, 0)

    body = {
        "timeMin": time_min.strftime(util.TIME_FORMAT + '+03:00'),
        "timeMax": time_max.strftime(util.TIME_FORMAT + '+03:00'),
        "timeZone": util.TIME_ZONE,
        "items": [{"id": cal_id} for cal_id in util.reading_calendars_id]
    }
    events_result = util.services['calendar'].freebusy().query(body=body).execute()
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
            if now > util.string_to_datetime(b_t['end']):  # skip past events
                continue
            times_not_combined.append({'start': util.string_to_datetime(b_t['start']),
                                       'end': util.string_to_datetime(b_t['end'])})

    times_not_combined.sort(key=lambda elem: elem['start'])

    result = []
    # combine busy times
    i = 0
    n = len(times_not_combined)
    while i < n - 1:
        s1 = times_not_combined[i]['start']
        e1 = times_not_combined[i]['end']
        s2 = times_not_combined[i + 1]['start']
        e2 = times_not_combined[i + 1]['end']
        if e1 <= s2 and s2 - e1 >= util.MIN_WORK_DELTA:
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
    time_max = time_min + timedelta(days=util.PLANNING_TIME_PERIOD)

    calendar_events = util.services['calendar'].events()\
        .list(calendarId=util.write_calendar_id,
              maxResults=1000,
              singleEvents=True,
              timeMin=util.datetime_to_string(time_min),
              timeMax=util.datetime_to_string(time_max)).execute()

    # keep only the events that have specific hours (leave out whole-day events):
    now = datetime.now()
    result = []

    for e in calendar_events['items']:
        if 'dateTime' in e['start'] and now <= util.string_to_datetime(e['end']['dateTime']):
            result.append(e['id'])

    return result


def plan_time_period(tasks, busy_times_lst, start_time):
    """
    plan the following time period and insert events in the writing calendar
    accordingly.
    the events inserted will not override the existing events in the reading
    calendars.

    :param tasks: list containing lists of length 3, each inner list represents
    a task. the inner lists are of the form: [summary, due_date, duration, id].
    summary :type: string
    due_date :type: datetime object
    duration :type: timedelta object
    the outer list is sorted by due-date.

    :param busy_times_lst: list of busy times sorted by the start time.
     each element is of the form: {'start': X, 'end': Y}.
    X and Y :type: datetime
    between each two busy time intervals there is at least 45 mins.

    :param start_time: the time of which to start the planning from.
    :type: datetime object.
    """
    print("planning and updating your calendar...")
    planning_period_end = datetime(start_time.year, start_time.month,
                                   start_time.day + util.PLANNING_TIME_PERIOD, 21, 0, 0)
    done_planning = False
    i = 0  # idx of busy_times_lst

    for task in tasks:

        if done_planning:
            break

        [summary, due_date, task_duration, task_id] = task

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
                if available_time < util.MIN_WORK_DELTA:
                    start_time = busy_times_lst[i]['end']
                    i += 1
                    continue

            else:  # done with busy times lst
                available_time = planning_period_end - start_time
                if available_time < util.MIN_WORK_DELTA:
                    done_planning = True
                    break

            # we have enough time to work on the task:

            event_duration = min(available_time, task_duration - actual_duration)

            if start_time + event_duration > daily_latest_work_time:
                start_time = daily_earliest_work_time + timedelta(days=1)
                continue

            create_event(summary, start_time.day, start_time.hour, start_time.minute, duration=event_duration)
            actual_duration += event_duration
            start_time += event_duration

            if start_time > due_date:
                print("sorry, the due date of ", summary, "is too close.")
                print("we planned for you ", actual_duration, "to spend on this task.")
                print("we could not fit ", task_duration - actual_duration, " before the due time.")
                actual_duration = task_duration  # move on to next task


def delete_future_events(event_ids):
    """
    delete all the events specified in event_ids.
    :param event_ids: list of ids of events to delete. :type: list of strings
    """
    for ev_id in event_ids:
        util.services['calendar'].events().delete(calendarId=util.write_calendar_id, eventId=ev_id).execute()
