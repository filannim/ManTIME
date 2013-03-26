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
import commands
from cgi import escape
import json
import nltk
import os
from os import listdir
import pickle
import random
import re
from StringIO import StringIO
import sys

import nlp_functions
from feature_factory import FeatureFactory
from nlp_functions import NLP
from nlp_functions import TreeTaggerTokeniser
from normalisers.general_timex_normaliser import normalise as generally_normalise
from text_extractor import TextExtractor
from properties import property as paths

class Tagger(object):

	def __init__(self):
		self.crf_path = paths['path_crf++']
		self.crf_timex_model = paths['path_crf++_model']
		self.crf_consistency_module = paths['path_consistency_module']
		self.crf_adjustment_module = paths['path_adjustment_module']

	def identify(self, sentence, IOB, debug=False):
		file_name = '/tmp/sentence_' + str(random.randint(0,9999999999)) + '.tmp'
		IOB_saved = open(file_name,'w')
		# Writing the IOB without header
		header = IOB.split('\n')[0]
		content = '\n'.join(IOB.split('\n')[1:])
		IOB_saved.write(content)
		IOB_saved.close()
		#Lets call CRF++
		command = self.crf_path + 'crf_test -m ' + self.crf_timex_model + ' ' + file_name
		#command = self.crf_path + 'crf_test -v2 -m ' + self.crf_timex_model + ' ' + file_name + ' | '
		#command += 'python ' + self.crf_adjustment_module + ' 0.5 "perturbate" | '
		#command += 'python ' + self.crf_consistency_module + ' "OI,BB,IB" | '
		#command += 'python ' + self.crf_adjustment_module + ' 0.87 "threshold_adjustment" | '
		#command += 'python ' + self.crf_consistency_module + ' "OI,BB,IB" | '
		#command += 'python ' + self.crf_consistency_module + ' "OI,BB,IB"'
		predictions = commands.getoutput(command)
		annotated_tokens = [(escape(line.split('\t')[0]), line.split('\t')[-1]) for line in predictions.split('\n')]
		if debug: print 'ANNOTATIONS:', annotated_tokens
		to_annotate = []
		sentence_character_pointer = 0
		if debug: print 'SENTENCE:', sentence
		for token, prediction in annotated_tokens:
			print token, sentence
			start = sentence.index(token, sentence_character_pointer)
			if prediction.startswith('B'):
				to_annotate.append([start,start+len(token),header.split('\t')[-1]])
			elif prediction.startswith('I'):
				try:
					to_annotate[-1][1] = start+len(token)
				except:
					to_annotate.append([start, start+len(token),header.split('\t')[-1]])
			sentence_character_pointer += len(token) + (start-sentence_character_pointer)
			if debug: print to_annotate, token, prediction, sentence_character_pointer
		os.remove(file_name)
		return to_annotate

	def tag(self, sentence, IOB, utterance, start_id=0, debug=False):
		sentence = escape(sentence)
		offsets = self.identify(sentence, IOB, debug=debug)
		annotated_sentence = list(sentence)
		displacement = 0
		for start, end, tag in offsets:
			timex_text = annotated_sentence[int(int(start)+displacement):int(int(end)+displacement)]
			try:
				_, timex_type, timex_value, _ = generally_normalise(''.join(timex_text), utterance.replace('-',''))
				if timex_type == 'NONE': timex_type = 'DATE'
				if timex_value == 'NONE': timex_value = 'X'
			except:
				timex_value = 'X'
				timex_type = 'DATE'
			#Complete annotation:	opening_tag = '<%s tid="t%d" type="%s" functionInDocument="%s" temporalFunction="%s" value="%s">' % (tag, start_id, timex_type, 'NONE', 'false', timex_value)
			opening_tag = '<%s tid="t%d" type="%s" value="%s">' % (tag, start_id, timex_type, timex_value)
			closing_tag = '</%s>' % (tag) 
			annotated_sentence.insert(int(start)+displacement, opening_tag)
			annotated_sentence.insert(int(end)+1+displacement, closing_tag)
			start_id += 1
			displacement += 2
		return {'sentence':''.join(annotated_sentence), 'start_id':start_id, 'tagged':bool(len(offsets))}