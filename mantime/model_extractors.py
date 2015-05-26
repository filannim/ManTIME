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

import types


class WordBasedResult(object):

    def __init__(self, value):
        assert type(value) in (types.NoneType, str, unicode, bool, int, float)
        if isinstance(value, types.NoneType):
            self.value = '_'
        elif type(value) in (str, bool):
            self.value = '"{}"'.format(str(value).replace(' ', '_'))
        elif type(value) == unicode:
            self.value = u'"{}"'.format(unicode(value.replace(u'\xa0', u'_')))
        else:
            self.value = '{}'.format(str(value).replace(' ', '_'))
        self.value = self.value.replace(' ', '_')

    def __eq__(self, other):
        return self.value == other.value


class WordBasedResults(object):
    '''Wraps a tuple of results.

       Each result is a tuple having the following form:
       result = ('name_of_attribute', WordBasedResult(...))

    '''

    def __init__(self, values):
        assert type(values) == tuple
        self.values = values


class SentenceBasedResult(object):

    def __init__(self, values):
        assert type(values) == tuple, 'Wrong type for values'
        self.values = values


class SentenceBasedResults(object):

    def __init__(self, values):
        assert type(values) == tuple, 'Wrong type for values'
        self.values = values
