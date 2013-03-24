#!/usr/bin/python
'''
	tempexp_normalizer.py
	
	Copyright (c) 2012, gnTEAM, School of Computer Science, University of Manchester.
	All rights reserved. This program and the accompanying materials
	are made available under the terms of the GNU General Public License.
	
	authors: Michele Filannino
	email:  filannim@cs.man.ac.uk
	
	TempExp normaliser is a piece of software that provide the TimeML type and
	value attributes for each temporal expression given in input.
	This work is an extension of TRIOS normaliser. See the next comment.
	For details, see www.cs.man.ac.uk/~filannim/
'''

'''
This program takes a temporal expression and returns the normalized type and 
value according to TimeML scheme. 

This is a regular expression based naive program, but this normalizer had the 
second best performance in TempEval 2010 (temporal evaluation competition). The 
reason for sharing this program is to help others start from this basic program 
and extend it to get better performance. It handles basic temporal expressions 
decently, so most of the people don't need to modify it. Any modification will 
be highly appreciated. Give me your updated copy, I will add your modification 
with credit. 

Usage:
call the function get_timex_value with your "temporal expression" and 
"document creation time" as parameters. See get_date() function to see the 
document creation time format and see examples in the bottom of the page to 
see usage. 

To see the sample output, run: 
	>> python tempexp-normalizer.py 
 
 
Output format:

TimeML specification can be found in:
http://www.timeml.org/site/publications/specs.html. 

This program used specification:

As mentioned already, this program takes temporal expressions as input. If you 
need the program to extract the temporal expressions from text then this is not 
the program you want. After using a program to extract temporal expression this 
program gives the normalized value of temporal expression with respect to 
document creation time. I will release my program for extracting temporal 
expression from text in future. If you need it before I release, feel free to 
let me know. 

Originally developed by:
- Naushad UzZaman (naushad AT cs.rochester.edu) 
	
Improved and maintained by:
- Michele Filannino (filannim AT cs.manchester.ac.uk)

Feel free to contact for any help. ;)
'''

import re
import os
import sys
import commands 
import math
import pickle
from datetime import date 

