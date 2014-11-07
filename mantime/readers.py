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

"""It contains all the readers for ManTIME.

   A reader must have a parse() method which is responsible for reading the
   input file and return a Document object, which is our internal
   representation of any input document (whetever the format is).

   In order to force the existence of the parse() method I preferred Python
   interfaces to the duck typing practice.
"""

from abc import ABCMeta, abstractmethod
import xml.etree.cElementTree as etree
from StringIO import StringIO

from nltk import ParentedTree

from model import Document
from model import Sentence
from model import Word
from model import DependencyGraph
from settings import PATH_CORENLP_FOLDER


class BatchedCoreNLP(object):

    def __init__(self, stanford_dir):
        from corenlp import batch_parse
        self.DIR = stanford_dir
        self.batch_parse = batch_parse

    def parse(self, text):
        import os
        import tempfile
        dirname = tempfile.mkdtemp()
        with tempfile.NamedTemporaryFile('w', dir=dirname) as tmp:
            tmp.write(text)
            tmp.flush()
            result = self.batch_parse(os.path.dirname(tmp.name), self.DIR)
            result = list(result)[0]
        return result

CORENLP = BatchedCoreNLP(PATH_CORENLP_FOLDER)


class Reader(object):
    """This class is an abstract reader for ManTIME."""
    __metaclass__ = ABCMeta

    @abstractmethod
    def parse(self, text):
        pass


class FileReader(Reader):
    """This classs is an abstract file reader for ManTIME."""
    __metaclass__ = ABCMeta

    def __init__(self):
        pass

    @abstractmethod
    def parse(self, file_path):
        pass


class TempEval3FileReader(FileReader):
    """This class is a reader for TempEval-3 files."""

    def __init__(self, annotation_format='IO', extension_filter='.tml'):
        super(TempEval3FileReader, self).__init__()
        self.tags_to_spot = {'TIMEX3', 'EVENT', 'SIGNAL'}
        self.annotations = []
        self.annotation_format = annotation_format
        self.extension_filter = extension_filter

    def parse(self, file_path):
        """It parses the content of file_path and extracts relevant information
        from a TempEval-3 annotated file. Those information are packed in a
        Document object, which is our internal representation.
        """
        xml_document = etree.parse(file_path)
        text_node = xml_document.findall(".//TEXT")[0]
        text = etree.tostring(text_node, method='text')
        xml = etree.tostring(text_node)
        xpath_dct = ".//TIMEX3[@functionInDocument='CREATION_TIME']"
        # StanfordParser strips internally the text :(
        l_strip_chars = len(text.lstrip()) - len(text)
        stanford_tree = CORENLP.raw_parse(text)
        document = Document(file_path)
        document.dct = xml_document.findall(xpath_dct)[0].attrib['value']
        document.text = text
        document.gold_annotations = self.__get_annotations(xml, l_strip_chars)
        document.coref = stanford_tree.get('coref', None)

        for stanford_sentence in stanford_tree['sentences']:
            dependencies = stanford_sentence.get('dependencies', None)
            i_dependencies = stanford_sentence.get('indexeddependencies', None)
            i_dependencies = DependencyGraph(i_dependencies)
            parsetree = ParentedTree(stanford_sentence.get('parsetree', u''))
            sentence_text = stanford_sentence.get('text', u'')

            sentence = Sentence(dependencies=dependencies,
                                indexed_dependencies=i_dependencies,
                                parsetree=parsetree,
                                text=sentence_text)
            for id, (word_form, attr) in enumerate(stanford_sentence['words']):
                word = Word(word_form=word_form,
                            char_offset_begin=attr['CharacterOffsetBegin'],
                            char_offset_end=attr['CharacterOffsetEnd'],
                            lemma=attr['Lemma'],
                            named_entity_tag=attr['NamedEntityTag'],
                            part_of_speech=attr['PartOfSpeech'],
                            id_token=id)
                sentence.words.append(word)
            document.sentences.append(sentence)

        document.store_gold_annotations(self.annotation_format)
        del stanford_tree, l_strip_chars, text, text_node, xml_document
        return document

    def __get_annotations(self, source, start_offset=0):
        '''It returns the annotations found in the document in the following
           format:
           [
            ('TAG', {ATTRIBUTES}, (start_offset, end_offset)),
            ('TAG', {ATTRIBUTES}, (start_offset, end_offset)),
            ...
            ('TAG', {ATTRIBUTES}, (start_offset, end_offset))
           ]
        '''
        annotations = []
        for event, element in etree.iterparse(
                StringIO(source), events=('start', 'end')):
            if event == 'start':
                if element.tag in self.tags_to_spot:
                    end_offset = start_offset + len(element.text)
                    annotations.append((element.tag, element.attrib,
                                        (start_offset, end_offset)))
                start_offset += len(element.text)
            elif event == 'end':
                if element.text is not None and element.tail is not None:
                    start_offset += len(element.tail)
        return annotations


Reader.register(FileReader)
FileReader.register(TempEval3FileReader)


def main():
    '''Simple ugly non-elegant test.'''
    import sys
    import pprint
    file_reader = TempEval3FileReader(annotation_format='IO')
    document = file_reader.parse(sys.argv[1])
    pprint.pprint(document.__dict__)

if __name__ == '__main__':
    main()
