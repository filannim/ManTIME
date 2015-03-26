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
import cPickle
import inspect
import logging

from model_extractors import WordBasedResult
from model_extractors import WordBasedResults
from model_extractors import SentenceBasedResult
from model_extractors import SentenceBasedResults
from extractors import WordBasedExtractors
from extractors import SentenceBasedExtractors
from extractors import DocumentBasedExtractors


class AttributesExtractor(object):
    """This class is a generic AttributesExtractor. In the future we can have
       muliple of them, each one dedicated to the identification of particular
       tasks: timexes, events, people, treatments, and so on.

       An AttributeExtractor contains sentence attributes extractors and word
       attributes extractor.
    """
    def __init__(self):
        self.document_extractors = []
        self.sentence_extractors = []
        self.word_extractors = []

    def __name_attr(self, type, num, name):
        return '{num:0>3}_{type}_{name}'.format(num=num, type=type, name=name)

    def __extract_from_word(self, word, attribute_number, level='word'):
        for word_extractor in self.word_extractors:
            extractor_result = word_extractor(word)
            if type(extractor_result) == WordBasedResult:
                attribute_name = self.__name_attr(level,
                                                  attribute_number,
                                                  word_extractor.func_name)
                word.attributes[attribute_name] = extractor_result.value
                attribute_number += 1
            elif type(extractor_result) == WordBasedResults:
                for attribute_name, attribute_value in extractor_result.values:
                    attribute_name = self.__name_attr(level,
                                                      attribute_number,
                                                      attribute_name)
                    word.attributes[attribute_name] = attribute_value
                    attribute_number += 1
            else:
                print extractor_result, type(extractor_result)
                raise Exception('Unexpected word-based attribute-value type.')
        return attribute_number

    def __extract_from_sentence(self, sentence, attribute_number,
                                level='sentence'):
        for sentence_extrator in self.sentence_extractors:
            extractor_result = sentence_extrator(sentence)
            if type(extractor_result) == SentenceBasedResult:
                assert len(extractor_result.values) == len(sentence.words)
                for word_num, word_value in enumerate(extractor_result.values):
                    word = sentence.words[word_num]
                    attr_name = self.__name_attr(level,
                                                 attribute_number,
                                                 sentence_extrator.func_name)
                    word.attributes[attr_name] = word_value.value
                attribute_number += 1
            elif type(extractor_result) == SentenceBasedResults:
                assert len(extractor_result.values) == len(sentence.words)
                for word_num, word_values in enumerate(extractor_result.values):
                    num_attributes = 0
                    for (attr_name, value) in word_values:
                        word = sentence.words[word_num]
                        attr_name = self.__name_attr(level,
                                                     attribute_number,
                                                     attr_name)
                        word.attributes[attr_name] = value.value
                        attribute_number += 1
                        num_attributes += 1
                    attribute_number -= num_attributes
                attribute_number = attribute_number + num_attributes + 1
            else:
                raise Exception('Unexpected sentence-based ' +
                                'attribute-value type.')
        return attribute_number

    def __extract_from_document(self, document, attribute_number,
                                level='document'):
        return attribute_number

    def extract(self, document):
        """It returns an updated word with all the attributes extractors
           applied on the word.
        """
        # document-based extractors
        doc_attr_number = self.__extract_from_document(document, 0)
        for sentence in document.sentences:
            # sentence-based extractors
            sent_attr_number = self.__extract_from_sentence(sentence,
                                                            doc_attr_number)
            for word in sentence.words:
                # word-based extractors
                self.__extract_from_word(word, sent_attr_number)
        logging.info('Attributes: extracted.')
        return document

    def store_caches(self):
        # all the extractors (word, sentence, document-level)
        extractors = self.word_extractors + self.sentence_extractors + \
            self.document_extractors
        pickle_path = lambda filename: '../buffer/extractors/{}'.format(filename)
        for extractor in extractors:
            try:
                cPickle.dump(extractor.cache,
                             open(pickle_path(extractor.__name__), 'w'))
                # print 'Extractor \'{}\'s cache SAVED.'.format(
                #     extractor.__name__)
            except AttributeError:
                # the extrator is not memoised
                # print 'Extractor \'{}\' not memoised.'.format(
                #     extractor.__name__)
                continue


class TimexesExtractor(AttributesExtractor):
    """This is what we had in ManTIME before the refactoring"""

    def __init__(self):
        super(TimexesExtractor, self).__init__()
        self.sentence_extractors = []
        self.word_extractors = []


class FullExtractor(AttributesExtractor):
    """This extractor should never be used since it contains all the possible
       features declared in ManTIME.
    """

    def __init__(self):
        '''Takes all the extractors (functions) declared in extractors.py.'''
        super(FullExtractor, self).__init__()
        self.document_extractors = [function[1] for function
                                    in inspect.getmembers(
                                        DocumentBasedExtractors,
                                        predicate=inspect.isfunction)]
        self.sentence_extractors = [function[1] for function
                                    in inspect.getmembers(
                                        SentenceBasedExtractors,
                                        predicate=inspect.isfunction)]
        self.word_extractors = [function[1] for function
                                in inspect.getmembers(
                                    WordBasedExtractors,
                                    predicate=inspect.isfunction)]


def main():
    '''Simple ugly non-elegant test.'''
    import sys
    import pprint
    from readers import TempEval3FileReader
    file_reader = TempEval3FileReader(annotation_format='IO')
    document = file_reader.parse(sys.argv[1])
    #extractor = FullExtractor()
    #extractor.extract(document)
    pprint.pprint(document.gold_annotations)
    for sentence in document.sentences:
        for word in sentence.words:
            #pprint.pprint(sorted(word.attributes.items()))
            pprint.pprint('({:5},{:5}) {:>20} > {:>10}'.format(
                word.character_offset_begin,
                word.character_offset_end,
                word.word_form,
                word.gold_label))

if __name__ == '__main__':
    main()
