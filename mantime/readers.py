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
import re

from lxml import etree
from lxml.html import fromstring

from nlp_functions import TreeTaggerTokeniser

class Reader(object):
    '''This class is an abstract reader for ManTIME.'''
    __metaclass__ = ABCMeta

    @abstractmethod
    def read(self, text):
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
    def read(self, file_path):
        pass


class TempEval_3_FileReader(FileReader):
    '''This class is a reader for TempEval-3 files.'''

    def __init__(self):
        super(TempEval_3_FileReader, self).__init__()
        self._extensions = {'TE3input'}
        self.corpus = []
        self.tokeniser = TreeTaggerTokeniser()
        self.tags = {'TIMEX3', 'EVENT', 'SIGNAL'}

    @property
    def extensions(self):
        return self._extensions

    def read(self, file_path):
        '''Extracts the text from a file and returns a list of sentences along
        with timexes and events' offsets.
        '''
        document = etree.parse(file_path)
        utterance = self.__get_utterance(document)
        text = etree.tostring(document.xpath("//TEXT")[0], encoding='utf-8', method='text')
        xml_form = re.findall('<TEXT[^>]*?>([\w\W]*)</TEXT>', xml_form)[0]
        xml_form = xml_form.replace(' ', ' __space__ ').split('\n\n')
        xml_form = [x for x in xml_form if x != '']
        txt_form = [fromstring(x).text_content().replace(' __space__ ', ' ')
                    for x in xml_form]
        result = []
        for i, sentence in enumerate(txt_form):
            offsets = self.__get_offsets_tokens(
                sentence, xml_form[i].replace(' __space__ ', ' '), self.tags)
            result.append((sentence, offsets))
        return utterance, result

    def __get_offsets_tokens(self, sentence, xml_sentence, tagnames):
        sentence = sentence.replace('`', '\`')
        xml_sentence = xml_sentence.replace('`', '\`')
        tags = '|'.join(tagnames)
        sentence_tokenised = self.tokeniser.tokenize(sentence)
        xml_tokenised = self.tokeniser.tokenize(xml_sentence)
        regEx = '(<('+tags+')[^>]*?>(.*?)</(?:'+tags+')>)'
        tags_full_tag_content = [[self.tokeniser.tokenize(full),tag,self.tokeniser.tokenize(' O '+content+' O ')[1:-1]] for full,tag,content in re.findall(regEx, xml_sentence)]
        offsets_full_tag_content = [[list(KMP.KMP(xml_tokenised,full_tokenised,True))[0],list(KMP.KMP(full_tokenised,content_tokenised,True))[-1],tag] for full_tokenised,tag,content_tokenised in tags_full_tag_content]
        displacement = 0
        offsets = {}; [offsets.setdefault(tag,[]) for tag in tagnames]
        for annotation in offsets_full_tag_content:
            updt_start = annotation[0][0] - displacement
            updt_end = updt_start + (annotation[1][1]-annotation[1][0])
            displacement += (annotation[0][1]-annotation[0][0])-(annotation[1][1]-annotation[1][0])
            offsets[annotation[2]].append([updt_start,updt_end])
        return offsets

    def __get_offsets(self, input, tagnames):
        tags = '|'.join(tagnames)
        regEx = '<('+tags+')[^>]*?>(.*?)</(?:'+tags+')>'
        full_offsets = [[c.start(), c.end()] for c in re.finditer(regEx, input)]
        content_offsets = [[c,len(c[1])] for c in re.findall(regEx, input)]
        offsets = {}; [offsets.setdefault(tag,[]) for tag in tagnames]
        displacement = 0
        for i, chunk in enumerate(full_offsets):
            updt_start = chunk[0] - displacement
            updt_end = updt_start + content_offsets[i][1]
            displacement += (chunk[1]-chunk[0])-content_offsets[i][1]
            offsets[content_offsets[i][0][0]].append([updt_start, updt_end])
        return offsets

    def __extract_sentences(self, source, tags_to_spot):
        """Calls the read function"""
        self.read(source, tags_to_spot)

    def __get_utterance(self, doc):
        utterance = doc.xpath("//TIMEX3[@functionInDocument='CREATION_TIME']")
        return utterance[0].attrib['value'].replace('-', '')

    def __get_header(self, file_name):
        header = ''
        for line in open(file_name, 'r').xreadlines():
            if line.startswith('<TEXT>'):
                return header + '<TEXT>'
            else:
                header += line
        return header + '<TEXT>'

    def __get_footer(self, file_name):
        return '</TEXT>\n</TimeML>'

Reader.register(FileReader)
FileReader.register(TempEval_3_FileReader)
