TO-DO List
=======

This document lists all the things I should look more carefully in the future.

- [ ] If an element ID contains `_` then the sneaking part in `relation_matrix` won't work.
- [ ] Insert some sample files in input and output folders.
- [ ] Update the code to support the last version of NLTK ParentedTree implementation.
- [ ] The writers should use an xml library instead of writing strings to a file.
- [ ] Installation script.
- [ ] Implement an error measurement framework (in ManTIME class) to get statistics from the models.
- [ ] Implement a shuffle method and cross-fold validation for the data.
- [ ] Do I really need to load Stanford Core NLP everytime for every document? Once (the problem)[https://github.com/dasmith/stanford-corenlp-python/issues/13] with long texts is solved I should switch to the new stanford-core-nlp.
- [ ] Unit-test the code with a proper testing framework (py.test).
- [ ] Comment the code: better and more verbosely using Google Commenting Style.

Done:
- [x] Make the code general with respect to different annotation standards for CRF (IO, BIO, WIO, WBIO, WBIOE, BIOE).
- [x] Can the same two objects be connected by two different types of temporal relations? No.
- [x] Can an event be anchored to two different MAKEINSTANCE tags? Yes. (not supported yet.)
- [x] Move the output folder up.
- [x] Complete the InTextEntity class development.
- [x] Implement features for the temporal relation extraction task looking at my notes from the literature.
- [x] Implement the classifier for Temporal Links.
- [x] Adapt the writers to output temporal links too.
- [x] Implement the feature extractor for Temporal Links.
- [x] Probably some variables in Document and Sentence objects can be deleted.
- [x] What's `id_token` in Word class?
- [x] Do we need EventInstance? Yes, we do.
- [x] In the attribute training phase, the multi-word expressions should be represented as one sample. The features will be merged according to the order of appearance.
- [x] add useful folder (models, output, buffer) in the Git repo
- [x] pickle the num2py arrays and remove the dependency
- [x] Activate the post processing pipeline.
- [x] Fix the logging messages (info, warning, debug)
- [x] The method search_subsequence is called many times. A more adequate ADT should be used.
- [x] Implement a HTML (CSS3) writer (timesheet.js, TimelineJS).
- [x] Make the features as lighter as possible (in terms of storage space).
- [x] show the #_files_processed/#files.
- [x] convert the gazetteers to Unicode.
- [x] Should the attribute data matrix be made of positive samples only?
- [x] Correct some morphological gazetteer features according to the English grammar. Are all the things called prepositions actually prepositions? (ask to Marilena Di Bari)
- [x] Implement the bufferisation at feature level.
- [x] Fix unicode-related bug at utilities.py:76.
- [x] Have a look at argparse ... it's not correct right now.
- [x] Filter out useless features such as female gazetters, male gazetters, US cities. (commented)
- [x] Look carefully at all the features and possibly cut them. (commented)
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