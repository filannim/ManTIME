#!/usr/bin/python
#
#   Copyright 2012-2015 Michele Filannino
#
#   gnTEAM, School of Computer Science, University of Manchester.
#   All rights reserved. This program and the accompanying materials
#   are made available under the terms of the GNU General Public License.
#
#   author: Michele Filannino
#   email:  filannim@cs.man.ac.uk
#
#   For details, see www.cs.man.ac.uk/~filannim/

from datetime import datetime
from flask import Flask, render_template, request
import re

from mantime.mantime import ManTIME
from mantime.readers import TextReader
from mantime.writers import TempEval3Writer
from mantime.attributes_extractor import FullExtractor

app = Flask("ManTIME")
app.debug = False

MANTIME = ManTIME(reader=TextReader(), writer=TempEval3Writer(), pipeline=True,
                  extractor=FullExtractor(), model_name='TBAQ_full_training')


@app.route('/', methods=['POST'])
def index():
    now = datetime.now()
    utterance = now.strftime("%A, %d %B %Y")
    sentence = request.form['sentence']
    result = MANTIME.label(sentence)[0]
    print sentence, result
    return render_template('mantime.html', sentence=sentence, result=result,
                           utterance=utterance)

app.run(host="130.88.192.69", port=4001, use_reloader=True)
