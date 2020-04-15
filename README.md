# TaskManager
A chatbot-like software to manage google tasks & google calendar for studying purposes.

This software is meant to help you plan your time. You will give it your task list and how long you need for each task.
It will plan your time and create events accordingly.
First you will need to answer a few quick questions about your pereferences and then you can start planning.
Please note that The program serializes your information so it can be used for future use.
Therefor, after the first run of the program you will find a few ".pkl" files in the same folder. 
Do not delete them or your information will be lost.

In order to run the program you need to have python 3.7.X installed on your computer,
and install the packages: maya, google_auth_oauthlib, googleapiclient.

about the files:
Task_Manager.py: main driver of the TaskManager program.
task_management.py:  file to be used for modifying the user's task list on this program and manage all communication with google tasks.
calendar_management.py:  file to be used for planning the user's schedule and manage all communication with google calendar. 
program_initial_setup.py:  file to be used in the first running of the program to set get credentials and preferences from the user.
settings_and_utility.py: file to be shared with all program files. contains utility functions, globals and constants.
