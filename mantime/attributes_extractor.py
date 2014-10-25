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





class AttributesExtractor(object):
    """This class is a generic AttributesExtractor. In the future we can have
       muliple of them, each one dedicated to the identification of particular
       tasks: timexes, events, people, treatments, and so on.

       An AttributeExtractor contains sentence attributes extractors and word
       attributes extractor.
    """

    def __init__(self):
        self.sentence_extractors = []
        self.word_extractors = []

    def extract(self, word):
        """It returns an updated word with all the attributes extractors
           applied on the word.
        """
        for num, extractor in enumerate(self.word_extractors):
            func_name = '{type}_{num}_{name}'.format(type='word',
                                                     num=str(num),
                                                     name=extractor.func_name)
            # document-based extractors
            # sentence-based extractors

            # word-based extractors
            result = memoize(extractor(word.word_form))
            if type(result) == set:
                for attribute_name, attribute_value in result:
                    word.attributes[attribute_name] = str(attribute_value)
            else:
                word.attributes[func_name] = str(result)
        return word


class TimexesExtractor(AttributeExtractor):
    """This is what we had in ManTIME before the refactoring"""

    def __init__(self):
        super(TimexesExtractor, self).__init__()
        self.sentence_extractors = []
        self.word_extractors = [
            a,
            b,
            c,
            d,
            e,
            f,
            g]



#-----------------------------------------------------------------------------#
#-----OLD CODE----------------------------------------------------------------#
#-----------------------------------------------------------------------------#


class FeatureFactory(object):
    '''Provides methods to obtain an input table for a classifier'''

    def __init__(self):
        self.wordnet = nltk.corpus.wordnet
        self.stopwords = nltk.corpus.stopwords.words('english')
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

    def __compute_token_attributes(self, index, token, pos_tag, gazetteer_offsets, gold_labels):
        '''It returns the attribute table for the word.'''
        features = {}
        # GAZETTEERs
        features['gaz_stopword'] = True if token.lower() in self.stopwords else False
        for gazetteer_name, offsets in gazetteer_offsets.iteritems():
            features['gaz_'+gazetteer_name] = 'O-'+gazetteer_name
            for start, end in offsets:
                if index == start:
                    features['gaz_'+gazetteer_name] = 'B-'+gazetteer_name
                if index in range(start+1, end+1):
                    features['gaz_'+gazetteer_name] = 'I-'+gazetteer_name

        return features
