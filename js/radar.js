// Radar loader: renders /radar.json into #radarGrid. Static cards in v2.html remain as fallback/no-JS.
// Categories for filter: nonfic = type non-fiction, fic = type fiction, ai = tags includes ai, creator = lenses/tags includes creator.
(async function(){
  const grid = document.getElementById('radarGrid');
  if(!grid) return;
  let items = null;
  try{
    const res = await fetch('radar.json',{cache:'no-store'});
    if(!res.ok) return; // keep static fallback
    items = await res.json();
  }catch(e){ return; }
  // Only re-render if JSON is newer/longer than static (avoids clobbering hand tweaks with same data)
  if(!Array.isArray(items) || items.length < grid.querySelectorAll('.story').length) return;
  const esc = s => String(s??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
  grid.innerHTML = items.map(d=>{
    const cats = [(d.type==='non-fiction'?'nonfic':'fic'), ...(d.lenses||[]), ...(d.tags||[])].join(' ');
    const lenses = [`<span class="lens ${d.type==='non-fiction'?'nonfic':'fic'}">${esc(d.type.toUpperCase())}</span>`, ...(d.lenses||[]).map(l=>`<span class="lens">${esc(l.toUpperCase())}</span>`)].join('');
    const state = d.state ? `<span class="lens" style="background:#07070c;color:var(--gold);border:1px solid var(--gold)">${esc(d.state)}${d.resonance!=null?' · '+esc(d.resonance):''}</span>` : '';
    const pct = Math.round((d.intensity/10)*100);
    const ext = /^https?:/.test(d.link||'') ? ' target="_blank" rel="noopener sponsored"' : '';
    const art = d.image ? `<div class="art"><img src="${esc(d.image)}" alt="${esc(d.image_alt||d.title)}" loading="lazy"></div>` : `<div class="art" style="background:${esc(d.gradient||'#222')}">${esc(d.emoji||'●')}</div>`;
    const src = d.source_url ? `<div class="meta src"><span>SOURCE</span><a href="${esc(d.source_url)}"${ext}>${esc(d.source_name||'Read the story')} ↗</a></div>` : '';
    const src2 = d.source2_url ? `<div class="meta src"><span>ALSO</span><a href="${esc(d.source2_url)}"${ext}>${esc(d.source2_name||'Related')} ↗</a></div>` : '';
    return `<article class="story" data-cat="${esc(cats)}">${art}<div class="body"><div class="lensrow">${lenses}${state}</div><h3>${esc(d.title)}</h3><p>${esc(d.dek)}</p>${src}${src2}<div class="meter" role="img" aria-label="Parasocial intensity ${esc(d.intensity)} out of 10"><i style="width:${pct}%"></i></div><div class="meta"><span>INTENSITY ${esc(d.intensity)} · ${esc(d.read_minutes)} MIN${d.affiliate?' · AD':''}</span><a href="${esc(d.link)}"${d.link&&d.link.startsWith('#')?'':ext}>${esc(d.link_label||'MY TAKE →')}</a></div></div></article>`;
  }).join('');
})();
