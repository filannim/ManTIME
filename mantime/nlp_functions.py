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
import pickle
import nltk
import re
import subprocess

import MBSP

from properties import property as paths


def memoise(function):
    """ Memoization decorator

        It save the result of a function wrt its arguments.
    """
    class Memodict(dict):
        """It extendes a Python dictionary and it's used to store intermediate
           results. It works like a cache memory for functions.
        """
        def __getitem__(self, *key):
            return dict.__getitem__(self, key)

        def __missing__(self, key):
            ret = self[key] = function(*key)
            return ret
    return Memodict().__getitem__

class NLP:
    """Natural Language Processing utility class

    It is a Word factory.  It's used to avoid waste of computation.  If you
    give it an already given word it will return an already existing object
    rather than a new one.
    """

    def __init__(self):
        self.words = {}
        self.new_objects = 0
        self.reused = 0
        self.calls = 0
        self.words_start = 0
        self.common_words = pickle.load(file('gazetteer/common_words.pickle','r'))

    def get(self,word):
        """Returns a Word object containing all its features.

        It's used to avoid waste of computation.  If you
        give it an already given word it will return an already existing object
        rather than a new one.
        """
        self.calls += 1 
        if self.words.get(word):
            self.reused += 1
            return self.words[word]
        else:
            self.new_objects += 1
            self.words[word] = Word(word, self.common_words)
            return self.words[word]

    def status(self):
        """Prints the factory status.

        There is the number of times the factory has been used along with the
        percentage of objects reused.
        """
        print '-- NLP Module status -----'
        print
        print ' Reused:', str(round(self.reused/self.calls*100,2))+'% out of', str(self.calls), 'calls.'
        print '--------------------------'

class Word:
    """Word class with all the word features saved in it.

    It contains all the features that depends on the word (as it is).
    """

    def __init__(self, word, common_words):
        self.word = word
        self.wn = nltk.corpus.wordnet
        self.synsets = self.wn.synsets(self.word)
        self.lemmas = list(set([lemma for synset in self.synsets for lemma in synset.lemmas]))
        self.synsets_vb = self.wn.synsets(self.word, self.wn.VERB)
        self.common_words = common_words
        self._no_letters = None
        self._no_letters_and_numbers = None
        self._is_all_caps_dots = None
        self._is_all_digits_dots = None
        self._unusual = None
        self._pattern = None
        self._extended_pattern = None
        self._vocal_pattern = None
        self._has_digit = None
        self._has_symbols = None
        self._lemma_names = None
        self._hypernyms = None
        self._entailments = None
        self._antonyms = None
        self._hyponyms = None
        self._preprocessedword = None

    def preprocessed_word(self):
        if not self._preprocessedword:
            self._preprocessedword = re.sub('[0-9]', '@', self.word)
        return self._preprocessedword

    def no_letters(self):
        if not self._no_letters:
            self._no_letters = ''.join([c for c in self.word if not c.isalpha()])
        return self._no_letters

    def no_letters_and_numbers(self):
        if not self._no_letters_and_numbers:
            self._no_letters_and_numbers = ''.join([c for c in self.word if not (c.isalpha() or c.isdigit())])
        return self._no_letters_and_numbers

    def is_all_caps_and_dots(self):
        if not self._is_all_caps_dots:
            self._is_all_caps_dots = all([(c.isupper() or c=='.') for c in self.word])
        return self._is_all_caps_dots

    def is_all_digits_and_dots(self):
        if not self._is_all_digits_dots:
            self._is_all_digits_dots = all([(c.isdigit() or c=='.') for c in self.word])
        return self._is_all_digits_dots

    def unusual(self):
        if not self._unusual:
            self._unusual = not self.word.lower() in self.common_words
        return self._unusual

    def pattern(self):
        if not self._pattern:
            pattern = ''
            for char in self.word:
                if char.isupper():
                    if pattern[-1:]!='X':
                        pattern += 'X'
                elif char.islower():
                    if pattern[-1:]!='x':
                        pattern += 'x'
                elif char.isdigit():
                    if pattern[-1:]!='d':
                        pattern += 'd'
                elif char.isspace():
                    if pattern[-1:]!=' ':
                        pattern += ' '
                else:
                    if pattern[-1:]!=char:
                        pattern += char
            self._pattern = pattern
        return self._pattern

    def extended_pattern(self):
        if not self._extended_pattern:
            pattern = ''
            for char in self.word:
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
            self._extended_pattern = pattern
        return self._extended_pattern

    def vocal_pattern(self):
        if not self._vocal_pattern:
            pattern = ''
            for char in self.word:
                if char in ['a','e','i','o','u']:
                    if pattern[-1:]!='v':
                        pattern += 'v'
                elif char.isdigit():
                    if pattern[-1:]!='D':
                        pattern += 'D'
                elif char.isspace():
                    if pattern[-1:]!=' ':
                        pattern += ' '
                elif not char.isalnum():
                    if pattern[-1:]!='p':
                        pattern += 'p'
                else:
                    if pattern[-1:]!='c':
                        pattern += 'c'
            self._vocal_pattern = pattern
        return self._vocal_pattern

    def has_digit(self):
        if not self._has_digit:
            for char in self.word:
                if char.isdigit():
                    self._has_digit = True
                    return True
                    break
            self._has_digit = False
            return False
        else:
            return self._has_digit

    def has_symbols(self):
        if not self._has_symbols:
            for char in self.word:
                if not (char.isdigit() or char.isalpha()):
                    self._has_symbols = True
                    return True
                    break
            self._has_symbols = False
            return False
        else:
            return self._has_symbols

    def wn_lemma_names(self):
        if self._lemma_names == None:
          self._lemma_names = list(set([name for synset in self.synsets[0:2] for name in synset.lemma_names[0:3]]))
        return self._lemma_names

    def wn_hypernyms(self):
        if self._hypernyms == None:
            self._hypernyms = list(set([str(name) for synset in self.synsets[0:2] for name in synset.hypernyms()[0:3]]))
        return self._hypernyms

    def wn_entailments(self):
        if self._entailments == None:
          self._entailments = list(set([str(ent) for synset in self.synsets_vb[0:2] for ent in synset.entailments()[0:3]]))
        return self._entailments

    def wn_antonyms(self):
        if self._antonyms == None:
          self._antonyms = list(set([str(ant) for lemma in self.lemmas[0:2] for ant in lemma.antonyms()[0:3]]))
        return self._antonyms

    def wn_hyponyms(self):
        if self._hyponyms == None:
          self._hyponyms = list(set([str(hyp) for synset in self.synsets[0:2] for hyp in synset.hyponyms()[0:3]]))
        return self._hyponyms

