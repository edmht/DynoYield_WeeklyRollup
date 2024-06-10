
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np


#variables

#if a test has 46 metricispass, it's a first time pass
mip_fpy_count = 46
golden_units = ['P1025598-00-U:ST13D0013400', 'P1025598-00-U:ST17A1021978']
retestTime = 20

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
						'Output Gear Clicking Positive']



#Import
df_raw = pd.read_csv('datasets\Week23_DynoSummary.csv')
df = df_raw.copy()


#Summary
summary = pd.Series({'FirstPasses':0,
                     'DLE':0,
                           'Retest Success':0,
                           'ReworkedPasses':0,
                           'Pending Rework / Unsuccessful Rework':0,
                           'Machine Health':0
                           })

#dropping Golden units
df = df[~df['FX_Thing'].isin(golden_units)]

#giving key
df['thing+metricName'] = df['FX_Thing']+'+'+df['metricName']

#converting Datetime
df['testTime'] = pd.to_datetime(df['testTime'])




#Finding all the first time passes. Every unit with 46 metricispass sum is a first time pass
sum_metricispass = df.groupby('FX_Thing')['metricispass'].sum()
firstPasses = sum_metricispass[sum_metricispass == mip_fpy_count].reset_index()['FX_Thing']
summary['FirstPasses'] = len(firstPasses)


#getting all the failures and the unique failing serials
df_allFailures = df[df['metricispass'] == 0].copy()

#count of unique failures
failing_serials = df_allFailures['FX_Thing'].drop_duplicates()


#anything with only passes, but looks like it has an interrupted run, is a DLE
DLEs = df['FX_Thing'].nunique() - len(firstPasses) - len(failing_serials)
summary['DLE'] = DLEs


#viewing the DLEs
uniqueSerials = df.drop_duplicates(subset = 'FX_Thing')
uniqueSerials[(~uniqueSerials['FX_Thing'].isin(failing_serials)) & (~uniqueSerials['FX_Thing'].isin(firstPasses))]



#lookup from df all the failing thing+metricNames
df_failures_and_Passes = df[df['thing+metricName'].isin(df_allFailures['thing+metricName'].unique())]

#summarizing parts and metricNames
failures_and_passes_summary = df_failures_and_Passes.drop_duplicates(['part', 'metricName'])[['part', 'metricName', 'thing+metricName']]
failures_and_passes_summary 


#is there a passing test afterwards?
def isPassTest(part):
    df_tmp = df_failures_and_Passes[(df_failures_and_Passes['part'] == part) & (df_failures_and_Passes['isTestPass'] == 1)]
    if df_tmp.shape[0] == 0:
        return False
    else:
        return True
failures_and_passes_summary['PassingTest?'] = failures_and_passes_summary['part'].apply(isPassTest) #applied to DF

#calculate the time between the tests
def calculateTime(part): #If there is a successful rework, find the time between the latest success and the latest failure
    df_test = df_failures_and_Passes[df_failures_and_Passes['part'] == part].drop_duplicates(['testID', 'isTestPass']).reset_index()
    if 1 in df_test['isTestPass'].values:
        passingLoc = df_test[df_test['isTestPass'] == 1].index
        comparison_result = df_test.loc[passingLoc[0], 'testTime'] - df_test.loc[passingLoc[0] - 1, 'testTime']
        return comparison_result
    else: return np.nan
failures_and_passes_summary['TimeToPass'] = failures_and_passes_summary['part'].apply(calculateTime)

#need to find out how many of these also have a pass

def isPass(thingmetricName):
    #checks if there is a pass for that thing+metricName
    df_tmp = df_failures_and_Passes[(df_failures_and_Passes['thing+metricName'] == thingmetricName) & (df_failures_and_Passes['metricispass'] == 1)]
    if df_tmp.shape[0] == 0:
        return False
    else:
        return True
failures_and_passes_summary['PassingTest?'] = failures_and_passes_summary['thing+metricName'].apply(isPass) #PassingTest? will show if there was a passing test after the initial failure



#if a part only has a single metric failure

#if a part has multiple metric failures




