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
from collections import Counter
from collections import defaultdict
import pickle
import sys
import os
from os import listdir
from os.path import abspath

def word(line):
	return line[0]

def lemma(line):
	return line[37]

def temp_patterns(line):
	return '|'.join(line[45:70])

def prediction(line):
	return line[-1]

def get_scale_factors(file_name):
	"""Let's calculate p('O-TIMEX3' | 'Monday' AND pre'O-TIMEX' AND post'O-TIMEX')
	"""
	input = open(file_name, 'r').readlines()
	input = [line.strip().split('\t') for line in input]

	frequency = dict()
	times = Counter()

	for num_line, line in enumerate(input[1:-1]):
		if len(line)>1:
			prev_line = input[num_line-1]
			next_line = input[num_line+1]
			curr_word = word(line)
			prev_prediction = prediction(prev_line)
			next_prediction = prediction(next_line)
			curr_prediction = prediction(line)
			
			frequency.setdefault(curr_word, defaultdict(float))
			frequency[curr_word][curr_prediction] += 1.0
			times[curr_word] += 1.0

	returned_factors = dict()
	for a in frequency.keys():
		for b in frequency[a].keys():
			if frequency[a]['I-TIMEX3']+frequency[a]['B-TIMEX3'] >= 2.0:
				returned_factors.setdefault(a, defaultdict(float))
				returned_factors[a][b] = frequency[a][b] / times[a]

	return returned_factors

def main():
	file_name = abspath(sys.argv[1])
	sf = get_scale_factors(file_name)
	print len(sf)
	pickle.dump(sf, open('../stats/factors.pickle','w'))

if __name__ == '__main__':
	main()