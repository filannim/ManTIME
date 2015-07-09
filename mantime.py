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

import argparse
import codecs
import glob
import logging
import os

from mantime.mantime import ManTIME
from mantime.readers import TempEval3FileReader
from mantime.writers import TempEval3Writer
from mantime.attributes_extractor import FullExtractor


def main():
    """ It annotates documents in a specific folder.
    """
    logging.basicConfig(format='%(asctime)s: %(message)s',
                        level=logging.DEBUG,
                        datefmt='%m/%d/%Y %I:%M:%S %p')
    # Parse input
    parser = argparse.ArgumentParser(
        description='ManTIME: temporal information extraction')
    parser.add_argument('mode', choices=['train', 'test'],
                        help='Train or Test mode?')
    parser.add_argument('input_folder', help='Input data folder path')
    parser.add_argument('model',
                        help='Name of the model to use (case sensitive)')
    parser.add_argument('-v', '--version', help='show the version and exit',
                        action='store_true')
    parser.add_argument('-ppp', '--post_processing_pipeline',
                        action='store_true',
                        help='it uses the post processing pipeline.')
    args = parser.parse_args()

    # ManTIME
    mantime = ManTIME(reader=TempEval3FileReader(),
                      writer=TempEval3Writer(),
                      extractor=FullExtractor(),
                      model_name=args.model,
                      pipeline=args.post_processing_pipeline)

    if args.mode == 'train':
        # Training
        mantime.train(args.input_folder)
    else:
        # Testing
        assert os.path.exists(args.input_folder), 'Model not found.'
        input_files = os.path.join(args.input_folder, '*.*')
        documents = sorted(glob.glob(input_files))
        assert documents, 'Input folder is empty.'
        for index, doc in enumerate(documents, start=1):
            basename = os.path.basename(doc)
            writein = os.path.join('./output/', basename)
            position = '[{}/{}]'.format(index, len(documents))
            # if writein not in glob.glob('./output/*.*'):
            file_path = '.'.join(writein.split('.')[:-1])
            with codecs.open(file_path, 'w', encoding='utf8') as output:
                # try:
                    logging.info('{} Doc {}.'.format(position, basename))
                    output.write(mantime.label(doc)[0])
                    logging.info('{} Doc {} annotated.'.format(position,
                                                               basename))
                # except Exception:
                    # logging.error('{} Doc {} ** skipped **!'.format(
                    #     position, basename))
                    # os.remove(file_path)
            # else:
            #     logging.info('{} Doc {} already in output folder.'.format(
            #         position, basename))

if __name__ == '__main__':
    main()
