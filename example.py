# TODO:
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

# time format
timezone = pytz.timezone("Europe/Athens")
# print the current time:
datetime.datetime.now(timezone).strftime("%Y-%m-%d %H:%M") # the '%' is used to format the date and time, examples:

date_str = '2023-04-27T13:30:00.0'
date_obj = datetime.datetime.strptime(date_str, '%Y-%m-%dT%H:%M:%S.%f')


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
    "-": f"Get daily step data for '{startdate.isoformat()}' to '{today.isoformat()}'",
    "o": "Get last activity",
    "8": f"Get steps data for '{today.isoformat()}'",
    None: f"----",
    "h": "Get personal record for user",
    "3": f"Get activity data for '{today.isoformat()}'",
    "c": f"Get sleep data for '{today.isoformat()}'",
    "f": f"Get SpO2 data for '{today.isoformat()}'",
    "g": f"Get max metric data (like vo2MaxValue and fitnessAge) for '{today.isoformat()}'",
    "n": f"Get activities data from start '{start}' and limit '{limit}'",
    "p": f"Download activities data by date from '{startdate.isoformat()}' to '{today.isoformat()}'",
    "r": f"Get all kinds of activities data from '{start}'",
    "x": f"Get Heart Rate Variability data (HRV) for '{today.isoformat()}'",
    "z": f"Get progress summary from '{startdate.isoformat()}' to '{today.isoformat()}' for all metrics",
    "A": "Get gear, the defaults, activity types and statistics",
    "Z": "Logout Garmin Connect portal",
    "q": "Exit",
}

# ============================================
#   # created by Siebe:                                      #
# ============================================

# def format_date(date_str):
#     """Format date string in YYYY-MM-DD format"""
#     date_obj = datetime.datetime.strptime(date_str, '%Y-%m-%d')
#     return date_obj.strftime('%Y-%m-%d')

def write_data_to_file(data):
    """Write data to a file in the desired format"""
    with open('step_data.txt', 'w') as f:
        f.write('Date\ttotalSteps\n')
        # reverse the list so that the oldest date is first
        data.reverse()
        for item in data:
            date_str = format_date(item['calendarDate'])
            total_steps = item['totalSteps']
            f.write(f'{date_str}\t{total_steps}\n')
    print('Data written to file: step_data.txt')

# :# ============================================
#    Original                                     #
# ============================================
def display_json(api_call, output):
    """Format API output for better readability."""

    dashed = "-"*20
    header = f"{dashed} {api_call} {dashed}"
    footer = "-"*len(header)

    print(header)
    print(json.dumps(output, indent=4))
    print(footer)

def display_text(output):
    """Format API output for better readability."""

    dashed = "-"*60
    header = f"{dashed}"
    footer = "-"*len(header)

    print(header)
    print(json.dumps(output, indent=4))
    print(footer)

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
        try:
            print(f"\n\nExecuting: {menu_options[i]}\n")

            # USER BASICS
            if i == "1":
                # Get full name from profile
                display_json("api.get_full_name()", api.get_full_name())