class TreeTaggerTokeniser():
    """TreeTagger tokeniser interface class

    It runs tokenize.pl script through the command line and parse the result.
    """
    path = paths['path_treetagger_tokenizer']

    @classmethod
    def tokenize(cls, sentence):
        p = subprocess.Popen([cls.path],stdout=subprocess.PIPE,stdin=subprocess.PIPE)
        p.stdin.write(sentence)
        sentence_tokenised = p.communicate()[0].strip().split('\n')
        p.stdin.close()
        tokens = [token.strip() for token 
                  in sentence_tokenised if token.strip() != '']
        return tokens

    @classmethod
    def set_path(cls, path):
        """Sets the tokeniser path."""
        cls.path = path

class TreeTaggerPOS():
    '''TreeTagger tokeniser interface class.

    It runs tokenize.pl script through the command line and parse the result.
    '''
    path = paths['path_treetagger']

    @classmethod
    def tag(cls, tokens):
        tokens = '\n'.join(tokens)
        p = subprocess.Popen([cls.path],stdout=subprocess.PIPE,stdin=subprocess.PIPE)
        p.stdin.write(tokens)
        sentence_tokenised = p.communicate()[0].strip().split('\n')
        p.stdin.close()
        for line in sentence_tokenised:
            yield line.split('\t')
        #return [line.split('\t') for line in sentence_tokenised.split('\n')]

    @classmethod
    def set_path(cls, path):
        """Sets the tokeniser path."""
        cls.path = path

class Parser():
  '''MBSP interface class.

  It uses MBSP system (from CliPs) and returns the results in an easily
  integrable format.
  
  Output format: [word_id, chunk, pnp]
  '''
  @classmethod
  def parse(cls, sentence):
      output = MBSP.chunk(sentence, tokenize=False, lemmata=False).split(' ')
      output = [token_tags.split('/') for token_tags in output]
      return [[token_tag[2], token_tag[3]] for token_tag in output]


@memoise
def tense(pos):
    if pos in ('VB', 'VD', 'VH', 'VV'):
        return 'BASE'
    elif pos in ('VBN', 'VDN', 'VHN', 'VVN'):
        return 'PASTPARTICIPLE'
    elif pos in ('VBD', 'VDD', 'VHD', 'VVD'):
        return 'PAST'
    elif pos in ('VBG', 'VDG', 'VHG', 'VVG'):
        return 'GERUND'
    elif pos in ('VBZ', 'VBP', 'VDZ', 'VDP', 'VHZ', 'VHP'):
        return 'PRESENT'
    else:
        return 'NONE'
