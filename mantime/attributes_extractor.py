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

from utilities import apply_gazetteer
from extractors import WordBasedResult
from extractors import WordBasedResults
from extractors import SentenceBasedResult


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

    def __get_attr_name(type, num, name):
            return '{type}_{num}_{name}'.format(type=type, num=num, name=name)

    def __extract_from_word(self, word, attribute_number, level='word'):
        for word_extractor in self.word_extractors:
            extractor_result = word_extractor(word)
            if type(extractor_result) == WordBasedResult:
                attribute_name = self.__get_attr_name(level,
                                                      attribute_number,
                                                      word_extractor.func_name)
                extractor_result.apply(word, attribute_name)
            elif type(extractor_result) == WordBasedResults:
                for attribute_name, attribute_value in extractor_result:
                    attribute_name = self.__get_attr_name(level,
                                                          attribute_number,
                                                          attribute_name)
                    attribute_value.apply(word, attribute_name)
                    attribute_number += 1
            else:
                raise Exception('Unexpected word-based attribute-value type.')
            attribute_number += 1
        return attribute_number

    def __extract_from_sentence(self, sentence, attribute_number,
                                level='sentence'):
        return attribute_number

    def __extract_from_document(self, document, attribute_number,
                                level='document'):
        return attribute_number

    def extract(self, document):
        """It returns an updated word with all the attributes extractors
           applied on the word.
        """
        # document-based extractors
        attribute_number = self.__extract_from_document(document, 0)
        for sentence in document.sentences:
            # sentence-based extractors
            attribute_number = self.__extract_from_sentence(sentence,
                                                            attribute_number)
            for word in sentence.words:
                # word-based extractors
                attribute_number = self.__extract_from_word(word,
                                                            attribute_number)


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
        self.stopwords = 
