#!/usr/bin/env node
/**
 * D0 Product Kanban Generator v2
 * Pulls active cycle data from Linear API → generates static HTML kanban
 * Two views: by-layer (五层架构) and by-person (人员维度)
 * Styled with Donut Design System
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

// ── Person → Layer mapping (based on actual work, not just org chart) ──
// Issues can also be tagged by keyword matching for cross-layer accuracy
const PERSON_DEFAULT_LAYER = {
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
  'sylvia':     'experience',
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
  'hanliang':   'trading',
  // 基础设施 Infrastructure
  'wenzhang':   'infra',
  'jiagui':     'infra',
  'regison':    'infra',
  // Cross-layer people (default, but issues get re-mapped by keywords)
  'justin':     'experience',
  'jim':        'infra',  // QA, cross-layer
  'kevin':      'infra',  // QA, cross-layer
};

// Keyword-based layer detection (overrides person default when matched)
const LAYER_KEYWORDS = {
  infra: ['k8s', 'kubernetes', 'infra', 'replica', 'pdb', 'argocd', 'helm', 'deploy', 'node编排',
          'monitoring', '监控', 'env管理', '.env', 'rolling update', 'draining', 'workspace-sync',
          'qmd embed', 'bm25', 'shared 模式', 'nofx'],
  trading: ['trading', 'tpsl', 'perps', 'swap', 'transfer', 'withdraw', 'deposit', '平仓', '止盈止损',
            'grps', '风控', '撮合', 'polymarket', 'hummingbot', 'birdeye', 'ohlcv', 'agents-backend',
            'build-transfer', 'helius'],
  ai: ['llm', 'prompt', 'eval', 'model', 'ai', 'd0-cli', '记忆系统', 'memory', 'frontier',
       'data source', 'user scenario'],
  experience: ['onboarding', 'dashboard', 'ui', 'ux', '简报', 'briefing', 'token 用量', '配额',
               'tgbot', '消息顺序', 'profile plugin', 'sqlite', 'user profile'],
  acquisition: ['seo', 'ugc', 'kol', '增长', 'growth', 'social', 'community'],
};

function detectLayer(issue) {
  const text = (issue.title + ' ' + issue.labels.join(' ')).toLowerCase();
  // Check keywords first (more accurate than person default)
  for (const [layer, keywords] of Object.entries(LAYER_KEYWORDS)) {
    for (const kw of keywords) {
      if (text.includes(kw.toLowerCase())) return layer;
    }
  }
  // Fall back to person default
  return PERSON_DEFAULT_LAYER[issue.assignee] || 'infra';
}

const LAYER_META = {
  acquisition: { name: '获客层', sub: 'Acquisition', icon: '📣', color: '#3b82f6', bg: 'rgba(59,130,246,.06)', gradient: 'linear-gradient(135deg, rgba(59,130,246,.08), rgba(59,130,246,.02))' },
  experience:  { name: '体验层', sub: 'Experience',  icon: '✨', color: '#14b8a6', bg: 'rgba(20,184,166,.06)', gradient: 'linear-gradient(135deg, rgba(20,184,166,.08), rgba(20,184,166,.02))' },
  ai:          { name: 'AI 层',  sub: 'Intelligence', icon: '🧠', color: '#f59e0b', bg: 'rgba(245,158,11,.06)', gradient: 'linear-gradient(135deg, rgba(245,158,11,.08), rgba(245,158,11,.02))' },
  trading:     { name: '交易层', sub: 'Trading',      icon: '📊', color: '#ef4444', bg: 'rgba(239,68,68,.06)', gradient: 'linear-gradient(135deg, rgba(239,68,68,.08), rgba(239,68,68,.02))' },
  infra:       { name: '基础设施', sub: 'Infrastructure', icon: '🏗', color: '#a78bfa', bg: 'rgba(167,139,250,.06)', gradient: 'linear-gradient(135deg, rgba(167,139,250,.08), rgba(167,139,250,.02))' },
};

const DISPLAY_NAMES = {
  'alex': 'Alex', 'ethan': 'Ethan', 'wenzhang': 'Wenzhang', 'xujin': 'Jin Xu',
  'jim': 'Jim', 'justin': 'Justin', 'hanliang': 'Liang Han', 'jiagui': 'Jiagui',
  'fei': 'Fei', 'jackjun': 'JackJun', 'zouye': 'Ye Zou', 'tao': 'Tao',
  'gary': 'Gary', 'jonas': 'Jonas', 'regison': 'Regison', 'peter': 'Peter',
  'sylvia': 'Sylvia', 'ruqihu': 'Ruqi', 'melvin': 'Melvin', 'javier': 'Javier',
  'hongweifeng': 'Hongwei', 'cindytang': 'Cindy', 'yixintan': 'Yi Tan',
  'rui li': 'Rui Li', 'kevin': 'Kevin', 'lvyang': 'Lvyang',
  'unassigned': 'Unassigned',
};

function stateStyle(type, name) {
  const map = {
    completed: { label: 'Done',        cls: 'done',    color: '#22c55e', icon: '✓' },
    canceled:  { label: 'Canceled',    cls: 'cancel',  color: '#52525b', icon: '✗' },
    started:   { label: name || 'In Progress', cls: 'active', color: '#f59e0b', icon: '◉' },
    unstarted: { label: name || 'Todo',        cls: 'todo',   color: '#71717a', icon: '○' },
    triage:    { label: 'Triage',      cls: 'triage',  color: '#a78bfa', icon: '◎' },
    backlog:   { label: 'Backlog',     cls: 'backlog', color: '#52525b', icon: '·' },
  };
  return map[type] || map.backlog;
}

function priorityBadge(label) {
  const map = {
    'Urgent':      { dot: '#ef4444', cls: 'p-urgent' },
    'High':        { dot: '#f59e0b', cls: 'p-high' },
    'Medium':      { dot: '#3b82f6', cls: 'p-medium' },
    'Low':         { dot: '#22c55e', cls: 'p-low' },
    'No priority': { dot: '#52525b', cls: 'p-none' },
  };
  return map[label] || map['No priority'];
}

// ── Fetch data ─────────────────────────────────────────────────────
async function fetchCycleData() {
  const cyclesData = await gql(`{
    cycles(filter: { isActive: { eq: true } }) {
      nodes { id number startsAt endsAt team { key name } }
    }
  }`);
  const cycles = cyclesData.cycles.nodes;
  console.log(`Found ${cycles.length} active cycles: ${cycles.map(c => c.team.key).join(', ')}`);

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

  // Detect layer for each issue
  for (const i of allIssues) {
    i.layer = detectLayer(i);
  }

  return { cycles, issues: allIssues };
}

// ── HTML generation ────────────────────────────────────────────────
function escHtml(s) {
  return s.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;');
}

function issueCard(issue) {
  const st = stateStyle(issue.stateType, issue.state);
  const pr = priorityBadge(issue.priority);
  const displayAssignee = DISPLAY_NAMES[issue.assignee] || issue.assignee;
  const layerMeta = LAYER_META[issue.layer];
  return `
    <div class="card ${st.cls}" data-assignee="${issue.assignee}" data-layer="${issue.layer}" data-state="${issue.stateType}">
      <div class="card-head">
        <a href="${issue.url}" target="_blank" rel="noopener" class="card-id">${issue.id}</a>
        <span class="priority-dot" style="background:${pr.dot}"></span>
      </div>
      <div class="card-title">${escHtml(issue.title)}</div>
      <div class="card-foot">
        <span class="card-assignee">${escHtml(displayAssignee)}</span>
        <span class="card-state" style="--state-color:${st.color}">${st.icon} ${st.label}</span>
      </div>
    </div>`;
}

function progressBar(active, done, total) {
  if (total === 0) return '';
  const donePct = Math.round((done / total) * 100);
  const activePct = Math.round((active / total) * 100);
  return `<div class="progress-bar">
    <div class="progress-done" style="width:${donePct}%"></div>
    <div class="progress-active" style="width:${activePct}%"></div>
  </div>`;
}

// Sort: active first (by priority), then todo, then done
function sortIssues(issues) {
  const stateOrder = { started: 0, triage: 1, unstarted: 2, completed: 3, canceled: 4, backlog: 5 };
  const prioOrder = { 'Urgent': 0, 'High': 1, 'Medium': 2, 'Low': 3, 'No priority': 4 };
  return [...issues].sort((a, b) => {
    const sd = (stateOrder[a.stateType] ?? 5) - (stateOrder[b.stateType] ?? 5);
    if (sd !== 0) return sd;
    return (prioOrder[a.priority] ?? 4) - (prioOrder[b.priority] ?? 4);
  });
}

function generateHTML(data) {
  const { cycles, issues } = data;
  const now = new Date().toISOString().slice(0, 10);

  const active = issues.filter(i => !['completed','canceled'].includes(i.stateType));
  const done = issues.filter(i => i.stateType === 'completed');
  const canceled = issues.filter(i => i.stateType === 'canceled');

  // By-Layer (using keyword-detected layer, not just person default)
  const byLayer = {};
  for (const layer of Object.keys(LAYER_META)) byLayer[layer] = [];
  for (const i of issues) byLayer[i.layer].push(i);

  // By-Person
  const byPerson = {};
  for (const i of issues) {
    if (!byPerson[i.assignee]) byPerson[i.assignee] = [];
    byPerson[i.assignee].push(i);
  }
  // Sort by active count desc, then total
  const sortedPeople = Object.entries(byPerson).sort((a,b) => {
    const aActive = a[1].filter(i => !['completed','canceled'].includes(i.stateType)).length;
    const bActive = b[1].filter(i => !['completed','canceled'].includes(i.stateType)).length;
    if (bActive !== aActive) return bActive - aActive;
    return b[1].length - a[1].length;
  });

  const totalIssues = issues.length;
  const doneCount = done.length;
  const activeCount = active.length;
  const uniquePeople = new Set(issues.map(i => i.assignee).filter(a => a !== 'unassigned')).size;
  const completionPct = totalIssues > 0 ? Math.round((doneCount / totalIssues) * 100) : 0;

  const cycleInfo = cycles.filter(c => c.team.key === 'ENG').map(c => `Sprint ${c.number}`).join(', ') || 'Current Cycle';
  const cycleRange = cycles.length > 0 ?
    `${fmtDate(cycles[0].startsAt)} → ${fmtDate(cycles[0].endsAt)}` : '';

  // Layer sections
  let layerSections = '';
  for (const [key, meta] of Object.entries(LAYER_META)) {
    const layerIssues = sortIssues(byLayer[key] || []);
    const lActive = layerIssues.filter(i => !['completed','canceled'].includes(i.stateType));
    const lDone = layerIssues.filter(i => i.stateType === 'completed');
    const isEmpty = layerIssues.length === 0;
    layerSections += `
      <div class="section" style="--accent:${meta.color};--accent-bg:${meta.bg}">
        <div class="section-head">
          <div class="section-title">
            <span class="section-icon">${meta.icon}</span>
            <span class="section-name">${meta.name}</span>
            <span class="section-sub">${meta.sub}</span>
          </div>
          <div class="section-meta">
            <span class="meta-count">${lActive.length} active</span>
            <span class="meta-sep">·</span>
            <span class="meta-count">${lDone.length} done</span>
          </div>
        </div>
        ${progressBar(lActive.length, lDone.length, layerIssues.length)}
        ${isEmpty
          ? '<div class="empty-state">当前 Cycle 暂无 issue</div>'
          : `<div class="card-grid">${layerIssues.filter(i => i.stateType !== 'canceled').map(issueCard).join('')}</div>`
        }
      </div>`;
  }

  // Person sections
  let personSections = '';
  for (const [person, pIssues] of sortedPeople) {
    const displayName = DISPLAY_NAMES[person] || person;
    // Use most common layer for this person's issues
    const layerCounts = {};
    for (const i of pIssues) layerCounts[i.layer] = (layerCounts[i.layer] || 0) + 1;
    const primaryLayer = Object.entries(layerCounts).sort((a,b) => b[1]-a[1])[0]?.[0] || 'infra';
    const layerMeta = LAYER_META[primaryLayer];
    const pActive = pIssues.filter(i => !['completed','canceled'].includes(i.stateType));
    const pDone = pIssues.filter(i => i.stateType === 'completed');
    const sorted = sortIssues(pIssues);
    personSections += `
      <div class="section" style="--accent:${layerMeta.color};--accent-bg:${layerMeta.bg}">
        <div class="section-head">
          <div class="section-title">
            <span class="person-avatar">${displayName.charAt(0).toUpperCase()}</span>
            <span class="section-name">${escHtml(displayName)}</span>
            <span class="section-sub" style="color:${layerMeta.color}">${layerMeta.icon} ${layerMeta.name}</span>
          </div>
          <div class="section-meta">
            <span class="meta-count">${pActive.length} active</span>
            <span class="meta-sep">·</span>
            <span class="meta-count">${pDone.length} done</span>
          </div>
        </div>
        ${progressBar(pActive.length, pDone.length, pIssues.length)}
        <div class="card-grid">
          ${sorted.filter(i => i.stateType !== 'canceled').map(issueCard).join('')}
        </div>
      </div>`;
  }

  return `<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>D0 Sprint Board — ${cycleInfo}</title>
<link href="https://fonts.googleapis.com/css2?family=Instrument+Serif:ital@0;1&family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500;600&display=swap" rel="stylesheet">
<style>
/* ── Design System Tokens ──────────────────────────────── */
:root {
  /* Background layers */
  --bg-base: #09090b;
  --bg-subtle: #18181b;
  --bg-muted: #27272a;
  --bg-emphasis: #3f3f46;

  /* Foreground */
  --fg-base: #fafafa;
  --fg-muted: #a1a1aa;
  --fg-subtle: #71717a;
  --fg-faint: #52525b;

  /* Borders */
  --border-base: #27272a;
  --border-emphasis: #3f3f46;

  /* Semantic */
  --success: #22c55e;
  --warning: #f59e0b;
  --error: #ef4444;
  --info: #3b82f6;

  /* Typography */
  --font-display: 'Instrument Serif', Georgia, serif;
  --font-sans: 'Inter', system-ui, -apple-system, sans-serif;
  --font-mono: 'JetBrains Mono', 'SF Mono', monospace;

  /* Spacing (4px base) */
  --space-1: 0.25rem;
  --space-2: 0.5rem;
  --space-3: 0.75rem;
  --space-4: 1rem;
  --space-6: 1.5rem;
  --space-8: 2rem;
  --space-12: 3rem;
  --space-16: 4rem;

  /* Radius */
  --radius-sm: 6px;
  --radius-md: 8px;
  --radius-lg: 12px;

  /* Motion */
  --ease-out: cubic-bezier(0.16, 1, 0.3, 1);
  --duration-fast: 100ms;
  --duration-normal: 200ms;
}

