#!/usr/bin/python
#
#   Copyright 2012 Michele Filannino
#
#   gnTEAM, School of Computer Science, University of Manchester.
#   All rights reserved. This program and the accompanying materials
#   are made available under the terms of the GNU General Public License.
#
#   authors: Michele Filannino
#   email:  filannim@cs.man.ac.uk
#
#   This work is part of 2012 i2b2 challenge.
#   For details, see www.cs.man.ac.uk/~filannim/

""" It analyses the structure of the clinical document (i2b2 format) and
    provides an object which exposes the key dates extracted in the doc.

"""

from __future__ import division
import codecs
from datetime import date as datex
import re
import os
import sys

from timex_clinical import normalise


class DocumentAnalyser(object):
    """Analyses clinical documents

    This module reads a txt file and extracts in the form of a key-value pairs
    all the clinical temporally relevant information: admission date, discharge
    date, operation date and so on.
    """
    def __init__(self):
        self.admission_signals = ('admission')
        self.discharge_signals = ('discharge')
        self.operation_signals = ('operating room')
        self.transfer_signals = ('transfer')
        self.date_syntaxes = ['[0-9][0-9]*[/|-][0-9][0-9]*(?:[/|-][0-9][0-9]*)?|[0-9]{8}|[0-9]{6}|[0-9]{4}']

    def analyse(self, path, filename, normalisation=False):
        clinical_note = ClinicalDocument()
        text = ''
        with codecs.open(os.path.join(path, filename)) as file_content:
            for line in file_content:
                if not re.match("^(?:\]\]>)?<(?:\?|/)?[A-Za-z]+", line):
                    text += line.lower()
        date_refs = [(match.start(), match.end()) for match in re.finditer(self.date_syntaxes[0], text)]
        clinical_note.file_name = filename
        clinical_note.file_path = path
        if normalisation:
            clinical_note.admission_date = normalise(self.search_closest(self.admission_signals, date_refs, text, 'forward', 6))[2]
            clinical_note.discharge_date = normalise(self.search_closest(self.discharge_signals, date_refs, text, 'forward', 6))[2]
            if clinical_note.discharge_date == 'NONE':
                clinical_note.discharge_date = normalise(self.search_closest(self.discharge_signals, date_refs, text, 'forward', 50))[2]
            clinical_note.operation_date = normalise(self.search_closest(self.operation_signals, date_refs, text, 'both'), clinical_note.admission_date.replace('-', ''))[2]
            clinical_note.transfer_date = normalise(self.search_closest(self.transfer_signals, date_refs, text, 'both'), clinical_note.admission_date.replace('-', ''))[2]
            clinical_note.course_length = self.get_difference_from_normalised_dates(clinical_note.admission_date, clinical_note.discharge_date)
        else:
            clinical_note.admission_date = self.search_closest(self.admission_signals, date_refs, text, 'forward', 6)
            clinical_note.discharge_date = self.search_closest(self.discharge_signals, date_refs, text, 'forward', 6)
            if not clinical_note.discharge_date:
                clinical_note.discharge_date = self.search_closest(self.discharge_signals, date_refs, text, 'forward', 50)
                clinical_note.discharge_date_not_in_header = True
            clinical_note.operation_date = self.search_closest(self.operation_signals, date_refs, text, 'both')
            clinical_note.transfer_date = self.search_closest(self.transfer_signals, date_refs, text, 'both')
            clinical_note.course_length = self.get_difference_from_normalised_dates(normalise(clinical_note.admission_date)[2], normalise(clinical_note.discharge_date)[2])
        return clinical_note

    def search_closest(self, object, date_refs, text, direction='both', threshold=10*10):
        min_value = 10**10
        object_refs = [match.start() for match in re.finditer(re.escape(object), text)]
        result = (-1, -1, -1)
        for target_word in object_refs:
            if direction =='forward': dates = [date for date in date_refs if date[0] > target_word and self.get_number_of_newlines_inside(0, date[0], text) <= threshold]
            elif direction =='backward': dates = [date for date in date_refs if date[0] < target_word and self.get_number_of_newlines_inside(0, date[0], text) <= threshold]
            else: dates = [date for date in date_refs if self.get_number_of_newlines_inside(0, date[0], text) <= threshold]
            for date in dates:
                n_of_returns = self.get_number_of_newlines_inside(date[0], target_word, text)
                distance = abs(date[0]-target_word)*(n_of_returns+1)
                # print n_of_returns, self.get_number_of_newlines_inside(date[0],target_word,text)
                if distance<min_value:
                    result = (target_word,date[0],date[1])
                    min_value = distance
                # print text[date[0]:date[1]]
        return text[result[1]:result[2]]

    def get_number_of_newlines_inside(self, start, end, text):
        return_refs = [match.start() for match in re.finditer(re.escape('\n'),
                       text)]
        result = len([return_pointer for return_pointer in return_refs if
                      return_pointer < max(start, end) and
                      return_pointer > min(start, end)])
        return result

    def get_difference_from_normalised_dates(self, date1, date2):
        try:
            date1 = date1.split('-')
            date2 = date2.split('-')
            date1 = datex(int(date1[0]), int(date1[1]), int(date1[2]))
            date2 = datex(int(date2[0]), int(date2[1]), int(date2[2]))
            return abs((date1-date2).days)
        except Exception:
            return -1


class ClinicalDocument(object):
    """Document representation

    This class synthetically represents a document and all the information
    required in order to accomplish the temporal expression normalisation phase.
    It contains information about: name, path, admission date, discharge date,
    date of the surgical operation, date of the transfer.
    """

    def __init__(self, file_name=None, file_path=None, admission=None,
                 operation=None, transfer=None, discharge=None):
        self.file_name = file_name
        self.file_path = file_path
        self.admission_date = admission
        self.discharge_date = discharge
        self.operation_date = operation
        self.transfer_date = transfer
        self.course_length = -1
        self.discharge_date_not_in_header = False
        self.text = ''

    def __str__(self):
        output = str(self.file_name.split('/')[-1]) + '\t'
        output += 'admission: ' + str(self.admission_date) + '\t'
        output += 'operation: ' + str(self.operation_date) + '\t'
        output += 'transfer: ' + str(self.transfer_date) + '\t'
        output += 'discharge: ' + str(self.discharge_date) + '\t'
        output += 'course_length: ' + str(self.course_length) + '\t'
        output += 'adm:p\t'
        if self.discharge_date_not_in_header:
            output += 'dis:a'
        else:
            output += 'dis:p'
        # output += 'Admission date: ' + ''
        return output


def main():
    path, filename = os.path.split(os.path.abspath(sys.argv[1]))
    analyser = DocumentAnalyser()
    print analyser.analyse(path, filename, False)

if __name__ == '__main__':
    main()
