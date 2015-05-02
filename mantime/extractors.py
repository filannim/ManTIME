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
import functools

import nltk
from num2words import num2words

from utilities import search_subsequence
from model_extractors import WordBasedResult
from model_extractors import SentenceBasedResult
from model_extractors import SentenceBasedResults
from settings import LANGUAGE
from settings import GAZETTEER_FOLDER


open_gazetteer = lambda file_name: open(GAZETTEER_FOLDER + file_name)


def memoise(obj):
    try:
        cache_file = open('../buffer/extractors/' + obj.__name__)
        cache = obj.cache = cPickle.load(cache_file)
    except IOError:
        cache = obj.cache = {}

    @functools.wraps(obj)
    def memoiser(*args, **kwargs):
        key = hash(args) * hash(frozenset(kwargs))
        if key not in cache:
            cache[key] = obj(*args, **kwargs)
        return cache[key]
    return memoiser


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
    CARDINAL_NUMBERS = set([num2words(num, True) for num in xrange(0, 1001)])
    CARDINAL_NUMBERS.update([num.replace('-', '') for num in CARDINAL_NUMBERS])
    CARDINAL_NUMBERS = '|'.join(CARDINAL_NUMBERS)
    LITERAL_NUMBERS = set([num2words(num) for num in xrange(0, 1001)])
    LITERAL_NUMBERS.update([num.replace('-', '') for num in LITERAL_NUMBERS])
    LITERAL_NUMBERS = '|'.join(LITERAL_NUMBERS)

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
                except (TypeError, AttributeError):
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
