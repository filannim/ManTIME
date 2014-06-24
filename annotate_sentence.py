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
from datetime import datetime
import multiprocessing
from multiprocessing import Pool
import os
from os import listdir
from os.path import abspath
from os.path import basename
from os.path import dirname
import sys
import tempfile


import components.nlp_functions
from components.feature_factory import FeatureFactory
from components.KMP import KMP
from components.nlp_functions import NLP
from components.text_extractor import TextExtractor
from components.tagger import Tagger
from components.normalisers.general_timex_normaliser import normalise as generally_normalise


def annotate(sentence, utterance=None, debug=False):
	now = datetime.now()
	month = str(now.month) if len(str(now.month))==2 else '0'+str(now.month)
	day = str(now.day) if len(str(now.day))==2 else '0'+str(now.day)
	os.chdir(os.path.dirname(os.path.abspath(__file__)))
	with tempfile.NamedTemporaryFile('w+t', delete=False) as bf:
		if utterance:
			bf.write(utterance)
		else:
			utterance = ''.join([str(now.year), month, day])
			bf.write(utterance)
	te = TextExtractor();
	ff = FeatureFactory();
	tagger = Tagger();
	start_id = 1
	month = str(now.month) if len(str(now.month))==2 else '0'+str(now.month)
	day = str(now.day) if len(str(now.day))==2 else '0'+str(now.day)
	#utterance = '-'.join([str(now.year), month, day])
	if debug: print 'UTTERANCE:', utterance
	sentence = sentence.replace('__space__', ' ').strip()
	if debug: print 'SENTENCE:', sentence
	sentence_iob = ff.getFeaturedSentence([sentence, {'TIMEX3':[]}], 'TIMEX3', True, debug=False)
	tagged = tagger.tag(sentence, sentence_iob, utterance, start_id, buffer=bf.name, withPipeline=True, debug=False)
	if debug: print 'TAGGED:', tagged
	os.remove(bf.name)
	return tagged['sentence'], tagged['tags']

def main():
	# Path check
	try:
		sentence = sys.argv[1]
	except:
		print '\033[1m'+'SYNOPSIS:'+'\033[0m'
		print '>> python ' + sys.argv[0] + ' <sentence>'
		print
		print '\033[1m'+'DESCRIPTION:'+'\033[0m'
		print 'It annotates the given sentence using today time as utterance time.'
		print 
		return None

	result = annotate(sentence)
	print result

	# TEST
	# pipeline(['/Users/michele/Dropbox/Workspace/ManTIME/data/test/test.tml.TE3input'], post_processing, debug=False)


if __name__ == '__main__':
	main()
