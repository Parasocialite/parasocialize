// Incoming: renders sweeper candidates (data/candidates.json) as clickable links.
// These are machine-found stories awaiting a take — the visible 4h agent.
(function(){
  const grid = document.getElementById('incomingGrid');
  if(!grid) return;
  const esc = s => String(s??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
  const ago = iso => { const m=Math.round((Date.now()-new Date(iso).getTime())/60000); if(m<60)return m+'m ago'; const h=Math.round(m/60); if(h<48)return h+'h ago'; return Math.round(h/24)+'d ago'; };
  fetch('data/candidates.json',{cache:'no-store'}).then(r=>r.ok?r.json():null).then(items=>{
    if(!Array.isArray(items)||!items.length){ grid.innerHTML = '<p class="mono" style="font-size:.66rem;color:var(--dim)">Nothing pending — sweeper runs every 4 hours. <a href="tip/index.html" style="color:var(--gold)">Tip a story →</a></p>'; return; }
    grid.innerHTML = items.slice(-6).reverse().map(c=>`
      <article class="story"><div class="body"><div class="lensrow"><span class="lens">${esc((c.lens||'fresh').toUpperCase())}</span><span class="lens" style="background:#07070c;color:var(--dim)">FOUND ${esc(ago(c.at))}</span></div><h3 style="font-size:1.05rem;">${esc(c.title)}</h3><div class="meta src"><a href="${esc(c.link)}" target="_blank" rel="noopener">Read ↗</a><a href="tip/index.html">Take pending</a></div></div></article>`).join('');
  }).catch(()=>{ grid.innerHTML = '<p class="mono" style="font-size:.66rem;color:var(--dim)">Offline — <a href="tip/index.html" style="color:var(--gold)">tip a story →</a></p>'; });
})();
