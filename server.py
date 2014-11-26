#!/usr/bin/python
#
#	Copyright 2012 Michele Filannino
#
#	gnTEAM, School of Computer Science, University of Manchester.
#	All rights reserved. This program and the accompanying materials
#	are made available under the terms of the GNU General Public License.
#	
#	author: Michele Filannino
#	email:  filannim@cs.man.ac.uk
#	
#	This work is part of TempEval-3 challenge.	
#	For details, see www.cs.man.ac.uk/~filannim/

from datetime import datetime
from flask import Flask, render_template, request
from pymongo import MongoClient
import re

from annotate_sentence import annotate

app = Flask("ManTIME")
app.debug = True

def toGoogleChartFormat(tags):
	assert type(tags)==list
	dataRows = []
	now = datetime.now()
	dataRows.append("[\'today\', new Date("+str(now.year)+","+str(now.month-1)+","+str(now.day)+",0,0), new Date("+str(now.year)+","+str(now.month-1)+","+str(now.day)+",23,59)]")

	for tag in tags:
		# Only dates and times are visualised
		id, timex_type, timex_value = tag
		# DATE
		if timex_type == 'DATE':
			
			m = re.match(r'^(?P<year>\d{4})\-(?P<month>\d{2})\-(?P<day>\d{2})$', timex_value)
			if m:
				start = ','.join([m.group('year'),str(int(m.group('month'))-1),m.group('day'),'0','0'])
				end = ','.join([m.group('year'),str(int(m.group('month'))-1),m.group('day'),'23','59'])
			
			m = re.match(r'^(?P<year>\d{4})\-(?P<month>\d{2})\-XX$', timex_value), re.match(r'^(?P<year>\d{4})\-(?P<month>\d{2})$', timex_value)
			if any(m):
				m = m[0] if m[0] else m[1]
				start = ','.join([m.group('year'),str(int(m.group('month'))-1),'1'])
				year, month = int(m.group('year')), int(m.group('month'))
				if month in (1,3,5,7,8,10,12):
					end = ','.join([m.group('year'),str(month-1),'31'])
				elif month in (4,6,9,11):
					end = ','.join([m.group('year'),str(month-1),'30'])
				else:
					if (year%400==0 or (year%100!=0 and year%4==0)):
						end = ','.join([m.group('year'),str(month-1),'29'])
					else:
						end = ','.join([m.group('year'),str(month-1),'28'])
			
			m = re.match(r'^(?P<year>\d{4})\-XX\-XX$', timex_value), re.match(r'^(?P<year>\d{4})$', timex_value)
			if any(m):
				m = m[0] if m[0] else m[1]
				start = ','.join([m.group('year'),'0','1'])
				end = ','.join([m.group('year'),'11','31'])
			dataRows.append("[\'t"+str(tag[0])+"\', new Date("+start+"), new Date("+end+")]")
		if timex_type=='TIME':
			print 'TIME'
	return ','.join(dataRows), 52*len(dataRows)+40

@app.route('/', methods=['POST'])
def index():
	now = datetime.now()
	month = str(now.month) if len(str(now.month))==2 else '0'+str(now.month)
	day = str(now.day) if len(str(now.day))==2 else '0'+str(now.day)
	utterance = '/'.join([day, month, str(now.year)])
	utterance_code = ''.join([str(now.year), month, day])
	sentence = request.form['sentence']
	sentence = re.sub(r'[^\x00-\x7F]+',' ', sentence)
	sentence = sentence.decode('ascii', 'xmlcharrefreplace').replace('<',' ').replace('>',' ')
	#sentence = unicode(sentence).decode('ascii', 'xmlcharrefreplace')
	result, tags = annotate(sentence, utterance_code)
	print sentence, result, tags
	tags, height = toGoogleChartFormat(tags)
	print tags
	return render_template('result.html', sentence=sentence, result=result, utterance=utterance, tags=tags, height=height)

@app.route('/api', methods=['POST'])
def api():
	now = datetime.now()
	month = str(now.month) if len(str(now.month))==2 else '0'+str(now.month)
	day = str(now.day) if len(str(now.day))==2 else '0'+str(now.day)
	utterance = '/'.join([day, month, str(now.year)])
	text = request.form['text']
	text = unicode(text, errors="ignore").encode('ascii', 'xmlcharrefreplace')
	result = annotate(text)
	print 'API used!\n', text
	return result

@app.route('/send_feedback', methods=['POST'])
def send_feedback():
	data = {'sentence': request.form['sentence'],
			'annotation': request.form['result'],
			'utterance': request.form['utterance'],
			'feedback': request.form['feedback']}
	conn = MongoClient()
	db = conn['ManTIME']
	table = db['feedback_online']
	table.insert(data)
	print request.form['feedback'] + ' feedback stored!'
	return render_template('result.html', sentence=request.form['sentence'], result=request.form['result'], utterance=request.form['utterance'])

app.run(host="130.88.192.69", port=4001, use_reloader=True)
#app.run(host="0.0.0.0", port=4001, use_reloader=False)
