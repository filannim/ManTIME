#!/usr/bin/python
#
#	Copyright 2012 Michele Filannino
#	
#	gnTEAM, School of Computer Science, University of Manchester.
#	All rights reserved. This program and the accompanying materials
#	are made available under the terms of the GNU General Public License.
#	
#	authors: Michele Filannino
#	email:  filannim@cs.man.ac.uk
#	
#	This work is part of 2012 i2b2 challenge.	
#	For details, see www.cs.man.ac.uk/~filannim/

"""TempExp normaliser is a piece of software that provide the TimeML type and
   value attributes for each temporal expression given in input.
   This work is an extension of TRIOS normaliser. See the next comment.
   For details, see www.cs.man.ac.uk/~filannim/

   This program takes a temporal expression and returns the normalised type,
   value and modifier according to i2b2 2012 scheme (derived from TimeML). 

   This is a regular expression-based normalisation system, developed in occasions
   of i2b2 2012 challenge on clinical data.

   Usage:
   call the function normalise with your "temporal expression" and proper
   "utterance time" as parameters. 

   To see the sample output, run: 
   >> python clinical_norMA.py 

   Output format: 
	the fuction outputs a tuple, e.g. 
	('about last friday', 'DATE', '2010-01-22', 'DOW', 'APPROX')
	the first entry is the temporal expression as it is processed, next entry is 
	TYPE (DATE, TIME, FREQUENCY, DURATION) according to i2b2 temporal annotation
	scheme (2012), the next entry is normalised VALUE according to ISO-8601, the
	next one is used for debugging and show the name of the fired rule and the
	last one refers to the MOD attribute (START, END, APPROX).

Developed by:
	Michele Filannino (filannim AT cs.manchester.ac.uk)

Feel free to contact for any help. :)
"""


from __future__ import division
import re
import os
import sys
import calendar
import commands 
import math
from datetime import date
from date_utility import date_utility as dt_util
from date_utility import numbers
from date_utility import ordinals
from datetime import date as datex
from datetime import timedelta

##################################################################
############			PROCESS TIMEX VALUE			###########
#
### DATE RELATED FUNCTIONS #### 
#
# usage
# generate_week_range(1998) to get week range for a particular year, 
# specifically the CREATION DATE 
# day_of_week(day, month, year) to get the day (Sunday, Monday, ..) for a 
# specific date 
# get_dows_date_from_date('Sunday', 31, 12, 2009, 'next')
# get_dows_date_from_date('Sunday', 26, 1, 2010, 'prev') 

dow = {} 
dow[0] = "sunday"
dow[1] = "monday"
dow[2] = "tuesday"
dow[3] = "wednesday"
dow[4] = "thursday"
dow[5] = "friday"
dow[6] = "saturday"
dow_reverse = {} 
dow_reverse["sunday"] = 0
dow_reverse["monday"] = 1
dow_reverse["tuesday"] = 2
dow_reverse["wednesday"] = 3
dow_reverse["thursday"] = 4
dow_reverse["friday"] = 5
dow_reverse["saturday"] = 6
days_in_month = {}

def get_today():
	today = datex.today()
	return today.year, today.month, today.day

def day_of_week(day, month, year): 
	a = math.floor((14-month)/12) 
	y = year - a 
	m = month + 12 * a - 2 
	d = (day + y + math.floor(y / 4) - math.floor(y / 100) +
		math.floor(y / 400) + math.floor((31 * m) / 12))  % 7
	return int(d)  

def isleapyear(year): 
	year = int(year) 
	if 0 == year % 4 and (0 != year % 100 or 0 == year % 400): 
		return 'true' 
	return 'false'

def init_days_in_month(year): 
	days_in_month = {} 
	days_in_month[1] = 31 # jan 
	if isleapyear(year) == 'true': 
		days_in_month[2] = 30
	else:
		days_in_month[2] = 29 
	days_in_month[3] = 31 # mar
	days_in_month[4] = 30 # apr
	days_in_month[5] = 31 # may 
	days_in_month[6] = 30 # jun
	days_in_month[7] = 31 # jul
	days_in_month[8] = 31 # aug 
	days_in_month[9] = 30 # sep 
	days_in_month[10] = 31 # oct 
	days_in_month[11] = 30 # nov
	days_in_month[12] = 31 # dec
	return days_in_month 

def get_string_range_numbers(start, stop, with_zeros=False):
	values = '('
	if start > stop:
		temp = start
		start = stop
		stop = temp
	if with_zeros:
		if start < 10 and stop < 10:
			values += '|'.join(['0'+str(n) for n in range(start,stop+1)]) + '|'
		elif start < 10 and stop >= 10:
			values += '|'.join(['0'+str(n) for n in range(start,10)]) + '|'
	values += '|'.join([str(n) for n in range(start,stop+1)]) 
	values += ')'
	return values
 
def init_month_start_end(year): 
	days_in_month = init_days_in_month(year)
	month_start_end = {} 
	month_start_end[0] = 0, 0 
	for i in range(1, 13): 
		a = month_start_end[i-1][1] + 1
		b = month_start_end[i-1][1] + days_in_month[i]
		month_start_end[i] = a, b 
	  #  print month_start_end[i]
	return month_start_end 

def get_week_range(index, month_start_end, days_in_month, year):	 
	start_month = 0
	end_month = 0
	# print 'index', str(index) 
	found_s = 'f' 
	found_e = 'f' 
	for i in range(1, 13): 
	#print 'm_s', month_start_end[i][0]
	#print 'm_e', month_start_end[i][1]
		if index >= month_start_end[i][0]: 
			if found_s == 'f': 
				start_month = i 
				#print 's', str(start_month)
		else: 
			found_s = 't' 
			#break 
		if index + 7 >= month_start_end[i-1][1]:
			if found_e == 'f':
				end_month = i 
			   # print 'e', str(end_month) 
		else:
			found_e = 't' 
			#break 
	start_date = (index - month_start_end[start_month][0] + 1) 
	end_date = (start_date + 7 - 1) % days_in_month[start_month]
	a = str(year) + '-' + get_date_str(start_month)+'-'+get_date_str(start_date) 
	b = str(year) + '-' + get_date_str(end_month)+'-'+get_date_str(end_date) 
	return a, b

def get_date_str(foo): 
	if foo < 10: 
		return '0'+str(foo) 
	return str(foo)

def generate_week_range(year):
	month_start_end = init_month_start_end(year) 
	days_in_month = init_days_in_month(year) 
	week_range = {} 
	for i in range(1, 54):
		#print i
		index = i * 7 - 6
		week_range[i] = get_week_range(index, month_start_end, days_in_month, year) 
 #	   print 'w:'+str(i), week_range[i]
	week_range[53] = week_range[53][0], str(year)+'-12-31'
 #   print 'w:53', week_range[53]
	return week_range 

#generate_week_range(1998) 

def get_year(date): 
	foo = date.split('-')[0] 

def get_one_week_range(week_date): 
	year = week_date.split('-')[0]
	#print year 
	week_range = generate_week_range(year)
	#week = re.sub('W', '', week_date.split('-')[1])
	for week in week_range: 
		start = week_range[week][0]
		end = week_range[week][1]
		if week_date >= start and week_date <= end: 
			#print 'INDEX: ', week
			return week
	return 0 

def add_date(day, month, year, diff): 
	#print diff
	days_in_month = init_days_in_month(year) 
	new_day = day + diff 
	#print new_day
	new_month = month 
	if new_day < 1: 
		if month == 1: 
			days_in_month_prev = init_days_in_month(year-1) 
			new_day = days_in_month[12] + new_day 
			new_month = 12 
		else: 
			new_day = days_in_month[month-1] + new_day 
			new_month = month - 1 
	elif new_day > days_in_month[month]: 
		new_day = new_day - days_in_month[month] 
		new_month = month + 1 
	new_year = year 
	if new_month < 1: 
		new_month = 12
		new_year = year - 1 
	elif new_month > 12: 
		new_month = 1 
		new_year = year + 1 
	new_year = str(new_year)
	new_month = str(new_month)
	if len(new_month) == 1: 
		new_month = '0'+new_month 
	new_day = str(new_day)
	if len(new_day) == 1: 
		new_day = '0'+new_day 
	return new_year+'-'+new_month+'-'+new_day 

## given a date (jan 26), it will calculate the next/prev DOW (Sunday)'s date 

def get_dows_date_from_date(dow, day, month, year, next_or_prev): 
	dow_of_date = day_of_week(day, month, year)
	#print 'dow_of_date:', dow_of_date 
	dow_reverse_foo = dow_reverse[dow] 
	#print 'dow_reverse_foo:', dow_reverse_foo 
	if next_or_prev == 'prev': 
		if dow_of_date >= dow_reverse_foo: 
			diff = dow_of_date - dow_reverse_foo 
		else: 
			diff = dow_of_date - dow_reverse_foo + 7 
		val = add_date(day, month, year, diff*-1)
	elif next_or_prev == 'next': 
		if dow_reverse_foo > dow_of_date: 
			diff = dow_reverse_foo - dow_of_date 
		else: 
			diff = dow_reverse_foo - dow_of_date + 7 
		val = add_date(day, month, year, diff)
		#print '#$$#', val
	return val 

#
#print get_dows_date_from_date('Sunday', 1, 3, 1998, 'prev')
  
def get_number(word): 
	#print '$', word, '$' 
	if word == 'one' or word == 'a': 
		return 1
	elif word == 'two' or word == 'couple': 
		return 2 
	elif word == 'three': 
		return 3
	elif word == 'four': 
		return 4 
	elif word == 'five': 
		return 5 
	elif word == 'six': 
		return 6 
	elif word == 'seven': 
		return 7 
	elif word == 'eight': 
		return 8 
	elif word == 'nine': 
		return 9 
	elif word == 'ten': 
		return 10 
	elif word == 'eleven': 
		return 11 
	elif word == 'tweleve': 
		return 12 
	elif word == 'thirteen': 
		return 13 
	elif word == 'fourteen': 
		return 14 
	elif word == 'fifteen': 
		return 15 
	elif word == 'sixteen': 
		return 16
	elif word == 'seventeen': 
		return 17 
	elif word == 'eighteen': 
		return 18 
	elif word == 'nineteen': 
		return 19 
	elif word == 'twenty': 
		return 20 
	elif word == 'thirty': 
		return 30
	elif word == 'forty': 
		return 40 
	elif word == 'fifty': 
		return 50 
	elif word == 'sixty':
		return 60 
	elif word == 'seventy': 
		return 70 
	elif word == 'eighty': 
		return 80 
	elif word == 'ninety': 
		return 90 
	elif re.search('hundred', word): 
		return 100 
	elif re.search('thousand', word): 
		return 1000 
	else: 
		return 0 

def get_month(month): 
	month = month.upper() 
	if month == 'JANUARY' or month == 'JAN' : 
		return '01' 
	elif month == 'FEBRUARY' or month == 'FEB': 
		return '02' 
	elif month == 'MARCH' or month == 'MAR': 
		return '03' 
	elif month == 'APRIL' or month == 'APR':
		return '04' 
	elif month == 'MAY' or month == 'MAY': 
		return '05' 
	elif month == 'JUNE' or month == 'JUN': 
		return '06' 
	elif month == 'JULY' or month == 'JUL': 
		return '07' 
	elif month == 'AUGUST' or month == 'AUG': 
		return '08' 
	elif month == 'SEPTEMBER' or month == 'SEP': 
		return '09' 
	elif month == 'OCTOBER' or month == 'OCT': 
		return '10' 
	elif month == 'NOVEMBER' or month == 'NOV': 
		return '11' 
	elif month == 'DECEMBER' or month == 'DEC': 
		return '12' 
	else: 
		return '00' 

def find_cons_in_string(cons, string): 
	for word in cons.split(' '): 
	   	#print 'compare:', word, string
		if re.search(word.strip(), string.strip()):
			return word 
	return 'NONE' 

def remove_punctuation(word): 
	word = re.sub('\.', '', word) 
	word = re.sub('\,', '', word) 
	return word 
				  
def pad_zero(word): 
	word = str(word) 
	if len(word) == 1: 
		word = '0'+word 
	return word 

def get_date_value(year, month, day): 
	year = str(year) 
	month = str(month) 
	day = str(day) 
	month = pad_zero(month) 
	day = pad_zero(day)	 
	if int(month) > 12:
		value = str(year) + '-' + str(day) + '-' + str(month)
	else:
		value = str(year) + '-' + str(month) + '-' + str(day)
	return value 
   
def get_datetime_value(year, month, day, hour, minutes, seconds=''):
	value = get_date_value(year, month, day)
	value += 'T' + str(hour) + ':' + str(minutes)
	if seconds:
		value  += ':' + str(seconds)
	return value

def pad_space(word): 
	return ' ' + word + ' ' 

