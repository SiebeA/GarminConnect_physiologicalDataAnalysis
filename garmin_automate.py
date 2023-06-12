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
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv("info.env")

# Configure debug logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
pd.set_option("display.max_rows", None)

# Read the email and password from environment variables
email = os.getenv("EMAIL")
password = os.getenv("PASSWORD")
api = None

timezone = pytz.timezone("Europe/Amsterdam") # greece
# print the current time:
datetime.datetime.now(timezone).strftime("%Y-%m-%d %H:%M") # the '%' is used to format the date and time, examples:

date_str = '2023-05-16T13:30:00.0'
date_obj = datetime.datetime.strptime(date_str, '%Y-%m-%dT%H:%M:%S.%f')

today = datetime.date.today() # datetime is a module, date is a class, today is a method


def init_api(email, password):
    """Initialize Garmin API with your credentials."""
    try:
        # Try to load the previous session
        with open("session.json") as f:
            saved_session = json.load(f)

            print("Login to Garmin Connect using session loaded from 'session.json'...\n")

            # Use the loaded session for initializing the API (without need for credentials)
            api = Garmin(session_data=saved_session)

            # Login using the loaded session
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


def switch(api, i, timeframe):
    """Run selected API call."""

    # Skip requests if login failed
    if api:
        today = datetime.date.today()

        try:
            if i == "8":
                if timeframe == "y" or timeframe == "yesterday".lower():
                    timeframe = today - datetime.timedelta(days=1)
                elif timeframe == "lxd".lower():
                    num_days = int(input("Enter the number of days: "))
                    timeframe = today - datetime.timedelta(days=num_days)
                else:
                    timeframe = today

                # Loop through each day in the timeframe
                while timeframe <= today:
                    output = api.get_steps_data(timeframe.isoformat())  # Get steps and floors climbed data for 'YYYY-MM-DD'
                    output_floors = api.get_floors(timeframe.isoformat())


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


                    # Convert output, which is a list of dictionaries, to a DataFrame
                    df = pd.DataFrame(output)
                    # Rename the "pushes" column to "cumulative steps"
                    df.rename(columns={"pushes": "cumulative steps"}, inplace=True)

                    # Calculate the cumulative steps by adding each steps value to the previous value starting from index 1
                    df["cumulative steps"] = df["steps"].cumsum()

                    # Add a new column to the DataFrame from output_floors["floorValuesArray"] 2nd column
                    df["floorsAscended"] = pd.DataFrame(output_floors["floorValuesArray"])[2]
                    df["floorsDescended"] = pd.DataFrame(output_floors["floorValuesArray"])[3]
                    df["floorsAscendedCumulative"] = df["floorsAscended"].cumsum()

                    # Convert it to an Excel file and save it with the specific date as filename
                    location = str(timezone).split("/")[1]
                    filename = f"steps_{timeframe.isoformat()}_{location}.xlsx"
                    filepath = os.path.join("Output_stepData", filename)
                    df.to_excel(filepath, index=False)

                    print(f"\n{filename} has been saved to the Output_stepData folder.\n")

                    # Increment to the next day
                    timeframe += datetime.timedelta(days=1)

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


if __name__ == "__main__":
    api = init_api(email, password)
    timeframe = input("yesterday (y), today, or last_x_days (lxd)? \n")

    switch(api, "8", timeframe)


# TODO:
# - download yesterday data to insure that the data is complete and synced
# - check delta with last sync timestamp