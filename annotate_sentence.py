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

'''It annotates a sentence.'''

from datetime import datetime
import argparse
import os
import tempfile

from mantime.feature_factory import FeatureFactory
from mantime.tagger import Tagger


def annotate(sentence, utterance=datetime.now().strftime('%Y%M%d')):
    '''It annotates a sentence.'''
    with tempfile.NamedTemporaryFile('w+t', delete=False) \
            as last_utterance_memory:
        last_utterance_memory.write(utterance)

    features_extractor = FeatureFactory()
    writer = Tagger()
    sentence = sentence.replace('__space__', ' ').strip()
    attribute_names, attribute_values = features_extractor.get_sentence_attributes(sentence,
                                                               {'TIMEX3': []},
                                                               'TIMEX3')
    output = writer.tag(sentence, attribute_values, utterance, start_id=1,
                        buffer=last_utterance_memory.name, withPipeline=True,
                        debug=False)
    os.remove(last_utterance_memory.name)
    return output['sentence'], output['tags']


def main():
    '''It annotates a sentence.'''
    parser = argparse.ArgumentParser(
        description='ManTIME: temporal information extraction')
    parser.add_argument(dest='sentence', metavar='input sentence', nargs='*')
    parser.add_argument('-u', '--utterance', dest='utterance',
                        metavar='utterance', action='store',
                        help='Utterance time for the normalisation of temporal \
                        expression. Use the format YYYYMMDD.')
    args = parser.parse_args()
    print annotate(args.sentence)


if __name__ == '__main__':
    main()
