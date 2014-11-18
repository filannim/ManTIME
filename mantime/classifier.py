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
import cPickle
import logging
from tempfile import NamedTemporaryFile

from crf_utilities.scale_factors import get_scale_factors
from settings import PATH_MODEL_FOLDER
from settings import PATH_CRF_PP_ENGINE_TEST
from settings import PATH_CRF_PP_ENGINE_TRAIN
from utilities import Mute_stderr
from utilities import extractors_timestamp


class Classifier(object):
    """This class is an abstract classifier for ManTIME."""
    __metaclass__ = ABCMeta

    def __init__(self):
        pass

    @abstractmethod
    def train(self, documents, pre_existing_model=None,
              post_processing_pipeline=False):
        """ It returns a ClassificationModel object.
        """
        assert len(set([d.annotation_format for d in documents])) == 1

    @abstractmethod
    def test(self, documents, model):
        """

            return List of <Document> (with .annotations filled in.)
        """
        if extractors_timestamp() != model.extractors_md5:
            # TO-DO: log instead of print
            print 'WARNING: The feature extractor component has changed!'


class CRFClassifier(Classifier):
    """This class is a CRF interface."""
    def __init__(self, model=None):
        super(CRFClassifier, self).__init__()
        if model:
            assert type(model) == ClassificationModel, 'Wrong model type.'
        self.model = model


    def train(self, documents, model_name, pre_existing_model=None):
        """ It returns a ClassificationModel object."""
        # TO-DO: feature extractor deve yieldare anziche' ritornare
        assert type(documents) == list, 'Wrong type for documents.'
        assert len(documents) > 0, 'Empty documents list.'
        # strictly convert model_name
        model_name = re.sub('\s+', '_', model_name)
        model_name = re.sub('[\W]+', '', model_name)

        path_and_modelname = (PATH_MODEL_FOLDER, model_name)
        header_path = '{}/{}.header'.format(*path_and_modelname)
        trainingset_path = '{}/{}.trainingset'.format(*path_and_modelname)
        model_path = '{}/{}.model'.format(*path_and_modelname)

        # save header to model_name.header
        first_word = documents[0].sentences[0].words[0]
        header = [k for k, _ in sorted(first_word.attributes.items())]
        with open(header_path, 'w') as header_file:
            header_file.write('\n'.join(header))

        if self.model:
            model = self.model
        else:
            model = ClassificationModel(header, model_name)
            model.name = model_name
            model.path = model_path
            model.extractors_md5 = extractors_timestamp()
            self.model = model

        # save trainingset to model_name.trainingset
        with open(trainingset_path, 'w') as trainingset:
            for document in documents:
                for sentence in document.sentences:
                    for word in sentence.words:
                        row = [v for _, v in sorted(word.attributes.items())]
                        trainingset.write('\t'.join(row))
                        trainingset.write('\t' + word.gold_label)
                        trainingset.write('\n')
                    trainingset.write('\n')

        # post-processing pipeline
        # scale_factors = get_scale_factors(trainingset_path)
        # factors_path = PATH_MODEL_FOLDER + '/' + model_name + '.factors'
        # pickle.dump(scale_factors, open(factors_path, 'w'))

        # run external CRF resource (Wapiti)
        # crf_command = [PATH_CRF_ENGINE, 'train',
        #                '-T', 'crf',
        #                '-a', 'l-bfgs',
        #                '-p', model.topology_path,
        #                '-t', str(multiprocessing.cpu_count()),
        #                trainingset_path,
        #                PATH_MODEL_FOLDER + '/' + model_name + '.model']
        crf_command = [PATH_CRF_PP_ENGINE_TRAIN, model.topology_path,
                       trainingset_path, model_path]
        with Mute_stderr():
            process = subprocess.Popen(crf_command)
            process.wait()

        # TO-DO: Check if the script saves a model or returns an error
        return model

    def test(self, documents, post_processing_pipeline=False):
        """ It returns the sequence of labels from the Wapiti classifier.

        It returns the same data structure (list of documents, of sentences,
        of words with the right labels.
        """
        assert self.model, 'No model loaded for CRF.'
        assert type(documents) == list, 'Wrong type for documents.'
        assert len(documents) > 0, 'Empty documents list.'

        # temporary saves the test set
        with NamedTemporaryFile(delete=True) as testset:
            for num_doc, document in enumerate(documents):
                for num_sent, sentence in enumerate(document.sentences):
                    for num_word, word in enumerate(sentence.words):
                        row = [v for _, v in sorted(word.attributes.items())]
                        testset.write('\t'.join(row))
                        # Adding an extra-column with word coordinates
                        testset.write('\t{}_{}_{}'.format(num_doc,
                                                          num_sent,
                                                          num_word))
                        testset.write('\n')
                    testset.write('\n')
                    testset.flush()

            # run external CRF resource (Wapiti)
            # crf_command = [PATH_CRF_ENGINE, 'label', '-m', self.model.path,
            #                '-l', testset.name]

            crf_command = [PATH_CRF_PP_ENGINE_TEST, '-m', self.model.path,
                           testset.name]
            with Mute_stderr():
                process = subprocess.Popen(crf_command, stdout=subprocess.PIPE)

            n_doc, n_sent, n_word = 0, 0, 0
            for label in iter(process.stdout.readline, ''):
                label = label.strip().split('\t')[-1]
                if label:
                    documents[n_doc].sentences[n_sent].words[n_word]\
                        .predicted_label = label
                    n_word += 1
                    if len(documents[n_doc].sentences[n_sent].words) == n_word:
                        n_word = 0
                        n_sent += 1
                        if len(documents[n_doc].sentences) == n_sent:
                            n_word, n_sent = 0, 0
                            n_doc += 1

        # post-processing pipeline
        if post_processing_pipeline:
            try:
                factors_path = PATH_MODEL_FOLDER + '/' + self.model.name + '.factors'
                factors = cPickle.load(open(factors_path))
            except IOError:
                logging.warning('Scale factors not found.')

        # for
        return documents


