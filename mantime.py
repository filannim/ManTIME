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

from __future__ import division
import multiprocessing
from multiprocessing import Pool
from functools import partial
import math
from os import listdir
from os.path import abspath
from os.path import basename
from os.path import dirname
import argparse


import mantime.nlp_functions
from mantime.feature_factory import FeatureFactory
from mantime.text_extractor import TextExtractor
from mantime.tagger import Tagger


class ManTIME(object):

    def __init__(self, reader, feature_factory, writer,
                 processes=multiprocessing.cpu_count()*2,
                 post_processing_pipeline=True):
        self.reader = reader
        self.feature_factory = feature_factory
        self.writer = writer
        self.processes = processes
        self.post_processing_pipeline = post_processing_pipeline

    def extract_from_folder(self, folder_path):
        files = [str(folder_path+'/'+f) for f in listdir(folder_path)
                 if f.endswith('.tml.TE3input')]
        chunk_size = math.ceil(len(files)/(self.processes))
        chunks = [files[i:i+chunk_size] for i in range(0, len(files), chunk_size)]
        pool = Pool(processes=self.processes)
        pool.map(partial(self.__pipeline,
                 pp_pipeline=self.post_processing_pipeline), chunks)

    def extract_from_file(self, file_path, use_post_processing_pipeline=True):
        pass


    def __pipeline(self, file_set, pp_pipeline=True):
        reader = TextExtractor()
        feature_factory = FeatureFactory()
        tagger = Tagger()
        start_id = 1
        for file in file_set:
            source_folder_path = abspath(dirname(file))
            original_file = abspath(file)
            annotated_file = source_folder_path + '/annotated_output/' + basename(file).replace(".TE3input","")
            utterance = reader.get_utterance(original_file)
            save_file = open(annotated_file, 'w')
            save_file_content = open(original_file, 'r').read()
            for sentence, offsets in reader.read(original_file, ['TIMEX3', 'EVENT', 'SIGNAL']):
                sentence = sentence.replace('__space__', ' ').strip()
                attribute_names, attribute_values = feature_factory.get_sentence_attributes([sentence, offsets], 'TIMEX3', True)
                tagged = tagger.tag(sentence, attribute_names, attribute_values, utterance, start_id, post_processing_pipeline=pp_pipeline)
                save_file_content = save_file_content.replace(sentence.replace("&", "&amp;"), tagged['sentence'])
                start_id = tagged['start_id']
            start_id = 1
            save_file.write(save_file_content)
            save_file.close()


def main():
    '''It annotates documents in a specific folder.'''
    parser = argparse.ArgumentParser(
        description='ManTIME: temporal information extraction')
    parser.add_argument(dest='folder', metavar='input folder', nargs='*')
    parser.add_argument('-ppp', '--post_processing_pipeline', dest='pipeline',
                        action='store_true',
                        help='it uses the post processing pipeline.')
    args = parser.parse_args()

    mantime = ManTIME()
    mantime.processes = 3
    mantime.post_processing_pipeline = True
    mantime.reader = TempEval_3_Reader()
    mantime.writer = ISO_TimeML_Writer()
    mantime.extract_from_folder(args.folder)


if __name__ == '__main__':
    main()
