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

'''This modules contains all the attribute extractors functions.'''

from __future__ import division

import re
import cPickle
import calendar
from datetime import date
import functools

import nltk

from utilities import search_subsequence
from model.data import Event, TemporalExpression, EventInstance
from model_extractors import WordBasedResult
from model_extractors import WordBasedResults
from model_extractors import SentenceBasedResult
from model_extractors import SentenceBasedResults
from settings import LANGUAGE
from settings import GAZETTEER_FOLDER


open_gazetteer = lambda file_name: open(GAZETTEER_FOLDER + file_name)

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


def matching_gazetteer(gazetteer, sentence):
    ''' It searches for gazetteer elements into the sentence and returns a
    SentenceBasedResult object which is composed of WordBasedResults
    'I's or 'O's.

    Example:
    sentence = ['I', 'live', 'in', 'New', 'York', '.']
    gazetteer = { ..., ('New', 'York'), ...}

    returns SentenceBasedResult(W('O'), W('O'), W('O'), W('I'), W('I'), W('O'))
    '''
    word_forms = [token.word_form for token in sentence.words]
    result = [WordBasedResult('O')] * len(word_forms)
    for gazetteer_item in gazetteer:
        subsequences = search_subsequence(word_forms, gazetteer_item, end=True)
        for start, end in subsequences:
            for index in xrange(start, end + 1):
                result[index] = WordBasedResult('I')
    return SentenceBasedResult(tuple(result))


