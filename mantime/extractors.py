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

import re
import pickle

import nltk

from utilities import Memoize
from utilities import search_subsequence

PORTER_STEMMER = Memoize(nltk.PorterStemmer().stem)
LANCASTER_STEMMER = Memoize(nltk.LancasterStemmer().stem)
WORDNET_LEMMATIZER = Memoize(nltk.WordNetLemmatizer().lemmatize)
COMMON_WORDS = pickle.load(open('data/gazetteer/common_words.pickle'))
POSITIVE_WORDS = pickle.load(open('data/gazetteer/positive_words.pickle'))
NEGATIVE_WORDS = pickle.load(open('data/gazetteer/negative_words.pickle'))
MALE_NAMES = pickle.load(open('data/gazetteer/male.pickle'))
FEMALE_NAMES = pickle.load(open('data/gazetteer/female.pickle'))
COUNTRIES = pickle.load(open('data/gazetteer/countries.pickle'))
ISO_COUNTRIES = pickle.load(open('data/gazetteer/isocountries.pickle'))
US_CITIES = pickle.load(open('data/gazetteer/uscities.pickle'))
NATIONALITIES = pickle.load(open('data/gazetteer/nationalities.pickle'))
FESTIVITIES = pickle.load(open('data/gazetteer/festivities.pickle'))
PHONEME_DICTIONARY = nltk.corpus.cmudict.dict()

