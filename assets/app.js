
(function(){
  var box = document.getElementById('filter');
  if(!box) return;
  var target = document.querySelector(box.dataset.target);
  if(!target) return;
  box.addEventListener('input', function(){
    var q = box.value.toLowerCase().trim();
    var rows = target.querySelectorAll('tbody tr');
    var shown = 0;
    rows.forEach(function(r){
      var hit = !q || r.textContent.toLowerCase().indexOf(q) > -1;
      r.style.display = hit ? '' : 'none';
      if(hit) shown++;
    });
    var c = document.getElementById('count');
    if(c) c.textContent = shown + ' of ' + rows.length + ' rows';
  });
})();
