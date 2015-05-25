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
import logging

from normalisers.timex_general import normalise as normalise_general
from normalisers.timex_clinical import normalise as normalise_clinical
from utilities import deephash


def format_annotation(start_token, end_token, annotations,
                      annotation_format='IO'):
    '''It returns the correct sequence class label for the given token.'''
    position = None
    tag_fired = ''
    attribs = {}
    annotations = {obj_id: obj for obj_id, obj in annotations.iteritems()
                   if type(obj) in (Event, TemporalExpression)}
    if annotations:
        for obj in annotations.itervalues():
            tag = obj.tag
            attribs = obj.tag_attributes
            start_offset = obj.start
            end_offset = obj.end
            tag_fired = tag
            if (start_offset, end_offset) == (start_token, end_token):
                position = 'W'
                break
            elif end_offset == end_token:
                position = 'E'
                break
            elif start_offset == start_token:
                position = 'B'
                break
            elif start_offset < start_token and end_offset > end_token:
                position = 'I'
                break
            else:
                position = 'O'
        if position not in list(annotation_format):
            position = 'I'
        return SequenceLabel(position, tag_fired), attribs
    else:
        return SequenceLabel('O'), attribs


class SequenceLabel(object):
    '''It represents a sequence label in the sequence labelling classifier.

    O, B-TIMEX and I-EVENT are examples of sequence labels.
    ^  ^           ^        position
         ^---^       ^---^  tag
    '''
    _SEPARATOR = '-'

    def __init__(self, position, tag=None):
        assert type(tag) == str or not tag
        assert type(position) == str
        try:
            self.position, self.tag = position.split(self._SEPARATOR)
            self.tag = self.tag.upper()
        except ValueError:
            self.position = position.upper()
            if tag:
                self.tag = tag.upper()
        finally:
            if self.position == 'O':
                self.tag = None
        assert self.position in 'WEBIO', 'Unknown position code: {}'.format(
            self.position)

    def is_timex(self):
        if self.tag:
            return self.tag.startswith('TIMEX')
        else:
            return False

    def is_event(self):
        if self.tag:
            return self.tag.startswith('EVENT')
        else:
            return False

    def is_out(self):
        return self.position == 'O'

    def set_out(self):
        '''Make the sequence label value equal to out ('O').'''
        self.tag = None
        self.position = 'O'

    def copy(self):
        return SequenceLabel(self.position, self.tag)

    def __str__(self):
        if self.tag:
            return self._SEPARATOR.join([self.position, self.tag])
        else:
            return self.position

    def __eq__(self, other):
        return (isinstance(self, type(other)) and
                self.position == other.position and self.tag == other.tag)

    def __ne__(self, other):
        return not self == other

    def __hash__(self):
        return deephash(self.__dict__)


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
        node = lambda dependency: int(dependency.split('-')[-1]) - 1
        indexeddependencies = ((relation, node(start), node(end))
                               for relation, start, end
                               in indexeddependencies)
        for relation, start, end in indexeddependencies:
            self.add_node(start)
            self.add_node(end)
            self.add_arc(relation, start, end)
        return self


class Document(object):
    '''It represents the root of a parsed document.

    '''
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
        self.gold_annotations = {}
        self.predicted_annotations = {}

    def get_text(self, start, end):
        return self.text[start + self.text_offset:end + self.text_offset]

    def store_gold_annotations(self):
        """Enriching the Stanford Parser output with gold annotations."""
        for sentence in self.sentences:
            for word in sentence.words:
                word.gold_label, word.tag_attributes = format_annotation(
                    int(word.character_offset_begin),
                    int(word.character_offset_end),
                    self.gold_annotations)

    def words(self, start=None, end=None):
        '''It returns the words satisfying within the boundaries.

        '''
        if start is None:
            start = 0
        if end is None:
            end = len(self.text)

        for sentence in self.sentences:
            for word in sentence.words:
                if (word.character_offset_begin >= start and
                        word.character_offset_end <= end):
                    yield word

    def __str__(self):
        return str(self.__dict__)

    def __repr__(self):
        return repr(self.__dict__)

    def __hash__(self):
        return deephash(self.__dict__)


class Sentence(object):

    def __init__(self, dependencies=None, indexed_dependencies=None,
                 parsetree='', text=''):
        from nltk import ParentedTree

        if dependencies:
            assert type(dependencies) == list, 'Wrong dependencies type'
        # if indexed_dependencies:
        #    assert type(indexed_dependencies) == DependencyGraph, \
        #        'Wrong indexed dependencies type'
        # if parsetree:
        #    assert type(parsetree) == ParentedTree, 'Wrong parsetree type'
        if text:
            assert type(text) == list, 'Wrong text type'

        self.dependencies = dependencies
        self._indexed_dependencies = indexed_dependencies
        self.indexed_dependencies = DependencyGraph(indexed_dependencies)
        self._parsetree = parsetree
        self.parsetree = ParentedTree(parsetree)
        self.words = []

    def __str__(self):
        return str(self.__dict__)

    def __repr__(self):
        return repr(self.__dict__)

    def __hash__(self):
        return deephash([self._indexed_dependencies, self._parsetree,
                         self.words])


