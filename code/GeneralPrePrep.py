import cycledata as cycle
import os
from datetime import datetime as dt

####################################################################################
# FIRST SET SOME ENVIRONMENTAL STUFF
# BASICS : (1) Put all your raw gpx/fit/tcx files into a folder by themselves (....Raw)
#          (2) Run some code to convert all raw files to a consistent .csv format and put these into (..... Intermediate)
#                   cycle.convertgeofilesbatch(rawfolder,intermediatefolder)
#          (3) Run some code that returns a single DataFrame with a whole bunch of processed data
# Suggested folder structure :
#  .....yourcycledatapath/
#  .....yourcycledatapath/BaseData
#  .....yourcycledatapath/Raw
#  .....yourcycledatapath/Intermediate
#  .....yourcycledatapath/Final
#####################################################################################

targetfolder = 'C:/Users/hanne/PycharmProjects/readcycledatafiles/Datafiles/'

rawfolder = targetfolder+'Raw/'
interfolder = targetfolder+'Intermediate/'
finalfolder = targetfolder+'Final/'


basedatafile = 'C:/Users/hanne/PycharmProjects/readcycledatafiles/Datafiles/BaseData/basedata.xlsx'

###########################################################################################
# TAKE ALL THE GPX,TCX and FIT source files and convert them to individual CSV files
# WITH A CONSISTENT FORMAT AND A CONVERSION REPORT
# At this stage we don't add any data to the source files, we just get it in a consistent
# easy to read tabular format. You will find all these files in your "intermediate" folder
###########################################################################################

cycle.convertgeofilesbatch(rawfolder,interfolder)

######################################################################################
# Now, from the consistently formatted intermediate CSV files, we create one large
# csv file with a whole bunch of additional data :
#     - Smoothed data
#     - "Runs" - periods of consecutive ascent, descent or flat with associated data
#     - Estimated power calculations
#     - Some useful additional fields, e.g. direction of travel, etc
# Please note the estimated power calculations requires a "basedata" excel file, an example
# of which has been included in the repository. This contains additional data (e.g. bicycle,
# wind direction and strength, etc). Each input file requires one row in the excel spreadsheet
# but even if the row does not exist, the algorithm will use default values to calculate estimated
# power
#####################################################################################################
## Specify 'folder' if you want all the csv files in the folder to be processed
## Specify 'files' if you want to specify a list of individual files in the folder to be processed
#####################################################################################################

targetfiles = 'folder'   # 'folder' or 'files'
filelist = []

print('\n\n................ Reading the intermediate folder .... REMEMBER to empty this folder from time to time')

if targetfiles == 'files' :
    filelist = [
    '_fitfile1.csv',
    '_gpxfile1.csv',
    '_tcxfile1.csv',
    '_etcetera'
    ]
elif targetfiles == 'folder':
    files = os.scandir(interfolder)
    filelist = []
    for file in files:
        filename = file.name
        prefix = filename[0:4]
        if prefix == '_gpx' or prefix == '_tcx' or prefix == '_fit':
            filelist.append(filename)

## Now run the function that will return a single DataFrame with gazzillions of extra calculated data
cycledf = cycle.readcyclecsv(interfolder, filelist,basedatafile)

## And now you can write this to a CSV file with whatever naming convention you choose
## this should be relatively easy to change to write to a database
if len(cycledf) > 0 :
    cycledf2 = cycle.addcomputedclimbdata(cycledf)
    print('................ Writing final files ')
    now=dt.now()
    filename='_fin_'+now.strftime('%Y-%m-%d %Hh%Mm%S')+'.csv'
    cycledf2.to_csv(finalfolder+filename,index_label='index')

else :
    print('\n-----##### NOTHING TO PROCESS #####-----\n')