@media (prefers-color-scheme: light) {
  :root {
    --bg-base: #fafafa;
    --bg-subtle: #ffffff;
    --bg-muted: #f4f4f5;
    --bg-emphasis: #e4e4e7;
    --fg-base: #09090b;
    --fg-muted: #71717a;
    --fg-subtle: #a1a1aa;
    --fg-faint: #d4d4d8;
    --border-base: #e4e4e7;
    --border-emphasis: #d4d4d8;
  }
}

/* ── Reset ─────────────────────────────────────────────── */
*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0 }
body {
  font-family: var(--font-sans);
  background: var(--bg-base);
  color: var(--fg-base);
  line-height: 1.5;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}
.page { max-width: 1280px; margin: 0 auto; padding: var(--space-6) }

/* ── Header ────────────────────────────────────────────── */
.header {
  text-align: center;
  padding: var(--space-8) 0 var(--space-4);
}
.header h1 {
  font-family: var(--font-display);
  font-size: 2.5rem;
  font-weight: 400;
  letter-spacing: -0.02em;
  line-height: 1.1;
}
.header .subtitle {
  font-family: var(--font-mono);
  font-size: 0.75rem;
  color: var(--fg-subtle);
  margin-top: var(--space-2);
  letter-spacing: 0.02em;
}
.header .cycle-badge {
  display: inline-flex;
  align-items: center;
  gap: var(--space-2);
  margin-top: var(--space-3);
  padding: var(--space-1) var(--space-4);
  background: var(--bg-subtle);
  border: 1px solid var(--border-base);
  border-radius: 100px;
  font-family: var(--font-mono);
  font-size: 0.68rem;
  color: var(--fg-muted);
}
.cycle-badge .pulse {
  width: 6px; height: 6px;
  background: var(--success);
  border-radius: 50%;
  animation: pulse 2s ease-in-out infinite;
}
@keyframes pulse { 0%,100% { opacity: 1 } 50% { opacity: .4 } }