class Word(object):

    def __init__(self, word_form, char_offset_begin, char_offset_end,
                 lemma, named_entity_tag, part_of_speech, id_token,
                 id_sentence):
        self.word_form = word_form
        self.character_offset_begin = char_offset_begin
        self.character_offset_end = char_offset_end
        self.lemma = lemma
        self.named_entity_tag = named_entity_tag
        self.part_of_speech = part_of_speech
        self.attributes = dict()
        self.id_token = id_token
        self.id_sentence = id_sentence
        self.gold_label = SequenceLabel('O')
        self.predicted_label = SequenceLabel('O')
        self.tag_attributes = dict()

    def __str__(self):
        return str(self.__dict__)

    def __repr__(self):
        return '[{} ({},{})]'.format(self.lemma, self.character_offset_begin,
                                     self.character_offset_end)

    def __eq__(self, other):
        return (isinstance(self, type(other)) and
                self.word_form == other.word_form and
                self.character_offset_begin == other.character_offset_begin and
                self.character_offset_end == other.character_offset_end)

    def __hash__(self):
        return deephash(self.__dict__)


class TemporalExpression(object):
    """It represents an annotated temporal expression in the TimeML standard.

    """
    def __init__(self, tid, words, ttype=None, value=None, mod=None,
                 meta=False, tag_attributes={}):
        assert isinstance(tid, str)
        assert isinstance(words, list)
        self.tid = tid
        self.words = words
        self.start = words[0].character_offset_begin
        self.end = words[-1].character_offset_end
        self.ttype = ttype
        self.value = value
        self.mod = mod
        self.text = ''
        self.meta = meta
        self.tag_attributes = tag_attributes
        self.tag = 'TIMEX'

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
        if not (dct.isdigit() and len(dct) == 8):
            dct = None
            logging.warning('Utterance time not found: using current date.')
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
        self.text = cgi.escape(text.replace('\n', ' '), True)
        self.ttype = ttype
        self.value = value
        self.mod = mod

    def identifier(self):
        return self.tid

    def id_sentence(self):
        return self.words[0].id_sentence

    def id_first_word(self):
        return self.words[0].id_token

    def id_last_word(self):
        return self.words[-1].id_token

    def __eq__(self, other):
        return (isinstance(self, type(other)) and self.text == other.text and
                self.start == other.start and self.end == other.end)

    def __repr__(self):
        return '{} {}'.format(self.tag, repr(self.words))


class Event(object):
    """It represents an annotated event in the TimeML standard.

    """
    def __init__(self, eid, words, eclass=None, pos=None, tense=None,
                 aspect=None, polarity=None, modality=None, sec_time_rel=None,
                 meta=False, tag_attributes={}):
        assert isinstance(eid, str)
        assert isinstance(words, list)
        self.eid = eid
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
        self.meta = meta
        self.tag_attributes = tag_attributes
        self.tag = 'EVENT'

    def append_word(self, word):
        assert isinstance(word, Word)
        self.words.append(word)
        self.end = self.words[-1].character_offset_end

    def normalise(self, document):
        # polarity and modality are valid in both schemas (i2b2 and ISO-TimeML)
        assert all(['polarity' in w.tag_attributes.keys() for w in self.words])
        assert all(['modality' in w.tag_attributes.keys() for w in self.words])
        self.pos = [w.tag_attributes.get('pos', '') for w in self.words][0]
        self.tense = [w.tag_attributes.get('tense', '') for w in self.words][0]
        self.aspect = [w.tag_attributes.get('aspect', '') for w
                       in self.words][0]
        self.polarity = [w.tag_attributes.get('polarity', '') for w
                         in self.words][0]
        self.modality = [w.tag_attributes.get('modality', '') for w
                         in self.words][0]
        self.sec_time_rel = ''
        start = self.words[0].character_offset_begin + document.text_offset
        end = self.words[-1].character_offset_end + document.text_offset
        text = document.text[start:end]
        self.text = cgi.escape(text.replace('\n', ' '), True)
        # [w.tag_attributes['sec_time_rel'] for w in self.words][0]

    def identifier(self):
        return self.eid

    def id_sentence(self):
        return self.words[0].id_sentence

    def id_first_word(self):
        return self.words[0].id_token

    def id_last_word(self):
        return self.words[-1].id_token

    def __eq__(self, other):
        return (isinstance(self, type(other)) and self.text == other.text and
                self.start == other.start and self.end == other.end)

    def __repr__(self):
        return '{} {}'.format(self.tag, repr(self.words))


class EventInstance(object):
    """It represents an instance for an annotated event.

    """
    def __init__(self, eiid, event):
        assert isinstance(eiid, str)
        assert isinstance(event, Event)
        self.eiid = eiid
        self.event = event
        self.tag = 'MAKEINSTANCE'

    def identifier(self):
        return self.eiid

    def id_sentence(self):
        return self.event.words[0].id_sentence

    def id_first_word(self):
        return self.event.words[0].id_token

    def id_last_word(self):
        return self.event.words[-1].id_token

    def __repr__(self):
        return '{} {}'.format(self.tag, repr(self.event))


class TemporalLink(object):
    """It represents an annotated temporal link in the TimeML standard.

    """
    def __init__(self, lid, from_obj, to_obj, relation_type=None):
        assert isinstance(lid, str)
        assert type(from_obj) in (TemporalExpression, Event, EventInstance)
        assert type(from_obj) in (TemporalExpression, Event, EventInstance)
        self.lid = lid
        self.from_obj = from_obj
        self.to_obj = to_obj
        self.relation_type = relation_type
        self.attributes = dict()
        self.tag = 'TLINK'

    def identifier(self):
        return self.lid

    def __eq__(self, other):
        """Two temporal links are the same if they link the same objects.

        """
        return (isinstance(self, type(other)) and
                (self.from_obj == other.from_obj and
                 self.to_obj == other.to_obj))

    def __repr__(self):
        return '{} {} -> {}'.format(self.tag, repr(self.from_obj),
                                    repr(self.to_obj))
