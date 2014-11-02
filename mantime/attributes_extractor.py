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
import inspect

from utilities import apply_gazetteer
from extractors import WordBasedResult
from extractors import WordBasedResults
from extractors import SentenceBasedResult
from extractors import SentenceBasedResults


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

    def __name_attr(self, type, num, name):
        num = str(num).zfill(3)
        return '{num}_{type}_{name}'.format(num=num, type=type, name=name)

    def __extract_from_word(self, word, attribute_number, level='word'):
        for word_extractor in self.word_extractors:
            extractor_result = word_extractor(word)
            if type(extractor_result) == WordBasedResult:
                attribute_name = self.__name_attr(level,
                                                  attribute_number,
                                                  word_extractor.func_name)
                extractor_result.apply(word, attribute_name)
                attribute_number += 1
            elif type(extractor_result) == WordBasedResults:
                for attribute_name, attribute_value in extractor_result.values:
                    attribute_name = self.__name_attr(level,
                                                      attribute_number,
                                                      attribute_name)
                    attribute_value.apply(word, attribute_name)
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
                    word_value.apply(word, attr_name)
                    attribute_number += 1
            elif type(extractor_result) == SentenceBasedResults:
                assert len(extractor_result.values) == len(sentence.words)
                for word_num, word_values in enumerate(extractor_result.values):
                    original_attribute_number = attribute_number
                    for (attr_name, value) in word_values:
                        word = sentence.words[word_num]
                        attr_name = self.__name_attr(level,
                                                     attribute_number,
                                                     attr_name)
                        value.apply(word, attr_name)
                        attribute_number += 1
                    attribute_number = original_attribute_number
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
        super(FullExtractor, self).__init__()
        from extractors import WordBasedExtractors
        from extractors import SentenceBasedExtractors
        from extractors import DocumentBasedExtractors
        self.document_extractors = [function[1] for function in inspect.getmembers(DocumentBasedExtractors, predicate=inspect.isfunction)]
        self.sentence_extractors = [function[1] for function in inspect.getmembers(SentenceBasedExtractors, predicate=inspect.isfunction)]
        self.word_extractors = [function[1] for function in inspect.getmembers(WordBasedExtractors, predicate=inspect.isfunction)]


def main():
    '''Simple ugly non-elegant test.'''
    import sys
    import pprint
    from readers import TempEval3FileReader
    file_reader = TempEval3FileReader(annotation_format='IO')
    document = file_reader.parse(sys.argv[1])
    extractor = FullExtractor()
    extractor.extract(document)
    for sentence in document.sentences:
        for word in sentence.words:
            pprint.pprint(sorted(word.attributes.items()))
            

if __name__ == '__main__':
    main()
