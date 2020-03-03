# readcycledata
Read GPX TCX and FIT cycling files (from Garmin or Strava) and convert to a single flat CSV format

# Overview
Created by a NONcoder obsessed with cycling data

The proposition is simple : Take cycling data files from Strava or a Garmin in a variety of formats, and create flat CSV files with a consistent format for each of the input files. 

This will allow you to manipulate the data in excel or write it to a database

## Extra stuff
Not included in this repository because it is not particularly readable or userfriendly at the moment, but I have also code that
1. Estimate power for any given ride
2. Estimate splits for a planned ride with a given average power input like BestBikeSplit.com (very useful for planning sportives)
3. Do monthly cycling analysis, e.g. number of 30/60/120 second intervals in specific heartrate or power training zones

If you are intersested in any of these message me or email me at hannesbuhrmann@gmail.com

## Special thanks
To https://github.com/dtcooper/python-fitparse for his fitparse library - i would have given up on fit files without this

# Instructions
## Dependencies
csv, os, fitparse (included in here but best to download from above link), pytz, re, xml.etree.ElementTree, pandas, numpy

## How to start
I will describe to you how I do it with PyCharm, there are probably loads of other ways to do it:

1. Import repository as a PyCharm project
2. Open ../scripts/GeneralPrep.py
3. Update your datafolder as described in GeneralPrep.py - initially you can point these to the included ../Datafiles/ folders on your local version

4. Load your raw cycling data into the "Raw" folder (and make sure that the "Intermediate" folder is clean). I have put some sample files into the raw folder already, they are guaranteed to work (well at least they do for me)
5. Run the GeneralPrep.py script
6. Use Excel or something to inspect the files in the Intermediate and Final folders

## Caveat
Nothing in here is super robust - if it breaks you can ask me, but please try and fix it yourself first .....

