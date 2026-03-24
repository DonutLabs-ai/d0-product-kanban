#!/usr/bin/env node
/**
 * sync-sprint-data.js
 * Fetches active cycle data from Linear API and updates the CYCLES block
 * in index.html. Does NOT regenerate the entire page — only the data.
 *
 * Usage: LINEAR_API_KEY=lin_api_xxx node sync-sprint-data.js
 */

const https = require('https');
const fs = require('fs');
const path = require('path');

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

// ── Keyword-based scope detection ──────────────────────────────────
const SCOPE_KEYWORDS = {
  'scope1.core': ['ai-core', 'llm', 'prompt', 'chat', 'dashboard', 'onboarding', 'ui', 'ux', 'harness', 'briefing', 'daily brief', 'model routing', 'skill', 'memory', 'heartbeat', 'eval', 'suna', 'profile', 'intent', 'web chat', 'sse', 'user scenario', '告警'],
  'scope2.trading': ['trading', 'perps', 'swap', 'transfer', 'withdraw', 'deposit', 'tpsl', 'tp/sl', 'jupiter', 'polymarket', 'clob', '平仓', '止盈止损', '交易对', '杠杆', 'leverage', 'perpetual', 'order', 'hummingbot', 'ohlcv', 'portfolio'],
  'scope3.proactive': ['proactive', 'signal', 'regime', 'discover', 'explore', '主动', 'strategy hub'],
  'scope4.safety': ['safety', 'security', 'grps', '风控', 'audit', '审计', 'container', 'isolation', '容器隔离', '权限', '凭证', 'credential', 'k8s 凭证', 'wallet-service'],
  'scope5.eval': ['eval', 'test', 'e2e', 'qa', 'quality', '困难用例', '回归'],
  'scope6.personal': ['personalization', 'user profile', 'behavioral', '千人千面', 'user preference'],
  'scope7.infra': ['infra', 'k8s', 'kubernetes', 'devops', 'argocd', 'helm', 'deploy', 'monitoring', '监控', 'pod', 'replica', 'vm', 'disk', 'activemq', 'workspace-sync', 'cost', '成本', 'orphan container'],
  'scope8.commercial': ['commercial', 'subscription', 'payment', '会员', 'tier', 'monetization', 'quota', '配额', 'access control'],
  'scope9.growth': ['seo', 'ugc', 'kol', '增长', 'growth', 'social', 'community', 'launch', 'gtm', 'marketing'],
};

const SCOPE_TO_LAYER = {
  'scope1.core': 'ai',
  'scope2.trading': 'trading',
  'scope3.proactive': 'ai',
  'scope4.safety': 'safety',
  'scope5.eval': 'ai',
  'scope6.personal': 'experience',
  'scope7.infra': 'infra',
  'scope8.commercial': 'commercial',
  'scope9.growth': 'acquisition',
};

// Legacy module detection for ENG issues
const LEGACY_KEYWORDS = {
  'ai.tools': ['ai-core', 'llm', 'prompt', 'chat', 'mcp', 'd0-cli', 'skill', 'memory', 'heartbeat', 'data source', 'birdeye', 'drift', 'nofx', 'web chat', 'sse', 'eval'],
  'trading.perps': ['perps', 'tpsl', 'tp/sl', 'jupiter', '平仓', '杠杆', 'leverage', 'perpetual', 'polymarket', 'clob', 'hummingbot'],
  'frontend.dashboard': ['dashboard', 'onboarding', 'ui', 'ux', '消息顺序'],
  'infra.k8s': ['k8s', 'kubernetes', 'pod', 'replica', 'activemq', 'devops', 'argocd', 'monitoring', 'disk', 'vm', 'namespace', 'workspace-sync', 'signo', 'deploy'],
  'infra.devops': ['extension', 'browser'],
  'scope4.safety': ['safety', 'security', '审计', 'audit', '凭证', 'credential', 'wallet-service'],
};

