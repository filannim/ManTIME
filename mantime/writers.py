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
import logging
import os


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


class SimpleXMLFileWriter(FileWriter):
    """This class is a simple XML writer."""

    def __init__(self):
        super(SimpleXMLFileWriter, self).__init__()

    def write(self, documents, save_to):
        """
        """
        return [word.predicted_label
                for doc in documents
                for sent in doc.sentences
                for word in sent.words]


class TempEval3Writer(FileWriter):
    """This class is a writer in the TempEval-3 format."""
    pass


class AttributeMatrixWriter(Writer):
    """This class writes the attribute matrix taken by ML algorithms."""

    def __init__(self, separator='\t', include_header=False):
        super(AttributeMatrixWriter, self).__init__()
        self.separator = separator
        self.header = include_header

    def write(self, documents, save_to):
        save_to = os.path.abspath(save_to)
        with open(save_to, 'w') as output:
            if self.header:
                first_word = documents[0].sentences[0].words[0]
                header = [k for k, _ in sorted(first_word.attributes.items())]
                output.write(self.separator.join(header))
                output.write('\n')
            for document in documents:
                for sentence in document.sentences:
                    for word in sentence.words:
                        row = [v for _, v in sorted(word.attributes.items())]
                        output.write(self.separator.join(row))
                        output.write(self.separator + word.gold_label)
                        output.write('\n')
                    output.write('\n')
        logging.info('{} exported.'.format(save_to))

Writer.register(FileWriter)
FileWriter.register(SimpleXMLFileWriter)
FileWriter.register(TempEval3Writer)
FileWriter.register(AttributeMatrixWriter)


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
