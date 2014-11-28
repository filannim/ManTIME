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
from abc import ABCMeta, abstractmethod
import subprocess
import re
import codecs
import cPickle
import logging
import os
import shutil
import multiprocessing
from tempfile import NamedTemporaryFile

from crf_utilities import get_scale_factors
from crf_utilities import probabilistic_correction
from crf_utilities import label_switcher
from settings import PATH_MODEL_FOLDER
from settings import PATH_CRF_PP_ENGINE_TEST
from settings import PATH_CRF_PP_ENGINE_TRAIN
from settings import EVENT_ATTRIBUTES
from settings import NO_ATTRIBUTE
from utilities import Mute_stderr
from utilities import extractors_stamp


def identification_attribute_matrix(documents, dest, subject, training=True):
    assert type(documents) == list, 'Wrong type for documents.'
    assert len(documents) > 0, 'Empty documents list.'
    assert subject in ('EVENT', 'TIMEX'), 'Wrong identification subject.'

    # It stores the attribute matrix
    with codecs.open(dest, 'w', encoding='utf8') as matrix:
        for document in documents:
            for sentence in document.sentences:
                for word in sentence.words:
                    row = [v for _, v in sorted(word.attributes.items())]
                    matrix.write('\t'.join(row))
                    gold_label = word.gold_label

                    # The class of the instances different from the subject are
                    # changed in 'O'
                    if subject == 'EVENT':
                        if gold_label.find('TIMEX') > -1:
                            gold_label = 'O'
                    else:
                        if gold_label.find('EVENT') > -1:
                            gold_label = 'O'

                    if training:
                        matrix.write('\t' + gold_label)
                    matrix.write('\n')
                matrix.write('\n')


def normalisation_attribute_matrix(documents, dest, subject, training=True):
    assert type(documents) == list, 'Wrong type for documents.'
    assert len(documents) > 0, 'Empty documents list.'
    assert subject in EVENT_ATTRIBUTES

    if training:
        get_label = lambda word: word.gold_label
    else:
        get_label = lambda word: word.predicted_label

    # It stores the attribute matrix
    with codecs.open(dest, 'w', encoding='utf8') as matrix:
        for ndoc, document in enumerate(documents):
            for nsen, sentence in enumerate(document.sentences):
                for nwor, word in enumerate(sentence.words):
                    row = [v for _, v
                           in sorted(word.attributes.items())]
                    row.append(get_label(word))
                    if training:
                        label = word.tag_attributes.get(subject, NO_ATTRIBUTE)
                        if not label:
                            label = NO_ATTRIBUTE
                        row.append(label)
                    else:
                        # I sneak in the coordinates of each token
                        row.append('{}_{}_{}'.format(ndoc, nsen, nwor))
                    matrix.write('\t'.join(row))

                    # I am using CRFs with singleton sequences
                    # (a small trick) ;)
                    matrix.write('\n\n')


class Classifier(object):
    """This class is an abstract classifier for ManTIME."""
    __metaclass__ = ABCMeta

    def __init__(self):
        self.num_cores = multiprocessing.cpu_count()

    @abstractmethod
    def train(self, documents, model_name):
        """ It returns a ClassificationModel object.
        """
        assert len(set([d.annotation_format for d in documents])) == 1

    @abstractmethod
    def test(self, documents, model, post_processing_pipeline=False):
        """

            return List of <Document> (with .annotations filled in.)
        """
        pass


