// Living ticker: loads data/ticker.json (built every 4h by tools/refresh_4h.py).
// Falls back to static HTML when offline. Appends sweep time as title tooltip.
(function(){
  const track = document.querySelector('.ticker-track');
  if(!track) return;
  fetch('data/ticker.json',{cache:'no-store'}).then(r=>r.ok?r.json():null).then(d=>{
    if(!d||!Array.isArray(d.phrases)||!d.phrases.length) return;
    const half = d.phrases.map(p=>`${p}&nbsp;&nbsp;●&nbsp;&nbsp;`).join('');
    track.innerHTML = `<span>${half}</span><span>${half}</span>`;
    const bar = document.querySelector('.ticker');
    if(bar&&d.updated) bar.title = 'Last sweep: ' + d.updated;
  }).catch(()=>{});
})();
