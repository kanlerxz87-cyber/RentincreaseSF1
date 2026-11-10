(function () {
  "use strict";
  var inputs = document.querySelectorAll("[data-table-filter]");
  inputs.forEach(function (input) {
    var targetId = input.getAttribute("data-table-filter");
    var table = document.getElementById(targetId);
    var counter = document.querySelector('[data-filter-count="' + targetId + '"]');
    if (!table) return;
    var rows = Array.prototype.slice.call(table.querySelectorAll("tbody tr"));
    var total = rows.length;
    function update() {
      var q = (input.value || "").trim().toLowerCase();
      var shown = 0;
      rows.forEach(function (row) {
        var match = !q || row.textContent.toLowerCase().indexOf(q) !== -1;
        row.style.display = match ? "" : "none";
        if (match) shown += 1;
      });
      if (counter) {
        counter.textContent = "Showing " + shown + " of " + total + " rows";
      }
    }
    input.addEventListener("input", update);
    update();
  });
})();
