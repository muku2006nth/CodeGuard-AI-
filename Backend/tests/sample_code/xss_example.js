function showComment(comment) {
  document.getElementById("output").innerHTML = comment;
}

function loadFromQuery() {
  const params = new URLSearchParams(window.location.search);
  showComment(params.get("q"));
}
