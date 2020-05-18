function maj(r) {
  if (!r.isFormatted) return 1;
  if (!r.isRhyming) return 2;
  return 0;
}

function compare(sortBy) {
  return (a,b) => {
    let x = a[sortBy];
    let y = b[sortBy];

    // "major" index for binning entries at a high level.
    // entries in lower indexed bins appear before higher ones
    // 0 for rhyming, 1 for unformatted, 2 for not rhyming
    let amaj = maj(a);
    let bmaj = maj(b);

    if (sortBy == "scheme") {
      if (typeof(x) == typeof([])) x = x.join("");
      if (typeof(y) == typeof([])) y = y.join("");

      let dmaj = amaj - bmaj;
      if (dmaj != 0) return dmaj;

      // break ties on rhyme scheme length
      let d = x.length - y.length;
      if (d != 0) return d;

      // finally lexicographically sort.
      return x.localeCompare(y);
    }

    if (typeof(x) == typeof("")) return x.localeCompare(y);
    else return x - y;
  };
}

function displayResults(sortBy) {
  if (!sortBy) sortBy = "default";

  let $results = $("#results");

  // clear existing entries
  $results.html("");

  let rs = [];

  for (let [book, res] of Object.entries(results)) {
    res.book = book;
    rs.push(res);
  }

  if (sortBy != "default") {
    rs.sort( compare(sortBy));
  }

  for (let r of rs) {
    el = makeResult(r.book, r);
    $results.append(el);
  }
}

function newEl(tag) {
  return document.createElement(tag);
}

function div() {
  return newEl("div");
}

function progressBar(percentage) {
  let d = div();
  $(d).css("width", "95%");
  $(d).css("position", "relative");

  let label = newEl("span");
  $(label).addClass("bar-label");
  $(label).text(`${percentage}%`);
  $(d).append(label);

  let bar = div();
  $(bar).addClass("bar");
  $(bar).css("width", `${percentage}%`);
  $(d).append(bar);

  return d;
}

function makeResult(book, res) {
  console.log(res);

  let d = div();
  $(d).addClass("result")

  // Build title
  let title = newEl("h3");
  book = book.replace(/.txt/g, "").replace(/_/g, " ");
  $(title).text(book);
  $(d).append(title);

  // Add year
  // $(d).append(newEl("br"));
  let year = newEl("h4");
  $(year).text(res.year);
  if (res.year == -1) $(year).text("???");
  $(d).append(year);

  // Add hr
  // $(d).append(newEl("hr"));

  let status = "";
  let rhyming = false;
  if (!res.isFormatted) {
    $(d).addClass("unsure");
    status = "Oh no! <br><br> This book's data wasn't formatted quite right. We can't tell if it rhymes or not!";
  } else if (res.isRhyming) {
    $(d).addClass("rhyming");
    status = "Rhymes!";
    rhyming = true;
  } else {
    $(d).addClass("norhyming");
    status = "No rhymes here!";
  }
  let statusSpan = newEl("span");
  $(statusSpan).html(status);
  $(d).append(statusSpan);

  // Add XX% of the book uses an XYZ rhyme scheme
  if (rhyming) {
    $(d).append(newEl("br"));
    $(d).append(newEl("br"));

    let container = div();
    $(container).addClass("bar-container");

    let prevSpan1 = newEl("span");
    let prevSpan2 = newEl("span");
    let scheme = res.scheme.join("");
    // Rhyme scheme of ABBAB
    // appears in 78% of lines
    // $(prevSpan).text(`${res.prevalence}% of lines have ${scheme} rhyme scheme`);
    $(prevSpan1).html(`Rhyme scheme of <b>${scheme}</b>`);
    $(prevSpan2).text(`appears in ${res.prevalence}% of lines`);

    $(container).append(prevSpan1);
    $(container).append(newEl("br"));
    $(container).append(prevSpan2);

    let bar = progressBar(res.prevalence);
    $(container).append(bar);

    $(d).append(container);
  }
  // Add a progress bar filled up XX% of the way.


  return d;
}

displayResults();
