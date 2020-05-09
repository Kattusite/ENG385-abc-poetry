import collections
import os
import re
import pronouncing
import inflect


in_dir = './abcbook_clean/'
out_dir = './abcbook_rhyme/'


p = inflect.engine()


def itos(i):
    return p.number_to_words(12345, group=2)


def toNumWord(match):
    i = int(match.group(0))
    return itos(i)


def cleanLine(s):
    replacements = {
        # HTML Escapes
        "\&amp;": " and ",

        # Replace fancy quotes with simple quotes
        "[‘’]": "'",
        "[“”]": "\"",

        # Remove line drawing chars:
        "---*": "",

        # Unwind contractions and possessives
        "'d": "ed",
        "y's": "ies",
        #"'s": "s", # breaks he's, that's, ...

        # Sub numbers for word forms
        "\d+": toNumWord,

        # Remove punctuation:
        "[\.\?\!,;:\\\\/\(\)\"\-—\*<>\^\[\]\{\}«\$\&■_]": " ",

        # Replace contiguous whitespace with a single space
        "\s+": " ",
    }

    for u, v in replacements.items():
        s = re.sub(u, v, s)
    return s


def getRhymingParts(s):
    """Given a word as a string, return a list of all of the possible rhyming
    parts that string might have based on its possible pronunciations.

    Return as second value the word, or part of the word, that we used to
    calculate that rhyming part."""

    # 1st pass: If CMUDict directly tells us how to pronounce a word,
    # use that to extract its rhyming part
    s = s.lower()
    phones = pronouncing.phones_for_word(s)
    if phones:
        return [pronouncing.rhyming_part(phone) for phone in phones], s

    # 2nd pass: Find the longest suffix of the word that CMUDict tells us
    # how to pronounce, and use that to extract its rhyming part.
    # (Produces incorrect results for some words! e.g.:
    #           lechugas -> gas
    #           magnanimously -> sly
    n = len(s)
    bestSuffix = None
    # iter over s[-1:], s[-2:], s[-3:], ... s[-(n-1):]
    for i in range(1, n):
        suffix = s[-i:]
        partial = pronouncing.phones_for_word(suffix)

        # track the longest pronouncable suffix
        if partial:
            bestSuffix = suffix
            phones = partial

    if phones:
        print(f"Guessed word: {s} ~~> {bestSuffix}")
        return [pronouncing.rhyming_part(phone) for phone in phones], bestSuffix

    # Final Pass: CMUDict knows nothing about this word (it's probably a typo
    # or non-English). Use the entire, raw word as the rhyming part,
    # adding a star to indicate we couldn't find any CMUDict information
    print("Unknown word: ", s)
    return [s], f"{s}*"


def simplifyRhymeScheme(scheme):
    """Given a list of numbers indicating which rhyme group each of the
    corresponding words belongs to, simplify the list to its canonical form
    (i.e. only introduce a new number once all earlier ones exhausted),
    and convert the numbers to corresponding chars A,B,C,...
    if the scheme can be expressed in 26 distinct letters or fewer

    Due to some words having multiple pronunciations, our rhymeID counter
    might end up skipping numbers; e.g rather than [1, 2, 3, 2, 3, 1, 4, 5]
    we might get:                                  [1, 5, 3, 5, 3, 1, 9, 5]

    To avoid this, condense the scheme back into the simplest possible
    representation.
    """

    if not scheme:
        return []

    # Simplify the scheme so the max is as small as possible, and
    # new indices are introduced in ascending order
    table = {}
    simplified = []
    i = 0
    for val in scheme:
        if val in table:
            simplified.append(table[val])
        else:
            table[val] = i
            simplified.append(i)
            i += 1

    # Try to convert to a nice alphabetical naming for rhyme schemes.
    # If it's too long just use ugly numbers instead
    schemeIDs = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"

    if max(simplified) < len(schemeIDs):
        prettified = [schemeIDs[s]
            for s in simplified]     # [1,2,1,2] ==> [A,B,A,B]
    else:
        prettified = [str(s) for s in simplified]

    return prettified


# For each segment:
#   For each line that isn't the title:
#       Let RP = rhyming part of the last word in the line
#       Add RP to a map of all RPs in the segment. the key is the
#       rhyming part, and the value is A, B, C, D based on whether we've
#       seen it yet in this segment already
#       (actually use 1,2,3,4 so we can increment)

