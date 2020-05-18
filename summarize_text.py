from collections import Counter
import json
import os
from book_data import books

in_dir = './abcbook_clean/'
out_dir = './abcbook_summary/'

json_out = './results/'


def summarize_formatting(seg):
    """Return True if we believe the input to be well-formatted, and therefore
    results to be reliable, or False if we believe the input not to be well-
    formatted, and therefore results to be unreliable"""
    segs = [s for s in seg if s]

    # If there are 3 or fewer segments there probably aren't line breaks
    # added at proper intervals
    return len(segs) > 3


def summarize_rhyming(rhyme):

    # Figure out the most common rhyme scheme
    schemes = [s for s in rhyme["scheme"] if s]
    c = Counter(schemes)

    nTotal = len(schemes)
    if nTotal == 0:
        return False, 100, ("A")

    common = c.most_common(1)
    (mostCommonScheme, nMatching) = common[0]

    isRhymingLikely = len(mostCommonScheme) > len(set(mostCommonScheme))
    prevalence = round((nMatching / nTotal) * 100)

    # TODO: Come up with some notion of prevalence / confidence
    # Prevalence being how many of the segments seem to rhyme,
    # and confidence being how sure we were that those segments did rhyme.
    # (more points for more repetitive rhyme schemes, less points for
    # very long, non-repeating schemes that happen to have duplicates)
    #

    return isRhymingLikely, prevalence, mostCommonScheme


def process_summary(rhymes, meters, allits):
    """Process the given rhymes, meters, and allits.

    """

    nmisses = 0

    unformatted = []
    results = {}

    for filename in os.listdir(in_dir):
        if not filename.endswith(".txt"):
            continue

        result = {}

        # Analyze the rhymes
        rhyme = rhymes[filename]
        isRhyming, prevalence, scheme = summarize_rhyming(rhyme)
        isFormatted = summarize_formatting(rhyme["segs"])

        result["isFormatted"] = isFormatted
        result["isRhyming"] = isRhyming
        result["prevalence"] = prevalence
        result["scheme"] = scheme

        if isFormatted:
            print(f"===== {filename} =====")
            s = "does not use" if not isRhyming else "uses"
            print(f"{s} rhyming with {prevalence}% prevalence")
            print(f"rhyme scheme is probably: {''.join(scheme)}\n")
        else:
            unformatted.append(filename)

        # Analyze the meters
        pass

        # Analyze the allits
        pass

        # with open(in_dir + filename, "r", encoding="utf-8") as f:
        #     txt = f.read()


        # Read and store the book metadata into the result
        if filename not in books:
            result["year"] = "-1"
            nmisses += 1
        else:
            metadata = books[filename]
            result = {**result, **metadata}

        result["year"] = int(result["year"])

        # Store the data for this book in the list of results
        results[filename] = result

        # Write a summary file, one per book.

    # Report unformatted files
    n = len(unformatted)
    print(f"{n} results suppressed due to improper file formatting...")
    print(f"{nmisses} results had no associated year...")

    # Also write a single JSON file summarizing for all books
    if not os.path.isdir(json_out):
        os.mkdir(json_out)
    with open(json_out + "results.json", "w") as f:
        json.dump(results, f, ensure_ascii=True, indent=2)

    # Also write a copy as JavaScript for displaying in a website
    with open("js/results.js", "w") as f:
        print("const results = ", end="", file=f)
        json.dump(results, f, ensure_ascii=True, indent=2)


if __name__ == '__main__':
    process_summary()
