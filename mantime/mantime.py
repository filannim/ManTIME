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
import pickle

from readers import TempEval3FileReader
from attributes_extractor import FullExtractor
from writers import SimpleXMLFileWriter
from classifier import WapitiClassifier
from settings import PATH_MODEL_FOLDER

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
        classifier = WapitiClassifier(pre_existing_model)
        for input_file in glob.glob(folder + '/*.tml'):
            try:
                document = self.reader.parse(input_file)
                self.extractor.extract(document)
                self.documents.append(document)
            except:
                print '{} skipped.'.format(input_file)
        model = classifier.train(self.documents, model_name, pre_existing_model)
        pickle.dump(model, open(PATH_MODEL_FOLDER + '/' + model_name + '.model.pickle', 'w'))
        return model

    def label(self, file_name, type, model_name):
        # according to the type
        assert os.path.isfile(file_name),\
            'File {} does not exist.'.format(file_name)
        assert os.path.isfile(PATH_MODEL_FOLDER + '/' + model_name + '.model.pickle'),\
            'File {} does not exist.'.format(
                PATH_MODEL_FOLDER + '/' + model_name)

        model = pickle.load(open(PATH_MODEL_FOLDER + '/' + model_name + '.model.pickle'))
        classifier = WapitiClassifier(model)
        try:
            document = self.reader.parse(file_name)
            self.extractor.extract(document)
            return self.writer.write(classifier.test([document], model))
        except:
            print '{} skipped.'.format(file_name)



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
    print mantime.train(args.folder[0], 'tempeval3')
    cPickle.dump(mantime.documents, open('tempeval3.documents', 'w'))
    #print mantime.label(args.folder[0], '', 'tempeval3')


if __name__ == '__main__':
    main()
