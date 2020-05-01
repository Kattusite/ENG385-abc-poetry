

def rhymes(wordA, wordB):
    """Return True iff wordA rhymes with wordB else False"""

    if wordA in CMUDict and wordB in CMUDict:
        # Return true if any of the possible pronunciations of A rhyme with
        # any of the possible pronunciations of B
        pass

    # Step 1: Check how many words aren't in CMUDict and see if this is a real
    # case we need to concern ourselves with.

    # Try to split words that aren't in CMUDict into smaller chunks that are
