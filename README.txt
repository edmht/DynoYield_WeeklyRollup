# To find dyno performance

#Intention is to automate the dyno first pass yield calculation for Service Weekly Rollup
Need to find non-tester related first pass yield. In other words, need to find

First Passes
Retries
Sucessful reworks
Unsuccessful / Pending reworks
DLEs


## Count unique Serials
This is the total number of units tested

## Find unique failures
How many unique serials with metricispass = 0

## Out of these serial failures, how many of them passed within the threshold time?
Compare the failing metric to the next occurance of the passing metric
Is it within the threshold time? If so, it's a retest pass. If not, it's a rework pass
If there's no next passing metric? True Failure, pending rework

## How to do?
How can unique runs be differentiated? Is there a way to assign an identifier for each test?
How can we identify a full run?
\
Group the runs per df['metricName'] and compare the times between the runs. 
If metricispass = 1 > metricispass = 0, < retestWindow_min = 15 min: It's a retest
If metricispass = 1 > metricispass = 0, > retestWindow_min = 15 min: It's a rework
If metricispass = 0 doesn't exist: Pending successful rework
Would need to account for breaks and lunches for retestWindow_min. Refer to the excel sheet you made for the megapack harrness guys
