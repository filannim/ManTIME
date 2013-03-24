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

import sys

class CRF(object):

	def __init__(self, corpus):
		self.feature_names = []
		self.class_names = []
		#self.corpus = self.loadcorpus(corpus)

	def loadcorpus(self, corpus):
		raw_lines = [line.strip() for line in open(corpus, 'r').readlines()]
		
		# HEADER
		header = raw_lines[0].strip().split('\t')
		self.feature_names = [feature for feature in header if not feature.isupper()]
		self.class_names = [feature for feature in header if feature.isupper()]
		
		#sentences = []
		#rows = raw_lines[1:].split([''])
		#for line in raw_lines[1:]:
		#	if line.split('\t')

	def generate_template(self):
		num_of_features = 92
		template = set()
		for i in [0]+range(9,41)+range(45,70):
			template.add('%%x[0,%d]' % (i))
			template.add('%%x[-1,%d]' % (i))
			template.add('%%x[-2,%d]' % (i))
			template.add('%%x[1,%d]' % (i))
			template.add('%%x[2,%d]' % (i))
			template.add('%%x[-2,%d]/%%x[-1,%d]' % (i,i))
			template.add('%%x[-1,%d]/%%x[0,%d]' % (i,i))
			template.add('%%x[0,%d]/%%x[1,%d]' % (i,i))
			template.add('%%x[-1,%d]/%%x[0,%d]/%%x[1,%d]' % (i,i,i))
			template.add('%%x[0,%d]/%%x[1,%d]/%%x[2,%d]' % (i,i,i))
			#SUPER LIGHT
			template.add('%%x[1,%d]/%%x[2,%d]' % (i,i))
			template.add('%%x[-2,%d]/%%x[-1,%d]/%%x[0,%d]' % (i,i,i))
			template.add('%%x[-1,%d]/%%x[1,%d]' % (i,i))
			template.add('%%x[-2,%d]/%%x[2,%d]' % (i,i))
			# for m in sorted(list(set(range(num_of_features)) - set([i]))):
			#  	template.add('%%x[0,%d]/%%x[0,%d]' % (i,m))
			#  	template.add('%%x[-1,%d]/%%x[0,%d]' % (i,m))
			#  	template.add('%%x[-1,%d]/%%x[0,%d]' % (m,i))
			#  	template.add('%%x[-2,%d]/%%x[-1,%d]' % (i,m))
			#  	template.add('%%x[-2,%d]/%%x[-1,%d]' % (m,i))
			#  	template.add('%%x[0,%d]/%%x[1,%d]' % (i,m))
			#  	template.add('%%x[0,%d]/%%x[1,%d]' % (m,i))
			#  	template.add('%%x[1,%d]/%%x[2,%d]' % (i,m))
			#  	template.add('%%x[1,%d]/%%x[2,%d]' % (m,i))
		for index, template in enumerate(list(sorted(template))):
			yield 'U%07d:' % index + template

def main():
	crf = CRF(sys.argv[1])
	for line in crf.generate_template():
		print line

if __name__ == '__main__':
	main()
