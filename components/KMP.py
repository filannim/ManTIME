#!/usr/bin/python
#
#	Copyright 2012 Michele Filannino
#
#	gnTEAM, School of Computer Science, University of Manchester.
#	All rights reserved. This program and the accompanying materials
#	are made available under the terms of the GNU General Public License.
#	
#	author: Michele Filannino
#	email:  filannim@cs.man.ac.uk
#	
#	This work is part of TempEval-3 challenge.	
#	For details, see www.cs.man.ac.uk/~filannim/

from __future__ import generators

def KMP(text, pattern,end=False,printIt=False):
	"""This code has been developed by David Eppstein, UC Irvine, 1 Mar 2002
	source: http://code.activestate.com/recipes/117214/"""
	"""Yields all starting positions of copies of the pattern in the text.
	Calling conventions are similar to string.find, but its arguments can be
	lists or iterators, not just strings, it returns all matches, not just
	the first one, and it does not need the whole text in memory at once.
	Whenever it yields, it will have read the text exactly up to and including
	the match that caused the yield."""

	if printIt:
		print 'KMP-----------'
		print text
		print pattern

	# allow indexing into pattern and protect against change during yield
	pattern = list(pattern)

	# build table of shift amounts
	shifts = [1] * (len(pattern) + 1)
	shift = 1
	for pos in range(len(pattern)):
		while shift <= pos and pattern[pos] != pattern[pos-shift]:
			shift += shifts[pos-shift]
		shifts[pos+1] = shift

	# do the actual search
	startPos = 0
	matchLen = 0
	for c in text:
		while matchLen == len(pattern) or matchLen >= 0 and pattern[matchLen] != c:
			startPos += shifts[matchLen]
			matchLen -= shifts[matchLen]
		matchLen += 1
		if matchLen == len(pattern):
			if end:
				if printIt: print [startPos, startPos+len(pattern)-1]
				yield startPos, startPos+len(pattern)-1
			else:
				yield startPos