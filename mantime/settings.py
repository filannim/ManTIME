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

PATH_CRF_EXECUTABLE_FOLDER = '/home/filannim/Downloads/CRF++-0.57/'
PATH_CRF_MODEL = HOME + '/components/crf_models/human_m1.crf'
PATH_CRF_CONSISTENCY_MODULE = HOME + '/components/make_consistent.py'
PATH_CRF_ADJUSTMENT_MODULE = HOME + '/components/make_adjusted.py'
PATH_TREETAGGER = 'tree-tagger-bundle'
PATH_TREETAGGER_TOKENIZER = '/usr/local/tree-tagger-linux-3.2/cmd/tokenize.pl'
PATH_CORENLP_FOLDER = '/home/filannim/Downloads/stanford-corenlp-full-2014-08-27'