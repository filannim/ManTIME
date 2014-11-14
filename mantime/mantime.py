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
import sys

from readers import TempEval3FileReader
from attributes_extractor import FullExtractor
from writers import SimpleXMLFileWriter
from classifier import WapitiClassifier

class ManTIME(object):

    def __init__(self, reader, writer, extractor):
        self.processes = multiprocessing.cpu_count()
        self.post_processing_pipeline = True
        self.reader = reader
        self.writer = writer
        self.extractor = extractor
        self.documents = []

    def train(self, folder, model_name, pre_existing_model=None):
        assert os.path.isdir(folder), 'Folder doesn\' exist.'
        folder = os.path.abspath(folder)
        file_reader = self.reader
        extractor = self.extractor
        classifier = WapitiClassifier(pre_existing_model)
        for document in glob.glob(folder + '/*.tml'):
            try:
                document = file_reader.parse(document)
                extractor.extract(document)
                self.documents.append(document)
            except:
                print '{} skipped.'.format(document)
        return classifier.train(self.documents, model_name, pre_existing_model)

    def extract(self, document_content, type):
        # according to the type
        pass


def main():
    '''It annotates documents in a specific folder.'''

    # Parse input
    parser = argparse.ArgumentParser(
        description='ManTIME: temporal information extraction')
    parser.add_argument(dest='folder', metavar='input folder', nargs='*')
    parser.add_argument('-ppp', '--post_processing_pipeline', dest='pipeline',
                        action='store_true',
                        help='it uses the post processing pipeline.')
    args = parser.parse_args()

    # Expected usage of ManTIME
    mantime = ManTIME(TempEval3FileReader(), SimpleXMLFileWriter(), FullExtractor())
    print mantime.train(args.folder[0], './delete.me')
    for doc in mantime.documents:
        for sentence in doc.sentences:
            for word in sentence.words:
                print word.gold_label


if __name__ == '__main__':
    main()