def get_timex_value(cons, date): 
	timex_str = cons
	#remove a, the, -, in  
	cons = ' ' + cons.lower() + ' '	 
	cons = re.sub(' - ', ' ', cons) 
	cons = re.sub(' a ', ' ', cons) 
	cons = re.sub(' the ', ' ', cons) 
	cons = cons.strip() 
	year = int(date[0])
	month = int(date[1])
	day = int(date[2])
	value = 'NONE' 
	type = 'DATE'	# for statistical reasons
	## handle DCT ## 
	year_re = '[12][0-9][0-9][0-9]'
	month_re = '[01][0-9]'
	day_re = '[0123][0-9]'
	hour_re = '[012][0-9]'
	minute_re = '[0123456][0-9]'
	
	# Handle "yyyymmdd"
	p = re.compile(year_re+month_re+day_re)
	if p.search(cons):
		val = cons.strip()  
		yr = val[0:4]
		mn = val[4:6]
		dt = val[6:8]
		value = get_date_value(yr, mn, dt)
		type = 'DATE' 
		return timex_str, type, value, 'DCT1mic'
	
	# Handle "mm/dd/yyyy hh:mm:ss"
	p = re.compile(month_re+'/'+day_re+'/'+year_re +' '+hour_re+':'+minute_re+':'+minute_re) 
	if p.search(cons): 
		val = p.findall(cons)[0] 
		mn = val[0:2]
		dt = val[3:5]
		yr = val[6:10]
		hr = val[11:13]
		min = val[14:16] 
		sec = val[17:19] 
		value = get_date_value(yr, mn, dt)+'T'+str(hr)+':'+str(min)+':'+str(sec)
		type = 'TIME'
		return timex_str, type, value, 'DCT2'

	# Handle "mm/dd/yyyy"
	p = re.compile(month_re+'/'+day_re+'/'+year_re) 
	if p.search(cons): 
		val = p.findall(cons)[0] 
		mn = val[0:2]
		dt = val[3:5]
		yr = val[6:10]
		value = get_date_value(yr, mn, dt)
		type = 'DATE' 
		return timex_str, type, value, 'DCT3'

	# Handle "mm/dd/yy"
	p = re.compile(month_re+'/'+day_re+'/[0-9][0-9]')
	if p.search(cons):
		val = p.findall(cons)[0] 
		mn = val[0:2]
		dt = val[3:5]
		yr = val[6:8]
		if int(yr) > 50:
		 	yr = '19'+str(yr)
		else:
			yr = '20'+str(yr)
		value = get_date_value(yr, mn, dt)
		type = 'DATE' 
		return timex_str, type, value, 'DCT4'
	
	# Handle "mm-dd-yy hhmmX...X OR mm/dd/yy hhmmX...X"
	p = re.compile(month_re+'[-|/]'+day_re+'[-|/][0-9]{2} [0-9]{4}[a-z]*')
	if p.search(cons): 
		val = p.findall(cons)[0] 
		mn = val[0:2]
		dt = val[3:5]
		yr = str(year)[:-2] + val[6:8]
		hh = val[9:11]
		mi = val[11:13]
		value = get_datetime_value(yr, dt, mn, hh, mi)
		type = 'DATE'
		return timex_str, type, value, 'mic2'

	# Handle "mm-dd-yy hhmmssX...X OR mm/dd/yy hhmmssX...X"
	p = re.compile(month_re+'[-|/]'+day_re+'[-|/][0-9]{2} [0-9]{6}[a-z]*')
	if p.search(cons): 
		val = p.findall(cons)[0] 
		mn = val[0:2]
		dt = val[3:5]
		yr = str(year)[:-2] + val[6:8]
		hh = val[9:11]
		mi = val[11:13]
		se = val[13:15]
		value = get_datetime_value(yr, dt, mn, hh, mi, se)
		type = 'DATE'
		return timex_str, type, value, 'mic3'
	
	# Handle "yyyy-mm-dd"
	p = re.findall('([0-9]{4})[-|/]([0-9][0-9]?)[-|/]([0-9][0-9]?)',cons)
	if p:
		x = list(p[0])
		if int(x[1])>12:
			mn = x[2]
			dt = x[1]
		else:
			mn = x[1]
			dt = x[2]
		yr = x[0]
		value = get_date_value(yr, mn, dt)
		type = 'DATE'
		return timex_str, type, value, 'DCT-2' 
	
	# Handle "mm-dd-yy"
	p = re.compile(month_re+'-'+day_re+'-[0-9][0-9]')
	if p.search(cons): 
		val = p.findall(cons)[0] 
		mn = val[0:2]
		dt = val[3:5]
		yr = val[6:8]
		if int(yr) > 50: 
			yr = '19'+str(yr)
		value = get_date_value(yr, mn, dt)
		type = 'DATE' 
		return timex_str, type, value, 'DCT5'

	# Handle "yyyy-mm-dd OR yyyy/mm/dd"
	p = re.compile(year_re+'[-|/]'+month_re+'[-|/]'+day_re)
	if p.search(cons): 
		val = p.findall(cons)[0] 
		yr = val[0:4]
		mn = val[5:7]
		dt = val[8:10]
		value = get_date_value(yr, mn, dt)
		type = 'DATE'
		return timex_str, type, value, 'mic1'
	
	# Handle "yyyy-mm-ddThh:mm OR yyyy/mm/ddThh:mm"
	p = re.compile(year_re+'[-|/]'+month_re+'[-|/]'+day_re+'T[0-9]{2}:[0-9]{2}')
	if p.search(cons): 
		val = p.findall(cons)[0] 
		yr = val[0:4]
		mn = val[5:7]
		dt = val[8:10]
		hh = val[11:13]
		mi = val[14:16]
		value = get_datetime_value(yr, dt, mn, hh, mi)
		type = 'DATE'
		return timex_str, type, value, 'mic4'

	# Handle "yyyy-mm-ddThh:mm:ss OR yyyy/mm/ddThh:mm:ss"
	p = re.compile(year_re+'[-|/]'+month_re+'[-|/]'+day_re+'T[0-9]{2}:[0-9]{2}:[0-9]{2}')
	if p.search(cons): 
		val = p.findall(cons)[0] 
		yr = val[0:4]
		mn = val[5:7]
		dt = val[8:10]
		hh = val[11:13]
		mi = val[14:16]
		se = val[17:19]
		value = get_datetime_value(yr, dt, mn, hh, mi, se)
		type = 'DATE'
		return timex_str, type, value, 'mic5'

	# Handle "mm-/dd-/yy or dd-/mm-/yy"
	p = re.findall('^([0-9][0-9]?)[-|/]([0-9][0-9]?)[-|/]([0-9]{2,4})',cons)
	if p:
		x = list(p[0])
		if int(x[0])>12:
			mn = x[1]
			dt = x[0]
		else:
			mn = x[0]
			dt = x[1]
		yr = x[2]
		if len(yr)==2:
			if int(yr) > 50:
				yr = '19'+str(yr)
			else:
				yr = "20"+str(yr)
		value = get_date_value(yr, mn, dt)
		type = 'DATE'
		return timex_str, type, value, 'DCT-'  
	   
	#### handle DATE type ####
	if cons == 'today': 
		value = date[0]+'-'+date[1]+'-'+date[2]
		type = 'DATE'
		return timex_str, type, value, 'today'
	if re.search(' now ', ' '+cons+' ') or cons == 'currently' or cons == 'at present' or re.search('moment', cons): 
		value = date[0]+'-'+date[1]+'-'+date[2]
		type = 'DATE'
		return timex_str, type, value, 'now' 
	if re.search('future', cons.strip()) or re.search('coming', cons.strip()) : 
		value = 'FUTURE_REF' 
		type = 'DATE'
		return timex_str, type, value, 'future_ref' 
	if cons.strip() == 'times' or cons.strip() == 'several years ago' or cons.strip() == 'last time' or cons.strip() == 'few years ago' or re.search('past', cons) or re.search('previous', cons.strip()) or re.search('recently', cons): 
		value = 'PAST_REF' 
		type = 'DATE'
		return timex_str, type, value, 'past_ref' 
	if cons.strip() == 'tomorrow': 
		value = add_date(day, month, year, 1)
		type = 'DATE' 
		return timex_str, type, value, 'tomorrow' 
	if cons.strip() == 'yesterday': 
		value = add_date(day, month, year, -1)
		type = 'DATE' 
		return timex_str, type, value, 'yesterday' 

	# TIME 
	p = re.compile('[012]?[0-9]:[0123456][0-9]')
	if p.search(cons): 
		q = re.compile('[012]?[0-9]') 
		hr = str(int(q.findall(cons)[0]))
		r = re.compile(':[0123456][0-9]')
		min = r.findall(cons)[0] 
		min = re.sub(':', '', min) 
			
		if re.search('p\.?m\.?', cons):			 
			if int(hr) < 12: 
				hr = int(hr) + 12 
				
		if len(str(hr))==1: hr='0'+hr
		value = get_datetime_value(year, month, day, hr, min) 
		type = 'TIME' 
		return timex_str, type, value, 'time' 
			

	# decade 
	prev_mod = 'previous|last' 
	next_mod = 'next|later' 
	current = 'this' 
	modifier = '('+prev_mod+'|'+next_mod+'|'+current+')'
	
	p = re.compile(modifier+'[ ]*decade')
	if p.search(cons): 
	  #  print  cons
		q = re.compile(modifier)
		dec = str(year)[:3] 
		type = 'DATE' 
		if q.search(cons): 
			mod = q.findall(cons)[0] 
			if re.search(mod, prev_mod): 
				mod_val = 'prev' 
				dec = int(dec) - 1 
			elif re.search(mod, next_mod): 
				mod_val = 'next'
				dec = int(dec) + 1 
			elif re.search(mod, current): 
				mod_val = 'current' 
				dec = dec 
			else: 
				type = 'DURATION' 
				dec = dec
			value = str(dec)+'X'
			return timex_str, type, value, 'decade' 
		
	if re.search('decade', cons): 
		type = 'DURATION' 
		value = 'P1E' 
		return timex_str, type, value, 'decade-rest' 

	# Sunday, Monday 
	prev_mod = '(previous|last)' 
	next_mod = '(next|later)' 
	modifier = '('+prev_mod+'|'+next_mod+')'
	dow_string = '(sunday|monday|tuesday|wednesday|thursday|friday|saturday)' 
	p = re.compile(modifier+'?[ ]*'+dow_string)
	if p.search(cons): 
		r = re.compile(dow_string) 
		tmp_dow = r.findall(cons)[0] 
		type = 'DATE' 
		q = re.compile(next_mod)
		if q.search(cons):			 
			value = get_dows_date_from_date(tmp_dow, day, month, year, 'next')
		else: 
			value = get_dows_date_from_date(tmp_dow, day, month, year, 'prev')

		if re.search('night', cons): 
			value = value + 'TNI' 
			type = 'TIME'
		if re.search('nights', cons): 
			type = 'FREQUENCY' 

		if re.search('morning', cons): 
			value = value + 'TMO' 
			type = 'TIME'
		if re.search('mornings', cons): 
			type = 'FREQUENCY' 

		if re.search('afternoon', cons): 
			value = value + 'TAF' 
			type = 'TIME'
		if re.search('afternoons', cons): 
			type = 'FREQUENCY' 

		if re.search('evening', cons): 
			value = value# + 'TEV' 
			type = 'TIME'
		if re.search('evenings', cons): 
			type = 'FREQUENCY'
		
		if re.search('[0-9]{2}( )?p.?m.?',cons):
			hours = int(re.findall('[0-9]{2}',cons)[0])+12
			value += 'T' + str(hours) + ':' + '00'
			type = 'TIME'
		
		if re.search('[0-9]{2}:[0-9]{2}( )?p.?m.?',cons):
			hours = int(re.findall('[0-9]{2}',cons)[0])+12
			minutes = int(re.findall('[0-9]{2}',cons)[1])+12
			value += 'T' + str(hours) + ':' + minutes
			type = 'TIME'
		
		return cons, type, value, 'DOWmic' 
		
	if re.search('mornin?g', cons): 
		value = get_date_value(year, month, day) #+'TMO' 
		type = 'DATE'
		return timex_str, type, value, 'morning'

	if re.search('evening', cons): 
		value = get_date_value(year, month, day)# +'TEV' 
		type = 'DATE' 
		return timex_str, type, value, 'evening'
	
	if re.search('afternoon', cons): 
		value = get_date_value(year, month, day)# +'TAF' 
		type = 'DATE' 
		return timex_str, type, value, 'afternoon'

	# Handle 'this century'
	#print p
	if re.search('this century',cons) > 0:
		return timex_str, 'DATE', 'P100Y', 'thisCentury'
		
	# nearly four years ago, three months ago, 10 days ago 
	number_one = 'one|two|couple|three|four|five|six|seven|eight|nine'
	number_two = 'ten|eleven|tweleve|thirteen|fourteen|fifteen|sixteen|seventeen|eighteen|nineteen' 
	number_three = 'twenty|thirty|forty|fifty|sixty|seventy|eighty|ninety|hundred|thousand' 
	num = '[0-9]+'
	number = '('+number_one+'|'+number_two+'|'+number_three + '|' + num+')'
	time_type = '(day|days|week|weeks|month|months|year|years|y|quarter)'
	
	p = re.compile(number + ' ' + time_type + '.* ago')
	if p.search(cons): 
		type = 'DATE' 
		mod = '?'
		q = re.compile(number)
		foo_num = q.findall(cons)[0] 
		q2 = re.compile(num)
		if q2.search(cons): 
			foo_num = int(foo_num) 
		else:
			foo_num = get_number(foo_num) 
		r = re.compile(time_type) 
		foo_time = r.findall(cons)[0] 
		
		if re.search('week', foo_time): 
			week_date = get_date_value(year, month, day)
			week = get_one_week_range(week_date)
			week = week - 1 - int(foo_num)
			value = str(year)+'-W'+pad_zero(week) 
		elif re.search('year', foo_time): 
			year = year - int(foo_num) 
			value = str(year)
			#mod = 'APPROX'
		elif re.search('day', foo_time): 
			value = add_date(day, month, year, -1*int(foo_num))
		elif re.search('month', foo_time):
			#print foo_num
			year_1 = int(foo_num / 12) 
			month_1 = int(foo_num % 12) 
			if month > month_1: 
				month = month - month_1 
				year = year + year_1
			else: 
				month = 12 + month - month_1 
				year = year + year_1 - 1 
			value = str(year) + '-' + pad_zero(month) 
		return timex_str, type, value, 'NUM TIME AGO', mod

	p = re.compile(' a ' + time_type + '.* ago')
	if p.search(' ' +timex_str.lower() +' '): 
		type = 'DATE' 
		foo_num = 1 
		r = re.compile(time_type) 
		foo_time = r.findall(cons)[0] 
		
		if re.search('week', cons): 
			week_date = get_date_value(year, month, day)
			week = get_one_week_range(week_date)
			week = week - int(foo_num)
			value = str(year)+'-W'+pad_zero(week) 
		elif re.search('year', cons): 
			year = year - int(foo_num) 
			value = str(year) 
		elif re.search('day', cons): 
			value = add_date(day, month, year, -1*int(foo_num))
		elif re.search('month', cons):
