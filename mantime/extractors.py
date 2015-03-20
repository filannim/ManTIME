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
import pickle
import calendar
import types

import nltk
from num2words import num2words

from utilities import Memoize
from utilities import matching_gazetteer
from model import Word
from settings import LANGUAGE

# PORTER_STEMMER = Memoize(nltk.PorterStemmer().stem)
# LANCASTER_STEMMER = Memoize(nltk.LancasterStemmer().stem)
# WORDNET_LEMMATIZER = Memoize(nltk.WordNetLemmatizer().lemmatize)
STOPWORDS = nltk.corpus.stopwords.words(LANGUAGE)
GAZETTEER_FOLDER = 'data/gazetteer/'
COMMON_WORDS = pickle.load(open(GAZETTEER_FOLDER + 'common_words.pickle'))
POSITIVE_WORDS = pickle.load(open(GAZETTEER_FOLDER + 'positive_words.pickle'))
NEGATIVE_WORDS = pickle.load(open(GAZETTEER_FOLDER + 'negative_words.pickle'))
# MALE_NAMES = pickle.load(open(GAZETTEER_FOLDER + 'male.pickle'))
# FEMALE_NAMES = pickle.load(open(GAZETTEER_FOLDER + 'female.pickle'))
COUNTRIES = pickle.load(open(GAZETTEER_FOLDER + 'countries.pickle'))
ISO_COUNTRIES = pickle.load(open(GAZETTEER_FOLDER + 'isocountries.pickle'))
# US_CITIES = pickle.load(open(GAZETTEER_FOLDER + 'uscities.pickle'))
# NATIONALITIES = pickle.load(open(GAZETTEER_FOLDER + 'nationalities.pickle'))
FESTIVITIES = pickle.load(open(GAZETTEER_FOLDER + 'festivities.pickle'))
# PHONEME_DICTIONARY = nltk.corpus.cmudict.dict()


