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

"""It contains the classes for the document of ManTIME.

"""

from ..utilities import deephash


def format_annotation(start, end, annotations, annotation_format='IO'):
    '''It returns the correct sequence class label for the given token.'''
    from data import Event, TemporalExpression
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
            if (start_offset, end_offset) == (start, end):
                position = 'W'
                break
            elif end_offset == end:
                position = 'E'
                break
            elif start_offset == start:
                position = 'B'
                break
            elif start_offset < start and end_offset > end:
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

    def __init__(self, label):
        self.label = label
        self.parents = dict()
        self.childs = dict()

    def __str__(self):
        parents = ', '.join(str(c) for c in self.parents.keys())
        childs = ', '.join(str(c) for c in self.childs.keys())
        return '(label:{}; parents: [{}]; childs:[{}])'.format(
            self.label, parents, childs)

    def __repr__(self):
        parents = ', '.join(str(c) for c in self.parents.keys())
        childs = ', '.join(str(c) for c in self.childs.keys())
        return '(label:{}; parents: {}; childs:[{}])'.format(
            self.label, parents, childs)


class DependencyGraph(object):

    DUMMY_LABEL = -1

    def __init__(self, dependencies=None):
        self.nodes = dict()
        if dependencies:
            self.load(dependencies)

    def add_node(self, id_word):
        if id_word not in self.nodes.keys():
            self.nodes[id_word] = DependencyGraphNode(id_word)

    def add_arc(self, relation, id_word1, id_word2):
        assert id_word1 in self.nodes.keys()
        assert id_word2 in self.nodes.keys()
        self.nodes[id_word1].childs[id_word2] = relation
        self.nodes[id_word2].parents[id_word1] = relation

    def parents(self, node):
        '''It returns a set of father-nodes.

        If all of them are the root then it returns None

        '''
        if node in self.nodes:
            results = set(self.nodes[node].parents.keys())
            if all((self.is_root(r) for r in results)):
                return None
            else:
                return results
        else:
            return None

    def grandparents(self, node):
        results = set()
        parents = self.parents(node)
        for parent in parents:
            results.update(self.parents(parent))
        return results

    def is_dummy(self, node):
        return node == self.DUMMY_LABEL

    def is_root(self, node):
        if node in self.nodes:
            return any(n == self.DUMMY_LABEL for n in self.nodes[node].parents)
        else:
            return False

    def load(self, dependencies):
        node = lambda e: int(e) - 1
        dependencies = ((dep_type, node(governor), node(dependent))
                        for dep_type, governor, dependent
                        in dependencies)
        for dep_type, governor, dependent in dependencies:
            self.add_node(governor)
            self.add_node(dependent)
            self.add_arc(dep_type, governor, dependent)
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
        self._coref = None
        self.coreferences = []
        self.gold_annotations = {}
        self.predicted_annotations = {}

    def complete_structure(self):
        '''Adorns the Document object with links to objects.

        It allows to query the structure in a bottom-up fashion. It adds:
         * Word
           - next                                           X
           - previous                                       X
           - constituency parent                            X
           - dependencies out (basic)                       X
           - dependencies in (basic)                        X
           - dependencies out (collapsed)                   X
           - dependencies in (collapsed)                    X
           - reference to (coreference mention)             X
           - reference to (coreference representative)      X
         * Sentence
           - next                                           X
           - previous                                       X
           - references to (co-reference mentions)          X
           - references to (co-reference representatives)   X
         * Coreference
           - representatives                                X
           - mentions                                       X
        '''
        # .next, .previous and .sentence for `Word` and `Sentence` classes.
        previous_sentence, previous_word = None, None
        for n_s, s in enumerate(self.sentences):
            s.previous = previous_sentence
            for n_w, w in enumerate(s.words):
                w.sentence = s
                w.previous = previous_word
                previous_word = w
                try:
                    # Next word in the same sentence
                    next_word = s.words[n_w + 1]
                except IndexError:
                    try:
                        # First word in the next sentence
                        next_word = self.sentences[n_s + 1].words[0]
                    except IndexError:
                        # This is the last word
                        next_word = None
                w.next = next_word
            previous_sentence = s
            try:
                # Next sentence in the document
                next_sentence = self.sentences[n_s + 1]
            except IndexError:
                # This is the last sentence
                next_sentence = None
            s.next = next_sentence

        # dependencies_out and dependencies_in for `Word`
        for sentence in self.sentences:
            # basic-dependencies
            for idx, node in sentence.basic_dependencies.nodes.iteritems():
                for parent_idx, rel in node.parents.iteritems():
                    parent = sentence.words[parent_idx]
                    sentence.words[idx].basic_dependencies_in[rel] = parent
                for child_idx, rel in node.childs.iteritems():
                    child = sentence.words[child_idx]
                    sentence.words[idx].basic_dependencies_out[rel] = child

            # collapsed-dependencies
            for idx, node in sentence.collapsed_dependencies.nodes.iteritems():
                for parent_idx, rel in node.parents.iteritems():
                    parent = sentence.words[parent_idx]
                    sentence.words[idx].collapsed_dependencies_in[rel] = parent
                for child_idx, rel in node.childs.iteritems():
                    child = sentence.words[child_idx]
                    sentence.words[idx].collapsed_dependencies_out[rel] = child

        # constituency anchoring for `Word`
        for sentence in self.sentences:
            for id_word in xrange(len(sentence.words)):
                word = sentence.words[id_word]
                word.constituency_parent = \
                    sentence.parsetree[
                        sentence.parsetree.leaf_treeposition(id_word)[:-1]]

        # coreference mentions, representatives for `Word`, `Sentence` and
        # `Document` classes.
        for coref_cluster in self._coref:
            r_text, r_sent, r_head, r_start, r_end = coref_cluster[-1][-1]
            if len(r_text) == 1 or r_text.isdigit():
                continue
            r_sent, r_head = int(r_sent), int(r_head)
            r_start, r_end = int(r_start), int(r_end) + 1
            r_words = self.sentences[r_sent].words[r_start:r_end]
            r_head = self.sentences[r_sent].words[r_head]
            representative = CoreferenceRepresentative(r_words, r_head)
            self.sentences[r_sent].coreference_representatives.append(
                representative)
            for [coref_mention, _] in coref_cluster:
                m_text, m_sent, m_head, m_start, m_end = coref_mention
                m_sent, m_head = int(m_sent), int(m_head)
                m_start, m_end = int(m_start), int(m_end) + 1
                m_words = self.sentences[m_sent].words[m_start:m_end]
                m_head = self.sentences[m_sent].words[m_head]
                mention = CoreferenceMention(m_words, m_head)
                mention.set_representative(representative)
                representative.mentions.append(mention)
                self.sentences[m_sent].coreference_mentions.append(mention)
            self.coreferences.append(representative)

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

        if start > end:
            start, end = end, start

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

    def __init__(self, id_sentence, basic_dependencies=None,
                 collapsed_dependencies=None, parsetree='', text=''):
        from nltk import ParentedTree

        assert type(id_sentence) == int, 'Wrong id type'
        assert basic_dependencies is None or \
            type(basic_dependencies) == list, 'Basic dependencies type'
        assert collapsed_dependencies is None or \
            type(collapsed_dependencies) == list, 'Collapsed dependencies type'
        if text:
            assert type(text) == list, 'Wrong text type'

        self.id_sentence = id_sentence
        self.basic_dependencies = DependencyGraph(basic_dependencies)
        self.collapsed_dependencies = DependencyGraph(collapsed_dependencies)
        self._parsetree = parsetree
        self.parsetree = ParentedTree(parsetree)
        self.words = []
        self.next = None
        self.previous = None
        self.coreference_mentions = []
        self.coreference_representatives = []
        self._connected_sentences = None

    def connected_sentences(self):
        '''It returns a set of all the id_sentences to which the current
        sentence is connected via coreference relations.

        '''
        id_connected_sentences = set()
        for m in self.coreference_mentions:
            id_connected_sentences.update(m.get_connected_sentences())
        for r in self.coreference_representatives:
            id_connected_sentences.update(r.get_connected_sentences())

        # a sentence is connected to itself
        id_connected_sentences.add(self.id_sentence)

        self._connected_sentences = id_connected_sentences
        return id_connected_sentences

    def connected_to(self, id_sentence):
        '''It returns whether the sentence is connected to a particular one.

        '''
        connections = self._connected_sentences
        if connections is None:
            connections = self.connected_sentences()
        return id_sentence in connections

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
        self.sentence = None
        self.gold_label = SequenceLabel('O')
        self.predicted_label = SequenceLabel('O')
        self.tag_attributes = dict()
        self.next = None
        self.previous = None
        self.basic_dependencies_in = dict()
        self.basic_dependencies_out = dict()
        self.collapsed_dependencies_in = dict()
        self.collapsed_dependencies_out = dict()
        self.constituency_left_sibling = None
        self.constituency_right_sibling = None
        self.constituency_parent = None
        self.coreference_mention = None
        self.is_coreference_head = False
        self.is_coreference_representative = False

    def dependencies_out(self, type, target_word=None):
        '''Returns couples (`relation_type`, `target_word`) of outgoing
        dependency relations from the current word.

        If a `target_word` is specified it returns the existing relations to
        that particular word only.

        '''
        assert type in ('basic', 'collapsed')

        if type == 'basic':
            deps = self.basic_dependencies_out
        else:
            deps = self.collapsed_dependencies_out
        if target_word is not None:
            return [(r, w) for r, w in deps.iteritems() if w == target_word]
        else:
            return [(r, w) for r, w in deps.iteritems()]

    def dependencies_in(self, type, source_word=None):
        '''Returns couples (`relation_type`, `source_word`) of incoming
        dependency relations to the current word.

        If a `source_word` is specified it returns the existing relations from
        that particular word only.

        '''
        assert type in ('basic', 'collapsed')

        if type == 'basic':
            deps = self.basic_dependencies_in
        else:
            deps = self.collapsed_dependencies_in
        if source_word is not None:
            return [(r, w) for r, w in deps.iteritems() if w == source_word]
        else:
            return [(r, w) for r, w in deps.iteritems()]

    def __str__(self):
        return str(self.__dict__)

    def __repr__(self):
        return '[{} ({},{})]'.format(self.lemma, self.character_offset_begin,
                                     self.character_offset_end)

    def __hash__(self):
        return deephash(self.__dict__)

    def __lt__(self, other):
        assert isinstance(self, type(other)), 'Wrong types!'
        if self.id_sentence != other.id_sentence:
            return self.id_sentence < other.id_sentence
        else:
            return self.id_word < other.id_word

    def __gt__(self, other):
        assert isinstance(self, type(other)), 'Wrong types!'
        if self.id_sentence != other.id_sentence:
            return self.id_sentence > other.id_sentence
        else:
            return self.id_word > other.id_word

    def __eq__(self, other):
        return ((isinstance(self, type(other)) and
                (self.id_sentence, self.id_token) ==
                (other.id_sentence, other.id_token)))


class CoreferenceMention(object):

    def __init__(self, words, head):
        assert all(isinstance(w, Word) for w in words), 'Wrong words'
        assert isinstance(head, Word) and head in words, 'Wrong head'
        self.words = words
        self.head = head
        head.is_coreference_head = True
        self.representative = None

    def set_representative(self, representative):
        assert isinstance(representative, CoreferenceRepresentative)
        self.representative = representative
        for w in self.words:
            w.coreference_representative = self.representative
            w.coreference_mention = self

    def get_connected_sentences(self):
        return {self.representative.id_sentence}

    @property
    def id_sentence(self):
        return self.words[0].id_sentence


class CoreferenceRepresentative(CoreferenceMention):

    def __init__(self, words, head):
        super(CoreferenceRepresentative, self).__init__(words, head)
        self.mentions = []
        self.representative = self
        for w in self.words:
            w.is_coreference_representative = True

    def get_connected_sentences(self):
        return {m.id_sentence for m in self.mentions}
