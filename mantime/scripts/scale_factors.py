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

'''It computes the scale factors.'''

from __future__ import division
import csv
from collections import Counter
import pickle
import sys
from os.path import abspath
from os.path import isfile


def get_scale_factors(file_path):
    '''It returns a dictionary of words with their:
       p_word(label='O-TIMEX3').
    '''
    assert isfile(file_path), 'Input file doesn\'t exist.'
    scale_factors = dict()
    with open(file_path) as source:
        data = csv.reader(source, delimiter='\t')
        next(data)  # skip header
        for row in data:
            try:
                word, label = row[0], row[-1]
                scale_factors.setdefault(word, Counter(label))
                scale_factors[word][label] += 1.0
            except IndexError:  # skip empty lines which cannot be unpacked.
                continue
    # normalise scale_factors (counts)
    for word in scale_factors.keys():
        counts = sum(word.values())
        is_acceptable = (word['I-TIMEX3'] + word['B-TIMEX3']) >= 2.0
        if is_acceptable:
            for label in word.iterkeys():
                scale_factors[word][label] /= counts
        else:
            scale_factors.pop(word)
    return scale_factors


def main():
    '''It computes and save the scale factors on the disk.'''
    scale_factors = get_scale_factors(abspath(sys.argv[1]))
    pickle.dump(scale_factors, open(abspath(sys.argv[2]), 'w'))

if __name__ == '__main__':
    main()