class WordBasedExtractors(object):

    # @staticmethod
    # def token(word):
    #     return WordBasedResult(word.word_form)

    @staticmethod
    def token_normalised(word):
        return WordBasedResult(re.sub(r'\d', 'D', word.lemma.strip()))

    @staticmethod
    def lexical_lemma(word):
        return WordBasedResult(word.lemma)

    @staticmethod
    def lexical_pos(word):
        return WordBasedResult(word.part_of_speech)

    @staticmethod
    def lexical_tense(word):
        postag = word.part_of_speech
        if postag in ('VB', 'VD', 'VH', 'VV'):
            return WordBasedResult('BASE')
        elif postag in ('VBN', 'VDN', 'VHN', 'VVN'):
            return WordBasedResult('PASTPARTICIPLE')
        elif postag in ('VBD', 'VDD', 'VHD', 'VVD'):
            return WordBasedResult('PAST')
        elif postag in ('VBG', 'VDG', 'VHG', 'VVG'):
            return WordBasedResult('GERUND')
        elif postag in ('VBZ', 'VBP', 'VDZ', 'VDP', 'VHZ', 'VHP'):
            return WordBasedResult('PRESENT')
        else:
            return WordBasedResult('NONE')

    @staticmethod
    def lexical_polarity(word):
        if word.word_form.lower() in POSITIVE_WORDS:
            return WordBasedResult('pos')
        elif word.word_form.lower() in NEGATIVE_WORDS:
            return WordBasedResult('neg')
        else:
            return WordBasedResult('neu')

    @staticmethod
    def lexical_named_entity_tag(word):
        return WordBasedResult(word.named_entity_tag)

    # @staticmethod
    # def morphological_wordnet_lemma(word):
    #     return WordBasedResult(WORDNET_LEMMATIZER(word.word_form))

    # @staticmethod
    # def morphological_porter_stem(word):
    #     return WordBasedResult(PORTER_STEMMER(word.word_form))

    # @staticmethod
    # def morphological_lancaster_stem(word):
    #     return WordBasedResult(LANCASTER_STEMMER(word.word_form))

    @staticmethod
    def morphological_unusual_word(word):
        return WordBasedResult(not word.word_form.lower() in COMMON_WORDS)

    @staticmethod
    def morphological_is_stopword(word):
        return WordBasedResult(word.word_form in STOPWORDS)

    @staticmethod
    def morphological_pattern(word):
        pattern = ''
        for char in word.word_form:
            if char.isupper():
                if pattern[-1:] != 'X':
                    pattern += 'X'
            elif char.islower():
                if pattern[-1:] != 'x':
                    pattern += 'x'
            elif char.isdigit():
                if pattern[-1:] != 'd':
                    pattern += 'd'
            elif char.isspace():
                if pattern[-1:] != ' ':
                    pattern += ' '
            else:
                if pattern[-1:] != char:
                    pattern += char
        return WordBasedResult(pattern)

    @staticmethod
    def morphological_extended_pattern(word):
        pattern = ''
        for char in word.word_form:
            if char.isupper():
                pattern += 'X'
            elif char.islower():
                pattern += 'x'
            elif char.isdigit():
                pattern += 'd'
            elif char.isspace():
                pattern += ' '
            else:
                pattern += char
        return WordBasedResult(pattern)

    # @staticmethod
    # def morphological_vocal_pattern(word):
    #     pattern = ''
    #     for char in word.word_form:
    #         if char in ['a', 'e', 'i', 'o', 'u']:
    #             if pattern[-1:] != 'v':
    #                 pattern += 'v'
    #         elif char.isdigit():
    #             if pattern[-1:] != 'D':
    #                 pattern += 'D'
    #         elif char.isspace():
    #             if pattern[-1:] != ' ':
    #                 pattern += ' '
    #         elif not char.isalnum():
    #             if pattern[-1:] != 'p':
    #                 pattern += 'p'
    #         else:
    #             if pattern[-1:] != 'c':
    #                 pattern += 'c'
    #     return WordBasedResult(pattern)

    @staticmethod
    def morphological_has_digit(word):
        return WordBasedResult(any(char.isdigit() for char in word.word_form))

    @staticmethod
    def morphological_has_symbol(word):
        issymbol = lambda x: not (x.isdigit() or x.isalpha())
        return WordBasedResult(any(issymbol(char) for char in word.word_form))

    @staticmethod
    def morphological_prefix(word):
        return WordBasedResult(word.word_form[:3] or
                               word.word_form[:2] or
                               word.word_form[:1])

    @staticmethod
    def morphological_suffix(word):
        return WordBasedResult(word.word_form[-3:] or
                               word.word_form[-2:] or
                               word.word_form[-1:])

    @staticmethod
    def morphological_first_upper(word):
        return WordBasedResult(word.word_form[0].isupper())

    @staticmethod
    def morphological_is_alpha(word):
        return WordBasedResult(word.word_form.isalpha())

    @staticmethod
    def morphological_is_lower(word):
        return WordBasedResult(word.word_form.islower())

    @staticmethod
    def morphological_is_digit(word):
        return WordBasedResult(word.word_form.isdigit())

    @staticmethod
    def morphological_is_alphabetic(word):
        return WordBasedResult(word.word_form.isalpha())

    @staticmethod
    def morphological_is_alphanumeric(word):
        return WordBasedResult(word.word_form.isalnum())

    @staticmethod
    def morphological_is_title(word):
        return WordBasedResult(word.word_form.istitle())

    @staticmethod
    def morphological_is_upper(word):
        return WordBasedResult(word.word_form.isupper())

    @staticmethod
    def morphological_is_numeric(word):
        return WordBasedResult(unicode(word.word_form).isnumeric())

    @staticmethod
    def morphological_is_decimal(word):
        return WordBasedResult(unicode(word.word_form).isdecimal())

    @staticmethod
    def morphological_ends_with_s(word):
        return WordBasedResult(word.word_form[-1] == 's')

    @staticmethod
    def morphological_token_with_no_letters(word):
        return WordBasedResult(''.join([c for c in word.word_form
                                        if not c.isalpha()]))

    @staticmethod
    def morphological_token_with_no_letters_and_numbers(word):
        return WordBasedResult(''.join([c for c in word.word_form
                                        if not (c.isalpha() or c.isdigit())]))

    @staticmethod
    def morphological_is_all_caps_and_dots(word):
        iscapsanddots = lambda x: x.isupper() or x == '.'
        return WordBasedResult(all(map(iscapsanddots, word.word_form)))

    @staticmethod
    def morphological_is_all_digits_and_dots(word):
        isdigitsanddots = lambda x: x.isdigit() or x == '.'
        return WordBasedResult(all(map(isdigitsanddots, word.word_form)))

    @staticmethod
    def temporal_number(word):
        pattern = r'^[0-9]+ ?(?:st|nd|rd|th)$'
        return WordBasedResult(any(re.findall(pattern,
                                              word.word_form.lower())))

    @staticmethod
    def temporal_time(word):
        pattern = r'^([0-9]{1,2})[:\.\-]([0-9]{1,2}) ?(a\.?m\.?|p\.?m\.?)?$'
        return WordBasedResult(any(re.findall(pattern,
                                              word.word_form.lower())))

    @staticmethod
    def temporal_digit(word):
        return WordBasedResult(any(re.findall('^[0-9]+$',
                                              word.word_form.lower())))

    @staticmethod
    def temporal_ordinal(word):
        return WordBasedResult(any(re.findall('^(st|nd|rd|th)$',
                                              word.word_form.lower())))

    @staticmethod
    def temporal_year(word):
        return WordBasedResult(any(re.findall('^[12][0-9]{3}|\'[0-9]{2,3}$',
                                              word.word_form.lower())))

    @staticmethod
    def temporal_literal_number(word):
        lit_numbers = set([num2words(num) for num in xrange(0, 1001)])
        lit_numbers.update([num.replace('-', '') for num in lit_numbers])
        pattern = r'^({pattern})$'.format(pattern='|'.join(lit_numbers))
        return WordBasedResult(any(re.findall(pattern,
                                   word.word_form.lower())))

    @staticmethod
    def temporal_cardinal_number(word):
        card_numbers = set([num2words(num, True) for num in xrange(0, 1001)])
        card_numbers.update([num.replace('-', '') for num in card_numbers])
        pattern = r'^({pattern})$'.format(pattern='|'.join(card_numbers))
        return WordBasedResult(any(re.findall(pattern,
                                              word.word_form.lower())))

    @staticmethod
    def temporal_month(word):
        regex = [calendar.month_name[num] for num in xrange(1, 13)]
        regex.extend([calendar.month_name[num][:3] for num in xrange(1, 13)])
        pattern = r'^({pattern})\.?$'.format(pattern='|'.join(regex))
        return WordBasedResult(any(re.findall(pattern,
                                              word.word_form.lower())))

    @staticmethod
    def temporal_period(word):
        periods = ['centur[y|ies]', 'decades?', 'years?', 'months?',
                   r'week\-?ends?', 'weeks?', 'days?', 'hours?', 'minutes?',
                   'seconds?', 'fortnights?']
        pattern = r'^({pattern})$'.format(pattern=periods)
        return WordBasedResult(any(re.findall(pattern,
                                              word.word_form.lower())))

    @staticmethod
    def temporal_weekday(word):
        return WordBasedResult(any(re.findall(r'^(monday|tuesday|wednesday|thursday|friday|saturday|sunday|wed|tues|tue|thurs|thur|thu|sun|sat|mon|fri)$', word.word_form.lower())))

    @staticmethod
    def temporal_pod(word):
        return WordBasedResult(any(re.findall(r'^(morning|afternoon|evening|night|noon|midnight|midday|sunrise|dusk|sunset|dawn|overnight|midday|noonday|noontide|nightfall|midafternoon|daybreak|gloaming|a\.?m\.?|p\.?m\.?)s?$', word.word_form.lower())))

    @staticmethod
    def temporal_season(word):
        return WordBasedResult(any(re.findall(r'^(winter|autumn|spring|summer)s?', word.word_form.lower())))

    @staticmethod
    def temporal_past_ref(word):
        return WordBasedResult(any(re.findall(r'^(yesterday|ago|earlier|early|last|recent|nearly|past|previous|before)$', word.word_form.lower())))

    @staticmethod
    def temporal_present_ref(word):
        return WordBasedResult(any(re.findall(r'^(tonight|current|present|now|nowadays|today|currently)$', word.word_form.lower())))

    @staticmethod
    def temporal_future_ref(word):
        future_refs = ['next', 'forthcoming', 'coming', 'tomorrow', 'after',
                       'later', 'ahead']
        pattern = r'^({pattern})$'.format(pattern='|'.join(future_refs))
        return WordBasedResult(any(re.findall(pattern, word.word_form.lower())))

    @staticmethod
    def temporal_signal(word):
        signals = ['after', 'about', 'into', 'between', 'again', 'within',
                   'every', 'for', 'on', 'the', 'since', 'in', 'of', 'until',
                   'at', 'over', 'from', 'by', 'through', 'to', 'and', 'a']
        pattern = r'^({pattern})$'.format(pattern='|'.join(signals))
        return WordBasedResult(any(re.findall(pattern, word.word_form.lower())))

    @staticmethod
    def temporal_fuzzy_quantifier(word):
        quantifiers = ['approximately', 'approximate', 'approx', 'about',
                       'few', 'some', 'bunch', 'several', 'around']
        pattern = r'^({pattern})$'.format(pattern='|'.join(quantifiers))
        return WordBasedResult(any(re.findall(pattern, word.word_form.lower())))

    @staticmethod
    def temporal_modifier(word):
        return WordBasedResult(any(re.findall(r'^(beginning|less|more|much|long|short|end|start|half)$', word.word_form.lower())))

    @staticmethod
    def temporal_temporal_adverbs(word):
        return WordBasedResult(any(re.findall(r'^(daily|earlier)$', word.word_form.lower())))

    @staticmethod
    def temporal_temporal_adjectives(word):
        return WordBasedResult(any(re.findall(r'^(early|late|soon|fiscal|financial|tax)$', word.word_form.lower())))

    @staticmethod
    def temporal_temporal_conjunctives(word):
        return WordBasedResult(any(re.findall(r'^(when|while|meanwhile|during|on|and|or|until)$', word.word_form.lower())))

    @staticmethod
    def temporal_temporal_prepositions(word):
        return WordBasedResult(any(re.findall(r'^(pre|during|for|over|along|this|that|these|those|than|mid)$', word.word_form.lower())))

    @staticmethod
    def temporal_temporal_coreference(word):
        return WordBasedResult(any(re.findall(r'^(dawn|time|period|course|era|age|season|quarter|semester|millenia|millenium|eve|festival|festivity)s?$', word.word_form.lower())))

    @staticmethod
    def temporal_festivity(word):
        return WordBasedResult(any(re.findall(r'^(christmas|easter|epifany|martin|luther|thanksgiving|halloween|saints|armistice|nativity|advent|solstice|boxing|stephen|sylvester)$', word.word_form.lower())))

    @staticmethod
    def temporal_compound(word):
        return WordBasedResult(any(re.findall(r'^[0-9]+\-(century|decade|year|month|week\-end|week|day|hour|minute|second|fortnight|)$', word.word_form.lower())))

    # @staticmethod
    # def phonetic_form(word):
    #     phonemes = PHONEME_DICTIONARY.get(word.word_form.lower(), [''])[0]
    #     attributes = (('phonetic_form', WordBasedResult('-'.join(phonemes))),
    #                   ('phonetic_length', WordBasedResult(len(phonemes))),
    #                   ('phonetic_first', WordBasedResult(phonemes[0] if phonemes else None)),
    #                   ('phonetic_last', WordBasedResult(phonemes[-1] if phonemes else None)))
    #     return WordBasedResults(attributes)


