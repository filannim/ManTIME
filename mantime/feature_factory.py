#!/usr/bin/env python
#
#   Copyright 2014 Michele Filannino
#
#   gnTEAM, School of Computer Science, University of Manchester.
#   All rights reserved. This program and the accompanying materials
#   are made available under the terms of the GNU General Public License.
#
#   author: Michele Filannino
#   email:  filannim@cs.man.ac.uk
#
#   For details, see www.cs.man.ac.uk/~filannim/

'''This module collect attributes from a sentence.'''

from __future__ import division
import nltk
import pickle
import re

from utilities import apply_gazetteer
import nlp_functions
from nlp_functions import Parser
from nlp_functions import NLP
from nlp_functions import TreeTaggerTokeniser
from nlp_functions import TreeTaggerPOS


class Memoize(object):
    '''Memoization utility.'''

    def __init__(self, function):
        self.function = function
        self.memo = {}

    def __call__(self, *args):
        if args not in self.memo:
            self.memo[args] = self.function(*args)
        return self.memo[args]


class FeatureFactory(object):
    '''Provides methods to obtain an input table for a classifier'''

    def __init__(self):
        self.nlp = NLP()
        self.porterstemmer = Memoize(nltk.PorterStemmer().stem)
        self.lancasterstemmer = Memoize(nltk.LancasterStemmer().stem)
        self.wordnetlemmatiser = Memoize(nltk.WordNetLemmatizer().lemmatize)
        self.tokeniser = TreeTaggerTokeniser()
        self.postagger = TreeTaggerPOS()
        self.parser = Parser()
        self.phonemedictionary = nltk.corpus.cmudict.dict()
        self.wordnet = nltk.corpus.wordnet
        self.stopwords = nltk.corpus.stopwords.words('english')
        self.positivewords = pickle.load(
            open('gazetteer/positive_words.pickle'))
        self.negativewords = pickle.load(
            open('gazetteer/negative_words.pickle'))
        self.malenames = pickle.load(open('gazetteer/male.pickle'))
        self.femalenames = pickle.load(open('gazetteer/female.pickle'))
        self.countries = pickle.load(open('gazetteer/countries.pickle'))
        self.isocountries = pickle.load(open('gazetteer/isocountries.pickle'))
        self.uscities = pickle.load(open('gazetteer/uscities.pickle'))
        self.nationalities = pickle.load(
            open('gazetteer/nationalities.pickle'))
        self.festivities = pickle.load(open('gazetteer/festivities.pickle'))

    def get_sentence_attributes(self, sentence, gold_predictions, tag):
        '''It returns the features of *sentence* in IOB representation.'''
        attributes_values = []
        words = self.__compute_sentence_attributes(sentence, gold_predictions)
        attribute_names = sorted([e for e in words[0].keys() if e.islower()]) \
            + [e for e in words[0].keys() if e.isupper() and e == tag]
        for word in words:
            # if word[index] == None, the or stataments returns 'False'
            row = [str(word[index] or 'False') for index in attribute_names]
            attributes_values.append('{}'.format('\t'.join(row)))
        return attribute_names, attributes_values

    def __compute_sentence_attributes(self, sentence, gold_labels):
        '''It returns the attribute table for the sentence.'''
        attributes = []
        tokens = self.tokeniser.tokenize(sentence)
        # Use gazetteers at sentence level
        gazetteers = {}
        gazetteers['male_names'] = apply_gazetteer(self.malenames, tokens)
        gazetteers['female_names'] = apply_gazetteer(self.femalenames, tokens)
        gazetteers['countries'] = apply_gazetteer(self.countries, tokens)
        gazetteers['iso_countries'] = apply_gazetteer(
            self.isocountries, tokens)
        gazetteers['uscities'] = apply_gazetteer(self.uscities, tokens)
        gazetteers['nationalities'] = apply_gazetteer(
            self.nationalities, tokens)
        gazetteers['festivities'] = apply_gazetteer(self.festivities, tokens)
        # Shallow parsing (chunk) and Propositional Noun Phrases recognition
        parsing = Parser.parse(' '.join(tokens))
        pos_tags = self.postagger.tag(tokens)
        # For each token, compute the word level features
        features = {}
        for index, (token, pos_tag) in enumerate(pos_tags):
            features = self.__compute_token_attributes(index, token, pos_tag,
                                                       gazetteers, parsing,
                                                       gold_labels)
            attributes.append(features)
        return attributes

    def __compute_token_attributes(self, index, token, pos_tag, gazetteer_offsets, parsing_info, gold_labels):
        '''It returns the attribute table for the word.'''
        features = {}
        nlp = self.nlp.get(token)
        features['_word'] = token
        # features['_word_preprocessed'] = nlp.preprocessed_word()
        # LEXICAL
        features['lex_lemma'] = self.wordnetlemmatiser(token)
        features['lex_porter_stem'] = self.porterstemmer(token)
        features['lex_lancaster_stem'] = self.lancasterstemmer(token)
        features['lex_treetagger_pos'] = token or '_'
        features['lex_treetagger_lemma'] = pos_tag or '_'
        features['lex_unusual'] = nlp.unusual()
        features['lex_pattern'] = nlp.pattern()
        features['lex_vocal_pattern'] = nlp.vocal_pattern()
        features['lex_extended_pattern'] = nlp.extended_pattern()
        features['lex_has_digit'] = nlp.has_digit()
        features['lex_has_symbols'] = nlp.has_symbols()
        features['lex_prefix'] = token[0:-3] or token[0:-2] or token[0:-1]
        features['lex_suffix'] = token[-3:] or token[-2:] or token[-1:]
        features['lex_first_upper'] = token[0].isupper()
        features['lex_is_alpha'] = token.isalpha()
        features['lex_is_lower'] = token.islower()
        features['lex_is_digit'] = token.isdigit()
        features['lex_is_alnum'] = token.isalnum()
        features['lex_is_space'] = token.isspace()
        features['lex_is_title'] = token.istitle()
        features['lex_is_upper'] = token.isupper()
        features['lex_is_numeric'] = unicode(token).isnumeric()
        features['lex_is_decimal'] = unicode(token).isdecimal()
        features['lex_last_s'] = True if token[-1] == 's' else False
        features['lex_token_with_no_letters'] = nlp.no_letters()
        features['lex_token_with_no_letters_and_numbers'] = \
            nlp.no_letters_and_numbers()
        features['lex_is_all_caps_and_dots'] = nlp.is_all_caps_and_dots()
        features['lex_is_all_digits_and_dots'] = nlp.is_all_digits_and_dots()
        features['lex_tense'] = \
            nlp_functions.tense(features['lex_treetagger_pos'])
        if token.lower() in self.positivewords:
            features['lex_polarity'] = 'pos'
        elif token.lower() in self.negativewords:
            features['lex_polarity'] = 'neg'
        else:
            features['lex_polarity'] = 'neu'
        # Parsing information (chunks and PNP)
        features['lex_chunk'] = parsing_info[index][0]
        features['lex_pnp'] = parsing_info[index][1]
        # LEXICAL: temporal
        # TO DO: They should be checked at sentence level because of the
        #        punctuation (11:11 could be tokenised and never match the
        #        regex)
        features['temp_number'] = any(re.findall('^[0-9]+ ?(?:st|nd|rd|th)$', token.lower()))
        features['temp_time'] = any(re.findall('^([0-9]{1,2})[:\.\-]([0-9]{1,2}) ?(a\.?m\.?|p\.?m\.?)?$', token.lower()))
        features['temp_digit'] = any(re.findall('^[0-9]+$', token.lower()))
        features['temp_ordinal'] = any(re.findall('^(st|nd|rd|th)$', token.lower()))
        features['temp_year'] = any(re.findall('^[12][0-9]{3}|\'[0-9]{2,3}$', token.lower()))
        features['temp_literal_number'] = any(re.findall('^(zero|one|two|three|four|five|six|seven|eight|nine|ten|eleven|twelve|thirteen|fourteen|fifteen|sixteen|seventeen|eighteen|nineteen|twenty|twenty|thirty|forty|fifty|sixty|seventy|eighty|ninety|hundreds?|thousands?|)$', token.lower()))
        features['temp_cardinal'] = any(re.findall('^(first|second|third|fourth|fifth|sixth|seventh|eighth|nineth|tenth|eleventh|twelfth|thirteenth|fourteenth|fifteenth|sixteenth|seventeenth|eighteenth|nineteenth|twentieth|thirtieth|fortieth|fiftieth|sixtieth|seventieth|eightieth|ninetieth|hundredth|thousandth)$', token.lower()))
        features['temp_month'] = any(re.findall('^(january|february|march|april|may|june|july|august|september|october|november|december|jan|feb|mar|apr|may|jun|jul|aug|sept|oct|nov|dec)\.?$', token.lower()))
        features['temp_period'] = any(re.findall('^(centur[y|ies]|decades?|years?|months?|week\-?ends?|weeks?|days?|hours?|minutes?|seconds?|fortnights?|)$', token.lower()))
        features['temp_weekday'] = any(re.findall('^(monday|tuesday|wednesday|thursday|friday|saturday|sunday|wed|tues|tue|thurs|thur|thu|sun|sat|mon|fri)$', token.lower()))
        features['temp_pod'] = any(re.findall('^(morning|afternoon|evening|night|noon|midnight|midday|sunrise|dusk|sunset|dawn|overnight|midday|noonday|noontide|nightfall|midafternoon|daybreak|gloaming|a\.?m\.?|p\.?m\.?)s?$', token.lower()))
        features['temp_season'] = any(re.findall('^(winter|autumn|spring|summer)s?', token.lower()))
        features['temp_past_ref'] = any(re.findall('^(yesterday|ago|earlier|early|last|recent|nearly|past|previous|before)$', token.lower()))
        features['temp_present_ref'] = any(re.findall('^(tonight|current|present|now|nowadays|today|currently)$', token.lower()))
        features['temp_future_ref'] = any(re.findall('^(next|forthcoming|coming|tomorrow|after|later|ahead)$', token.lower()))
        features['temp_signal'] = any(re.findall('^(after|about|into|between|again|within|every|for|on|the|since|in|of|until|at|over|from|by|through|to|and|a)$', token.lower()))
        features['temp_fuzzy_quantifier'] = any(re.findall('^(approximately|approximate|approx|about|few|some|bunch|several|around)$', token.lower()))
        features['temp_modifier'] = any(re.findall('^(beginning|less|more|much|long|short|end|start|half)$', token.lower()))
        features['temp_temporal_adverbs'] = any(re.findall('^(daily|earlier)$', token.lower()))
        features['temp_temporal_adjectives'] = any(re.findall('^(early|late|soon|fiscal|financial|tax)$', token.lower()))
        features['temp_temporal_conjunctives'] = any(re.findall('^(when|while|meanwhile|during|on|and|or|until)$', token.lower()))
        features['temp_temporal_prepositions'] = any(re.findall('^(pre|during|for|over|along|this|that|these|those|than|mid)$', token.lower()))
        features['temp_temporal_co-reference'] = any(re.findall('^(dawn|time|period|course|era|age|season|quarter|semester|millenia|millenium|eve|festival|festivity)s?$', token.lower()))
        features['temp_festivity'] = any(re.findall('^(christmas|easter|epifany|martin|luther|thanksgiving|halloween|saints|armistice|nativity|advent|solstice|boxing|stephen|sylvester)$', token.lower()))
        features['temp_compound'] = any(re.findall('^[0-9]+\-(century|decade|year|month|week\-end|week|day|hour|minute|second|fortnight|)$', token.lower()))
        # WORDNET
        synsets = nlp.synsets
        features['wordnet_n_senses'] = len(synsets)
        features['wordnet_1_sense'] = str(synsets[0]) if len(synsets) else '_'
        features['wordnet_2_sense'] = str(synsets[1]) if len(synsets) > 1 else '_'
        lemma_names = nlp.wn_lemma_names()
        features['wordnet_lemma_name1'] = lemma_names[0] if len(lemma_names) else '_'
        features['wordnet_lemma_name2'] = lemma_names[1] if len(lemma_names) > 1 else '_'
        features['wordnet_lemma_name3'] = lemma_names[2] if len(lemma_names) > 2 else '_'
        features['wordnet_lemma_name4'] = lemma_names[3] if len(lemma_names) > 3 else '_'
        entailments = nlp.wn_entailments()
        features['wordnet_entailment1'] = entailments[0] if len(entailments) else '_'
        features['wordnet_entailment2'] = entailments[1] if len(entailments) > 1 else '_'
        features['wordnet_entailment3'] = entailments[2] if len(entailments) > 2 else '_'
        features['wordnet_entailment4'] = entailments[3] if len(entailments) > 3 else '_'
        antonyms = nlp.wn_antonyms()
        features['wordnet_antonym1'] = antonyms[0] if len(antonyms) else '_'
        features['wordnet_antonym2'] = antonyms[1] if len(antonyms) > 1 else '_'
        features['wordnet_antonym3'] = antonyms[2] if len(antonyms) > 2 else '_'
        features['wordnet_antonym4'] = antonyms[3] if len(antonyms) > 3 else '_'
        hypernyms = nlp.wn_hypernyms()
        features['wordnet_hypernym1'] = hypernyms[0] if len(hypernyms) else '_'
        features['wordnet_hypernym2'] = hypernyms[1] if len(hypernyms) > 1 else '_'
        features['wordnet_hypernym3'] = hypernyms[2] if len(hypernyms) > 2 else '_'
        features['wordnet_hypernym4'] = hypernyms[3] if len(hypernyms) > 3 else '_'
        hyponyms = nlp.wn_hyponyms()
        features['wordnet_hyponym1'] = hyponyms[0] if len(hyponyms) else '_'
        features['wordnet_hyponym2'] = hyponyms[1] if len(hyponyms) > 1 else '_'
        features['wordnet_hyponym3'] = hyponyms[2] if len(hyponyms) > 2 else '_'
        features['wordnet_hyponym4'] = hyponyms[3] if len(hyponyms) > 3 else '_'
        # PHONETIC
        phonemes = self.phonemedictionary.get(token.lower(), [''])[0]
        features['phon_form'] = '-'.join(phonemes) or '_'
        features['phon_length'] = len(phonemes)
        features['phon_first_phoneme'] = phonemes[0] if len(phonemes) else '_'
        features['phon_last_phoneme'] = phonemes[-1] if len(phonemes) else '_'
        # GAZETTEERs
        features['gaz_stopword'] = True if token.lower() in self.stopwords else False
        for gazetteer_name, offsets in gazetteer_offsets.iteritems():
            features['gaz_'+gazetteer_name] = 'O-'+gazetteer_name
            for start, end in offsets:
                if index == start:
                    features['gaz_'+gazetteer_name] = 'B-'+gazetteer_name
                if index in range(start+1, end+1):
                    features['gaz_'+gazetteer_name] = 'I-'+gazetteer_name
        # GOLD PREDICTIONs
        for gold_annotations, offsets in gold_labels.iteritems():
            features[gold_annotations.upper()] = 'O-' + gold_annotations.upper()
            for offset in offsets:
                if index == offset[0]:
                    features[gold_annotations.upper()] = 'B-' + gold_annotations.upper()
                if offset[0]+1 <= index <= offset[1]:
                    features[gold_annotations.upper()] = 'I-' + gold_annotations.upper()    

        return features
