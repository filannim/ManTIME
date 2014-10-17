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


def format_annotation(start_token, end_token, annotations, annotation_format):
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

    def __init__(self, name, dct=None):
        self.name = name
        self.dct = dct
        self.annotations = []
        self.children = []
        self.stanford_tree = {}
        self.attributes = dict()

    def push_classes(self, annotation_format):
        """Enriching the Stanford Parser output with annotations."""
        import copy
        tree = self.stanford_tree
        for num_sentence, sentence in enumerate(tree['sentences']):
            new_sentence = copy.deepcopy(sentence)
            for num_word, (_, attributes) in enumerate(new_sentence['words']):
                new_sentence['words'][num_word][1]['CLASS'] = format_annotation(
                    int(attributes['CharacterOffsetBegin']),
                    int(attributes['CharacterOffsetEnd']),
                    self.annotations,
                    annotation_format)
            tree['sentences'][num_sentence] = new_sentence

    def __str__(self):
        return self.__dict__

    def __repr__(self):
        return repr(self.__dict__)


class DocumentNode(Document):
    '''It represents a generic node of the parsed document.'''
    def __init__(self, start, end):
        super(DocumentNode, self).__init__('')
        self.start = start
        self.end = end

    def extract_features(self):
        '''It returns all the features.'''
        pass

    def __len__(self):
        return self.end - self.start

    def __str__(self):
        return ''.join([str(leave) for leave in self.leaves()])

    def __repr__(self):
        return '<node_{} lenght:{}>'.format(str(type(self)).lower(),
                                            len(list(self.leaves())))


class Section(DocumentNode):
    '''It represents a section of a parsed document.'''
    def __init__(self, start, end):
        super(Section, self).__init__(start, end)


class Sentence(DocumentNode):
    '''It represents a sequence of a parsed document.'''
    def __init__(self, start, end):
        super(Sentence, self).__init__(start, end)


class Token(DocumentNode):
    '''It represents a single token of a parsed document.'''
    def __init__(self, text, start, end, label):
        super(Token, self).__init__(start, end)
        self.text = text
        self.children = None
        self.labels = []
        if label:
            self.labels.append(label)

    def __str__(self):
        return str(self.text)

    def __repr__(self):
        return '<token {}, labels:{}>'.format(repr(self.text),
                                              str(self.labels))


class Gap(DocumentNode):
    '''It represents a delimiter character among nodes of a parsed document.'''
    def __init__(self, text, start, end):
        super(Gap, self).__init__(start, end)
        self.text = text
        self.children = None

    def __str__(self):
        return str(self.text)

    def __repr__(self):
        return '<gap {}>'.format(repr(self.text))