def findRhymes(seg):
    """For a given segment, estimate the rhyme scheme of that segment using the
    rhyming parts of the final word on each line.

    Returns:
    * scheme: the estimated rhyme scheme, as a tuple of strings "A", "B", "C"...
        If there are more than 26 entries in the scheme, they will all be
        labeled using numerical strings instead: "1", "2", "3", ...
    * rhymes: a tuple containing one string for each string in the rhyme scheme.
        The string will be the word (or suffix of a word) that was used to
        estimate the rhyme scheme for this line. Strings ending in "*" indicate
        no nontrivial rhyming information could be derived from that word.
    * tidied: a tuple of strings containing all non-empty lines of text in this
        segment.

    This alg is buggy, but mostly just in weird corner cases
    (lots of possible pronunciations, other languages, etc)

    A more sophisticated algorithm would greatly clarify the flow of logic and
    address all the dicey corner cases we currently ignore"""

    lines = seg.split("\n")

    rhymingParts = collections.defaultdict(lambda: None)

    scheme = []     # The rhyme scheme (e.g. ABAB) as ints
    rhymes = []     # The rhyming words
    tidied = [lines[0]]      # the tidied lines

    # Skip 1st line (assuming it is the letter) --
    # TODO: Warning, what if the rhyme involves the letter? X/Expects, J/say, etc
    i = 0
    for ln in lines[1:]:

        words = cleanLine(ln.lower()).strip().split()
        if not words:
            continue
        # stylistic choice: append ln or cleanLine(ln.lower) ?
        tidied.append(ln)

        lastWord = words[-1]
        rs, wordpart = getRhymingParts(lastWord)

        rhymeFound = None

        for r in rs:
            # Has this rhyme appeared yet?
            rhymeID = rhymingParts[r]

            # If this is the first time we've seen this rhyming part,
            # make a note of it in case it appears again in this segment
            if not rhymeID:
                i += 1
                rhymingParts[r] = i

            else:
                rhymeFound = rhymeID

        # If a rhyme was found, report it. Otherwise add a new distinct rhyme ID
        if rhymeFound:
            scheme.append(rhymeFound)
        else:
            scheme.append(i)
            # BUG: if many pron's are valid, we don't know which of their IDs
            # will eventually end up rhyming a later word, do we?

        # Special case: if the rhymed word was unrecognized, add a star:
        rhymes.append(wordpart)

    scheme = simplifyRhymeScheme(scheme)
    return tuple(scheme), tuple(rhymes), tuple(tidied)


def process_allit():
    """Read all of the input files, finding rhymes in each one. Write an output
    file annotating the original with rhyming information, and return a map
    from file names to the following dict for each file:

    * segs:    A list of strings, one for each segment
    * schemes: A list of rhyme schemes, one for each segment
    * endWords: A list of the words (or subwords) at the end of each line
                that the rhyming algorithm used to check for rhyme scheme
    * tidied: A list of lists of strings, one for each line for each segment
    """

    if not os.path.isdir(out_dir):
        os.mkdir(out_dir)

    allRhymeInfo = {}

    for filename in os.listdir(in_dir):
        if not filename.endswith(".txt"):
            continue

        fileRhymeInfo = {
            "scheme":   [],
            "endWords": [],
            "tidied":   [],
        }

        with open(in_dir + filename, "r", encoding="utf-8") as f:
            txt = f.read()

        # Assume standard line break structure.
        # Split on "\n\n"
        segs = txt.split("\n\n")

        # Print to a new file
        with open(out_dir + filename, "w", encoding="utf-8") as f:
            for seg in segs:
                scheme, rhymingWords, tidiedLines = findRhymes(seg)

                # add info to file's dictionary to be returned
                fileRhymeInfo["segs"].append(seg)
                fileRhymeInfo["scheme"].append(scheme)
                fileRhymeInfo["endWords"].append(rhymingWords)
                fileRhymeInfo["tidied"].append(tidiedLines)

                # write info out to file
                for i, ln in enumerate(tidiedLines):
                    # First line in seg is header; no rhymes
                    if i == 0:
                        print(ln, file=f)
                        continue

                    # Later lines: print original line, plus a rhyme tag
                    w = rhymingWords[i-1]
                    s = scheme[i-1]

                    print(f"{ln:45s}   [{w:^12s}]: ({s})", file=f)
                print(file=f)

        allRhymeInfo[filename] = fileRhymeInfo
    return allRhymeInfo


if __name__ == '__main__':
    process_allit()
