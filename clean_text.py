import os
import re
import pronouncing
import inflect

in_dir = './abcbook_texts/'
out_dir = './abcbook_clean/'


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


def cleanText(txt):
    """Cleans an entire multiline text (as a string) and returns the clean string.

    abcs_of_forest_fire_prevention is the gold standard.

    LETTER
    line1...
    line2...
    line3...
    line4...

    LETTER...
    """

    # Replace multi-newline with
    txt = re.sub("\r?\n(\r?\n)+", "\n\n", txt)
    return txt


def main():

    if not os.path.isdir(out_dir):
        os.mkdir(out_dir)

    for filename in os.listdir(in_dir):
        if not filename.endswith(".txt"):
            continue

        with open(in_dir + filename, "r", encoding="utf-8") as f:
            txt = f.read()

        # Fix line breaks if possible
        txt = cleanText(txt)

        # with open(out_dir + filename, "w", encoding="utf-8") as f:
        #     f.write(txt)

        # Assume standard line break structure.
        # Split on "\n\n"
        segs = txt.split("\n\n")

        # Drop segments that are significantly shorter than average (titles, metadata)
        lens = [seg.count("\n") for seg in segs]
        avgLen = sum(lens) / len(lens)
        # and seg.count("\n") >= avgLen # avg length check breaks a lot
        longSegs = [seg for seg in segs if seg]
        # Sort remaining segments alphabetically to reorder ABCs
        longSegs.sort()

        # Extract the letter if possible
        # TODO: If first line is just one word, let that be the section title
        try:
            letters = [seg[0] for seg in longSegs]
        except:
            print("some segs too short on", filename)
            print(longSegs)

        # Print to a new file
        with open(out_dir + filename, "w", encoding="utf-8") as f:
            for i, seg in enumerate(longSegs):
                lns = seg.split("\n")

                # Skip the title line
                print(letters[i], file=f)
                for ln in lns:
                    if len(ln) > 3:
                        print(ln.strip(), file=f)
                print(file=f)

        # Write code to, for each segment:
        #   For each line that isn't the title:
        #       Let RP = rhyming part of the last word in the line
        #       Add RP to a map of all RPs in the segment. the key is the
        #       rhyming part, and the value is A, B, C, D based on whether we've
        #       seen it yet in this segment already
        #       (actually use 1,2,3,4 so we can increment)
        #


if __name__ == '__main__':
    main()