class IdentificationClassifier(Classifier):
    """This class is a CRF interface.

    """
    def __init__(self):
        super(IdentificationClassifier, self).__init__()

    def train(self, documents, model_name):
        """It returns a ClassificationModel object.

        """
        # TO-DO: feature extractor deve yieldare anziche' ritornare
        assert type(documents) == list, 'Wrong type for documents.'
        assert len(documents) > 0, 'Empty documents list.'

        model = ClassificationModel(model_name)

        # load the header into the model
        first_word = documents[0].sentences[0].words[0]
        header = [k for k, _ in sorted(first_word.attributes.items())]
        model.load_header(header)

        # search for the token_normalised attribute position
        token_normalised_pos = [p for p, a in enumerate(header)
                                if a.find('token_normalised') > -1][0]
        model.pp_pipeline_attribute_pos = token_normalised_pos

        # save trainingset to model_name.trainingset.class
        scaling_factors = {}
        for idnt_class in ('EVENT', 'TIMEX'):
            path_and_model = (PATH_MODEL_FOLDER, model.name, idnt_class)
            trainingset_path = '{}/{}/identification.trainingset.{}'.format(
                *path_and_model)
            identification_attribute_matrix(documents, trainingset_path,
                                            idnt_class)

            # save scale factors for post processing pipeline
            scaling_factors[idnt_class] = get_scale_factors(
                trainingset_path, token_normalised_pos)

            crf_command = [PATH_CRF_PP_ENGINE_TRAIN,
                           '-p', str(self.num_cores), model.path_topology,
                           trainingset_path, '{}.{}'.format(model.path,
                                                            idnt_class)]
            with Mute_stderr():
                process = subprocess.Popen(crf_command, stdout=subprocess.PIPE)
                _, _ = process.communicate()

            # TO-DO: Check if the script saves a model or returns an error
            logging.info('Identification CRF model ({}): trained.'.format(
                idnt_class))

        # save factors in the model
        model.load_scaling_factors(scaling_factors)

        return model

    def test(self, documents, model, post_processing_pipeline=False):
        """It returns the sequence of labels from the CRF classifier.

        It returns the same data structure (list of documents, of sentences,
        of words with the right labels.

        """
        if extractors_stamp() != model.extractors_md5:
            logging.warning('The feature extractor component is different' +
                            'from the one used in the training!')

        if post_processing_pipeline:
            try:
                factors = cPickle.load(open(model.path_factors))
            except IOError:
                post_processing_pipeline = False
                logging.warning('Scale factors not found.')

        for idnt_class in ('EVENT', 'TIMEX'):
            testset_path = NamedTemporaryFile(delete=False).name
            model_path = '{}.{}'.format(model.path, idnt_class)
            identification_attribute_matrix(documents, testset_path,
                                            idnt_class, training=False)
            if post_processing_pipeline:
                crf_command = [PATH_CRF_PP_ENGINE_TEST, '-v2', '-m',
                               model_path, testset_path]
            else:
                crf_command = [PATH_CRF_PP_ENGINE_TEST, '-m',
                               model_path, testset_path]

            # Draconianly check the input files
            assert os.path.isfile(model_path), 'Model doesn\'t exist at {}'.format(model_path)
            assert os.stat(model_path).st_size > 0, 'Model is empty!'
            assert os.path.isfile(testset_path), 'Test set doesn\'t exist!'

            with Mute_stderr():
                process = subprocess.Popen(crf_command, stdout=subprocess.PIPE)

            n_doc, n_sent, n_word = 0, 0, 0

            # post-processing pipeline
            if post_processing_pipeline and factors:
                scale_factors = factors[idnt_class]
                lines = label_switcher(
                    probabilistic_correction(
                        iter(process.stdout.readline, ''),
                        scale_factors, model.pp_pipeline_attribute_pos, .5),
                    scale_factors, model.pp_pipeline_attribute_pos, .87)
            else:
                lines = iter(process.stdout.readline, '')

            for label in lines:
                label = label.strip().split('\t')[-1]
                if label:
                    if label != 'O':
                        documents[n_doc].sentences[n_sent].words[n_word]\
                            .predicted_label = label
                    n_word += 1
                    if len(documents[n_doc].sentences[n_sent].words) == n_word:
                        n_word = 0
                        n_sent += 1
                        if len(documents[n_doc].sentences) == n_sent:
                            n_word, n_sent = 0, 0
                            n_doc += 1
        return documents


