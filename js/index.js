// Index renderer: loads index.json into #indexTable. Rows are real links.
// Adds Copy-as-text (for X/TikTok captions) + week label.
(function(){
  const table = document.getElementById('indexTable');
  if(!table) return;
  const esc = s => String(s??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
  const badge = m => {
    if(m.movement==='up') return `<span class="move up">▲${m.n||''}</span>`;
    if(m.movement==='down') return `<span class="move down">▼${m.n||''}</span>`;
    if(m.movement==='new') return `<span class="move new">NEW</span>`;
    if(m.movement==='house'||m.movement==='mine') return `<span class="move new">★ MINE</span>`;
    return `<span class="move">—</span>`;
  };
  const ext = u => /^https?:/.test(u||'') ? ' target="_blank" rel="noopener"' : '';
  const artFor = m => { const l = String(m.lens||'').toUpperCase();
    if(/AI/.test(l)) return 'img/art/ai.svg';
    if(/CHARACTER|FICTION/.test(l)) return 'img/art/character.svg';
    if(/CREATOR/.test(l)) return 'img/art/creator.svg';
    if(/IDOL/.test(l)) return 'img/art/idol.svg';
    return 'img/art/universe.svg'; };
  fetch('index.json',{cache:'no-store'}).then(r=>r.ok?r.json():null).then(d=>{
    if(!d||!Array.isArray(d.items)||!d.items.length) return;
    table.innerHTML = d.items.map((m,i)=>`
      <a class="index-row" href="${esc(m.link||'#radar')}"${ext(m.link)}><img src="${artFor(m)}" alt="" loading="lazy">
      <span><b>${esc(m.title)}</b><br><span class="mono" style="font-size:.62rem;color:var(--dim)">${esc(m.lens)} · ${esc(m.detail)}</span></span>
      ${badge(m)}</a>`).join('');
    const label = document.getElementById('indexWeek');
    if(label) label.textContent = 'WEEK ' + (d.week||'');
    const btn = document.getElementById('indexCopy');
    if(btn && !btn.dataset.wired){ btn.dataset.wired='1'; btn.onclick = async () => {
      const txt = `PARASOCIAL INDEX (${d.week})\n` + d.items.map(m=>`${m.rank}. ${m.title} [${m.lens}]`).join('\n') + `\nvia parasocialize.com`;
      try{ await navigator.clipboard.writeText(txt); btn.textContent='Copied — paste anywhere ✓'; setTimeout(()=>btn.textContent='Copy as text',2500); }
      catch(e){ prompt('Copy this:', txt); }
    }; }
  }).catch(()=>{});
})();
