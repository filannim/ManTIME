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

"""It contains all the writers for ManTIME.

   A writer must have a write() method which is responsible for returning a
   string representation of each document (Writer) or writing on a file
   (FileWriter). In any case a writer always takes in input a single document.

   In order to force the existence of the write() method I preferred Python
   interfaces to the duck typing practice.
"""

from abc import ABCMeta, abstractmethod
import logging
import os


class Writer(object):
    """This class is an abstract writer for ManTIME."""
    __metaclass__ = ABCMeta

    @abstractmethod
    def write(self, document):
        pass


class FileWriter(Writer):
    """This classs is an abstract file writer for ManTIME."""
    __metaclass__ = ABCMeta

    def __init__(self):
        pass

    @abstractmethod
    def write(self, document, save_to):
        pass


class SimpleXMLFileWriter(FileWriter):
    """This class is a simple XML writer."""

    def __init__(self):
        super(SimpleXMLFileWriter, self).__init__()

    def write(self, document, save_to):
        """
        """
        return [(word.word_form, word.predicted_label)
                for doc in documents
                for sent in doc.sentences
                for word in sent.words]


class TempEval3Writer(FileWriter):
    """This class is a writer in the TempEval-3 format."""

    def __init__(self):
        super(TempEval3Writer, self).__init__()

    def write(self, document, save_to):
        """It writes on an external file in the TempEval-3 format.

        """
        with open(os.path.abspath(save_to), 'w') as output:
            output.write('<?xml version="1.0" ?>\n')
            output.write('<TimeML xmlns:xsi="http://www.w3.org/2001/XMLSchem' +
                         'a-instance" xsi:noNamespaceSchemaLocation="http://' +
                         'timeml.org/timeMLdocs/TimeML_1.2.1.xsd">\n')
            output.write('\n')
            output.write('<DOCID>CNN_20130322_248</DOCID>\n')
            output.write('\n')
            output.write(str('<DCT><TIMEX3 tid="t0" type="DATE" value="{dct_' +
                         'value}" temporalFunction="false" functionInDocumen' +
                         't="CREATION_TIME">{dct_text}</TIMEX3></DCT>\n'
                         ).format(dct_value=, dct_text=))



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
