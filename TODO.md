TO-DO List
=======

This document lists all the things I should look more carefully in the future.

- [ ] Have a look at argparse ... it's a mess right now
- [ ] Introduce model folders instead of files
- [ ] Remove the output produced by CRF++ in the training phase
- [ ] Better and more verbously comment the code
- [x] Remove the output produced from Stanford Parse in the stdout/stderr (if
  everything goes ok).
- [ ] Correct some morphological gazetteer features according to the English
  grammar. Are all the things called prepositions actually prepositions?
- [ ] Probably you can avoid the text variable for Sentence objects.
- [ ] Do I really need to load Stanford Core NLP everytime for every document?
  Once (the problem)[https://github.com/dasmith/stanford-corenlp-python/issues/13] with long texts is solved I should switch to the new stanford-core-nlp.
- [x] There are some print statement somewhere (WARNING cases). I should use
  something more appropriate for them (log).
- [ ] Instead of the settings.py file, I should use the OS.ENVIRONS variable.
  Have a look in CORENLP and others to have a grasp.
- [x] Find documentation about how to comment the code so that nice Python-doc
  style web pages can be automatically generated.
- [x] Love ManTIME!