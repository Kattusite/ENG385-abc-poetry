function displayResults() {
  let $results = $("#results");
  for (let [book, res] of Object.entries(results)) {
    el = makeResult(book, res);
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

  // Add hr
  // $(d).append(newEl("hr"));

  let status = "";
  let rhyming = false;
  if (!res.isFormatted) {
    $(d).addClass("unsure");
    status = "Unsure about rhyming... not enough data!";
  } else if (res.isRhyming) {
    $(d).addClass("rhyming");
    status = "Rhymes!";
    rhyming = true;
  } else {
    $(d).addClass("norhyming");
    status = "Doesn't rhyme :(";
  }
  let statusSpan = newEl("span");
  $(statusSpan).text(status);
  $(d).append(statusSpan);

  // Add XX% of the book uses an XYZ rhyme scheme
  if (rhyming) {
    $(d).append(newEl("br"));
    $(d).append(newEl("br"));

    let container = div();
    $(container).addClass("bar-container");

    let prevSpan = newEl("span");
    let scheme = res.scheme.join("");
    $(prevSpan).text(`${res.prevalence}% of lines have ${scheme} rhyme scheme`);
    $(container).append(prevSpan);

    let bar = progressBar(res.prevalence);
    $(container).append(bar);

    $(d).append(container);
  }
  // Add a progress bar filled up XX% of the way.


  return d;
}

displayResults();
