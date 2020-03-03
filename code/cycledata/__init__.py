import csv
import os
import fitparse
import pytz
import re
import xml.etree.ElementTree as et
import pandas as pd
import numpy as np


# takes in a GPX file of an actual ride and outputs a CSV file
# Must have at least latitude, longitude, altitude and time
def convertrideGPX(input,output,fileid):

    error = False
    errorcount = 0
    lasterror = ''
    lines = 0

    tree = et.parse(input)
    root = tree.getroot()
    m = re.match(r'^({.*})', root.tag)
    if m:
        ns = m.group(1)
    else:
        ns = ''

    if root.tag != ns + 'gpx':
        print('Looking for root "gpx", but Unknown root found: ' + root.tag)
        return lines, error, errorcount, lasterror

    metadata = root.find(ns+ 'metadata')
    if not metadata:
        print('Unable to find "gpx.metadata"')
        return lines,error,errorcount,lasterror

    actid = fileid
    tracks = root.find(ns + 'trk')
    if not tracks:
        print('Unable to find "trk" under root')
        return lines, error, errorcount, lasterror

    columnsEstablished = False

    tracksegments = tracks.find(ns + 'trkseg')
    if not tracksegments:
        print('Unable to find "trkseg" under "trk"')
        return lines, error, errorcount, lasterror

    if columnsEstablished:
        fout.write('New Track Segment\n')

    for trackpoint in tracksegments.iter(ns + 'trkpt'):

        #print (trackpoint.get('lat'))

        lines += 1
        rowid = "{:0>7d}".format(lines)
        lasterror = ''

        time = ''
        latitude = ''
        longitude = ''
        distance = ''
        altitude=''
        bpm=''
        cadence=''
        watts=''
        speed = ''
        try:
            time = trackpoint.find(ns + 'time').text.strip()
            time = time.replace('T', ' ')
            time = time.replace('Z', '')
        except:
            time = ''
            error = True
            errorcount += 1
            lasterror += 'time |'
        try:
            latitude = trackpoint.get('lat').strip()
        except:
            latitude = ''
            error = True
            errorcount += 1
            lasterror += 'latitude |'
        try:
            longitude = trackpoint.get('lon').strip()
        except:
            longitude = ''
            error = True
            errorcount += 1
            lasterror += 'longitude |'
        try:
            altitude = trackpoint.find(ns + 'ele').text.strip()
        except:
            altitude = ''
            error = True
            errorcount += 1
            lasterror += 'altitude |'

        #gpx files does not contain a distance field or a speed field
        speed = ''
        distance = ''

        for extension in trackpoint.iter(ns + 'extensions'):
            try:
                watts = extension.find(ns+'power').text.strip()
            except:
                watts = ''
                error = True
                errorcount += 1
                lasterror += 'watts |'

            bpm = ''
            cadence = ''

            for tpextension in extension.iter():
                if tpextension.tag[-2:] == 'hr':
                    bpm = tpextension.text.strip()
                elif tpextension.tag[-3:] == 'cad':
                    cadence = tpextension.text.strip()

        if not columnsEstablished:
            filetype = 'gpx'
            fout = open(output, 'w')
            fout.write(','.join(
                ('FileType','RowId', 'ActivityId', 'Time', 'LatitudeDegrees', 'LongitudeDegrees', 'DistanceMeters',
                 'AltitudeMeters', 'HeartRate', 'Cadence', 'Watts', 'Speed')) + '\n')
            columnsEstablished = True
        fout.write(
            ','.join((filetype,rowid, actid, time, latitude, longitude, distance, altitude, bpm, cadence, watts, speed)) + '\n')

    return lines, error, errorcount, lasterror


# Some of the Garmin TCX files puts whitespace at the start of the file. this function removes the whitespace
def prepTCXfile(inputfolder, inputfile, outputfolder, outputfile):
    file = open(inputfolder + '/' + inputfile, 'r')
    fulltext = file.readlines()
    file.close()

    if fulltext[0][0] == ' ':

        while fulltext[0][0] == ' ':
            fulltext[0] = fulltext[0][1:]

        outfile = open(inputfolder + '/' + inputfile, 'w')
        outfile.writelines(fulltext)

        outfile.close()

    return


