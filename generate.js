#!/usr/bin/env node
/**
 * D0 Product Kanban Generator
 * Pulls active cycle data from Linear API → generates static HTML kanban
 * Two views: by-layer (五层架构) and by-person (人员维度)
 */

const https = require('https');
const fs = require('fs');

const LINEAR_API_KEY = process.env.LINEAR_API_KEY;
if (!LINEAR_API_KEY) { console.error('Missing LINEAR_API_KEY'); process.exit(1); }

// ── Linear API helper ──────────────────────────────────────────────
function gql(query) {
  return new Promise((resolve, reject) => {
    const data = JSON.stringify({ query });
    const req = https.request({
      hostname: 'api.linear.app',
      path: '/graphql',
      method: 'POST',
      headers: {
        'Authorization': LINEAR_API_KEY,
        'Content-Type': 'application/json',
        'Content-Length': Buffer.byteLength(data),
      },
    }, res => {
      let body = '';
      res.on('data', c => body += c);
      res.on('end', () => {
        try {
          const j = JSON.parse(body);
          if (j.errors) reject(new Error(JSON.stringify(j.errors)));
          else resolve(j.data);
        } catch (e) { reject(e); }
      });
    });
    req.on('error', reject);
    req.write(data);
    req.end();
  });
}

// ── Person → Layer mapping ─────────────────────────────────────────
const LAYER_MAP = {
  // 获客层 Acquisition
  'ruqihu':     'acquisition',
  'melvin':     'acquisition',
  'javier':     'acquisition',
  'hongweifeng':'acquisition',
  'cindytang':  'acquisition',
  // 体验层 Experience
  'zouye':      'experience',
  'gary':       'experience',
  'yixintan':   'experience',
  'jonas':      'experience',
  // AI层
  'jackjun':    'ai',
  'fei':        'ai',
  'xujin':      'ai',
  'lvyang':     'ai',
  'tao':        'ai',
  // 交易层 Trading
  'alex':       'trading',
  'rui li':     'trading',
  'ethan':      'trading',
  'peter':      'trading',
  'sylvia':     'trading',
  'hanliang':   'trading',
  // 基础设施 Infrastructure
  'wenzhang':   'infra',
  'jiagui':     'infra',
  'regison':    'infra',
  // Product (maps to experience by default)
  'justin':     'experience',
  'jim':        'experience',
  'kevin':      'experience',
};

const LAYER_META = {
  acquisition: { name: '获客层 Acquisition', icon: '📣', color: '#3b82f6', bg: 'rgba(59,130,246,.08)' },
  experience:  { name: '体验层 Experience',  icon: '✨', color: '#14b8a6', bg: 'rgba(20,184,166,.08)' },
  ai:          { name: 'AI / Intelligence',   icon: '🧠', color: '#d4a73a', bg: 'rgba(212,167,58,.08)' },
  trading:     { name: '交易层 Trading',      icon: '📊', color: '#ef4444', bg: 'rgba(239,68,68,.08)' },
  infra:       { name: '基础设施 Infra',      icon: '🏗', color: '#a78bfa', bg: 'rgba(167,139,250,.08)' },
};

const DISPLAY_NAMES = {
  'alex': 'Alex', 'ethan': 'Ethan', 'wenzhang': 'Wenzhang', 'xujin': 'Jin Xu',
  'jim': 'Jim', 'justin': 'Justin', 'hanliang': 'Liang Han', 'jiagui': 'Jiagui',
  'fei': 'Fei', 'jackjun': 'JackJun', 'zouye': 'Ye Zou', 'tao': 'Tao',
  'gary': 'Gary', 'jonas': 'Jonas', 'regison': 'Regison', 'peter': 'Peter',
  'sylvia': 'Sylvia', 'ruqihu': 'Ruqi', 'melvin': 'Melvin', 'javier': 'Javier',
  'hongweifeng': 'Hongwei', 'cindytang': 'Cindy', 'yixintan': 'Yi Tan',
  'rui li': 'Rui Li', 'kevin': 'Kevin', 'lvyang': 'Lvyang',
  'unassigned': '⚠ Unassigned',
};

