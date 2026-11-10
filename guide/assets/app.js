(function () {
  "use strict";
  document.addEventListener("DOMContentLoaded", function () {
    var input = document.getElementById("table-filter");
    var countEl = document.getElementById("filter-count");
    if (!input) return;

    function applyFilter() {
      var q = input.value.trim().toLowerCase();
      var rows = document.querySelectorAll("table.guide-table tbody tr");
      var shown = 0;
      rows.forEach(function (tr) {
        var match = !q || tr.textContent.toLowerCase().indexOf(q) !== -1;
        tr.style.display = match ? "" : "none";
        if (match) shown += 1;
      });
      if (countEl) {
        countEl.textContent = q
          ? "Showing " + shown + " of " + rows.length + " verified rows"
          : rows.length + " verified source-linked rows on this page";
      }
    }

    input.addEventListener("input", applyFilter);
    applyFilter();
  });
})();
