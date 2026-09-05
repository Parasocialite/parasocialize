// Cases gate: renders cases.json into #caseGrid. ?member=1 previews unlocked state (demo for you).
// Real gate = Buttondown/Stripe paid tier hiding full body. Teaser always free = SEO + conversion.
(function(){
  const grid = document.getElementById('caseGrid');
  if(!grid) return;
  const isMember = new URLSearchParams(location.search).get('member')==='1';
  fetch('cases.json',{cache:'no-store'}).then(r=>r.ok?r.json():null).then(items=>{
    if(!Array.isArray(items)||!items.length) return;
    const esc = s => String(s??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
    grid.innerHTML = items.map(c=>`
      <article class="card case">
        <p class="mono" style="font-size:.6rem;letter-spacing:.2em;color:var(--accent)">FILE ${esc(c.file_no)} · ${esc(c.date)}</p>
        <h3 class="serif">${esc(c.title)}</h3>
        <p style="color:var(--dim);font-size:.88rem">${esc(c.teaser)}</p>
        <span class="mono buy">READ FREE TEASER →</span>
        <div class="lock">${isMember ? '✅ MEMBER PREVIEW UNLOCKED — full text + audio would stream here' : '🔒 '+esc(c.unlock)}</div>
        ${isMember?'':'<a class="btn btn-solid" style="margin-top:10px;text-align:center" href="#circle">Unlock $7/mo →</a>'}
      </article>`).join('')
      + (isMember?'':'<p class="mono" style="grid-column:1/-1;font-size:.62rem;color:var(--dim)">DEMO: add <span style="color:var(--gold)">?member=1</span> to URL to preview unlocked state.</p>');
  }).catch(()=>{});
  // member toggle button (demo only)
  const sec = document.getElementById('cases');
  if(sec && !document.getElementById('memberToggle')){
    const b=document.createElement('button');
    b.id='memberToggle'; b.className='fbtn'; b.style.marginTop='14px';
    b.textContent = isMember ? 'Exit member preview' : 'Preview as member';
    b.onclick=()=>{const u=new URL(location.href); isMember?u.searchParams.delete('member'):u.searchParams.set('member','1'); location.href=u.toString();};
    sec.querySelector('.sec-head').appendChild(b);
  }
})();
