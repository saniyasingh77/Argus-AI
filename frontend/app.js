/* ============================================================
   Argus AI — shared frontend helpers
   ============================================================ */

/* ---- Inline SVGs (no external assets, CSP-safe) ---- */
const I = (p) => `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">${p}</svg>`;
const ICONS = {
  logo: `<svg class="logo" viewBox="0 0 48 48" fill="none" xmlns="http://www.w3.org/2000/svg">
    <rect width="48" height="48" rx="12" fill="url(#ag)"/>
    <path d="M8 24s6-9 16-9 16 9 16 9-6 9-16 9S8 24 8 24Z" stroke="#fff" stroke-width="2.4" fill="none"/>
    <circle cx="24" cy="24" r="5.5" fill="#fff"/><circle cx="24" cy="24" r="2.4" fill="#4338ca"/>
    <defs><linearGradient id="ag" x1="0" y1="0" x2="48" y2="48">
      <stop stop-color="#6366f1"/><stop offset="1" stop-color="#0ea5a6"/></linearGradient></defs>
  </svg>`,
  grid: I(`<rect x="3" y="3" width="7" height="7" rx="1"/><rect x="14" y="3" width="7" height="7" rx="1"/><rect x="14" y="14" width="7" height="7" rx="1"/><rect x="3" y="14" width="7" height="7" rx="1"/>`),
  activity: I(`<path d="M22 12h-4l-3 9L9 3l-3 9H2"/>`),
  alert: I(`<path d="M10.29 3.86 1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"/><line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/>`),
  shield: I(`<path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/>`),
  users: I(`<path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M23 21v-2a4 4 0 0 0-3-3.87M16 3.13a4 4 0 0 1 0 7.75"/>`),
  heart: I(`<path d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 1 0-7.78 7.78L12 21.23l8.84-8.84a5.5 5.5 0 0 0 0-7.78z"/>`),
  monitor: I(`<rect x="2" y="3" width="20" height="14" rx="2"/><line x1="8" y1="21" x2="16" y2="21"/><line x1="12" y1="17" x2="12" y2="21"/>`),
  video: I(`<polygon points="23 7 16 12 23 17 23 7"/><rect x="1" y="5" width="15" height="14" rx="2"/>`),
  list: I(`<line x1="8" y1="6" x2="21" y2="6"/><line x1="8" y1="12" x2="21" y2="12"/><line x1="8" y1="18" x2="21" y2="18"/><line x1="3" y1="6" x2="3.01" y2="6"/><line x1="3" y1="12" x2="3.01" y2="12"/><line x1="3" y1="18" x2="3.01" y2="18"/>`),
  bell: I(`<path d="M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9"/><path d="M13.73 21a2 2 0 0 1-3.46 0"/>`),
  empty: I(`<path d="M22 12h-6l-2 3h-4l-2-3H2"/><path d="M5.45 5.11 2 12v6a2 2 0 0 0 2 2h16a2 2 0 0 0 2-2v-6l-3.45-6.89A2 2 0 0 0 16.76 4H7.24a2 2 0 0 0-1.79 1.11z"/>`),
  check: I(`<polyline points="20 6 9 17 4 12"/>`),
  plus: I(`<line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/>`),
  search: I(`<circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/>`),
  logout: I(`<path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"/><polyline points="16 17 21 12 16 7"/><line x1="21" y1="12" x2="9" y2="12"/>`),
  eye: I(`<path d="M1 12s4-7 11-7 11 7 11 7-4 7-11 7-11-7-11-7z"/><circle cx="12" cy="12" r="3"/>`),
  eyeOff: I(`<path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19m-6.72-1.07a3 3 0 1 1-4.24-4.24"/><line x1="1" y1="1" x2="23" y2="23"/>`),
};

function brandHTML() {
  return `<span class="brand">${ICONS.logo}<span class="name">Argus<b>AI</b></span></span>`;
}

/* ---- Toast notifications ---- */
function toast(title, msg = "", type = "info") {
  let box = document.getElementById("toasts");
  if (!box) { box = document.createElement("div"); box.id = "toasts"; document.body.appendChild(box); }
  const el = document.createElement("div");
  el.className = "toast " + (type === "info" ? "" : type);
  el.innerHTML = `<div class="bar"></div><div><div class="t-title">${title}</div>${msg ? `<div class="t-msg">${msg}</div>` : ""}</div>`;
  box.appendChild(el);
  setTimeout(() => { el.style.opacity = "0"; el.style.transition = "opacity .3s"; setTimeout(() => el.remove(), 300); }, 3800);
}