// ── State styling ──────────────────────────────────────────────────
function stateStyle(type, name) {
  const map = {
    completed: { label: '✓ Done',       cls: 'done',    color: '#22c55e' },
    canceled:  { label: '✗ Canceled',   cls: 'cancel',  color: '#6b7280' },
    started:   { label: name || 'In Progress', cls: 'active', color: '#f59e0b' },
    unstarted: { label: name || 'Todo',        cls: 'todo',   color: '#8a9ab5' },
    triage:    { label: 'Triage',       cls: 'triage',  color: '#a78bfa' },
    backlog:   { label: 'Backlog',      cls: 'backlog', color: '#5a6a85' },
  };
  return map[type] || map.backlog;
}

function priorityBadge(label) {
  const map = {
    'Urgent':      { emoji: '🔴', cls: 'p-urgent' },
    'High':        { emoji: '🟠', cls: 'p-high' },
    'Medium':      { emoji: '🟡', cls: 'p-medium' },
    'Low':         { emoji: '🟢', cls: 'p-low' },
    'No priority': { emoji: '⚪', cls: 'p-none' },
  };
  return map[label] || map['No priority'];
}

// ── Fetch data ─────────────────────────────────────────────────────
async function fetchCycleData() {
  // 1. Get active cycles
  const cyclesData = await gql(`{
    cycles(filter: { isActive: { eq: true } }) {
      nodes { id number startsAt endsAt team { key name } }
    }
  }`);
  const cycles = cyclesData.cycles.nodes;
  console.log(`Found ${cycles.length} active cycles: ${cycles.map(c => c.team.key).join(', ')}`);

  // 2. Fetch issues per cycle (avoid complexity limit)
  let allIssues = [];
  for (const cycle of cycles) {
    const data = await gql(`{
      cycle(id: "${cycle.id}") {
        issues(first: 100) {
          nodes {
            identifier title priority priorityLabel
            state { name type }
            assignee { displayName }
            labels { nodes { name } }
            url
          }
        }
      }
    }`);
    const issues = data.cycle.issues.nodes.map(i => ({
      id: i.identifier,
      title: i.title,
      state: i.state.name,
      stateType: i.state.type,
      assignee: (i.assignee?.displayName || 'unassigned').toLowerCase(),
      priority: i.priorityLabel || 'No priority',
      labels: (i.labels?.nodes || []).map(l => l.name),
      team: cycle.team.key,
      url: i.url || `https://linear.app/donutbrowser/issue/${i.identifier}`,
    }));
    allIssues.push(...issues);
    console.log(`  ${cycle.team.key} cycle #${cycle.number}: ${issues.length} issues`);
  }

  return { cycles, issues: allIssues };
}

// ── HTML generation ────────────────────────────────────────────────

function issueCard(issue) {
  const st = stateStyle(issue.stateType, issue.state);
  const pr = priorityBadge(issue.priority);
  const displayAssignee = DISPLAY_NAMES[issue.assignee] || issue.assignee;
  return `
    <div class="card ${st.cls}" data-assignee="${issue.assignee}" data-layer="${LAYER_MAP[issue.assignee] || 'infra'}" data-state="${issue.stateType}">
      <div class="card-head">
        <a href="${issue.url}" target="_blank" class="card-id">${issue.id}</a>
        <span class="card-priority ${pr.cls}">${pr.emoji}</span>
      </div>
      <div class="card-title">${escHtml(issue.title)}</div>
      <div class="card-foot">
        <span class="card-assignee">${escHtml(displayAssignee)}</span>
        <span class="card-state" style="color:${st.color}">${st.label}</span>
      </div>
    </div>`;
}

function escHtml(s) {
  return s.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;');
}

