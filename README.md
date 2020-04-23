# TaskManager
A chatbot-like software to manage google tasks & google calendar for studying purposes.

# About the Software
This software is meant to help you plan your time. You will give it your task list and how long you need for each task.
It will plan your time and create events accordingly.
First you will need to answer a few quick questions about your pereferences and then you can start planning.
Please note that The program serializes your information so it can be used for future use.
Therefor, after the first run of the program you will find a few ".pkl" files in the same folder. 
Do not delete them or your information will be lost.

# Implementation Details
This program runs on mechines that have python 3.7.X installed as well as the following modules:
maya - used to parse user's natural language date and time input.
google_auth_oauthlib - used to get a Flow object that is used for getting authorization from the user. 
googleapiclient - used for building Resource objects, that are used for interacting with the service.

Google calendar & tasks API uses the OAuth 2.0 protocol for authorization. usesInitially, the program uses its client secret (json file previously downloaded) to create a google_auth_oauthlib.flow.Flow object. It then asks the user to give their permission that the program will access their google calendar and tasks. After the user's consent, it gets back a 	google.oauth2.credentials.Credentials object and dumps it into a pickle file, to be saved for the next times the program is run. Every time the program runs, the credentials file is read and a services variable is set, to be used by the functions of the program that communicates with the server. This object will then be used to handle all http requests and repsonses. 


# About the Files
Task_Manager.py: main driver of the TaskManager program.
task_management.py:  file to be used for modifying the user's task list on this program and manage all communication with google tasks.
calendar_management.py:  file to be used for planning the user's schedule and manage all communication with google calendar. 
program_initial_setup.py:  file to be used in the first running of the program to set get credentials and preferences from the user.
settings_and_utility.py: file to be shared with all program files. contains utility functions, globals and constants.
