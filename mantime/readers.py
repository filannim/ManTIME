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

'''It contains all the readers for ManTIME.'''

from abc import ABCMeta, abstractmethod, abstractproperty
from StringIO import StringIO
import xml.etree.cElementTree as etree

from nltk import TreebankWordTokenizer

from model import Document
from model import Sentence
from model import Token
from model import Gap

class Reader(object):
    '''This class is an abstract reader for ManTIME.'''
    __metaclass__ = ABCMeta

    @abstractmethod
    def parse(self, text):
        '''It reads an input text.'''
        pass


class FileReader(Reader):
    '''This classs is an abstract file reader for ManTIME.'''
    __metaclass__ = ABCMeta

    def __init__(self):
        self._extensions = set()

    @abstractproperty
    def extensions(self):
        '''It returns the set of the file extensions.'''
        pass

    @abstractmethod
    def parse(self, file_path):
        pass


class TempEval_3_FileReader(FileReader):
    '''This class is a reader for TempEval-3 files.'''

    def __init__(self):
        super(TempEval_3_FileReader, self).__init__()
        self._extensions = {'TE3input'}
        self.tags_to_spot = {'TIMEX3', 'EVENT', 'SIGNAL'}
        self.text = None
        self.dct = None
        self.annotations = None
        self.tree = None

    @property
    def extensions(self):
        return self._extensions

    def parse(self, file_path):
        '''Extracts relevant information from a TempEval-3 annotated file.'''
        document = etree.parse(file_path)
        text_node = document.findall(".//TEXT")[0]
        xpath_dct = ".//TIMEX3[@functionInDocument='CREATION_TIME']"
        self.dct = document.findall(xpath_dct)[0].attrib['value']
        self.text = etree.tostring(text_node, method='text')
        self.annotations = self.__offsets(etree.tostring(text_node))
        self.tree = self.__build_tree(file_path)
        return self.tree

    def __build_tree(self, file_path):
        '''It builds the tree representation of document.'''
        sentence_splitter = lambda text: text.replace(
            '\n\n', '\\sentence\n\n\\sentence').split('\\sentence')
        revise = lambda token: token
        tokenizer = TreebankWordTokenizer()
        start_counter = 0
        document = Document(file_path, dct=self.dct)
        for line in sentence_splitter(self.text):
            if line == '\n\n':
                document.add_child(Gap(line, start_counter, 2+start_counter))
                start_counter += 2
                line = line[2:]
            else:
                line_length = len(line)
                sentence_node = Sentence(start_counter, line_length+start_counter)
                start_token = start_counter
                tokens = map(revise, tokenizer.tokenize(line))
                while line:
                    node = None
                    if tokens:
                        word = tokens[0]
                        if line[:len(word)] == word:
                            node = Token(tokens.pop(0), start_token, len(word)+start_token)
                        else:
                            node = Gap(line[0], start_token, 1+start_token)
                    else:
                        node = Gap(line[0], start_token, 1+start_token)
                    sentence_node.add_child(node)
                    start_token += len(node)
                    line = line[len(node):]
                document.add_child(sentence_node)
                start_counter += line_length
                assert line_length == sum(len(node) for node in sentence_node.children)
            assert not(line)
        assert not(tokens)
        return document


    def __offsets(self, source, start_offset=0):
        '''It yields the annotations found in the document.'''
        for event, element in etree.iterparse(
                StringIO(source), events=('start', 'end')):
            if event == 'start':
                if element.tag in self.tags_to_spot:
                    yield (element.tag, element.attrib,
                           (start_offset, start_offset + len(element.text)))
                start_offset += len(element.text)
            elif event == 'end':
                if element.text is not None and element.tail is not None:
                    start_offset += len(element.tail)

Reader.register(FileReader)
FileReader.register(TempEval_3_FileReader)

def main():
    import sys
    file_reader = TempEval_3_FileReader()
    file_reader.parse(sys.argv[1])
    print file_reader.__dict__.items()


if __name__ == '__main__':
    main()