#			print foo_num
			year_1 = foo_num / 12 
			month_1 = foo_num % 12 
			if month > month_1: 
				month = month - month_1 
				year = year + year_1
			else: 
				month = 12 + month - month_1 
				year = year + year_1 - 1 
			value = str(year) + '-' + pad_zero(month) 
		return timex_str, type, value, 'A TIME AGO' 


	# January this year, June last year 
	prev_mod = 'previous|last' 
	next_mod = 'next|later' 
	current_mod = 'this|current' 
	modifier = '('+prev_mod+'|'+next_mod+'|'+current_mod +')'
	month_string = '(january|jan|february|feb|march|mar|april|apr|may|june|jun|july|jul|august|aug|september|sep|sept|october|oct|november|nov|december|dec)'

	p = re.compile(month_string+' '+modifier+' year')
	if p.search(cons): 
		q = re.compile(month_string) 
		foo_month = q.findall(cons)[0]  
		month = get_month(foo_month)
		r = re.compile(modifier) 
		if r.search(cons):
			mod = r.findall(cons)[0] 
			if re.search(mod, prev_mod): 
				year = year - 1 
			elif re.search(mod, next_mod): 
				year = year + 1 
		type = 'DATE' 
		value = str(year) + '-' + pad_zero(month) 
		return timex_str, type, value, 'January this year' 


	# last February 
	p = re.compile(modifier + ' ' + month_string)
	if p.search(cons):
		q = re.compile(month_string) 
		foo_month = q.findall(cons)[0]  
		month = get_month(foo_month)
		r = re.compile(modifier) 
		if r.search(cons):
			mod = r.findall(cons)[0] 
			if re.search(mod, prev_mod) and int(date[1]) <= int(month): 
				year = year - 1 
			elif re.search(mod, next_mod) and int(date[1]) >= int(month): 
				year = year + 1 
		type = 'DATE' 
		value = str(year) + '-' + pad_zero(month) 
		return timex_str, type, value, 'last February' 
		

	# set 
	# every quarters|months|years|weeks 
	season = 'summer|winter|spring|fall' 
	duration = 'day|days|hour|hours|week|weeks|month|months|year|years|quarter|quarters|period|periods'
	all = '('+season+'|'+duration+')' 
	p = re.compile('every '+all) 
	if p.search(cons): 
		type = 'FREQUENCY' 
		foo = p.findall(cons)[0][:1].upper()
		value = 'P1'+str(foo) 
		return timex_str, type, value, 'every' 


	# several months, quarters 
	season = 'summer|winter' 
	duration = 'day|days|hour|hours|week|weeks|month|months|year|years|quarters|period|periods'
	all = '('+season+'|'+duration+')' 
	p = re.compile('(several|recent) '+all) 
	if p.search(cons): 
		type = 'DURATION' 
		r = re.compile(all) 
		foo = r.findall(cons)[0][:1].upper()
		value = 'P3'+str(foo)	#3 INSTEAD OF X 
		return timex_str, type, value, 'several-recent', 'APPROX' 
	

	# quarter 
	if cons.strip() == 'quarter' or cons.strip() == 'period': 
		if month >= 1 and month <= 3: 
			qt = 1#'Q1' 
		elif month >= 4 and month <= 6: 
			qt = 2#'Q2' 
		elif month >= 7 and month <= 9: 
			qt = 3#'Q3'
		elif month >= 10 and month <= 12: 
			qt = 4 
		else: 
			qt = 'X'
		type = 'DATE' 
		value = str(year) + '-Q'+str(qt) 
		return timex_str, type, value, 'quarter-only' 

	# year-ago (first)? quarter, 1988 second quarter
	time = '(first|second|third|fourth)'
	year_re = '[12][0-9][0-9][0-9]'
	
	p = re.compile('(year-(ago|earlier)|'+year_re+') ('+ time +' )?(quarter|period)') 
	if p.search(cons): 
		type = 'DATE' 
		if re.search('first', cons):
			qt = 1#'Q1' 
		elif re.search('second', cons):
			qt = 2#'Q2' 
		elif re.search('third', cons): 
			qt = 3#'Q3' 
		elif re.search('fourth', cons): 
			qt = 4#'Q4'	 
		elif month >= 1 and month <= 3: 
			qt = 1#'Q1' 
		elif month >= 4 and month <= 6: 
			qt = 2#'Q2' 
		elif month >= 7 and month <= 9: 
			qt = 3#'Q3'
		elif month >= 10 and month <= 12: 
			qt = 4 
		else: 
			qt = 'X'
		if re.search('year-ago', cons) or re.search('year-earlier', cons):
			year = year - 1	 
		r = re.compile(year_re)
		if r.search(cons): 
			year = r.findall(cons)[0] 

		value = str(year) + '-Q'+str(qt) 
		return timex_str, type, value, 'year quarter' 

	# next three quarters (P9M)	
	number_one = ' one|two|couple|three|four|five|six|seven|eight|nine'
	number_two = 'ten|eleven|tweleve|thirteen|fourteen|fifteen|sixteen|seventeen|eighteen|nineteen' 
	number_three = 'twenty|thirty|forty|fifty|sixty|seventy|eighty|ninety|hundred|thousand' 
	num = '[0-9]+'
	number = '('+number_one+'|'+number_two+'|'+number_three + '|' + num +')'
	trace = '' 
	p = re.compile(number+ ' (quarter|period)') 
	if p.search(cons): 
		q = re.compile(number) 
		if q.search(timex_str): 
#		if cons == number:
			r1 = re.compile(number_three) 
			r2 = re.compile(number_one) 
			r3 = re.compile(number_two) 
			r4 = re.compile(num) 
			if r1.search(cons): 
				trace += 'r1'
				word1 = r1.findall(cons)[0]
			  #  print word1, cons
				if not re.search(pad_space(word1), pad_space(cons)): 
					word1 = '0' 
			else: 
				word1 = '0'
			if r2.search(cons): 
				trace += 'r2' 
				word3 = r2.findall(cons)[0]
				if not re.search(pad_space(word3), pad_space(cons)): 
					word3 = '0' 

			else: 
				word3 = '0' 

			if r3.search(cons):
				trace += 'r3' 
				word2 = r3.findall(cons)[0]
				if not re.search(pad_space(word2), pad_space(cons)): 
					word2 = '0' 

			else: 
				word2 = '0'

			if r4.search(cons):
				trace += 'r4' 
				word4 = r4.findall(cons)[0]
			else: 
				word4 = '0'

			num = get_number(word1) + get_number(word2) + get_number(word3) + int(word4) 
			qt = num# * 3 
			value = 'P'+str(qt)+'Q' 
			type = 'DURATION' 
			return timex_str, type, value, 'quarter-duration' 


		
	
	# this year's third quarter, next year's first quarter	 
	prev_mod = 'previous|last' 
	next_mod = 'next|later' 
	current_mod = 'this|current|latest' 
	time = 'first|second|third|fourth'
	modifier = '('+prev_mod+'|'+next_mod+'|'+current_mod +')'

	p = re.compile(modifier+ ' year\'s ' + time + '[- ]?(quarter|period)') 
	if p.search(cons): 
		type = 'DATE' 
		r = re.compile(modifier) 
		if r.search(cons):
			mod = r.findall(cons)[0] 
			if re.search(mod, prev_mod): 
				mod_val = 'prev' 
				year = year - 1 
			elif re.search(mod, next_mod): 
				mod_val = 'next'
				year = year + 1 
			else: 
				mod_val = 'current' 
			
			if re.search('first', cons):
				qt = 1#'Q1' 
			elif re.search('second', cons):
				qt = 2#'Q2' 
			elif re.search('third', cons): 
				qt = 3#'Q3' 
			elif re.search('fourth', cons): 
				qt = 4#'Q4'	 
			elif month >= 1 and month <= 3: 
				qt = 1#'Q1' 
			elif month >= 4 and month <= 6: 
				qt = 2#'Q2' 
			elif month >= 7 and month <= 9: 
				qt = 3#'Q3'
			elif month >= 10 and month <= 12: 
				qt = 4 
			else: 
				qt = 'X'

			value = str(year) + '-Q'+str(qt) 
			return timex_str, type, value, 'quarter-special' 

	# quarter, fourth quarter, latest quarter,  third-quarter, next quarter
 
	prev_mod = 'previous|last' 
	next_mod = 'next|later' 
	current_mod = 'this|current|latest' 
	time = 'first|second|third|fourth'
	modifier = '('+prev_mod+'|'+next_mod+'|'+current_mod + '|' +time+')'
	quarter = '(quarter|period)'
	p = re.compile(modifier+'?[- ]?'+quarter)
	if p.search(' ' +cons + ' '): 
		type = 'DURATION' 
		r = re.compile(modifier) 
		if r.search(cons):
			mod = r.findall(cons)[0] 
			
			if re.search(mod, time):
				mod_val = 'none' 
				if re.search('first', mod.strip()):
					qt = 1#'Q1' 
				elif re.search('second', mod.strip()):
					qt = 2#'Q2' 
				elif re.search('third', mod.strip()): 
					qt = 3#'Q3' 
				elif re.search('fourth', mod.strip()): 
					qt = 4#'Q4' 
			elif re.search(mod, prev_mod): 
				mod_val = 'prev' 
			elif re.search(mod, next_mod): 
				mod_val = 'next' 

			else:
				mod_val = 'current' 
		else: 
			mod_val = 'current' 

		if mod_val != 'none': 
			if month >= 1 and month <= 3: 
				qt = 1#'Q1' 
			elif month >= 4 and month <= 6: 
				qt = 2#'Q2' 
			elif month >= 7 and month <= 9: 
				qt = 3#'Q3'				 
			elif month >= 10 and month <= 12: 
				qt = 4 

		if mod_val == 'prev': 
			qt = qt - 1 
			if qt == 0: 
				qt = 4
				year = year - 1 
		elif mod_val == 'next': 
			qt = qt + 1 
			if qt == 5: 
				qt = 1
				year = year + 1 
		else: 
			qt = qt 

		value = str(year) +'-Q'+str(qt) 
		return timex_str, type, value, 'quarter', 'APPROX' 



	# last month, next year, 
	prev_mod = 'previous|last' 
	next_mod = 'next|later' 
	current_mod = 'this|current' 
	modifier = '('+prev_mod+'|'+next_mod+'|'+current_mod +')'
	time_type = 'day|days|week|weeks|month|months|year|years'
	season = 'summer|winter|spring|fall' 
	all_time = '('+time_type + '|' + season + ')' 
	p = re.compile(modifier+' '+all_time)
	if p.search(cons): 
		type = 'DATE'		
		r = re.compile(modifier) 
		if r.search(cons):
			mod = r.findall(cons)[0] 
			if re.search(mod, prev_mod): 
				mod_val = 'prev' 
			elif re.search(mod, next_mod): 
				mod_val = 'next' 
			else: 
				mod_val = 'current' 
		else: 
			mod_val = 'current' 
		t = re.compile(season) 
		if re.search('day', cons): 
			if mod_val == 'prev': 
				value = add_date(day, month, year, -1)
			elif mod_val == 'next': 
				value = add_date(day, month, year, 1)
			else: 
				value = get_date_value(year, month, day)
		elif re.search('week', cons): 
			week_date = get_date_value(year, month, day)
			week = get_one_week_range(week_date)
			if mod_val == 'prev': 
				week = week - 1
			elif mod_val == 'next': 
				week += 1 

			value = str(year)+'-W'+pad_zero(week) 
			type = 'DATE' 
		elif re.search('month', cons): 
			if mod_val == 'prev': 
				if month == 1: 
					month = 12 
					year = year -1 
				else: 
					month = month - 1
				value = str(year) + '-'+pad_zero(month)
			elif mod_val == 'next': 
				if month == 12: 
					month = 1 
					year = year +1 
				else: 
					month = month + 1
				value = str(year) + '-'+pad_zero(month)
			else: 
				value = str(year) + '-'+pad_zero(month)

		elif re.search('year', cons): 
			if mod_val == 'prev': 
				year = year - 1 
			elif mod_val == 'next': 
				year = year + 1
			
			value = str(year)

		elif t.search(cons):
			foo = t.findall(cons)[0] 
			if mod_val == 'prev': 
				year = year - 1 
			elif mod_val == 'next': 
				year = year + 1

			value = str(year) + '-'+ foo[:2].upper()
			
		return timex_str, type, value, 'last month, this week' 


	month_string = '(january|jan|february|feb|march|mar|april|apr|may|june|jun|july|jul|august|aug|september|sep|sept|october|oct|november|nov|december|dec)'
	cons = remove_punctuation(cons)
	#print cons 

	# Feb. 21, Jan. 26, May 23; March 23, 1996 instances 
	p = re.compile(month_string + r'.?[0-9]?[0-9] ')
	cons = ' ' + cons + ' ' 
	if p.search(cons): 
		q = re.compile(month_string) 
		foo_month = q.findall(cons)[0]  
		month = get_month(foo_month)
		r = re.compile(r'[0-9]?[0-9]')
		foo_day = r.findall(cons)[0] 
		yr = re.compile(r'[12][0-9][0-9][0-9]') 
		if yr.search(cons): 
			year = yr.findall(cons)[0]
		value = get_date_value(year, month, foo_day)
		type = 'DATE' 

		return timex_str, type, value, 'Month. Date, MM DD YYYY' 

	# 1 March 1996
	p = re.compile(get_string_range_numbers(1,31,True) + ' ' + month_string + ' ' + '.?[12][0-9][0-9][0-9]')
	if p.search(cons): 
		type = 'DATE' 
		q = re.compile(month_string) 
		foo_month = q.findall(cons)[0]  
		month = get_month(foo_month)
		yr = re.compile(r'[12][0-9][0-9][0-9]') 
		if yr.search(cons): 
			year = yr.findall(cons)[0]
		day = cons.split(' ')[1]
		if int(day) < 10:
			day = '0' + day
		value = str(year)+'-'+pad_zero(month)+'-'+day
		return timex_str, type, value, 'Day Month Year mic'
	
	# March 1996
	p = re.compile(month_string + r'.?[12][0-9][0-9][0-9]')
	if p.search(cons): 
		type = 'DATE' 
		q = re.compile(month_string) 
		foo_month = q.findall(cons)[0]  
		month = get_month(foo_month)
		yr = re.compile(r'[12][0-9][0-9][0-9]') 
		if yr.search(cons): 
			year = yr.findall(cons)[0]
		value = str(year)+'-'+pad_zero(month) 
		return timex_str, type, value, 'Month Year'
	
	# January, February, Jan 
	p = re.compile('[ -]'+month_string+' ')
	if p.search(cons): 
		foo_month = p.findall(' ' +cons+' ')[0]
		month = get_month(foo_month)
		value = str(year) + '-'+pad_zero(month) 
		type = 'DATE' 
		return timex_str, type, value, 'Month' 


	# fiscal 
	if re.search('fiscal year', cons):
		type = 'DATE' 
		return timex_str, type, str(year), 'fiscal' 

	# current year, current week 
	time_type = '(week|weeks|month|months|year|years|quarter)'
	p = re.compile(' current .*'+time_type +' ' )
	if p.search(' ' +cons+' '):
		r = re.compile(time_type)
		foo = r.findall(time_type)[0] 
		if re.search('year', foo): 
			value = str(year) 
		elif re.search('month', foo):
			value = str(year) + '-'+pad_zero(month) 
		elif re.search('week', foo): 
			week_date = get_date_value(year, month, day)
			week = get_one_week_range(week_date)
			value = str(year)+'-W'+pad_zero(week) 
