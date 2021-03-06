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

'''It adjusts the sequence labels predicted by Conditional Random Fields
   algorithm. It uses probabilities extracted from the training corpus to
   rescale the CRF predictions (which are commonly skewed towards the best
   label).

   Bio_fixer can be useless with other Conditional Random Fields implementation
   that offer a specific flag to avoid wrong sequences.

   The methods may need to be adpted for different Conditional Random Fields
   implementations. This module has been written according to the output of
   CRF++ v.0.57.
'''

from __future__ import division

import argparse
import codecs
from collections import Counter
from os.path import isfile
import logging
import pickle
import sys


def get_scale_factors(source, column_index):
    '''It returns a dictionary of words with their:
       p_word(label='I-TIMEX3').
    '''
    assert isfile(source), 'Input file doesn\'t exist.'
    assert column_index > 0, 'Invalid index.'

    scale_factors = dict()
    with codecs.open(source) as source:
        for row in source.xreadlines():
            row = row.strip().split('\t')
            if len(row) > 1:
                word = row[column_index]
                label = unicode(row[-1])
                scale_factors.setdefault(word, Counter([label]))
                scale_factors[word][label] += 1.0

    # normalise scale_factors (counts)
    for word in scale_factors.keys():
        freq = sum(scale_factors[word].values())
        freq_positive = sum((c for k, c in scale_factors[word].iteritems()
                             if k.startswith('I')))
        if freq_positive >= 2.0:
            for label in scale_factors[word].iterkeys():
                scale_factors[word][label] /= freq
        else:
            scale_factors.pop(word)
    return scale_factors


def probabilistic_correction(row_iterator, factors, index, lenght, threshold):
    '''It yields perturbated sequences of predicted labels accoding to the
       specified *threshold*.

       It takes in input an attribute values matrix (N instances x M columns)
       and returns a matrix with a DIFFERENT DIMENSION [Nx(M-4)].
    '''
    assert 0. <= threshold <= 1., 'Invalid threshold.'

    def get_marginals(elements):
        return {e.split('/')[0]: float(e.split('/')[1]) for e in elements}

    def perturbate_row(marginals, factor, threshold):
        '''It analyses the CRF predictions of a single token and returns the
           most likely perturbated label with its confidence rate.
        '''
        import operator
        # extract dictionary from CRF predictions
        perturbate_value = lambda value1, value2, threshold: \
            (value1*threshold) + value2*(1-threshold)
        # perturbate it in place
        for label, confidence in marginals.iteritems():
            marginals[label] = perturbate_value(confidence, factor[label],
                                                threshold)
        best_prediction, best_prediction_confidence = sorted(
            marginals.iteritems(), key=operator.itemgetter(1),
            reverse=True)[0]
        return (best_prediction, best_prediction_confidence)

    try:
        line = next(row_iterator).strip().split('\t')
        while True:
            # we skip lines which are not carrying data
            # this happens when we use crf_test -v2 (verbose mode)
            # the second condition makes sure it's not a data line with simply
            # has a word starting by '#'.
            if not (line[0].strip().startswith('#') or len(line) == 1):
                current_word = line[index]
                prediction = line[lenght].split('/')[0]
                assert prediction[0] in 'OBIW', 'Wrong sequence label.'
                marginals = get_marginals(line[lenght+1:])
                data = '\t'.join(line[:-4])
                if current_word in factors.keys():
                    perturbated_label, confidence = \
                        perturbate_row(marginals, factors[current_word],
                                       threshold)
                    if confidence >= threshold:
                        if prediction != perturbated_label:
                            logging.debug('PER: "{}"  {} --> {}'.format(
                                current_word, prediction, perturbated_label))
                        yield '{}\t{}'.format(data, perturbated_label)
                    else:
                        yield '{}\t{}'.format(data, prediction)
                else:
                    yield '{}\t{}'.format(data, prediction)
            else:
                if line[0].strip():
                    yield ''
            line = next(row_iterator).strip().split('\t')
    except StopIteration:
        pass


def label_switcher(row_iterator, factors, index, threshold):
    '''It yields adjusted sequences of predicted labels according to the
       specified *threshold*.

       It takes in input an attribute values matrix (N instances x M columns)
       and returns a matrix with the SAME DIMENSION.
    '''
    assert 0. <= threshold <= 1., 'Invalid threshold.'

    try:
        line = next(row_iterator).strip().split('\t')
        while True:
            if len(line) > 1:
                current_word = line[index]
                prediction = line[-1]
                data = '\t'.join(line[:-1])
                if current_word in factors.keys():
                    most_likely_label, confidence = \
                        factors[current_word].most_common(1)[0]
                    if confidence >= threshold:
                        if prediction != most_likely_label:
                            logging.debug('LBS: "{}"  {} --> {}'.format(
                                current_word, prediction, most_likely_label))
                        yield '{}\t{}'.format(
                            data, most_likely_label)
                    else:
                        yield '{}\t{}'.format(data, prediction)
                else:
                    yield '{}\t{}'.format(data, prediction)
            else:
                yield ''
            line = next(row_iterator).strip().split('\t')
    except StopIteration:
        pass


def main():
    '''It reads from stdin and adjust or perturbate.'''
    parser = argparse.ArgumentParser(
        description='ManTIME: adjust predicted sequences.')
    parser.add_argument('algorithm', help='training set file.')
    parser.add_argument('option2', help='threshold or patterns.')
    args = parser.parse_args()

    lines = sys.stdin.xreadlines()
    factors = pickle.load(open('models/tempeval3/factors'))['TIMEX']
    if args.algorithm == 'probabilistic_correction':
        adjusted_lines = probabilistic_correction(lines, factors,
                                                  135, float(args.option2))
    elif args.algorithm == 'label_switcher':
        adjusted_lines = label_switcher(lines, factors, 135,
                                        float(args.option2))
    else:
        raise NameError('Algorithm name invalid!')

    for adjusted_line in adjusted_lines:
        print adjusted_line

if __name__ == '__main__':
    main()
