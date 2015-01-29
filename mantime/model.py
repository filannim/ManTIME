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

"""It contains the classes for the document data model of ManTIME.

"""

import cgi

from normalisers.timex_general import normalise as normalise_general
from normalisers.timex_clinical import normalise as normalise_clinical


def format_annotation(start_token, end_token, annotations,
                      annotation_format='IO'):
    '''It returns the correct sequence class label for the given token.'''
    sequence_label = None
    tag_fired = ''
    attribs = None
    if annotations:
        for tag, attribs, (start_offset, end_offset) in annotations:
            tag_fired = tag
            if (start_offset, end_offset) == (start_token, end_token):
                sequence_label = 'W'
                break
            elif end_offset == end_token:
                sequence_label = 'E'
                break
            elif start_offset == start_token:
                sequence_label = 'B'
                break
            elif start_offset < start_token and end_offset > end_token:
                sequence_label = 'I'
                break
            else:
                sequence_label = 'O'
        if sequence_label not in list(annotation_format):
            sequence_label = 'I'
        if sequence_label == 'O':
            return sequence_label, {}
        else:
            return sequence_label + '-' + tag_fired, attribs
    else:
        return 'O', {}


class DependencyGraphNode(object):

    def __init__(self, label, parent=None, childs=None):
        self.label = label
        self.parent = parent
        if childs:
            self.childs = childs
        else:
            self.childs = dict()

    def __str__(self):
        childs = ' '.join(str(c) for c in self.childs.keys())
        return '(label:{}; parent: {}; childs:{})'.format(
            self.label, self.parent, childs)


class DependencyGraph(object):

    DUMMY_LABEL = -1

    def __init__(self, indexeddependencies=None):
        self.nodes = dict()
        if indexeddependencies:
            self.load(indexeddependencies)

    def add_node(self, label):
        if label not in self.nodes.keys():
            self.nodes[label] = DependencyGraphNode(label)

    def add_arc(self, relation, label1, label2):
        assert label1 in self.nodes.keys()
        assert label2 in self.nodes.keys()
        self.nodes[label1].childs[label2] = relation
        self.nodes[label2].parent = label1

    def tree(self, node=DUMMY_LABEL):
        if self.nodes[node].childs:
            childs = ' '.join([self.tree(t) for t
                               in self.nodes[node].childs.keys()])
            return '({} {})'.format(self.nodes[node].label, childs)
        else:
            return '({})'.format(self.nodes[node].label)

    def father(self, node):
        try:
            result = self.nodes[node].parent
            if result == self.DUMMY_LABEL:
                return None
            else:
                return result
        except KeyError:
            return None

    def grandfather(self, node):
        return self.father(self.father(node))

    def is_dummy(self, node):
        return node == self.DUMMY_LABEL

    def load(self, indexeddependencies):
        node = lambda dependency: int(dependency.split('-')[-1])-1
        indexeddependencies = ((relation, node(start), node(end))
                               for relation, start, end
                               in indexeddependencies)
        for relation, start, end in indexeddependencies:
            self.add_node(start)
            self.add_node(end)
            self.add_arc(relation, start, end)
        return self


class Document(object):
    '''It represents the root of a parsed document.'''

    def __init__(self, name, file_path='', dct=None):
        self.name = name
        self.text_offset = 0
        self.file_path = file_path
        self.doc_id = None
        self.dct = dct
        self.dct_text = None
        self.title = None
        self.sec_times = []
        self.text = ''
        self.sentences = []
        self.coref = None
        self.gold_annotations = []
        self.predicted_annotations = []

    def get_text(self, start, end):
        return self.text[start+self.text_offset:end+self.text_offset]

    def store_gold_annotations(self):
        """Enriching the Stanford Parser output with gold annotations."""
        for sentence in self.sentences:
            for word in sentence.words:
                word.gold_label, word.tag_attributes = format_annotation(
                    int(word.character_offset_begin),
                    int(word.character_offset_end),
                    self.gold_annotations)

    def __str__(self):
        return str(self.__dict__)

    def __repr__(self):
        return repr(self.__dict__)


class Sentence(object):

    def __init__(self, dependencies=None, indexed_dependencies=None,
                 parsetree='', text=''):
        from nltk import ParentedTree

        if dependencies:
            assert type(dependencies) == list, 'Wrong dependencies type'
        if indexed_dependencies:
            assert type(indexed_dependencies) == DependencyGraph, \
                'Wrong indexed dependencies type'
        if parsetree:
            assert type(parsetree) == ParentedTree, 'Wrong parsetree type'
        if text:
            assert type(text) == list, 'Wrong text type'

        self.dependencies = dependencies
        self.indexed_dependencies = indexed_dependencies
        self.parsetree = parsetree
        self.words = []

    def __str__(self):
        return str(self.__dict__)

    def __repr__(self):
        return repr(self.__dict__)


