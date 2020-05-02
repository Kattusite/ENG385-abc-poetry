import os
import re
import pronouncing
import inflect

in_dir = './abcbook_texts/'
out_dir = './abcbook_clean/'


def cleaner(s, res):
    """A helper function for cleaning individual texts that e.g. need line breaks
    added in. I've been calling it manually in IDLE."""

    s = s.strip()
    for (src, tgt) in res:
        s = re.sub(src, tgt, s)

    lns = s.split("\n")
    for ln in lns:
        print(ln.strip())


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
        lens.sort()
        qrt1 = lens[len(lens) // 4]
        # and seg.count("\n") >= avgLen # avg length check breaks a lot
        longSegs = [seg for seg in segs if seg]
        # longSegs = [seg for seg in segs if seg and seg.count("\n") >= qrt1]
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


if __name__ == '__main__':
    main()
