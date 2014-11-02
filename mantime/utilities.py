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
                key[current_position] != key[current_position-shift]:
            shift += shifts_table[current_position-shift]
        shifts_table[current_position+1] = shift
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


def apply_gazetteer(sentence, gazetteer, case_sensitive=False):
    '''It returns a list of indexes corresponding to the beginning of a
    found *gazetteer* item in the *sentence*.'''
    # TO-DO: If I use a Trie structure for each gazetteer, I should save
    #        a bit of computational time.
    case = lambda text: text.lower() if case_sensitive else text
    indexes = []
    sentence = case(sentence)
    for item in gazetteer:
        indexes.extend(search_subsequence(sentence, case(item), end=True))
    return sorted(indexes)


def matching_gazetteer(gazetteer, sentence):
    word_forms = [token.word_form for token in sentence.words]
    matchings = set()
    for gazetteer_item in gazetteer:
        subsequences = search_subsequence(word_forms, gazetteer_item)
        if subsequences:
            for subsequence_start in subsequences:
                subsequence_end = subsequence_start + len(gazetteer_item)
                matchings.update(range(subsequence_start, subsequence_end))
    return __format(matchings, len(word_forms))


def __format(matching_elements, length):
    from extractors import WordBasedResult
    from extractors import SentenceBasedResult

    assert type(length) == int
    assert type(matching_elements) == set

    if matching_elements:
        assert max(matching_elements) <= length
        matching_elements = sorted(matching_elements)
        result = []
        for index in xrange(length):
            if matching_elements:
                if index == matching_elements[0]:
                    result.append(WordBasedResult('I'))
                    matching_elements.pop(0)
                else:
                    result.append(WordBasedResult('O'))
            else:
                result.append(WordBasedResult('O'))
        return SentenceBasedResult(tuple(result))
    else:
        return SentenceBasedResult(tuple([WordBasedResult('O')]*length))


class Memoize(object):
    """Memoization utility."""

    def __init__(self, function):
        self.function = function
        self.memo = {}

    def __call__(self, *args):
        if args not in self.memo:
            self.memo[args] = self.function(*args)
        return self.memo[args]


def main():
    '''Test code'''
    assert list(search_subsequence('', 'come')) == []
    assert list(search_subsequence('caraamicamiacomestai', 'come')) == [12]
    assert list(search_subsequence('caraamicamiacomestai', 'amico')) == []
    assert list(search_subsequence('caraamicamiacomestai', 'am')) == [4, 8]
    assert list(search_subsequence([4, 8, 5, 6, 4, 8], [4, 8])) == [0, 4]

if __name__ == '__main__':
    main()
