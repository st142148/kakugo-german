Trying to fix the german language import of [Kakugo](https://github.com/blastrock/kakugo), a learning app for japanese Kanji and Vocabulary.
Dictionary file taken from [Version 1.36.2](https://github.com/blastrock/kakugo/releases/tag/1.36.2). It uses JMDICT which in turn uses Wadoku for the german translation.

---
#### Credits
- dict.sqlite: [Kakugo](https://github.com/blastrock/kakugo), based on [JMDict](https://www.edrdg.org/jmdict/j_jmdict.html) and [kanjidic](http://www.edrdg.org/kanjidic/kanjidic.html)
- wadokudict2: [Wadoku Projekt](https://www.wadoku.de/wiki/display/WAD/Wadoku+Projekt)

---
#### Kanjis
##### Stats for the original file
- 3265 total entries
- 146 false entries for "unregelmäsige Zähne" ("irregular teeth")
- 573 entries without german translations and an unknown number of wrong translation stemming from the fact that wadoku is not meant for kanji lookups.


##### Possible fixes
- remove irregular teeth (ouch)
- take the english kanji definitions and translate them
- alternatively parse Remembering the Kanji ("Die Kanji lernen und behalten") for those who bought the ebook

---
#### Words
##### Stats for the original file
- 8780 total entries
- 106 entries without translation
- many entries have only one translation, leaving out nuances which can lead to confusion (i. e. 局, 公務, 役所, 係 all being translated just as "Amt")

##### Possible fixes
- querry Wadoku myself, but better

##### Solution
- querry Wadoku

##### Some statistics for the wadoku extract
- 102 entries without german translation
- 604 entries matched 1:1, meaning wadoku gave the same single word/phrase as in the database
- 4592 times the first word matched exactly, but wadoku provided variations
- 6492 times the old definiton is found within the first three wadoku definitions
- 上げる [あげる] has the most variations with 448
- 来る [くる] has the longest definition counting 313 characters
