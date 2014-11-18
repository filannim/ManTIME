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

'''This file containes some absolute paths you need to customize according to
you installation.'''

import os

HOME = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))

LANGUAGE = 'english'
PATH_CRF_ENGINE = '/Users/michele/Downloads/wapiti-1.5.0/wapiti'
PATH_CRF_PP_ENGINE_TRAIN = '/Users/michele/Downloads/CRF++-0.58/crf_learn'
PATH_CRF_PP_ENGINE_TEST = '/Users/michele/Downloads/CRF++-0.58/crf_test'
PATH_CRF_CONSISTENCY_MODULE = HOME + 'components/make_consistent.py'
PATH_CRF_ADJUSTMENT_MODULE = HOME + 'components/make_adjusted.py'
PATH_CORENLP_FOLDER = '/Users/filannim/Downloads/stanford-corenlp-full-2014-08-27'
PATH_MODEL_FOLDER = 'models'