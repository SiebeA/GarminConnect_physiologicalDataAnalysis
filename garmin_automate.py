# TODO:
# - solve the timezone issue: since the data is recorded in different time zones; the df output does not start from 00:00 when the timezone does not match the local timezonej 
# - only show one line of the day date; thereafter only the time


#!/usr/bin/env python3
"""
pip3 install cloudscraper requests readchar pwinput

export EMAIL=<your garmin email>
export PASSWORD=<your garmin password>

"""
import datetime
import json
import logging
import os
import sys

import requests
import pwinput
import readchar

from garminconnect import (
    Garmin,
    GarminConnectAuthenticationError,
    GarminConnectConnectionError,
    GarminConnectTooManyRequestsError,
)

import datetime
import openpyxl
import pytz
import pandas as pd
pd.set_option("display.max_rows", None)

# time format
# timezone = pytz.timezone("Europe/London") # tenerife
# timezone = pytz.timezone("Europe/Amsterdam") # Thuis
timezone = pytz.timezone("Europe/Athens") # greece
# print the current time:
datetime.datetime.now(timezone).strftime("%Y-%m-%d %H:%M") # the '%' is used to format the date and time, examples:

date_str = '2023-05-16T13:30:00.0'
date_obj = datetime.datetime.strptime(date_str, '%Y-%m-%dT%H:%M:%S.%f')

today = datetime.date.today() # datetime is a module, date is a class, today is a method


# Configure debug logging
# logging.basicConfig(level=logging.DEBUG)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables if defined
email = os.getenv("EMAIL")
password = os.getenv("PASSWORD")
api = None

# Example selections and settings
today = datetime.date.today()
startdate = today - datetime.timedelta(days=10) # Select past week
start = 0
limit = 100
start_badge = 1  # Badge related calls calls start counting at 1
activitytype = ""  # Possible values are: cycling, running, swimming, multi_sport, fitness_equipment, hiking, walking, other
activityfile = "MY_ACTIVITY.fit" # Supported file types are: .fit .gpx .tcx


menu_options = {
    "8": f"Get steps and floors data for today or specific date",
    # "-": f"Get daily step data for '{startdate.isoformat()}' to '{today.isoformat()}'",
    # "info": "e.g. enter: datetime.date(2023,4,14)",
    # "o": "Get last activity",
    # None: f"----",
    # # "h": "Get personal record for user",
    # "3": f"Get activity data for '{today.isoformat()}'",
    # "c": f"Get sleep data for '{today.isoformat()}'",
    # "f": f"Get SpO2 data for '{today.isoformat()}'",
    # "g": f"Get max metric data (like vo2MaxValue and fitnessAge) for '{today.isoformat()}'",
    # "n": f"Get activities data from start '{start}' and limit '{limit}'",
    # "p": f"Download activities data by date from '{startdate.isoformat()}' to '{today.isoformat()}'",
    # "r": f"Get all kinds of activities data from '{start}'",
    # "x": f"Get Heart Rate Variability data (HRV) for '{today.isoformat()}'",
    # "z": f"Get progress summary from '{startdate.isoformat()}' to '{today.isoformat()}' for all metrics",
    # "A": "Get gear, the defaults, activity types and statistics",
    # "Z": "Logout Garmin Connect portal",
    # "q": "Exit",
}

# ============================================
#   # created by Siebe:                                      #
# ============================================

def format_date(date_str):
    """Format date string in YYYY-MM-DD format"""
    date_obj = datetime.datetime.strptime(date_str, '%Y-%m-%d')
    return date_obj.strftime('%Y-%m-%d')

def write_data_to_file(data):
    """Write data to a file in the desired format"""
    with open('Output_stepData\step_data.txt', 'w') as f:
        f.write('Date\ttotalSteps\n')
        # reverse the list so that the oldest date is first
        data.reverse()
        for item in data:
            date_str = format_date(item['calendarDate'])
            total_steps = item['totalSteps']
            f.write(f'{date_str}\t{total_steps}\n')
            # also print the steps to the console
            print(f'{total_steps}')
    print('Data written to file: step_data.txt')

# :# ============================================
#    Original                                     #
# ============================================

def get_credentials():
    """Get user credentials."""
    email = input("Login e-mail: ")
    password = pwinput.pwinput(prompt='Password: ') # pwinput is a library that hides the password input

    return email, password


