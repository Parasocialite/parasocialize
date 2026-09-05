// Radar loader: renders /radar.json into magazine layout (#leadWrap hero,
// #secGrid secondary pair, #radarGrid rest). Static cards remain as fallback.
(async function(){
  const lead = document.getElementById('leadWrap');
  const sec = document.getElementById('secGrid');
  const grid = document.getElementById('radarGrid');
  if(!grid) return;
  let items = null;
  try{
    const res = await fetch('radar.json',{cache:'no-store'});
    if(!res.ok) return;
    items = await res.json();
  }catch(e){ return; }
  const staticCount = document.querySelectorAll('#leadWrap .story, #leadWrap .lead, #secGrid .story, #radarGrid .story').length;
  if(!Array.isArray(items) || items.length < staticCount) return;
  const esc = s => String(s??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
  const shortSrc = u => { try{ return new URL(u).hostname.replace(/^www\./,'').split('.')[0]; }catch(e){ return 'Source'; } };
  const cats = d => [(d.type==='non-fiction'?'nonfic':'fic'), ...(d.lenses||[]), ...(d.tags||[])].join(' ');
  const storyUrl = d => d.link || ('radar/' + String(d.slug||'').replace(/[^a-z0-9-]/g,'') + '.html');
  const art = (d,url) => d.image ? `<a class="art" href="${esc(url)}"><img src="${esc(d.image)}" alt="${esc(d.image_alt||d.title)}" loading="lazy"></a>` : '';
  const srcRow = d => { const ext = /^https?:/.test(d.source_url||'') ? ' target="_blank" rel="noopener"' : '';
    const takeUrl = storyUrl(d); const takeExt = /^https?:/.test(takeUrl) ? ' target="_blank" rel="noopener sponsored"' : '';
    return `<div class="meta src">${d.source_url?`<a href="${esc(d.source_url)}"${ext}>${esc(d.source_name||shortSrc(d.source_url))} ↗</a>`:''}<a href="${esc(takeUrl)}"${takeExt}>${esc(d.link_label||'Story →')}</a></div>`; };
  const badge = d => d.state==='FLASHING' ? ' · <span style="color:var(--accent)">NEW</span>' : d.state==='LINGERING' ? ' · <span style="color:var(--gold)">STILL RESONATING</span>' : '';
  const card = d => `<article class="story" data-cat="${esc(cats(d))}">${art(d,storyUrl(d))}<div class="body"><h3>${esc(d.title)}${badge(d)}</h3><p>${esc(d.dek)}</p>${srcRow(d)}</div></div></article>`;
  const d0 = items[0];
  if(lead && d0) lead.innerHTML = `<article class="lead" data-cat="${esc(cats(d0))}">${art(d0,storyUrl(d0))}<div class="body"><p class="kicker-lead">LEAD STORY · ${esc((d0.lenses||['FRESH'])[0].toUpperCase())} <span id="freshPill" class="mono" style="color:var(--gold)">· CHECKING…</span></p><h2>${esc(d0.title)}${badge(d0)}</h2><p>${esc(d0.dek)}</p>${srcRow(d0)}</div></div></article>`;
  if(sec) sec.innerHTML = items.slice(1,3).map(card).join('');
  grid.innerHTML = items.slice(3).map(card).join('');
})();
