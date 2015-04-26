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

''' This module contains general utility functions.'''

from __future__ import generators
import collections
import copy
import md5
import os


class Mute_stderr(object):
    '''A context manager for doing a "deep suppression" of stderr.

    It will suppress all print, even if the print originates in a compiled
    C/Fortran sub-function. This will not suppress raised exceptions.
    '''
    def __init__(self):
        # Open a pair of null files
        self.null_fds = os.open(os.devnull, os.O_RDWR)
        # Save the actual stderr file descriptors.
        self.save_fds = os.dup(2)

    def __enter__(self):
        """Assign the null pointers to stderr."""
        os.dup2(self.null_fds, 2)

    def __exit__(self, *_):
        """Re-assign the real stderr back (2)."""
        os.dup2(self.save_fds, 2)
        # Close the null file
        os.close(self.null_fds)


def deephash(obj):
    '''
    Makes a hash from a dictionary, list, tuple or set to any level, that
    contains only other hashable types (including any lists, tuples, sets, and
    dictionaries). In the case where other kinds of objects (like classes) need
    to be hashed, pass in a collection of object attributes that are pertinent.
    For example, a class can be hashed in this fashion:

    make_hash([cls.__dict__, cls.__name__])

    A function can be hashed like so:

    make_hash([fn.__dict__, fn.__code__])
    '''
    if type(obj) == type(object.__dict__):
        obj_2 = {}
        for key, value in obj.items():
            obj_2[key] = value
        obj = obj_2

    if isinstance(obj, (set, tuple, list)):
        return hash(tuple([deephash(elem) for elem in obj]))
    elif not isinstance(obj, dict):
        return hash(obj)
    else:
        new_obj = copy.deepcopy(obj)
        for key, value in new_obj.items():
            new_obj[key] = deephash(value)
        return hash(tuple(frozenset(sorted(new_obj.items()))))


def search_subsequence(sequence, key, end=False):
    '''Yields all the start positions of the *key* in the *sequence*.

    Calling conventions are similar to string.find, but its arguments can be
    lists or iterators, not just strings, it returns all matches, not just
    the first one, and it does not need the whole text in memory at once.
    Whenever it yields, it will have read the text exactly up to and including
    the match that caused the yield.

    Keyword arguments:
    sequence -- input sequence
    key -- pattern searched for
    end -- flag used to return the ending sequence position too
    '''
    assert isinstance(sequence, collections.Iterable) and \
        isinstance(key, collections.Iterable)
    assert len(key) > 0, 'The key is empty.'
    if not key:
        return
    # build table of shift amounts
    shifts_table = [1] * (len(key) + 1)
    shift = 1
    for current_position in range(len(key)):
        while shift <= current_position and \
                key[current_position] != key[current_position - shift]:
            shift += shifts_table[current_position - shift]
        shifts_table[current_position + 1] = shift
    # do the actual search
    start_position = 0
    matched_lenght = 0
    for item in sequence:
        while matched_lenght == len(key) or \
                matched_lenght >= 0 and key[matched_lenght] != item:
            start_position += shifts_table[matched_lenght]
            matched_lenght -= shifts_table[matched_lenght]
        matched_lenght += 1
        if matched_lenght == len(key):
            if end:
                yield start_position, start_position + len(key) - 1
            else:
                yield start_position


def extractors_stamp():
    attributes_extractor_content = open('./attributes_extractor.py').read()
    md5_obj = md5.new()
    md5_obj.update(attributes_extractor_content)
    return md5_obj.digest()


def main():
    '''Test code'''
    assert list(search_subsequence('', 'come')) == []
    assert list(search_subsequence('caraamicamiacomestai', 'come')) == [12]
    assert list(search_subsequence('caraamicamiacomestai', 'amico')) == []
    assert list(search_subsequence('caraamicamiacomestai', 'am')) == [4, 8]
    assert list(search_subsequence([4, 8, 5, 6, 4, 8], [4, 8])) == [0, 4]

if __name__ == '__main__':
    main()
