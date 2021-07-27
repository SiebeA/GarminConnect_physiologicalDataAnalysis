
def clientt():
    from garminconnect import ( Garmin,GarminConnectConnectionError,GarminConnectTooManyRequestsError, GarminConnectAuthenticationError,)
    try:
        client = Garmin('email', 'password')
    except ( GarminConnectConnectionError, GarminConnectAuthenticationError, GarminConnectTooManyRequestsError, )as err:
        print("Error occured during Garmin Connect Client init: %s" % err)
        quit()
    except Exception:  # pylint: disable=broad-except
        print("Unknown error occured during Garmin Connect Client init")
        quit()
    return client

def login():
    client = clientt()
    import datetime
    today = datetime.date.today()
    from garminconnect import ( Garmin,GarminConnectConnectionError,GarminConnectTooManyRequestsError, GarminConnectAuthenticationError,)
    try:
        client.login()
    except ( GarminConnectConnectionError, GarminConnectAuthenticationError, 
    GarminConnectTooManyRequestsError, ) as err:
        print("Error occured during Garmin Connect Client login: %s" % err)
        quit()
    except Exception:  # pylint: disable=broad-except
        print("Unknown error occured during Garmin Connect Client login")
        quit()
    return client, today


def get_activities(nractsincluded):
    # client = login() PRObleMS IF LEFT HERE
    
    #TODO print timestamp ; \n after day , automatic summing of the day ; daysBack instead of nr of activities; endTime = startime+elapsed ; 
    nrOfActivitiesIncluded = nractsincluded
    activities = client.get_activities(0,nrOfActivitiesIncluded)
    #remove non objects for all the activities:
    Counter =0
    for I in activities:
        activities[Counter] = {k: v for k, v in I.items() if v is not None}
        Counter +=1
    
    from pandas import DataFrame as df
    keys = 'averageHR startTimeLocal activityName calories duration elapsedDuration distance '.split() #from activities; will be used for columns in df
    activities_filtered = []
    for dic in activities: #activities = listOfDics each holding keysRepresentingGarminMetrics
        for key in keys:
            if key =='activityName':
                dic['activityName'] = dic['activityName'][20:] #remove the town of the activity
                # dic['startTimeLocal'] = dic['startTimeLocal'][5:-3] #easy for ide, but messes up dateformat for csv
            dic = { key:val for key, val in dic.items() if key in keys } # my defined keys from all the keys
        activities_filtered.append(dic)
    activities_filtered_df = df().from_dict(activities_filtered)
    # change a columns values from seconds to minutes:
    activities_filtered_df['duration']  = activities_filtered_df['duration'] /60
    activities_filtered_df['elapsedDuration']  = activities_filtered_df['elapsedDuration'] /60
    activities_filtered_df['distance']  = activities_filtered_df['distance'] /1000
    activities_filtered_df.to_csv('output.csv', index=False)
    return activities_filtered_df, activities


activities_filtered_df, activities = get_activities(5)




