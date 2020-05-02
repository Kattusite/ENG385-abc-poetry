# from tqdm import tqdm


def isVowel(phoneme):
    # vowels are marked with a numerical stress from 0-2, e.g. OY2
    return phoneme[-1] in "012"


class CMUSyl():
    def __init__(self, onset=None, nucleus=None, coda=None):
        """Given tuples of strings for the onset and nucleus, and a single
        string for the nucleus, return a new CMUSyl"""
        self.onset = tuple(onset) if onset is not None else None
        self.nucleus = nucleus
        self.coda = tuple(coda) if coda is not None else None

    def __str__(self):
        pcs = (".".join(self.onset), self.nucleus, ".".join(self.coda))
        return "|".join(pcs)

    def __repr__(self):
        return self.__str__()


class CMUWord():
    def __init__(self, line):
        """Create a new word from a single line of the CMU dictionary file."""
        pcs = line.strip().split("  ")
        self.word = pcs[0].strip()
        self.pron = pcs[1].strip().split(" ")
        self.syls = None    # set by CMUDict once all words are read

    def _wordOnset(self):
        """Return a tuple of strings representing the phonemes at the start of
        this word."""

        # find all phonemes before the first vowel
        onset = []
        for p in self.pron:
            if isVowel(p[-1]):
                break
            onset.push(p)
        return tuple(onset)

    def _syllables(self, validOnsets):
        """Given a set of all valid syllable onsets in a given language,
        split the phonemes of this word into syllables using the maximal onset
        principle, and return the result as a tuple of CMUSyl's"""

        # BUG: Currently doesn't work - assigns all phonemes to coda

        def isValid(onset):
            return len(onset) == 0 or tuple(onset) in validOnsets

        # WARNING: The one-pass algorithm makes the following assumption, which
        # may or may not be true of English:
        # If a language allows a particular syllable onset, then it also allows
        # all suffixes of that onset as valid syllable onsets.

        syls = []

        # One pass syllable chunking algorithm.
        # Iterate backwards over list, adding longest possible onset to rtSyl,
        # with remainder used as coda for left syl.
        L = len(self.pron)  # left-hand index: last phoneme possibly in onset
        R = len(self.pron)  # rt-hand index:  first phoneme possibly in onset
        rtSyl = None        # closest syllable to the right of current phoneme
        for i, p in reversed(list(enumerate(self.pron))):
            if isVowel(p):
                rtSyl = CMUSyl(nucleus=p, coda=self.pron[i+1:R])
                R = L = i
                syls.insert(0, rtSyl)
            elif rtSyl is None:
                # Finished building our onset for this run. wait for new vowel
                continue
            elif i == 0:
                # Made it to start of word. whatever's left is by def. an onset
                rtSyl.onset = tuple(self.pron[:R])

            elif isValid(self.pron[L:R]):
                # Expand onset as much as possible
                L -= 1
            else:
                # This is the maximal onset (under our suffix assumption)
                # Store onset and start building coda
                rtSyl.onset = tuple(self.pron[L+1:R])
                rtSyl = None

        return tuple(syls)

        # Old approach:
        # Extract all vowels as the nucleus of their own syllable
        # syls = tuple([CMUSyl(nucleus=p) for p in self.pron if isVowel(p)])

    def __str__(self):
        if self.syls is None:
            return self.word
        return " / ".join([str(s) for s in self.syls])

    def __repr__(self):
        return self.__str__()


class CMUDict():

    def __init__(self, filename=None):
        """Read the CMUDict in from a file."""
        if filename is None:
            filename = "cmudict-0.7b"

        self.words = {}

        # Read all words from file
        with open(filename, "r") as f:
            for ln in f:

                # Skip comments
                if ln[:3] == ";;;":
                    continue

                w = CMUWord(ln)
                self.words[w.word] = w

        # Find all phoneme sequences that are valid word-onsets
        validOnsets = set()
        for w in self.words.values():
            validOnsets.add(w._wordOnset)

        for w in self.words.values():
            w.syls = w._syllables(validOnsets)

    def __getitem__(self, name):
        return self.words[name.upper()]


def main():
    cmu = CMUDict()

    word = cmu["linguistics"]
    print(word.syls)

    print(cmu["linguistics"])


if __name__ == '__main__':
    main()
