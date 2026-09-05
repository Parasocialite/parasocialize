// Radar loader: renders /radar.json into #radarGrid. Static cards remain as fallback.
// Sleek card: image, title, one-line dek, source + take. State badge = freshness cue.
(async function(){
  const grid = document.getElementById('radarGrid');
  if(!grid) return;
  let items = null;
  try{
    const res = await fetch('radar.json',{cache:'no-store'});
    if(!res.ok) return;
    items = await res.json();
  }catch(e){ return; }
  if(!Array.isArray(items) || items.length < grid.querySelectorAll('.story').length) return;
  const esc = s => String(s??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
  const shortSrc = u => { try{ return new URL(u).hostname.replace(/^www\./,'').split('.')[0]; }catch(e){ return 'Source'; } };
  grid.innerHTML = items.map(d=>{
    const cats = [(d.type==='non-fiction'?'nonfic':'fic'), ...(d.lenses||[]), ...(d.tags||[])].join(' ');
    const ext = /^https?:/.test(d.source_url||'') ? ' target="_blank" rel="noopener"' : '';
    const storyUrl = 'radar/' + String(d.slug||'').replace(/[^a-z0-9-]/g,'') + '.html';
    const takeUrl = d.link || storyUrl;
    const takeExt = /^https?:/.test(takeUrl) ? ' target="_blank" rel="noopener sponsored"' : '';
    const art = d.image ? `<div class="art"><img src="${esc(d.image)}" alt="${esc(d.image_alt||d.title)}" loading="lazy"></div>` : '';
    const badge = d.state==='FLASHING' ? ' · <span style="color:var(--accent)">NEW</span>' : d.state==='LINGERING' ? ' · <span style="color:var(--gold)">STILL RESONATING</span>' : '';
    return `<article class="story" data-cat="${esc(cats)}">${art}<div class="body"><h3>${esc(d.title)}${badge}</h3><p>${esc(d.dek)}</p><div class="meta src">${d.source_url?`<a href="${esc(d.source_url)}"${ext}>${esc(d.source_name||shortSrc(d.source_url))} ↗</a>`:''}<a href="${esc(takeUrl)}"${takeExt}>${esc(d.link_label||'Story →')}</a></div></div></article>`;
  }).join('');
})();
