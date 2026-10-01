const $=id=>document.getElementById(id);
const chat=$('chat'), opts=$('opts'), chipsEl=$('chips'), screen=$('smsScreen');
// Voice ON by default: a woman who cannot READ must still HEAR everything.
let SID=null, PHONES='9999'+Math.floor(100000+Math.random()*899999), TID=null, LANG='hi', VOICE_ON=true;
const STEPS=[["👋","Start"],["🌐","Language"],["🌾","Scheme"],["❓","Q&A"],["📄","Form"],["🚚","Track"]];

/* ---------------- rail ---------------- */
function renderRail(cur){
  $('rail').innerHTML=STEPS.map(([ico,lab],i)=>{
    const idx={GREETING:0,LANGUAGE:1,SCHEME:2,INTERVIEW:3,VERDICT:3,DOCS:4,PROFILE:4,FORM:4,TRACKING:5,CSC:5,CLOSED:5}[cur]??0;
    const cls=i<idx?'done':i===idx?'on':'';
    return `<div class="rstep ${cls}"><span class="ico">${ico}</span>${lab}</div>`;
  }).join('');
}

/* ---------------- chat ---------------- */
function bubble(text,who,heard,card){
  const d=document.createElement('div'); d.className='msg '+who;
  d.textContent=text;
  if(heard){const h=document.createElement('div');h.className='heard';h.textContent='🎤 heard: "'+heard+'"';d.appendChild(h);}
  if(card&&who==='bot') d.appendChild(renderCard(card));
  chat.appendChild(d); chat.scrollTop=chat.scrollHeight;
  if(who==='bot'&&VOICE_ON) speak(text);
  return d;
}
const esc=s=>String(s).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
function renderCard(c){
  const el=document.createElement('div');
  const cls=c.type==='success'?'green':c.type==='reject'?'red':c.type==='info'?'blue':'';
  el.className='rcard '+cls;
  el.innerHTML=`<div class="t">${esc(c.emoji||'')} ${esc(c.title||'')}</div>
    <ul>${(c.facts||[]).map(f=>`<li>${esc(f)}</li>`).join('')}</ul>
    ${c.source?`<div class="src">ℹ️ ${esc(c.source)}</div>`:''}`;
  if(c.type==='success'&&TID) el.innerHTML+=`<a class="pdfbtn" href="/pdf/${TID}.pdf" target="_blank">📄 Download form PDF</a>`;
  return el;
}
const SPEECH_LANG={en:'en-IN',hi:'hi-IN',ta:'ta-IN',te:'te-IN',kn:'kn-IN',ml:'ml-IN',mr:'mr-IN',gu:'gu-IN',bn:'bn-IN',pa:'pa-IN',ur:'ur-IN',or:'or-IN',as:'as-IN'};
function speak(text){
  try{
    if(!window.speechSynthesis||!VOICE_ON) return;
    speechSynthesis.cancel();
    const u=new SpeechSynthesisUtterance(text.replace(/[#*🌿🏠🔥🌾🏦👷🔨🎓🛵📱☀️🏥🚁💼🤝📋💰📄]/g,''));
    u.lang=SPEECH_LANG[LANG]||'hi-IN'; u.rate=.95;
    const v=speechSynthesis.getVoices().find(v=>v.lang.startsWith((SPEECH_LANG[LANG]||'').slice(0,2)));
    if(v) u.voice=v;
    speechSynthesis.speak(u);
  }catch(e){}
}
function typing(on){
  const t=$('typing'); if(t)t.remove();
  if(on){const d=document.createElement('div');d.id='typing';d.className='msg bot typing';d.innerHTML='<i></i><i></i><i></i>';chat.appendChild(d);chat.scrollTop=chat.scrollHeight;}
}
function renderOpts(list){ opts.innerHTML=''; (list||[]).forEach(o=>{const b=document.createElement('button');b.textContent=o.label;b.onclick=()=>act(o.value,o.action);opts.appendChild(b);}); }
function renderChips(list){
  chipsEl.innerHTML='';
  const LABELS={kisan:'🌾 kisan',ghar:'🏠 ghar',gas:'🔥 gas',kaam:'👷 kaam',
    scholarship:'🎓 scholarship',pension:'👴 pension',ebike:'🛵 e-bike',
    documents:'📋 documents','other scheme':'🔁 other scheme',ayushman:'🏥 free treatment',
    'mudra loan':'💼 business loan'};
  const items=(list&&list.length)?list:['kisan','ghar','gas','ebike','scholarship','pension'];
  items.forEach(c=>{
    const b=document.createElement('button');b.textContent=LABELS[c]||c;b.onclick=()=>act(c,'chip');chipsEl.appendChild(b);
  });
}
function renderImpact(t){
  const f=n=>n>=1e7?(n/1e7).toFixed(2)+' Cr':n>=1e5?(n/1e5).toFixed(1)+' L':n>=1000?(n/1000).toFixed(1)+'k':n;
  $('impactGrid').innerHTML=`
    <div class="stat"><b>👩 ${f(t.women_helped)}</b><span>women helped</span></div>
    <div class="stat"><b>₹${f(t.benefit_inr)}</b><span>benefits unlocked</span></div>
    <div class="stat"><b>🍃 ${f(t.co2_kg)} kg</b><span>CO₂ saved</span></div>
    <div class="stat"><b>🚌 ${f(t.km_avoided)} km</b><span>travel avoided</span></div>
    <div class="stat"><b>📄 ${f(t.paper_sheets)}</b><span>paper sheets saved</span></div>
    <div class="stat"><b>🌳 ${t.trees_equiv}</b><span>tree-years equiv.</span></div>`;
}
function pushSMS(body){
  const ph=screen.querySelector('.placeholder'); if(ph)ph.remove();
  const d=document.createElement('div'); d.className='sms';
  const t=new Date().toLocaleTimeString([],{hour:'2-digit',minute:'2-digit'});
  d.innerHTML=`<div class="from">SAHAYI · ${t}</div><div>${esc(body)}</div><div class="time">SMS ✓✓</div>`;
  screen.prepend(d);
}
async function refreshImpact(){ const r=await fetch('/api/impact'); renderImpact(await r.json()); }
async function refreshSMS(){ const r=await fetch('/api/sms/'+PHONES); const j=await r.json();
  screen.innerHTML='';
  if(!j.messages.length){screen.innerHTML='<div style="text-align:center;color:#94a3b8;font-size:.8rem;padding:40px 10px">No messages yet.</div>';return;}
  j.messages.slice().reverse().forEach(m=>pushSMS(m.body)); }

/* ---------------- core conversation ---------------- */
async function act(value,action,label){
  if(!SID) await start();
  bubble(label||value,'user');
  typing(true);
  try{
    const r=await fetch('/api/message',{method:'POST',headers:{'Content-Type':'application/x-www-form-urlencoded'},
      body:new URLSearchParams({session_id:SID,text:value,phone:PHONES})});
    const j=await r.json();
    typing(false);
    if(j.detail){ bubble('⚠️ '+j.detail,'bot'); return; }
    LANG=j.language;
    bubble(j.text,'bot',null,j.card);
    renderOpts(j.options); renderChips(j.chips);
    if(j.tracking){TID=j.tracking.tracking_id;showTracker(j.tracking);}
    if(j.fraud_shield){$('fraud').textContent='🛡️ '+j.fraud_shield.message;$('fraud').classList.add('show');}
  }catch(e){ typing(false); bubble('⚠️ Network issue - SAHAYI is still here. Try again.','bot'); }
  refreshImpact(); refreshSMS();
}
function showTracker(t){
  TID=t.tracking_id;
  $('tracker').classList.add('show');
  $('trkTitle').textContent=`📄 ${t.scheme_emoji} ${t.scheme} · ${t.tracking_id}`;
  $('trkMsg').textContent=t.status_message;
  for(let i=1;i<=4;i++){$('s'+i).classList.toggle('done',i<=t.step_index+1);}
}
async function advance(){
  if(!TID)return;
  const r=await fetch('/api/track/'+TID+'/advance',{method:'POST'});
  showTracker(await r.json());
  pushSMS('Status update: application '+TID+' moved forward. SAHAYI saath hai.');
}
async function send(){ const t=$('txt').value.trim(); if(!t)return; $('txt').value=''; await act(t,'chat'); }
$('send').onclick=send;
$('txt').addEventListener('keydown',e=>{if(e.key==='Enter')send();});
$('vox').onclick=()=>{VOICE_ON=!VOICE_ON;$('vox').textContent=VOICE_ON?'🔊':'🔇';$('vox').classList.toggle('on',VOICE_ON);if(VOICE_ON)speak('SAHAYI ki awaaz on hai');};

/* mic */
const SR=window.SpeechRecognition||window.webkitSpeechRecognition;
let rec=null,listening=false;
if(SR){
  rec=new SR(); rec.interimResults=false; rec.maxAlternatives=1;
  rec.onresult=e=>{const t=e.results[0][0].transcript; act(t,'voice',t);};
  rec.onend=()=>{$('mic').classList.remove('rec');listening=false;};
  rec.onerror=()=>{$('mic').classList.remove('rec');listening=false;};
  $('mic').onclick=()=>{ if(listening){rec.stop();return;}
    speechSynthesis&&speechSynthesis.cancel();
    rec.lang=SPEECH_LANG[LANG]||'hi-IN';
    try{rec.start();listening=true;$('mic').classList.add('rec');}catch(e){} };
}else{ $('mic').onclick=()=>alert('Use Chrome or Edge for live mic, or type your answer.'); }

/* ---------------- start / reset / auto-demo ---------------- */
async function start(){
  const r=await fetch('/api/start',{method:'POST',headers:{'Content-Type':'application/x-www-form-urlencoded'},body:new URLSearchParams({phone:PHONES})});
  const j=await r.json(); SID=j.session_id; LANG='hi';
  bubble(j.text,'bot',null,null); renderOpts(j.options); renderChips([]);
  renderRail('LANGUAGE');
  if(j.fraud_shield){$('fraud').textContent='🛡️ '+j.fraud_shield.message;$('fraud').classList.add('show');}
}
async function resetAll(){
  SCRIPT.forEach(s=>clearTimeout(s.t));
  chat.innerHTML=''; screen.innerHTML='<div class="placeholder" style="text-align:center;color:#94a3b8;font-size:.8rem;padding:40px 10px">No messages yet.</div>';
  $('tracker').classList.remove('show'); TID=null; SID=null;
  await start(); refreshSMS(); refreshImpact();
}
const SCRIPT=[
  {d:0,   do:()=>start()},
  {d:1800,do:()=>act('english','chat')},
  {d:3600,do:()=>act('farmer money','chat')},
  {d:5400,do:()=>act('yes','chat')},
  {d:7000,do:()=>act('yes','chat')},
  {d:8600,do:()=>act('no','chat')},
  {d:10200,do:()=>act('documents','chat')},
  {d:11800,do:()=>act('yes','chat')},
  {d:13200,do:()=>act('Lakshmi','chat')},
  {d:14400,do:()=>act(PHONES,'chat')},
  {d:15600,do:()=>act('Rajasthan Barmer','chat')},
  {d:17400,do:()=>act('csc','chat')},
];
function autoDemo(){
  resetAll().then(()=>{ SCRIPT.forEach(step=>{ step.t=setTimeout(step.do, step.d); }); });
}
(async function boot(){
  // warm the voice list (browsers load voices asynchronously)
  if(window.speechSynthesis){ speechSynthesis.getVoices(); speechSynthesis.onvoiceschanged=()=>speechSynthesis.getVoices(); }
  const h=await (await fetch('/api/health')).json();
  $('mode').textContent=h.speech.stt==='google'?'production-voice':'demo-mode';
  renderImpact(h.impact); renderRail('LANGUAGE'); renderChips([]);
  await start(); refreshSMS();
})();

/* --- event wiring (no inline handlers) --- */
$('advBtn').addEventListener('click', advance);
$('resetBtn').addEventListener('click', resetAll);
$('demoBtn').addEventListener('click', autoDemo);