class ClassificationModel(object):
    """Classification model.

    It just contains a time stamp of the files involved in the extraction
    of the attributes (nlp_functions.py) and their MD5-sum codes. I would
    like to be sure that the attribute set is compatible with the trained
    model. In order to check for it I'll check if the timestamps of the .pyc
    files are equal. Does something more elegant exists? I don't know.
    """

    def __init__(self, header, model_name):
        self.name = model_name
        self.header = header
        self.topology_path = None
        self.topology = self._generate_template(model_name)
        self.pipeline_factors = None
        self.path = None
        self.extractors_md5 = None

    def _generate_template(self, model_name):
        num_of_features = len(self.header)
        patterns = set()
        for i in xrange(num_of_features):
            patterns.add('%x[0,{}]'.format(i))
            patterns.add('%x[-1,{}]'.format(i))
            patterns.add('%x[1,{}]'.format(i))
            patterns.add('%x[-2,{}]/%x[-1,{}]'.format(i, i))
            patterns.add('%x[-1,{}]/%x[0,{}]'.format(i, i))
            patterns.add('%x[0,{}]/%x[1,{}]'.format(i, i))
            patterns.add('%x[-1,{}]/%x[0,{}]/%x[1,{}]'.format(i, i, i))
            patterns.add('%x[0,{}]/%x[1,{}]/%x[2,{}]'.format(i, i, i))
            # SUPER LIGHT
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
        self.topology = ['U{:0>7}:{}'.format(index, pattern)
                         for index, pattern
                         in enumerate(list(sorted(patterns)))]
        model_name += '.template'
        with open(PATH_MODEL_FOLDER + '/' + model_name, 'w') as template:
            for pattern in self.topology:
                template.write(pattern)
                template.write('\n')
        self.topology_path = PATH_MODEL_FOLDER + '/' + model_name
