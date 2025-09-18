// Guardar y cargar datos simples en localStorage


// Helpers
const DB = { notes: 'm_mentor_notes', sessions: 'm_mentor_sessions', progress: 'm_mentor_progress' };
function load(){
const notes = localStorage.getItem(DB.notes); if(notes) notesEl.value = notes;
const sessions = JSON.parse(localStorage.getItem(DB.sessions)||'[]'); renderSessions(sessions);
const pr = localStorage.getItem(DB.progress) || '40'; setProgress(Number(pr));
}
function setProgress(n){ n = Math.max(0,Math.min(100,Math.round(n))); pbFill.style.width = n + '%'; pbLabel.textContent = n + '%'; localStorage.setItem(DB.progress,String(n)); }


// Notes
saveNotesBtn.onclick = ()=>{ localStorage.setItem(DB.notes, notesEl.value); saveNotesBtn.textContent='Guardado'; setTimeout(()=>saveNotesBtn.textContent='Guardar notas',900);}
clearNotesBtn.onclick = ()=>{ notesEl.value=''; localStorage.removeItem(DB.notes); }


// Sessions
sessionForm.onsubmit = e =>{
e.preventDefault();
const title = document.getElementById('sessionTitle').value.trim();
const date = document.getElementById('sessionDate').value || null;
if(!title) return;
const sessions = JSON.parse(localStorage.getItem(DB.sessions)||'[]');
sessions.unshift({id:Date.now(),title,date});
localStorage.setItem(DB.sessions, JSON.stringify(sessions));
renderSessions(sessions);
sessionForm.reset();
}


document.getElementById('resetSessions').onclick = ()=>{ localStorage.removeItem(DB.sessions); renderSessions([]); }


function renderSessions(list){
sessionsList.innerHTML='';
if(!list.length){ summary.textContent='Sin sesiones. Guarda notas y añade una sesión.'; return; }
summary.textContent = `Tienes ${list.length} sesión(es) programada(s). Próxima: ${list[0].date||'s/fecha'}.`;
list.forEach(s=>{
const li = document.createElement('li');
li.innerHTML = `<div><strong>${s.title}</strong><div class='muted' style='font-size:12px'>${s.date||'Sin fecha'}</div></div><button data-id='${s.id}' class='ghost'>Hecho</button>`;
sessionsList.appendChild(li);
});
sessionsList.querySelectorAll('button').forEach(b=>b.onclick = ev=>{
const id = Number(ev.currentTarget.dataset.id);
let sessions = JSON.parse(localStorage.getItem(DB.sessions)||'[]');
sessions = sessions.filter(x=>x.id!==id);
localStorage.setItem(DB.sessions, JSON.stringify(sessions));
renderSessions(sessions);
});
}


// Progress controls
updateProgress.onclick = ()=>{ setProgress(Number(progressInput.value||0)); }


// Init
load();