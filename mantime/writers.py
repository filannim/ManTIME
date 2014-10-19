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
    def parse(self, text):
        pass


class FileWriter(Writer):
    """This classs is an abstract file writer for ManTIME."""
    __metaclass__ = ABCMeta

    def __init__(self):
        pass

    @abstractmethod
    def write(self, save_to):
        pass


class SimpleXMLFileWriter(FileWriter):
    """This class is a reader for TempEval-3 files."""

    def __init__(self):
        super(SimpleXMLFileWriter, self).__init__()

    def write(self, save_to):
        """
        """
        if not save_to.endswith('.xml'):
            save_to += '.xml'
        open(save_to, 'w').close()


Writer.register(FileWriter)
FileWriter.register(SimpleXMLFileWriter)


def main():
    '''Simple ugly non-elegant test.'''
    import sys
    import pprint
    file_reader = SimpleXMLFileWriter(annotation_format='IO')
    document = file_reader.parse(sys.argv[1])
    pprint.pprint(document.__dict__)

if __name__ == '__main__':
    main()
