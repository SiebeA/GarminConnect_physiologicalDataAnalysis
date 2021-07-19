#https://pypi.org/project/garminconnect/
#!/usr/bin/env python3

#%%
 
from garminconnect import ( Garmin,     GarminConnectConnectionError, GarminConnectTooManyRequestsError, GarminConnectAuthenticationError,)

import datetime
today = datetime.date.today()
date_list = [today - datetime.timedelta(days=x) for x in range(10)]

import pandas as pd



#=======================#
'   Initialize Garmin client with credentials Only needed when your program is initialized              '
#========================= #

try:
    client = Garmin('siebealbers@hotmail.com', 'Bobobalto45!')
except (
    GarminConnectConnectionError,
    GarminConnectAuthenticationError,
    GarminConnectTooManyRequestsError,
) as err:
    print("Error occured during Garmin Connect Client init: %s" % err)
    quit()
except Exception:  # pylint: disable=broad-except
    print("Unknown error occured during Garmin Connect Client init")
    quit()
    
#
    
"""
Login to Garmin Connect portal
Only needed at start of your program
The libary will try to relogin when session expires
"""
try:
    client.login()
except (
    GarminConnectConnectionError,
    GarminConnectAuthenticationError,
    GarminConnectTooManyRequestsError,
) as err:
    print("Error occured during Garmin Connect Client login: %s" % err)
    quit()
except Exception:  # pylint: disable=broad-except
    print("Unknown error occured during Garmin Connect Client login")
    quit()






#%%
    
#======================================================================== #
'''  downloading activity inf'''
#======================================================================== #
    
#for steps
stepList = [client.get_stats(date_list[I].isoformat())['totalSteps'] for I in range(len(date_list)) ]
stepList = [i for i in stepList if i] #remove nons 

#import numpy as np
#stepList = np.array(stepList)
#stepList.mean()
#stepList.max()
#stepList.min()
#stepList.argmax()

datψAsteps = {}
for I,J in zip(date_list,stepList):
    datψAsteps[I] = J
    
#stripping all the NonObject values in the dict
datψAsteps = {k: v for k, v in datψAsteps.items() if v is not None}
import statistics
statistics.median(list(datψAsteps.values()))
statistics.stdev(list(datψAsteps.values())) # Its very high because of the faulty outlier of 83k ; 

#%%===========================================================================

#lookUpThisDate = datetime.date(2020,4,4)

#for heart rates:  
heartRates = client.get_heart_rates(today.isoformat())

import datetime
Timestamp = 1585958040000
print (  datetime.datetime.fromtimestamp(Timestamp/1000) )
#print("dt_object =", dt_object)
#print("type(dt_object) =", type(dt_object))

#extracting the timestamps that have heart rates, deleting nontypes
hrlistCleaned = [I for I in heartRates['heartRateValues'] if I[1] != None ]


# I think I have millisecond, so divide timestamp by 1000
for I,J in enumerate(hrlistCleaned):
    hrlistCleaned[I][0] = datetime.datetime.fromtimestamp(J[0]/1000)


#%%===========================================================================

#timestampsHRvalues = [datetime.datetime.fromtimestamp(I[0]/1000) for I in hrlistCleaned]

#activities
activities = client.get_activities(0,5)
listv = list(activities[0].keys())
for I in listv:
    if activities[0][I] != None:
        print( activities[0][I] ) 

#all data for today:
allData_forTheDay = client.get_stats_and_body(today.isoformat())
#only keep the keys for which I have data (i.e. remove non objects)
allData_forTheDay = {k: v for k, v in allData_forTheDay.items() if v is not None}

#remove non objects for all the activities:
Counter =0
for I in activities:
    activities[Counter] = {k: v for k, v in I.items() if v is not None}
    Counter +=1
#%%===========================================================================

#%%=======================#
'            Organizing (df)                '
#========================= #

df = pd.DataFrame()

keys = 'averageHR startTimeLocal activityName calories duration elapsedDuration distance '.split()


activities_filtered = []
# counter = 0
for dic in activities:
    for key in keys:
        # print(key,'\t\t', dic[key])
        # df.[dic['activityName'][20:]] = dic[key] # df.append({'keys':key,'values':dic[key]},ignore_index=True)
        
        # df=df.append({'keys':key,'values':dic[key]},ignore_index=True)
        dic = { key:val for key, val in dic.items() if key in keys }
    activities_filtered.append(dic)
        # counter +=1

activities_filtered_df = pd.DataFrame.from_dict(activities_filtered)

# change a columns values from seconds to minutes:
activities_filtered_df['duration']  = activities_filtered_df['duration'] /60


#%%=======================#
'            Analyzing                '
#========================= #

df['heartbeats'] = df['duration']*df['averageHR']









#%%
#======================================================================== #
'     enhance further:                                                         '
#======================================================================== #

# dates next to steps in steplist
# multisport specification
# are heart rates, the ones taen evvery 2 minutes *hrlistcleaned) averages?



#======================================================================== #
' see if I can do something with time series:                                                              '
#======================================================================== #

##format time
#format = '%Y-%m-%d %H:%M:%S %z'
#hr['@creationDate'] = pd.to_datetime(df['@creationDate'],
#                                     format=format)
#
#hr['@startDate'] = pd.to_datetime(df['@startDate'],
#                                  format=format)
#hr['@endDate'] = pd.to_datetime(df['@endDate'],
#                                format=format)
#
#
#hr.loc[:,'@value'] = pd.to_numeric(hr.loc[:,'@value'])
#
#
#hr.dtypes
#
#
#hrByCreation = hr.groupby('@creationDate').sum()
#
##this sums everything in a X; not helpful for HR, but yes for steps
#by_minute = hrByCreation['hr'].resample('T').sum()
#
#
#hrByCreation.iloc[:1]
#
#x = by_minute[by_minute['@value']>0]