# takes in a TCX file and outputs a CSV file
# Must have at least longitude, latitude, altitude and time
def convertrideTCX(input,output,fileid):
    error = False
    errorcount = 0
    lasterror = ''
    lines = 0
    tree = et.parse(input)
    root = tree.getroot()
    m = re.match(r'^({.*})', root.tag)
    if m:
        ns = m.group(1)
    else:
        ns = ''
    if root.tag != ns + 'TrainingCenterDatabase':
        print('Unknown root found: ' + root.tag)
        return
    activities = root.find(ns + 'Activities')
    if not activities:
        activities = root.find(ns + 'Courses')
        if not activities:
            print('Unable to find Activities or Courses under root')
            return
    activity = activities.find(ns + 'Activity')
    if not activity:
        activity = activities.find(ns + 'Course')
        if not activity:
            print('Unable to find Activity or Course under Activities/Courses')
            return
    actid = fileid
    columnsEstablished = False
    for lap in activity.iter(ns + 'Lap'):
        if columnsEstablished:
            fout.write('New Lap\n')
        for track in lap.iter(ns + 'Track'):
            # pdb.set_trace()
            if columnsEstablished:
                fout.write('New Track\n')
            for trackpoint in track.iter(ns + 'Trackpoint'):
                lines += 1
                excludeline = False
                rowid="{:0>7d}".format(lines)
                lasterror = ''
                try:
                    time = trackpoint.find(ns + 'Time').text.strip()
                    time = time.replace('T', ' ')
                    time = time.replace('Z', '')
                except:
                    time = ''
                    error = True
                    errorcount += 1
                    lasterror += 'time |'
                    excludeline = True
                try:
                    latitude = trackpoint.find(ns + 'Position').find(ns + 'LatitudeDegrees').text.strip()
                except:
                    latitude = ''
                    error = True
                    errorcount += 1
                    lasterror += 'latitude |'
                    excludeline = True;
                try:
                    longitude = trackpoint.find(ns + 'Position').find(ns + 'LongitudeDegrees').text.strip()
                except:
                    longitude = ''
                    error = True
                    errorcount += 1
                    lasterror += 'longitude |'
                    excludeline = True
                try:
                    altitude = trackpoint.find(ns + 'AltitudeMeters').text.strip()
                except:
                    altitude = ''
                    error = True
                    errorcount += 1
                    lasterror += 'altitude |'
                    excludeline = True
                try:
                    distance = trackpoint.find(ns + 'DistanceMeters').text.strip()
                except:
                    distance = ''
                    error = True
                    errorcount += 1
                    lasterror += 'distance |'
                try:
                    bpm = trackpoint.find(ns + 'HeartRateBpm').find(ns + 'Value').text.strip()
                except:
                    bpm = ''
                    error = True
                    errorcount += 1
                    lasterror += 'heart |'
                try:
                    cadence = trackpoint.find(ns + 'Cadence').text.strip()
                except:
                    cadence = ''
                    error = True
                    errorcount += 1
                    lasterror += 'cadence |'
                try:
                    watts = ''
                    speed = ''
                    # watts=trackpoint.find(ns+'Extensions').text.strip()
                    for extension in trackpoint.iter(ns + 'Extensions'):
                        for extension2 in extension.iter():
                            if extension2.tag[-5:] == 'Watts':
                                watts = extension2.text.strip()
                            if extension2.tag[-5:] == 'Speed':
                                speed = extension2.text.strip()
                except:
                    watts = ''
                    speed = ''
                    error = True
                    errorcount += 1
                    lasterror += 'speedorpower |'

                if not columnsEstablished:
                    filetype='tcx'
                    fout = open(output, 'w')
                    fout.write(','.join(('FileType','RowId','ActivityId', 'Time', 'LatitudeDegrees', 'LongitudeDegrees', 'DistanceMeters',
                                         'AltitudeMeters', 'HeartRate', 'Cadence', 'Watts', 'Speed')) + '\n')
                    columnsEstablished = True

                if excludeline != True:
                    fout.write(
                        ','.join((filetype,rowid, actid, time, latitude, longitude, distance, altitude, bpm, cadence, watts, speed)) + '\n')

    fout.close()
    return lines, error, errorcount, lasterror

