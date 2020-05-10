import json
from collections import Counter
from scipy import stats

def main():
    with open("results/results.json", "r") as f:
        results = json.load(f)

    n = len(results)

    unformatted = {name: data for name, data in results.items() if not data["isFormatted"]}
    formatted = {name: data for name, data in results.items() if data["isFormatted"]}

    rhyming = {name: data for name, data in formatted.items() if data["isRhyming"]}
    unrhyming = {name: data for name, data in formatted.items() if not data["isRhyming"]}

    print(rhyming)

    print(f"{len(results)} books processed in total.")
    print(f"{len(unformatted)} unformatted. Of {len(formatted)} remaining:")
    print(f"{len(rhyming)} rhymed, and {len(unrhyming)} did not.")

    print(f"\nOf the {len(rhyming)} that rhymed:")

    schemes = ["".join(r["scheme"]) for _, r in rhyming.items()]
    c = Counter(schemes)

    print("the most common schemes were:")
    for x in c.most_common(None):
        print(x)


    ps = [int(r["prevalence"]) for _, r in rhyming.items()]
    print("\nwith prevalences:")

    print(stats.describe(ps))

    ps.sort()
    print("median", ps[len(ps)//2])


    # print(results)


if __name__ == '__main__':
    main()