#		elif re.search('quarter', foo): 
		else: 
			value = str(year) 
		type = 'DATE' 
		return timex_str, type, value, 'current time_type' 

	# Handles 199'0s'
	yr = re.compile('{1-2}[0-9]{2}0(\')?s')
	if yr.match(cons):
		return timex_str, 'DATE', cons[:3] + 'X', 'mic0s'
	
	# should go after everything 
	# 1998, 1901, 2010 
	yr = re.compile(r'[ -]?[12][0-9][0-9][0-9]s? ') 
	if yr.search(' ' + cons + ' '): 
		year = yr.findall(cons)[0]
		if re.search(year, cons): 
			value = str(year).strip()		 
			type = 'DATE' 
			if re.search('s', year): 
				value = year.strip()[:3]# + '-XX-XX'
			return timex_str, type, value, 'Year' 
#		if year.strip() == cons.strip(): 
#			type = 'DATE' 
#			return timex_str, type, value, 'Year' 

	#### handle DURATION type ####
	trace = '' 
	prev_mod = 'previous|last' 
	next_mod = 'next|later' 
	ignore_mod = 'nearly|almost'
	modifier = prev_mod+'|'+next_mod+'|'+ignore_mod
	number_one = ' couple|one|two|three|four|five|six|seven|eight|nine'
	number_two = 'ten|eleven|tweleve|thirteen|fourteen|fifteen|sixteen|seventeen|eighteen|nineteen' 
	number_three = 'twenty|thirty|forty|fifty|sixty|seventy|eighty|ninety|hundred|thousand' 
	num = '[0-9]+'
	number = number_one+'|'+number_two+'|'+number_three + '|' + num
	season = 'summer|winter|spring|fall' 
	duration = 'day|days|hour|hours|week|weeks|month|months|year|years'+'|'+season

	# couple of weeks, two months, last five years 
	a = re.compile(duration) 
	p = re.compile(modifier+'?[ ]*'+number +'?[ ]*'+duration) 
	if a.search(cons): 
#	if cons == (modifier+'?[ ]*'+number +'?[ ]*'+duration):
		type = 'DURATION'
		mod = 'NA'
		q = re.compile(number) 
		if q.search(timex_str): 
#		if cons == number:
			r1 = re.compile(number_three) 
			r2 = re.compile(number_one) 
			r3 = re.compile(number_two) 
			r4 = re.compile(num) 
			if r1.search(cons): 
				trace += 'r1'
				word1 = r1.findall(cons)[0]
				if not re.search(pad_space(word1), pad_space(cons)): 
					word1 = '0' 
			else: 
				word1 = '0'
				
			if r2.search(cons): 
				trace += 'r2'
				word3 = r2.findall(cons)[0]
				if not re.search(pad_space(word3), pad_space(cons)): 
				 	word3 = '0' 
			else: 
				word3 = '0' 

			if r3.search(cons):
				trace += 'r3'
				word2 = r3.findall(cons)[0]
				if not re.search(pad_space(word2), pad_space(cons)): 
					word2 = '0' 
			else: 
				word2 = '0'

			if r4.search(cons):
				trace += 'r4' 
				word4 = r4.findall(cons)[0]
				mod = 'APPROX'
			else: 
				word4 = '0'

			num = get_number(word1) + get_number(word2) + get_number(word3) + int(word4)
			 
		else:
			num = '3'	#changed in 3
			#mod = 'APPROX'
		r = re.compile(duration) 
		if r.search(cons): 
			foo_duration = r.findall(cons)[0].upper()
			if re.search(' a '+ foo_duration.lower(), ' ' +timex_str.lower()+ ' '):
				num = '1' 
#		print cons, foo_duration
		if foo_duration[0] == 'H':
			value = 'PT'+str(num)+foo_duration[0]
		else:
			value = 'P'+str(num)+foo_duration[0]
		return timex_str, type, value, 'duration'+trace, mod

	# time, this time, some time, any time, 
	if re.search(' time ', ' ' + cons + ' '): 
		
		if cons == 'this time' or cons == 'time': 
			type = 'DATE'
			value = date[0]+'-'+date[1]+'-'+date[2]
			return timex_str, type, value, 'time-1' 
		elif cons == 'any time' or re.search('next', cons): 
			type = 'DATE'
			value = 'FUTURE_REF' 
			return timex_str, type, value, 'time-2' 
		elif cons == 'some time': 
			type = 'DURATION'
			value = 'PXM' 
			return timex_str, type, value, 'time-3'
		else: 
			type = 'DATE'
			value = date[0]+'-'+date[1]+'-'+date[2]
			return timex_str, type, value, 'time-default' 
	
	# centuries 
	if re.search(' centuries ', ' '+cons+' '): 
		type = 'DURATION' 
		value = 'PXC' 
		timex_str, type, value, 'centuries'

	# 90's 80s. nineties, eighties
	ties = 'fifties|sixties|seventies|eighties|nineties|two-thousands' 
	reg_ties = '\'?[0-9][0-9]\'?s' 
	all = '('+ties+'|'+reg_ties+')' 
	p = re.compile(all)
	if p.search(cons): 
		type = 'DATE' 
		r = re.compile(reg_ties) 
		if re.search('fifties', cons):
			value = '195' 
		elif re.search('sixties', cons): 
			value = '196'
		elif re.search('seventies', cons): 
			value = '197' 
		elif re.search('eighties', cons): 
			value = '198' 
		elif re.search('nineties', cons):
			value = '199' 
		elif re.search('two-thousands', cons): 
			value = '200' 
		elif r.search(cons): 
			foo = r.findall(cons) 
			if foo[0][0] == '\'':
				foo[0] = foo[0][1:]
			if re.search(foo[0][0], '012'): 
				value = '20'+foo[0][0]
			else:
				value = '19'+foo[0][0]
		else:
			value = str(year).strip()[:3]

		return timex_str, type, value+'X', '90s nineties'
	
	# Year in numbers, nineteen ninety-one 
	number_one = 'thirteen|fourteen|fifteen|sixteen|seventeen|eighteen|nineteen' 
	number_two = 'twenty|thirty|forty|fifty|sixty|seventy|eighty|ninety' 
	number_three = 'one|two|three|four|five|six|seven|eight|nine'
	number_four = 'two-thousand|twenty' 
	number_five = 'ten|eleven|tweleve' 
	cons = cons.strip() 
	p = re.compile(number_one+' ' + number_two+'[ -]'+number_three)
	if p.search(cons): 
		q1 = re.compile(number_one)
		a1 = q1.findall(cons)[0] 
		q2 = re.compile(number_two) 
		a2 = q2.findall(cons)[0] 
		q3 = re.compile(number_three) 
		a3_1 = q3.findall(cons)
		a3 = a3_1[len(a3_1)-1] 
		type = 'DATE'
		value = str(get_number(a1)) + pad_zero(str(get_number(a2)+get_number(a3)))
		return timex_str, type, value, 'Year number 90s&before'

	p = re.compile(number_four + '[ -]('+number_five+'|'+number_three+')')
	if p.search(cons): 
		a1 = '20' 
		q2 = re.compile('('+number_five+'|'+number_three+')') 
		a2_1 = get_number(q2.findall(cons)[0]) 
		a2 = a2_1[len(a2_1)-1]
		value = a1 + str(a2) 
		type = 'DATE'
		return timex_str, type, value, 'Year number 2000&after'
	 
	# Handle easy times like 10 p.m.	
	if re.search('[0-9]{2}( )?p.?m.?',cons):
		hours = int(re.findall('[0-9]{2}',cons)[0])+12
		value += 'T' + str(hours) + ':' + '00'
		type = 'TIME'
		return timex_str, type, value, 'mic8'
		
	#20th century 
	p = re.compile('[0-9][0-9]th century') 
	if p.search(cons): 
		q = re.compile('[0-9][0-9]') 
		cen = q.findall(cons)[0]
		cen = int(cen) - 1 
		value = str(cen)+'XX' 
		type = 'DATE' 
		return timex_str, type, value, '20th century'

	# minutes, weeks 
	time_type = '(minutes|days|weeks|months|years|quarters)'
	p = re.compile(time_type) 
	if p.search(cons): 
		foo = p.findall(cons)[0][:1].upper()
		value = 'PX'+foo 
		type = 'DURATION' 
		return timex_str, type, value, 'times_plural' 
	  
 
	# near term, short term 
	if re.search(' term ', ' ' + cons + ' '): 
		type = 'DATE' 
		value = 'FUTURE_REF' 
		return timex_str, type, value, 'term'

	# later date 
	if re.search(' later ', ' ' + cons + ' '): 
		type = 'DATE' 
		value = 'FUTURE_REF' 
		return timex_str, type, value, 'later'

	# then, then current 
	if re.search(' then ', ' ' + cons + ' '): 
		type = 'DURATION'	#i just followed the training data, I am not sure of DURATION
		value = 'PAST_REF' 
		return timex_str, type, value, 'then'

	# yet 
	if re.search(' yet ', ' ' + cons + ' '): 
		type = 'DATE' 
		value = date[0]+'-'+date[1]+'-'+date[2] 
		return timex_str, type, value, 'yet'

	# last 
	if re.search(' last ', ' ' + cons + ' '): 
		type = 'DATE' 
		value = 'PAST_REF' 
		return timex_str, type, value, 'last'

	if re.search(' while ', ' ' + cons + ' '): 
		type = 'DURATION' 
		value = 'PXD' 
		return timex_str, type, value, 'while'

	if re.search(' possible ', ' ' + cons + ' '): 
		type = 'DATE' 
		value = 'FUTURE_REF' 
		return timex_str, type, value, 'possible'

	if cons.strip() == 'date': 
		type = 'DATE' 
		value = get_date_value(year, month, day)
		return timex_str, type, value, 'date'
	
	return timex_str, type, value, 'default'
   
def search_in_list(element, list, separator='|'):
	splitted_list = list.split(separator)
	counter = 0
	for elem in splitted_list:
		if element == elem:
			   return counter
		counter += 1
	return -1

##########################################################################################

