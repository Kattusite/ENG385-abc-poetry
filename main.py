from clean_text import process_cleaning
from find_rhymes import process_rhymes
from find_allit import process_allit
from find_meter import process_meter
from summarize_text import process_summary

from collections import Counter


def main():
    # Clean the raw input files
    process_cleaning()

    # Find rhymes
    rhymeInfo = process_rhymes()

    # Find allit
    # Warning, some allit is phonetic, other allit is orthographic

    # Find meter

    # Now that all info has been found, do a little analysis + summary

    scheme = rhymeInfo["abcfun.txt"]["scheme"]
    c = Counter(scheme)
    print(c.most_common(1))

    process_summary(rhymeInfo, None, None)


if __name__ == '__main__':
    main()
