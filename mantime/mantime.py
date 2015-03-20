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
__codename__ = "purple tempo"

import argparse
import glob
import os
import cPickle
import logging
import sys
import xml.etree.cElementTree as cElementTree

from readers import i2b2FileReader
from readers import TempEval3FileReader
from readers import WikiWarsInLineFileReader
from attributes_extractor import FullExtractor
from writers import TempEval3Writer
from writers import AttributeMatrixWriter
from writers import i2b2Writer
from classifier import IdentificationClassifier
from classifier import NormalisationClassifier
from settings import PATH_MODEL_FOLDER


class ManTIME(object):

    def __init__(self, reader, writer, extractor, model_name, pipeline=True):
        self.post_processing_pipeline = pipeline
        self.reader = reader
        self.writer = writer
        self.extractor = extractor
        self.documents = []
        self.model_name = model_name
        self.model_path = '{}/{}/model.pickle'.format(PATH_MODEL_FOLDER,
                                                      self.model_name)
        try:
            self.model = cPickle.load(open(self.model_path))
            logging.info('{} model: loaded.'.format(self.model.name))
        except IOError:
            self.model = None
            logging.info('{} model: built.'.format(model_name))

    def train(self, folder):
        folder = os.path.abspath(folder)
        assert os.path.isdir(folder), 'Folder doesn\' exist.'

        identifier = IdentificationClassifier()
        normaliser = NormalisationClassifier()

        # corpus collection
        input_files = os.path.join(folder, self.reader.file_filter)
        for input_file in glob.glob(input_files):
            try:
                doc = self.extractor.extract(self.reader.parse(input_file))
                self.documents.append(doc)
            except cElementTree.ParseError:
                msg = 'Document {} skipped.'.format(os.path.relpath(input_file))
                logging.error(msg)

        # training models (identification and normalisation)
        modl = identifier.train(self.documents, self.model_name)
        modl = normaliser.train(self.documents, modl)
        self.model = modl
        # dumping models
        cPickle.dump(modl, open(self.model_path, 'w'))

        return modl

    def label(self, file_name):
        # according to the type
        assert os.path.isfile(file_name), 'Input file does not exist.'
        assert self.model, 'Model not loaded.'

        identifier = IdentificationClassifier()
        normaliser = NormalisationClassifier()

        # try:
        doc = self.extractor.extract(self.reader.parse(file_name))
        annotated_doc = identifier.test([doc], self.model,
                                         self.post_processing_pipeline)
        annotated_doc = normaliser.test([doc], self.model)

        output = self.writer.write(annotated_doc)
        return output
        # except:
        #    logging.info('{} skipped.'.format(file_name))


def main():
    """ It annotates documents in a specific folder.
    """
    import codecs
    logging.basicConfig(format='%(asctime)s: %(message)s',
                        level=logging.INFO,
                        datefmt='%m/%d/%Y %I:%M:%S %p')
    # Parse input
    parser = argparse.ArgumentParser(
        description='ManTIME: temporal information extraction')
    parser.add_argument('input_folder', help='Input data folder path')
    parser.add_argument('model',
                        help='Name of the model to use (case sensitive)')
    parser.add_argument('-v', '--version', help='show the version and exit',
                        action='store_true')
    parser.add_argument('-ppp', '--post_processing_pipeline',
                        action='store_true',
                        help='it uses the post processing pipeline.')
    args = parser.parse_args()

    # Expected usage of ManTIME
    mantime = ManTIME(reader=i2b2FileReader(),
                      writer=i2b2Writer(),
                      extractor=FullExtractor(),
                      model_name=args.model,
                      pipeline=False)
    # mantime.train(sys.argv[2])
    assert os.path.exists(args.input_folder), 'Model not found.'
    documents = sorted(glob.glob(os.path.join(args.input_folder, '*.xml')))
    assert documents, 'Input folder is empty.'
    for doc in documents:
        basename = os.path.basename(doc)
        writein = os.path.join('./output/', basename)
        if not os.path.exists(writein):
            with codecs.open(writein, 'w', encoding='utf8') as output:
                # try:
                output.write(mantime.label(doc)[0])
                # except:
                #    print 'Doc {} skipped.'.format(basename)

if __name__ == '__main__':
    main()