# ============================================
#                                         #
# ============================================
            elif i == "8":
                # Get steps data for 'YYYY-MM-DD'
                output = api.get_steps_data(today.isoformat())
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
                # print the last 3 rows of the dataframe:
                print(df)
                # convert it to a excel file and save it with the date in the file name
                df.to_excel(f'step_data_{today.strftime("%Y-%m-%d")}.xlsx', index=False)
                print(f"Data written to file: step_data_{today.strftime('%Y-%m-%d')}.xlsx")
                # convert output which is a list of dictionaries to a csv file


            # USER STATISTIC SUMMARIES
            elif i == "3":
                # Get activity data for 'YYYY-MM-DD'
                display_json(f"api.get_stats('{today.isoformat()}')", api.get_stats(today.isoformat()))
            elif i == "-":
                # Get daily step data for 'YYYY-MM-DD'
                steps = display_json(f"api.get_daily_steps('{startdate.isoformat()}, {today.isoformat()}')", api.get_daily_steps(startdate.isoformat(), today.isoformat()))
                # steps = api.get_daily_steps(startdate.isoformat(), today.isoformat())
                write_data_to_file(steps)



            elif i == "c":
                # Get sleep data for 'YYYY-MM-DD'
                display_json(f"api.get_sleep_data('{today.isoformat()}')", api.get_sleep_data(today.isoformat()))
            elif i == "f":
                # Get SpO2 data for 'YYYY-MM-DD'
                display_json(f"api.get_spo2_data('{today.isoformat()}')", api.get_spo2_data(today.isoformat()))
            elif i == "g":
                # Get max metric data (like vo2MaxValue and fitnessAge) for 'YYYY-MM-DD'
                display_json(f"api.get_max_metrics('{today.isoformat()}')", api.get_max_metrics(today.isoformat()))
            # ACTIVITIES
            elif i == "n":
                # Get activities data from start and limit
                display_json(f"api.get_activities({start}, {limit})", api.get_activities(start, limit)) # 0=start, 1=limit
            elif i == "o":
                # Get last activity
                output = api.get_last_activity()
                output = {k: v for k, v in output.items() if v is not None}
                display_json("api.get_last_activity()", output)
                print("# only returned the dictionary keys whose value is not null, or None \n\n")
                # print the following keys from the dictionary: duration; elevationGain; calories; steps:
                print(f"Duration: {round(output['duration']/60)} minutes \n Elevation Gain: {output['elevationGain']}\nCalories: {output['calories']}\nSteps: {output['steps']:,} \n\n")
            
            elif i == "p":
                # Get activities data from startdate 'YYYY-MM-DD' to enddate 'YYYY-MM-DD', with (optional) activitytype
                # Possible values are: cycling, running, swimming, multi_sport, fitness_equipment, hiking, walking, other
                activities = api.get_activities_by_date(
                    startdate.isoformat(), today.isoformat(), activitytype
                )

                # Download activities
                for activity in activities:

                    activity_id = activity["activityId"]
                    display_text(activity)

                    print(f"api.download_activity({activity_id}, dl_fmt=api.ActivityDownloadFormat.GPX)")
                    gpx_data = api.download_activity(
                        activity_id, dl_fmt=api.ActivityDownloadFormat.GPX
                    )
                    output_file = f"./{str(activity_id)}.gpx"
                    with open(output_file, "wb") as fb:
                        fb.write(gpx_data)
                    print(f"Activity data downloaded to file {output_file}")

                    print(f"api.download_activity({activity_id}, dl_fmt=api.ActivityDownloadFormat.TCX)")
                    tcx_data = api.download_activity(
                        activity_id, dl_fmt=api.ActivityDownloadFormat.TCX
                    )
                    output_file = f"./{str(activity_id)}.tcx"
                    with open(output_file, "wb") as fb:
                        fb.write(tcx_data)
                    print(f"Activity data downloaded to file {output_file}")

                    print(f"api.download_activity({activity_id}, dl_fmt=api.ActivityDownloadFormat.ORIGINAL)")
                    zip_data = api.download_activity(
                        activity_id, dl_fmt=api.ActivityDownloadFormat.ORIGINAL
                    )
                    output_file = f"./{str(activity_id)}.zip"
                    with open(output_file, "wb") as fb:
                        fb.write(zip_data)
                    print(f"Activity data downloaded to file {output_file}")

                    print(f"api.download_activity({activity_id}, dl_fmt=api.ActivityDownloadFormat.CSV)")
                    csv_data = api.download_activity(
                        activity_id, dl_fmt=api.ActivityDownloadFormat.CSV
                    )
                    output_file = f"./{str(activity_id)}.csv"
                    with open(output_file, "wb") as fb:
                        fb.write(csv_data)
                    print(f"Activity data downloaded to file {output_file}")


            elif i == "r":
                # Get activities data from start and limit
                activities = api.get_activities(start, limit)  # 0=start, 1=limit

                # Get activity splits
                first_activity_id = activities[0].get("activityId")

                display_json(f"api.get_activity_splits({first_activity_id})", api.get_activity_splits(first_activity_id))

                # Get activity split summaries for activity id
                display_json(f"api.get_activity_split_summaries({first_activity_id})", api.get_activity_split_summaries(first_activity_id))

                # Get activity weather data for activity
                display_json(f"api.get_activity_weather({first_activity_id})", api.get_activity_weather(first_activity_id))

                # Get activity hr timezones id
                display_json(f"api.get_activity_hr_in_timezones({first_activity_id})", api.get_activity_hr_in_timezones(first_activity_id))

                # Get activity details for activity id
                display_json(f"api.get_activity_details({first_activity_id})", api.get_activity_details(first_activity_id))

                # Get gear data for activity id
                display_json(f"api.get_activity_gear({first_activity_id})", api.get_activity_gear(first_activity_id))

                # Activity self evaluation data for activity id
                display_json(f"api.get_activity_evaluation({first_activity_id})", api.get_activity_evaluation(first_activity_id))

                # Get exercise sets in case the activity is a strength_training
                if activities[0]["activityType"]["typeKey"] == "strength_training":
                    display_json(f"api.get_activity_exercise_sets({first_activity_id})", api.get_activity_exercise_sets(first_activity_id))

            elif i == "x":
                # Get Heart Rate Variability (hrv) data
                display_json(f"api.get_hrv_data({today.isoformat()})", api.get_hrv_data(today.isoformat()))

            elif i == "z":
                # Get progress summary
                for metric in ["elevationGain", "duration", "distance", "movingDuration"]:
                    display_json(
                        f"api.get_progress_summary_between_dates({today.isoformat()})", api.get_progress_summary_between_dates(
                            startdate.isoformat(), today.isoformat(), metric
                        ))

            elif i == "Z":
                # Logout Garmin Connect portal
                display_json("api.logout()", api.logout())
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
    print("\n*** Garmin Connect API Demo by cyberjunky ***\n")

    # Init API
    if not api:
        api = init_api(email, password)

    # Display menu
    print_menu()
    option = readchar.readkey()
    switch(api, option)