def init_api(email, password):
    """Initialize Garmin API with your credentials."""

    try:
        ## Try to load the previous session
        with open("session.json") as f:
            saved_session = json.load(f)

            print(
                "Login to Garmin Connect using session loaded from 'session.json'...\n"
            )

            # Use the loaded session for initializing the API (without need for credentials)
            api = Garmin(session_data=saved_session)

            # Login using the
            api.login()

    except (FileNotFoundError, GarminConnectAuthenticationError):
        # Login to Garmin Connect portal with credentials since session is invalid or not present.
        print(
            "Session file not present or turned invalid, login with your Garmin Connect credentials.\n"
            "NOTE: Credentials will not be stored, the session cookies will be stored in 'session.json' for future use.\n"
        )
        try:
            # Ask for credentials if not set as environment variables
            if not email or not password:
                email, password = get_credentials()

            api = Garmin(email, password)
            api.login()

            # Save session dictionary to json file for future use
            with open("session.json", "w", encoding="utf-8") as f:
                json.dump(api.session_data, f, ensure_ascii=False, indent=4)
        except (
            GarminConnectConnectionError,
            GarminConnectAuthenticationError,
            GarminConnectTooManyRequestsError,
            requests.exceptions.HTTPError,
        ) as err:
            logger.error("Error occurred during Garmin Connect communication: %s", err)
            return None

    return api


def print_menu():
    """Print examples menu."""
    for key in menu_options.keys():
        print(f"{key} -- {menu_options[key]}")
    print("Make your selection: ", end="", flush=True)


def switch(api, i):
    """Run selected API call."""

    # Exit example program
    if i == "q":
        print("Bye!")
        sys.exit()

    # Skip requests if login failed
    if api:
        today = datetime.date.today()

        
        try:
            print(f"\n\nExecuting: {menu_options[i]}\n")
# ============================================
#                                         #
# ============================================
            if i == "8":
                today = datetime.date.today()
                # always today as default because we want to automate this and download the data every day for today
                # Get steps and floors climbed data for 'MM-DD'
                output = api.get_steps_data(today.isoformat())
                output_floors = api.get_floors(today.isoformat())
                # output = api.get_steps_data(datetime.date.today().isoformat())
                for item in output:
                    # parse the start time
                    start_time = datetime.datetime.fromisoformat(item["startGMT"])
                    # convert the start time to the user's timezone
                    start_time = pytz.utc.localize(start_time).astimezone(timezone)
                    # format the start time without the GMT offset
                    item["startGMT"] = start_time.strftime('%m-%d %H:%M')

                    # parse the end time
                    end_time = datetime.datetime.fromisoformat(item["endGMT"])
                    # convert the end time to the user's timezone
                    end_time = pytz.utc.localize(end_time).astimezone(timezone)
                    # format the end time without the GMT offset
                    # item["endGMT"] = end_time.strftime('%m-%d %H:%M')
                    item["endGMT"] = end_time.strftime('%H:%M')

                # convert output which is a list of dictionaries to a dataframe
                df = pd.DataFrame(output)
                # rename the "pushes" column to "cumulative steps"
                df.rename(columns={"pushes": "cumulative steps"}, inplace=True)
                
                # calculate the cumulative steps by adding eachh steps value to the previous value starting from index 1
                df["cumulative steps"] = df["steps"].cumsum()

                # add a new column to the df from : output_floors["floorValuesArray"] 2th column:
                df["floorsAscended"] =  pd.DataFrame(output_floors["floorValuesArray"])[2]
                df["floorsDescended"] =  pd.DataFrame(output_floors["floorValuesArray"])[3]
                df["floorsAscendedCumulative"] = df["floorsAscended"].cumsum()
                
                # print(df.tail(50))
                print(df)
                # convert it to a excel file and save it with the specific date as filename:

                # save it tot he Output_stepData folder:
                df.to_excel(f"Output_stepData/steps_{specific_date.isoformat()}.xlsx", index=False)

                print(f"\n steps_{specific_date.isoformat()}.xlsx has been saved to the current directory\n")
                print(f'\n the timezone location is {timezone.zone}\n')
                print(f"if you want to go to the garmin connect website for this day you can click this link: \n https://connect.garmin.com/modern/daily-summary/{specific_date.isoformat()} \n\n")


 
            elif i == "Z":
                # Logout Garmin Connect portal
                api.logout()
                api = None

        except (
            GarminConnectConnectionError,
            GarminConnectAuthenticationError,
            GarminConnectTooManyRequestsError,
            requests.exceptions.HTTPError,
        ) as err:
            logger.error("Error occurred: %s", err)
        except KeyError:
            # Invalid menu option chosen
            pass
    else:
        print("Could not login to Garmin Connect, try again later.")

# Main program loop
while True:
    # Display header and login

    # Init API
    if not api: # if api is not defined yet because it is the first time the program is run
        api = init_api(email, password)

    # Display menu
    print_menu()
    i = readchar.readkey()
    switch(api, i)