def get_modifiers(timex_expression, type):
	# POINTS
	timex_expression = timex_expression.strip().lower()
	attribute_value = ''
	#	BEFORE
	pattern = re.compile('(more than) .* (ago)')
	if pattern.search(timex_expression): 
		if type == 'DATE' or type == 'TIME':
			attribute_value = 'BEFORE'
		elif type == 'DURATION':
			attribute_value = 'MORE_THAN'
	#	AFTER
	pattern = re.compile('(less than) .* (ago)')
	if pattern.search(timex_expression):
		if type == 'DATE' or type == 'TIME':
			attribute_value = 'AFTER'
		elif type == 'DURATION':
			attribute_value = 'LESS_THAN'
	#	ON_OR_BEFORE
	pattern = re.compile('(no less than) .* (ago)')
	if pattern.search(timex_expression): attribute_value = 'ON_OR_BEFORE'
	#	ON_OR_AFTER
	pattern = re.compile('(no more than) .* (ago)')
	if pattern.search(timex_expression):
		if type == 'DATE' or type=='TIME':
			attribute_value = 'ON_OR_AFTER'
		elif type == 'DURATION':
			attribute_value = 'EQUAL_OR_LESS'
	#	LESS_THAN
	pattern = re.compile('(nearly) .* (of)?')
	if pattern.search(timex_expression): attribute_value = 'LESS_THAN'
	#	MORE_THAN
		# see above (BEFORE section)	
	#	EQUAL_OR_LESS
		# see above (ON_OR_AFTER section)
	#	EQUAL_OR_MORE
	pattern = re.compile('(at least)')
	if pattern.search(timex_expression): attribute_value = 'EQUAL_OR_MORE'
	#	START
	pattern = re.compile('(early|down of|start|beginning)')
	if pattern.search(timex_expression): attribute_value = 'START'
	#	MID
	pattern = re.compile('(middle|mid-)')
	if pattern.search(timex_expression): attribute_value = 'MID'
	#	END
	pattern = re.compile('(end|late)')
	if pattern.search(timex_expression): attribute_value = 'END'
	#	APPROX
	pattern = re.compile('(about|around|more or less|nearly|middle|mid|early)')
	if pattern.search(timex_expression): attribute_value = 'APPROX'
	
	return attribute_value

def get_date(today=True):
	if today:
		return get_today()
	else:
		return '2011', '09', '07' 

'''
def demo():
	examples = 'last friday , tomorrow , last week , now, the next year, '
			   '50 days, 19 years, afternoon, five'
	dct = get_date() 
	print '\nDocument creation time', dct, '\nExample output:' 
	for tempexp in examples.split(','): 
		normalized_value = get_timex_value(tempexp, dct) 
		print normalized_value
'''

def get_triple_date(date):
	return date[:4], date[4:6], date[6:8]

def get_quarter_string(month):
	month = int(month)
	if month <= 3:
		return 'Q1'
	elif month <= 6:
		return 'Q2'
	elif month <= 9:
		return 'Q3'
	else:
		return 'Q4'

def higher_tier(cons, date):
	
	raw_expression = cons.strip().lower()
	p = re.findall("([\.|\?|-||||;|,|>|<|/|#|\:|\']+)$",raw_expression)
	n = -1
	if p: n = len(p[0])
	if n>0: raw_expression = raw_expression[:-n].strip()
	raw_expression = raw_expression.replace("this year", str(date[0]))
	if '(' in raw_expression and not ')' in raw_expression:
		#print raw_expression
		raw_expression = raw_expression[:raw_expression.find('(')].strip()
	
	utterance = str(date[0]) + "-" + str(date[1]) + "-" + str(date[2])
	
	if raw_expression == 'current':
		return cons, 'DATE', date[0]+'-'+date[1]+'-'+date[2], 'current'
	
	if raw_expression == 'the weekend':
		return cons, 'DATE', date[0]+'-'+date[1]+'-'+date[2], 'the weekend'
	
	if re.match('(a )?(year)(-| )?(earlier)',raw_expression):
		value = int(date[0]) - 1
		value = str(value)
		return cons, 'DATE', value, 'a year earlier'
	
	if re.match('^(a )?(year)(-)?(ago)',raw_expression):
		return cons, 'DATE', str(int(date[0])-1)+'-'+get_quarter_string(date[1]), 'a year ago'
	
	if re.match('^(the )?(year)(\'s|-| )(end)$',raw_expression):
		return cons, 'DATE', date[0]+'-12-31', 'year end'
	
	if re.match('^(the )(summer|winter|autumn|spring)',raw_expression):
		return cons, 'DATE', date[0]+'-'+raw_expression.split(' ')[1][:2].upper(), 'the season'
	
	if re.match('^(summer|winter|autumn|spring)',raw_expression):
		return cons, 'DATE', date[0]+'-'+raw_expression.split(' ')[0][:2].upper(), 'season'
	
	if re.match('^(one minute)$',raw_expression):
		return cons, 'DURATION', 'PT1M', 'one minute'
	
	if re.match('^(one)( |-)(hour)$',raw_expression):
		return cons, 'DURATION', 'PT1H', 'one hour'
	
	if re.match('^(one)( |-)(week)$',raw_expression):
		return cons, 'DURATION', 'P1W', 'one week'
	
	if re.match('^(one)( |-)(month)$',raw_expression):
		return cons, 'DURATION', 'P1M', 'one month'
	
	if re.match('^(one)( |-)(year)$',raw_expression):
		return cons, 'DURATION', 'P1Y', 'one year'
	
	p = re.findall('^([0-9][0-9]?) ?(?:/|-) ?([0-9][0-9]?)(?: a\.?m\.?| p\.?m\.?)?$', raw_expression)
	if p:
		num1 = int(p[0][0])
		num2 = int(p[0][1])
		if num2>31:
			if num2>50:
				num2 += 1900
			else:
				num2 += 2000
			if len(str(num1))==1: num1 = "0"+str(num1)
			return cons, 'DATE', str(num2)+'-'+str(num1), 'XX/YY'
		elif num1>12:
			num1, num2 = str(num1), str(num2)
			if len(str(num1))==1: num1 = "0"+str(num1)
			if len(str(num2))==1: num2 = "0"+str(num2)
			return cons, 'DATE', str(date[0])+'-'+num2+'-'+num1, 'XX/YY'
		else:
			num1, num2 = str(num1), str(num2)
			if len(str(num1))==1: num1 = "0"+str(num1)
			if len(str(num2))==1: num2 = "0"+str(num2)
			return cons, 'DATE', str(date[0])+'-'+num1+'-'+num2, 'XX/YY'
		
	
	if re.match("^(?:the|that) day$", raw_expression):
		return cons, 'DATE', utterance, "the day"
	
	if re.match("^the weeks?$", raw_expression):
		return cons, 'DURATION', utterance, "the week"
	
	if re.match("^the days$", raw_expression):
		return cons, 'DURATION', 'P3D', "the days", "APPROX"
	
	if re.match("overnight", raw_expression):
		return cons, 'DURATION', 'PT12H', "overnight", "APPROX" # maybe PTXH is better
	
	p = re.findall("(?:'|&apos;)([0-9][0-9]*)", raw_expression)
	if p:
		num = int(p[0])
		if num>50:
			num+=1900
		else:
			num+=2000
		return cons, 'DATE', str(num), "'XX" 
		
	
	p = re.findall("(?:the )?(?:past|previous\last) ([0-9][0-9]*) (days?|months?|years?|hours?|minutes?|weeks?|seconds?)", raw_expression)
	if p:
		mod = ""
		if ''.join(p[0][1][0:2]) in ('mi','ho','se'): mod = "T"
		return cons, 'DURATION', 'P'+mod+str(p[0][0])+p[0][1][0].upper(), "past X days/minutes..."
	
	p = re.findall('(?:the )?(?:past|previous\last) ('+'|'.join(dt_util.get_literal_nums())+') (days?|months?|years?|hours?|minutes?|weeks?|seconds?)', raw_expression)
	if p:
		mod = ""
		if ''.join(p[0][1][0:2]) in ('mi','ho','se'): mod = "T"
		return cons, 'DURATION', 'P'+mod+str(dt_util.get_num_from_literal(p[0][0]))+p[0][1][0].upper(), "past X days/minutes..."
	
	p = re.findall("([0-9][0-9]*) (?:days?|months?|years?|hours?|minutes?|weeks?) before", raw_expression)
	if p:
		raw_expression = raw_expression.replace("before", "ago")
		return higher_tier(raw_expression, date)
	
	p = re.findall('('+'|'.join(dt_util.get_literal_nums())+') (?:days?|months?|years?|hours?|minutes?|weeks?) before', raw_expression)
	if p:
		raw_expression = raw_expression.replace("before", "ago")
		raw_expression = raw_expression.replace(p[0], str(dt_util.get_num_from_literal(p[0])))
		return higher_tier(raw_expression, date)
	
	p = re.findall("the early on ([0-9][0-9]*)(?:-|/)([0-9][0-9]*)(?: a\.?m\.?| p\.?m\.?)", raw_expression)
	if p:
		return higher_tier(p[0][0]+"-"+p[0][1], date)
	
	p = re.findall("^([0-9][0-9]?/[0-9][0-9]?) ?(?:-|to) ?([0-9][0-9]?/[0-9][0-9]?)$", raw_expression)
	if p:
		date1 = [int(x) for x in higher_tier(p[0][0],date)[2].split('-')]
		date1 = datex(date1[0], date1[1], date1[2])
		date2 = [int(x) for x in higher_tier(p[0][1],date)[2].split('-')]
		date2 = datex(date2[0], date2[1], date2[2])
		difference = int(math.fabs((date1-date2).days))
		return cons, 'DURATION', 'P' + str(difference) + "D", "compact range"
	
	if re.match('^(?:[a-z]+ )?half (?:an )?hour$', raw_expression):
		return cons, 'DURATION', 'PT30M', 'half hour'
	
	month_string = 'january|jan|february|feb|march|mar|april|apr|may|june|jun|july|jul|august|aug|september|sep|sept|october|oct|november|nov|december|dec'
	
	p = re.findall('('+month_string+') (?:through|to) ('+month_string+')(?: of)? ([0-9][0-9]*)', raw_expression)
	if p:
		month1 = int(get_month(p[0][0]))
		month2 = int(get_month(p[0][1]))
		diff = abs(month2-month1)#+1
		year = p[0][2]
		if len(year)==2:
			if int(year)>50:
				year = int(year) + 1900
			else:
				year = int(year) + 2000
		year = int(year)
		return cons, 'DURATION', 'P'+str(diff)+'M', 'two months of YEAR'	
	
	p = re.findall('(?:the )?('+month_string+') (?:of |in )([0-9]+)',raw_expression)
	if p:
		month = get_month(p[0][0])
		year = p[0][1]
		if len(year)==2:
			if int(year)>50:
				year = int(year) + 1900
			else:
				year = int(year) + 2000
		year = int(year)
		return cons, 'DATE', str(year)+'-'+month, 'ICS of YEAR'	
	
	if re.match("^o/n$", raw_expression):
		return cons, 'DURATION', 'PT8H', "o/n"
	
	p = re.findall('^(a|'+'|'.join(dt_util.get_literal_nums())+')? ?(days?|months?|years?|hours?|minutes?|seconds?|weeks?) ?(?:[a-z]* ?half ?) ago$', raw_expression)
	if p:
		mod = ''
		if p[0][1][0:2] in ['mi','ho','se']:
			mod = "T"
		if p[0][0]=="a":
			num = 1
		else:
			num = dt_util.get_num_from_literal(p[0][0])
		if re.search("half", raw_expression):
			num += 0.5
		return cons, 'DURATION', 'P'+mod+str(num)+p[0][1][0].upper(), 'ICS day/week ago'
	
	p = re.findall('^([0-9][0-9]?[0-9]?)? ?(days?|months?|years?|hours?|minutes?|seconds?|weeks?) ?(?:[a-z]* ?half ?) ago$', raw_expression)
	if p:
		mod = ''
		if p[0][1][0:2] in ('mi','ho','se'): mod = "T"
		num = int(p[0][0])
		if re.search("half", raw_expression):
			num += 0.5
		return cons, 'DURATION', 'P'+mod+str(num)+p[0][1][0].upper(), 'X day/week ago'
	
	p = re.findall('^(?:the )?([0-9][0-9]?)(?:th|st|nd|rd)? of ('+month_string+')$', raw_expression)
	if p:
		num = str(int(p[0][0]))
		if len(num)==1: num = "0"+num
		return cons, 'DATE', str(date[0])+'-'+get_month(p[0][1])+'-'+num, 'the XX of ICS'

	if re.match('(?:the )?day (?:prior|before) to', raw_expression):
		utterance = datex(int(date[0]),int(date[1]),int(date[2]))
		return cons, 'DATE', (utterance-timedelta(days=1)).isoformat(), 'the day prior to...'
	
	p = re.findall('([0-9][0-9]?/[0-9][0-9]?)-([0-9][0-9]?/[0-9][0-9]?)/([0-9][0-9]?[0-9]?[0-9]?)', raw_expression)
	if p:
		date1 = [int(x) for x in (higher_tier(p[0][0]+'/'+p[0][2],date)[2]).split('-')]
		date2 = [int(x) for x in (higher_tier(p[0][1]+'/'+p[0][2],date)[2]).split('-')]
		diff = abs(int((datex(date1[0],date1[1],date1[2])-datex(date2[0],date2[1],date2[2])).days))
		return cons, 'DURATION', 'P'+str(diff)+'D', 'two dates'
	
	p = re.findall('([012]?[0-9]:?[0123456]?[0-9]? ?[a|p]\.?m\.?) ?on ?([0-9][0-9]*[/|-][0-9][0-9]*(?:[/-][0-9][0-9]*)?)$', raw_expression)
	if p:
		value = higher_tier(p[0][1], date)[2] + higher_tier(p[0][0], date)[2][10:]
		return cons, 'TIME', value, 'HOUR on DATE'
	
	p = re.findall('([0-9][0-9]*[/|-][0-9][0-9]*(?:[/-][0-9][0-9]*)?) ?at ?([012]?[0-9]:?[0123456]?[0-9]? ?[a|p]\.?m\.?)$', raw_expression)
	if p:
		value = higher_tier(p[0][0], date)[2] + higher_tier(p[0][1], date)[2][10:]
		return cons, 'TIME', value, 'DATE at HOUR'
	
	if re.match('^(?:the )?night (?:before|prior)', raw_expression):
		value = datex(int(date[0]), int(date[1]), int(date[2])-1)
		return cons, 'DATE', value.isoformat(), 'night before' 	# I removed TNI
	
	p = re.findall('^[the ]?('+'|'.join(dt_util.get_literal_nums())+') nights?', raw_expression)
	if p:
		return cons, 'DURATION', 'P'+str(dt_util.get_num_from_literal(p[0]))+'D', 'ICS nights'
	
	p = re.findall('^[the ]?([0-9][0-9]*) nights?', raw_expression)
	if p:
		return cons, 'DURATION', 'P'+str(int(p[0]))+'D', 'X nights'
		
	p = re.findall('^(?:the )?(?:morning|afternoon|night|evening) (?:of|on) (?:the)? ?([a-zA-Z0-9 -/]+)$', raw_expression)
	if p:
		if re.search('admission|discharge|transfer|operation',p[0]):
			utterance = datex(int(date[0]), int(date[1]), int(date[2]))
			return cons, 'DATE', utterance.isoformat(), 'the morning/evening of ...'
		return cons, 'DATE', higher_tier(p[0],date)[2], 'the morning/evening of ...'
	
	p = re.findall('^(?:the )?(?:morning|afternoon|night|evening)? ?(?:of|on)? ?(?:the)? ?([0-9][0-9]*)(?:rd|nd|st|th)$', raw_expression)
	if p:
		d1 = datex(int(date[0]), int(date[1]), int(date[2]))
		d2 = datex(int(date[0]), int(date[1]), int(p[0]))
		if (d2-d1).days>0: d2 = d2.replace(month=int(date[1])-1)
		return cons, 'DATE', d2.isoformat(), 'the XXrd'
	
	if re.match('(?:the|that)? ?(?:to)?night', raw_expression): 
		value = datex(int(date[0]), int(date[1]), int(date[2])) 
		return cons, 'DATE', value.isoformat(), 'night' 	# I removed TNI
	
	p = re.findall('^(?:the|on) ('+'|'.join(dt_util.get_literal_nums())+')$', raw_expression)
	if p:
		utterance = datex(int(date[0]), int(date[1]), int(date[2]))
		d2 = datex(int(date[0]), int(date[1]), int(dt_util.get_num_from_literal(p[0])))
		if (utterance-d2).days>0: d2 = d2.replace(month=int(date[1])+1)
		return cons, 'DATE', d2.isoformat(), 'the ICSth'
	
	p = re.findall('^(?:the|on) ([012]?[0-9])(?: |-)?(?:st|nd|rd|th)?$', raw_expression)
	if p:
		utterance = datex(int(date[0]), int(date[1]), int(date[2]))
		d2 = datex(int(date[0]), int(date[1]), int(p[0]))
		if (utterance-d2).days>0: d2 = d2.replace(month=int(date[1])+1)
		return cons, 'DATE', d2.isoformat(), 'the ICSth'
	
	p = re.findall('^(?:early|late) ?(?:on)? ?([a-zA-Z0-9 -/]+)$', raw_expression)
	if p:
		return cons, 'DATE', higher_tier(p[0],date)[2], 'early on ***'
	
	if re.search('(?:(?:(?:tuesday|tue|tu) ?(?:/|-|,) ?(?:thursday|thu|th) ?(?:/|-|,|and) ?(?:saturday|sat|sa))|(?:(?:monday|mon|mo) ?(?:/|-|,) ?(?:wednesday|wed|we|wd) ?(?:/|-|,|and) ?(?:friday|fri|fr)))', raw_expression):
		return cons, 'FREQUENCY', 'RP2D', 'tu/th/sa'
	
	p = re.findall('^(?:an|a|the)? ?(?:many|lots?|several|a lot of|a number of) (days?|months?|years?|hours?|minutes?|seconds?|weeks?)$', raw_expression)
	if p:
		mod = ''
		if ''.join(p[0][0:2]) in ('mi','ho','se'): mod = "T"
		return cons, 'DURATION', 'P'+mod+'3'+p[0][0].upper(), 'many years/days', 'APPROX'
	
	p = re.findall('^(?:an|a|the)? ?(?:many|lots?|several|a lot of|a number of) years? ago$', raw_expression)
	if p:
		return cons, 'DURATION', str(int(date[0])-10), 'many years ago', 'APPROX'
	
	p = re.findall('(\d?\d[/|-]\d?\d[/|-]\d+) (?:at|, at|,) (\d?\d:\d?\d(?: ?[p|a]\.?m\.?)?)', raw_expression)
	if p:
		return cons, 'TIME', higher_tier(p[0][0],date)[2][:10] + higher_tier(p[0][1],date)[2][10:], 'date, time'
	
	p = re.findall('^([xivdcml]+)$', raw_expression)
	if p:
		num = dt_util.roman_to_int(p[0])
		if num>0:
			if num<50:
				return cons, 'TIME', 'R'+str(num), 'roman number'
			else:
				return higher_tier(str(num) ,date)
	
	if re.match('^annually$', raw_expression):
		return cons, 'FREQUENCY', 'RP1Y', 'annually'
	
	if re.match('^(?:the)? ?(?:admission|discharge|operation) (?:date|day|night|morning)$', raw_expression):
		utterance = datex(int(date[0]), int(date[1]), int(date[2]))
		return cons, 'DATE', utterance.isoformat(), 'the admission date/day'
	
	if re.match('^(?:the) ([0-9-/]+)$', raw_expression):
		return higher_tier(raw_expression[3:], date)
	
	p = re.findall('^('+'|'.join(dt_util.get_literal_nums())+') ?(years?|yrs?|ys?|months|mns?|ms?|weeks?|wks?|ws?|days?|ds?) (?:prior|ago|pta)$', raw_expression)
	if p:
		num = dt_util.get_num_from_literal(p[0][0])
		return higher_tier(str(num)+' '+p[0][1]+' ago', date)
	
	p = re.findall('^([0-9\.]+) ?(years?|yrs?|ys?|months|mns?|ms?|weeks?|wks?|ws?|days?|ds?) (?:prior|ago|pta)$', raw_expression)
	if p:
		mod = '?'
		num = int(p[0][0].split(".")[0])
		if re.search('\.',p[0][0]): mod = 'APPROX'
		if p[0][1][0]=="w":
			num = num * 7
		utterance = datex(int(date[0]), int(date[1]), int(date[2]))
		result = utterance
		if p[0][1][0] == 'y':
			result = result.replace(year=result.year-num)
			mod = 'APPROX'
		elif p[0][1][0] == 'm':
			if result.month<=num:
				result = result.replace(year=result.year-1,month=12-abs(num-result.month))
			else:	
				result = result.replace(month=result.month-num)
		else:
			if result.day<=num:
				if result.month==1:
					result = result.replace(year=result.year-1,month=12)
				else:
					result = result.replace(month=result.month-1)
				prev_day = calendar.monthrange(result.year, result.month)[1]-abs(num-result.day)
				result = result.replace(day=prev_day)
			else:
				result = result.replace(day=result.day-num)
		return cons, 'DATE', result.isoformat(), 'XX ymd ago', mod
	
	p = re.findall('^([0-9]+) ?(?:to|-) ?([0-9]+) ?(years?|yrs?|ys?|months|mns?|ms?|days?|ds?) (?:prior|ago|pta)$', raw_expression)
	if p:
		num = int(int(p[0][0])+int(p[0][1])/2)
		if num-int(num)==0.0: num=int(num)
		return higher_tier(str(num)+' '+p[0][2]+' ago', date)
	
	p = re.findall('^('+'|'.join(dt_util.get_literal_nums())+') ?(?:to|-) ?('+'|'.join(dt_util.get_literal_nums())+') ?(years?|yrs?|ys?|months|mns?|ms?|days?|ds?) (?:prior|ago|pta)$', raw_expression)
	if p:
		num = round(((dt_util.get_num_from_literal(p[0][0]) + dt_util.get_num_from_literal(p[0][1])) /2),1)
		if num-int(num)==0.0: num=int(num)
		return higher_tier(str(num)+' '+p[0][2]+' ago', date)
	
	if re.match('^daily ?\( ?daily$', raw_expression):
		return cons, 'DURATION', 'RPT24H', 'DAILY ( daily'
	
	p = re.findall('^(?:the)? ?(?:a\.?m\.?|p\.?m\.?|morning|afternoon|evening) of (.+)$', raw_expression)
	if p:
		return higher_tier(p[0], date)
	
	p = re.findall('^([0-9a-z\.-/ ]*) ?(?:(?:of)? the same (?:night|morning|day|period))$', raw_expression)
	if p:
		return higher_tier(p[0], date)
	
	if re.search('(?:the )?course of (?:the )?night', raw_expression):
		return cons, 'DURATION', 'PT12H', 'course of the night'
	
	p = re.findall('^(?:monday|mon|mo|tuesday|tue|tu|wednesday|wed|we|thursday|thu|th|friday|fri|fr|saturday|sat|sa|sunday|sun|su) ?(?:-|/|,) ?([0-9-/]*)$', raw_expression)
	if p:
		return higher_tier(p[0], date)
	
	if re.match("year", raw_expression):
		return cons, 'DURATION', 'P1Y', 'year'
	
	if re.match("monthly", raw_expression):
		return cons, 'FREQUENCY', 'RP1M', 'monthly'
	
	if re.match("weekly", raw_expression):
		return cons, 'FREQUENCY', 'RP1W', 'weekly'
	
	if re.match("(?:the)? ?same day", raw_expression):
		return higher_tier('today', date)
	
	if re.match("^(?:the )?day (?:before|ago|prior)$", raw_expression):
		return higher_tier('yesterday', date)
	
	p = re.findall('^(?:every )([0-9]+) (days?|ds?|months?|years?|ys?|hours?|hrs?|minutes?|mns?|seconds?|secs?|weeks?|wks?)$', raw_expression)
	if p:
		num = str(int(p[0][0]))
		mod = 'T'
		if p[0][1][0:2] in ['ho','hr','mi','mn','se']:
			mod = 'T'
		return cons, 'FREQUENCY', 'RP'+mod+num+p[0][1][0].upper(), 'every X bla'
	
	p = re.findall('every ('+'|'.join(dt_util.get_literal_nums())+') (days?|ds?|months?|years?|ys?|hours?|hrs?|minutes?|mns?|seconds?|secs?|weeks?|wks?)', raw_expression)
	if p:
		num = str(dt_util.get_num_from_literal(p[0][0]))
		mod = 'T'
		if p[0][1][0:2] in ['ho','hr','mi','mn','se']:
			mod = 'T'
		return cons, 'FREQUENCY', 'RP'+mod+num+p[0][1][0].upper(), 'every X bla'
	
	if re.search("^(a short time)$", raw_expression):
		return cons, 'DURATION', 'PT1H', 'a short time'
	
