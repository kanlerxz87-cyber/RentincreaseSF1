
// Progressive enhancement only. Every page is fully readable without it.
(function(){
  var input=document.getElementById('filter');
  if(!input) return;
  var rows=[].slice.call(document.querySelectorAll('table.filterable tbody tr'));
  var count=document.getElementById('count');
  function upd(){
    var q=input.value.trim().toLowerCase(),n=0;
    rows.forEach(function(r){
      var hit=!q||r.textContent.toLowerCase().indexOf(q)>-1;
      r.style.display=hit?'':'none';
      if(hit)n++;
    });
    if(count) count.textContent=q?n+' of '+rows.length+' shown':'';
  }
  input.addEventListener('input',upd);
  upd();
})();
