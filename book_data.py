import csv, json, re

titles_file = "abcbook_orig/____titles.csv"
data_file   = "abcbook_orig/book_metadata.json"

filenames = {}
books = {}

def standardize(title):
    """Convert titles to a standardize form."""

    # annoying special cases:
    special_cases = ["eatables", "allegorical"]
    for s in special_cases:
        if s in title.lower():
            return s

    # yeah technically this eliminates all A's but whatever
    # for our purposes the mapping need not be invertible
    title = re.sub("or,.*", "", title)      # or ...
    title = re.sub("&", "and", title)       # & => and
    title = re.sub("(the|an|a)", "", title, flags=re.IGNORECASE)

    title = re.sub("[\.,;'’\" ]", "", title)  # punctuation
    title = re.sub(":.*", "", title)        # : ...

    return title.lower()

with open(titles_file, "r", encoding="utf-8") as f:
    r = csv.reader(f)
    for row in r:
        filename = row[1]
        title = standardize(row[0])

        # print(title)

        filenames[title] = filename

# for k in filenames:
#     print(k)

nmiss=0
nhit=0

with open(data_file, "r", encoding="utf-8") as f:
    r = json.load(f)
    for row in r:
        title = standardize(row["title"])
        if title not in filenames:
            print(f"~~|{title}| not in filenames")
            nmiss += 1
            continue
        else:
            # print(f"{title} found")
            nhit += 1
        filename = filenames[title]
        books[filename] = {**row}

print(f"{nmiss} filenames unrecognized, {nhit} found")

# for k, v in books.items():
#    print(k, v["title"])
#
# exit()
