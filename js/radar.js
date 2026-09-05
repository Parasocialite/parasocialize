// Radar loader: renders /radar.json into #feed (uniform rows, first pinned).
// Static rows remain as fallback. Feed toolbar (sort/filter/search) owns order after render.
(async function(){
  const feed = document.getElementById('feed');
  if(!feed) return;
  let items = null;
  try{
    const res = await fetch('radar.json',{cache:'no-store'});
    if(!res.ok) return;
    items = await res.json();
  }catch(e){ return; }
  const staticCount = feed.querySelectorAll('.story').length;
  if(!Array.isArray(items) || items.length < staticCount) return;
  const esc = s => String(s??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
  const shortSrc = u => { try{ return new URL(u).hostname.replace(/^www\./,'').split('.')[0]; }catch(e){ return 'Source'; } };
  const cats = d => [(d.type==='non-fiction'?'nonfic':'fic'), ...(d.lenses||[]), ...(d.tags||[])].join(' ');
  const storyUrl = d => d.link || ('radar/' + String(d.slug||'').replace(/[^a-z0-9-]/g,'') + '.html');
  const flairFor = d => { const l=(d.lenses||[]).map(x=>String(x).toLowerCase());
    if(l.includes('idol'))return'IDOLS'; if(l.includes('character'))return'CHARACTERS';
    if(l.includes('creator')&&l.includes('companion'))return'AI × CREATORS';
    if(l.includes('creator'))return'CREATORS'; if(l.includes('companion'))return'AI';
    if(l.includes('universe'))return'UNIVERSES'; if(l.includes('brand'))return'BRANDS'; return'FRESH'; };
  const dateFmt = iso => { try{ return new Date(iso+'T00:00:00Z').toLocaleDateString('en-US',{month:'short',year:'numeric'}).toUpperCase(); }catch(e){ return ''; } };
  feed.innerHTML = items.map((d,i)=>{
    const pin = i===0 ? '<span class="flair pin">📌 PINNED</span>' : '';
    const ext = /^https?:/.test(d.source_url||'') ? ' target="_blank" rel="noopener"' : '';
    const takeUrl = storyUrl(d);
    return `<article class="story${i===0?' pinned':''}" data-cat="${esc(cats(d))}" data-res="${esc(d.resonance??'')}" data-date="${esc(d.last_seen||d.date||'')}" data-int="${esc(d.intensity??'')}"><a class="art" href="${esc(takeUrl)}">${d.image?`<img src="${esc(d.image)}" alt="${esc(d.image_alt||d.title)}" loading="lazy">`:''}</a><div class="body"><div class="lensrow">${pin}<span class="flair">${esc(flairFor(d))}</span><span class="mono postdate">${esc(dateFmt(d.last_seen||d.date||''))}</span></div><h3>${esc(d.title)}</h3><p>${esc(d.dek)}</p><div class="meta src">${d.source_url?`<a href="${esc(d.source_url)}"${ext}>${esc(d.source_name||shortSrc(d.source_url))} ↗</a>`:''}<a href="${esc(takeUrl)}">${esc(d.link_label||'Story →')}</a></div></div></article>`;
  }).join('');
})();
