/* Small, dependency-free table filter for the verification dashboard. */
(function () {
  "use strict";
  var input = document.getElementById("tableFilter");
  if (!input) return;
  var tables = Array.prototype.slice.call(document.querySelectorAll("table[data-filter]"));
  var rows = [];
  tables.forEach(function (table) {
    Array.prototype.slice.call(table.querySelectorAll("tbody tr")).forEach(function (row) {
      rows.push({ row: row, text: row.textContent.toLowerCase() });
    });
  });

  function apply() {
    var q = input.value.trim().toLowerCase();
    var hidden = 0;
    rows.forEach(function (item) {
      var hide = q !== "" && item.text.indexOf(q) === -1;
      item.row.classList.toggle("filter-hidden", hide);
      if (hide) hidden += 1;
    });
    input.setAttribute("aria-label", q ? "Filter table rows, " + (rows.length - hidden) + " shown" : "Filter table rows");
  }

  input.addEventListener("input", apply);
  input.addEventListener("keydown", function (ev) {
    if (ev.key === "Escape") { input.value = ""; apply(); }
  });
})();
