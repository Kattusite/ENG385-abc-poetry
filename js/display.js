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
