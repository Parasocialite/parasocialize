// Cases: renders cases.json teasers into #caseGrid. Full files arrive with
// membership later (gated at 500 subs) — for now every lock points at the Guide.
(function(){
  const grid = document.getElementById('caseGrid');
  if(!grid) return;
  fetch('cases.json',{cache:'no-store'}).then(r=>r.ok?r.json():null).then(items=>{
    if(!Array.isArray(items)||!items.length) return;
    const esc = s => String(s??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
    grid.innerHTML = items.map(c=>`
      <article class="card case">
        <p class="mono" style="font-size:.6rem;letter-spacing:.2em;color:var(--accent)">FILE ${esc(c.file_no)} · ${esc(c.date)}</p>
        <h3 class="serif">${esc(c.title)}</h3>
        <p style="color:var(--dim);font-size:.88rem">${esc(c.teaser)}</p>
        <span class="mono buy">READ FREE TEASER →</span>
        <div class="lock">${esc(c.unlock)} — <a href="guide/index.html" style="color:var(--gold)">Field Guide ($12) →</a></div>
      </article>`).join('');
  }).catch(()=>{});
})();