class WordBasedExtractors(object):

    STOPWORDS = nltk.corpus.stopwords.words(LANGUAGE)
    COMMON_WORDS = cPickle.load(open_gazetteer('common_words.pickle'))
    POSITIVE_WORDS = cPickle.load(open_gazetteer('positive_words.pickle'))
    NEGATIVE_WORDS = cPickle.load(open_gazetteer('negative_words.pickle'))
    CARDINAL_NUMBERS = cPickle.load(open_gazetteer('cardinal_numbers.pickle'))
    LITERAL_NUMBERS = cPickle.load(open_gazetteer('literal_numbers.pickle'))

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
        if word.word_form.lower() in WordBasedExtractors.POSITIVE_WORDS:
            return WordBasedResult('pos')
        elif word.word_form.lower() in WordBasedExtractors.NEGATIVE_WORDS:
            return WordBasedResult('neg')
        else:
            return WordBasedResult('neu')

    @staticmethod
    def lexical_named_entity_tag(word):
        return WordBasedResult(word.named_entity_tag)

    @staticmethod
    def morphological_unusual_word(word):
        res = not word.word_form.lower() in WordBasedExtractors.COMMON_WORDS
        return WordBasedResult(res)

    @staticmethod
    def morphological_is_stopword(word):
        return WordBasedResult(word.word_form in WordBasedExtractors.STOPWORDS)

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
        pattern = r'^({})$'.format(WordBasedExtractors.LITERAL_NUMBERS)
        return WordBasedResult(any(re.findall(pattern,
                                   word.word_form.lower())))

    @staticmethod
    def temporal_cardinal_number(word):
        pattern = r'^({})$'.format(WordBasedExtractors.CARDINAL_NUMBERS)
        return WordBasedResult(any(re.findall(pattern,
                                              word.word_form.lower())))

    @staticmethod
    def temporal_month(word):
        months = [calendar.month_name[num] for num in xrange(1, 13)]
        months_abbr = [m[:3] for m in months]
        months.extend([m + '.' for m in months_abbr])
        months.extend(months_abbr)
        return WordBasedResult(word.word_form.lower() in months)

    @staticmethod
    def temporal_period(word):
        periods = ['centur[y|ies]', 'decades?', 'years?', 'months?', 'days?',
                   'week\-?ends?', 'weeks?', 'hours?', 'minutes?',
                   'seconds?', 'fortnights?']
        pattern = r'^({pattern})$'.format(pattern='|'.join(periods))
        return WordBasedResult(any(re.findall(pattern,
                                              word.word_form.lower())))

    @staticmethod
    def temporal_weekday(word):
        keys = ('monday', 'tuesday', 'wednesday', 'thursday', 'friday',
                'saturday', 'sunday', 'wed', 'tues', 'tue', 'thurs', 'thur',
                'thu', 'sun', 'sat', 'mon', 'fri')
        return WordBasedResult(word.word_form.lower() in keys)

    @staticmethod
    def temporal_pod(word):
        pods = ('morning', 'afternoon', 'evening', 'night', 'noon', 'midnight',
                'midday', 'sunrise', 'dusk', 'sunset', 'dawn', 'overnight',
                'midday', 'noonday', 'noontide', 'nightfall', 'midafternoon',
                'daybreak', 'gloaming', 'a\.?m\.?', 'p\.?m\.?')
        pattrn = r'^({})s?$'.format('|'.join(pods))
        return WordBasedResult(any(re.findall(pattrn, word.word_form.lower())))

    @staticmethod
    def temporal_season(word):
        pattrn = r'^(winter|autumn|spring|summer)s?'
        return WordBasedResult(any(re.findall(pattrn, word.word_form.lower())))

    @staticmethod
    def temporal_past_ref(word):
        refs = ('yesterday', 'ago', 'earlier', 'early', 'last', 'recent',
                'nearly', 'past', 'previous', 'before')
        pattrn = r'^({})$'.format('|'.join(refs))
        return WordBasedResult(any(re.findall(pattrn, word.word_form.lower())))

    @staticmethod
    def temporal_present_ref(word):
        pattrn = r'^(tonight|current|present|now|nowadays|today|currently)$'
        return WordBasedResult(any(re.findall(pattrn, word.word_form.lower())))

    @staticmethod
    def temporal_future_ref(word):
        future_refs = ('next', 'forthcoming', 'coming', 'tomorrow', 'after',
                       'later', 'ahead')
        return WordBasedResult(word.word_form.lower() in future_refs)

    @staticmethod
    def temporal_signal(word):
        signals = ('after', 'about', 'into', 'between', 'again', 'within',
                   'every', 'for', 'on', 'the', 'since', 'in', 'of', 'until',
                   'at', 'over', 'from', 'by', 'through', 'to', 'and', 'a',
                   'each', 'till', 'as', 'about')
        return WordBasedResult(word.word_form.lower() in signals)

    @staticmethod
    def temporal_fuzzy_quantifier(word):
        quantifiers = ('approximately', 'approximate', 'approx', 'about',
                       'few', 'some', 'bunch', 'several', 'around', 'any')
        return WordBasedResult(word.word_form.lower() in quantifiers)

    @staticmethod
    def temporal_modifier(word):
        modifiers = ('beginning', 'less', 'more', 'much', 'long', 'short',
                     'end', 'start', 'half', 'few', 'most', 'several')
        return WordBasedResult(word.word_form.lower() in modifiers)

    @staticmethod
    def temporal_temporal_adverbs_points_of_time_definite(word):
        adverbs = ('now', 'then', 'today', 'tomorrow', 'tonight', 'yesterday',
                   'immediately')
        return WordBasedResult(word.word_form.lower() in adverbs)

    @staticmethod
    def temporal_temporal_adverbs_points_of_time_indefinite(word):
        adverbs = ('nowadays', 'suddenly', 'currently')
        return WordBasedResult(word.word_form.lower() in adverbs)

    @staticmethod
    def temporal_temporal_adverbs_frequency_indefinite(word):
        adverbs = ('always', 'constantly', 'ever', 'frequently', 'generally',
                   'infrequently', 'never', 'normally', 'occasionally',
                   'often', 'rarely', 'regularly', 'seldom', 'sometimes',
                   'regularly', 'usually', 'continually', 'periodically',
                   'repeatedly')
        return WordBasedResult(word.word_form.lower() in adverbs)

    @staticmethod
    def temporal_temporal_adverbs_frequency_definite(word):
        adverbs = ('annually', 'daily', 'fortnightly', 'hourly', 'monthly',
                   'nightly', 'quarterly', 'weekly', 'yearly', 'bimonthly',
                   'once', 'twice')
        return WordBasedResult(word.word_form.lower() in adverbs)

    @staticmethod
    def temporal_temporal_adverbs_relationships_in_time_indefinite(word):
        adverbs = ('already', 'before', 'early', 'earlier', 'eventually',
                   'finally', 'first', 'formerly', 'just', 'last', 'late',
                   'later', 'lately', 'next', 'previously', 'recently',
                   'since', 'soon', 'still', 'yet', 'after', 'earliest',
                   'latest', 'afterwards')
        return WordBasedResult(word.word_form.lower() in adverbs)

    @staticmethod
    def temporal_temporal_adjectives(word):
        adjectives = ('early', 'late', 'soon', 'fiscal', 'financial', 'tax')
        return WordBasedResult(word.word_form.lower() in adjectives)

    @staticmethod
    def temporal_temporal_conjunctions(word):
        conjunctions = ('when', 'while', 'meanwhile', 'during', 'on', 'and',
                        'or', 'until')
        return WordBasedResult(word.word_form.lower() in conjunctions)

    @staticmethod
    def temporal_temporal_prepositions(word):
        prepositions = ('over', 'by', 'throughout', 'pre', 'during', 'for',
                        'along', 'this', 'that', 'these', 'those', 'than',
                        'mid', 'then', 'from', 'about', 'to', 'at')
        return WordBasedResult(word.word_form.lower() in prepositions)

    @staticmethod
    def temporal_temporal_coreference(word):
        coreferences = ('dawn', 'time', 'period', 'course', 'era', 'age',
                        'season', 'quarter', 'semester', 'millenia', 'eve',
                        'millenium', 'festival', 'festivity')
        pattrn = r'^({})s?$'.format('|'.join(coreferences))
        return WordBasedResult(any(re.findall(pattrn, word.word_form.lower())))

    @staticmethod
    def temporal_festivity(word):
        festivities = ('christmas', 'easter', 'epifany', 'martin', 'luther',
                       'thanksgiving', 'halloween', 'saints', 'armistice',
                       'nativity', 'advent', 'solstice', 'boxing', 'stephen',
                       'sylvester')
        return WordBasedResult(word.word_form.lower() in festivities)

    @staticmethod
    def temporal_compound(word):
        pattrn = r'^[0-9]+\-(century|decade|year|month|week\-?end|week|day|hour|minute|second|fortnight)$'
        return WordBasedResult(any(re.findall(pattrn, word.word_form.lower())))

    @staticmethod
    def parse_2_levels_up_node(word):
        try:
            node_label = word.constituency_parent.parent().node
            return WordBasedResult(node_label)
        except TypeError:
            return WordBasedResult('_^_')

    @staticmethod
    def parse_3_levels_up_node(word):
        try:
            node_label = word.constituency_parent.parent().parent().node
            return WordBasedResult(node_label)
        except AttributeError:
            return WordBasedResult('_^_')

    @staticmethod
    def parse_2_levels_up_childs(word):
        try:
            node = word.constituency_parent.parent()
            node_labels = [i.node for i in node]
            return WordBasedResult('_'.join(node_labels))
        except AttributeError:
            return WordBasedResult('_^_')

    @staticmethod
    def parse_3_levels_up_childs(word):
        try:
            node = word.constituency_parent.parent().parent()
            node_label = [i.node for i in node]
            return WordBasedResult('_'.join(node_label))
        except AttributeError:
            return WordBasedResult('_^_')

    @staticmethod
    def parse_3_levels_up_nodes(word):
        parents = []
        try:
            parents.append(word.constituency_parent.parent().node)
            parents.append(word.constituency_parent.parent().parent().node)
            parents.append(
                word.constituency_parent.parent().parent().parent().node)
        except AttributeError:
            pass
        return WordBasedResult('_'.join(reversed(parents)))

    @staticmethod
    def parse_2_levels_up_nodes(word):
        parents = []
        try:
            parents.append(word.constituency_parent.parent().node)
            parents.append(word.constituency_parent.parent().parent().node)
        except AttributeError:
            pass
        return WordBasedResult('_'.join(reversed(parents)))

    @staticmethod
    def is_coreference_head(word):
        return WordBasedResult(word.is_coreference_head)

    @staticmethod
    def is_part_of_coreference_mention(word):
        return WordBasedResult(word.coreference_mention is not None)

    # BASIC DEPENDENCY RELATIONS
    @staticmethod
    def dependency_outgoing_relations_basic(word):
        '''For each word I represent a vector of all outgoing relations

           for each word =
            dr1   dr2   dr2   dr2   dr2   dr2   ...   dr2
           [ F  ,  F  ,  T ,   F  ,  F  ,  F  , ... ,  T ]

           Dependencies relations are taken from:
           http://nlp.stanford.edu/software/dependencies_manual.pdf

        '''
        f_suffix = lambda f_name: 'basic_dependency_outgoing_' + f_name

        r = ((f_suffix(l),
              WordBasedResult(bool(word.basic_dependencies_out.get(l, False))))
             for l in dep_labels)
        return WordBasedResults(tuple(r))

    @staticmethod
    def dependency_outgoing_relations_number_basic(word):
        return WordBasedResult(len(word.basic_dependencies_out))

    @staticmethod
    def dependency_incoming_relations_basic(word):
        '''For each word I represent a vector of all incoming relations

           for each word =
            dr1   dr2   dr2   dr2   dr2   dr2   ...   dr2
           [ F  ,  F  ,  T ,   F  ,  F  ,  F  , ... ,  T ]

           Dependencies relations are taken from:
           http://nlp.stanford.edu/software/dependencies_manual.pdf

        '''
        f_suffix = lambda f_name: 'basic_dependency_incoming_' + f_name

        r = ((f_suffix(l),
              WordBasedResult(bool(word.basic_dependencies_in.get(l, False))))
             for l in dep_labels)
        return WordBasedResults(tuple(r))

    @staticmethod
    def dependency_incoming_relations_number_basic(word):
        return WordBasedResult(len(word.basic_dependencies_in))

    # COLLAPSED DEPENDENCY RELATIONS
    @staticmethod
    def dependency_outgoing_relations_collapsed(word):
        '''For each word I represent a vector of all outgoing collapsed
        relations.

           for each word =
            dr1   dr2   dr2   dr2   dr2   dr2   ...   dr2
           [ F  ,  F  ,  T ,   F  ,  F  ,  F  , ... ,  T ]

           Dependencies relations are taken from:
           http://nlp.stanford.edu/software/dependencies_manual.pdf

        '''
        f_suffix = lambda f_name: 'collapsed_dependency_outgoing_' + f_name

        r = ((f_suffix(l),
              WordBasedResult(bool(word.collapsed_dependencies_out.get(l,
                                                                       False)))
              )
             for l in dep_labels)
        return WordBasedResults(tuple(r))

    @staticmethod
    def dependency_outgoing_relations_number_collapsed(word):
        return WordBasedResult(len(word.collapsed_dependencies_out))

    @staticmethod
    def dependency_incoming_relations_collapsed(word):
        '''For each word I represent a vector of all incoming collapsed
        relations.

           for each word =
            dr1   dr2   dr2   dr2   dr2   dr2   ...   dr2
           [ F  ,  F  ,  T ,   F  ,  F  ,  F  , ... ,  T ]

           Dependencies relations are taken from:
           http://nlp.stanford.edu/software/dependencies_manual.pdf

        '''
        f_suffix = lambda f_name: 'collapsed_dependency_incoming_' + f_name

        r = ((f_suffix(l),
              WordBasedResult(bool(word.collapsed_dependencies_in.get(l,
                                                                      False))))
             for l in dep_labels)
        return WordBasedResults(tuple(r))

    @staticmethod
    def dependency_incoming_relations_number_collapsed(word):
        return WordBasedResult(len(word.collapsed_dependencies_in))

    @staticmethod
    def dependency_incoming_granfather_relations_basic(word):
        try:
            gfather = word.dependencies_in('basic')[0][1].dependencies_in(
                'basic')[0][0]
            return WordBasedResult(gfather)
        except IndexError:
            return WordBasedResult(False)

    @staticmethod
    def dependency_incoming_granfather_relations_collapsed(word):
        try:
            gfather = word.dependencies_in('collapsed')[0][1].dependencies_in(
                'collapsed')[0][0]
            return WordBasedResult(gfather)
        except IndexError:
            return WordBasedResult(False)

    @staticmethod
    def dependency_incoming_granfather_pos_basic(word):
        try:
            pos = word.dependencies_in('basic')[0][1].dependencies_in(
                'basic')[0][1].part_of_speech
            return WordBasedResult(pos)
        except IndexError:
            return WordBasedResult(False)

    @staticmethod
    def dependency_incoming_granfather_pos_collapsed(word):
        try:
            pos = word.dependencies_in('collapsed')[0][1].dependencies_in(
                'collapsed')[0][1].part_of_speech
            return WordBasedResult(pos)
        except IndexError:
            return WordBasedResult(False)

    @staticmethod
    def dominant_verb_basic(word):
        if word.part_of_speech.startswith('V'):
            return WordBasedResult(word.part_of_speech)
        else:
            while not word.part_of_speech.startswith('V'):
                try:
                    word = word.dependencies_in('basic')[0][1]
                except IndexError:
                    return WordBasedResult(False)
            return WordBasedResult(word.part_of_speech)

    @staticmethod
    def dominant_verb_collapsed(word):
        if word.part_of_speech.startswith('V'):
            return WordBasedResult(word.part_of_speech)
        else:
            while not word.part_of_speech.startswith('V'):
                try:
                    word = word.dependencies_in('collapsed')[0][1]
                except:
                    return WordBasedResult(False)
            return WordBasedResult(word.part_of_speech)