# takes in a FIT file and outputs a CSV file
# must have at least latitude, longitude, altitude and time
def convertrideFIT(fitfile, output_file, fileid):

    # Prepare all the mapping naming conventions and mandaotry elements
    # The following fields appear to available on Garmin FIT files with a Stages Power Meter
    # position_lat position_long  distance  accumulated_power  enhanced_altitude  altitude  enhanced_speed  speed  power
    # heart_rate  cadence  temperature  left_torque_effectiveness  right_torque_effectiveness  left_pedal_smoothness  right_pedal_smoothness

    allowed_fields = ['file_type','row_id', 'activity_id', 'timestamp', 'position_lat', 'position_long', 'distance', 'altitude',
                      'speed', 'heart_rate', 'cadence', 'power','temperature']
    mapped_names = ['FileType','RowId', 'ActivityId', 'Time', 'LatitudeDegrees', 'LongitudeDegrees', 'DistanceMeters',
                    'AltitudeMeters', 'Speed', 'HeartRate', 'Cadence', 'Watts','Temperature']

    required_fields = ['FileType','RowId', 'ActivityId', 'Time', 'LatitudeDegrees', 'LongitudeDegrees', 'AltitudeMeters']

    UTC = pytz.UTC

    linecount = 1
    messages = fitfile.messages
    data = []
    for m in messages:
        skip = False
        if not hasattr(m, 'fields'):
            continue
        fields = m.fields

        # add an activity identity column
        # check for important data types
        mdata = {}
        for field in fields:
            if field.name in allowed_fields:
                fieldname = mapped_names[allowed_fields.index(field.name)]
                if field.name == 'timestamp':
                    timestamp=field.value.strftime('%Y/%m/%d %H:%M:%S')
                    mdata[fieldname] = timestamp
                    mdata['RowId'] = linecount
                    mdata['ActivityId'] =  fileid
                    mdata['FileType'] = 'fit'
                else:
                    #First remove some horribleness with cadence, watts and heartrate, where it is sometimes set to a non-numeric
                    if fieldname == 'Cadence' or fieldname == 'HeartRate':
                        try:
                            fieldval = float(field.value)
                        except:
                            fieldval = np.nan
                        mdata[fieldname] = fieldval
                    else:
                        mdata[fieldname] = field.value
        for rf in required_fields:
            if rf not in mdata:
                skip = True
        if not skip:
            linecount+=1
            data.append(mdata)
    # write to csv
    with open(output_file, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(mapped_names)
        for entry in data:
            writer.writerow([str(entry.get(k, '')) for k in mapped_names])

    return linecount


# Takes an inputfolder and converts all the GPX,FIT and TCX files in the folder to a uniform CSV format
def convertgeofilesbatch(inputpath, outputpath):
    files = os.scandir(inputpath)
    countTcx = 0
    countFit = 0
    countGpx = 0
    results = []
    results.append(['Filename','Outputfile','Linecount','Errorfound','Errorcount','Errortext'])
    print('\n\n .............. Converting GPX/TCX/FIT files to a standardised CSV intermediate format \n\n')
    for file in files:
        inputfilename = file.name
        fileid = '_' + inputfilename[:-4]
        if file.name[-3:].upper() == 'FIT':
            outputfilename = '_fit' + inputfilename[:-3]+'csv'
            cvinput = inputpath + inputfilename
            cvoutput = outputpath + outputfilename
            print('FIT : ',cvinput)
            fitfile = fitparse.FitFile(cvinput, data_processor=fitparse.StandardUnitsDataProcessor())
            lines = convertrideFIT(fitfile, cvoutput,fileid)
            results.append([file.name,outputfilename,lines,'','',''])
        elif file.name[-3:].upper() == 'TCX':
            outputfilename = '/_tcx' + ''.join(file.name)
            countTcx += 1
            prepTCXfile(inputpath, file.name, outputpath, outputfilename)
            cvinput = inputpath + inputfilename
            cvoutput = outputpath + outputfilename[0:-3] + 'csv'
            print('TCX : ',cvinput)
            lines, error, errorcount, lasterror = convertrideTCX(cvinput, cvoutput,fileid)
            results.append([file.name,outputfilename[1:-3] + 'csv', lines, error, errorcount, lasterror])
        elif file.name[-3:].upper() == 'GPX':
            outputfilename = '/_gpx' + ''.join(file.name)
            countGpx += 1
            cvinput = inputpath + inputfilename
            cvoutput = outputpath + outputfilename[0:-3] + 'csv'
            print('GPX : ',cvinput)
            lines, error, errorcount, lasterror = convertrideGPX(cvinput, cvoutput,fileid)
            results.append([file.name,outputfilename[1:-3] + 'csv', lines, error, errorcount, lasterror])

        with open(outputpath+'/'+'___process_report.csv', 'w', newline='') as f:
            writer = csv.writer(f)
            for line in results:
                writer.writerow(line[i] for i in range(0,len(line)))
        f.close()


# Takes a dataframe and adds geographic distance columns to the dataframe
def addgeodistanceindf(df,curlatname,prevlatname,curlongname,prevlongname,curaltname,prevaltname,distxycolname,distxyzcolname):

    earthradius =   6371000  # meter
    latdiff = np.radians(df[curlatname]) - np.radians(df[prevlatname])
    longdiff = np.radians(df[curlongname]) - np.radians(df[prevlongname])
    lat1rad = np.radians(df[curlatname])
    lat2rad = np.radians(df[prevlatname])
    altdiff = df[curaltname]-df[prevaltname]

    a = np.sin(latdiff/2.0)**2 + np.cos(lat1rad)*np.cos(lat2rad)*np.sin(longdiff/2.0)**2
    c = 2*np.arctan2(np.sqrt(a),np.sqrt(1-a))
    d = np.round(earthradius*c,2) # distance in the xy plane
    d3 = np.round(np.sqrt(d*d+altdiff*altdiff),2) #distance in the 3 dimensional plane

    df[distxycolname] = d
    df[distxyzcolname] = d3

    return df

# Takes the raw cycle data and add a few computed columns : xy distance, xyz distance, speed, gradient, elapsed time
# between points and so forth
def addcomputedcycledata(sourcedf,riderweight, bikeweight, crr, rho, cd, fa, exfact,wspeedkph,wdirdeg,fhw,ftw):

    #First add columns that may be missing
    #For now it is only Watts that seems to be missing but in future there may be more
    if 'Watts' not in sourcedf.columns:
        sourcedf['Watts'] = np.nan

    sourcedf[['PrevLat','PrevLong','PrevAlt','PrevTime']] = sourcedf[['LatitudeDegrees','LongitudeDegrees','AltitudeMeters','Time']].shift(periods=1)
    #Calculate all the geo distances

    addgeodistanceindf(sourcedf, curlatname = 'LatitudeDegrees', prevlatname = 'PrevLat', curlongname = 'LongitudeDegrees',
                       prevlongname = 'PrevLong', curaltname = 'AltitudeMeters', prevaltname = 'PrevAlt',
                       distxycolname = 'DistXY', distxyzcolname = 'DistXYZ')

    sourcedf[['PrevLat','PrevLong','PrevAlt','PrevTime']] = sourcedf[['LatitudeDegrees','LongitudeDegrees','AltitudeMeters','Time']].shift(periods=1)

    sourcedf['CumDistXYZ'] = sourcedf.DistXYZ.cumsum()
    sourcedf['Elevation'] = sourcedf['AltitudeMeters'].astype(float)-sourcedf['PrevAlt'].astype(float)
    sourcedf['Direction'] = np.degrees(np.arctan2((sourcedf['LongitudeDegrees'] - sourcedf['PrevLong']),
                                                  (sourcedf['LatitudeDegrees'] - sourcedf['PrevLat']))).apply(lambda x: x if x >= 0 else 360 + x)
    sourcedf['Direction'] = np.round(sourcedf.Direction,0)
    sourcedf['Gradient'] = (sourcedf['Elevation']/sourcedf['DistXY']).apply(lambda x: 0 if x == np.inf else 0 if x == -np.inf else x)
    sourcedf['Gradient'] = np.round(sourcedf.Gradient,3)
    #Make sure that all gradients are set to a number (set to 0 if not a number)
    sourcedf['Gradient']=sourcedf['Gradient'].apply(lambda x: 0 if np.isnan(x) == True else x)

    time = pd.to_datetime(sourcedf['Time']).astype(np.int64)
    prevtime = pd.to_datetime(sourcedf['PrevTime']).astype(np.int64)

    prevtime[0]=time[0]
    starttime = time[0]
    sourcedf['Duration']=(time-prevtime)/1000000000.0
    sourcedf['ElapsedDuration']=(time-starttime)/1000000000.0

    sourcedf['Speedmps']=np.round(sourcedf['DistXYZ'].astype(np.float)/sourcedf['Duration'].astype(np.float),3)

    #Determine the rows that indicate the bike was stationary
    #This is a bit of a hack that seems to work for Garmin
    #It appears that any row where the duration is more than 1 second is a stationary row, but not quite
    #I added the condition that the speed must be below 0.2mps just as an extra safety -
    sourcedf['StationaryDuration']=sourcedf.Duration
    sourcedf.loc[(sourcedf.Duration < 2) | ((sourcedf.Duration >= 2) & (sourcedf.Speedmps > 0.2)),'StationaryDuration']=0
    sourcedf['CumStatDuration'] = sourcedf.StationaryDuration.cumsum()
    sourcedf['CumMoveDuration'] = sourcedf.ElapsedDuration-sourcedf.CumStatDuration

    #Add some calculated cumulative data that is useful in excel
    sourcedf['TotalMeasuredWork']=sourcedf.Watts*sourcedf.Duration
    sourcedf['CumMeasuredWork']=sourcedf.TotalMeasuredWork.cumsum()
    sourcedf['AvCumPower']=np.round(sourcedf.CumMeasuredWork/sourcedf.CumMoveDuration,1)
    sourcedf['AvMoveSpeedkph']=np.round(sourcedf.CumDistXYZ/sourcedf.CumMoveDuration*3.6,1)
    sourcedf['AvOverallSpeedkph']=np.round(sourcedf.CumDistXYZ/sourcedf.ElapsedDuration*3.6,1)


    #Add some stuff that will be very useful to show on map layers in QGIS
    timeh = np.floor(sourcedf.ElapsedDuration / 3600)
    timemin = np.floor((sourcedf.ElapsedDuration - timeh * 3600) / 60)
    timehstr = timeh.apply(lambda x: '{:02d}'.format(int(x)))
    timeminstr = timemin.apply(lambda x: '{:02d}'.format(int(x)))
    timestring = timehstr + ':' + timeminstr
    diststring = sourcedf.CumDistXYZ.apply(lambda x: str(round(x / 1000, 1)) + 'km')
    stoplabel = sourcedf.StationaryDuration.apply(lambda x: '  {:2d}m'.format(int(x / 60)) + '{:02d}s'.format(int(x) - int(x / 60) * 60) + ' stop' if x > 1 else '')
    gpslabel = timestring + '  -  ' + diststring + stoplabel
    sourcedf['gpslabel']=gpslabel
    sourcedf['showgpslabel']=sourcedf.ElapsedDuration.apply(lambda x: 1 if int(x/300) == int(x)/300 else 0)
    sourcedf['showstoplabel']=sourcedf.StationaryDuration.apply(lambda x: 1 if x > 1 else 0)
    sourcedf.loc[(sourcedf.showgpslabel==0) & (sourcedf.showstoplabel == 0),'gpslabel'] = ''
    sourcedf.drop(columns=['showgpslabel','showstoplabel'],inplace=True,axis=1)
    #End of QGIS stuff

    #Calculate the real windspeed based on the basedata in the basedata excel file. This is used to calculate estimated power
    wspeedmps = round(wspeedkph/3.6,3)
    sourcedf['Windspeedmps'] = wspeedmps
    sourcedf['Winddirection'] = wdirdeg
    sourcedf['Relwspeedmps']=np.round((np.cos(np.radians(sourcedf['Direction']-sourcedf['Winddirection']))*sourcedf['Windspeedmps']),3)


    ### Data smoothing, which is sometimes handy

    #The altitude data is particularly spiky - the below will smooth altitude and gradient
    sourcedf['SumDistance10']=sourcedf.DistXYZ.rolling(window=10,min_periods=1).sum()
    sourcedf['SumDuration10'] = sourcedf.Duration.rolling(window=10,min_periods=1).sum()
    sourcedf['smoothalt']=np.round(sourcedf.AltitudeMeters.rolling(window=10,min_periods = 1).mean()*5,0)/5
    sourcedf['SmoothAltitude10']=sourcedf.smoothalt.shift(-5)
    sourcedf['SmoothElevation10']=sourcedf.SmoothAltitude10-sourcedf.SmoothAltitude10.shift(periods=1)
    sourcedf['SmoothGradient10']=np.round(sourcedf.SmoothAltitude10.diff(periods=10)/sourcedf.SumDistance10,3)

    #If the Smoothgradient in a specific row is not a number but elevation and distxy is, then just set the gradient to this particular row's gradient (elevation/distxy)
    sourcedf.loc[(np.isnan(sourcedf['SmoothGradient10'])==True) & (np.isnan(sourcedf['Elevation'])==False) & (np.isnan(sourcedf['DistXY'])==False),'SmoothGradient10']= np.round(sourcedf.Elevation/sourcedf.DistXY,3)

    #Add a small amount of smoothing to the direction as well, not too much because we still need to pick up corners and turns
    sourcedf['SmoothDirection5']=np.round(sourcedf.Direction.rolling(window=5,min_periods=1).mean(),3)
    sourcedf['SmoothSpeed10'] = np.round(sourcedf.SumDistance10/sourcedf.SumDuration10,1)
    sourcedf['TrueRelwspeed10'] = np.round((np.cos(np.radians(sourcedf['SmoothDirection5'] - sourcedf['Winddirection'])) * sourcedf['Windspeedmps']),3)

    #Add some smoothing to the measured powerdata too so that we can track poweroutput intervals a bit more smoothly, especially for the WahooKickr
    sourcedf['SmoothWatts3']=np.round(sourcedf.Watts.rolling(window=3,min_periods=0).mean(),0)


    #Fudge the wind data for head and tail winds - for some reason if you don't fudge it it massively overestimates the power
    #and it does not do it consistently for head and tailwinds. So we adjust the headwind by a factor, obtained from the basedata file
    sourcedf['adjustedforhead'] = sourcedf.TrueRelwspeed10*fhw
    sourcedf['adjustedfortail'] = sourcedf.TrueRelwspeed10*ftw
    sourcedf['usehead'] = (sourcedf.TrueRelwspeed10<0) * 1.0
    sourcedf['usetail'] = (sourcedf.TrueRelwspeed10>=0) * 1.0
    sourcedf['Relwspeed10'] = sourcedf.adjustedforhead*sourcedf.usehead + sourcedf.adjustedfortail*sourcedf.usetail

    #Drop some spurious columns
    sourcedf.drop(columns=['adjustedforhead','adjustedfortail','usehead','usetail'],axis=1,inplace=True)

    #Calculate and smooth the estimated power output - this is a work in progress and can be commented out if not needced
    # for the sake of simplicity, this has been removed from the code, comment at https://github.com/hbuhrmann/readcycledata
    # I have lots of extra goodies to estimate power and to plan a journey, and to do a month by month analysis on your ride data

    #Drop some spurious columns
    sourcedf.drop(
        columns=['PrevLat', 'PrevLong', 'PrevAlt', 'PrevTime','smoothalt'], axis=1, inplace=True)

    return sourcedf

# This function takes a pathname and a list of file names as input, and combines them all
# into a single CSV, with a number of additional calculated fields
def readcyclecsv(pathname,filelist,basedatafile):
    # pathname is a folder name
    # filelist is a list of files in the folder

    if pathname[:-1] != '/':
        pathname+='/'

    # in addition to basic data, the basedata excel file also contains a worksheet called routestops - this is only used when
    # planning a journey and is not relevant here
    basedata = readbasedata(basedatafile)

    filecounter = 0
    cycledata = pd.DataFrame()

    print('\n\n .............. Converting ',len(filelist),' intermediate files into a final single large dataframe \n\n')

    for file in filelist:
        try:
            rawdata = pd.read_csv(pathname+file)
        except Exception as e:
            print(f'{file} something went wrong {e}')
            continue

        #Get all the parameterdata from basedata
        matchfilename = file[4:-4]+'.'+file[1:4]  # this is a hack to get the file name back to the original raw file name, not the name as per the interim folder
        basedataread = True
        basedatamessage = ''
        try:
            params = basedata[basedata.filename == matchfilename].iloc[0]
            targetwatts = params.targetwatts
            temperature = params.temperature
            wspeedkph = params.wspeedkph
            wdirdeg = params.wdirdeg
            airpressure = params.airpressure
            rho = params.rho
            riderweight = params.riderweight
            crr = params.crr
            bike = params.bike
            bikeweight = params.bikeweight
            cd = params.cd
            fa = params.fa
            exfact = params.exfact
            fheadw = params.fheadw
            ftailw = params.ftailw
            filecounter += 1
        except IndexError:
            basedatamessage = matchfilename + ' not found in the basedata file. Default values will be used'
            basedataread = False
            try:
                params = basedata[basedata.filename == 'Generic'].iloc[0]
                targetwatts = params.targetwatts
                temperature = params.temperature
                wspeedkph = params.wspeedkph
                wdirdeg = params.wdirdeg
                airpressure = params.airpressure
                rho = params.rho
                riderweight = params.riderweight
                crr = params.crr
                bike = params.bike
                bikeweight = params.bikeweight
                cd = params.cd
                fa = params.fa
                exfact = params.exfact
                fheadw = params.fheadw
                ftailw = params.ftailw
                filecounter += 1
            except IndexError:
                basedatamessage = matchfilename + ' not found, and default row "Generic" not found either. This file will be skipped'
                print (basedatamessage)
                continue

        #Add calculated fields to the dataframe
        filedata=addcomputedcycledata(rawdata,riderweight, bikeweight, crr, rho, cd, fa, exfact,wspeedkph,wdirdeg,fheadw,ftailw)

        if filecounter == 0 :
            cycledata = filedata.copy(deep=True)
        else:
            cycledata=cycledata.append(filedata,ignore_index=True,sort=False)
        filecounter+=1
        print('Intermediate file added : ',file,len(filedata),'rows      ',basedatamessage)

    return cycledata

#This function returns a CSV file as a dataframe
def getfinalcsvcycledata(filepath,filename):
    rawdata = pd.read_csv(filepath+filename,dtype={'Cadence' : np.float, 'HeartRate' : np.float})
    return rawdata

# Determine runtype - returns Level, Climb or Descend
def runtype(elevation):
    if elevation >= 0.02:
        return 'Climb'
    elif elevation <= -0.02:
        return 'Descend'
    elif elevation < 0.2 and elevation > -0.02:
        return 'Level'

    return 'Not Known'

def addcomputedclimbdata(sourcedf):

    print('\n\n............... Calculating climb data on the full  dataset (for climbs, levels and descends) .........\n\n')

    # Add a column to indicate whether the row is level, climb or descend. This assumes that df.Elevation has already been populated
    sourcedf['RunType'] = sourcedf.SmoothElevation10.apply(runtype)

    #Get rid of single instances sandwiched by the same runtype, eg climb-climb-level-climb must become climb-climb-climb-climb

    sourcedf['nextruntype'] = sourcedf.RunType.shift(-1)
    sourcedf['prevruntype'] = sourcedf.RunType.shift(1)
    sourcedf.loc[(sourcedf.nextruntype == sourcedf.prevruntype) & (sourcedf.RunType == "Level"), 'RunType'] = sourcedf['prevruntype']

    sourcedf['nextruntype'] = sourcedf.RunType.shift(-1)
    sourcedf['prevruntype'] = sourcedf.RunType.shift(1)
    sourcedf.loc[(sourcedf.nextruntype == sourcedf.prevruntype) & (sourcedf.RunType == "Descend"), 'RunType'] = sourcedf['prevruntype']

    sourcedf['nextruntype'] = sourcedf.RunType.shift(-1)
    sourcedf['prevruntype'] = sourcedf.RunType.shift(1)
    sourcedf.loc[(sourcedf.nextruntype == sourcedf.prevruntype) & (sourcedf.RunType == "Climb"), 'RunType'] = sourcedf['prevruntype']

    # Determine run start and run end
    # If the run type of the previous row and the run type of the current row differ, then it signifies a run start
    # or if the activity id is different - we can assume that the RunType value of the first row for a new activity
    # id will always be 'Not Known' so we don't have to write specific logic to pick up new activity id

    sourcedf['prevruntype'] = sourcedf.RunType.shift(1)
    sourcedf['RunStart'] = (sourcedf.RunType != sourcedf.prevruntype) * 1

    sourcedf['nextruntype'] = sourcedf.RunType.shift(-1)
    sourcedf['RunEnd'] = (sourcedf.RunType != sourcedf.nextruntype) * 1

    sourcedf.drop(columns=['prevruntype', 'nextruntype'], axis=1, inplace=True)

    # Calculate run id's
    # The run id will be equivalent to the rowid of the run's starting row
    # Just to make the logic here obvious - because only rows at the start of the run has a value of 1, the rest a value of 0,
    #       cumsum() will allocate the startrow id to all the entries in the same run

    sourcedf['RunId'] = sourcedf.RunStart.cumsum()

    # Now add columns for cumulative distance, duration, etc and cumulative averages by run

    sourcedf[['RunDistXY', 'RunDistXYZ', 'RunElevation', 'RunDuration']] = sourcedf.groupby(['RunId']).cumsum()[
        ['DistXY', 'DistXYZ', 'SmoothElevation10', 'Duration']]

    sourcedf['RunGradient'] = np.round((sourcedf.RunDistXYZ != 0) * sourcedf.RunElevation / sourcedf.RunDistXY,3)
    sourcedf['RunSpeedmps'] = np.round(sourcedf.RunDistXYZ / sourcedf.RunDuration,3)

    sourcedf['pedalstrokes'] = sourcedf.Cadence * sourcedf.Duration / 60
    sourcedf['RunPedalstrokes'] = sourcedf.groupby(['RunId']).cumsum()['pedalstrokes']
    sourcedf['RunCadence'] = np.round(sourcedf.RunPedalstrokes / sourcedf.RunDuration * 60, 1)

    sourcedf.drop(columns=['pedalstrokes'], axis=1, inplace=True)
    sourcedf['RunPedalstrokes'] = np.round(sourcedf.RunPedalstrokes,2)

    sourcedf['RunTotalWatts'] = sourcedf.groupby(['RunId']).cumsum()['Watts']
    sourcedf['RunAvgWatts'] = np.round(sourcedf.RunTotalWatts/sourcedf.RunDuration,2)

    return sourcedf

def readbasedata(filepathandname):
    dtypes = {
        'filename': np.str,
        'ridedate': np.datetime64,
        'temperature': np.float,
        'wspeedkph': np.float,
        'wdirdeg': np.float,
        'airpressure': np.float,
        'rho': np.float,
        'bike': np.str,
        'bikeweight': np.float,
        'riderweight': np.float,
        'cd': np.float,
        'fa': np.float,
        'crr': np.float,
        'exfact': np.float,
        'fheadw': np.float,
        'ftailw': np.float,
        'targetwatts': np.float
    }

    df = pd.read_excel(io=filepathandname, sheet_name = 'basedata', header = 0, dtype = dtypes, parse_dates = ['ridedate'])

    return df
