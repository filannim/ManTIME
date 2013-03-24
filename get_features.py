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
import sys
import os
from os import listdir

import components.nlp_functions
from components.feature_factory import FeatureFactory
from components.KMP import KMP
from components.nlp_functions import NLP
from components.nlp_functions import TreeTaggerTokeniser
from components.text_extractor import TextExtractor
from components.tagger import Tagger
from components.normalisers.general_timex_normaliser import normalise as generally_normalise


def main():
	# Path check
	try:
		path = sys.argv[1]
		if path.endswith('/'): path = path[:-1]
	except:
		print '\033[1m'+'SYNOPSIS:'+'\033[0m'
		print '>> python ' + sys.argv[0] + ' <source_directory>'
		print 'Where\'s the source_directory?!?'
		print 
		return None
	
	output = open(path + '/corpus.features', 'w')
	te = TextExtractor();
	ff = FeatureFactory();
	tagger = Tagger();
	start_id = 1

	files_to_process = [f for f in listdir(path) if f.endswith('.tml')]
	for file_id, file_name in enumerate(files_to_process):
		absolute_path = path + '/' + file_name
		print '%d/%d reading from disk %s' % (file_id+1, len(files_to_process), absolute_path)
		utterance = te.get_utterance(absolute_path)
		for sentence, offsets in te.read(absolute_path, ['TIMEX3','EVENT','SIGNAL']):
			sentence_iob = ff.getFeaturedSentence([sentence, offsets], 'TIMEX3', False)
			output.write(sentence_iob + '\n')
	
	output.close()

if __name__ == '__main__':
	main()