class SentenceBasedExtractors(object):

    COUNTRIES = cPickle.load(open_gazetteer('countries.pickle'))
    ISO_COUNTRIES = cPickle.load(open_gazetteer('isocountries.pickle'))
    FESTIVITIES = cPickle.load(open_gazetteer('festivities.pickle'))

    @staticmethod
    def gazetteer_country(sentence):
        return matching_gazetteer(SentenceBasedExtractors.COUNTRIES, sentence)

    @staticmethod
    def gazetteer_isocountry(sentence):
        res = SentenceBasedExtractors.ISO_COUNTRIES
        return matching_gazetteer(res, sentence)

    @staticmethod
    def gazetteer_festivity(sentence):
        return matching_gazetteer(SentenceBasedExtractors.FESTIVITIES,
                                  sentence)

    @staticmethod
    def parse_start_or_end_child_in_s_clause(sentence):
        '''Suggested by Marilena Di Bari.
        Typically temporal expressions are at the very end or beginning of a
        well-formed English sentence.
        '''
        parsetree = sentence.parsetree
        result = []
        for idx in parsetree.treepositions(order='leaves'):
            try:
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
                leaf_result = position_under_s in(0, len(tree) - 1)
                result.append(WordBasedResult(leaf_result))
            except Exception:
                result.append(WordBasedResult(False))
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
            try:
                while not (tree.node.startswith('S') or tree.node == 'ROOT'):
                    tree = tree.parent()
                    steps_up += 1
            except AttributeError:
                pass

            result.append(WordBasedResult(steps_up))
        return SentenceBasedResult(tuple(result))


