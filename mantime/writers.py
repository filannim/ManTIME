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
import cgi

from model import TemporalExpression
from model import Event


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
    def write(self, document):
        pass


class SimpleXMLFileWriter(FileWriter):
    """This class is a simple XML writer."""

    def __init__(self):
        super(SimpleXMLFileWriter, self).__init__()

    def write(self, document):
        """
        """
        return [(word.word_form, word.predicted_label)
                for sent in document.sentences
                for word in sent.words]


class TempEval3Writer(FileWriter):
    """This class is a writer in the TempEval-3 format."""

    def __init__(self):
        super(TempEval3Writer, self).__init__()

    def write(self, documents):
        """It writes on an external file in the TempEval-3 format.

        """

        outputs = []
        for document in documents:
            output = []
            output.append('<?xml version="1.0" ?>')
            output.append('<TimeML xmlns:xsi="http://www.w3.org/2001/XMLSche' +
                          'ma-instance" xsi:noNamespaceSchemaLocation="http:' +
                          '//timeml.org/timeMLdocs/TimeML_1.2.1.xsd">\n')
            output.append(u'<DOCID>{doc_id}</DOCID>\n'.format(
                doc_id=document.doc_id))
            output.append(str('<DCT><TIMEX3 tid="t0" type="DATE" value="{}" ' +
                              'temporalFunction="false" functionInDocument="' +
                              'CREATION_TIME">{}</TIMEX3></DCT>\n'
                              ).format(document.dct, document.dct_text))
            output.append(u'<TITLE>{}</TITLE>\n\n'.format(document.title))

            text = list(document.text)
            # TO-DO: This works properly only for IO annotation schema!
            for element in document.predicted_annotations:
                # sostituisco il pezzetto nel testo con la stringa annotata
                if isinstance(element, TemporalExpression):
                    utterance = document.dct.replace('-', '')
                    element.normalise(document, utterance, 'general')
                    annotation = str('<TIMEX3 tid="{tid}" type="{ttype}" ' +
                                     'mod="{mod}" value="{value}">' +
                                     '{text}</TIMEX3>').format(
                                         **element.__dict__)
                elif isinstance(element, Event):
                    element.normalise(document)
                    annotation = str('<EVENT eid="{eid}" class="{eclass}">' +
                                     '{text}</EVENT>').format(
                                         **element.__dict__)
                text[element.start + document.text_offset] = annotation
                # empty the remaining characters
                for i in xrange(document.text_offset + element.start + 1,
                                document.text_offset + element.end):
                    text[i] = ''

            output.append(u'<TEXT>{}</TEXT>\n\n'.format(
                ''.join(text)))

            # MAKEINSTANCEs
            events = (e for e in document.predicted_annotations
                      if isinstance(e, Event))
            for event in events:
                instance = str('<MAKEINSTANCE eiid="{eid}" eventID="{eid}" ' +
                               'pos="{pos}" tense="{tense}" ' +
                               'aspect="{aspect}" polarity="{polarity}" ' +
                               'modality="{modality}" />').format(
                                   **event.__dict__)
                output.append(instance)
            output.append('')

            # TLINKs
            output.append('</TimeML>\n')
            outputs.append('\n'.join(output))
        return outputs


