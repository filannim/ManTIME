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

'''It adjusts the sequencing labels predicted by CRF++.
   It can be useless with other Conditional Random Fields implementation that
   offer a specific flag to avoid wrong sequences.
'''

from __future__ import division
import sys


def make_consistent(row_iterator, tags):
    '''It yields consistent sequences of predicted labels in IOB format.'''
    attributes_values = lambda line: '\t'.join(line.split('\t')[0:-1])
    predicted_2_next_labels = lambda line, next_line:  \
        line.split('\t')[-1][0] + \
        next_line.split('\t')[-1][0]

    try:
        line = next(row_iterator).strip()
        next_line = next(row_iterator).strip()
        while True:
            label_couple = predicted_2_next_labels(line, next_line)
            if label_couple == 'OI' and 'OI' in tags:
                yield '{}\tB-TIMEX3'.format(attributes_values(line))
            elif (label_couple == 'BB' and 'BB' in tags) or \
                 (label_couple == 'IB' and 'IB' in tags):
                yield line
                next_line = '{}\tI-TIMEX3'.format(attributes_values(next_line))
            else:
                yield line
            line = next_line
            next_line = next(row_iterator).strip()
    except StopIteration:  # there aren't two lines
        try:
            yield line
        except UnboundLocalError:  # there weren't lines at all
            pass


def main():
    '''It reads from the stdin and adjust'''
    tags = sys.argv[1].split(',')
    lines = sys.stdin.xreadlines()
    for consistent_line in make_consistent(lines, tags):
        print consistent_line

if __name__ == '__main__':
    main()