#	p = re.findall('^the ('+'|'.join(dt_util.get_literal_nums())+') day$', raw_expression)
#	if p:
#		num = dt_util.get_num_from_literal(p[0])
#		result = datex(int(date[0]), int(date[1]), int(date[2]))
#		if num>1:
#			result = result+timedelta(days=num-1)
#		return cons, 'DATE', result.isoformat(), 'the ICS day/month'
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	# CLINICAL
	
	p = re.findall('^([0-9][0-9])[-|/]([0-9][0-9])$',raw_expression)
	if p:
		x = list(p[0])
		mn = x[0]
		dd = x[1]
		if int(x[0])>12: mn, dd = dd, mn
		result = str(''.join(date[0])) + "-" + str(mn) + "-" + str(dd)			
		return cons, 'DATE', result, 'month and day only'
	
	if re.match('^(?:the|this|that)? ?(a\.?m\.?|ante meridiem|morning|before noon)$', raw_expression):
		utterance = datex(int(date[0]), int(date[1]), int(date[2]))
		return cons, 'DATE', utterance.isoformat(), 'am', 'START'
	
	if re.match('^(alt\.? ?h\.?|every other hours?|alternis horis)$', raw_expression):
		return cons, 'FREQUENCY', '<UNKNOWN>', 'alt. h.'
	
	if re.match('^(every other hours?)$', raw_expression):
		return cons, 'FREQUENCY', 'RPT2H', 'every other hour'
	
	if re.match('^(b\.?i\.?d\.?|bis in die|twice daily|twice a day|two times [for|by] day)$', raw_expression):
		return cons, 'FREQUENCY', 'RPT12H', 'bid'
	
	if re.match('^(b\.?t\.?|bed ?times?|h\.?s\.?|nocte|noct\.?)$', raw_expression):
		return cons, 'FREQUENCY', 'RPTNI', 'bt'
	
	if re.match('^(dieb.?[ |-]?alt.?|diebus alternis|quoque alternis die|e\.?o\.?d\.?|q\.?a\.?d\.?|q\.?o\.?d\.?)$', raw_expression):
		return cons, 'FREQUENCY', 'RP48H', 'every other day'
	
	if re.match('^(mane|in the morning)$', raw_expression):
		return cons, 'FREQUENCY', 'RPTMO', 'in the morning'
	
	if re.match('^(o\.?d\.?|omne in die|every ?day|once a day|once daily|daily|q\.?d\.?|q\.?1d\.?)$', raw_expression):
		return cons, 'FREQUENCY', 'RP1D', 'every day, once daily'
	
	if re.match('^(o\.?m\.?)$', raw_expression):
		return cons, 'FREQUENCY', 'RP1D', 'every morning'
	
	if re.match('^(o\.?m\.?|every mornings?|omne mane)$', raw_expression):
		return cons, 'FREQUENCY', 'RP1D', 'every morning'
	
	if re.match('^(o\.?m\.?|every nights?|omne nocte)$', raw_expression):
		return cons, 'FREQUENCY', 'RP1D', 'every night'
	
	if re.match('^(o\.?p\.?d\.?|once per day|once a day)$', raw_expression):
		return cons, 'FREQUENCY', 'RPT24H', 'once per day'
	
	if re.match('^(at lunch|lunch ?time|lunch)$', raw_expression):
		return cons, 'TIME', utterance+'T14:00', 'lunch'
	
	if re.match('^(at dinner|dinner ?time|dinner)$', raw_expression):
		return cons, 'TIME', utterance, 'dinner' # no time in the training set
	
	if re.match('^(post cibum|p\.?c\.?|after meals?)$', raw_expression): 
		return cons, 'FREQUENCY', 'RPT12H', 'after meals'
	
	if re.match('^(post meridiem|p\.?m\.?|evening|afternoon?)$', raw_expression):
		return cons, 'DATE', utterance, 'afternoon or evening'	# the annotators are annotating referring to the date the value should be "utterance+'TAF'"
	
	if re.match('^(q\.?a\.?m\.?|every ?day before noon|quaque die ante meridiem)$', raw_expression): 
		return cons, 'FREQUENCY', 'RP1D', 'every day before noon' #noon is 12:00 (source: guidelines)
	
	if re.match('^(?:few|several|different|many|lots) times? a day$', raw_expression): 
		return cons, 'FREQUENCY', 'RPT8H', 'several times a day', "APPROX"
	
	if re.match('^(?:one time|once|one)(?: episode)?$', raw_expression): 
		return cons, 'FREQUENCY', 'R1', 'one'
	
	if re.match('^(?:twice|two times|two)(?: episode)?$', raw_expression): 
		return cons, 'FREQUENCY', 'R1', 'one'
	
	if re.match('^(?:multiples?|many|severals?|differents?|lots?) ?(?:times?|episodes?)?$', raw_expression):
		return cons, 'FREQUENCY', 'R3', 'many times', 'APPROX' 	#I modified X in 3
	
	if re.match('^(q\.?i\.?d\.? ?\( ?(?:4|four) times a day ?\)|q\.?d\.?s\.?|q\.?i\.?d\.?|4 times? a day|four times? a day|quater die sumendus|quattuor in die)$', raw_expression): 
		return cons, 'FREQUENCY', 'RPT6H', 'four times a day'
	
	if re.match('^(t\.?i\.?d\.? ?\( ?(?:3|three) times a day ?\)|t\.?d\.?s\.?|t\.?i\.?d\.?|3 times? a day|three times? a day|ter die sumendum|ter in die)$', raw_expression): 
		return cons, 'FREQUENCY', 'RPT8H', 'three times a day'
	
	if re.match('^(t\.?i\.?w\.?|3 times? a week|three times? a week)$', raw_expression): 
		return cons, 'FREQUENCY', 'RP0.3W', 'three times a week' #it's coherent with the guidelines, not with ISO8601 syntax
	
	if re.match('^(q\.?p\.?m\.?|every ?day after noon|quaque die post meridiem|q\.? ?daily|q\.? ?day|each day|per day)$', raw_expression): 
		return cons, 'FREQUENCY', 'RP24H', 'every day after noon' #noon is 12:00 (source: guidelines) # RPTAF should be a proper annotation I used 24H instead of 1D
	
	if re.match('^(q\.? ?h\.? ?s\.? ?|every nights? at bed ?times?|quaque hora somni)$', raw_expression):
		return cons, 'FREQUENCY', 'RP24H', 'every night at bedtime' #take from training data
	
	if re.match('q\.? ?hs', raw_expression):
		return cons, 'FREQUENCY', 'RP24HT22:00', 'q hs', 'APPROX'
	 
	if re.match('^(q\.?q\.?h\.?|every four hours?|quater quaque hora|q\.? ?four)$', raw_expression):
		return cons, 'FREQUENCY', 'RPT4H', 'every four hours'
	
	p = re.findall('^(?:q\.?|quaque) ?([0-9]+) ?-?(?:h\.?|hours?|hora)$', raw_expression)
	if p: 
		return cons, 'FREQUENCY', 'RPT'+str(int(p[0]))+'H', 'every X hour'
	
	p = re.findall('^(?:q\.?|quaque) ?([0-9]+) ?(?:d\.?|days?|dies?)$', raw_expression)
	if p: 
		return cons, 'FREQUENCY', 'RP'+str(int(p[0]))+'D', 'every X hour latin'
	
	if re.match('^(q\.?h\.?|every hour|quaque hora)$', raw_expression): 
		return cons, 'FREQUENCY', 'RPT1H', 'every hour'
	
	p = re.findall('^p ?([0-9]+) ?([a-z]{2})$', raw_expression)
	if p:
		if p[1] == "am":
			time = int(p[0])
		else:
			time = int(p[0])+12
		return cons, 'TIME', utterance+'T'+str(time)+':00', 'at QXYY'
	
	if re.match('^(q\.?w\.?k\.?|every weeks?)$', raw_expression):
		return cons, 'FREQUENCY', 'RP1W', 'every week'
	
	if re.match('^(stat.?|statim|immediately|present)$', raw_expression):
		return higher_tier('now', date)
	
	p = re.findall('^([0-9]+)(?:-?| ?)x$', raw_expression)
	if p:
		return cons, 'FREQUENCY', 'R'+str(int(p[0])), 'XXX x'
	
	p = re.findall('^x(?:-?| ?)([0-9]+)$', raw_expression)
	if p:
		return cons, 'FREQUENCY', 'R'+str(int(p[0])), 'x XXX'
	
	if re.search('(p\.?r\.?n\.?|ad lib|as needed|needed)', raw_expression):
		return cons, 'FREQUENCY', 'R', 'prn'
	
	p = re.findall('^([0-9]+) times ?every (days?|weeks?|months?|years?|hours?|minutes?)$', raw_expression)
	if p:
		mod = ""
		if ''.join(p[0][1][0:2]) in ('mi','ho'): mod = "T"
		return cons, 'FREQUENCY', 'R'+str(int(p[0][0]))+'P'+mod+'1'+p[0][1][0].upper(), 'x times every days/months...'
		
	p = re.findall('^times? ([0-9]+)(?: day)?$', raw_expression)
	if p:
		fraction = 24/int(p[0][0])
		if (fraction-int(fraction))==0.0:
			return cons, 'FREQUENCY', 'RP'+str(int(fraction))+'H', 'x times'
		else:
			return cons, 'FREQUENCY', 'RP'+math.round(fraction,1)+'H', 'x times'
	
	p = re.findall('^('+'|'.join(dt_util.get_literal_nums())+')(?: ?)(?:occasions?)?(?:doses?)?(?:times?)?$', raw_expression)
	if p:
		num = dt_util.get_num_from_literal(p[0])
		if num>50:
			return cons, 'DATE', '19'+str(num), 'just a number: date'
		return cons, 'FREQUENCY', 'R'+str(num), 'just a number'
	
	p = re.findall('^([0-9][0-9]?)(?: ?)(?:occasions?)?(?:doses?)?(?:times?)?$', raw_expression)
	if p:
		num = int(p[0])
		if num>50:
			return cons, 'DATE', '19'+str(num), 'just a number: date'
		return cons, 'FREQUENCY', 'R'+str(num), 'just a number'
	
	p = re.findall('^(?:a)? ?(an|a couple of|couple of|a|'+'|'.join(dt_util.get_literal_nums())+') ?(days?|weeks?|months?|years?|hrs?|hours?|mins?|minutes?|secs?|seconds?)$', raw_expression)
	if p:
		mod=''
		mod_attribute = 'NA'
		if ''.join(p[0][1][0:2]) in ('mi','ho','se'): mod = "T"
		if p[0][0] in ['an','a']:
			num = 1
		elif re.search('couple',p[0][0]):
			num = 2
			mod_attribute = 'APPROX'
		else:
			num = dt_util.get_num_from_literal(p[0][0])
		return cons, 'DURATION', 'P'+mod+str(num)+p[0][1][0].upper(), 'ics minutes/days/years...', mod_attribute
	
	p = re.findall('^([0-9]+) ?(days?|weeks?|months?|years?|hrs?|hours?|mins?|minutes?|secs?|seconds?|d\.?|w\.?|s\.?|y\.?)$', raw_expression)
	if p:
		mod = ''
		if ''.join(p[0][1][0:2]) in ('mi','ho','se'): mod = "T"
		num = int(p[0][0])
		return cons, 'DURATION', 'P'+mod+str(num)+p[0][1][0].upper(), 'X minutes/days/years...'
	
	p = re.findall('^times ('+'|'.join(dt_util.get_literal_nums())+')$', raw_expression)
	if p:
		return cons, 'FREQUENCY', 'R'+str(dt_util.get_num_from_literal(p[0])), 'just a number'
	
	p = re.findall('^q\.? ?('+'|'.join(dt_util.get_literal_nums())+') ?(d\.?|w\.?|mo\.?|y\.?|hours?|minutes?|h\.?)$', raw_expression)
	if p:
		mod=''
		if ''.join(p[0][1][0:2]) in ('mi','ho') or p[0][1][0]=='h': mod = "T"
		return cons, 'FREQUENCY', 'RPT'+str(dt_util.get_num_from_literal(p[0][0]))+'H', 'q ICS hour'
	
	if re.match('^(?:the |her |his |their )?(?:post-|post|day)? ?(?:pod|operative|op|hospital|hsp|day|hd)(?:ly)? (?:day |night |afternoon )? ?(?:number|num\.?|#)? ?('+'|'.join(dt_util.get_literal_nums())+'|[0-9][0-9]?) ?(?:and|to) ?('+'|'.join(dt_util.get_literal_nums())+'|[0-9][0-9]?)$', raw_expression):
		return cons, 'DURATION', 'P2D', 'postoperative_RANGE2'
	
	p = re.findall('^(?:the |her |his |their )?(?:post-|post|day)? ?(?:pod|operative|op|hospital|hsp|day|hd)(?:ly)? ?(?:day |night |afternoon )? ?(?:number|num\.?|#)? ?([0-9][0-9]*)$', raw_expression)
	if p:
		value = add_date(int(date[2]), int(date[1]), int(date[0]), int(p[0]))
		return cons, 'DATE', value, 'postoperative_num1'
	
	p = re.findall('^(?:the |her |his |their )?(?:post-|post|day)? ?(?:pod|operative|op|hospital|hsp|day|hd)(?:ly)? (?:day |night |afternoon )? ?(?:number|num\.?|#)? ?('+'|'.join(dt_util.get_literal_nums())+')$', raw_expression)
	if p:
		value = add_date(int(date[2]), int(date[1]), int(date[0]), int(dt_util.get_num_from_literal(p[0])))
		return cons, 'DATE', value, 'postoperative_literals1'
	
	p = re.findall('^(?:the |her |his |their )?('+'|'.join(dt_util.get_literal_nums())+') (?:post-|post|day)? ?(?:pod|operative|op|hospital|hsp|day|hd)(?:ly)? (?:day|night|afternoon)?$', raw_expression)
	if p:
		value = add_date(int(date[2]), int(date[1]), int(date[0]), int(dt_util.get_num_from_literal(p[0])))
		return cons, 'DATE', value, 'postoperative_literals2'
	
	p = re.findall('^(?:the |her |his |their )?([0-9][0-9]*)(?:st|nd|rd|th) (?:post-|post|day)? ?(?:pod|operative|op|hospital|hsp|day|hd)(?:ly)? (?:day|night|afternoon)?$', raw_expression)
	if p:
		value = add_date(int(date[2]), int(date[1]), int(date[0]), int(p[0]))
		return cons, 'DATE', value, 'postoperative_literals3'
	
	p = re.findall('^(?:the)? ?([0-9][0-9]?)(?:st|nd|rd|th)? ?(-|to|or) ?([0-9][0-9]?)(?:st|nd|rd|th)? (?:post-|post|day)? ?(?:pod|operative|op|hospital|hsp|day|hd)(?:ly)? ?(?:days?|nights?|afternoons?)?$', raw_expression)
	if p:
		diff = abs(int(p[0][2]) - int(p[0][0]))
		middle = str(int((int(p[0][2]) + int(p[0][0]))/2))
		if re.search('or', p[0][1]):
			return cons, 'DATE', higher_tier('day '+middle,date)[2], 'Xth to Yth postoperative day', 'APPROX'
		return cons, 'DURATION', 'P'+str(diff)+'D', 'Xth to Yth postoperative day'
	
	p = re.findall('^(?:the |her |his |their )?(?:post-|post|day)? ?(?:pod|operative|op|hospital|hsp|day|hd)(?:ly)? ?(?:day|night|afternoon)?$', raw_expression)
	if p:
		value = add_date(int(date[2]), int(date[1]), int(date[0]), 0)	#TODO: Maybe is more appropriate 1 as value
		return cons, 'DATE', value, 'postoperative'
	
	if re.match('(?:the |her |his |their )?day (?:of )?(?:the )?discharge', raw_expression):
		return cons, 'DATE', utterance, 'discharge_day'
	
	if re.match('(?:the |her |his |their )?day (?:of )?(?:the )?admission', raw_expression):
		return cons, 'DATE', utterance, 'admission_day'
	
	if re.match('(?:the |her |his |their )?day (?:of )?(?:the )?transfer', raw_expression):
		return cons, 'DATE', utterance, 'tranfer_day'
	
	p = re.findall('^([0-9][0-9]?[0-9]?) (?:[a-zA-Z]+) (q.*)',raw_expression)
	if p:
		snd_part = str(higher_tier(p[0][1],date)[2])
		if snd_part[0]=="R":
			snd_part = snd_part[1:]
		return cons, "FREQUENCY", "R" + p[0][0] + snd_part,"puffs" 
	
	p = re.findall('^(?:the|her|his|their)? ?day of life ?#? ?([0-9][0-9]*)$', raw_expression)
	if p:
		value = add_date(int(date[2]), int(date[1]), int(date[0]), int(p[0])-1)
		return cons, 'DATE', value, 'day_of_life_num1'
	
	p = re.findall('^(?:the|her|his|their)? ?day of life ?#? ?('+'|'.join(dt_util.get_literal_nums())+')$', raw_expression)
	if p:
		value = add_date(int(date[2]), int(date[1]), int(date[0]), int(dt_util.get_num_from_literal(p[0]))-1)
		return cons, 'DATE', value, 'day_of_life_literals1'
	
	p = re.findall('^q\.?([0-9]+)$', raw_expression)
	if p:
		return cons, 'FREQUENCY', 'RPT'+str(int(p[0]))+'H', 'qXX'
	
	if re.match('^(?:early)? ?(?:post)? ?(?:-)? ?(operative|extubation) ?(?:course)$', raw_expression):
		value = add_date(int(date[2]), int(date[1]), int(date[0]), 1)
		return cons, 'DATE', value, 'look at early on ***'
	
	if re.match('^per minute$', raw_expression):
		return cons, 'FREQUENCY', 'RPT60S', 'per minute'
	
	p = re.findall('([a-z]{3}) ?\([a-z0-9 \.,]+\) ?for ([0-9]+) ?days?', raw_expression)
	if p:
		value1 = higher_tier(str(p[0][0]),date)[2]
		valuein1 = re.findall('([0-9]+)',value1)[0]
		value2 = int(24/int(valuein1)) * int(p[0][1])
		return cons, 'FREQUENCY', value1.replace('R','R'+str(value2)), 'xxx (...) for X days'
	
	
	
	
	
	
	#UNCERTAIN EXPRESSIONS
	p = re.findall('^([0-9]+) ?(?:-|to) ?([0-9]+) (days?|weeks?|months?|years?|hours?|minutes?)$', raw_expression)
	if p:
		average = simplifyDoubleNumbers(round((int(p[0][0])+int(p[0][1]))/2,1))
		mod = ""
		if ''.join(p[0][2][0:2]) in ('mi','ho', 'se'): mod = "T"
		return cons, 'DURATION', 'P'+mod+str(average)+p[0][2][0].upper(), 'XX -to XX days/months...', 'APPROX'
	
	p = re.findall('^('+'|'.join(dt_util.get_literal_nums())+') ?(?:-|to) ?('+'|'.join(dt_util.get_literal_nums())+') (days?|weeks?|months?|years?|hours?|minutes?|seconds?)$', raw_expression)
	if p:
		num1 = dt_util.get_num_from_literal(p[0][0])
		num2 = dt_util.get_num_from_literal(p[0][1])
		average = simplifyDoubleNumbers(round((num1+num2)/2,1))
		mod = ""
		if ''.join(p[0][2][0:2]) in ('mi','ho','se'): mod = "T"
		return cons, 'DURATION', 'P'+mod+str(average)+p[0][2][0].upper(), 'ICS days/months...', 'APPROX'
	
	p = re.findall('a? ?(?:few|several|lots?|bunch|much|different) (years?|weeks?|months?|days?|hours?|minutes?|seconds?)', raw_expression)
	if p:
		mod = ""
		if ''.join(p[0][0:2]) in ('mi','ho','se'): mod = "T"
		return cons, 'DURATION', 'P'+mod+'3'+p[0][0].upper(), 'few seconds', 'APPROX'	# value 3 taken from the data
	
	if re.match("period",raw_expression):
		return cons, 'DURATION', 'PT24H', 'period', 'APPROX'
	
	p = re.findall('^q\.? ?([0-9]+)(?:to|-)([0-9]+) ?h$', raw_expression)
	if p:
		num = (int(p[0][0])+int(p[0][1]))/2
		if num-int(num)==0.0:
			num=str(int(num))
		else:
			num = str(round(num,1))
		return cons, 'FREQUENCY', 'RPT'+str(num)+'H', 'qXX'
	
	
	
	
	
	
	
	
	
	
	
	
	
	# TRANSFORMATION RULES
	numbers_nl = 'one|two|three|four|five|six|seven|eight|nine|ten|eleven|twelve'
	period_nl = 'minute(s)?|hour(s)?|day(s)?|week(s)?|month(s)?|year(s)?|decade(s)?'
	if re.match('('+numbers_nl+')(-| )('+period_nl+')$',raw_expression):
		return higher_tier(cons.replace('-',' '),date)
	
	if re.match('(week)$',raw_expression):
		return higher_tier('1 '+cons,date)
	
	if re.match('(the )(year|week|decade|hour|month)$',raw_expression):
		return higher_tier('this '+cons.split(' ')[1],date)
	
	if re.match('(the year)$',raw_expression):
		return higher_tier('this year '+cons,date)
	
	if re.match('(the past )(year|month|day|week|decade)',raw_expression):
		return higher_tier(raw_expression.replace('the past','the last'),date)
	
	if re.match('(the fiscal )(year|month|day|week|decade)',raw_expression):
		return higher_tier(raw_expression.replace('the fiscal','the'),date)
	
	if re.match('^(the past )',raw_expression):
		return higher_tier(raw_expression.replace('the past ',''),date)
	
	if re.match('^(the full )',raw_expression):
		return higher_tier(raw_expression.replace('full ',''),date)
	
	if re.match('(noon)',raw_expression):
		return higher_tier(raw_expression.replace('noon','12:00'),date)
	
	if re.match('^(earlier )',raw_expression):
		return higher_tier(raw_expression.replace('earlier ',''),date)
	
	if re.match('^(the following )',raw_expression):
		return higher_tier(raw_expression.replace('following','next'),date)
	
	if re.match('^(sometime )', raw_expression):
		result = higher_tier(raw_expression.replace('sometime ',''),date)
		if re.match('\d\d\d\d',result[2]): # is a year
			return result[0], result[1], result[2]+'-XX-XX', 'sometime'
	
	if re.match('^years?[-| ]?old$',raw_expression):
		return higher_tier('one ' + raw_expression,date)
	
	if re.match('[a-zA-Z]* (year two)(-| )(thousand)$',raw_expression):
		raw_expression = raw_expression.replace('two thousand','2000')
		raw_expression = raw_expression.replace('two-thousand','2000')
		return higher_tier(raw_expression,date)
	
	p = re.findall('^([0-9]?[0-9]) ?(?:a\.?m\.?|anti meridian)$',raw_expression)
	if p:
		if len(p[0]) == 1:
			value = raw_expression.replace(p[0],'0'+p[0]+':00')
		else:
			value = raw_expression.replace(p[0],p[0]+':00')
		return higher_tier(value,date)
	
	p = re.findall('^([0-9]?[0-9]) ?(p\.?m\.?|pm|post meridian)',raw_expression)
	if p:
		value = int(p[0][0])+12
		cons = raw_expression.replace(raw_expression.split(' ')[0],str(value)+':00')
		return higher_tier(cons,date)
	
	if re.match('^[0-9]{6}$',raw_expression):
		if int(raw_expression[:2]) > 15:
			return higher_tier('19'+raw_expression,date)
		else:
			return higher_tier('19'+raw_expression,date)
	
	#	FESTIVITIES
	if re.match('(thanksgiving day)',raw_expression):
		utterance = datex(int(date[0]), int(date[1]), int(date[2]))
		festivity = datex(int(date[0]), 11, 25)
		if (festivity-utterance).days>0: festivity.replace(year=int(date[0])-1)
		return cons, 'DATE', festivity.isoformat(), "thanks giving day"
	
	if re.match('new years? eve', raw_expression):
		utterance = datex(int(date[0]), int(date[1]), int(date[2]))
		festivity = datex(int(date[0]), 12, 31)
		if (festivity-utterance).days>0: festivity.replace(year=int(date[0])-1)
		return cons, 'DATE', festivity.isoformat(), "new years eve"
		
	if re.match('labou?r day', raw_expression):
		utterance = datex(int(date[0]), int(date[1]), int(date[2]))
		festivity = datex(int(date[0]),1,1)
		for i in range(1,31):
			if datex(int(date[0]), 9, i).isocalendar()[2]==1:
				festivity = datex(int(date[0]), 9, i)
				break
		if (festivity-utterance).days>0: festivity.replace(year=int(date[0])-1)
		return cons, 'DATE', festivity.isoformat(), "labou?r day"
	
	if re.match('(columbus day)',raw_expression):
		utterance = datex(int(date[0]), int(date[1]), int(date[2]))
		festivity = datex(int(date[0]), 10, 12)
		if (festivity-utterance).days>0: festivity.replace(year=int(date[0])-1)
		return cons, 'DATE', festivity.isoformat(), "columbus day"
	
	if re.match('(martin luther king,? ?(?:jr\.?)? day)', raw_expression):
		utterance = datex(int(date[0]), int(date[1]), int(date[2]))
		festivity = datex(int(date[0]),1,1)
		num = 0
		for i in range(1,31):
			if datex(int(date[0]), 1, i).isocalendar()[2]==1:
				num += 1
				if num==3:
					festivity = datex(int(date[0]), 1, i)
					break
		if (festivity-utterance).days>0: festivity.replace(year=int(date[0])-1)
		return cons, 'DATE', festivity.isoformat(), "martin luther king day"
	
	if re.match('memorial day', raw_expression):
		utterance = datex(int(date[0]), int(date[1]), int(date[2]))
		festivity = datex(int(date[0]),1,1)
		for i in range(1,31):
			if datex(int(date[0]), 6, i).isocalendar()[2]==1:
				festivity = datex(int(date[0]), 6, i)
				break
		festivity = festivity-timedelta(days=7)
		if (festivity-utterance).days>0: festivity.replace(year=int(date[0])-1)
		return cons, 'DATE', festivity.isoformat(), "memorial day"
	
	
	# EXTENSIONS
	if re.match('(summer|winter|autumn|spring)', raw_expression):
		a,b,c,d = higher_tier(cons)
		if not re.match('(su|wi|au|sp)',c[:-2]):
			if re.match('(summer)',raw_expression): return a, b, c+'-SU', d
			if re.match('(winter)',raw_expression): return a, b, c+'-WI', d
			if re.match('(autumn)',raw_expression): return a, b, c+'-AU', d
			if re.match('(spring)',raw_expression): return a, b, c+'-SP', d
		return a, b, c, 'seasons'
	
	return get_timex_value(cons.lower().strip(), date)