class Word(object):

    def __init__(self, word_form, char_offset_begin, char_offset_end,
                 lemma, named_entity_tag, part_of_speech, id_token):
        self.word_form = word_form
        self.character_offset_begin = char_offset_begin
        self.character_offset_end = char_offset_end
        self.lemma = lemma
        self.named_entity_tag = named_entity_tag
        self.part_of_speech = part_of_speech
        self.attributes = dict()
        self.id_token = id_token
        self.gold_label = 'O'
        self.predicted_label = 'O'
        self.tag_attributes = dict()

    def __str__(self):
        return str(self.__dict__)

    def __repr__(self):
        return repr(self.__dict__)

    def __eq__(self, other):
        return (isinstance(self, type(other)) and
                self.word_form == other.word_form and
                self.character_offset_begin == other.character_offset_begin and
                self.character_offset_end == other.character_offset_end)


class TemporalExpression(object):
    """It represents an annotated temporal expression in the TimeML standard.

    """
    def __init__(self, tid, words, ttype=None, value=None, mod=None):
        assert isinstance(tid, int)
        assert isinstance(words, list)
        self.tid = 't{}'.format(tid)
        self.words = words
        self.start = words[0].character_offset_begin
        self.end = words[-1].character_offset_end
        self.ttype = ttype
        self.value = value
        self.mod = mod
        self.text = ''

    def append_word(self, word):
        assert isinstance(word, Word)
        self.words.append(word)
        self.end = self.words[-1].character_offset_end

    def normalise(self, document, dct, domain='general'):
        """ It calls the normalisation component and provides the ISO-8601
        representation.

        """
        assert self.words
        assert domain in ('general', 'clinical')
        start = self.words[0].character_offset_begin + document.text_offset
        end = self.words[-1].character_offset_end + document.text_offset
        text = document.text[start:end]
        mod = ''
        try:
            if domain == 'general':
                timex_normalise = normalise_general
                _, ttype, value, _ = timex_normalise(text, dct)
            else:
                timex_normalise = normalise_clinical
                _, ttype, value, _, mod = timex_normalise(text, dct)
        except Exception:
            ttype, value = 'DATE', 'X'
        self.text = cgi.escape(self.text.replace('\n', ' '), True)
        self.ttype = ttype
        self.value = value
        self.mod = mod


class Event(object):
    """It represents an annotated event in the TimeML standard.

    """
    def __init__(self, eid, words, eclass=None, pos=None, tense=None,
                 aspect=None, polarity=None, modality=None, sec_time_rel=None):
        assert isinstance(eid, int)
        assert isinstance(words, list)
        self.eid = 'e{}'.format(eid)
        self.words = words
        self.eclass = eclass
        self.text = ''
        self.pos = pos
        self.tense = tense
        self.aspect = aspect
        self.polarity = polarity
        self.modality = modality
        self.sec_time_rel = sec_time_rel
        self.start = words[0].character_offset_begin
        self.end = words[-1].character_offset_end

    def append_word(self, word):
        assert isinstance(word, Word)
        self.words.append(word)
        self.end = self.words[-1].character_offset_end

    def normalise(self):
        assert all(['type' in w.tag_attributes.keys() for w in self.words])
        assert all(['modality' in w.tag_attributes.keys() for w in self.words])
        assert all(['polarity' in w.tag_attributes.keys() for w in self.words])
        self.eclass = [w.tag_attributes['type'] for w in self.words][0]
        self.modality = [w.tag_attributes['modality'] for w in self.words][0]
        self.polarity = [w.tag_attributes['polarity'] for w in self.words][0]
        self.sec_time_rel = ''
        self.text = cgi.escape(self.text.replace('\n', ' '), True)
        # [w.tag_attributes['sec_time_rel'] for w in self.words][0]


class EventInstance(object):
    """It represents an instance for an annotated event.

    """
    def __init__(self, eiid, event):
        assert isinstance(eiid, int)
        assert isinstance(event, Event)
        self.eiid = 'ei{}'.format(eiid)


class TemporalLink(object):
    """It represents an annotated temporal link in the TimeML standard.

    """
    def __init__(self, lid, element1, element2, reltype=None):
        assert isinstance(lid, int)
        assert type(element1) in (TemporalExpression, Event, EventInstance)
        assert type(element2) in (TemporalExpression, Event, EventInstance)
        self.lid = 'l{}'.format(lid)
        self.element1 = element1
        self.element2 = element2
        self.reltype = reltype

# class AnnotationStandard(object):
#     """ It represents an annotation standard.

#     """
#     def __init__(self, structure):
#         """ Structure = {TAG1: [ATTR1, ATTR2], TAG2: [ATTR1, ATTR2]} """
#         self.identification_tags = structure.keys()

