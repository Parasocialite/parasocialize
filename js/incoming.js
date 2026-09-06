// Incoming: renders sweeper candidates (data/candidates.json) as clickable links.
// These are machine-found stories awaiting a take — the visible 4h agent.
(function(){
  const grid = document.getElementById('incomingGrid');
  if(!grid) return;
  const esc = s => String(s??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
  const ago = iso => { const m=Math.round((Date.now()-new Date(iso).getTime())/60000); if(m<60)return m+'m ago'; const h=Math.round(m/60); if(h<48)return h+'h ago'; return Math.round(h/24)+'d ago'; };
  const artFor = l => ({idol:'img/art/idol.svg',character:'img/art/character.svg',creator:'img/art/creator.svg',ai:'img/art/ai.svg',companion:'img/art/ai.svg',universe:'img/art/universe.svg',brand:'img/art/universe.svg'}[String(l||'').toLowerCase()]||'img/art/universe.svg');
  fetch('data/candidates.json',{cache:'no-store'}).then(r=>r.ok?r.json():null).then(items=>{
    if(!Array.isArray(items)||!items.length){ grid.innerHTML = '<p class="mono" style="font-size:.66rem;color:var(--dim)">Nothing pending — sweeper runs every 4 hours. <a href="tip/index.html" style="color:var(--gold)">Tip a story →</a></p>'; return; }
    grid.innerHTML = items.slice(-6).reverse().map(c=>`
      <article class="story"><a class="art" tabindex="-1" aria-hidden="true" href="${esc(c.link)}" target="_blank" rel="noopener"><img src="${artFor(c.lens)}" alt="" loading="lazy"></a><div class="body"><h3 style="font-size:1.02rem;"><a href="${esc(c.link)}" target="_blank" rel="noopener" style="color:inherit">${esc(c.title)}</a></h3><div class="meta src"><span>FOUND ${esc(ago(c.at))}</span><a href="tip/index.html">Take pending</a></div></div></article>`).join('');
  }).catch(()=>{ grid.innerHTML = '<p class="mono" style="font-size:.66rem;color:var(--dim)">Offline — <a href="tip/index.html" style="color:var(--gold)">tip a story →</a></p>'; });
})();
