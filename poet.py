from collections import defaultdict
import random


def isVowel(phoneme):
    return phoneme[-1] in "012"

def stress(phoneme):
    if not isVowel(phoneme):
        return None
    return int(phoneme[-1])

def prettySyls(syls):
    return str([str(syl) for syl in syls])

class Syllable:
    def __init__(self, onset, nucleus, coda):
        self.onset = onset
        self.nucleus = nucleus
        self.coda = coda

    def __repr__(self):
        return f"Syllable({self.onset}, {self.nucleus}, {self.coda})"

    def __str__(self):
        return f"{' '.join(self.onset)} {self.nucleus} {' '.join(self.coda)}"

    def __hash__(self):
        return hash( (self.onset, self.nucleus, self.coda) )

    def __eq__(self, oth):
        # Not 100% right but close
        return hash(self) == hash(oth)

class Word:
    def __init__(self, token, name, pron):
        """e.g. token= "-", name="dash", pron=[D AH SH]"""
        self.token = token
        self.name = name
        self.pron = pron

        self.nsyls = 0
        """number of syllables"""

        self.stresses = []
        """stress pattern, as a list of ints 0-2"""

        self._syllables = None   # defined at time of use
        """syllables as lists of phonemes"""

        # syllable stresses are indicated by a digit 0, 1, 2
        for p in pron:
            if isVowel(p):
                self.nsyls += 1
                self.stresses.append(stress(p))

    def __repr__(self):
        return f"Word({self.token}, {self.name}, {self.pron})"

    def __str__(self):
        return f"{{{self.name}: {self.pron}}}"

    def wordOnset(self):
        onset = []
        for p in self.pron:
            if isVowel(p):
                break
            onset.append(p)
        return tuple(onset)

    def hasAlternatingStress(self):
        prev = self.stresses[0]
        for s in self.stresses[1:]:
            if bool(prev) == bool(s):
                return False
        return True

    def hasInitialStress(self):
        return self.stresses[0] != 0

    def hasFinalStress(self):
        return self.stresses[-1] != 0

    @property
    def syllables(self):
        if self._syllables is None:
            raise RuntimeError("Syllables have not yet been initialized")
        return self._syllables

    def parseSyllables(self, onsets):
        # Don't repeat work unnecessarily. Just fill them in lazily
        if self._syllables is not None:
            return

        # split pron into spans of consonants between vowels
        spans = []
        span = []
        nuclei = []
        for i, p in enumerate(self.pron):
            if isVowel(p):
                nuclei.append(p)
                spans.append(span)
                span = []
            else:
                span.append(p)

            if i == len(self.pron)-1:
                spans.append(span)
                span = []

        # Build a syllable for each nucleus, and assign border consonants
        syls = [Syllable((), n, ()) for n in nuclei]
        syls[0].onset = tuple(spans[0])
        syls[-1].coda = tuple(spans[-1])

        # build the largest onset possible, and shunt rest into coda
        # (note i runs from 0 even tho spans is indexed from 1)
        for i, span in enumerate(spans[1:-1]):
            # try using the last i phonemes as an onset of syls[i+1]
            # the rest are a coda of syls[i]
            for start in range(len(span)):
                candidate = tuple(span[start:])
                if candidate in onsets or len(candidate) == 0:
                    if len(candidate) == 0:
                        print("Weird syllable parse on", self.word)
                    syls[i+1].onset = candidate
                    syls[i].coda = tuple(span[:start])
                    break
        self._syllables = syls

    def finalSyllable(self):
        return self.syllables[-1]

    def initSyllable(self):
        return self.syllables[0]

    def rime(self):
        f = self.finalSyllable()
        r = Syllable((), f.nucleus, f.coda)
        return r