class SentenceBasedExtractors(object):

    # @staticmethod
    # def gazetteer_malename(sentence):
    #     return matching_gazetteer(MALE_NAMES, sentence)

    # @staticmethod
    # def gazetteer_femalename(sentence):
    #     return matching_gazetteer(FEMALE_NAMES, sentence)

    @staticmethod
    def gazetteer_country(sentence):
        return matching_gazetteer(COUNTRIES, sentence)

    @staticmethod
    def gazetteer_isocountry(sentence):
        return matching_gazetteer(ISO_COUNTRIES, sentence)

    # @staticmethod
    # def gazetteer_uscity(sentence):
    #     return matching_gazetteer(US_CITIES, sentence)

    # @staticmethod
    # def gazetteer_nationality(sentence):
    #     return matching_gazetteer(NATIONALITIES, sentence)

    @staticmethod
    def gazetteer_festivity(sentence):
        return matching_gazetteer(FESTIVITIES, sentence)

    @staticmethod
    def parse_2_levels_up_node(sentence):
        result = []
        for tree_index in sentence.parsetree.treepositions(order='leaves'):
            try:
                node_label = sentence.parsetree[tree_index[:-2]].node()
                result.append(WordBasedResult(node_label))
            except TypeError:
                result.append(WordBasedResult('_^_'))
                continue
        return SentenceBasedResult(tuple(result))

    @staticmethod
    def parse_3_levels_up_node(sentence):
        result = []
        for tree_index in sentence.parsetree.treepositions(order='leaves'):
            node = tree_index[:-3]
            try:
                node_label = sentence.parsetree[node].node()
                result.append(WordBasedResult(node_label))
            except TypeError:
                result.append(WordBasedResult('_^_'))
                continue
        return SentenceBasedResult(tuple(result))

    @staticmethod
    def parse_2_levels_up_childs(sentence):
        result = []
        for tree_index in sentence.parsetree.treepositions(order='leaves'):
            node = tree_index[:-2]
            try:
                node_labels = [i.node for i in sentence.parsetree[node]]
                result.append(WordBasedResult('_'.join(node_labels)))
            except TypeError:
                result.append(WordBasedResult('_^_'))
                continue
        return SentenceBasedResult(tuple(result))

    @staticmethod
    def parse_3_levels_up_childs(sentence):
        result = []
        for tree_index in sentence.parsetree.treepositions(order='leaves'):
            node = tree_index[:-3]
            try:
                node_label = [i.node for i in sentence.parsetree[node]]
                result.append(WordBasedResult('_'.join(node_label)))
            except TypeError:
                result.append(WordBasedResult('_^_'))
                continue
        return SentenceBasedResult(tuple(result))

    @staticmethod
    def parse_3_levels_up_nodes(sentence):
        result = []
        for tree_index in sentence.parsetree.treepositions(order='leaves'):
            parents = []
            for level in xrange(-3, 0):
                node = tree_index[:-level]
                try:
                    parents.append(sentence.parsetree[node].node)
                except (TypeError, AttributeError):
                    continue
            result.append(WordBasedResult('_'.join(parents)))
        return SentenceBasedResult(tuple(result))

    @staticmethod
    def parse_2_levels_up_nodes(sentence):
        result = []
        for tree_index in sentence.parsetree.treepositions(order='leaves'):
            parents = []
            for level in xrange(-2, 0):
                node = tree_index[:-level]
                try:
                    parents.append(sentence.parsetree[node].node)
                except TypeError:
                    continue
            result.append(WordBasedResult('_'.join(parents)))
        return SentenceBasedResult(tuple(result))

    @staticmethod
    def parse_start_or_end_child_in_s_clause(sentence):
        '''Suggested by Marilena Di Bari.
        Typically temporal expressions are at the very end or beginning of a
        well-formed English sentence.
        '''
        parsetree = sentence.parsetree
        result = []
        for idx in parsetree.treepositions(order='leaves'):
            tree = parsetree[idx[:-1]]
            steps_up = 1
            # there are some leaves which are not necessarily child of S
            # all the leaves are always child of ROOT)
            # Don't believe me? Try to parse this sentence:
            # -  "And Rosneft benefits from BP's expertise in exploring in
            #     difficult and potentially hazardous conditions."
            while not (tree.node.startswith('S') or tree.node == 'ROOT'):
                tree = tree.parent()
                steps_up += 1
            position_under_s = idx[(len(idx) - steps_up)]
            leaf_result = position_under_s in(0, len(tree)-1)
            result.append(WordBasedResult(leaf_result))
        return SentenceBasedResult(tuple(result))

    @staticmethod
    def parse_distance_from_s_node(sentence):
        '''How far the current node (its POS) is from an S-parent.
        '''
        parsetree = sentence.parsetree
        result = []
        for idx in parsetree.treepositions(order='leaves'):
            tree = parsetree[idx[:-1]]
            steps_up = 1
            # there are some leaves which are not necessarily child of S
            # all the leaves are always child of ROOT)
            # Don't believe me? Try to parse this sentence:
            # -  "And Rosneft benefits from BP's expertise in exploring in
            #     difficult and potentially hazardous conditions."
            while not (tree.node.startswith('S') or tree.node == 'ROOT'):
                tree = tree.parent()
                steps_up += 1

            result.append(WordBasedResult(steps_up))
        return SentenceBasedResult(tuple(result))

    @staticmethod
    def dependency_outgoing_relations(sentence):
        '''For each word I represent a vector of all outgoing relations, plus
           the information related to the number of outgoing dependency
           relations.

           for each word =
            dr1   dr2   dr2   dr2   dr2   dr2   ...   dr2   #outgoing_deps
           [ F  ,  F  , NNS ,  F  ,  F  ,  F  , ... , VBZ ,       2         ]

           Dependencies relations are taken from:
           http://nlp.stanford.edu/software/dependencies_manual.pdf

           Since I don't trust 100% the documentat linked above, I print out
           a warning message in case a dependency relation is not in the list
           belove (*dep_labels*), so that I can update this list in the future.
           Anyway, the list should be quite complete as it is.
        '''
        dependencies = sentence.indexed_dependencies
        dep_labels = ['root', 'dep', 'aux', 'auxpass', 'cop', 'arg',
                      'agent', 'comp', 'acomp', 'ccomp', 'xcomp', 'obj',
                      'dobj', 'iobj', 'pobj', 'subj', 'nsubj', 'nsubjpass',
                      'csubj', 'csubjpass', 'cc', 'conj', 'expl', 'mod',
                      'amod', 'appos', 'advcl', 'det', 'predet', 'preconj',
                      'vmod', 'mwe', 'mark', 'advmod', 'neg', 'rcmod',
                      'quantmod', 'nn', 'npadvmod', 'tmod', 'num', 'number',
                      'prep', 'prepc', 'poss', 'possessive', 'prt',
                      'parataxis', 'punct', 'ref', 'sdep', 'xsubj',
                      'discourse', 'n_of_outgoing_relations']

        result = []
        f_suffix = lambda function_name: 'dependency_outgoing_' + function_name
        for word in sentence.words:
            word_vector = {f_suffix(dep): WordBasedResult(False) for dep
                           in dep_labels}
            word_dep_node = dependencies.nodes.get(word.id_token, None)
            if word_dep_node:
                for out_ref, relation in word_dep_node.childs.iteritems():
                    if relation in dep_labels:
                        relation = relation.split('-')[0]
                        try:
                            word_vector[f_suffix(relation)] = WordBasedResult(
                                sentence.words[out_ref].part_of_speech)
                        except KeyError:
                            print 'WARNING: {} dep. relation missed.'.format(
                                relation)
                        word_vector[f_suffix('n_of_outgoing_relations')] =\
                            WordBasedResult(len(word_dep_node.childs))
            result.append(tuple(word_vector.items()))
        return SentenceBasedResults(tuple(result))

    @staticmethod
    def dependency_incoming_relations(sentence):
        '''For each word I represent a vector derived from the incoming
           dependency relations. I represent the following information:
           - father dependency relation (fdr);
           - grandfather dependecy relation (gdr);
           - part-of-speech tag for the father word (pfw);
           - part-of-speech tag for the grandfather word (pgw);
           - dominant verb (dmv);

           for each word =
            fdr   gdr   pfw   pgw   dmv
           [aux , cop , NNS,  F  ,  F  ,  F  , ... , VBZ ,       2         ]
        '''

        deps = sentence.indexed_dependencies
        attributes = ['father_dep_rel',
                      'gfather_dep_rel',
                      'postag_father',
                      'postag_gfather',
                      'dominant_verb']
        f_suffix = lambda function_name: 'dependency_incoming_' + function_name
        result = []
        for _ in sentence.words:
            result.append({f_suffix(dep): WordBasedResult(False) for dep
                           in attributes})
        for ref in deps.nodes.iterkeys():
            if ref == deps.DUMMY_LABEL:
                continue
            elif deps.grandfather(ref):
                fref = deps.father(ref)
                gref = deps.father(fref)
                result[ref][f_suffix('father_dep_rel')] = WordBasedResult(
                    deps.nodes[fref].childs[ref])
                result[ref][f_suffix('postag_father')] =\
                    WordBasedResult(sentence.words[fref].part_of_speech)
                result[ref][f_suffix('gfather_dep_rel')] = WordBasedResult(
                    deps.nodes[gref].childs[fref])
                result[ref][f_suffix('postag_gfather')] =\
                    WordBasedResult(sentence.words[gref].part_of_speech)
            elif deps.father(ref):
                fref = deps.father(ref)
                result[ref][f_suffix('father_dep_rel')] = WordBasedResult(
                    deps.nodes[fref].childs[ref])
                result[ref][f_suffix('postag_father')] =\
                    WordBasedResult(sentence.words[fref].part_of_speech)
                result[ref][f_suffix('gfather_dep_rel')] =\
                    WordBasedResult(False)
                result[ref][f_suffix('postag_gfather')] =\
                    WordBasedResult(False)

            # Dominant verb calculation
            current_ref = ref
            current_pos = sentence.words[ref].part_of_speech
            if current_pos.startswith('V'):
                result[ref][f_suffix('dominant_verb')] =\
                    WordBasedResult(current_pos)
            else:
                while not (current_pos.startswith('V')
                           or deps.is_dummy(current_ref)):
                    current_ref = deps.father(current_ref)
                    if current_ref is None:
                        break
                    current_pos = sentence.words[current_ref].part_of_speech
                result[ref][f_suffix('dominant_verb')] =\
                    WordBasedResult(current_pos)
        for num, word_result in enumerate(result):
            result[num] = tuple(word_result.items())
        return SentenceBasedResults(tuple(result))


class DocumentBasedExtractors(object):

    pass


class WordBasedResult(object):

    def __init__(self, value):
        assert type(value) in (types.NoneType, str, unicode, bool, int, float)
        if isinstance(value, types.NoneType):
            self.value = '_'
        elif type(value) in (str, bool):
            self.value = '"{}"'.format(str(value).replace(' ', '_'))
        elif type(value) == unicode:
            self.value = u'"{}"'.format(unicode(value.replace(u'\xa0', u'_')))
        else:
            self.value = '{}'.format(str(value).replace(' ', '_'))
        self.value = self.value.replace(' ', '_')

    def apply(self, word, name):
        assert type(word) == Word, 'Wrong word type'
        word.attributes[name] = self.value


class WordBasedResults(object):

    def __init__(self, values):
        assert type(values) == tuple
        self.values = values


class SentenceBasedResult(object):

    def __init__(self, values):
        assert type(values) == tuple, 'Wrong type for values'
        self.values = values


class SentenceBasedResults(object):

    def __init__(self, values):
        assert type(values) == tuple, 'Wrong type for values'
        self.values = values
