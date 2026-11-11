(function () {
  "use strict";
  document.addEventListener("DOMContentLoaded", function () {
    var inputs = document.querySelectorAll("[data-table-filter]");
    inputs.forEach(function (input) {
      var targetId = input.getAttribute("data-table-filter");
      var table = document.getElementById(targetId);
      var status = document.querySelector('[data-filter-status="' + targetId + '"]');
      if (!table || !table.tBodies.length) {
        return;
      }
      var rows = Array.prototype.slice.call(table.tBodies[0].rows);
      var update = function () {
        var q = (input.value || "").trim().toLowerCase();
        var shown = 0;
        rows.forEach(function (row) {
          var match = !q || row.textContent.toLowerCase().indexOf(q) !== -1;
          row.style.display = match ? "" : "none";
          if (match) {
            shown += 1;
          }
        });
        if (status) {
          status.textContent = "Showing " + shown + " of " + rows.length + " rows";
        }
      };
      input.addEventListener("input", update);
      update();
    });
  });
})();
