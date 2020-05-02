# ENG385-abc-poetry
 Simple tools for analyzing poetic devices like rhyme and meter in ABC books, for ENG385.

## Dependencies

* https://github.com/aparrish/pronouncingpy
* NLTK (maybe)
* TQDM (maybe)

```bash
python -m pip install tqdm nltk pronouncing cmudict inflect
```

## Limitations

The CMU Pronouncing Dictionary is in English, and this dictionary is used
to figure out syllable segmentation, so results may be incorrect for non-English
texts.

## Acknowledgments

Ships with version 0.7b of the CMU Pronouncing Dictionary.

## Fallbacks
For texts not formatted for rhyme scheme extraction, instead create a map
of all possible rhyming parts of words in that text, to how frequently that
part occurs.

For example, "The Cat in the Hat saw a Boy with a Bat" would be something like:
"uh": 4 // might wanna exclude the/in/but/of/so/for
"at": 3
"oy": 1
"aw": 1
"ith": 1
