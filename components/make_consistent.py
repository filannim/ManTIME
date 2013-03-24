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

from __future__ import division
import pprint
import sys

def word(line):
	return line.split('\t')[0].strip()

def lemma(line):
	return line.split('\t')[38].strip()

def gold(line):
	return line.split('\t')[-2].strip()[0]

def prediction(line):
	try:
		return line.split('\t')[-1].strip()[0]
	except:
		return '.'

def main():
	tags = sys.argv[1].split(',')
	pp = pprint.PrettyPrinter(indent=4)
	lines = []
	suspiciousBB = []
	suspiciousIB = []
	mistakes = []
	for line in sys.stdin:
		lines.append(line)

	skip_next_line = False
	#print "Polpettone loaded.\n"
	for num_line, line in enumerate(lines[0:-1]):
		if not skip_next_line:
			line = line.strip()
			next_line = lines[num_line+1].strip()
			skip_next_line = False
			if prediction(line)=='O' and prediction(next_line)=='I':
				mistakes.append([word(line),word(next_line)])
				if 'OI' in tags:
					print '\t'.join(line.split('\t')[0:-1])+'\t'+'B-TIMEX3'
				else:
					print line
			elif prediction(line)=='B' and prediction(next_line)=='B':
				suspiciousBB.append([word(line),word(next_line)])
				if 'BB' in tags:
					print line
					print '\t'.join(next_line.split('\t')[0:-1])+'\t'+'I-TIMEX3'
					skip_next_line = True
				else:
					print line
			elif prediction(line)=='I' and prediction(next_line)=='B':
				suspiciousIB.append([word(line),word(next_line)])
				if 'IB' in tags:
					print line
					print '\t'.join(next_line.split('\t')[0:-1])+'\t'+'I-TIMEX3'
					skip_next_line = True
				else:
					print line
			else:
				print line
		else:
			skip_next_line = False
	print next_line
	
	#print 'MISTAKES'; pp.pprint(mistakes)
	#print 'SUSPICIOUS BB'; pp.pprint(suspiciousBB)
	#print 'SUSPICIOUS IB'; pp.pprint(suspiciousIB)

	
if __name__ == '__main__':
	main()