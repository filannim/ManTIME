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

HOME = '/home/filannim/Dropbox/Workspace/ManTIME'

PATHS = {}
PATHS['crf++'] = '/home/filannim/Downloads/CRF++-0.57/'
PATHS['crf++_model'] = HOME + '/components/crf_models/human_m1.crf'
PATHS['consistency_module'] = HOME + '/components/make_consistent.py'
PATHS['adjustment_module'] = HOME + '/components/make_adjusted.py'
PATHS['treetagger'] = 'tree-tagger-bundle'
PATHS['treetagger_tokenizer'] = \
    '/usr/local/tree-tagger-linux-3.2/cmd/tokenize.pl'
