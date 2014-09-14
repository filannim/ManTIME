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

'''It uses the external CRFs algorithms to predict the labels.'''

from __future__ import division
from cgi import escape
import os
import subprocess
from tempfile import NamedTemporaryFile

from normalisers.general_timex_normaliser import normalise
from properties import PATHS

class Tagger(object):

    def __init__(self):
        pass

    def __identify(self, sentence, attribute_names, attribute_values,
                   post_processing_pipeline=True):
        '''It returns positive sequences' offsets from the external CRF
        implementation.
        '''
        temp_file = NamedTemporaryFile('w+t', delete=False)
        temp_file.write('\n'.join(attribute_values))
        temp_file.close()

        if post_processing_pipeline:
            cmd = '{} crf_test -v2 -m {} {} | '.format(PATHS['crf++'], PATHS['crf++_model'], temp_file.name)
            cmd += 'python {} {} "{}" | '.format(PATHS['adjustment_module'], 0.5, 'perturbate')
            cmd += 'python {} "{}" | '.format(PATHS['consistency_module'], 'OI,BB,IB')
            cmd += 'python {} {} "{}" | '.format(PATHS['adjustment_module'], 0.87, 'threshold_adjustment')
            cmd += 'python {} "{}" | '.format(PATHS['consistency_module'], 'OI,BB,IB')
        else:
            cmd = '{} crf_test --m {} {} | '.format(PATHS['crf++'], PATHS['crf++_model'], temp_file.name)
        predictions = subprocess.Popen([cmd], shell=True, stdout=subprocess.PIPE)

        sequence_offsets = []
        sentence_char_pointer = 0
        for row in iter(predictions.stdout.readline, ''):
            row = row.split('\t')
            word, label = escape(row[0]), row[-1]
            start = sentence.index(word, sentence_char_pointer)
            if label.startswith('B'):
                sequence_offsets.append(
                    [start, start+len(word), attribute_names.split('\t')[-1]])
            elif label.startswith('I'):
                try:
                    sequence_offsets[-1][1] = start+len(word)
                except:
                    sequence_offsets.append(
                        [start, start+len(word), attribute_names.split('\t')[-1]])
            sentence_char_pointer += len(word)+(start-sentence_char_pointer)
        os.remove(temp_file.name)
        return sequence_offsets

    def tag(self, sentence, attribute_names, attribute_values, utterance,
            position=0, buffer=None, post_processing_pipeline=True):
        positive_sequences = []
        sentence = escape(sentence)
        offsets = self.__identify(sentence, attribute_names, attribute_values,
                                  use_post_processing_pipeline=
                                  post_processing_pipeline)
        annotated_sentence = list(sentence)
        displacement = 0
        for start, end, tag in offsets:
            timex_text = annotated_sentence[int(int(start)+displacement):
                                            int(int(end)+displacement)]
            try:
                _, timex_type, timex_value, _ = normalise(''.join(timex_text),
                                                          utterance,
                                                          buffer_file=buffer)
                if timex_type == 'NONE':
                    timex_type = 'DATE'
                if timex_value == 'NONE':
                    timex_value = 'X'
            except:
                timex_type = 'DATE'
                timex_value = 'X'
            # Complete annotation:
            #   opening_tag = '<%s tid="t%d" type="%s" functionInDocument="%s"
            #   temporalFunction="%s" value="%s">' %
            #   (tag, start_id, timex_type, 'NONE', 'false', timex_value)
            tag = '<{tag} tid="t{id}" type="{type}" value="{value}">'.format(
                tag=tag, id=position, type=timex_type, value=timex_value)
            closing_tag = '</{tag_name}>'.format(tag_name=tag)
            positive_sequences.append((position, timex_type, timex_value))
            annotated_sentence.insert(int(start)+displacement, tag)
            annotated_sentence.insert(int(end)+1+displacement, closing_tag)
            position += 1
            displacement += 2
        return ''.join(annotated_sentence), position, positive_sequences