class i2b2Writer(FileWriter):
    """This class is a writer in the i2b2 format."""

    def __init__(self, inline=False):
        assert isinstance(inline, bool), 'Wrong inline variable type.'
        super(i2b2Writer, self).__init__()
        self.inline = inline

    def write(self, documents):
        """It writes on an external file in the i2b2 format.

        Can write both in inline and stand-off XML format.
        """
        if self.inline:
            return self.write_inline(documents)

        # stand-off way
        outputs = []
        for document in documents:
            output = []
            output.append('<?xml version="1.0" ?>')
            output.append('<ClinicalNarrativeTemporalAnnotation>')
            output.append(u'<TEXT><![CDATA[{}]]></TEXT>'.format(document.text))

            output.append(u'<TAGS>')
            # TIMEX3s and EVENTs
            for element in document.predicted_annotations:
                element.text = document.get_text(element.start, element.end)
                cstart, cend = element.start + 1, element.end + 1
                if isinstance(element, TemporalExpression):
                    element.normalise(document, document.dct_text, 'clinical')
                    xml_tag = str('<TIMEX3 id="{tid}" start="{cstart}" ' +
                                  'end="{cend}" text="{text}" type="{ttype}"' +
                                  ' val="{value}" mod="{mod}" />').format(
                        cstart=cstart, cend=cend, **element.__dict__)
                elif isinstance(element, Event):
                    element.normalise(document)
                    xml_tag = str('<EVENT id="{eid}" start="{cstart}" ' +
                                  'end="{cend}" text="{text}" ' +
                                  'modality="{modality}" ' +
                                  'polarity="{polarity}" ' +
                                  'type="{eclass}" />').format(
                        cstart=cstart, cend=cend, **element.__dict__)
                output.append(xml_tag)

            # SECTIMEs
            output.append(str('<SECTIME id="S0" start="_" end="_" ' +
                              'text="_" type="ADMISSION" ' +
                              'dvalue="{}" />').format(
                document.sec_times.admission_date))
            output.append(str('<SECTIME id="S0" start="_" end="_" ' +
                              'text="_" type="DISCHARGE" ' +
                              'dvalue="{}" />').format(
                document.sec_times.discharge_date))

            # TLINKs

            # Ending
            output.append(u'</TAGS>')
            output.append(u'</ClinicalNarrativeTemporalAnnotation>')

            outputs.append('\n'.join(output))
        return outputs

    def write_inline(self, documents):
        """It writes on an external file in the TempEval-3 format.

        """
        outputs = []
        for document in documents:
            output = []
            output.append('<?xml version="1.0" ?>')
            output.append('<ClinicalNarrativeTemporalAnnotation>')

            text = [cgi.escape(c, True) for c in list(document.text)]
            # TO-DO: This works properly only for IO annotation schema!
            for element in document.predicted_annotations:
                # sostituisco il pezzetto nel testo con la stringa annotata
                if isinstance(element, TemporalExpression):
                    element.normalise(document, document.dct_text, 'clinical')
                    annotation = unicode('<TIMEX3 tid="{tid}" type="{ttype}"' +
                                         ' mod="{mod}" value="{value}">' +
                                         '{text}</TIMEX3>').format(
                                             **element.__dict__)
                elif isinstance(element, Event):
                    element.normalise(document)
                    annotation = unicode('<EVENT id="{eid}" type="{eclass}" ' +
                                         'modality="{modality}" ' +
                                         'polarity="{polarity}"' +
                                         '>{text}</EVENT>').format(
                                             **element.__dict__)
                text[element.start + document.text_offset] = annotation
                # empty the remaining characters
                for i in xrange(document.text_offset + element.start + 1,
                                document.text_offset + element.end):
                    text[i] = ''

            output.append(u'<TEXT>{}</TEXT>\n\n'.format(
                ''.join(text)))

            output.append(u'')

            # TLINKs
            output.append(u'</ClinicalNarrativeTemporalAnnotation>')
            outputs.append('\n'.join(output))
        return outputs