class WordBasedExtractors(object):

    @staticmethod
    def token(word):
        return word.word_form

    @staticmethod
    def token_normalised(word):
        return re.sub(r'\d', 'D', word.word_form.strip())

    @staticmethod
    def lexical_lemma(word):
        return word.lemma

    @staticmethod
    def lexical_pos(word):
        return word.part_of_speech

    @staticmethod
    def lexical_tense(word):
        postag = word.part_of_speech
        if postag in ('VB', 'VD', 'VH', 'VV'):
            return 'BASE'
        elif postag in ('VBN', 'VDN', 'VHN', 'VVN'):
            return 'PASTPARTICIPLE'
        elif postag in ('VBD', 'VDD', 'VHD', 'VVD'):
            return 'PAST'
        elif postag in ('VBG', 'VDG', 'VHG', 'VVG'):
            return 'GERUND'
        elif postag in ('VBZ', 'VBP', 'VDZ', 'VDP', 'VHZ', 'VHP'):
            return 'PRESENT'
        else:
            return 'NONE'

    @staticmethod
    def lexical_polarity(word):
        if word.word_form.lower() in POSITIVE_WORDS:
            return 'pos'
        elif word.word_form.lower() in NEGATIVE_WORDS:
            return 'neg'
        else:
            return 'neu'

    @staticmethod
    def lexical_named_entity_tag(word):
        return word.named_entity_tag

    @staticmethod
    def morphological_wordnet_lemma(word):
        return WORDNET_LEMMATIZER(word.word_form)

    @staticmethod
    def morphological_porter_stem(word):
        return PORTER_STEMMER(word.word_form)

    @staticmethod
    def morphological_lancaster_stem(word):
        return LANCASTER_STEMMER(word.word_form)

    @staticmethod
    def morphological_unusual_word(word):
        return not word.word_form.lower() in COMMON_WORDS

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
        return pattern

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
        return pattern

    @staticmethod
    def morphological_vocal_pattern(word):
        pattern = ''
        for char in word.word_form:
            if char in ['a', 'e', 'i', 'o', 'u']:
                if pattern[-1:] != 'v':
                    pattern += 'v'
            elif char.isdigit():
                if pattern[-1:] != 'D':
                    pattern += 'D'
            elif char.isspace():
                if pattern[-1:] != ' ':
                    pattern += ' '
            elif not char.isalnum():
                if pattern[-1:] != 'p':
                    pattern += 'p'
            else:
                if pattern[-1:] != 'c':
                    pattern += 'c'
        return pattern

    @staticmethod
    def morphological_has_digit(word):
        return any(map(str.isdigit, word.word_form))

    @staticmethod
    def morphological_has_symbol(word):
        issymbol = lambda x: not (x.isdigit() or x.isalpha())
        return any(map(issymbol, word.word_form))

    @staticmethod
    def morphological_prefix(word):
        return word.word_form[:3] or word.word_form[:2] or word.word_form[:1]

    @staticmethod
    def morphological_suffix(word):
        return word.word_form[-3:] or word.word_form[-2:] or word.word_form[-1:]

    @staticmethod
    def morphological_first_upper(word):
        return word.word_form[0].isupper()

    @staticmethod
    def morphological_is_alpha(word):
        return word.word_form.isalpha()

    @staticmethod
    def morphological_is_lower(word):
        return word.word_form.islower()

    @staticmethod
    def morphological_is_digit(word):
        return word.word_form.isdigit()

    @staticmethod
    def morphological_is_alphabetic(word):
        return word.word_form.isalpha()

    @staticmethod
    def morphological_is_alphanumeric(word):
        return word.word_form.isalnum()

    @staticmethod
    def morphological_is_title(word):
        return word.word_form.istitle()

    @staticmethod
    def morphological_is_upper(word):
        return word.word_form.isupper()

    @staticmethod
    def morphological_is_numeric(word):
        return unicode(word.word_form).isnumeric()

    @staticmethod
    def morphological_is_decimal(word):
        return unicode(word.word_form).isdecimal()

    @staticmethod
    def morphological_ends_with_s(word):
        return word.word_form[-1] == 's'

    @staticmethod
    def morphological_token_with_no_letters(word):
        return ''.join([c for c in word.word_form if not c.isalpha()])

    @staticmethod
    def morphological_token_with_no_letters_and_numbers(word):
        return ''.join([c for c in word.word_form if not (c.isalpha() or c.isdigit())])

    @staticmethod
    def morphological_is_all_caps_and_dots(word):
        iscapsanddots = lambda x: x.isupper() or x == '.'
        return all(map(iscapsanddots, word.word_form))

    @staticmethod
    def morphological_is_all_digits_and_dots(word):
        isdigitsanddots = lambda x: x.isdigit() or x == '.'
        return all(map(isdigitsanddots, word.word_form))

    @staticmethod
    def temporal_number(word):
        return any(re.findall('^[0-9]+ ?(?:st|nd|rd|th)$', word.word_form.lower()))

    @staticmethod
    def temporal_time(word):
        return any(re.findall('^([0-9]{1,2})[:\.\-]([0-9]{1,2}) ?(a\.?m\.?|p\.?m\.?)?$', word.word_form.lower()))

    @staticmethod
    def temporal_digit(word):
        return any(re.findall('^[0-9]+$', word.word_form.lower()))

    @staticmethod
    def temporal_ordinal(word):
        return any(re.findall('^(st|nd|rd|th)$', word.word_form.lower()))

    @staticmethod
    def temporal_year(word):
        return any(re.findall('^[12][0-9]{3}|\'[0-9]{2,3}$', word.word_form.lower()))

    @staticmethod
    def temporal_literal_number(word):
        return any(re.findall('^(zero|one|two|three|four|five|six|seven|eight|nine|ten|eleven|twelve|thirteen|fourteen|fifteen|sixteen|seventeen|eighteen|nineteen|twenty|twenty|thirty|forty|fifty|sixty|seventy|eighty|ninety|hundreds?|thousands?|)$', word.word_form.lower()))

    @staticmethod
    def temporal_cardinal(word):
        return any(re.findall('^(first|second|third|fourth|fifth|sixth|seventh|eighth|nineth|tenth|eleventh|twelfth|thirteenth|fourteenth|fifteenth|sixteenth|seventeenth|eighteenth|nineteenth|twentieth|thirtieth|fortieth|fiftieth|sixtieth|seventieth|eightieth|ninetieth|hundredth|thousandth)$', word.word_form.lower()))

    @staticmethod
    def temporal_month(word):
        return any(re.findall('^(january|february|march|april|may|june|july|august|september|october|november|december|jan|feb|mar|apr|may|jun|jul|aug|sept|oct|nov|dec)\.?$', word.word_form.lower()))

    @staticmethod
    def temporal_period(word):
        return any(re.findall('^(centur[y|ies]|decades?|years?|months?|week\-?ends?|weeks?|days?|hours?|minutes?|seconds?|fortnights?|)$', word.word_form.lower()))

    @staticmethod
    def temporal_weekday(word):
        return any(re.findall('^(monday|tuesday|wednesday|thursday|friday|saturday|sunday|wed|tues|tue|thurs|thur|thu|sun|sat|mon|fri)$', word.word_form.lower()))

    @staticmethod
    def temporal_pod(word):
        return any(re.findall('^(morning|afternoon|evening|night|noon|midnight|midday|sunrise|dusk|sunset|dawn|overnight|midday|noonday|noontide|nightfall|midafternoon|daybreak|gloaming|a\.?m\.?|p\.?m\.?)s?$', word.word_form.lower()))

    @staticmethod
    def temporal_season(word):
        return any(re.findall('^(winter|autumn|spring|summer)s?', word.word_form.lower()))

    @staticmethod
    def temporal_past_ref(word):
        return any(re.findall('^(yesterday|ago|earlier|early|last|recent|nearly|past|previous|before)$', word.word_form.lower()))    

    @staticmethod
    def temporal_present_ref(word):
        return any(re.findall('^(tonight|current|present|now|nowadays|today|currently)$', word.word_form.lower()))    

    @staticmethod
    def temporal_future_ref(word):
        return any(re.findall('^(next|forthcoming|coming|tomorrow|after|later|ahead)$', word.word_form.lower()))

    @staticmethod
    def temporal_signal(word):
        return any(re.findall('^(after|about|into|between|again|within|every|for|on|the|since|in|of|until|at|over|from|by|through|to|and|a)$', word.word_form.lower()))

    @staticmethod
    def temporal_fuzzy_quantifier(word):
        return any(re.findall('^(approximately|approximate|approx|about|few|some|bunch|several|around)$', word.word_form.lower()))

    @staticmethod
    def temporal_modifier(word):
        return any(re.findall('^(beginning|less|more|much|long|short|end|start|half)$', word.word_form.lower()))

    @staticmethod
    def temporal_temporal_adverbs(word):
        return any(re.findall('^(daily|earlier)$', word.word_form.lower()))

    @staticmethod
    def temporal_temporal_adjectives(word):
        return any(re.findall('^(early|late|soon|fiscal|financial|tax)$', word.word_form.lower()))

    @staticmethod
    def temporal_temporal_conjunctives(word):
        return any(re.findall('^(when|while|meanwhile|during|on|and|or|until)$', word.word_form.lower()))

    @staticmethod
    def temporal_temporal_prepositions(word):
        return any(re.findall('^(pre|during|for|over|along|this|that|these|those|than|mid)$', word.word_form.lower()))

    @staticmethod
    def temporal_temporal_coreference(word):
        return any(re.findall('^(dawn|time|period|course|era|age|season|quarter|semester|millenia|millenium|eve|festival|festivity)s?$', word.word_form.lower()))

    @staticmethod
    def temporal_festivity(word):
        return any(re.findall('^(christmas|easter|epifany|martin|luther|thanksgiving|halloween|saints|armistice|nativity|advent|solstice|boxing|stephen|sylvester)$', word.word_form.lower()))

    @staticmethod
    def temporal_compound(word):
        return any(re.findall('^[0-9]+\-(century|decade|year|month|week\-end|week|day|hour|minute|second|fortnight|)$', word.word_form.lower()))

    @staticmethod
    def phonetic_form(word):
        phonemes = PHONEME_DICTIONARY.get(word.word_form.lower(), [''])[0]
        attributes = (('phonetic_form', '-'.join(phonemes) or '_'),
                      ('phonetic_length', len(phonemes)),
                      ('phonetic_first', phonemes[0] if phonemes else '_'),
                      ('phonetic_last', phonemes[-1] if phonemes else '_'))
        return WordBasedResults(attributes)


class SentenceBasedExtractors(object):

    @staticmethod
    def gazetteer_malename(sentence):
        tokens = [token[0] for token in sentence['words']]
        result = []
        for gazetteer_item in MALE_NAMES:
            if 

    @staticmethod
    def gazetteer_femalename

    @staticmethod
    def gazetteer_country

    @staticmethod
    def gazetteer_male


class DocumentBasedExtractor(ojbect):

    @staticmethod
    def ...


class WordBasedResult(object):

    def __init__(self, value):
        assert type(value) in (str, bool, int, float)
        if type(self.value) in (str, bool):
            self.value = '"{}"'.format(str(self.value))
        else:
            self.value = '{}'.format(str(self.value))

    def apply(word, name):
        assert type(word) == Word, 'Wrong word type'
        word.attributes[name] == self.value


class WordBasedResults(object):

    def __init__(self, values):
        assert type(values) == tuple
        self.values = values


class SentenceBasedResult(object):

    def __init__(self, values):
        assert type(values) == tuple, 'Wrong type for values'
        assert len(set([type(value) for value in values])) == 1, \
            'Multiple types in values'
        assert set([type(value) for value in values])[0] == WordBasedResult, \
            'No word-based values in values'
        self.values = values