class DocumentBasedExtractors(object):

    pass


class RelationExtractors(object):

    @staticmethod
    def from_text(from_obj, to_obj, document):
        return WordBasedResult(from_obj.text)

    @staticmethod
    def to_text(from_obj, to_obj, document):
        return WordBasedResult(to_obj.text)

    @staticmethod
    def from_lemma(from_obj, to_obj, document):
        res = '-'.join([e.part_of_speech for e in from_obj.words])
        return WordBasedResult(res)

    @staticmethod
    def to_lemma(from_obj, to_obj, document):
        res = ' '.join([e.lemma for e in to_obj.words])
        return WordBasedResult(res)

    @staticmethod
    def from_pos(from_obj, to_obj, document):
        res = '-'.join([e.part_of_speech for e in from_obj.words])
        return WordBasedResult(res)

    @staticmethod
    def to_pos(from_obj, to_obj, document):
        res = '-'.join([e.part_of_speech for e in to_obj.words])
        return WordBasedResult(res)

    @staticmethod
    def same_pos(from_obj, to_obj, document):
        return WordBasedResult(
            RelationExtractors.from_pos(
                from_obj, to_obj, document) ==
            RelationExtractors.to_pos(from_obj, to_obj, document))

    @staticmethod
    def from_tag(from_obj, to_obj, document):
        return WordBasedResult(from_obj.tag)

    @staticmethod
    def to_tag(from_obj, to_obj, document):
        return WordBasedResult(to_obj.tag)

    @staticmethod
    def from_meta(from_obj, to_obj, document):
        return WordBasedResult(from_obj.meta)

    @staticmethod
    def to_meta(from_obj, to_obj, document):
        return WordBasedResult(to_obj.meta)

    @staticmethod
    def both_meta(from_obj, to_obj, document):
        return WordBasedResult(from_obj.meta and to_obj.meta)

    @staticmethod
    def both_non_meta(from_obj, to_obj, document):
        return WordBasedResult(not from_obj.meta and not to_obj.meta)

    @staticmethod
    def from_tense(from_obj, to_obj, document):
        return WordBasedResult(getattr(from_obj, 'tense', None))

    @staticmethod
    def to_tense(from_obj, to_obj, document):
        return WordBasedResult(getattr(to_obj, 'tense', None))

    @staticmethod
    def same_tense(from_obj, to_obj, document):
        if isinstance(from_obj, Event) and isinstance(to_obj, Event):
                return WordBasedResult(from_obj.tense == to_obj.tense)
        else:
            return WordBasedResult(False)

    @staticmethod
    def from_aspect(from_obj, to_obj, document):
        return WordBasedResult(getattr(from_obj, 'aspect', None))

    @staticmethod
    def to_aspect(from_obj, to_obj, document):
        return WordBasedResult(getattr(to_obj, 'aspect', None))

    @staticmethod
    def same_aspect(from_obj, to_obj, document):
        if isinstance(from_obj, Event) and isinstance(to_obj, Event):
                return WordBasedResult(from_obj.aspect == to_obj.aspect)
        else:
            return WordBasedResult(False)

    @staticmethod
    def from_polarity(from_obj, to_obj, document):
        return WordBasedResult(getattr(from_obj, 'polarity', None))

    @staticmethod
    def to_polarity(from_obj, to_obj, document):
        return WordBasedResult(getattr(to_obj, 'polarity', None))

    @staticmethod
    def same_polarity(from_obj, to_obj, document):
        if isinstance(from_obj, Event) and isinstance(to_obj, Event):
                return WordBasedResult(from_obj.polarity == to_obj.polarity)
        else:
            return WordBasedResult(False)

    @staticmethod
    def from_modality(from_obj, to_obj, document):
        return WordBasedResult(getattr(from_obj, 'modality', None))

    @staticmethod
    def to_modality(from_obj, to_obj, document):
        return WordBasedResult(getattr(to_obj, 'modality', None))

    @staticmethod
    def same_modality(from_obj, to_obj, document):
        if isinstance(from_obj, Event) and isinstance(to_obj, Event):
                return WordBasedResult(from_obj.modality == to_obj.modality)
        else:
            return WordBasedResult(False)

    @staticmethod
    def direction(from_obj, to_obj, document):
        if from_obj.id_sentence() - to_obj.id_sentence() < 0:
            return WordBasedResult('>')
        elif from_obj.id_sentence() - to_obj.id_sentence() > 0:
            return WordBasedResult('<')
        else:
            if from_obj.id_first_word() - to_obj.id_first_word() > 0:
                return WordBasedResult('>')
            else:
                return WordBasedResult('<')

    @staticmethod
    def next_each_other(from_obj, to_obj, document):
        return WordBasedResult(
            from_obj.id_sentence() == to_obj.id_sentence()
            and (from_obj.id_first_word() == to_obj.id_last_word() + 1 or
                 to_obj.id_first_word() == from_obj.id_last_word() + 1))

    @staticmethod
    def sentence_distance(from_obj, to_obj, document):
        return WordBasedResult(
            abs(from_obj.id_sentence() - to_obj.id_sentence()))

    @staticmethod
    def word_distance(from_obj, to_obj, document):
        if from_obj.id_sentence() == to_obj.id_sentence():
            if from_obj.id_first_word() < to_obj.id_first_word():
                return WordBasedResult(
                    abs(to_obj.id_first_word() - from_obj.id_last_word()))
            else:
                return WordBasedResult(
                    abs(from_obj.id_first_word() - to_obj.id_last_word()))
        else:
            return WordBasedResult('_')

    @staticmethod
    def temporal_difference(from_obj, to_obj, document):
        if isinstance(from_obj, TemporalExpression) and \
                isinstance(to_obj, TemporalExpression):
            from_dt = re.match(
                r'^([0-9]{4})-([0-9]{2})-([0-9]{2})', from_obj.value)
            to_dt = re.match(
                r'^([0-9]{4})-([0-9]{2})-([0-9]{2})', to_obj.value)
            if from_dt and to_dt:
                from_dt = date(int(from_dt.group(1)), int(from_dt.group(2)),
                               int(from_dt.group(3)))
                to_dt = date(int(to_dt.group(1)), int(to_dt.group(2)),
                             int(to_dt.group(3)))
                diff = from_dt - to_dt
                return WordBasedResult(diff.days)
            return WordBasedResult('_')
        else:
            return WordBasedResult('_')

    @staticmethod
    def from_temp_dct(from_obj, to_obj, document):
        if isinstance(from_obj, TemporalExpression):
            res = from_obj.value.replace('-', '') == \
                document.dct.replace('_', '')
            return WordBasedResult(res)
        else:
            return WordBasedResult('_')

    @staticmethod
    def from_temp_type(from_obj, to_obj, document):
        if isinstance(from_obj, TemporalExpression):
            return WordBasedResult(from_obj.ttype)
        else:
            return WordBasedResult('_')

    @staticmethod
    def to_temp_type(from_obj, to_obj, document):
        if isinstance(to_obj, TemporalExpression):
            return WordBasedResult(to_obj.ttype)
        else:
            return WordBasedResult('_')

    @staticmethod
    def same_temp_type(from_obj, to_obj, document):
        if isinstance(from_obj, TemporalExpression) and \
                isinstance(to_obj, TemporalExpression):
                return WordBasedResult(from_obj.ttype == to_obj.ttype)
        else:
            return WordBasedResult(False)

    @staticmethod
    def from_temp_modality(from_obj, to_obj, document):
        if isinstance(from_obj, TemporalExpression):
            return WordBasedResult(from_obj.mod)
        else:
            return WordBasedResult('_')

    @staticmethod
    def to_temp_modality(from_obj, to_obj, document):
        if isinstance(to_obj, TemporalExpression):
            return WordBasedResult(to_obj.mod)
        else:
            return WordBasedResult('_')

    @staticmethod
    def same_temp_modality(from_obj, to_obj, document):
        if isinstance(from_obj, TemporalExpression) and \
                isinstance(to_obj, TemporalExpression):
                return WordBasedResult(from_obj.mod == to_obj.mod)
        else:
            return WordBasedResult(False)

    @staticmethod
    def sentences_linked_by_coref(from_obj, to_obj, document):
        """Checks whether the sentence of from_obj and the one of to_obj are
        linked by a coreferencial link.

        """
        linked = document.sentences[from_obj.id_sentence()].connected_to(
            to_obj.id_sentence())
        return WordBasedResult(linked)

    @staticmethod
    def linked_by_dependency_relation(from_obj, to_obj, document):
        '''It returns if the two elements are connected through one of their
        words.

        '''
        def same_sentence(from_obj, to_obj):
            return from_obj.id_sentence() == to_obj.id_sentence()

        def connected(word1, word2):
            cond1 = word1.dependencies_in('basic', word2)
            cond2 = word2.dependencies_in('basic', word1)
            if cond1:
                return '<'
            if cond2:
                return '>'
            return False

        if same_sentence(from_obj, to_obj):
            for from_word in from_obj.words:
                for to_word in to_obj.words:
                    conn = connected(from_word, to_word)
                    if conn:
                        return WordBasedResult(conn)
        return WordBasedResult(False)

    @staticmethod
    def prepositions_in_between(from_obj, to_obj, document):
        words_in_between = document.words(start=from_obj.end, end=to_obj.start)
        preps = '-'.join([w.lemma for w in words_in_between
                          if w.part_of_speech == 'IN'])
        return WordBasedResult(preps)

    @staticmethod
    def prepositions_first_last_in_between(from_obj, to_obj, document):
        words_in_between = document.words(start=from_obj.end, end=to_obj.start)
        preps = [w.lemma for w in words_in_between if w.part_of_speech == 'IN']
        if len(preps) >= 2:
            preps = [preps[0], preps[-1]]
        return WordBasedResult(' '.join(preps))

    @staticmethod
    def dependency_relation_type(from_obj, to_obj, document):
        if from_obj.id_sentence() != to_obj.id_sentence():
            return WordBasedResult('')

        result = []
        for from_word in from_obj.words:
            for to_word in to_obj.words:
                try:
                    from_father = from_word.dependencies_in('basic', to_word)
                    to_father = to_word.dependencies_in('basic', from_word)
                    if from_father:
                        result.append(from_father[0][0])
                        continue
                    if to_father:
                        result.append(to_father[0][0])
                        continue
                except KeyError:
                    pass
        return WordBasedResult(' '.join(result))

    @staticmethod
    def from_is_root(from_obj, to_obj, document):
        """It returns True if one of the words in `from_obj` is ROOT according
        to the dependency relations.

        """
        sent = document.sentences[from_obj.id_sentence()]
        from_ids = [w.id_token for w in from_obj.words]
        res = any([sent.basic_dependencies.is_root(n) for n in from_ids])
        return WordBasedResult(res)

    @staticmethod
    def to_is_root(from_obj, to_obj, document):
        """It returns True if one of the words in `to_obj` is ROOT according
        to the dependency relations.

        """
        sent = document.sentences[to_obj.id_sentence()]
        to_ids = [w.id_token for w in to_obj.words]
        res = any([sent.basic_dependencies.is_root(n) for n in to_ids])
        return WordBasedResult(res)

    @staticmethod
    def from_governor_verb_lemma(from_obj, to_obj, document):

        def stop_condition(word):
            return any([word_to.part_of_speech.startswith('V') for _, word_to
                        in word.dependencies_in('basic')])

        sentence = document.sentences[from_obj.id_sentence()]
        governors_lemma = set()
        for word in from_obj.words:
            try:
                while not stop_condition(word):
                    parents = sentence.dependencies_in('basic')
                    if parents:
                        word = parents[0][1]
                governors_lemma.add(word.lemma)
            except:
                continue
        return WordBasedResult('-'.join(sorted(governors_lemma)))

    @staticmethod
    def from_governor_verb_pos(from_obj, to_obj, document):

        def stop_condition(word):
            return any([word_to.part_of_speech.startswith('V') for _, word_to
                        in word.dependencies_in('basic')])

        sentence = document.sentences[from_obj.id_sentence()]
        governors_pos = set()
        for word in from_obj.words:
            try:
                while not stop_condition(word):
                    parents = sentence.dependencies_in('basic')
                    if parents:
                        word = parents[0][1]
                governors_pos.add(word.part_of_speech)
            except:
                continue
        return WordBasedResult('-'.join(sorted(governors_pos)))

    @staticmethod
    def to_governor_verb_lemma(from_obj, to_obj, document):

        def stop_condition(word):
            return any([word_to.part_of_speech.startswith('V') for _, word_to
                        in word.dependencies_in('basic')])

        sentence = document.sentences[from_obj.id_sentence()]
        governors_lemma = set()
        for word in from_obj.words:
            try:
                while not stop_condition(word):
                    parents = sentence.dependencies_in('basic')
                    if parents:
                        word = parents[0][1]
                governors_lemma.add(word.lemma)
            except:
                continue
        return WordBasedResult('-'.join(sorted(governors_lemma)))

    @staticmethod
    def to_governor_verb_pos(from_obj, to_obj, document):

        def stop_condition(word):
            return any([word_to.part_of_speech.startswith('V') for _, word_to
                        in word.dependencies_in('basic')])

        sentence = document.sentences[to_obj.id_sentence()]
        governors_pos = set()
        for word in to_obj.words:
            try:
                while not stop_condition(word):
                    parents = sentence.dependencies_in('basic')
                    if parents:
                        word = parents[0][1]
                governors_pos.add(word.part_of_speech)
            except:
                continue
        return WordBasedResult('-'.join(sorted(governors_pos)))

    @staticmethod
    def temporal_signals_in_between(from_obj, to_obj, document):
        start, end = from_obj.id_first_word(), to_obj.id_last_word()
        words = document.words(start=start, end=end)
        return WordBasedResult(' '.join([w.lemma for w in words
                                         if w.part_of_speech == 'IN']))

    @staticmethod
    def from_prepositional_phrase(from_obj, to_obj, document):
        start, end = from_obj.id_first_word() + 1, from_obj.id_last_word() + 1
        sentence = document.sentences[from_obj.words[0].id_sentence]
        positions = list(sentence.parsetree.treepositions(order='leaves'))
        address = positions[start - 1]
        for w in positions[start:end]:
            if len(w) < len(address):
                address = w
        common_ancestor = sentence.parsetree[address[:-1]]
        return WordBasedResult(common_ancestor == 'PP')

    @staticmethod
    def to_prepositional_phrase(from_obj, to_obj, document):
        start, end = to_obj.id_first_word() + 1, to_obj.id_last_word() + 1
        sentence = document.sentences[to_obj.words[0].id_sentence]
        positions = list(sentence.parsetree.treepositions(order='leaves'))
        address = positions[start - 1]
        for w in positions[start:end]:
            if len(w) < len(address):
                address = w
        common_ancestor = sentence.parsetree[address[:-1]]
        return WordBasedResult(common_ancestor == 'PP')

    @staticmethod
    def from_parse_common_ancestor(from_obj, to_obj, document):
        start, end = from_obj.id_first_word() + 1, from_obj.id_last_word() + 1
        sentence = document.sentences[from_obj.words[0].id_sentence]
        positions = list(sentence.parsetree.treepositions(order='leaves'))
        address = positions[start - 1]
        for w in positions[start:end]:
            if len(w) < len(address):
                address = w
        common_ancestor = sentence.parsetree[address[:-1]]
        return WordBasedResult(common_ancestor.node)

    @staticmethod
    def to_parse_common_ancestor(from_obj, to_obj, document):
        start, end = to_obj.id_first_word() + 1, to_obj.id_last_word() + 1
        sentence = document.sentences[to_obj.words[0].id_sentence]
        positions = list(sentence.parsetree.treepositions(order='leaves'))
        address = positions[start - 1]
        for w in positions[start:end]:
            if len(w) < len(address):
                address = w
        common_ancestor = sentence.parsetree[address[:-1]]
        return WordBasedResult(common_ancestor.node)