/* ---- Fetch wrapper ---- */
async function api(path, opts = {}) {
  try {
    const res = await fetch(path, opts);
    let data = null;
    try { data = await res.json(); } catch (_) {}
    return { ok: res.ok, status: res.status, data };
  } catch (e) {
    return { ok: false, status: 0, data: null, error: e };
  }
}

/* ---- Auth ---- */
function currentUser() {
  return {
    loggedIn: localStorage.getItem("loggedIn") === "true",
    role: localStorage.getItem("role"),
    name: localStorage.getItem("name") || "User",
    email: localStorage.getItem("email") || "",
  };
}
function requireAuth(role) {
  const u = currentUser();
  if (!u.loggedIn || (role && u.role !== role)) { window.location.href = "/"; return null; }
  return u;
}
function logout() { localStorage.clear(); window.location.href = "/"; }
function initials(name) {
  return (name || "U").trim().split(/\s+/).map(w => w[0]).slice(0, 2).join("").toUpperCase();
}

/* ---- Password show/hide toggle ---- */
function togglePassword(btn) {
  const input = btn.parentElement.querySelector("input");
  const show = input.type === "password";
  input.type = show ? "text" : "password";
  btn.innerHTML = show ? ICONS.eyeOff : ICONS.eye;
  btn.setAttribute("aria-label", show ? "Hide password" : "Show password");
}

/* ---- Rendering helpers ---- */
function riskBadge(risk) {
  const r = (risk || "").toUpperCase();
  const cls = r === "HIGH" ? "high" : r === "MEDIUM" ? "medium" : "low";
  return `<span class="badge badge-${cls}"><span class="dot"></span>${r || "LOW"}</span>`;
}
function timeAgo(ts) {
  if (!ts) return "";
  const d = new Date(ts.replace(" ", "T"));
  if (isNaN(d)) return ts;
  const secs = Math.floor((Date.now() - d.getTime()) / 1000);
  if (secs < 60) return "just now";
  const mins = Math.floor(secs / 60);
  if (mins < 60) return mins + "m ago";
  const hrs = Math.floor(mins / 60);
  if (hrs < 24) return hrs + "h ago";
  return Math.floor(hrs / 24) + "d ago";
}
function emptyState(text) {
  return `<div class="empty">${ICONS.empty}<div>${text}</div></div>`;
}

/* ---- App shell: sidebar + topbar + view switching ---- */
function buildShell(user, navItems, defaultView) {
  const nav = navItems.map((n, i) => `
    <button class="nav-item ${i === 0 ? "active" : ""}" data-view="${n.view}" onclick="switchView('${n.view}', this)">
      <span class="nav-ic">${ICONS[n.icon]}</span><span>${n.label}</span>
    </button>`).join("");

  document.getElementById("shell").innerHTML = `
    <aside class="sidebar">
      <div class="sidebar-brand">${brandHTML()}</div>
      <nav class="nav">${nav}</nav>
      <div class="sidebar-foot">
        <div class="user-chip">
          <div class="avatar">${initials(user.name)}</div>
          <div class="meta"><div class="nm">${user.name}</div><div class="rl">${user.role}</div></div>
        </div>
        <button class="btn btn-ghost btn-block" onclick="logout()">${ICONS.logout}<span>Logout</span></button>
      </div>
    </aside>
    <main class="main">
      <header class="topbar"><h1 id="viewTitle">${navItems[0].label}</h1><div id="topActions"></div></header>
      <div class="content" id="content"></div>
    </main>`;
  window.__nav = navItems;
}

function switchView(view, btn) {
  document.querySelectorAll(".view").forEach(v => v.classList.toggle("active", v.id === "view-" + view));
  document.querySelectorAll(".nav-item").forEach(n => n.classList.remove("active"));
  if (btn) btn.classList.add("active");
  const item = (window.__nav || []).find(n => n.view === view);
  if (item) document.getElementById("viewTitle").textContent = item.label;
  window.scrollTo(0, 0);
}
