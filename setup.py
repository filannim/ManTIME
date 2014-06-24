from setuptools import setup

with open('README.md') as fh:
	long_description = fh.read()

setup(
	name = 'ManTIME',
	version = '0.1.0',
	description = 'Temporal Expression Extraction software',
	long_description = long_description,
	author = 'Michele Filannino',
	author_email = 'filannim@cs.man.ac.uk',
	url = 'https://github.com/filannim/ManTIME',
	packages = ['mantime'],
	install_requires = ['ntlk', 'lxml'],
	classifiers = [
		'Programming Language :: Python',
		'Programming Language :: Python 2.7'
	],
)