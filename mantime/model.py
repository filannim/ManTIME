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


class Document(object):
    '''It represents the root of a parsed document.'''

    def __init__(self, name, dct=None):
        self.name = name
        self.dct = None
        self.children = []

    def add_child(self, child):
        '''It adds a *child* to a document node.'''
        assert isinstance(child, DocumentNode)
        self.children.append(child)

    def remove_child(self, child):
        '''It removes a *child* to a document node.'''
        self.children.pop(self.children.index(child))

    def leaves(self, leaf_type=object):
        '''It returns the very last element in the document hirearchy.'''
        for child in self.children:
            if child.children:
                for nephew in child.leaves(leaf_type=leaf_type):
                    yield nephew
            else:
                if isinstance(child, leaf_type):
                    yield child

    def __str__(self):
        return ''.join([str(leave) for leave in self.leaves()])

    def __repr__(self):
        return '<document lenght:{}>'.format(len(list(self.leaves())))


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
                                            len(list(self.leaves)))


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
    def __init__(self, text, start, end):
        super(Token, self).__init__(start, end)
        self.text = text
        self.children = None

    def __str__(self):
        return str(self.text)

    def __repr__(self):
        return '<token {}>'.format(repr(self.text))


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