/* ── Stats ─────────────────────────────────────────────── */
.stats {
  display: flex;
  gap: var(--space-3);
  justify-content: center;
  flex-wrap: wrap;
  margin: var(--space-6) 0;
}
.stat {
  text-align: center;
  padding: var(--space-3) var(--space-6);
  background: var(--bg-subtle);
  border: 1px solid var(--border-base);
  border-radius: var(--radius-lg);
  min-width: 110px;
  transition: border-color var(--duration-normal) var(--ease-out);
}
.stat:hover { border-color: var(--border-emphasis) }
.stat .num {
  font-family: var(--font-mono);
  font-size: 1.5rem;
  font-weight: 700;
  line-height: 1;
}
.stat .label {
  font-size: 0.68rem;
  color: var(--fg-subtle);
  margin-top: var(--space-1);
}

/* ── Controls ──────────────────────────────────────────── */
.controls {
  display: flex;
  justify-content: center;
  gap: var(--space-2);
  margin-bottom: var(--space-6);
  flex-wrap: wrap;
}
.ctrl-group {
  display: flex;
  gap: 1px;
  background: var(--border-base);
  border-radius: 100px;
  overflow: hidden;
}
.ctrl-btn {
  font-family: var(--font-sans);
  font-size: 0.75rem;
  font-weight: 500;
  padding: var(--space-2) var(--space-4);
  background: var(--bg-subtle);
  color: var(--fg-muted);
  border: none;
  cursor: pointer;
  transition: all var(--duration-fast);
  white-space: nowrap;
}
.ctrl-btn:hover { color: var(--fg-base); background: var(--bg-muted) }
.ctrl-btn.active {
  color: var(--fg-base);
  background: var(--bg-muted);
}

