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

from document import Document, Sentence, Word
from ..normalisers.timex_general import normalise as normalise_general
from ..normalisers.timex_clinical import normalise as normalise_clinical


class Entity(object):
    """It represents any entity.

    """
    def __init__(self, identifier, meta=False):
        assert isinstance(meta, bool)
        self.idx = identifier
        self.meta = meta


class InTextEntity(Entity):
    """It represents any entity which is represented by a portion of text in a
       document.

    """
    def __init__(self, identifier, words, meta=False, tag_attributes={},
                 document=None):
        assert isinstance(identifier, str)
        assert document is None or isinstance(document, Document)
        super(InTextEntity, self).__init__(identifier, meta)
        self.words = words
        self.tag_attributes = tag_attributes
        if document:
            self.start = words[0].character_offset_begin + document.text_offset
            self.end = words[-1].character_offset_end + document.text_offset
            self.text = document.text[self.start:self.end]
        else:
            self.text = ''
            self.start = words[0].character_offset_begin
            self.end = words[-1].character_offset_end

    def append_word(self, word):
        assert isinstance(word, Word)
        self.words.append(word)
        self.end = self.words[-1].character_offset_end

    def identifier(self):
        return self.idx

    def id_sentence(self):
        return self.words[0].id_sentence

    def id_first_word(self):
        return self.words[0].id_token

    def id_last_word(self):
        return self.words[-1].id_token

    def dependencies_out(self):
        result = set()
        for word in self.words:
            for dependency in word.dependencies_out():
                result.add(dependency)
        return result

    def dependencies_in(self):
        result = set()
        for word in self.words:
            for dependency in word.dependencies_in():
                result.add(dependency)
        return result

    # TODO
    def dependency_head(self):
        '''Returns the headword among the its words.

        The headword is the highest in the dependency tree structure.

        '''
        if len(self.dependencies_in() + self.dependencies_out()):
            if len(self.words) == 1:
                return self.words[0]
            else:
                raise NotImplementedError
        else:
            return None

    # TODO
    def constituency_head(self):
        '''Returns a reference to the lowest common ancestor in the
        constituency tree.

        '''
        pass

    def __lt__(self, other):
        assert isinstance(self, type(other)), 'Wrong types!'
        if self.id_sentence() != other.id_sentence():
            return self.id_sentence() < other.id_sentence()
        else:
            return self.id_last_word() < other.id_first_word()

    def __gt__(self, other):
        assert isinstance(self, type(other)), 'Wrong types!'
        if self.id_sentence() != other.id_sentence():
            return self.id_sentence() > other.id_sentence()
        else:
            return self.id_last_word() > other.id_first_word()

    def __eq__(self, other):
        return (isinstance(self, type(other)) and self.text == other.text and
                self.start == other.start and self.end == other.end)

    def __repr__(self):
        return '{} {}'.format(self.tag, repr(self.words))


class TemporalExpression(InTextEntity):
    """It represents an annotated temporal expression in the TimeML standard.

    """
    def __init__(self, tid, words, ttype=None, value=None, mod=None,
                 meta=False, tag_attributes={}, document=None):
        assert isinstance(tid, str)
        assert isinstance(words, list)
        super(TemporalExpression, self).__init__(tid, words, meta,
                                                 tag_attributes, document)
        self.ttype = ttype
        self.value = value
        self.mod = mod
        self.tag = 'TIMEX'

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


class Event(InTextEntity):
    """It represents an annotated event in the TimeML standard.

    """
    def __init__(self, eid, words, eclass=None, pos=None, tense=None,
                 aspect=None, polarity=None, modality=None, sec_time_rel=None,
                 meta=False, tag_attributes={}, document=None):
        assert isinstance(eid, str)
        assert isinstance(words, list)
        super(Event, self).__init__(eid, words, meta,
                                    tag_attributes, document)
        self.eclass = eclass
        self.pos = pos
        self.tense = tense
        self.aspect = aspect
        self.polarity = polarity
        self.modality = modality
        self.sec_time_rel = sec_time_rel
        self.tag = 'EVENT'

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


class WrapperEntity(Entity):
    """It represents any entity which is associated to a InTextEntity.

    """
    def __init__(self, identifier, entity, meta=False):
        assert isinstance(identifier, str)
        assert isinstance(entity, InTextEntity)
        super(WrapperEntity, self).__init__(identifier, meta)
        self.entity = entity

    def identifier(self):
        return self.entity.idx

    def id_sentence(self):
        return self.entity.words[0].id_sentence

    def id_first_word(self):
        return self.entity.words[0].id_token

    def id_last_word(self):
        return self.entity.words[-1].id_token

    @property
    def start(self):
        return self.entity.start

    @property
    def end(self):
        return self.entity.end

    @property
    def text(self):
        return self.entity.text

    @property
    def words(self):
        return self.entity.words

    # TODO
    def comparator(self, other):
        return 'chi viene prima? w1 o w2?'

    def __eq__(self, other):
        return (isinstance(self, type(other)) and self.text == other.text and
                self.start == other.start and self.end == other.end)

    def __repr__(self):
        return '{} {}'.format(self.tag, repr(self.words))


class EventInstance(WrapperEntity):
    """It represents an instance for an annotated event.

    """
    def __init__(self, eiid, event):
        assert isinstance(eiid, str)
        assert isinstance(event, Event)
        super(EventInstance, self).__init__(eiid, event)
        self.tag = 'MAKEINSTANCE'


class TemporalLink(Entity):
    """It represents an annotated temporal link in the TimeML standard.

    """
    def __init__(self, lid, from_obj, to_obj, relation_type=None):
        assert isinstance(lid, str)
        assert type(to_obj) in (TemporalExpression, Event, EventInstance)
        assert type(from_obj) in (TemporalExpression, Event, EventInstance)
        super(TemporalLink, self).__init__(lid)
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
