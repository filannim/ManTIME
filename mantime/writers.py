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

from model import Document


class Writer(object):
    """This class is an abstract writer for ManTIME."""
    __metaclass__ = ABCMeta

    @abstractmethod
    def write(self, documents):
        pass


class FileWriter(Writer):
    """This classs is an abstract file writer for ManTIME."""
    __metaclass__ = ABCMeta

    def __init__(self):
        pass

    @abstractmethod
    def write(self, documents, save_to):
        pass


class SimpleWriter(Writer):
    """This class is a simple writer for ManTIME."""

    def __init__(self):
        super(SimpleWriter, self).__init__()

    def write(self, documents):
        """
        """
        pass


class SimpleXMLFileWriter(FileWriter):
    """This class is a reader for TempEval-3 files."""

    def __init__(self):
        super(SimpleXMLFileWriter, self).__init__()

    def write(self, documents):
        """
        """
        return [word.predicted_label
                for doc in documents
                for sent in doc.sentences
                for word in sent.words]


Writer.register(FileWriter)
FileWriter.register(SimpleXMLFileWriter)


def main():
    '''Simple ugly non-elegant test.'''
    import sys
    from readers import TempEval3FileReader

    file_reader = TempEval3FileReader(annotation_format='IO')
    document = file_reader.parse(sys.argv[1])
    file_writer = SimpleWriter()
    print file_writer.write([document])

if __name__ == '__main__':
    main()
