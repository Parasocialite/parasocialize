// Index renderer: loads index.json into #indexTable. Keeps static rows as fallback.
// Adds Copy-as-text (for X/TikTok captions) + week label. Screenshot = Win+Shift+S the table.
(function(){
  const table = document.getElementById('indexTable');
  if(!table) return;
  const esc = s => String(s??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
  const badge = m => {
    if(m.movement==='up') return `<span class="move up">▲${m.n||''}</span>`;
    if(m.movement==='down') return `<span class="move down">▼${m.n||''}</span>`;
    if(m.movement==='new') return `<span class="move new">NEW</span>`;
    if(m.movement==='house') return `<span class="move new">★ HOUSE</span>`;
    return `<span class="move">—</span>`;
  };
  fetch('index.json',{cache:'no-store'}).then(r=>r.ok?r.json():null).then(d=>{
    if(!d||!Array.isArray(d.items)||!d.items.length) return;
    table.innerHTML = d.items.map((m,i)=>`
      <div class="index-row"><span class="rank${i<3?' top':''}">${String(m.rank).padStart(2,'0')}</span>
      <span><b>${esc(m.title)}</b><br><span class="mono" style="font-size:.62rem;color:var(--dim)">${esc(m.lens)} · ${esc(m.detail)}</span></span>
      ${badge(m)}</div>`).join('');
    const label = document.getElementById('indexWeek');
    if(label) label.textContent = 'WEEK ' + (d.week||'');
    const btn = document.getElementById('indexCopy');
    if(btn) btn.onclick = async () => {
      const txt = `PARASOCIAL INDEX (${d.week})\n` + d.items.map(m=>`${m.rank}. ${m.title} [${m.lens}]`).join('\n') + `\nvia parasocialize.com`;
      try{ await navigator.clipboard.writeText(txt); btn.textContent='Copied — paste to X/TikTok ✓'; }
      catch(e){ prompt('Copy this:', txt); }
    };
  }).catch(()=>{});
})();
