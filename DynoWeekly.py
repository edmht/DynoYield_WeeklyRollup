# %%
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# %%
NVH_metrics = ['6208 Cage Failure', 'CH/Input Bearing Race Defect', 'CH/Input Bearing Ball Defect',
						'CH Inter Bearing Race Defect',
						'CH Inter Bearing Ball Defect',
						'Input Gear Clicking',
						'Intermediate Gear Clicking',
						'Output Gear Clicking',
						'Intermediate Gear Clicking Negative',
						'Intermediate Gear Clicking Positive',
						'Input Gear Clicking Positive',
						'Input Gear Clicking Negative',
						'Output Gear Clicking Negative',
						'Output Gear Clicking Positive', 
                        'Motor 3rd Ord Avg', 
                        'Growl 4-6']

# %%
df_raw = pd.read_csv('datasets\Week25.csv')
df_raw.head()

# %%
summary = pd.Series({'FirstPasses':0,
                     'DLE':0,
                           'Retest Success':0,
                           'Reworked Pass':0,
                           'Pending Rework / Unsuccessful Rework':0,
                           'Machine Health Failure':0
                           })

# %%
df = df_raw.copy()
#df.groupby('FX_Thing')['metricispass'].sum().min()
#if a test has 46 metricispass, it's a first time pass

#dropping Golden units
golden_units = ['P1025598-00-U:ST13D0013400', 'P1025598-00-U:ST17A1021978']
df = df[~df['FX_Thing'].isin(golden_units)]

retestTime = 30 #threshold time


# %%
#key and datetime
df['thing+metricName'] = df['FX_Thing']+'+'+df['metricName']
df['testTime'] = pd.to_datetime({'year':df['testYear'], 'month':df['testMonth'], 'day':df['testDay'], 'hour':df['testHour'], 'minute':df['testMinute']}) #proper formatting of datetime

# %%
df['part'].nunique()

# %%
#Finding all the first time passes. Every unit with 46 metricispass sum is a first time pass
sum_metricispass = df.groupby('FX_Thing')['metricispass'].sum()
firstPasses = sum_metricispass[sum_metricispass == 46].reset_index()['FX_Thing']
summary['FirstPasses'] = len(firstPasses)

# %%
#getting all the failures and the unique failing serials
df_allFailures = df[df['metricispass'] == 0].copy()
df_allFailures.head()

#count of unique failures
failing_serials = df_allFailures['FX_Thing'].drop_duplicates()
len(failing_serials)



# %%
#anything with only passes, but doesn't have 46 runs, is a DLE
DLEs = df['FX_Thing'].nunique() - len(firstPasses) - len(failing_serials)
summary['DLE'] = DLEs

# %%
#DLEs
uniqueSerials = df.drop_duplicates(subset = 'FX_Thing')
uniqueSerials[(~uniqueSerials['FX_Thing'].isin(failing_serials)) & (~uniqueSerials['FX_Thing'].isin(firstPasses))]

# %%
#getting all the failing and passing tests of the failing thing+metricName combinations
df_failures_and_Passes = df[df['thing+metricName'].isin(df_allFailures['thing+metricName'].unique())]

# %%
failures_and_passes_summary = df_failures_and_Passes.drop_duplicates(['part', 'metricName'])[['part', 'metricName', 'thing+metricName']]
failures_and_passes_summary 

# %% [markdown]
# # Is there a passing test?
# 

# %%
#checks to see if a passing test exists
def isPassTest(part):
    df_tmp = df_failures_and_Passes[(df_failures_and_Passes['part'] == part) & (df_failures_and_Passes['isTestPass'] == 1)]
    if df_tmp.shape[0] == 0:
        return False
    else:
        return True

# %%
failures_and_passes_summary['PassingTest?'] = failures_and_passes_summary['part'].apply(isPassTest)

# %%
failures_and_passes_summary

# %%
def calculateTime(part): #If there is a successful rework, find the time between the latest success and the latest failure
    df_test = df_failures_and_Passes[df_failures_and_Passes['part'] == part].drop_duplicates(['testID', 'isTestPass']).reset_index()
    if 1 in df_test['isTestPass'].values: #if there is a passing value
        passingLoc = df_test[df_test['isTestPass'] == 1].index.max() #max is to find the latest pass
        failingLoc = df_test[df_test['isTestPass'] == 0].index.max() #finds the latest fail
        comparison_result = df_test.loc[passingLoc, 'testTime'] - df_test.loc[failingLoc, 'testTime'] #compares the latest pass with the latest fail to find the difference between
        return comparison_result
    else: return np.nan

# %%
def failDisposition(row):
    if row['MachineHealth?'] == True:
        return 'Machine Health Failure'
    elif row['retestSuccess?'] == True:
        return 'Retest Success'
    elif row['PassingTest?'] == True:
        return 'Reworked Pass'
    else:
        return 'Pending Rework / Unsuccessful Rework'
    

# %%
#cleaningTable
failures_and_passes_summary['TimeToPass'] = failures_and_passes_summary['part'].apply(calculateTime)
failures_and_passes_summary['TimeToPass_minutes'] = failures_and_passes_summary['TimeToPass'].apply(lambda x: x.total_seconds()/60)
failures_and_passes_summary['retestSuccess?'] = failures_and_passes_summary['TimeToPass_minutes'].apply(lambda x: True if x < retestTime else False)
failures_and_passes_summary['MachineHealth?'] = failures_and_passes_summary['metricName'].apply(lambda x: False if x in NVH_metrics else True)

#create a column to disposition each part based on passingTest? retestSuccess? and machine Health?
failures_and_passes_summary['disposition'] = failures_and_passes_summary.apply(failDisposition, axis = 1)

# %%
dispositionCounts = failures_and_passes_summary.drop_duplicates(subset = 'part')['disposition'].value_counts()

# %%
for index, values in dispositionCounts.iteritems():
    summary[index] = values

# %%
failures_and_passes_summary

# %%
#lookup
df_failures_and_Passes[df_failures_and_Passes['part'] == 'P1025598-01-U-ST18K1062403']

# %%
summary['firstPassTotal'] = summary['FirstPasses'] + summary['DLE'] + summary['Retest Success'] + summary['Machine Health Failure']
summary['fallout'] = summary['Reworked Pass'] + summary['Pending Rework / Unsuccessful Rework']
summary['FPY'] = summary['firstPassTotal'] / (summary['firstPassTotal'] + summary['fallout'])
summary

# %%
#output
failures_and_passes_summary.to_csv('summary.csv')
summary.to_csv('summary.csv', mode = 'a')

# %%
print(summary)
print(failures_and_passes_summary)