/* ── Section ───────────────────────────────────────────── */
.section {
  margin-bottom: var(--space-8);
  animation: fadeUp 0.4s var(--ease-out) both;
}
.section-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: var(--space-3) 0;
  border-bottom: 1px solid var(--border-base);
  margin-bottom: var(--space-3);
}
.section-title {
  display: flex;
  align-items: center;
  gap: var(--space-3);
}
.section-icon { font-size: 1.2rem }
.section-name {
  font-family: var(--font-display);
  font-size: 1.3rem;
  font-weight: 400;
}
.section-sub {
  font-family: var(--font-mono);
  font-size: 0.65rem;
  color: var(--fg-subtle);
  text-transform: uppercase;
  letter-spacing: 0.05em;
}
.section-meta {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  font-family: var(--font-mono);
  font-size: 0.65rem;
  color: var(--fg-subtle);
}
.meta-sep { opacity: 0.3 }

/* Person avatar */
.person-avatar {
  width: 28px;
  height: 28px;
  border-radius: 50%;
  background: var(--accent, var(--bg-muted));
  color: var(--bg-base);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.72rem;
  font-weight: 600;
  flex-shrink: 0;
}

/* ── Progress Bar ──────────────────────────────────────── */
.progress-bar {
  height: 2px;
  background: var(--bg-muted);
  border-radius: 1px;
  display: flex;
  overflow: hidden;
  margin-bottom: var(--space-4);
}
.progress-done {
  background: var(--success);
  transition: width 0.6s var(--ease-out);
}
.progress-active {
  background: var(--warning);
  transition: width 0.6s var(--ease-out);
}

