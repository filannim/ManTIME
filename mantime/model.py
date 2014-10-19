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

'''It contains the classes for the document data model of ManTIME.'''


def __format_annotation(start_token, end_token, annotations, annotation_format):
    '''It returns the correct sequence class label for the given token.'''
    sequence_label = None
    tag_fired = ''
    for tag, _, (start_offset, end_offset) in annotations:
        tag_fired = tag
        if (start_offset, end_offset) == (start_token, end_token):
            sequence_label = 'W'
            break
        elif end_offset == end_token:
            sequence_label = 'E'
            break
        elif start_offset == start_token:
            sequence_label = 'B'
            break
        elif start_offset < start_token and end_offset > end_token:
            sequence_label = 'I'
            break
        else:
            sequence_label = 'O'
    if sequence_label not in list(annotation_format):
        sequence_label = 'I'
    if sequence_label == 'O':
        return sequence_label
    else:
        return sequence_label + '-' + tag_fired


class Document(object):
    '''It represents the root of a parsed document.'''

    def __init__(self, name, file_path='', dct=None):
        self.name = name
        self.file_path = file_path
        self.dct = dct
        self.text = ''
        self.gold_annotations = []
        self.predicted_annotations = []
        self.children = []
        self.stanford_tree = {}
        self.attributes = dict()
        self.annotation_format = ''

    def store_gold_annotations(self, annotation_format):
        """Enriching the Stanford Parser output with gold annotations."""
        import copy
        tree = self.stanford_tree
        for num_sentence, sentence in enumerate(tree['sentences']):
            new_sentence = copy.deepcopy(sentence)
            for num_word, (_, attributes) in enumerate(new_sentence['words']):
                new_sentence['words'][num_word][1]['CLASS'] = \
                    __format_annotation(
                        int(attributes['CharacterOffsetBegin']),
                        int(attributes['CharacterOffsetEnd']),
                        self.gold_annotations,
                        annotation_format)
            tree['sentences'][num_sentence] = new_sentence
        self.annotation_format = annotation_format

    def __str__(self):
        return self.__dict__

    def __repr__(self):
        return repr(self.__dict__)


class Classifier(object):
    """
    """
    def __init__(self):
        pass


class AttributesExtractor(object):
    """
    """
    def __init__(self):
        pass
