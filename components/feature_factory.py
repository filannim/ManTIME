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
import nltk
import pickle
import re

import KMP
import nlp_functions
from nlp_functions import NLP
from nlp_functions import TreeTaggerTokeniser
from nlp_functions import Parser
from properties import properties

class Memoize:
    def __init__(self, fn):
        self.fn = fn
        self.memo = {}
  
    def __call__(self, *args):
        if not self.memo.has_key(args):
            self.memo[args] = self.fn(*args)
        return self.memo[args]

class FeatureFactory(object):
	"""Provides methods to obtain an input table for a classifier"""

	def __init__(self):
		self.NLP = NLP()
		self.porterstemmer = Memoize(nltk.PorterStemmer().stem)
		self.lancasterstemmer = Memoize(nltk.LancasterStemmer().stem)
		self.wordnetlemmatiser = Memoize(nltk.WordNetLemmatizer().lemmatize)
		self.tokeniser = TreeTaggerTokeniser()
		self.parser = Parser()
		self.phonemedictionary = nltk.corpus.cmudict.dict()
		self.wordnet = nltk.corpus.wordnet
		self.stopwords = nltk.corpus.stopwords.words('english')
		self.positivewords = set(pickle.load(open('gazetteer/positive_words.pickle')))
		self.negativewords = set(pickle.load(open('gazetteer/negative_words.pickle')))
		self.malenames = pickle.load(open('gazetteer/male.pickle'))
		self.femalenames = pickle.load(open('gazetteer/female.pickle'))
		self.countries = pickle.load(open('gazetteer/countries.pickle'))
		self.isocountries = pickle.load(open('gazetteer/isocountries.pickle'))
		self.uscities = pickle.load(open('gazetteer/uscities.pickle'))
		self.nationalities = pickle.load(open('gazetteer/nationalities.pickle'))
		self.festivities = pickle.load(open('gazetteer/festivities.pickle'))

	def getFeaturedSentence(self, sentence, tag, print_header=True):
		iob_format = ''
		gold_predictions = sentence[1]
		words = self.computeSentenceFeatures(sentence[0], gold_predictions)
		indexes = sorted([e for e in words[0].keys() if e.islower()]) + [e for e in words[0].keys() if e.isupper() and e==tag]
		for word in words:
			if print_header:
				iob_format += '\t'.join(indexes) + '\n'
				print_header = False
			iob_format += '\t'.join([str(word[index] or 'False') for index in indexes]) + '\n'
		return iob_format

	def computeSentenceFeatures(self, sentence, gold_predictions):
		"""For each token in the sentence the compute feature vector"""
		sentence = sentence.replace('`','\\`')
		featuretable = []
		treetagger_path = properties['path_treetagger']
		# Tokenise
		tokens = self.tokeniser.tokenize(sentence)
		tokens = [t.replace('"','\\"') for t in tokens]	# " character escape
		tokens = [t.replace('`','\\`') for t in tokens]	# " character escape
		# POS-tagging (Tree-Tagger)
		sentence_as_echo_input = '"' + '\n'.join(tokens) + '"'
		command = 'echo ' + sentence_as_echo_input + ' | ' + treetagger_path
		sentence_tokenised = commands.getoutput(command)
		tokensTT = [line.split('\t') for line in sentence_tokenised.split('\n')]
		# Use gazetteers at sentence level
		gazetteers = {}
		gazetteers['male_names'] = self.spotfromgazetteer(self.malenames, tokens)
		gazetteers['female_names'] = self.spotfromgazetteer(self.femalenames, tokens)
		gazetteers['countries'] = self.spotfromgazetteer(self.countries, tokens)
		gazetteers['iso_countries'] = self.spotfromgazetteer(self.isocountries, tokens)
		gazetteers['uscities'] = self.spotfromgazetteer(self.uscities, tokens)
		gazetteers['nationalities'] = self.spotfromgazetteer(self.nationalities, tokens)
		gazetteers['festivities'] = self.spotfromgazetteer(self.festivities, tokens)

		# Shallow parsing (chunk) and Propositional Noun Phrases recognition
		# parsing = Parser.parse(' '.join(tokens))
		parsing = None

		# For each token, compute the word level features
		features = {}
		for index, token in enumerate(tokensTT):
			pos_lemma = [token[1],token[2]]
			features = self.computeWordFeatures(index, token[0], pos_lemma, gazetteers, parsing, gold_predictions)
			featuretable.append(features)
		return featuretable

	def spotfromgazetteer(self, gazetteer, sentence, casesensitive=False):
		# TO-DO: If I use a Trie structure for each gazetteer, I should save
		#        a bit of computational time.
		result = []
		if casesensitive:
			sentence = [e.lower() for e in sentence]
		for line in gazetteer:
			if casesensitive:
				line = [e.lower() for e in line]
			partialresult = [[x,len(line)-1+x] for x in KMP.KMP(sentence, line)]
			for e in partialresult:
				result.append(e) 
		return sorted(result)

	def computeWordFeatures(self, index, word, pos_lemma, gazetteer_offsets, parsing_info, gold_predictions):
		"""Plug all the features at word level"""
		# TODO: I need to use the memoisation from Downey's code
		# Directly on the function. If the function is called with parameters
		# already knonw, I will not compute features again.
		features = {}
		nlp = self.NLP.get(word)

		features['_word'] = word

		# LEXICAL
		features['lex_lemma'] = self.wordnetlemmatiser(word)
		features['lex_porter_stem'] = self.porterstemmer(word)
		features['lex_lancaster_stem'] = self.lancasterstemmer(word)
		features['lex_treetagger_pos'] = pos_lemma[0] or '_'
		features['lex_treetagger_lemma'] = pos_lemma[1] or '_'
		features['lex_unusual'] = nlp.unusual()
		features['lex_pattern'] = nlp.pattern()
		features['lex_vocal_pattern'] = nlp.vocal_pattern()
		features['lex_extended_pattern'] = nlp.extended_pattern()
		features['lex_has_digit'] = nlp.has_digit()
		features['lex_has_symbols'] = nlp.has_symbols()
		features['lex_prefix'] = word[0:-3] or word[0:-2] or word[0:-1]
		features['lex_suffix'] = word[-3:] or word[-2:] or word[-1:]
		features['lex_first_upper'] = word[0].isupper()
		features['lex_is_alpha'] = word.isalpha()
		features['lex_is_lower'] = word.islower()
		features['lex_is_digit'] = word.isdigit()
		features['lex_is_alnum'] = word.isalnum()
		features['lex_is_space'] = word.isspace()
		features['lex_is_title'] = word.istitle()
		features['lex_is_upper'] = word.isupper()
		features['lex_is_numeric'] = unicode(word).isnumeric()
		features['lex_is_decimal'] = unicode(word).isdecimal()
		features['lex_last_s'] = True if word[-1]=='s' else False
		features['lex_token_with_no_letters'] = nlp.no_letters()
		features['lex_token_with_no_letters_and_numbers'] = nlp.no_letters_and_numbers()
		features['lex_is_all_caps_and_dots'] = nlp.is_all_caps_and_dots()
		features['lex_is_all_digits_and_dots'] = nlp.is_all_digits_and_dots()
		features['lex_tense'] = nlp_functions.tense(features['lex_treetagger_pos'])
		if word.lower() in self.positivewords:
			features['lex_polarity'] = 'pos'
		elif word.lower() in self.negativewords:
			features['lex_polarity'] = 'neg'
		else:
			features['lex_polarity'] = 'neu'
		# Parsing information (chunks and PNP)
		features['lex_chunk'] = '_' #	parsing_info[index][0]
		features['lex_pnp'] = '_' #	parsing_info[index][1]

		# LEXICAL: temporal
		# TO DO: They should be checked at sentence level because of the
		#        punctuation (11:11 could be tokenised and never match the 
		#        regex)
		features['temp_number'] = any(re.findall('^[0-9]+ ?(?:st|nd|rd|th)$',word.lower()))
		features['temp_time'] = any(re.findall('^([0-9]{1,2})[:\.\-]([0-9]{1,2}) ?(a\.?m\.?|p\.?m\.?)?$',word.lower()))

		features['temp_digit'] = any(re.findall('^[0-9]+$',word.lower()))
		features['temp_ordinal'] = any(re.findall('^(st|nd|rd|th)$',word.lower()))
		features['temp_year'] = any(re.findall('^[12][0-9]{3}|\'[0-9]{2,3}$',word.lower()))
		features['temp_literal_number'] = any(re.findall('^(zero|one|two|three|four|five|six|seven|eight|nine|ten|eleven|twelve|thirteen|fourteen|fifteen|sixteen|seventeen|eighteen|nineteen|twenty|twenty|thirty|forty|fifty|sixty|seventy|eighty|ninety|hundreds?|thousands?|)$',word.lower()))
		features['temp_cardinal'] = any(re.findall('^(first|second|third|fourth|fifth|sixth|seventh|eighth|nineth|tenth|eleventh|twelfth|thirteenth|fourteenth|fifteenth|sixteenth|seventeenth|eighteenth|nineteenth|twentieth|thirtieth|fortieth|fiftieth|sixtieth|seventieth|eightieth|ninetieth|hundredth|thousandth)$',word.lower()))
		features['temp_month'] = any(re.findall('^(january|february|march|april|may|june|july|august|september|october|november|december|jan|feb|mar|apr|may|jun|jul|aug|sept|oct|nov|dec)\.?$',word.lower()))
		features['temp_period'] = any(re.findall('^(centur[y|ies]|decades?|years?|months?|week\-?ends?|weeks?|days?|hours?|minutes?|seconds?|fortnights?|)$',word.lower()))
		features['temp_weekday'] = any(re.findall('^(monday|tuesday|wednesday|thursday|friday|saturday|sunday|wed|tues|tue|thurs|thur|thu|sun|sat|mon|fri)$',word.lower()))
		features['temp_pod'] = any(re.findall('^(morning|afternoon|evening|night|noon|midnight|midday|sunrise|dusk|sunset|dawn|overnight|midday|noonday|noontide|nightfall|midafternoon|daybreak|gloaming|a\.?m\.?|p\.?m\.?)s?$',word.lower()))
		features['temp_season'] = any(re.findall('^(winter|autumn|spring|summer)s?',word.lower()))
		features['temp_past_ref'] = any(re.findall('^(yesterday|ago|earlier|early|last|recent|nearly|past|previous|before)$',word.lower()))
		features['temp_present_ref'] = any(re.findall('^(tonight|current|present|now|nowadays|today|currently)$',word.lower()))
		features['temp_future_ref'] = any(re.findall('^(next|forthcoming|coming|tomorrow|after|later|ahead)$',word.lower()))
		features['temp_signal'] = any(re.findall('^(after|about|into|between|again|within|every|for|on|the|since|in|of|until|at|over|from|by|through|to|and|a)$',word.lower()))
		features['temp_fuzzy_quantifier'] = any(re.findall('^(approximately|approximate|approx|about|few|some|bunch|several|around)$',word.lower()))
		features['temp_modifier'] = any(re.findall('^(beginning|less|more|much|long|short|end|start|half)$',word.lower()))
		features['temp_temporal_adverbs'] = any(re.findall('^(daily|earlier)$',word.lower()))
		features['temp_temporal_adjectives'] = any(re.findall('^(early|late|soon|fiscal|financial|tax)$',word.lower()))
		features['temp_temporal_conjunctives'] = any(re.findall('^(when|while|meanwhile|during|on|and|or|until)$',word.lower()))
		features['temp_temporal_prepositions'] = any(re.findall('^(pre|during|for|over|along|this|that|these|those|than|mid)$',word.lower()))
		features['temp_temporal_co-reference'] = any(re.findall('^(dawn|time|period|course|era|age|season|quarter|semester|millenia|millenium|eve|festival|festivity)s?$',word.lower()))
		features['temp_festivity'] = any(re.findall('^(christmas|easter|epifany|martin|luther|thanksgiving|halloween|saints|armistice|nativity|advent|solstice|boxing|stephen|sylvester)$',word.lower()))
		features['temp_compound'] = any(re.findall('^[0-9]+\-(century|decade|year|month|week\-end|week|day|hour|minute|second|fortnight|)$',word.lower()))

		# WORDNET
		synsets = nlp.synsets
		features['wordnet_n_senses'] = '_'	#len(synsets)
		features['wordnet_1_sense'] = '_'	#str(synsets[0]) if len(synsets) else '_'
		features['wordnet_2_sense'] = '_'	#str(synsets[1]) if len(synsets)>1 else '_'
		lemma_names = nlp.wn_lemma_names()
		features['wordnet_lemma_name1'] = '_'	#lemma_names[0] if len(lemma_names) else '_'
		features['wordnet_lemma_name2'] = '_'	#lemma_names[1] if len(lemma_names)>1 else '_'
		features['wordnet_lemma_name3'] = '_'	#lemma_names[2] if len(lemma_names)>2 else '_'
		features['wordnet_lemma_name4'] = '_'	#lemma_names[3] if len(lemma_names)>3 else '_'
		entailments = nlp.wn_entailments()
		features['wordnet_entailment1'] = '_'	#entailments[0] if len(entailments) else '_'
		features['wordnet_entailment2'] = '_'	#entailments[1] if len(entailments)>1 else '_'
		features['wordnet_entailment3'] = '_'	#entailments[2] if len(entailments)>2 else '_'
		features['wordnet_entailment4'] = '_'	#entailments[3] if len(entailments)>3 else '_'
		antonyms = nlp.wn_antonyms()
		features['wordnet_antonym1'] = '_'	#antonyms[0] if len(antonyms) else '_'
		features['wordnet_antonym2'] = '_'	#antonyms[1] if len(antonyms)>1 else '_'
		features['wordnet_antonym3'] = '_'	#antonyms[2] if len(antonyms)>2 else '_'
		features['wordnet_antonym4'] = '_'	#antonyms[3] if len(antonyms)>3 else '_'
		hypernyms = nlp.wn_hypernyms()
		features['wordnet_hypernym1'] = '_'	#hypernyms[0] if len(hypernyms) else '_'
		features['wordnet_hypernym2'] = '_'	#hypernyms[1] if len(hypernyms)>1 else '_'
		features['wordnet_hypernym3'] = '_'	#hypernyms[2] if len(hypernyms)>2 else '_'
		features['wordnet_hypernym4'] = '_'	#hypernyms[3] if len(hypernyms)>3 else '_'
		hyponyms = nlp.wn_hyponyms()
		features['wordnet_hyponym1'] = '_'	#hyponyms[0] if len(hyponyms) else '_'
		features['wordnet_hyponym2'] = '_'	#hyponyms[1] if len(hyponyms)>1 else '_'
		features['wordnet_hyponym3'] = '_'	#hyponyms[2] if len(hyponyms)>2 else '_'
		features['wordnet_hyponym4'] = '_'	#hyponyms[3] if len(hyponyms)>3 else '_'

		# PHONETIC
		phonemes = '_'	#self.phonemedictionary.get(word.lower(),[''])[0]
		features['phon_form'] = '_'	#'-'.join(phonemes) or '_'
		features['phon_length'] = '_'	#len(phonemes)
		features['phon_first_phoneme'] = '_'	#phonemes[0] if len(phonemes) else '_'
		features['phon_last_phoneme'] = '_'	#phonemes[-1] if len(phonemes) else '_'

		# GAZETTEERs
		features['gaz_stopword'] = True if word.lower() in self.stopwords else False
		for gazetteer_name, offsets in gazetteer_offsets.items():
			#IOB format is better!
			features['gaz_'+gazetteer_name] = 'O-'+gazetteer_name
			for offset in offsets:
				if index == offset[0]:
					features['gaz_'+gazetteer_name] = 'B-'+gazetteer_name
				if index in range(offset[0]+1,offset[1]+1):
					features['gaz_'+gazetteer_name] = 'I-'+gazetteer_name

		# GOLD PREDICTIONs
		for gold_annotations, offsets in gold_predictions.items():
			#IOB format is better!
			features[gold_annotations.upper()] = 'O-' + gold_annotations.upper()
			for offset in offsets:
				if index == offset[0]:
					features[gold_annotations.upper()] = 'B-' + gold_annotations.upper()
				if index in range(offset[0]+1,offset[1]+1):
					features[gold_annotations.upper()] = 'I-' + gold_annotations.upper()	

		return features