def simplifyDoubleNumbers(num):
	if (num - int(num))==0.0:
		return int(num)
	else:
		return num

def check_mod(timex):
	to_check = False
	if len(timex)<4:
		print "ERROR!"
	else:
		expression = timex[0].strip().lower()
		mod = 'NA'
		if re.search('around|period|postoperatively|all| eve|eve | or |multiple| up |overnight|essentially|approximately|approx|nearly|near|several|different|many|about|couple|few|around|fall|centuries|decades|course', expression):
			mod = 'APPROX'
		if re.search('begin|start?|morning', expression):
			mod = 'START'
		if re.search('less', expression):
			mod = 'LESS'
		if re.search('more|greater', expression):
			mod = 'MORE'
		if re.search('end|late|night|evening', expression):
			mod = 'END'
		if re.search(' mid|mid |mid-|middle|afternoon', expression):
			mod = 'MIDDLE'
		if len(timex)==5:
			if mod!=timex[4] and timex[4]!='?':
				mod = timex[4]
		return timex[0], timex[1], timex[2], timex[3], mod

def main():
	raw_word1 = sys.argv[1]
	raw_word2 = sys.argv[2]
	print normalise(raw_word1, raw_word2)
	
def normalise(raw_word, raw_date=None, bufferised=False):
	if raw_date == "ERROR":
		raw_date = None
	if not bufferised:
		try: os.remove('normaliser_buffer.dat')
		except: pass
	raw_time = ''
	today = datex.today().isoformat().replace("-","")
	utterance_date = today
	result = ''
	
	#if re.search('^(that afternoon|that morning|that night|that evening|the utterance_date|that point|this afternoon|the afternoon|this am|am|this morning|the morning|this point|night|the night|this night|now|day|the day|that day|the time|that time|this time|which time|the same time|the present time|)$',raw_word.strip().lower()):
	if re.search('^(that [a-z]+|the time)$',raw_word.strip().lower()) and bufferised:
		file = open('normaliser_buffer.dat','r')
		last_normalised_date = file.read()
		file.close() 
		#print last_normalised_date, "rather than", raw_date
		raw_date = last_normalised_date
		
	if not raw_date:
		raw_date = str(datex.today().isoformat().replace("-",""))
	
	if re.match('[0-9]{8}T[0-9]{6}',raw_date):
		utterance_date = raw_date[0:4], raw_date[4:6], raw_date[6:8]
		time = raw_date[9:11], raw_date[11:13], raw_date[13:15]
	elif re.match('[0-9]{8}',raw_date):
		utterance_date = raw_date[0:4], raw_date[4:6], raw_date[6:8]
	try:
		result = higher_tier(raw_word,utterance_date)
	except Exception:
		#print 'This script still contains bloody bugs!'
		raise
	result = check_mod(result)
	if result[1]=='DATE' and len(result[2])==10 and bufferised:
		file = open('normaliser_buffer.dat','w')
		file.write(result[2].replace('-',''))
		file.close()
	return result

if __name__ == '__main__':
	main()