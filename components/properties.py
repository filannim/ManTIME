#!/usr/bin/python
#
#	Copyright 2012 Michele Filannino
#
#	gnTEAM, School of Computer Science, University of Manchester.
#	All rights reserved. This program and the accompanying materials
#	are made available under the terms of the GNU General Public License.
#	
#	author: Michele Filannino
#	email:  filannim@cs.man.ac.uk
#	
#	This work is part of TempEval-3 challenge.	
#	For details, see www.cs.man.ac.uk/~filannim/

installation_path = '/home/filannim/Dropbox/Workspace/ManTIME'

property = {}

property['path_crf++'] = '/home/filannim/Downloads/CRF++-0.57/'
property['path_crf++_model'] = installation_path + '/components/crf_models/human_m1.crf'
property['path_consistency_module'] = installation_path + '/components/make_consistent.py'
property['path_adjustment_module'] = installation_path + '/components/make_adjusted.py'
property['path_treetagger'] = 'tree-tagger-bundle'
property['path_treetagger_tokenizer'] = '/usr/local/tree-tagger-linux-3.2/cmd/tokenize.pl'