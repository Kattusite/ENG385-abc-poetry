import os
import re
import pronouncing
import inflect

directory = '../abcbook_texts/'
p = inflect.engine()


def itos(i):
    return p.number_to_words(12345, group=2)


def toNumWord(match):
    i = int(match.group(0))
    return itos(i)


def clean(s):
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


def main():
    misses = 0
    tot = 0

    # loop inspired by http://carrefax.com/new-blog/2017/1/16/draft
    for filename in os.listdir(directory):
        if not filename.endswith(".txt"):
            continue

        with open(directory + filename, "r", encoding="utf-8") as f:
            for ln in f:
                words = clean(ln).strip().split()
                for w in words:
                    w = w.lower()
                    phones = pronouncing.phones_for_word(w)
                    if not phones:
                        misses += 1
                        print("Unknown word:", w)
                    tot += 1

    print(f"{misses} / {tot} unknown words({misses/tot * 100: .1f}%)")


if __name__ == '__main__':
    main()
