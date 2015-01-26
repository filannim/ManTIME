TO-DO List
=======

This document lists all the things I should look more carefully in the future.

- [ ] In the attribtue training phase, the multi-word expressions should be
represented as one sample. The features will be merged according to the order
of appearance.
- [ ] Fix unicode-related bug at utilities.py:76.
- [ ] Implement the feature extractor for Temporal Links.
- [ ] Implement the classifier for Temporal Links.
- [ ] The writers should use an xml library instead of writing strings to a file.
- [ ] Adapt the writers to output temporal links too.
- [ ] Look carefully at all the features and possibly cut them.
- [ ] Make the features as lighter as possible (in terms of storage space).
- [ ] Filter out useless features such as female gazetters, male gazetters, US cities.
- [ ] Correct some morphological gazetteer features according to the English grammar. Are all the things called prepositions actually prepositions?
- [ ] Do I really need to load Stanford Core NLP everytime for every document? Once (the problem)[https://github.com/dasmith/stanford-corenlp-python/issues/13] with long texts is solved I should switch to the new stanford-core-nlp.
- [ ] Probably you can avoid some variables for Document and Sentence objects.
- [ ] Group the annotations token based at sentence level.
- [ ] Should the attribute data matrix be made of positive samples only?
- [ ] Implement an error method to get statistics from the models.
- [ ] Implement a shuffle method and cross-fold validation for the data.
- [ ] Comment the code: better and more verbously using Google Commenting Style.
- [ ] Have a look at argparse ... it's not correct right now.
- [ ] Implement a HTML (CSS3) writer.
- [ ] Extend the models to the annotations. 
- [x] Instead of the settings.py file, use OS.ENVIRONS variable.
- [x] Implement the i2b2 reader.
- [x] Implement the i2b2 writer.
- [x] Implement a caching system for Stanford Core NLP.
- [x] Remove the output produced by CRF++ in the training phase.
- [x] Integrate (Norma)[https://github.com/filannim/timex-normaliser].
- [x] Introduce model folders instead of files.
- [x] Fix and connect the post-processing pipeline.
- [x] Attributes models should include identification feature (heavier but hopefully better).
- [x] Split identification models (TIMEXes and EVENTs).
- [x] CRF based attributes extraction.
- [x] There are some print statement somewhere (WARNING cases). I should use
  something more appropriate for them (log).
- [x] Remove the output produced from Stanford Parser in the stdout/stderr (if
  everything goes ok).
- [x] Implement AttributeDataMatrix writer.  
- [x] Implement TempEval-3 writer.
- [x] Implement TempEval-3 reader.
- [x] Implement the classifier for events and timexes.
- [x] Implement the universal feature extractor for events and timexes.
- [x] Find documentation about how to comment the code so that nice Python-doc
  style web pages can be automatically generated.
- [x] Love ManTIME and refactor it!