function detectModule(issue) {
  const text = (issue.title + ' ' + (issue.labels || []).join(' ')).toLowerCase();

  // For PRODUCT issues with scope labels, use those directly
  if (issue.team === 'PRODUCT') {
    for (const label of (issue.labels || [])) {
      const lbl = label.toLowerCase();
      // Match labels like "S1: Core Experience" or "Scope 1" etc.
      const scopeMatch = lbl.match(/^s(\d)/);
      if (scopeMatch) {
        const num = scopeMatch[1];
        const scopeMap = { '1': 'scope1.core', '2': 'scope2.trading', '3': 'scope3.proactive', '4': 'scope4.safety', '5': 'scope5.eval', '6': 'scope6.personal', '7': 'scope7.infra', '8': 'scope8.commercial', '9': 'scope9.growth' };
        if (scopeMap[num]) return { module: scopeMap[num], scope: 'S' + num };
      }
    }
    // Fall back to keyword detection for PRODUCT
    for (const [mod, keywords] of Object.entries(SCOPE_KEYWORDS)) {
      for (const kw of keywords) {
        if (text.includes(kw.toLowerCase())) {
          const scopeNum = mod.match(/scope(\d)/)?.[1];
          return { module: mod, scope: scopeNum ? 'S' + scopeNum : undefined };
        }
      }
    }
    return { module: 'scope1.core', scope: 'S1' }; // default
  }

  // For ENG issues, use legacy module keys
  for (const [mod, keywords] of Object.entries(LEGACY_KEYWORDS)) {
    for (const kw of keywords) {
      if (text.includes(kw.toLowerCase())) return { module: mod };
    }
  }
  return { module: 'infra.k8s' }; // default for ENG
}

function detectLayer(issue, module) {
  if (SCOPE_TO_LAYER[module]) return SCOPE_TO_LAYER[module];
  const modPrefix = module.split('.')[0];
  const layerMap = { 'ai': 'ai', 'trading': 'trading', 'frontend': 'experience', 'infra': 'infra', 'scope4': 'safety' };
  return layerMap[modPrefix] || 'infra';
}

// ── Assignee normalization ─────────────────────────────────────────
const ASSIGNEE_MAP = {
  'alex': 'alex', 'ethan': 'ethan', 'wenzhang': 'wenzhang', 'jin xu': 'xujin', 'xujin': 'xujin',
  'jim': 'jim', 'justin wu': 'justin', 'justin': 'justin', 'liang han': 'hanliang', 'hanliang': 'hanliang',
  'jiagui': 'jiagui', 'fei': 'fei', 'jackjun': 'jackjun', 'ye zou': 'zouye', 'zouye': 'zouye',
  'tao': 'tao', 'tao yuan': 'tao', 'gary': 'gary', 'jonas': 'jonas', 'regison': 'regison',
  'peter': 'peter', 'sylvia': 'sylvia', 'ruqi hu': 'ruqihu', 'ruqihu': 'ruqihu', 'melvin': 'melvin',
  'javier ruedas': 'javier', 'javier': 'javier', 'hongwei feng': 'hongweifeng', 'hongweifeng': 'hongweifeng',
  'cindy tang': 'cindytang', 'cindytang': 'cindytang', 'yi tan': 'yixintan', 'yixintan': 'yixintan',
  'rui li': 'lirui', 'lirui': 'lirui', 'lvyang': 'lvyang', 'kevin wang': 'kevin', 'kevin': 'kevin',
  'chris zhu': 'chriszhu', 'chriszhu': 'chriszhu', 'mond wonder': 'wondermond',
};

function normalizeAssignee(name) {
  if (!name) return 'unassigned';
  const lower = name.toLowerCase().trim();
  return ASSIGNEE_MAP[lower] || lower.replace(/\s+/g, '');
}

// ── Priority mapping ───────────────────────────────────────────────
function mapPriority(priorityLabel) {
  const map = { 'Urgent': 'urgent', 'High': 'high', 'Medium': 'medium', 'Low': 'low', 'No priority': 'no priority' };
  return map[priorityLabel] || 'no priority';
}

