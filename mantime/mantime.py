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

'''It returns the ISO-TimeML-annotated input documents.'''
__author__ = "Michele Filannino <filannino.m@gmail.com>"
__version__ = "0.1"

import argparse
import multiprocessing
import glob
import os
import cPickle
import logging

from readers import TempEval3FileReader
from attributes_extractor import FullExtractor
from writers import TempEval3Writer, AttributeMatrixWriter
from classifier import IdentificationClassifier
from classifier import NormalisationClassifier
from settings import PATH_MODEL_FOLDER

class ManTIME(object):

    def __init__(self, reader, writer, extractor, model_name):
        self.processes = multiprocessing.cpu_count()
        self.post_processing_pipeline = True
        self.reader = reader
        self.writer = writer
        self.extractor = extractor
        self.documents = []
        self.model_name = model_name
        self.model_path = '{}/{}.model.pickle'.format(PATH_MODEL_FOLDER,
                                                      self.model_name)
        self.model = cPickle.load(open(self.model_path))

    def train(self, folder):
        folder = os.path.abspath(folder)
        assert os.path.isdir(folder), 'Folder doesn\' exist.'

        identifier = IdentificationClassifier()
        normaliser = NormalisationClassifier()

        # corpus collection
        for input_file in glob.glob(folder + '/*.tml'):
            #try:
            doc = self.extractor.extract(self.reader.parse(input_file))
            self.documents.append(doc)
            logging.info('{} done.'.format(input_file))
            #except:
            #    logging.error('{} skipped.'.format(input_file))

        # training models (identification and normalisation)
        modl = identifier.train(self.documents, self.model_name)
        modl = normaliser.train(self.documents, self.model)
        # dumping models
        cPickle.dump(modl, open(self.model_path, 'w'))

        return modl

    def label(self, file_name):
        # according to the type
        assert os.path.isfile(file_name), 'Input file does not exist.'
        assert os.path.isfile(self.model_path), 'Model file does not exist.'

        identifier = IdentificationClassifier()
        normaliser = NormalisationClassifier()

        #try:
        doc = self.extractor.extract(self.reader.parse(file_name))
        annotated_docs = identifier.test([doc], self.model)
        annotated_docs = normaliser.test([doc], self.model)
        output = self.writer.write(annotated_docs)
        return output
        #except:
        #    logging.info('{} skipped.'.format(file_name))


def main():
    '''It annotates documents in a specific folder.'''

    logging.getLogger().setLevel(logging.INFO)
    # Parse input
    parser = argparse.ArgumentParser(
        description='ManTIME: temporal information extraction')
    parser.add_argument(dest='folder', metavar='input folder', nargs='*')
    parser.add_argument('-ppp', '--post_processing_pipeline', dest='pipeline',
                        action='store_true',
                        help='it uses the post processing pipeline.')
    args = parser.parse_args()

    # Expected usage of ManTIME
    mantime = ManTIME(TempEval3FileReader(),
                      AttributeMatrixWriter(),
                      FullExtractor(),
                      'tempeval3')
    print mantime.train(args.folder[0])
    print mantime.label('/Users/michele/Dropbox/Workspace/ManTIME_refactoring/ManTIME/data/test1/test_short.tml.TE3input')


if __name__ == '__main__':
    main()
