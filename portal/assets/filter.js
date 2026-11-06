(function () {
  var wrappers = document.querySelectorAll('[data-filter-scope]');
  wrappers.forEach(function (scope) {
    var input = scope.querySelector('input[type="search"]');
    var select = scope.querySelector('select');
    var rows = scope.querySelectorAll('tbody tr');
    var countEl = scope.querySelector('[data-row-count]');
    function apply() {
      var q = input ? input.value.trim().toLowerCase() : '';
      var st = select ? select.value : 'all';
      var shown = 0;
      rows.forEach(function (tr) {
        var textMatch = !q || tr.textContent.toLowerCase().indexOf(q) !== -1;
        var rowSt = tr.getAttribute('data-status-group') || '';
        var stMatch = st === 'all' || rowSt === st;
        var vis = textMatch && stMatch;
        tr.style.display = vis ? '' : 'none';
        if (vis) shown += 1;
      });
      if (countEl) {
        countEl.textContent = shown + ' of ' + rows.length + ' rows shown';
      }
    }
    if (input) input.addEventListener('input', apply);
    if (select) select.addEventListener('change', apply);
    apply();
  });
})();