function mapStateType(type) {
  // Linear state types: started, unstarted, completed, canceled, triage, backlog
  return type || 'unstarted';
}

// ── Fetch data ─────────────────────────────────────────────────────
async function fetchAllCycles() {
  // Get active cycles for all teams
  const cyclesData = await gql(`{
    cycles(filter: { or: [
      { isActive: { eq: true } },
      { isNext: { eq: true } }
    ]}) {
      nodes { id number startsAt endsAt team { key name } isActive }
    }
  }`);
  
  const cycles = cyclesData.cycles.nodes;
  console.log(`Found ${cycles.length} cycles: ${cycles.map(c => `${c.team.key}#${c.number}${c.isActive ? ' (active)' : ' (next)'}`).join(', ')}`);

  const result = {};
  
  for (const cycle of cycles) {
    // Fetch issues with pagination
    let allIssues = [];
    let hasMore = true;
    let after = null;
    
    while (hasMore) {
      const afterClause = after ? `, after: "${after}"` : '';
      const data = await gql(`{
        cycle(id: "${cycle.id}") {
          issues(first: 100${afterClause}) {
            nodes {
              identifier title priority priorityLabel
              state { name type }
              assignee { displayName }
              labels { nodes { name } }
            }
            pageInfo { hasNextPage endCursor }
          }
        }
      }`);
      
      const { nodes, pageInfo } = data.cycle.issues;
      allIssues.push(...nodes);
      hasMore = pageInfo.hasNextPage;
      after = pageInfo.endCursor;
    }
    
    const teamKey = cycle.team.key;
    // Use team-prefixed key to avoid sprint number collisions across teams
    const cycleKey = `${teamKey.toLowerCase()}${cycle.number}`;
    const startDate = new Date(cycle.startsAt);
    const endDate = new Date(cycle.endsAt);
    const fmtDate = d => `${d.getMonth()+1}/${d.getDate()}`;
    
    const issues = allIssues.map(i => {
      const labels = (i.labels?.nodes || []).map(l => l.name);
      const assignee = normalizeAssignee(i.assignee?.displayName);
      const { module, scope } = detectModule({
        title: i.title,
        labels,
        team: teamKey,
      });
      const layer = detectLayer({ title: i.title, labels }, module);
      
      const entry = {
        id: i.identifier,
        title: i.title,
        assignee,
        layer,
        module,
        state: mapStateType(i.state.type),
        stateLabel: i.state.name,
        priority: mapPriority(i.priorityLabel),
        team: teamKey,
      };
      if (scope) entry.scope = scope;
      return entry;
    });
    
    result[cycleKey] = {
      label: `Sprint ${cycle.number} (${teamKey})`,
      dates: `${fmtDate(startDate)} → ${fmtDate(endDate)}`,
      status: cycle.isActive ? 'active' : 'upcoming',
      teamKey,
      number: cycle.number,
      issues,
    };
    
    console.log(`  ${teamKey} Sprint ${cycle.number}: ${issues.length} issues (${cycle.isActive ? 'active' : 'next'})`);
  }
  
  return result;
}

// ── Serialize issue to JS source ───────────────────────────────────
function escapeJS(s) {
  return s.replace(/\\/g, '\\\\').replace(/'/g, "\\'").replace(/\n/g, '\\n');
}

function issueToJS(issue, indent) {
  const parts = [`id:'${escapeJS(issue.id)}'`, `title:'${escapeJS(issue.title)}'`];
  parts.push(`assignee:'${escapeJS(issue.assignee)}'`);
  parts.push(`layer:'${escapeJS(issue.layer)}'`);
  parts.push(`module:'${escapeJS(issue.module)}'`);
  parts.push(`state:'${escapeJS(issue.state)}'`);
  parts.push(`stateLabel:'${escapeJS(issue.stateLabel)}'`);
  parts.push(`priority:'${escapeJS(issue.priority)}'`);
  parts.push(`team:'${escapeJS(issue.team)}'`);
  if (issue.scope) parts.push(`scope:'${escapeJS(issue.scope)}'`);
  return `${indent}{ ${parts.join(', ')} }`;
}

function cyclesToJS(cycles) {
  const keys = Object.keys(cycles).sort((a, b) => {
    const numA = parseInt(a.replace('sprint', ''));
    const numB = parseInt(b.replace('sprint', ''));
    return numA - numB;
  });
  
  let js = 'const CYCLES = {\n';
  for (let k = 0; k < keys.length; k++) {
    const key = keys[k];
    const cycle = cycles[key];
    js += `  ${key}: {\n`;
    js += `    label: '${escapeJS(cycle.label)}', dates: '${escapeJS(cycle.dates)}', status: '${cycle.status}',\n`;
    js += `    issues: [\n`;
    for (let i = 0; i < cycle.issues.length; i++) {
      js += issueToJS(cycle.issues[i], '      ');
      if (i < cycle.issues.length - 1) js += ',';
      js += '\n';
    }
    js += `    ]\n`;
    js += `  }`;
    if (k < keys.length - 1) js += ',';
    js += '\n';
  }
  js += '};\n';
  return js;
}

// ── Generate cycle selector buttons ────────────────────────────────
function generateCycleSelector(cycles) {
  // Sort: ENG first, then PRODUCT, then others; within team by number
  const teamOrder = { 'ENG': 0, 'PRODUCT': 1, 'TES': 2, 'GTM': 3 };
  const keys = Object.keys(cycles).sort((a, b) => {
    const tA = teamOrder[cycles[a].teamKey] ?? 99;
    const tB = teamOrder[cycles[b].teamKey] ?? 99;
    if (tA !== tB) return tA - tB;
    return cycles[a].number - cycles[b].number;
  });
  
  // Default to latest active PRODUCT cycle, then ENG, then any active
  const defaultKey = keys.find(k => cycles[k].status === 'active' && cycles[k].teamKey === 'PRODUCT')
    || keys.find(k => cycles[k].status === 'active' && cycles[k].teamKey === 'ENG')
    || keys.find(k => cycles[k].status === 'active')
    || keys[keys.length - 1];
  
  const buttons = keys.map((key) => {
    const c = cycles[key];
    const icon = c.status === 'active' ? '🏃' : '📋';
    const activeClass = key === defaultKey ? ' active' : '';
    return `      <button class="cycle-btn${activeClass}" onclick="switchCycle('${key}')" id="btn-${key}">${icon} ${c.label} (${c.dates})</button>`;
  });
  
  return buttons.join('\n');
}

// ── Update index.html ──────────────────────────────────────────────
async function main() {
  const htmlPath = path.join(__dirname, 'index.html');
  let html = fs.readFileSync(htmlPath, 'utf-8');
  
  console.log('Fetching Linear cycles...');
  const cycles = await fetchAllCycles();
  
  // Filter out empty cycles
  for (const key of Object.keys(cycles)) {
    if (cycles[key].issues.length === 0) {
      console.log(`  Skipping ${key} (empty)`);
      delete cycles[key];
    }
  }
  
  if (Object.keys(cycles).length === 0) {
    console.error('No cycles with issues found!');
    process.exit(1);
  }
  
  // 1. Replace CYCLES data block
  const cyclesStart = html.indexOf('const CYCLES = {');
  if (cyclesStart === -1) {
    console.error('Could not find CYCLES block in index.html');
    process.exit(1);
  }
  
  // Find the matching closing brace by counting braces
  let braceCount = 0;
  let cyclesEnd = -1;
  for (let i = cyclesStart + 'const CYCLES = '.length; i < html.length; i++) {
    if (html[i] === '{') braceCount++;
    if (html[i] === '}') {
      braceCount--;
      if (braceCount === 0) {
        cyclesEnd = i + 1;
        // Include the semicolon if present
        if (html[i + 1] === ';') cyclesEnd = i + 2;
        break;
      }
    }
  }
  
  if (cyclesEnd === -1) {
    console.error('Could not find end of CYCLES block');
    process.exit(1);
  }
  
  const newCyclesJS = cyclesToJS(cycles);
  html = html.substring(0, cyclesStart) + newCyclesJS + html.substring(cyclesEnd);
  console.log('✅ Replaced CYCLES data block');
  
  // 2. Replace cycle selector buttons
  const selectorStart = html.indexOf('<div class="cycle-selector" id="cycleSelector">');
  if (selectorStart !== -1) {
    const selectorEnd = html.indexOf('</div>', selectorStart) + '</div>'.length;
    const newSelector = `<div class="cycle-selector" id="cycleSelector">\n${generateCycleSelector(cycles)}\n    </div>`;
    html = html.substring(0, selectorStart) + newSelector + html.substring(selectorEnd);
    console.log('✅ Updated cycle selector buttons');
  }
  
  // 3. Update the init call to use the latest active main-team cycle
  const teamOrder = { 'ENG': 0, 'PRODUCT': 1, 'TES': 2, 'GTM': 3 };
  const cycleKeys = Object.keys(cycles).sort((a, b) => {
    const tA = teamOrder[cycles[a].teamKey] ?? 99;
    const tB = teamOrder[cycles[b].teamKey] ?? 99;
    if (tA !== tB) return tA - tB;
    return cycles[a].number - cycles[b].number;
  });
  const latestKey = cycleKeys.find(k => cycles[k].status === 'active' && cycles[k].teamKey === 'PRODUCT')
    || cycleKeys.find(k => cycles[k].status === 'active')
    || cycleKeys[cycleKeys.length - 1];
  
  // Update activeCycleKey default (may be let or var)
  const oldActiveCycle = html.match(/(let|var|const)\s+activeCycleKey\s*=\s*'[^']+'/);
  if (oldActiveCycle) {
    const decl = oldActiveCycle[1]; // preserve let/var/const
    html = html.replace(oldActiveCycle[0], `${decl} activeCycleKey = '${latestKey}'`);
    console.log(`✅ Set default cycle to ${latestKey}`);
  }
  
  // Update switchCycle call in initApp
  const oldInitCycle = html.match(/switchCycle\('[a-z]+\d+'\)/);
  if (oldInitCycle) {
    html = html.replace(oldInitCycle[0], `switchCycle('${latestKey}')`);
  }

  // 4. Update timestamp
  const now = new Date();
  const dateStr = `${now.getFullYear()}-${String(now.getMonth()+1).padStart(2,'0')}-${String(now.getDate()).padStart(2,'0')}`;
  const timeStr = `${String(now.getUTCHours()).padStart(2,'0')}:${String(now.getUTCMinutes()).padStart(2,'0')} UTC`;
  
  // Update the cycle-badge version date
  html = html.replace(
    /(<div class="cycle-badge"><span class="pulse"><\/span>)v\d+\s*·\s*[\d-]+(<\/div>)/,
    `$1v11 · ${dateStr}$2`
  );
  
  // Update the sync timestamp if it exists
  const syncTsRegex = /id="syncTimestamp">[^<]*/;
  if (syncTsRegex.test(html)) {
    html = html.replace(syncTsRegex, `id="syncTimestamp">${dateStr} ${timeStr}`);
  }
  
  // Write updated HTML
  fs.writeFileSync(htmlPath, html);
  
  // Summary
  let totalIssues = 0;
  for (const key of cycleKeys) {
    totalIssues += cycles[key].issues.length;
  }
  console.log(`\n✅ Sync complete — ${cycleKeys.length} cycles, ${totalIssues} issues`);
  console.log(`   Updated: ${htmlPath}`);
}

main().catch(err => {
  console.error('Sync failed:', err);
  process.exit(1);
});
