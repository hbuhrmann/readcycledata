import re
import sys
import argparse
import string
import pdb
import sourcetocsv as cy
import xml.etree.ElementTree as et


# takes in a TCX file and outputs a CSV file
def convertTCX (input, output):

	tree = et.parse(input)
	root = tree.getroot()
	m=re.match(r'^({.*})', root.tag)
	if m:
		ns=m.group(1)
	else:
		ns=''
	if root.tag!=ns+'TrainingCenterDatabase':
		print('Unknown root found: '+root.tag)
		return
	activities=root.find(ns+'Activities')
	if not activities:
		print('Unable to find Activities under root')
		return
	activity=activities.find(ns+'Activity')
	if not activity:
		print('Unable to find Activity under Activities')
		return
	try:
		id=activity.find(ns+'Id').text.strip()
		stripped=re.findall('\d', id)
		actid='_'+''.join(stripped)
	except:
		actid=''
	columnsEstablished=False
	for lap in activity.iter(ns+'Lap'):
		if columnsEstablished:
			fout.write('New Lap\n')
		for track in lap.iter(ns+'Track'):
			#pdb.set_trace()
			if columnsEstablished:
				fout.write('New Track\n')
			for trackpoint in track.iter(ns+'Trackpoint'):
				try:
					time=trackpoint.find(ns+'Time').text.strip()
					time=time.replace('T',' ')
					time=time.replace('Z','')
					print (time)
				except:
					time=''
				try:
					latitude=trackpoint.find(ns+'Position').find(ns+'LatitudeDegrees').text.strip()
				except:
					latitude=''
				try:
					longitude=trackpoint.find(ns+'Position').find(ns+'LongitudeDegrees').text.strip()
				except:
					longitude=''
				try:
					altitude=trackpoint.find(ns+'AltitudeMeters').text.strip()
				except:
					altitude=''
				try:
					distance=trackpoint.find(ns+'DistanceMeters').text.strip()
				except:
					distance='err'
				try:
					bpm=trackpoint.find(ns+'HeartRateBpm').find(ns+'Value').text.strip()
				except:
					bpm=''
				try:
					cadence=trackpoint.find(ns+'Cadence').text.strip()
				except:
					cadence=''
				try:
					watts='ph'
					speed='ph'
					#watts=trackpoint.find(ns+'Extensions').text.strip()
					for extension in trackpoint.iter(ns+'Extensions'):
						for extension2 in extension.iter():
							if extension2.tag[-5:] == 'Watts':
								watts=extension2.text.strip()
							if extension2.tag[-5:] == 'Speed':
								speed=extension2.text.strip()
				except:
					watts='err'
					speed='err'
				if not columnsEstablished:
					fout=open(output, 'w')
					fout.write(','.join(('ActivityId','Time','LatitudeDegrees','LongitudeDegrees','DistanceMeters','AltitudeMeters','Heartrate','Cadence','Watts','Speed'))+'\n')
					columnsEstablished=True
				fout.write(','.join((actid,time,latitude,longitude,distance,altitude,bpm,cadence,watts,speed))+'\n')

	fout.close()

