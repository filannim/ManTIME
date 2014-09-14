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

from __future__ import division
import re

from lxml import etree
from lxml.html import fromstring

import KMP
from nlp_functions import TreeTaggerTokeniser

class TextExtractor(object):
    """Extracts the text from each TML documents in the corpus"""

    def __init__(self):
        self.corpus = []
        self.tokeniser = TreeTaggerTokeniser()

    def read(self, file_name, tags_to_spot, debug=False):
        """Extracts the text from all the TML documents existing in a given 
        directory and returns a list of strings along with timex and event
        offsets"""
        
        utterance = self.get_utterance(file_name)
        # I extract all the text in the TEXT element (ignoring tags)
        doc = etree.parse(file_name)
        main_node = doc.xpath("//TEXT")[0]
        xml_form = etree.tostring(main_node).strip()
        xml_form = re.findall('<TEXT[^>]*?>([\w\W]*)</TEXT>', xml_form)[0]
        xml_form = xml_form.replace(' ',' __space__ ').split('\n\n')
        xml_form = [x for x in xml_form if x != ''] # filter out empy elements
        txt_form = [fromstring(x).text_content().replace(' __space__ ', ' ') for x in xml_form]
        
        if debug: print 'TXTFORM:', txt_form

        # For each sentence I save the timex and event offsets
        for i, sentence in enumerate(txt_form):
            # offsets = self.get_offsets(xml_form[i],['TIMEX3','EVENT'])
            offsets = self.get_offsets_tokens(sentence,xml_form[i].replace(' __space__ ', ' '),tags_to_spot)
            # self.compare_offsets(offsets, offsets_tokens, xml_form[i])
            yield [sentence, offsets]

    def compare_offsets(self, d1, d2, sentence):
        if set(d1.keys())!=set(d2.keys()):
            print "ERR: different keys!"
            print d1
            print d2
            print
            return
        for key in d1.iterkeys():
            if len(d1[key])!=len(d2[key]):
                print "ERR: ", sentence
                print "ERR: different offsets lists!", str(len(d1[key])), 'vs', str(len(d2[key]))
                print d1
                print d2
                print

    def get_offsets_tokens(self, sentence, xml_sentence, tagnames):
        sentence = sentence.replace('`','\`')
        xml_sentence = xml_sentence.replace('`','\`')
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

    def get_offsets(self, input, tagnames):
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

    def extract_sentences(self, source, tags_to_spot):
        """Calls the read function"""
        self.read(source, tags_to_spot)

    def get_utterance(self, file_name):
        doc = etree.parse(file_name)
        utterance_node = doc.xpath("//TIMEX3[@functionInDocument='CREATION_TIME']")[0]
        return utterance_node.attrib['value'].replace('-', '')

    def get_header(self, file_name):
        header = ''
        for line in open(file_name, 'r').xreadlines():
            if line.startswith('<TEXT>'):
                return header + '<TEXT>'
            else:
                header += line
        return header + '<TEXT>'

    def get_footer(self, file_name):
        return '</TEXT>\n</TimeML>'