##################################################################
############            PROCESS TIMEX VALUE            ###########
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
	today = date.today()
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
    
    #print month_start_end[start_month][0]

    start_date = (index - month_start_end[start_month][0] + 1) 
    #print (start_date + 7)
    #print days_in_month[start_month]

    end_date = (start_date + 7 - 1) % days_in_month[start_month]
    a = str(year) + '-' + get_date_str(start_month)+'-'+get_date_str(start_date) 
    b = str(year) + '-' + get_date_str(end_month)+'-'+get_date_str(end_date) 
    #print a, b
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
        # print 'w:'+str(i), week_range[i]
    week_range[53] = week_range[53][0], str(year)+'-12-31'
    # print 'w:53', week_range[53]
    return week_range 

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
    days_in_month = init_days_in_month(year) 
    new_day = day + diff 
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
	if len(str(hour))==1:
		value += 'T0' + str(hour) + ':' + str(minutes)
	else:
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
    # DEFAULT ONES
    value = 'X' 
    type = 'DATE' 
    ## handle DCT ## 
    year_re = '[12][0-9][0-9][0-9]'
    month_re = '[01][0-9]'
    day_re = '[0123][0-9]'
    hour_re = '[012][0-9]'
    minute_re = '[0123456][0-9]'
    
    # Handle "yyyymmdd"
    p = re.compile(year_re+'[\-|/]'+month_re+'[\-|/]'+day_re)
    if p.search(cons):
        val = cons.strip()  
        yr = val[0:4]
        mn = val[5:7]
        dt = val[8:10]
        value = get_date_value(yr, mn, dt)
        type = 'DATE' 
        return timex_str, type, value, 'DCT0'

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

    #### handle DATE type ####
    if cons == 'today': 
        value = date[0]+'-'+date[1]+'-'+date[2]
        type = 'DATE'
        return timex_str, type, value, 'today'
    if re.search(' now ', ' '+cons+' ') or cons == 'currently' or cons == 'at present' or re.search('moment', cons): 
        value = 'PRESENT_REF' 
        type = 'DATE'
        return timex_str, type, value, 'now' 
    if cons.strip() == 'one day' or re.search('future', cons.strip()) or re.search('coming', cons.strip()) : 
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
        hr = q.findall(cons)[0] 
        r = re.compile(':[0123456][0-9]')
        try:
        	min = r.findall(cons)[0] 
        	min = re.sub(':', '', min)
        except:
        	min = 0
        if re.search('p\.?m\.?', cons):             
            if int(hr) < 12: 
                hr = int(hr) + 12 
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
            value = str(dec)
            return timex_str, type, value, 'decade' 
        
    if re.search('decade ago', cons): 
        type = 'DATE' 
        value = get_date_value(year-10, month, day)
        return timex_str, type, value, 'decade-ago'    

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
            type = 'SET' 

        if re.search('morning', cons): 
            value = value + 'TMO' 
            type = 'TIME'
        if re.search('mornings', cons): 
            type = 'SET' 

        if re.search('afternoon', cons): 
            value = value + 'TAF' 
            type = 'TIME'
        if re.search('afternoons', cons): 
            type = 'SET' 

        if re.search('evening', cons): 
            value = value + 'TEV' 
            type = 'TIME'
        if re.search('evenings', cons): 
            type = 'SET'
        
        if re.search('[0-9]{2}( )?p.?m.?',cons):
            hours = int(re.findall('[0-9]{2}',cons)[0])+12
            value += 'T' + str(hours) + ':' + '00'
            type = 'TIME'
        
        if re.search('[0-9]{2}:[0-9]{2}( )?p.?m.?',cons):
        	hours = int(re.findall('[0-9]{2}',cons)[0])+12
        	minutes = int(re.findall('[0-9]{2}',cons)[1])+12
        	value += 'T' + str(hours) + ':' + minutes
        	type = 'TIME'
		
        return timex_str, type, value, 'DOWmic' 

    if re.search('night', cons): 
        value = get_date_value(year, month, day) +'TNI' 
        type = 'DATE' 
        return timex_str, type, value, 'night' 
    
    if re.search('morning', cons): 
        value = get_date_value(year, month, day) +'TMO' 
        type = 'DATE' 
        return timex_str, type, value, 'morning' 

    if re.search('evening', cons): 
        value = get_date_value(year, month, day) +'TEV' 
        type = 'DATE' 
        return timex_str, type, value, 'evening' 
    
    if re.search('afternoon', cons): 
        value = get_date_value(year, month, day) +'TAF' 
        type = 'TIME' 
        return timex_str, type, value, 'afternoon' 

	# Handle 'this century'
	if p.find('this century') > 0:
		return timex_str, 'DATE', 'P100Y', 'thisCentury'
        
    # nearly four years ago, three months ago, 10 days ago 
    number_one = 'one|two|couple|three|four|five|six|seven|eight|nine'
    number_two = 'ten|eleven|tweleve|thirteen|fourteen|fifteen|sixteen|seventeen|eighteen|nineteen' 
    number_three = 'twenty|thirty|forty|fifty|sixty|seventy|eighty|ninety|hundred|thousand' 
    num = '[0-9]+'
    number = '('+number_one+'|'+number_two+'|'+number_three + '|' + num+')'
    time_type = '(day|days|week|weeks|month|months|year|years|quarter)'
    
    p = re.compile(number + ' ' + time_type + '.* ago')
    if p.search(cons): 
        type = 'DATE' 
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
        elif re.search('day', foo_time): 
            value = add_date(day, month, year, -1*int(foo_num))
        elif re.search('month', foo_time):
            #print foo_num
            year_1 = foo_num / 12 
            month_1 = foo_num % 12 
            if month > month_1: 
                month = month - month_1 
                year = year + year_1
            else: 
                month = 12 + month - month_1 
                year = year + year_1 - 1 
            value = str(year) + '-' + pad_zero(month) 
        return timex_str, type, value, 'NUM TIME AGO' 

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
            # print foo_num
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
        type = 'SET' 
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
        value = 'PX'+str(foo) 
        return timex_str, type, value, 'several-recent' 
    

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
        # if cons == number:
            r1 = re.compile(number_three) 
            r2 = re.compile(number_one) 
            r3 = re.compile(number_two) 
            r4 = re.compile(num) 
            if r1.search(cons): 
                trace += 'r1'
                word1 = r1.findall(cons)[0]
                # print word1, cons
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
        type = 'DATE' 
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
        return timex_str, type, value, 'quarter' 

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
        # elif re.search('quarter', foo): 
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
                value = year.strip()[:3]+'X'# + '-XX-XX'
            return timex_str, type, value, 'Year' 
            # if year.strip() == cons.strip(): 
                # type = 'DATE' 
            # return timex_str, type, value, 'Year' 

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
    # if cons == (modifier+'?[ ]*'+number +'?[ ]*'+duration):
        type = 'DURATION' 
        q = re.compile(number) 
        if q.search(timex_str): 
        # if cons == number:
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
            else: 
                word4 = '0'

            num = get_number(word1) + get_number(word2) + get_number(word3) + int(word4)
             
        else:
            num = 'X'             
        r = re.compile(duration) 
        if r.search(cons): 
            foo_duration = r.findall(cons)[0].upper() 
            if re.search(' a '+ foo_duration.lower(), ' ' +timex_str.lower()+ ' '):
                num = '1' 
        # print cons, foo_duration
        if foo_duration[0] == 'H':
        	value = 'PT'+str(num)+foo_duration[0]
        else:
        	value = 'P'+str(num)+foo_duration[0]
        return timex_str, type, value, 'duration'+trace 

    # time, this time, some time, any time, 
    if re.search(' time ', ' ' + cons + ' '): 
        
        if cons == 'this time' or cons == 'time': 
            type = 'DATE'
            value = 'PRESENT_REF' 
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
            value = 'PRESENT_REF' 
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
        type = 'DATE' 
        value = 'PAST_REF' 
        return timex_str, type, value, 'then'

    # yet 
    if re.search(' yet ', ' ' + cons + ' '): 
        type = 'DATE' 
        value = 'PRESENT_REF' 
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
	pattern = re.compile('(about|around|more or less)')
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
	
	numbers_nl = 'one|two|three|four|five|six|seven|eight|nine|ten|eleven|twelve'
	period_nl = 'minute(s)?|hour(s)?|day(s)?|week(s)?|month(s)?|year(s)?|decade(s)?'

	if raw_expression in ('current', 'currently', 'now'):
		return cons, 'DATE', 'PRESENT_REF', 'current'
	
	if raw_expression == 'the weekend':
		return cons, 'DATE', 'PRESENT_REF', 'the weekend'
	
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
	
	if re.match('^(one)( |-)(day)$',raw_expression):
		return cons, 'DATE', 'FUTURE_REF', 'one day'
	
	if re.match('^(one)( |-)(week)$',raw_expression):
		return cons, 'DURATION', 'P1W', 'one week'
	
	if re.match('^(one)( |-)(month)$',raw_expression):
		return cons, 'DURATION', 'P1M', 'one month'
	
	if re.match('^(one)( |-)(year)$',raw_expression):
		return cons, 'DURATION', 'P1Y', 'one year'

	if re.match('^(daily)$',raw_expression):
		return cons, 'DURATION', 'P1D', 'daily'

	if re.match('^(annually|the year)$',raw_expression):
		return cons, 'DURATION', 'P1Y', 'annually'

	if re.match('^(monthly)$',raw_expression):
		return cons, 'DURATION', 'P1M', 'monthly'

	if re.match('^(weekly)$',raw_expression):
		return cons, 'DURATION', 'P1W', 'weekly'

	if re.match('^(hourly)$',raw_expression):
		return cons, 'DURATION', 'PT1H', 'hourly'

	if re.match('^(soon)$',raw_expression):
		return cons, 'DATE', 'FUTURE_REF', 'annually'
	
	if re.match('^(recent|recently)$',raw_expression):
		return cons, 'DATE', 'PAST_REF', 'recent'

	if re.match('^(recent (?:'+period_nl+'))$',raw_expression):
		return cons, 'DATE', 'PAST_REF', 'recent PERIOD'

	if re.match('^(from time to time)$',raw_expression):
		return cons, 'DATE', 'PRESENT_REF', 'from time to time'

	# TRANSFORMATION RULES
	if re.match('('+numbers_nl+')(-| )('+period_nl+')$',raw_expression):
		return get_timex_value(cons.replace('-',' '),date)
	
	if re.match('(week)$',raw_expression):
		return get_timex_value('1 '+cons,date)
	
	if re.match('(the )(year|week|decade|hour|month)$',raw_expression):
		return get_timex_value('this '+cons.split(' ')[1],date)
	
	if re.match('(the year)$',raw_expression):
		return get_timex_value('this year '+cons,date)
	
	if re.match('(the past )(year|month|day|week|decade)',raw_expression):
		return get_timex_value(raw_expression.replace('the past','the last'),date)
	
	if re.match('(the fiscal )(year|month|day|week|decade)',raw_expression):
		return get_timex_value(raw_expression.replace('the fiscal','the'),date)
	
	if re.match('^(the past )',raw_expression):
		return get_timex_value(raw_expression.replace('the past ',''),date)
	
	if re.match('^(the full )',raw_expression):
		return get_timex_value(raw_expression.replace('full ',''),date)
	
	if re.match('(noon)',raw_expression):
		return get_timex_value(raw_expression.replace('noon','12:00'),date)
	
	if re.match('^(earlier )',raw_expression):
		return get_timex_value(raw_expression.replace('earlier ',''),date)
	
	if re.match('^(the following )',raw_expression):
		return get_timex_value(raw_expression.replace('following','next'),date)
	
	if re.match('^(sometime )', raw_expression):
		result = get_timex_value(raw_expression.replace('sometime ',''),date)
		if re.match('\d\d\d\d',result[2]): # is a year
			return result[0], result[1], result[2]+'-XX-XX', 'sometime'
	
	if re.match('^(year(s)?(-)?(old)$)',raw_expression):
		return get_timex_value('one ' + raw_expression,date)
	
	if re.match('[a-zA-Z]*( )(year two)(-| )(thousand)$',raw_expression):
		raw_expression = raw_expression.replace('two thousand','2000')
		raw_expression = raw_expression.replace('two-thousand','2000')
		return get_timex_value(raw_expression,date)
	
	if re.match('^[0-9]?[0-9]( )?(a.?m.?|am|anti meridian)',raw_expression):
		if len(raw_expression.split(' ')[0]) == 1:
			value = raw_expression.replace(raw_expression.split(' ')[0],
										'0'+raw_expression.split(' ')[0]+':00')
		elif len(raw_expression.split(' ')[0]) == 2:
			value = raw_expression.replace(raw_expression.split(' ')[0],
										raw_expression.split(' ')[0]+':00')
		return get_timex_value(value,date)
	
	if re.match('^[0-9]?[0-9]( )?(p.?m.?|pm|post meridian)',raw_expression):
		value = int(raw_expression.split(' ')[0])+12
		if len(str(value)) == 2:
			cons = raw_expression.replace(raw_expression.split(' ')[0],
										str(value)+':00')
		else:
			cons = raw_expression.replace(raw_expression.split(' ')[0],
										'0' + str(value)+':00') 
		return get_timex_value(cons,date)
	
	if re.match('^[0-9]{6}$',raw_expression):
		if int(raw_expression[:2]) > 15:
			return get_timex_value('19'+raw_expression,date)
		else:
			return get_timex_value('19'+raw_expression,date)
	
	#	FESTIVITIES
	if re.match('(thanksgiving day)',raw_expression):
		return get_timex_value(raw_expression.replace('thanksgiving day',
													  date[0]+'/11/25'),date)
	
	# EXTENSIONS
	if re.match('(summer|winter|autumn|spring)', raw_expression):
		a,b,c,d = get_timex_value(cons)
		if not re.match('(su|wi|au|sp)',c[:-2]):
			if re.match('(summer)',raw_expression): return a, b, c+'-SU', d
			if re.match('(winter)',raw_expression): return a, b, c+'-WI', d
			if re.match('(autumn)',raw_expression): return a, b, c+'-AU', d
			if re.match('(spring)',raw_expression): return a, b, c+'-SP', d
		return a, b, c, 'seasons'
	
	return get_timex_value(cons.lower().strip(), date)

