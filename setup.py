import os
from setuptools import setup
from setuptools import find_packages


def read(fname):
    '''Utility function to read the README file.

    '''
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(name='ManTIME',
      version='0.1.0',
      author='Michele Filannino',
      author_email='filannim@cs.man.ac.uk',
      description='Temporal Expression Extraction software',
      long_description=read('README.md'),
      url='https://github.com/filannim/ManTIME',
      packages=find_packages(),
      install_requires=['nltk==2.0.5',
                        'jsonrpclib>=0.1.3',
                        'pexpect>=3.1',
                        'xmltodict>=0.9.0'],
      classifiers=['Development Status :: 3 - Alpha',
                   'Environment :: Console',
                   'Intended Audience :: Healthcare Industry',
                   'Intended Audience :: Science/Research',
                   'License :: OSI Approved :: BSD License',
                   'Natural Language :: English',
                   'Operating System :: Unix',
                   'Operating System :: MacOS :: MacOS X',
                   'Programming Language :: Python',
                   'Programming Language :: Python 2.7',
                   'Programming Language :: Java',
                   'Topic :: Scientific/Engineering :: Artificial Intelligence',
                   'Topic :: Scientific/Engineering :: Information Analysis',
                   'Topic :: Text Processing :: Linguistic',
                   'Topic :: Text Processing :: Markup'])
