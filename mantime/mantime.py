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
import sys

from distutils.version import StrictVersion

from readers import TempEval3Reader
from writers import SimpleXMLFileWriter
# import mantime.nlp_functions
# from mantime.feature_factory import FeatureFactory
# from mantime.text_extractor import TextExtractor
# from mantime.tagger import Tagger


class ManTIME(object):

    def __init__(self, reader, feature_factory, writer,
                 processes=multiprocessing.cpu_count()*2,
                 post_processing_pipeline=True):
        self.reader = reader
        self.feature_factory = feature_factory
        self.writer = writer
        self.processes = processes
        self.post_processing_pipeline = post_processing_pipeline

        """ HAVE A LOOK HERE IN ORDER TO CRAFT THE MANTIME CLASS AND ITS
            BEHAVIOUR. THIS SUMS UP SOME IDEAS.

            Take the following as pseudo-code, ignore the rest.

            # check for the dependencies and imports (are all the modules
              required there? what about the versions?)
            # is Wapiti installed in the expected folder?
            # inizialise a server for the Stanford Parser
              hopefully we should be faster with the server and we should be
              able to easily parallelise the execution (with multiprocessing)
            # in the init of MANTIME I need to ask for the IOB annotation
              format. So that using the same MANTIME object I make sure I've
              got back the same annotation style.

            Please, do these things keeping in mind that we need to use LOG.
        """
        # start STANFORDCoreNLP


    def annotate(self, list_of_files, reader_type):
        """ If any of the files in the list doesn't exist just shout a WARNING
            on the LOG.

            I am not sure about the type of reader_type variable. (1) If it's
            a string then I need a switch to internally create the right object
            but this is ugly since then I need to update the switch every time
            I introduce a new reader type. (2) If it's the reader, directly,
            than I need to create it from the outside. Is this allright?

            return List of <Document>
        """
        pass


    def train(self, list_of_files, reader_type, save_to):
        """ The doubts are the same as in the annotate function.

            This method automatically parses the input files, gets the internal
            representation from them, runs the attribute extractor
            and train a Wapiti model. It saves the model where save_to says.
            Attribute topology for CRF should be dealt internally in the
            classifier module (this should be changed in the future).

            return <Classification_Model>
        """
        pass

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

    # Lets ensure the python modules requirements are met.
    requirements = [tuple(requirement.strip().split('==')) for requirement
                    in open('requirements.txt', 'r').xreadlines()]
    for requested_module, requested_version in requirements:
        try:
            locals()[requested_module] = __import__(requested_module)
            current_version = locals()[requested_module].__version__
            if StrictVersion(current_version) < \
               StrictVersion(requested_version):
                sys.stderr.write(("WARNING: ManTIME requires {} {}, " +
                                  "an older version ({}) is installed.\n")
                                 .format(requested_module,
                                         requested_version,
                                         current_version))
        except ImportError:
            sys.stderr.write("ERROR: {} module not found.\n"
                             .format(requested_module))
            sys.exit(2)
        except AttributeError:
            sys.stderr.write(("WARNING: I can't verify {}'s version. " +
                              "Make sure it's {} (or newer).\n")
                             .format(requested_module, requested_version))

    # Parse input
    parser = argparse.ArgumentParser(
        description='ManTIME: temporal information extraction')
    parser.add_argument(dest='folder', metavar='input folder', nargs='*')
    parser.add_argument('-ppp', '--post_processing_pipeline', dest='pipeline',
                        action='store_true',
                        help='it uses the post processing pipeline.')
    args = parser.parse_args()

    # Expected usage of ManTIME
    mantime = ManTIME()
    mantime.processes = 3
    mantime.post_processing_pipeline = True
    mantime.reader = TempEval3Reader()
    mantime.writer = SimpleXMLFileWriter()
    mantime.extract_from_folder(args.folder)


if __name__ == '__main__':
    main()