class NormalisationClassifier(Classifier):
    """This class is a CRF interface.

    """
    def __init__(self):
        super(NormalisationClassifier, self).__init__()
        self.attributes = EVENT_ATTRIBUTES

    def train(self, documents, model):
        """It returns a ClassificationModel object for event CLASS attributes.

        """
        # TO-DO: feature extractor deve yieldare anziche' ritornare
        assert type(documents) == list, 'Wrong type for documents.'
        assert len(documents) > 0, 'Empty documents list.'

        # save trainingset to model_name.trainingset.*attribute*
        for attribute in self.attributes:
            path_model_attribute = (PATH_MODEL_FOLDER, model.name, attribute)
            trainingset_path = '{}/{}/normalisation.trainingset.{}'.format(
                *path_model_attribute)
            normalisation_attribute_matrix(documents, trainingset_path,
                                           attribute, training=True)
            model_path = '{}.{}'.format(model.path_normalisation, attribute)
            crf_command = [PATH_CRF_PP_ENGINE_TRAIN, '-p', str(self.num_cores),
                           model.path_attribute_topology, trainingset_path,
                           model_path]

            with Mute_stderr():
                process = subprocess.Popen(crf_command, stdout=subprocess.PIPE)
                _, _ = process.communicate()

            # Weakly check the output models
            if not os.path.isfile(model_path):
                msg = 'Normalisation CRF model ({}): *not* trained.'
                logging.error(msg.format(attribute))
            else:
                msg = 'Normalisation CRF model ({}): trained.'
                logging.info(msg.format(attribute))
        return model

    def test(self, documents, model):
        """It returns the sequence of labels from the classifier.

        It returns the same data structure (list of documents, of sentences,
        of words with the right labels.

        """
        for attribute in self.attributes:
            testset_path = NamedTemporaryFile(delete=False).name
            model_path = '{}.{}'.format(model.path_normalisation, attribute)
            normalisation_attribute_matrix(documents, testset_path, attribute,
                                           training=False)
            crf_command = [PATH_CRF_PP_ENGINE_TEST, '-m', model_path,
                           testset_path]

            # Weakly check the input files
            if not os.path.isfile(model_path):
                logging.error('Model doesn\'t exist at {}'.format(model_path))
            else:
                if os.stat(model_path).st_size == 0:
                    msg = 'Normalisation model for {} is empty!'
                    logging.error(msg.format(attribute.lower()))
            if not os.path.isfile(testset_path):
                msg = 'Normalisation test set for {} doesn\'t exist at {}.'
                logging.error(msg.format(attribute.lower(), testset_path))

            with Mute_stderr():
                process = subprocess.Popen(crf_command, stdout=subprocess.PIPE)

            for line in iter(process.stdout.readline, ''):
                line = line.strip()
                if line:
                    line = line.split('\t')
                    label = line[-1]
                    location = line[-2]
                    is_event = line[-3] == 'I-EVENT'
                    if is_event:
                        n_doc, n_sent, n_word = location.split('_')
                        documents[int(n_doc)]\
                            .sentences[int(n_sent)].words[int(n_word)]\
                            .tag_attributes[attribute] = label
        return documents


