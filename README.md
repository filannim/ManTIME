ManTIME
=======

ManTIME is a Temporal information extraction pipeline for general and clinical domain. Given a piece of English text it is able to recognise and highlight clinical named entities (problems, treatments, clinical departments) and temporal expressions.

The clinical model is based on the ([i2b2/2012 annotation schema](http://www.sciencedirect.com/science/article/pii/S1532046413001032)), whereas the general model is based on the ([TempEval-3 annotation schema](http://arxiv.org/pdf/1206.5333v2.pdf)) Models will be soon available.

##Dependencies

ManTIME is based on the following software components:

* CRF++ 0.57 ([web page](http://crfpp.googlecode.com/svn/trunk/doc/index.html))
* Stanford CoreNLP ([web page](http://nlp.stanford.edu/software/corenlp.shtml#Download)) 
* stanfor-corenlp-python ([web page](https://pypi.python.org/pypi/stanford-corenlp-python/3.3.9))
* nltk ([web page](https://pypi.python.org/pypi/nltk/2.0.4)) + `stopwords` corpus

##Web interface

![ManTIME web interface](http://www.cs.man.ac.uk/~filannim/images/thumb_mantime_demo.png)

You can use ManTIME (TempEval-3 version) via its web server by ([clicking here](http://www.cs.man.ac.uk/~filannim/projects/tempeval-3/)). It currently runs on my personal workstation. If the web service doesn't work that only means I am using my machine to do some intense computing. It will be back online soon. :)

<!--
##Installation

The easiest way to install ManTIME on a Debian-based system is by using the [install-mantime.sh](http://www.cs.man.ac.uk/~filannim/public/install-mantime.sh) script.
-->
##How to use it

Put the input files in a particular folder and run:

    $ python mantime.py test [-ppp] <folder_path> <model_name>

the option -ppp uses the post-processing pipeline on top of the CRFs model.

You can also annotate just a sentence using the following command:

    $ python mantime.py train <folder_path> <model_name>


The script will create a new model folder in `mantime/models/`.

##License

(GPL v2)

Copyright (c) 2012 Michele Filannino, <http://www.cs.man.ac.uk/~filannim/>.

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 2 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.

##Contact
- Email: filannim@cs.man.ac.uk
- Web: http://www.cs.man.ac.uk/~filannim/