/* ── Card Grid ─────────────────────────────────────────── */
.card-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: var(--space-3);
}

/* ── Card ──────────────────────────────────────────────── */
.card {
  background: var(--bg-subtle);
  border: 1px solid var(--border-base);
  border-radius: var(--radius-md);
  padding: var(--space-3) var(--space-4);
  transition: all var(--duration-normal) var(--ease-out);
  position: relative;
}
.card::before {
  content: '';
  position: absolute;
  left: 0;
  top: 0;
  bottom: 0;
  width: 3px;
  background: var(--accent, var(--fg-faint));
  border-radius: var(--radius-md) 0 0 var(--radius-md);
  opacity: 0.6;
}
.card:hover {
  border-color: var(--border-emphasis);
  transform: translateY(-1px);
  box-shadow: 0 4px 20px rgba(0,0,0,.15);
}
.card.done { opacity: 0.5 }
.card.done:hover { opacity: 0.7 }
.card.cancel { opacity: 0.3 }
.card-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: var(--space-1);
}
.card-id {
  font-family: var(--font-mono);
  font-size: 0.65rem;
  color: var(--fg-subtle);
  text-decoration: none;
  transition: color var(--duration-fast);
}
.card-id:hover { color: var(--fg-base) }
.priority-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  flex-shrink: 0;
}
.card-title {
  font-size: 0.82rem;
  font-weight: 500;
  line-height: 1.4;
  margin-bottom: var(--space-2);
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
.card-foot {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: var(--space-2);
}
.card-assignee {
  font-family: var(--font-mono);
  font-size: 0.62rem;
  color: var(--fg-subtle);
  background: var(--bg-muted);
  padding: 2px var(--space-2);
  border-radius: 100px;
}
.card-state {
  font-family: var(--font-mono);
  font-size: 0.62rem;
  font-weight: 500;
  color: var(--state-color, var(--fg-subtle));
}

/* ── Empty State ───────────────────────────────────────── */
.empty-state {
  text-align: center;
  padding: var(--space-8) var(--space-4);
  color: var(--fg-faint);
  font-size: 0.82rem;
  font-style: italic;
}

/* ── Views ─────────────────────────────────────────────── */
#view-layer, #view-person { display: none }
#view-layer.active, #view-person.active { display: block }

/* ── Footer ────────────────────────────────────────────── */
.footer {
  text-align: center;
  padding: var(--space-8) 0 var(--space-4);
  font-family: var(--font-mono);
  font-size: 0.62rem;
  color: var(--fg-faint);
}
.footer a { color: var(--fg-subtle); text-decoration: none }
.footer a:hover { color: var(--fg-base) }

/* ── Responsive ────────────────────────────────────────── */
@media (max-width: 700px) {
  .page { padding: var(--space-4) }
  .card-grid { grid-template-columns: 1fr }
  .stats { gap: var(--space-2) }
  .stat { min-width: 80px; padding: var(--space-2) var(--space-4) }
  .header h1 { font-size: 1.8rem }
}

@keyframes fadeUp {
  from { opacity: 0; transform: translateY(8px) }
  to { opacity: 1; transform: translateY(0) }
}
@media (prefers-reduced-motion: reduce) { .section { animation: none } }
</style>
</head>
<body>
<div class="page">

  <header class="header">
    <h1>D0 Sprint Board</h1>
    <div class="subtitle">${cycleInfo} · ${cycleRange}</div>
    <div class="cycle-badge">
      <span class="pulse"></span>
      Last synced ${now}
    </div>
  </header>

  <div class="stats">
    <div class="stat"><div class="num">${totalIssues}</div><div class="label">Total</div></div>
    <div class="stat"><div class="num" style="color:var(--warning)">${activeCount}</div><div class="label">Active</div></div>
    <div class="stat"><div class="num" style="color:var(--success)">${doneCount}</div><div class="label">Done</div></div>
    <div class="stat"><div class="num">${completionPct}%</div><div class="label">Completion</div></div>
    <div class="stat"><div class="num">${uniquePeople}</div><div class="label">People</div></div>
  </div>

  <div class="controls">
    <div class="ctrl-group">
      <button class="ctrl-btn active" onclick="switchView('layer')">🏗 五层架构</button>
      <button class="ctrl-btn" onclick="switchView('person')">👤 按人员</button>
    </div>
    <div class="ctrl-group">
      <button class="ctrl-btn active" data-filter="all" onclick="filterState('all')">All</button>
      <button class="ctrl-btn" data-filter="active" onclick="filterState('active')">Active</button>
      <button class="ctrl-btn" data-filter="done" onclick="filterState('done')">Done</button>
    </div>
  </div>

  <div id="view-layer" class="active">
    ${layerSections}
  </div>

  <div id="view-person">
    ${personSections}
  </div>

  <div class="footer">
    Auto-synced from <a href="https://linear.app/donutbrowser">Linear</a> active cycles
  </div>

</div>

<script>
function switchView(view) {
  document.querySelectorAll('.ctrl-group:first-child .ctrl-btn').forEach(b => b.classList.remove('active'));
  document.querySelectorAll('#view-layer,#view-person').forEach(v => v.classList.remove('active'));
  document.getElementById('view-' + view).classList.add('active');
  event.currentTarget.classList.add('active');
}

function filterState(filter) {
  document.querySelectorAll('.ctrl-group:last-child .ctrl-btn').forEach(b => b.classList.remove('active'));
  event.currentTarget.classList.add('active');
  document.querySelectorAll('.card').forEach(card => {
    const state = card.dataset.state;
    if (filter === 'all') card.style.display = '';
    else if (filter === 'active') card.style.display = ['completed','canceled'].includes(state) ? 'none' : '';
    else if (filter === 'done') card.style.display = state === 'completed' ? '' : 'none';
  });
  // Update empty sections
  document.querySelectorAll('.card-grid').forEach(grid => {
    const visible = grid.querySelectorAll('.card:not([style*="display: none"])');
    // Could add empty state dynamically here
  });
}
</script>
</body>
</html>`;
}

function fmtDate(iso) {
  const d = new Date(iso);
  return `${d.getMonth()+1}/${d.getDate()}`;
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
