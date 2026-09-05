// Living ticker + freshness pill. Loads data/ticker.json (built every 4h).
// Falls back to static HTML when offline.
(function(){
  const track = document.querySelector('.ticker-track');
  const ago = iso => { const m=Math.round((Date.now()-new Date(iso).getTime())/60000); if(m<60)return m+'M AGO'; const h=Math.round(m/60); if(h<48)return h+'H AGO'; return Math.round(h/24)+'D AGO'; };
  const setPill = txt => { const pill = document.getElementById('freshPill'); if(pill) pill.textContent = txt; };
  fetch('data/ticker.json',{cache:'no-store'}).then(r=>r.ok?r.json():null).then(d=>{
    if(!d||!Array.isArray(d.phrases)||!d.phrases.length) return;
    const half = d.phrases.map(p=>`${p}&nbsp;&nbsp;●&nbsp;&nbsp;`).join('');
    if(track) track.innerHTML = `<span>${half}</span><span>${half}</span>`;
    if(d.updated) setPill(`· UPDATED ${ago(d.updated)} · SWEEP #${d.sweep||'?'}`);
    const bar = document.querySelector('.ticker');
    if(bar&&d.updated) bar.title = 'Last sweep: ' + d.updated;
  }).catch(()=>{ setPill('· UPDATED EVERY 4 HOURS'); });
})();