class Words:
    def __init__(self, d):
        self.d = d

        self.byNSyls = defaultdict(lambda: {})
        for k, w in self.d.items():
            self.byNSyls[w.nsyls][k] = w

        self._onsets = None
        """Fill in word onsets lazily"""

        self._byFinalSyls = None
        self._byInitSyls = None
        self._byRimes = None

        for _, w in self.d.items():
            w.parseSyllables(self.onsets)

    def __len__(self):
        return len(self.d)

    def __getitem__(self, k):
        return self.d[k.upper()]

    def __contains__(self, k):
        return k in self.d

    def __iter__(self):
        return self.d.__iter__()

    def randomWord(self, v=None, dName=None):
        if dName is None:
            dName = "byNSyls"
        d = getattr(self, dName)
        if d is None:
            raise ValueError(f"{dName} not a property of this object")
        if v is None:
            k = random.choice(list(self.d.keys()))
        elif not v.__hash__:
            raise ValueError(f"Unhashable type v is not allowed: {v}")
        elif len(d[v]) > 0:
            k = random.choice(list(d[v].keys()))
        else:
            raise ValueError(f"No words in provided d with v={v}")

        return self.d[k]

    def randomWordSatisfying(self, f, v=None, dName=None, failAfter=1000):
        """Return a random word w such that f(w) == True.
        Sample from the dictionary specified by dName, with the given v.

        Raise an exception if failAfter attempts are made unsuccessfully"""

        for i in range(failAfter):
            w = self.randomWord(v=v, dName=dName)

            if f(w):
                return w
        raise ValueError(f"Couldn't find a matching word after {failAfter} tries")

    @property
    def onsets(self):
        """Return a list of all onsets represented in the dataset"""
        if self._onsets is not None:
            return self._onsets

        self._onsets = set([])
        for _, w in self.d.items():
            self._onsets.add(w.wordOnset())
        return self._onsets

    @property
    def byFinalSyls(self):
        if self._byFinalSyls is not None:
            return self._byFinalSyls

        self._byFinalSyls = defaultdict(lambda: {})
        for k, w in self.d.items():
            self._byFinalSyls[w.finalSyllable()][k] = w

        return self._byFinalSyls

    @property
    def byInitSyls(self):
        if self._byInitSyls is not None:
            return self._byInitSyls

        self._byInitSyls = defaultdict(lambda: {})
        for k, w in self.d.items():
            self._byInitSyls[w.initSyllable()][k] = w

        return self._byInitSyls

    @property
    def byRimes(self):
        if self._byRimes is not None:
            return self._byRimes

        self._byRimes = defaultdict(lambda: {})
        for k, w in self.d.items():
            self._byRimes[w.rime()][k] = w

        return self._byRimes

    # BUG: Rhymes might use more than just the final syllable.
    def rhyme(self, w):
        if type(w) == type(""):
            w = w.upper()
            if w not in self.d:
                raise ValueError(f"{w} not a recognized word!")
            w = self.d[w]

        rime = w.rime()
        return self.randomWord(rime, dName="byRimes")

    def iambicPenatameterLine(self, rime=None, nsyls=10):
        """Create a line of the spec'd #syls ending in rime, with alternating
        stressed/unstressed syllables"""

        # really naive slow implementation
        ws = []
        n = 0

        def rStressAligned(w):
            return w.hasFinalStress() and w.hasAlternatingStress()

        # If we need to rhyme the last word figure it out first
        # BUG possibly: The stress pattern is not guaranteed to be aligned with the
        # first several words and the final word., e.g.
        # .X .X .X .X. .X is not an iambic stress pattern but could be generated
        lastWord = None
        if rime is not None:
            lastWord = self.randomWordSatisfying(rStressAligned, v=rime, dName="byRimes")
            nsyls -= lastWord.nsyls

        initStress = False
        while True:
            def stressAligned(w):
                return initStress == w.hasInitialStress() and w.hasAlternatingStress()

            w = self.randomWordSatisfying(stressAligned)
            ws.append(w)
            n += w.nsyls

            if n >= nsyls:
                break

        # Append the final rhyming word
        if lastWord is not None:
            ws.append(lastWord)

        return " ".join([w.name for w in ws])

    def unmeteredLine(self, nsyls=5):

        ws = []
        n = 0

        while True:
            w = self.randomWord()
            if n + w.nsyls > nsyls:
                continue
            ws.append(w)
            n += w.nsyls

            if n == nsyls:
                break
        return " ".join([w.name for w in ws])

    def haiku(self):
        return [
            self.unmeteredLine(5),
            self.unmeteredLine(7),
            self.unmeteredLine(5),
        ]

    def printLines(self, nlines=5, rimes=None, nsyls=10):
        if type(rimes) != type([]):
            rimes = [rimes] * nlines
        for i in range(nlines):
            print(self.iambicPenatameterLine(rime=rimes[i], nsyls=nsyls))



def readWords(inFile="cmudict/cmudict-0.7b"):
    """Read in the CMUDICT file and return a dictionary, mapping tokens to
    their Word objects."""

    d = {}

    with open(inFile, "r") as f:
        for ln in f:

            # Ignore commented lines
            if ln[:3] == ";;;":
                continue

            pcs = ln.strip().split("  ")
            if len(pcs) != 2:
                print("Error: couldn't split line:", pcs)
                continue

            token = pcs[0]
            name  = pcs[0]
            pron  = pcs[1].split(" ")

            # split symbolic tokens off token names
            # e.g. ;SEMI-COLON --> (; , SEMICOLON)
            if not ln[0].isalnum():
                token = token[0]
                name  = name[1:]

            d[name] = Word(token, name, pron)
    return Words(d)

def rhymeTest(ws, w):
    print(f"==== words rhyming with {w} ====")
    for i in range(10):
        print(ws.rhyme(w))

def main():
    ws = readWords()

    # ws.parseAllSyllables()
    # for i in range(1,8):
    #     print(f"===== {i} syl words =====")
    #     for _ in range(4):
    #         w = ws.randomWord(v=i)
    #         print(w.name, w.pron, prettySyls(w.syllables))
            # print(ws.randomWord(nsyls=i))

    # w = ws["trinity"]
    # print(w, w.rime())

    # rhymeTest(ws, "bat")
    # rhymeTest(ws, "free")
    # rhymeTest(ws, "raven")

    # w = ws["careen"]
    # r = w.rime()
    # ws.printLines(rimes=r)

    # print("\n\n")
    h = ws.haiku()
    for ln in h:
        print(ln)

if __name__ == '__main__':
    main()
