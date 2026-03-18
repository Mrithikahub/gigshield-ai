const API = "http://localhost:8000";

async function apiPost(p,b){
    const r=await fetch(API+p,{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify(b)});
    const d=await r.json();
    if(!r.ok)throw new Error(d.detail||"Error");
    return d;
}

async function apiGet(p){
    const r=await fetch(API+p);
    const d=await r.json();
    if(!r.ok)throw new Error(d.detail||"Error");
    return d;
}

function saveWorker(d){localStorage.setItem("gs_worker",JSON.stringify(d));}
function getWorker(){const s=localStorage.getItem("gs_worker");return s?JSON.parse(s):null;}
function clearWorker(){localStorage.removeItem("gs_worker");}

function goTo(page){
    var p=window.location.pathname.split('/');
    p[p.length-1]=page;
    window.location.href=p.join('/');
}
function goToLogin(){ goTo('login.html'); }
function goToDashboard(){ goTo('dashboard.html'); }