class ClassificationModel(object):
    """Classification model.

    It just contains a time stamp of the files involved in the extraction
    of the attributes (nlp_functions.py) and their MD5-sum codes. I would
    like to be sure that the attribute set is compatible with the trained
    model. In order to check for it I'll check if the timestamps of the .pyc
    files are equal. Does something more elegant exists? I don't know.

    """
    def __init__(self, model_name):
        simplify = lambda name: re.sub(r'[\W]+', '', re.sub(r'\s+', '_', name))
        self.name = simplify(model_name)
        path_and_model = (PATH_MODEL_FOLDER, self.name)
        self.path = '{}/{}/identification.model'.format(*path_and_model)
        self.path_normalisation = '{}/{}/normalisation.model'.format(
            *path_and_model)
        self.path_topology = '{}/{}/template'.format(*path_and_model)
        self.path_attribute_topology = '{}/{}/attribute.template'.format(
            *path_and_model)
        self.path_header = '{}/{}/header'.format(*path_and_model)
        self.path_factors = '{}/{}/factors'.format(*path_and_model)
        shutil.rmtree('{}/{}'.format(*path_and_model), ignore_errors=True)
        os.makedirs('{}/{}'.format(*path_and_model))
        self.num_of_features = 0
        self.topology = None
        self.attribute_topology = None
        self.pp_pipeline_attribute_pos = None
        self.extractors_md5 = extractors_stamp()
        logging.info('Classification model: initialised.')

    def load_header(self, header):
        """It loads the header and stores it.

        """
        self.num_of_features = len(header)
        with open(self.path_header, 'w') as header_file:
            header_file.write('\n'.join(header))
        logging.info('Header: stored.')
        self.topology = self._generate_template()
        self.attribute_topology = self._generate_template(True)

    def load_scaling_factors(self, factors):
        cPickle.dump(factors, open(self.path_factors, 'w'))
        logging.info('Identification scaling factors: stored.')

    def _generate_template(self, attribute=False):
        """It generates and dumps the CRF template for CRF++.

        """
        assert self.num_of_features > 0, 'Header not loaded yet.'

        n_of_features = self.num_of_features
        if attribute:
            n_of_features += 1

        patterns = set()
        for i in xrange(n_of_features):
            patterns.add('%x[0,{}]'.format(i))
            patterns.add('%x[-1,{}]'.format(i))
            patterns.add('%x[1,{}]'.format(i))
            patterns.add('%x[-2,{}]/%x[-1,{}]'.format(i, i))
            patterns.add('%x[-1,{}]/%x[0,{}]'.format(i, i))
            patterns.add('%x[0,{}]/%x[1,{}]'.format(i, i))
            patterns.add('%x[-1,{}]/%x[0,{}]/%x[1,{}]'.format(i, i, i))
            patterns.add('%x[0,{}]/%x[1,{}]/%x[2,{}]'.format(i, i, i))
            # Super light
            patterns.add('%x[1,{}]/%x[2,{}]'.format(i, i))
            patterns.add('%x[-2,{}]/%x[-1,{}]/%x[0,{}]'.format(i, i, i))
            patterns.add('%x[-1,{}]/%x[1,{}]'.format(i, i))
            patterns.add('%x[-2,{}]/%x[2,{}]'.format(i, i))
            # for m in sorted(list(set(range(num_of_features)) - set([i]))):
            #   template.add('%%x[0,%d]/%%x[0,%d]' % (i,m))
            #   template.add('%%x[-1,%d]/%%x[0,%d]' % (i,m))
            #   template.add('%%x[-1,%d]/%%x[0,%d]' % (m,i))
            #   template.add('%%x[-2,%d]/%%x[-1,%d]' % (i,m))
            #   template.add('%%x[-2,%d]/%%x[-1,%d]' % (m,i))
            #   template.add('%%x[0,%d]/%%x[1,%d]' % (i,m))
            #   template.add('%%x[0,%d]/%%x[1,%d]' % (m,i))
            #   template.add('%%x[1,%d]/%%x[2,%d]' % (i,m))
            #   template.add('%%x[1,%d]/%%x[2,%d]' % (m,i))
        topology = ['U{:0>7}:{}'.format(index, pattern)
                    for index, pattern
                    in enumerate(list(sorted(patterns)))]
        if attribute:
            dest = self.path_attribute_topology
        else:
            dest = self.path_topology
        with open(dest, 'w') as template:
            for pattern in topology:
                template.write(pattern)
                template.write('\n')
        logging.info('CRF topology template (attribute={}): stored.'.format(
            attribute))
        return topology
