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
import itertools
import math
import pickle
import sys

def word(line):
	try:
		return line.split('\t')[0].strip()
	except:
		return ''

def lemma(line):
	return line.split('\t')[38].strip()

def gold(line):
	return line.split('\t')[-2].strip()[0]

def prediction(line):
	try:
		return line.split('\t')[-4].strip().split('/')[0]
	except:
		return '.'

def predictions(line):
	probs = line.split('\t')[-3:]
	probs = [a.split('/') for a in probs]
	probs = list(itertools.chain(*probs))
	probs = dict(zip(probs[0::2], probs[1::2]))
	for key in probs.keys():
		probs[key] = float(probs[key])
	return probs

def threshold_adjustment():
	# Threshold check
	try:
		threshold = float(sys.argv[1])
		if threshold>1.0 or threshold<0.0:
			raise NameError('Threshold out of range!')
	except:
		print '\033[1m'+'SYNOPSIS:'+'\033[0m'
		print '>> python ' + sys.argv[0] + ' <threshold eo [0.0,1.0]>'
		print 'Where\'s the source_directory?!?'
		print 
		return None
	
	factors = pickle.load(open('stats/factors.pickle'))
	lines = []
	for line in sys.stdin:
		lines.append(line)
	current_word = ''
	for num_line, line in enumerate(lines[0:-1]):
		line = line.strip()
		current_word = word(line) 
		if prediction(line)=='O':
			if current_word in factors.keys():
				new_tag = sorted(factors[current_word])[0]
				coeff = factors[current_word][new_tag]
				if coeff >= threshold and prediction(line)!=new_tag[0]:
					#print current_word, prediction(line), new_tag, coeff
					#print current_word, new_tag
					print '\t'.join(line.split('\t')[0:-1])+'\t'+new_tag
				else:
					print line
			else:
				print line
		else:
			print line

def perturbate_crf(debug=False):
	# Threshold check
	try:
		threshold = float(sys.argv[1])
		if threshold>1.0 or threshold<0.0:
			raise NameError('Threshold out of range!')
	except:
		print '\033[1m'+'SYNOPSIS:'+'\033[0m'
		print '>> python ' + sys.argv[0] + ' <threshold eo [0.0,1.0]>'
		print 'Where\'s the source_directory?!?'
		print 
		return None

	factors = pickle.load(open('stats/factors.pickle'))
	lines = []
	for line in sys.stdin:
		lines.append(line)
	current_word = ''
	for num_line, line in enumerate(lines):
		line = line.strip()
		if not (line.startswith('#') and len(line.split('\t'))==1):
			current_word = word(line) 
			if debug: print 'PREDICTION:', prediction(line)[0]
			if prediction(line)[0]=='O':
				if debug: print 'CURRENTWORD:', current_word
				if current_word in factors.keys():
					new_tags = {}
					if debug: print 'PREDICTIONS:', predictions(line)
					for IOB in predictions(line).keys():
						new_tags[IOB] = (predictions(line)[IOB]*threshold) + (factors[current_word][IOB]*(1-threshold))
					if debug: print 'NEW_TAGS:', new_tags
					new_tag = sorted(new_tags)[0]	#take just the first character
					if new_tags[new_tag] >= threshold and prediction(line)[0]!=new_tag[0]:
						#print current_word, prediction(line), new_tag, new_tags[new_tag]
						if debug: print 'FACTORS:', factors
						print '\t'.join(line.split('\t')[0:-4])+'\t'+new_tag
					else:
						print '\t'.join(line.split('\t')[0:-4])+'\t'+prediction(line)
				else:
					print '\t'.join(line.split('\t')[0:-4])+'\t'+prediction(line)
			else:
				if not len(current_word):
					print
				else:
					print '\t'.join(line.split('\t')[0:-4])+'\t'+prediction(line)

def main():
	# Path check
	try:
		algorithm = sys.argv[2]
	except:
		print '\033[1m'+'SYNOPSIS:'+'\033[0m'
		print '>> python ' + sys.argv[0] + ' <threshold>' + ' <algorithm_name>'
		print 
		print '\033[1m'+'EXAMPLE:'+'\033[0m'
		print '>> python ' + sys.argv[0] + ' 0.5' + ' "perturbate"'
		return None
	
	if algorithm == 'perturbate':
		perturbate_crf(debug=False)
	elif algorithm == 'threshold_adjustment':
		threshold_adjustment()
	else:
		raise NameError('Algorithm name invalid!')
	
if __name__ == '__main__':
	main()