ManTIME
=======

Temporal expression extraction pipeline for general domain. System submitted to TempEval-3 challenge.

##Dependencies

You should have installed the following softwares:

* CRF++ 0.57 ([web page](http://crfpp.googlecode.com/svn/trunk/doc/index.html))
* NLTK ([web page](http://nltk.org/))
* TreeTagger ([web page](http://www.ims.uni-stuttgart.de/projekte/corplex/TreeTagger/))
* MBSP CLIPS for Python ([web page](http://www.clips.ua.ac.be/software/mbsp-for-python)) [the code is commented]

##Installation

The easiest way to install ManTIME on Debian-based operating systems is by using the [install-mantime.sh](http://www.cs.man.ac.uk/~filannim/public/install-mantime.sh) script. Thanks to [Prof. Roberts](http://www.dcs.shef.ac.uk/~angus/) (University of Sheffield) for it!

##How to use it

Put the .tml files in a particular folder and run the pipeline.py script.

    $ python pipeline.py <folder_path> [-pp]

the option -pp uses the post-processing pipeline on top of the CRFs model.

You can also annotate just a sentence using the following command:

    $ echo "<sentence>" | python annotate_sentence.py


The script will create a new folder in it, called "annotated", with the annotated .tml documents.

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
