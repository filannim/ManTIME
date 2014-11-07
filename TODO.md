TO-DO List
=======

This document lists all the things I should look more carefully in the future.

- Remove the output produced from Stanford Parse in the stdout/stderr (if
  everything goes ok).
- Correct some morphological gazetteer features according to the English
  grammar. Are all the things called prepositions actually prepositions?
- Probably you can avoid the text variable for Sentence objects.
- Do I really need to load Stanford Core NLP everytime for every document?
- There are some print statement somewhere (WARNING cases). I should use
  something more appropriate for them (log).
- Instead of the settings.py file, I should use the OS.ENVIRONS variable.
  Have a look in CORENLP and others to have a grasp.