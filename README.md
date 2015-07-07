ManTIME
=======

ManTIME is a Temporal information extraction pipeline for general and clinical domain. Given a piece of English text it is able to recognise and highlight clinical named entities (problems, treatments, clinical departments) and temporal expressions.

The clinical model is based on the ([i2b2/2012 annotation schema](http://www.sciencedirect.com/science/article/pii/S1532046413001032)), whereas the general model is based on the ([TempEval-3 annotation schema](http://arxiv.org/pdf/1206.5333v2.pdf)) Models will be soon available.

##Dependencies

ManTIME is based on the following software components:

* CRF++ 0.57 ([web page](http://crfpp.googlecode.com/svn/trunk/doc/index.html))
* Stanford CoreNLP ([web page](http://nlp.stanford.edu/software/corenlp.shtml#Download))
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

Copyright (c) 2012-2015, Michele Filannino
All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:

1. Redistributions of source code must retain the above copyright notice, this
   list of conditions and the following disclaimer.
2. Redistributions in binary form must reproduce the above copyright notice,
   this list of conditions and the following disclaimer in the documentation
   and/or other materials provided with the distribution.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR
ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
(INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
(INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

The views and conclusions contained in the software and documentation are those
of the authors and should not be interpreted as representing official policies,
either expressed or implied, of the FreeBSD Project.

##Contact
- Email: filannim@cs.man.ac.uk
- Web: http://www.cs.man.ac.uk/~filannim/