class HTMLWriter(FileWriter):
    """This class is a writer in HTML/CSS3 format."""

    def __init__(self, domain):
        assert domain in ('clinical', 'general'), 'Wrong domain.'
        super(HTMLWriter, self).__init__()
        self.domain = domain

    def write(self, documents, domain='general'):
        """It writes on an external file in the HTML/CSS3 format.

        """
        maxcdn_bootstrap = 'https://maxcdn.bootstrapcdn.com/bootstrap/3.3.4/'
        outputs = []
        for document in documents:
            output = []
            output.append('<?xml version="1.0" encoding="UTF-8"?>')
            output.append('<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 ' +
                          'Strict//EN" "http://www.w3.org/TR/xhtml1/DTD/' +
                          'xhtml1-strict.dtd">')
            output.append('<html xmlns="http://www.w3.org/1999/xhtml">')
            output.append('<meta name="Author" content="Michele Filannino" />')
            output.append('<link rel="stylesheet" href="{}css/bootstrap.min.css" />'.format(maxcdn_bootstrap))
            output.append('<link rel="stylesheet" href="{}css/bootstrap-theme.min.css" />'.format(maxcdn_bootstrap))
            output.append('<script src="{}js/bootstrap.min.js"></script>'.format(maxcdn_bootstrap))
            output.append('<link href="https://rawgit.com/filannim/ManTIME/master/static/mantime.css" rel="stylesheet" type="text/css" />')
            output.append('<title>{}</title>'.format(str(document.title)))

            text = [cgi.escape(c, True) for c in list(document.text)]
            # TO-DO: This works properly only for IO annotation schema!
            for element in document.predicted_annotations:
                # sostituisco il pezzetto nel testo con la stringa annotata
                if isinstance(element, TemporalExpression):
                    element.normalise(document, document.dct_text, 'clinical')
                    annotation = unicode('<TIMEX3 tid="{tid}" type="{ttype}"' +
                                         ' mod="{mod}" value="{value}">' +
                                         '{text}</TIMEX3>').format(
                                             **element.__dict__)
                elif isinstance(element, Event):
                    element.normalise(document)
                    annotation = unicode('<EVENT id="{eid}" type="{eclass}" ' +
                                         'modality="{modality}" ' +
                                         'polarity="{polarity}"' +
                                         '>{text}</EVENT>').format(
                                             **element.__dict__)
                text[element.start + document.text_offset] = annotation
                # empty the remaining characters
                for i in xrange(document.text_offset + element.start + 1,
                                document.text_offset + element.end):
                    text[i] = ''

            output.append(u'<body>')
            output.append(u'''<div id="wrapper">

                            <div id="sidebar-wrapper" style="background-color: #f7f7f7;">
                              <ul class="sidebar-nav">
                                <li class="sidebar-brand">Legend</li>
                                <li>TEMPORAL EXPRESSIONS</li>
                                <ul>
                                  <li><TIMEX3 value="value" type="DATE">date</TIMEX3></li>
                                  <li><TIMEX3 value="value" type="TIME">time</TIMEX3></li>
                                  <li><TIMEX3 value="value" type="DURATION">duration</TIMEX3></li>
                                  <li><TIMEX3 value="value" type="SET">frequency</TIMEX3></li>
                                </ul>
                                <li>EVENTS</li>
                                <ul>
                                  <li><EVENT type="PROBLEM">problem</EVENT></li>
                                  <li><EVENT type="TREATMENT">treatment</EVENT></li>
                                  <li><EVENT type="TEST">test</EVENT></li>
                                  <li><EVENT type="OCCURRENCE">occurrence</EVENT></li>
                                  <li><EVENT type="CLINICAL_DEPT">clinical department</EVENT></li>
                                  <li><EVENT type="EVIDENTIAL">evidential</EVENT></li>
                                </ul>
                            </ul>
                            </div>

                            <div id="page-content-wrapper">
                              <div class="container-fluid">
                                <div class="row">
                                  <div class="col-lg-12">
                                    <h1>{}</h1>
                                    <hr />'''.format(str(document.title)))

            output.append(u''.join(text))

            output.append(u'''<footer class="footer"><p>Generated by <a href="https://github.com/filannim/ManTIME" style="display: inline;">ManTIME</a> &copy; 2015 Michele Filannino</p><p><img src="https://rawgit.com/filannim/ManTIME/master/static/uni_logo.jpg" height="55"/></p></footer></div></div></div></div>''')
            output.append(u'<script src="https://code.jquery.com/jquery-2.1.4.min.js"></script>')

            output.append(u'</body>')

            # TLINKs
            output.append(u'</html>')
            outputs.append('\n'.join(output))
        return outputs


class AttributeMatrixWriter(Writer):
    """This class writes the attribute matrix taken by ML algorithms."""

    def __init__(self, separator='\t', include_header=False):
        super(AttributeMatrixWriter, self).__init__()
        self.separator = separator
        self.header = include_header

    def write(self, documents):
        # save_to = os.path.abspath(save_to)
        # with open(save_to, 'w') as output:
        output = []
        if self.header:
            first_word = documents[0].sentences[0].words[0]
            header = [k for k, _ in sorted(first_word.attributes.items())]
            output.append(self.separator.join(header))
        for document in documents:
            for sentence in document.sentences:
                for word in sentence.words:
                    row = [v for _, v in sorted(word.attributes.items())]
                    row.append(word.predicted_label)
                    output.append(self.separator.join(row))
                output.append('')
        # logging.info('{} exported.'.format(save_to))
        return '\n'.join(output)

Writer.register(FileWriter)
FileWriter.register(SimpleXMLFileWriter)
FileWriter.register(TempEval3Writer)
FileWriter.register(AttributeMatrixWriter)
FileWriter.register(i2b2Writer)


def main():
    '''Simple ugly non-elegant test.'''
    import sys
    from readers import TempEval3FileReader

    file_reader = TempEval3FileReader(annotation_format='IO')
    document = file_reader.parse(sys.argv[1])
    file_writer = i2b2Writer()
    print file_writer.write([document])

if __name__ == '__main__':
    main()