def main():
	'''
	raw_word = sys.argv[1]
	raw_date = sys.argv[2]
	raw_time = ''
	if re.match('[0-9]{8}T[0-9]{6}',raw_date):
		date = raw_date[0:4], raw_date[4:6], raw_date[6:8]
		time = raw_date[9:11], raw_date[11:13], raw_date[13:15]
	elif re.match('[0-9]{8}',raw_date):
		date = raw_date[0:4], raw_date[4:6], raw_date[6:8]
	print 'Temporal expression: \"%s\"' % raw_word
	print 'Utterance reference: %s at %s' % ('/'.join(date),':'.join(time))
	print 'RochesterNormalizer: %s' % (str(get_timex_value(raw_word,date)))
	'''
	#print normalise("last month", "20121212")

	raw_word = sys.argv[1]
	print normalise(raw_word, "20120608")

def most_common(lst):
    return max(set(lst), key=lst.count)

def check_from_golds(raw_word, golds):
	query_results = [e for e in golds if e[0].lower()==raw_word.lower()]
	if len(query_results) == 0:
		return raw_word, 'DATE', 'X', 'no way :('
	elif len(query_results) == 1:
		return raw_word, query_results[0][1], query_results[0][2], 'from golds'
	else:
		types = [t[1] for t in query_results]
		values = [t[2] for t in query_results]
		return raw_word, most_common(types), most_common(values), 'from golds (most common)'

def normalise(raw_word, raw_date):
	raw_time = ''
	date = get_date()
	if re.match('[0-9]{8}T[0-9]{6}',raw_date):
		date = raw_date[0:4], raw_date[4:6], raw_date[6:8]
		time = raw_date[9:11], raw_date[11:13], raw_date[13:15]
	elif re.match('[0-9]{8}',raw_date):
		date = raw_date[0:4], raw_date[4:6], raw_date[6:8]
	else:
		raise Exception('Invalid date format!')
	try:
		result = higher_tier(raw_word,date)
		if result[1]=="DATE" and result[2]=="X" and result[3]=="default":
			golds = pickle.load(open(os.path.abspath('/home/filannim/Dropbox/Workspace/TempEval-3/components/normalisers/gold_human_timexes.pickle'),'r'))
			result = check_from_golds(raw_word, golds)
	except Exception:
		#print 'This script still contains bloody bugs!'
		raise
	return result

if __name__ == '__main__':
	main()