function generateHTML(data) {
  const { cycles, issues } = data;
  const now = new Date().toISOString().slice(0, 10);

  // Separate active (non-completed/canceled) vs done
  const active = issues.filter(i => !['completed','canceled'].includes(i.stateType));
  const done = issues.filter(i => i.stateType === 'completed');
  const canceled = issues.filter(i => i.stateType === 'canceled');

  // ── By-Layer view ──
  const byLayer = {};
  for (const layer of Object.keys(LAYER_META)) byLayer[layer] = [];
  for (const i of issues) {
    const layer = LAYER_MAP[i.assignee] || 'infra';
    byLayer[layer].push(i);
  }

  // ── By-Person view ──
  const byPerson = {};
  for (const i of issues) {
    if (!byPerson[i.assignee]) byPerson[i.assignee] = [];
    byPerson[i.assignee].push(i);
  }
  // Sort people by issue count desc
  const sortedPeople = Object.entries(byPerson).sort((a,b) => b[1].length - a[1].length);

  // ── Stats ──
  const totalIssues = issues.length;
  const doneCount = done.length;
  const activeCount = active.length;
  const uniquePeople = new Set(issues.map(i => i.assignee).filter(a => a !== 'unassigned')).size;

  const cycleInfo = cycles.map(c => `${c.team.key} #${c.number}`).join(' · ');
  const cycleRange = cycles.length > 0 ?
    `${cycles[0].startsAt.slice(0,10)} → ${cycles[0].endsAt.slice(0,10)}` : '';

  // ── Build layer sections ──
  let layerSections = '';
  for (const [key, meta] of Object.entries(LAYER_META)) {
    const layerIssues = byLayer[key] || [];
    const layerActive = layerIssues.filter(i => !['completed','canceled'].includes(i.stateType));
    const layerDone = layerIssues.filter(i => i.stateType === 'completed');
    layerSections += `
      <div class="layer-section" style="--layer-color:${meta.color};--layer-bg:${meta.bg}">
        <div class="layer-head">
          <span class="layer-icon">${meta.icon}</span>
          <span class="layer-name">${meta.name}</span>
          <span class="layer-count">${layerActive.length} active · ${layerDone.length} done</span>
        </div>
        <div class="card-grid">
          ${layerIssues.filter(i => i.stateType !== 'canceled').map(issueCard).join('')}
        </div>
      </div>`;
  }

  // ── Build person sections ──
  let personSections = '';
  for (const [person, pIssues] of sortedPeople) {
    const displayName = DISPLAY_NAMES[person] || person;
    const layer = LAYER_MAP[person] || 'infra';
    const layerMeta = LAYER_META[layer];
    const pActive = pIssues.filter(i => !['completed','canceled'].includes(i.stateType));
    const pDone = pIssues.filter(i => i.stateType === 'completed');
    personSections += `
      <div class="person-section" style="--layer-color:${layerMeta.color};--layer-bg:${layerMeta.bg}">
        <div class="person-head">
          <span class="person-name">${escHtml(displayName)}</span>
          <span class="person-layer" style="color:${layerMeta.color}">${layerMeta.icon} ${layerMeta.name}</span>
          <span class="person-count">${pActive.length} active · ${pDone.length} done</span>
        </div>
        <div class="card-grid">
          ${pIssues.filter(i => i.stateType !== 'canceled').map(issueCard).join('')}
        </div>
      </div>`;
  }

  return `<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>D0 Product Kanban — Linear Cycle View</title>
<link href="https://fonts.googleapis.com/css2?family=Instrument+Serif:ital@0;1&family=JetBrains+Mono:wght@400;500;600;700&family=DM+Sans:wght@400;500;600;700&display=swap" rel="stylesheet">
<style>
:root{--bg:#0c1220;--surface:#131d32;--s2:#182640;--s3:#1e304e;--border:rgba(255,255,255,.06);--ba:rgba(212,167,58,.3);--text:#e8e4dc;--dim:#8a9ab5;--muted:#5a6a85;--gold:#d4a73a;--gd:rgba(212,167,58,.1);--red:#ef4444;--rd:rgba(239,68,68,.1);--green:#22c55e;--grd:rgba(34,197,94,.1);--amber:#f59e0b;--ad:rgba(245,158,11,.1);--blue:#3b82f6;--bd:rgba(59,130,246,.1);--teal:#14b8a6;--td:rgba(20,184,166,.1);--purple:#a78bfa;--pd:rgba(167,139,250,.1);--fd:'Instrument Serif',Georgia,serif;--fb:'DM Sans',system-ui,sans-serif;--fm:'JetBrains Mono',monospace}
@media(prefers-color-scheme:light){:root{--bg:#f4f0e6;--surface:#fff;--s2:#f8f5ee;--s3:#efe9dd;--border:rgba(0,0,0,.07);--ba:rgba(180,130,30,.25);--text:#1a1a2e;--dim:#5a5a7a;--muted:#9a9ab0;--green:#16a34a;--red:#dc2626;--amber:#d97706;--blue:#2563eb;--teal:#0d9488;--purple:#7c3aed;--gold:#b8860b}}
*,*::before,*::after{box-sizing:border-box;margin:0;padding:0}
body{font-family:var(--fb);background:var(--bg);color:var(--text);line-height:1.5;-webkit-font-smoothing:antialiased}
.page{max-width:1400px;margin:0 auto;padding:1.5rem}

/* HERO */
.hero{text-align:center;padding:1.5rem 0 .5rem}
.hero h1{font-family:var(--fd);font-size:2.2rem;font-weight:400}
.hero .sub{font-family:var(--fm);font-size:.72rem;color:var(--dim);margin-top:.25rem}
.hero .badge{display:inline-block;margin-top:.4rem;padding:.15rem .7rem;background:var(--gd);color:var(--gold);font-family:var(--fm);font-size:.65rem;border-radius:100px;border:1px solid var(--ba)}

/* STATS BAR */
.stats{display:flex;gap:.5rem;justify-content:center;flex-wrap:wrap;margin:1rem 0 1.5rem}
.stat{text-align:center;padding:.5rem 1rem;background:var(--surface);border:1px solid var(--border);border-radius:8px;min-width:100px}
.stat .num{font-family:var(--fm);font-size:1.3rem;font-weight:700;color:var(--gold)}
.stat .label{font-size:.68rem;color:var(--dim)}

/* VIEW TOGGLE */
.toggle-bar{display:flex;justify-content:center;gap:.3rem;margin-bottom:1.5rem}
.toggle-btn{font-family:var(--fm);font-size:.72rem;padding:.4rem 1rem;border-radius:100px;border:1px solid var(--border);background:var(--surface);color:var(--dim);cursor:pointer;transition:all .2s}
.toggle-btn:hover{border-color:var(--gold);color:var(--gold)}
.toggle-btn.active{background:var(--gd);color:var(--gold);border-color:var(--ba)}

/* FILTER BAR */
.filter-bar{display:flex;justify-content:center;gap:.3rem;margin-bottom:1.5rem;flex-wrap:wrap}
.filter-btn{font-family:var(--fm);font-size:.65rem;padding:.25rem .7rem;border-radius:100px;border:1px solid var(--border);background:var(--surface);color:var(--dim);cursor:pointer;transition:all .2s}
.filter-btn:hover{border-color:var(--gold);color:var(--text)}
.filter-btn.active{background:var(--s2);color:var(--text);border-color:var(--gold)}

/* LAYER SECTION */
.layer-section,.person-section{margin-bottom:1.5rem}
.layer-head,.person-head{display:flex;align-items:center;gap:.5rem;padding:.5rem .8rem;margin-bottom:.5rem;border-bottom:2px solid var(--layer-color,var(--gold))}
.layer-icon{font-size:1.1rem}
.layer-name,.person-name{font-family:var(--fd);font-size:1.2rem;font-weight:400}
.layer-count,.person-count{font-family:var(--fm);font-size:.65rem;color:var(--muted);margin-left:auto}
.person-layer{font-family:var(--fm);font-size:.65rem;margin-left:.5rem}

/* CARD GRID */
.card-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(280px,1fr));gap:.5rem}

/* CARD */
.card{background:var(--surface);border:1px solid var(--border);border-radius:8px;padding:.6rem .8rem;transition:all .2s;border-left:3px solid var(--layer-color,var(--border))}
.card:hover{border-color:var(--ba);transform:translateY(-1px);box-shadow:0 4px 12px rgba(0,0,0,.2)}
.card.done{opacity:.55}
.card.cancel{opacity:.35;text-decoration:line-through}
.card-head{display:flex;align-items:center;justify-content:space-between;margin-bottom:.25rem}
.card-id{font-family:var(--fm);font-size:.65rem;color:var(--gold);text-decoration:none}
.card-id:hover{text-decoration:underline}
.card-priority{font-size:.7rem}
.card-title{font-size:.82rem;line-height:1.4;margin-bottom:.3rem;display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;overflow:hidden}
.card-foot{display:flex;align-items:center;justify-content:space-between;gap:.5rem}
.card-assignee{font-family:var(--fm);font-size:.62rem;color:var(--dim);background:var(--s2);padding:.1rem .4rem;border-radius:100px}
.card-state{font-family:var(--fm);font-size:.62rem;font-weight:600}

/* VIEWS */
#view-layer,#view-person{display:none}
#view-layer.active,#view-person.active{display:block}

/* FOOTER */
.footer{text-align:center;padding:1.5rem 0 .5rem;font-family:var(--fm);font-size:.62rem;color:var(--muted)}
.footer a{color:var(--gold);text-decoration:none}

@media(max-width:700px){.card-grid{grid-template-columns:1fr}.stats{gap:.3rem}.stat{min-width:70px;padding:.4rem .6rem}}
@keyframes fadeUp{from{opacity:0;transform:translateY(8px)}to{opacity:1;transform:translateY(0)}}
.anim{animation:fadeUp .35s ease-out both}
</style>
</head>
<body>
<div class="page">

<div class="hero anim">
  <h1>D0 Product Kanban</h1>
  <div class="sub">Linear Cycle 联动 · ${cycleInfo} · ${cycleRange}</div>
  <div class="badge">Generated ${now} · Ring for Donut</div>
</div>

<div class="stats anim">
  <div class="stat"><div class="num">${totalIssues}</div><div class="label">Total Issues</div></div>
  <div class="stat"><div class="num">${activeCount}</div><div class="label">Active</div></div>
  <div class="stat"><div class="num">${doneCount}</div><div class="label">Done</div></div>
  <div class="stat"><div class="num">${canceled.length}</div><div class="label">Canceled</div></div>
  <div class="stat"><div class="num">${uniquePeople}</div><div class="label">People</div></div>
</div>

<div class="toggle-bar anim">
  <button class="toggle-btn active" onclick="switchView('layer')">🏗 五层架构</button>
  <button class="toggle-btn" onclick="switchView('person')">👤 按人员</button>
</div>

<div class="filter-bar anim">
  <button class="filter-btn active" data-filter="all" onclick="filterState('all')">All</button>
  <button class="filter-btn" data-filter="active" onclick="filterState('active')">🔥 Active</button>
  <button class="filter-btn" data-filter="done" onclick="filterState('done')">✓ Done</button>
</div>

<div id="view-layer" class="active anim">
  ${layerSections}
</div>

<div id="view-person" class="anim">
  ${personSections}
</div>

<div class="footer">
  Auto-generated from <a href="https://linear.app/donutbrowser">Linear</a> active cycles · Updated every 6h via GitHub Actions
</div>

</div>

<script>
function switchView(view) {
  document.querySelectorAll('.toggle-btn').forEach(b => b.classList.remove('active'));
  document.querySelectorAll('#view-layer,#view-person').forEach(v => v.classList.remove('active'));
  document.getElementById('view-' + view).classList.add('active');
  event.target.classList.add('active');
}

function filterState(filter) {
  document.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
  event.target.classList.add('active');
  document.querySelectorAll('.card').forEach(card => {
    const state = card.dataset.state;
    if (filter === 'all') card.style.display = '';
    else if (filter === 'active') card.style.display = ['completed','canceled'].includes(state) ? 'none' : '';
    else if (filter === 'done') card.style.display = state === 'completed' ? '' : 'none';
  });
}
</script>
</body>
</html>`;
}

// ── Main ───────────────────────────────────────────────────────────
(async () => {
  try {
    const data = await fetchCycleData();
    const html = generateHTML(data);
    fs.writeFileSync('index.html', html);
    console.log(`✓ Generated index.html (${(html.length / 1024).toFixed(1)} KB) with ${data.issues.length} issues`);
  } catch (e) {
    console.error('Error:', e.message);
    process.exit(1);
  }
})();
