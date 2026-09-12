const USER="RifatNSU701", DATA="./data"; const $=s=>document.querySelector(s);
const esc=s=>String(s??"").replace(/[&<>"']/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c]));
const profile=await fetch(`${DATA}/profile.json`).then(r=>r.json());
let gh=await fetch(`${DATA}/github.json`).then(r=>r.ok?r.json():{}).catch(()=>({}));
let contrib=await fetch(`${DATA}/contributions.json`).then(r=>r.ok?r.json():{}).catch(()=>({}));

function renderProfile(){
  $("#tagline").textContent=profile.tagline; $("#aboutText").textContent=profile.about;
  $("#degree").textContent=profile.education.degree; $("#institution").textContent=profile.education.institution; $("#eduStatus").textContent=profile.education.status;
  $("#currentlyList").innerHTML=profile.currently.map(x=>`<div class="current-item">${esc(x)}</div>`).join("");
  $("#focusList").innerHTML=profile.focus.slice(0,5).map(x=>`<div class="check">Focused on ${esc(x)}</div>`).join("");
  $("#skillCount").textContent=`${profile.skills.length} CAPABILITIES`;
  const cats=[...new Set(profile.skills.map(x=>x[0]))]; $("#skillTabs").innerHTML=[`ALL`,...cats].map((x,i)=>`<button class="skill-tab ${i===0?"active":""}" data-cat="${esc(x)}">${esc(x)}</button>`).join("");
  const drawSkills=(cat="ALL")=>$("#skillGrid").innerHTML=profile.skills.filter(x=>cat==="ALL"||x[0]===cat).map(x=>`<div class="skill"><div class="mono">${esc(x[2])}</div><strong>${esc(x[1])}</strong><small>${esc(x[0])}</small></div>`).join("");
  drawSkills(); $("#skillTabs").addEventListener("click",e=>{if(e.target.matches(".skill-tab")){document.querySelectorAll(".skill-tab").forEach(b=>b.classList.remove("active"));e.target.classList.add("active");drawSkills(e.target.dataset.cat)}});
  const toolNames=["Kali Linux","Wireshark","Wazuh","Splunk","Elastic","Metasploit","Nmap","Burp Suite","pfSense","Snort"];
  $("#toolGrid").innerHTML=toolNames.map(n=>{let s=profile.skills.find(x=>x[1]===n);return `<div class="tool"><span class="mono">${esc(s?.[2]||n.slice(0,3).toUpperCase())}</span><span>${esc(n)}</span></div>`}).join("");
  $("#experienceList").innerHTML=profile.experience.map(x=>`<div class="timeline-item"><h3>${esc(x.role)}</h3><div class="company">${esc(x.company)}</div><div class="period">${esc(x.period)}</div><p>${esc(x.description)}</p></div>`).join("");
  $("#certList").innerHTML=profile.certifications.map(x=>`<div class="cert"><div class="cert-badge">${esc(x.issuer.split(/[ /]/)[0].slice(0,4).toUpperCase())}</div><div><h3>${esc(x.name)}</h3><p>${esc(x.issuer)}${x.date?` · ${esc(x.date)}`:""}</p><span class="status">${esc(x.status)}</span></div></div>`).join("");
  $("#orgList").innerHTML=profile.organizations.map(x=>`<div class="org"><div class="org-icon">◈</div><div><h3>${esc(x.name)}</h3><p>${esc(x.detail)}</p></div><a href="${esc(x.url)}" target="_blank" rel="noreferrer">↗</a></div>`).join("");
  $("#contactGrid").innerHTML=profile.socials.map(x=>`<a class="contact" href="${esc(x.url)}" target="_blank" rel="noreferrer"><div class="contact-icon">${esc(x.icon)}</div><div><strong>${esc(x.label)}</strong><span>${esc(x.value)}</span></div></a>`).join("");
}
renderProfile();

async function liveGitHub(){
  const [u,r,e]=await Promise.all([
    fetch(`https://api.github.com/users/${USER}`).then(x=>x.ok?x.json():null),
    fetch(`https://api.github.com/users/${USER}/repos?per_page=100&sort=updated`).then(x=>x.ok?x.json():[]),
    fetch(`https://api.github.com/users/${USER}/events/public?per_page=15`).then(x=>x.ok?x.json():[])
  ]);
  if(!u)return gh;
  gh={...gh,user:u,repos:r,events:e,source:"live"}; return gh;
}
try{gh=await liveGitHub();$("#syncStatus").textContent="LIVE";}catch{$("#syncStatus").textContent="CACHE";}

const user=gh.user||{}; const repos=Array.isArray(gh.repos)?gh.repos:[]; const events=Array.isArray(gh.events)?gh.events:[];
const stars=repos.reduce((n,r)=>n+(r.stargazers_count||0),0), forks=repos.reduce((n,r)=>n+(r.forks_count||0),0);
$("#repoCount").textContent=user.public_repos??gh.public_repos??"—"; $("#starCount").textContent=stars; $("#forkCount").textContent=forks; $("#followers").textContent=user.followers??"—"; $("#sideFollowers").textContent=user.followers??"—"; $("#sideFollowing").textContent=user.following??"—";

const featured=profile.featuredOverride.map(n=>repos.find(r=>r.name===n)).filter(Boolean);
const chosen=featured.length?featured:repos.filter(r=>!r.fork).sort((a,b)=>(b.stargazers_count-a.stargazers_count)||(new Date(b.pushed_at)-new Date(a.pushed_at))).slice(0,6);
$("#projectMeta").textContent=`${chosen.length} SELECTED / ${repos.length} PUBLIC`;
$("#projectGrid").innerHTML=chosen.map(r=>`<article class="project"><div class="project-top"><div class="project-icon">${esc((r.language||"GH").slice(0,3).toUpperCase())}</div><h3>${esc(r.name)}</h3></div><p>${esc(r.description||"Repository with no public description.")}</p><div class="badges"><span class="badge">${esc(r.language||"Mixed")}</span>${(r.topics||[]).slice(0,2).map(t=>`<span class="badge">${esc(t)}</span>`).join("")}</div><div class="project-foot"><span>★ ${r.stargazers_count||0} &nbsp;⑂ ${r.forks_count||0}</span><a href="${esc(r.html_url)}" target="_blank" rel="noreferrer">VIEW ↗</a></div></article>`).join("")||`<div class="muted">No public repositories returned by the API.</div>`;

function eventText(ev){const repo=ev.repo?.name||"GitHub"; const t=ev.type||""; const map={PushEvent:"Pushed commits",WatchEvent:"Starred",ForkEvent:"Forked",CreateEvent:"Created",IssuesEvent:"Updated an issue",PullRequestEvent:"Updated a pull request",PullRequestReviewEvent:"Reviewed a pull request",ReleaseEvent:"Published a release"}; return `${map[t]||t.replace("Event","")} <a href="https://github.com/${esc(repo)}" target="_blank" rel="noreferrer">${esc(repo.split("/").pop())}</a>`}
$("#activityList").innerHTML=events.slice(0,7).map(ev=>`<div class="activity"><span class="activity-icon">${ev.type==="PushEvent"?"↥":"◉"}</span><span><b>${eventText(ev)}</b></span><time>${timeAgo(ev.created_at)}</time></div>`).join("")||`<div class="muted">No public events available.</div>`;
function timeAgo(d){if(!d)return"—";const s=(Date.now()-new Date(d))/1000;if(s<60)return"now";if(s<3600)return`${Math.floor(s/60)}m`;if(s<86400)return`${Math.floor(s/3600)}h`;return`${Math.floor(s/86400)}d`}

const langAgg={}; if(gh.languages)Object.assign(langAgg,gh.languages); else repos.forEach(r=>{if(r.language)langAgg[r.language]=(langAgg[r.language]||0)+1});
const langEntries=Object.entries(langAgg).sort((a,b)=>b[1]-a[1]).slice(0,6), langTotal=langEntries.reduce((a,b)=>a+b[1],0)||1;
$("#languageList").innerHTML=langEntries.map(([n,v])=>`<div class="lang"><div class="lang-head"><span>${esc(n)}</span><b>${Math.round(v/langTotal*100)}%</b></div><div class="lang-bar"><i style="width:${Math.max(3,Math.round(v/langTotal*100))}%"></i></div></div>`).join("")||`<div class="muted">Language data will appear after synchronization.</div>`;

function renderContrib(data){
  const days=Array.isArray(data.days)?data.days:[]; const cells=days.slice(-371); $("#heatGrid").innerHTML="";
  const wrap=document.createElement("div"); wrap.className="heat-grid"; wrap.style.gridTemplateRows="repeat(7,14px)"; wrap.style.gridAutoFlow="column";
  cells.forEach(d=>{const c=document.createElement("span");c.className="heat-cell "+(d.count>=12?"l4":d.count>=7?"l3":d.count>=3?"l2":d.count>=1?"l1":"");c.title=`${d.date||""}: ${d.count||0} contributions`;wrap.appendChild(c)}); $("#heatGrid").appendChild(wrap);
  $("#contribTotal").textContent=data.total!=null?`${data.total} CONTRIBUTIONS`:"DATA VIA ACTIONS"; $("#streak").textContent=data.currentStreak!=null?`STREAK ${data.currentStreak} DAYS`:"STREAK —";
}
renderContrib(contrib);
$("#months").innerHTML=["JAN","FEB","MAR","APR","MAY","JUN","JUL","AUG","SEP","OCT","NOV","DEC"].map(m=>`<span>${m}</span>`).join("");

function terminal(){const lines=["$ whoami","rifat-khan","$ focus","cybersecurity / networking / infrastructure","$ status","building secure systems..."];let i=0;const body=$("#terminalBody");const type=()=>{if(i>=lines.length){body.innerHTML+=`<span class="terminal-cursor"></span>`;return}let line=lines[i++],j=0,el=document.createElement("div");body.appendChild(el);const tick=()=>{el.textContent=line.slice(0,j++);if(j<=line.length)setTimeout(tick,line.startsWith("$")?42:22);else setTimeout(type,220)};tick()};type()}terminal();

function canvasWorld(){
 const c=$("#worldCanvas"),ctx=c.getContext("2d"),parent=c.parentElement;let w,h,dpr,raf,visible=true;const rand=(()=>{let s=1337;return()=>{s=(s*1664525+1013904223)>>>0;return s/4294967296}})();const pts=Array.from({length:38},()=>({x:.1+rand()*.8,y:.13+rand()*.7,r:1+rand()*2,a:rand()*Math.PI*2}));
 const resize=()=>{dpr=Math.min(devicePixelRatio||1,2);w=parent.clientWidth;h=parent.clientHeight;c.width=w*dpr;c.height=h*dpr;ctx.setTransform(dpr,0,0,dpr,0,0)};resize();addEventListener("resize",resize);
 const draw=t=>{if(!visible)return;ctx.clearRect(0,0,w,h);const cx=w*.54,cy=h*.5,rx=Math.min(w*.43,220),ry=Math.min(h*.39,140);ctx.strokeStyle="rgba(0,210,255,.13)";ctx.lineWidth=1;for(let i=0;i<8;i++){ctx.beginPath();ctx.ellipse(cx,cy,rx-i*8,ry-i*5,0,0,Math.PI*2);ctx.stroke()}pts.forEach((p,k)=>{const x=cx+(p.x-.5)*rx*2,y=cy+(p.y-.5)*ry*2+Math.sin(t*.0008+p.a)*3;pts.slice(k+1).forEach(q=>{const x2=cx+(q.x-.5)*rx*2,y2=cy+(q.y-.5)*ry*2;const dd=Math.hypot(x-x2,y-y2);if(dd<90){ctx.strokeStyle=`rgba(0,205,255,${.18-dd/650})`;ctx.beginPath();ctx.moveTo(x,y);ctx.lineTo(x2,y2);ctx.stroke()}});ctx.fillStyle="#00e4ff";ctx.shadowBlur=12;ctx.shadowColor="#00e4ff";ctx.beginPath();ctx.arc(x,y,p.r,0,Math.PI*2);ctx.fill();ctx.shadowBlur=0});ctx.strokeStyle="rgba(0,245,160,.45)";ctx.beginPath();ctx.arc(cx,cy,rx+8,Math.sin(t*.00025),Math.sin(t*.00025)+.9);ctx.stroke();raf=requestAnimationFrame(draw)};
 new IntersectionObserver(es=>{visible=es[0].isIntersecting;if(visible)raf=requestAnimationFrame(draw);else cancelAnimationFrame(raf)}).observe(c);raf=requestAnimationFrame(draw);
}canvasWorld();

function network(){
 const c=$("#networkCanvas"),ctx=c.getContext("2d"),p=c.parentElement;let w,h,dpr,raf,on=true;const names=["CLIENT","FIREWALL","SOC","SIEM","CLOUD","DB","ENDPOINT","NMAP","SENSOR","SERVER"];const nodes=names.map((name,i)=>({name,x:.08+((i*37)%83)/100,y:.25+((i*61)%53)/100}));const edges=[[0,1],[1,2],[2,3],[3,4],[3,5],[4,6],[6,7],[2,8],[8,9],[5,9]];
 const resize=()=>{dpr=Math.min(devicePixelRatio||1,2);w=p.clientWidth;h=p.clientHeight;c.width=w*dpr;c.height=h*dpr;ctx.setTransform(dpr,0,0,dpr,0,0)};resize();addEventListener("resize",resize);
 const draw=t=>{if(!on)return;ctx.clearRect(0,0,w,h);edges.forEach(([a,b])=>{let A=nodes[a],B=nodes[b],ax=A.x*w,ay=A.y*h,bx=B.x*w,by=B.y*h;ctx.strokeStyle="rgba(0,198,255,.23)";ctx.beginPath();ctx.moveTo(ax,ay);ctx.lineTo(bx,by);ctx.stroke();let q=(t*.00012+(a+b)/7)%1;ctx.fillStyle="#00f5a0";ctx.shadowBlur=8;ctx.shadowColor="#00f5a0";ctx.beginPath();ctx.arc(ax+(bx-ax)*q,ay+(by-ay)*q,2,0,7);ctx.fill();ctx.shadowBlur=0});nodes.forEach((n,i)=>{let x=n.x*w,y=n.y*h;ctx.fillStyle="#031923";ctx.strokeStyle=i===2?"#00f5a0":"#00d9ff";ctx.lineWidth=1.2;ctx.beginPath();ctx.arc(x,y,8,0,7);ctx.fill();ctx.stroke();ctx.fillStyle="#83a9b6";ctx.font="8px JetBrains Mono,monospace";ctx.fillText(n.name,x+12,y+3)});raf=requestAnimationFrame(draw)};
 new IntersectionObserver(es=>{on=es[0].isIntersecting;if(on)raf=requestAnimationFrame(draw);else cancelAnimationFrame(raf)}).observe(c);raf=requestAnimationFrame(draw);
}network();
