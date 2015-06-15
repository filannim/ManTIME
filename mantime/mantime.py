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

import cPickle
import glob
import logging
import os
import xml.etree.cElementTree as cElementTree

from classifier import IdentificationClassifier
from classifier import NormalisationClassifier
from classifier import RelationClassifier
from settings import PATH_MODEL_FOLDER


class ManTIME(object):

    def __init__(self, reader, writer, extractor, model_name, pipeline=True,
                 domain='general'):
        assert domain in ('general', 'clinical')
        self.post_processing_pipeline = pipeline
        self.reader = reader
        self.writer = writer
        self.extractor = extractor
        self.documents = []
        self.model_name = model_name
        self.model_path = '{}/{}/model.pickle'.format(PATH_MODEL_FOLDER,
                                                      self.model_name)
        try:
            self.model = cPickle.load(open(os.path.abspath(self.model_path)))
            logging.info('{} model: loaded.'.format(self.model.name))
        except IOError:
            self.model = None
            logging.info('{} model: built.'.format(model_name))
        self.domain = domain

    def train(self, folder):
        folder = os.path.abspath(folder)
        assert os.path.isdir(folder), 'Folder doesn\'t exist.'

        identifier = IdentificationClassifier()
        normaliser = NormalisationClassifier()
        linker = RelationClassifier()

        # corpus collection
        input_files = os.path.join(folder, self.reader.file_filter)
        for input_file in glob.glob(input_files):
            try:
                doc = self.extractor.extract(self.reader.parse(input_file))
                self.documents.append(doc)
            except cElementTree.ParseError:
                msg = 'Document {} skipped: parse error.'.format(
                    os.path.relpath(input_file))
                logging.error(msg)

        # training models (identification and normalisation)
        modl = identifier.train(self.documents, self.model_name)
        modl = normaliser.train(self.documents, modl)
        modl = linker.train(self.documents, modl)
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
        linker = RelationClassifier()

        try:
            doc = self.extractor.extract(self.reader.parse(file_name))
            annotated_doc = identifier.test([doc], self.model,
                                            self.post_processing_pipeline)
            annotated_doc = normaliser.test([doc], self.model, self.domain)
            annotated_doc = linker.test([doc], self.model)

            output = self.writer.write(annotated_doc)
            return output
        except cElementTree.ParseError:
            msg = 'Document {} skipped: parse error.'.format(
                os.path.relpath(file_name))
            logging.error(msg)
            return ['']
