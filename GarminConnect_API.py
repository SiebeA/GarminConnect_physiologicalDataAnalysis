#https://pypi.org/project/garminconnect/
#!/usr/bin/env python3

from pandas import DataFrame as df
 
from garminconnect import ( Garmin,GarminConnectConnectionError,GarminConnectTooManyRequestsError, GarminConnectAuthenticationError,)

nrOfActivitiesIncluded = 5

import datetime
today = datetime.date.today()


# date_list = [today - datetime.timedelta(days=x) for x in range(10)]
#=======================#
'   Initialize Garmin client with credentials Only needed when your program is initialized              '
#========================= #
try:
    client = Garmin('siebealbers@hotmail.com', 'Bobobalto45!')
except ( GarminConnectConnectionError, GarminConnectAuthenticationError, GarminConnectTooManyRequestsError, )as err:
    print("Error occured during Garmin Connect Client init: %s" % err)
    quit()
except Exception:  # pylint: disable=broad-except
    print("Unknown error occured during Garmin Connect Client init")
    quit()
    
# =============================================================================
# Login to Garmin Connect portal Only needed at start of your program The libary will try to relogin when session expires
# =============================================================================

try:
    client.login()
except ( GarminConnectConnectionError, GarminConnectAuthenticationError, 
GarminConnectTooManyRequestsError, ) as err:
    print("Error occured during Garmin Connect Client login: %s" % err)
    quit()
except Exception:  # pylint: disable=broad-except
    print("Unknown error occured during Garmin Connect Client login")
    quit()



#%%
    
#======================================================================== #
'''  downloading activity inf'''
#======================================================================== #
    
#all data for today:
allData_forTheDay = client.get_stats_and_body(today.isoformat())
allData_forTheDay = {k: v for k, v in allData_forTheDay.items() if v is not None}#only keep the keys for which I have data (i.e. remove non objects)

stats = client.get_stats(today.isoformat())
stats = {k: v for k, v in stats.items() if v is not None}

act_details = client.get_activity_details(7162578374)
heartrates = client.get_heart_rates(str(today))
url = client.url_activities
#timestampsHRvalues = [datetime.datetime.fromtimestamp(I[0]/1000) for I in hrlistCleaned]

#activities
activities = client.get_activities(0,nrOfActivitiesIncluded)
listv = list(activities[0].keys())
for I in listv:
    if activities[0][I] != None:
        print( activities[0][I] ) 
#remove non objects for all the activities:
Counter =0
for I in activities:
    activities[Counter] = {k: v for k, v in I.items() if v is not None}
    Counter +=1

keys = 'averageHR startTimeLocal activityName calories duration elapsedDuration distance '.split() #from activities; will be used for columns in df
activities_filtered = []
for dic in activities: #activities = listOfDics each holding keysRepresentingGarminMetrics
    for key in keys:
        if key =='activityName':
            dic['activityName'] = dic['activityName'][20:] #remove the town of the activity
            dic['startTimeLocal'] = dic['startTimeLocal'][5:-3] #remove the town of the
        dic = { key:val for key, val in dic.items() if key in keys } # my defined keys from all the keys
    activities_filtered.append(dic)

activities_filtered_df = df.from_dict(activities_filtered)
# change a columns values from seconds to minutes:
activities_filtered_df['duration']  = activities_filtered_df['duration'] /60
activities_filtered_df['elapsedDuration']  = activities_filtered_df['elapsedDuration'] /60
activities_filtered_df['distance']  = activities_filtered_df['distance'] /1000

# change the name of the column to indicate the ... , although perhaps self explantatory
# aactivities_filtered_df = activities_filtered_df.rename(columns={'duration':'duration minutes decimal'})

#%%=======================#
'            Analyzing                '
#========================= #

activities_filtered_df['heartbeats'] = activities_filtered_df['duration']*activities_filtered_df['averageHR']

#TODO all the heart rate datapoints to calculate the SD


