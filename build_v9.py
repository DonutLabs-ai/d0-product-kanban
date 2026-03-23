#!/usr/bin/env python3
"""Build v9.0 of the D0 Product Kanban dashboard."""

import json
import re

# Read original
WS = '/app/workspace/agents/dono/workspace/tmp/kanban-update'
with open(f'{WS}/original-index.html', 'r') as f:
    html = f.read()

with open(f'{WS}/cycle23_js_issues.json', 'r') as f:
    cycle23_issues = json.load(f)

with open(f'{WS}/eng22_js_issues.json', 'r') as f:
    eng22_issues = json.load(f)

# ═══════════════════════════════════════════════════════════
# 1. Update title and version
# ═══════════════════════════════════════════════════════════
html = html.replace(
    '<title>D0 Product Dashboard — v8.4</title>',
    '<title>D0 Product Dashboard — v9.0</title>'
)
html = html.replace(
    '<div class="cycle-badge"><span class="pulse"></span>v8.4 · 2026-03-20</div>',
    '<div class="cycle-badge"><span class="pulse"></span>v9.0 · 2026-03-23</div>'
)
html = html.replace(
    'D0 Product Dashboard v8.4 · Auto-synced from <a href="https://linear.app/donutbrowser">Linear</a> · Unified Sprint View',
    'D0 Product Dashboard v9.0 · Auto-synced from <a href="https://linear.app/donutbrowser">Linear</a> · Unified Sprint View'
)
html = html.replace(
    'CEO 重点跟踪的跨团队关注领域 · 聚合相关 Issue 状态 · v8.4',
    'CEO 重点跟踪的跨团队关注领域 · 聚合相关 Issue 状态 · v9.0'
)

# ═══════════════════════════════════════════════════════════
# 2. Add Milestone tab button + CSS
# ═══════════════════════════════════════════════════════════
html = html.replace(
    '<button class="tab-btn" onclick="switchTab(\'ceo\')">🎯 CEO 关注线</button>',
    '<button class="tab-btn" onclick="switchTab(\'ceo\')">🎯 CEO 关注线</button>\n    <button class="tab-btn" onclick="switchTab(\'milestone\')">🗓 Milestone</button>'
)

# ═══════════════════════════════════════════════════════════
# 3. Add Milestone tab panel HTML (before closing </div><!-- /page -->)
# ═══════════════════════════════════════════════════════════
milestone_tab_html = '''
  <!-- ══════════════════════════════════════════════════════
       TAB 9: MILESTONE PLANNING (v9.0)
       ══════════════════════════════════════════════════════ -->
  <div id="tab-milestone" class="tab-panel">
    <div class="sec"><div class="sec-head"><span class="sec-num">08</span><h2>🗓 Milestone Planning — 里程碑规划</h2></div>
      <div class="hint">M1 执行看板 + M2-M4 路线图 + 周二 Sync 议程 · v9.0</div>
    </div>

    <!-- M1 Execution Sheet -->
    <div style="margin:var(--space-4) 0">
      <div style="font-family:var(--font-display);font-size:1.6rem;font-weight:400;margin-bottom:var(--space-2);color:var(--fg-base)">M1: Foundation Sprint</div>
      <div style="font-family:var(--font-mono);font-size:0.68rem;color:var(--fg-subtle);margin-bottom:var(--space-4)">3/16 → 4/15 · 30 days · 18 deliverables across 9 scopes</div>
      <div id="m1ExecutionSheet"></div>
    </div>

    <!-- M2-M4 Roadmap -->
    <div style="margin:var(--space-8) 0">
      <div style="font-family:var(--font-display);font-size:1.3rem;font-weight:400;margin-bottom:var(--space-4)">M2 → M4 Roadmap</div>
      <div id="milestoneRoadmap" style="display:grid;grid-template-columns:repeat(auto-fit,minmax(380px,1fr));gap:var(--space-4)"></div>
    </div>

    <!-- Weekly Sync Agenda -->
    <div style="margin:var(--space-8) 0">
      <div style="font-family:var(--font-display);font-size:1.3rem;font-weight:400;margin-bottom:var(--space-4)">📅 周二 Milestone Sync Template</div>
      <div id="weeklySyncAgenda"></div>
    </div>
  </div>
'''

html = html.replace(
    '  <div class="footer">',
    milestone_tab_html + '\n  <div class="footer">'
)

# ═══════════════════════════════════════════════════════════
# 4. Add Milestone CSS
# ═══════════════════════════════════════════════════════════
milestone_css = '''
/* ══ MILESTONE TAB STYLES (v9.0) ═══════════════════════ */
.m1-table { width: 100%; border-collapse: collapse; font-size: 0.78rem }
.m1-table th { font-family: var(--font-mono); font-size: 0.62rem; text-transform: uppercase; letter-spacing: 0.06em; color: var(--fg-subtle); padding: var(--space-2) var(--space-3); text-align: left; border-bottom: 2px solid var(--border-emphasis); background: var(--bg-subtle) }
.m1-table td { padding: var(--space-2) var(--space-3); border-bottom: 1px solid var(--border-base); vertical-align: top }
.m1-table tr:hover td { background: rgba(255,255,255,.02) }
.m1-scope { font-weight: 600; white-space: nowrap; font-size: 0.72rem }
.m1-feature { font-weight: 500 }
.m1-status { font-family: var(--font-mono); font-size: 0.62rem; padding: 2px 8px; border-radius: 100px; white-space: nowrap; display: inline-block }
.m1-status.dev { background: rgba(245,158,11,.12); color: var(--warning) }
.m1-status.plan { background: rgba(59,130,246,.12); color: var(--info) }
.m1-status.prd { background: rgba(167,139,250,.12); color: var(--purple) }
.m1-status.idea { background: rgba(113,113,122,.12); color: var(--fg-subtle) }
.m1-status.todo { background: rgba(113,113,122,.12); color: var(--fg-subtle) }
.m1-owner { font-family: var(--font-mono); font-size: 0.65rem; color: var(--fg-muted) }
.m1-acceptance { font-size: 0.72rem; color: var(--fg-muted) }
.m1-dep { font-size: 0.65rem; color: var(--fg-subtle); font-style: italic }
.ms-card { background: var(--bg-subtle); border: 1px solid var(--border-base); border-radius: var(--radius-lg); padding: var(--space-4); position: relative; overflow: hidden }
.ms-card::before { content: ''; position: absolute; top: 0; left: 0; right: 0; height: 3px }
.ms-card.m2::before { background: linear-gradient(90deg, var(--info), var(--teal)) }
.ms-card.m3::before { background: linear-gradient(90deg, var(--warning), var(--gold)) }
.ms-card.m4::before { background: linear-gradient(90deg, var(--purple), var(--error)) }
.ms-card h3 { font-family: var(--font-display); font-size: 1.15rem; font-weight: 400; margin-bottom: var(--space-2) }
.ms-card .ms-dates { font-family: var(--font-mono); font-size: 0.62rem; color: var(--fg-subtle); margin-bottom: var(--space-3) }
.ms-card .ms-core { margin-bottom: var(--space-3) }
.ms-card .ms-core li { font-size: 0.78rem; color: var(--fg-muted); padding: 2px 0 }
.ms-card .ms-deps { font-size: 0.72rem; color: var(--fg-subtle); margin-bottom: var(--space-2) }
.ms-card .ms-ns { font-family: var(--font-mono); font-size: 0.65rem; color: var(--info); padding: var(--space-2); background: rgba(59,130,246,.06); border-radius: var(--radius-sm); margin-bottom: var(--space-2) }
.ms-card .ms-effort { font-family: var(--font-mono); font-size: 0.6rem; color: var(--fg-subtle) }
.sync-box { background: var(--bg-subtle); border: 1px solid var(--border-base); border-radius: var(--radius-lg); padding: var(--space-4); font-family: var(--font-mono); font-size: 0.75rem; line-height: 1.8; white-space: pre-wrap }
.sync-box .sync-title { font-family: var(--font-display); font-size: 1.1rem; font-weight: 400; margin-bottom: var(--space-3); display: block; font-family: var(--font-sans) }
.sync-box .sync-section { color: var(--fg-base); font-weight: 600 }
.sync-box .sync-detail { color: var(--fg-muted); padding-left: var(--space-4) }
.sync-box .sync-sep { color: var(--fg-faint); display: block; margin: var(--space-2) 0 }
.sync-box .sync-footer { color: var(--fg-subtle); font-size: 0.65rem; margin-top: var(--space-3) }
'''

html = html.replace(
    '/* ── Reset ─',
    milestone_css + '\n/* ── Reset ─'
)

# ═══════════════════════════════════════════════════════════
# 5. Replace PRODUCT_TREE
# ═══════════════════════════════════════════════════════════
old_tree_start = "const PRODUCT_TREE = ["
old_tree_end = "];\n\n/* Helper: map issue module to tree category key */"

# Find and replace PRODUCT_TREE + helper functions
tree_section_start = html.index(old_tree_start)
tree_section_end = html.index("/* Helper: map issue module to tree category key */")

new_tree = '''const PRODUCT_TREE = [
  { key:'scope1', icon:'🧠', name:'S1 Core Experience', children:[
    { key:'scope1.core', name:'核心体验', keys:['scope1.core'], owners:'JackJun, Gary, Jin Xu' }
  ]},
  { key:'scope2', icon:'💰', name:'S2 Trading System', children:[
    { key:'scope2.trading', name:'交易系统', keys:['scope2.trading'], owners:'Peter, Alex, Ethan, Rui Li' }
  ]},
  { key:'scope3', icon:'🔮', name:'S3 Proactive Intelligence', children:[
    { key:'scope3.proactive', name:'主动智能', keys:['scope3.proactive'], owners:'Chris, JackJun' }
  ]},
  { key:'scope4', icon:'🛡', name:'S4 Safety & Trust', children:[
    { key:'scope4.safety', name:'安全与信任', keys:['scope4.safety'], owners:'Jiagui, Sylvia, JackJun' }
  ]},
  { key:'scope5', icon:'📊', name:'S5 Eval & Quality', children:[
    { key:'scope5.eval', name:'质量体系', keys:['scope5.eval'], owners:'Fei, Kevin' }
  ]},
  { key:'scope6', icon:'🎯', name:'S6 Personalization', children:[
    { key:'scope6.personal', name:'千人千面', keys:['scope6.personal'], owners:'Sylvia, Justin' }
  ]},
  { key:'scope7', icon:'🏗', name:'S7 Infrastructure', children:[
    { key:'scope7.infra', name:'基础设施', keys:['scope7.infra'], owners:'Wenzhang, JackJun' }
  ]},
  { key:'scope8', icon:'💳', name:'S8 Commercialization', children:[
    { key:'scope8.commercial', name:'商业化', keys:['scope8.commercial'], owners:'Ye Zou' }
  ]},
  { key:'scope9', icon:'📣', name:'S9 Growth & Onboarding', children:[
    { key:'scope9.growth', name:'增长与获客', keys:['scope9.growth'], owners:'Ruqi, Hongwei, Melvin' }
  ]}
];

'''

html = html[:tree_section_start] + new_tree + html[tree_section_end:]

# Now replace the helper functions
old_helpers = """/* Helper: map issue module to tree category key */
function getTreeCatKey(moduleKey) {
  const m = moduleKey || '';
  for (const cat of PRODUCT_TREE) {
    for (const sub of cat.children) {
      if (sub.keys ? sub.keys.includes(m) : m === sub.key) return cat.key;
    }
  }
  return PRODUCT_TREE[0].key;
}
function issueMatchesSub(issue, sub) {
  const m = issue.module || issue.layer || '';
  return sub.keys ? sub.keys.includes(m) : m === sub.key;
}
function issueMatchesCat(issue, cat) {
  return cat.children.some(sub => issueMatchesSub(issue, sub));
}"""

new_helpers = """/* Helper: map issue module to tree category key */
function getTreeCatKey(moduleKey) {
  const m = moduleKey || '';
  for (const cat of PRODUCT_TREE) {
    for (const sub of cat.children) {
      if (sub.keys && sub.keys.includes(m)) return cat.key;
    }
  }
  // Fallback: map legacy module keys
  const legacyMap = {
    'ai.tools':'scope1','ai.llmproxy':'scope1','ai.agent':'scope1',
    'ai.eval':'scope5','frontend.dashboard':'scope1','frontend.hil':'scope1',
    'frontend.extension':'scope1','infra.backend':'scope7','infra.k8s':'scope7',
    'infra.devops':'scope7','infra.cron':'scope7',
    'trading.perps':'scope2','trading.spot':'scope2','trading.agents':'scope2','trading.wallet':'scope2',
    'quality.e2e':'scope5','quality.triage':'scope5',
    'growth.seo':'scope9','growth.referral':'scope9','growth.voice':'scope9'
  };
  if (legacyMap[m]) return legacyMap[m];
  return PRODUCT_TREE[0].key;
}
function issueMatchesSub(issue, sub) {
  const m = issue.module || issue.layer || '';
  return sub.keys && sub.keys.includes(m);
}
function issueMatchesCat(issue, cat) {
  return cat.children.some(sub => issueMatchesSub(issue, sub));
}"""

html = html.replace(old_helpers, new_helpers)

# ═══════════════════════════════════════════════════════════
# 6. Replace CYCLES data
# ═══════════════════════════════════════════════════════════

# Build sprint22 issues JS
def format_eng_issue(issue):
    """Format ENG issue for JS."""
    esc_title = issue['title'].replace("'", "\\'").replace('\n', ' ')
    return (f"      {{ id:'{issue['id']}', title:'{esc_title}', "
            f"assignee:'{issue['assignee']}', layer:'{issue['layer']}', "
            f"module:'{issue['module']}', state:'{issue['state']}', "
            f"stateLabel:'{issue['stateLabel']}', priority:'{issue['priority']}', "
            f"team:'{issue['team']}' }}")

def format_product_issue(issue):
    """Format PRODUCT issue for JS."""
    esc_title = issue['title'].replace("'", "\\'").replace('\n', ' ')
    return (f"      {{ id:'{issue['id']}', title:'{esc_title}', "
            f"assignee:'{issue['assignee']}', layer:'{issue['layer']}', "
            f"module:'{issue['module']}', state:'{issue['state']}', "
            f"stateLabel:'{issue['stateLabel']}', priority:'{issue['priority']}', "
            f"team:'{issue['team']}', scope:'{issue.get('scope','')}' }}")

sprint22_js = ",\n".join(format_eng_issue(i) for i in eng22_issues)
sprint23_js = ",\n".join(format_product_issue(i) for i in cycle23_issues)

# Find the CYCLES block
cycles_start = html.index("const CYCLES = {")
cycles_end = html.index("/* ── Shared Mappings")

new_cycles = f"""const CYCLES = {{
  sprint22: {{
    label: 'Sprint 22 (ENG)', dates: '3/15 → 3/29', status: 'active',
    issues: [
{sprint22_js}
    ]
  }},
  sprint23: {{
    label: 'Sprint 23 (PRODUCT)', dates: '3/23 → 4/3', status: 'active',
    issues: [
{sprint23_js}
    ]
  }}
}};

"""

html = html[:cycles_start] + new_cycles + html[cycles_end:]

# ═══════════════════════════════════════════════════════════
# 7. Update moduleAccents
# ═══════════════════════════════════════════════════════════
html = html.replace(
    "const moduleAccents = {'scope1':'#f59e0b','scope2':'#ef4444','scope3':'#a78bfa','support':'#22c55e','frontend':'#3b82f6','ai':'#f59e0b','trading':'#ef4444','infra':'#71717a','quality':'#14b8a6','growth':'#22c55e'};",
    "const moduleAccents = {'scope1':'#f59e0b','scope2':'#ef4444','scope3':'#a78bfa','scope4':'#dc2626','scope5':'#14b8a6','scope6':'#8b5cf6','scope7':'#71717a','scope8':'#d4a73a','scope9':'#22c55e','frontend':'#3b82f6','ai':'#f59e0b','trading':'#ef4444','infra':'#71717a','quality':'#14b8a6','growth':'#22c55e'};"
)

# ═══════════════════════════════════════════════════════════
# 8. Update cycle buttons
# ═══════════════════════════════════════════════════════════
html = html.replace(
    """<button class="cycle-btn" onclick="switchCycle('sprint22')" id="btn-sprint22">🏃 Sprint 22 (当前 3/15→3/29)</button>
      <button class="cycle-btn active" onclick="switchCycle('sprint23')" id="btn-sprint23">📋 Sprint 23 (upcoming 3/23→4/3)</button>""",
    """<button class="cycle-btn" onclick="switchCycle('sprint22')" id="btn-sprint22">🏃 Sprint 22 — ENG (3/15→3/29)</button>
      <button class="cycle-btn active" onclick="switchCycle('sprint23')" id="btn-sprint23">📋 Sprint 23 — PRODUCT (3/23→4/3)</button>"""
)

# ═══════════════════════════════════════════════════════════
# 9. Update switchTab to handle milestone
# ═══════════════════════════════════════════════════════════
html = html.replace(
    "if (tab==='ceo') renderCEOFocus();",
    "if (tab==='ceo') renderCEOFocus();\n  if (tab==='milestone') renderMilestone();"
)

# ═══════════════════════════════════════════════════════════
# 10. Replace PANORAMA_DATA
# ═══════════════════════════════════════════════════════════
pano_start = html.index("const PANORAMA_DATA = [")
pano_end = html.index("function renderProductPanorama()")

new_panorama = """const PANORAMA_DATA = [
  { key:'scope1', icon:'🧠', name:'S1 Core Experience — 核心体验', modules:[
    { name:'PRODUCT-1948: D0 困难用例场景分析与实现', owner:'JackJun', desc:'12 Hard Use Cases · In Progress', issues:12, updated:'2026-03-23' },
    { name:'PRODUCT-2261: MCP Server 工具精简 170→22', owner:'Regison', desc:'Token 效率提升 50%+ · In Review', issues:1, updated:'2026-03-23' },
    { name:'PRODUCT-2205: 用户认证修复', owner:'Gary', desc:'Session/Cookie/401 清零 · Todo', issues:5, updated:'2026-03-23' },
    { name:'PRODUCT-2184: Dashboard & Onboarding UI/UX', owner:'Gary', desc:'In Progress', issues:3, updated:'2026-03-23' },
    { name:'PRODUCT-1949: D0 自定义看板', owner:'Jin Xu', desc:'HTML 页面工具调用 · In Progress', issues:1, updated:'2026-03-23' },
    { name:'PRODUCT-2251: 统一聚合报警机制', owner:'JackJun', desc:'Turing 跨模块告警 · In Review', issues:1, updated:'2026-03-23' }
  ]},
  { key:'scope2', icon:'💰', name:'S2 Trading System — 交易系统', modules:[
    { name:'PRODUCT-2216: Jupiter V2 迁移', owner:'Regison', desc:'Adapter 重构 + Trigger Order · In Progress', issues:5, updated:'2026-03-23' },
    { name:'PRODUCT-2218: TP/SL v1 → Jupiter V2', owner:'Ethan', desc:'止盈止损功能迁移 · In Progress', issues:1, updated:'2026-03-23' },
    { name:'PRODUCT-2219: Perps 交易对 10→20', owner:'Alex', desc:'SQL Migration + 灰度 · In Progress', issues:1, updated:'2026-03-23' },
    { name:'PRODUCT-2492: Per-Symbol 杠杆持久化', owner:'Rui Li', desc:'SET_LEVERAGE API · Todo', issues:1, updated:'2026-03-23' },
    { name:'PRODUCT-2014: Polymarket Pipeline', owner:'Liang Han', desc:'信号到执行全链路 · Planning', issues:4, updated:'2026-03-23' },
    { name:'PRODUCT-2019: Perps 体验优化', owner:'Rui Li', desc:'预检外漏 + 下单体验 · In Progress', issues:1, updated:'2026-03-23' }
  ]},
  { key:'scope3', icon:'🔮', name:'S3 Proactive Intelligence — 主动智能', modules:[
    { name:'PRODUCT-1872: Knowledge Pipeline Master Plan', owner:'Chris', desc:'数据基建 + 知识注入 · Planning', issues:3, updated:'2026-03-23' },
    { name:'PRODUCT-1882: Daily Report 升级', owner:'Jim', desc:'数据驱动分析 · In Review', issues:1, updated:'2026-03-23' },
    { name:'PRODUCT-2297: 用户行为记忆系统 v3.0', owner:'Jim', desc:'In Review', issues:1, updated:'2026-03-23' },
    { name:'PRODUCT-1790: 信号学习闭环', owner:'Chris', desc:'知识积累 + 自主优化 · Todo', issues:1, updated:'2026-03-23' }
  ]},
  { key:'scope4', icon:'🛡', name:'S4 Safety & Trust — 安全与信任', modules:[
    { name:'PRODUCT-2149: 安全漏洞修复总览', owner:'Jiagui', desc:'53 个漏洞 P0/P1 清零 · In Progress', issues:5, updated:'2026-03-23' },
    { name:'PRODUCT-2207: GRPS v1 风控引擎', owner:'Sylvia', desc:'链上风控规则 + 参数约束 · Todo', issues:3, updated:'2026-03-23' },
    { name:'PRODUCT-2228: 内部权限控制', owner:'Jiagui', desc:'防止单人完成资金转移 · Todo', issues:3, updated:'2026-03-23' },
    { name:'PRODUCT-2186: AI Skill GRPS 软约束', owner:'Jin Xu', desc:'grps-risk-guard · In Progress', issues:1, updated:'2026-03-23' },
    { name:'PRODUCT-2026: K8s 生产基础设施修复', owner:'Wenzhang', desc:'In Progress', issues:2, updated:'2026-03-23' }
  ]},
  { key:'scope5', icon:'📊', name:'S5 Eval & Quality — 质量体系', modules:[
    { name:'PRODUCT-1963: Eval Harness v1', owner:'Fei', desc:'B3/B4 真实后端测试 · In Progress', issues:2, updated:'2026-03-23' },
    { name:'PRODUCT-1992: E2E CI 自动化', owner:'Kevin', desc:'GitHub Actions · In Progress', issues:3, updated:'2026-03-23' },
    { name:'PRODUCT-1947: Eval 全景图 v0316', owner:'Fei', desc:'In Progress', issues:1, updated:'2026-03-23' },
    { name:'PRODUCT-1891: UI/UX 设计走查验收', owner:'Yi Tan', desc:'In Review', issues:1, updated:'2026-03-23' },
    { name:'PRODUCT-2330: 原子与不变量级 LLM 评测', owner:'Fei', desc:'In Review', issues:1, updated:'2026-03-23' }
  ]},
  { key:'scope6', icon:'🎯', name:'S6 Personalization — 千人千面', modules:[
    { name:'PRODUCT-1736: User Profile Schema', owner:'Sylvia', desc:'架构设计与实现 · In Review', issues:2, updated:'2026-03-23' },
    { name:'PRODUCT-1739: User Profile Skill', owner:'Sylvia', desc:'数据采集 + 查询接口 · In Review', issues:1, updated:'2026-03-23' }
  ]},
  { key:'scope7', icon:'🏗', name:'S7 Infrastructure — 基础设施', modules:[
    { name:'PRODUCT-2496: 线上成本 Tracking', owner:'JackJun', desc:'Infra + LLM 监控 · Todo', issues:3, updated:'2026-03-23' },
    { name:'PRODUCT-2043: K8s 多副本 + PDB', owner:'Wenzhang', desc:'消除单副本风险 · In Progress', issues:1, updated:'2026-03-23' },
    { name:'PRODUCT-2025: OpenClaw 上游升级', owner:'Wenzhang', desc:'全量回归 · Todo', issues:1, updated:'2026-03-23' },
    { name:'PRODUCT-2098: AMQP 故障容错', owner:'JackJun', desc:'Birdeye 熔断 + 告警 · Todo', issues:1, updated:'2026-03-23' }
  ]},
  { key:'scope8', icon:'💳', name:'S8 Commercialization — 商业化', modules:[
    { name:'PRODUCT-2121: 计费域模型 + Plan Config', owner:'Wenzhang', desc:'数据建模 + 订阅状态机 · In Progress', issues:1, updated:'2026-03-23' },
    { name:'PRODUCT-2122: Creem 支付通道对接', owner:'Wenzhang', desc:'Checkout + Webhook · In Progress', issues:1, updated:'2026-03-23' },
    { name:'PRODUCT-2485: Skill 分层访问控制', owner:'Jin Xu', desc:'Pro/Free 权益分层 · In Progress', issues:1, updated:'2026-03-23' },
    { name:'PRODUCT-2009: 商业化规划 MVP', owner:'Ye Zou', desc:'付费验证路线 · Planning', issues:3, updated:'2026-03-23' }
  ]},
  { key:'scope9', icon:'📣', name:'S9 Growth & Onboarding — 增长与获客', modules:[
    { name:'PRODUCT-2127: D0 launch 素材', owner:'Yi Tan', desc:'In Progress', issues:1, updated:'2026-03-23' },
    { name:'PRODUCT-2125: 3/27 活动素材', owner:'Yi Tan', desc:'In Progress', issues:1, updated:'2026-03-23' },
    { name:'PRODUCT-1999: Landing Page iframe 重构', owner:'Gary', desc:'Todo', issues:1, updated:'2026-03-23' }
  ]}
];

"""

html = html[:pano_start] + new_panorama + html[pano_end:]

# ═══════════════════════════════════════════════════════════
# 11. Replace CEO_FOCUS_AREAS
# ═══════════════════════════════════════════════════════════
ceo_start = html.index("const CEO_FOCUS_AREAS = [")
ceo_end = html.index("function renderCEOFocus()")

new_ceo = """const CEO_FOCUS_AREAS = [
  {
    title: '🛡 安全 & 风控 — P0 漏洞清零 + GRPS 上线',
    owners: 'Jiagui (容器安全) + Sylvia (GRPS) + JackJun (Infra)',
    color: 'var(--error)',
    keywords: ['safety','安全','灾备','风控','grps','container','security','risk','漏洞','权限','隔离'],
    moduleKeys: ['scope4.safety'],
    risks: ['53 个安全漏洞中 P0/P1 尚未全部清零','GRPS 风控引擎核心依赖交易 API 稳定','内部权限控制方案仍在 Todo'],
    criticalPath: ['PRODUCT-2227 容器隔离 (In Progress)','PRODUCT-2228 内部权限控制','PRODUCT-2207 GRPS v1 风控引擎','PRODUCT-1918 数据诚实性加固 (In Review)']
  },
  {
    title: '💰 交易系统 — Jupiter V2 + TP/SL + 20 对',
    owners: 'Peter (PM) + Regison (V2) + Alex (Perps) + Ethan (TP/SL)',
    color: 'var(--warning)',
    keywords: ['trading','交易','perps','jupiter','tpsl','杠杆','polymarket','持仓','下单','止盈','止损'],
    moduleKeys: ['scope2.trading'],
    risks: ['Jupiter V2 迁移影响面广 — Adapter + Trigger Order + 签名链路','Per-Symbol 杠杆持久化 urgent 但未开始','Polymarket Pipeline 仍在 Planning 阶段'],
    criticalPath: ['PRODUCT-2216 Jupiter V2 迁移 (In Progress)','PRODUCT-2218 TP/SL 迁移 (In Progress)','PRODUCT-2219 交易对 10→20 (In Progress)','PRODUCT-2492 杠杆持久化 (Todo)']
  },
  {
    title: '📊 Eval & 核心体验 — 12 Use Cases + Eval Harness',
    owners: 'JackJun (Use Cases) + Fei (Eval) + Gary (Dashboard)',
    color: 'var(--gold)',
    keywords: ['eval','use case','harness','dashboard','mcp','tool','测试','认证','cookie','session'],
    moduleKeys: ['scope1.core','scope5.eval'],
    risks: ['MCP 170→22 精简中，Token 效率提升需验证','用户认证 Session/Cookie 问题多线程修复','Eval Harness B3/B4 真实后端双模式复杂'],
    criticalPath: ['PRODUCT-1948 12 Hard Use Cases (In Progress)','PRODUCT-2261 MCP 精简 (In Review)','PRODUCT-1963 Eval Harness v1 (In Progress)','PRODUCT-2205 认证修复 (Todo)']
  },
  {
    title: '💳 商业化 — 计费 + 支付闭环 + Skill 分层',
    owners: 'Ye Zou (PM) + Wenzhang (Backend) + Jin Xu (Skill)',
    color: 'var(--purple)',
    keywords: ['付费','billing','计费','monetization','payment','subscription','quota','配额','会员','商业化','creem','pricing','skill 分层'],
    moduleKeys: ['scope8.commercial'],
    risks: ['计费域模型是支付闭环 foundation — 正在开发','Creem 支付通道第三方依赖','Skill 分层访问需要 AI-Core 配合'],
    criticalPath: ['PRODUCT-2121 计费域模型 (In Progress)','PRODUCT-2122 Creem 支付通道 (In Progress)','PRODUCT-2485 Skill 分层 (In Progress)','PRODUCT-2124 Membership Panel (Todo)']
  }
];

"""

html = html[:ceo_start] + new_ceo + html[ceo_end:]

# ═══════════════════════════════════════════════════════════
# 12. Update renderCEOFocus to use new module keys
# ═══════════════════════════════════════════════════════════
# The existing renderCEOFocus function should work since we match by keywords too
# But let's make sure module matching works with the issue.module field
html = html.replace(
    "if (area.moduleKeys.some(mk => i.module === mk)) return true;",
    "if (area.moduleKeys.some(mk => (i.module||'') === mk || (i.scope ? 'scope'+i.scope.replace('S','').toLowerCase()+'.'+mk.split('.')[1] : '') === mk)) return true;"
)

# ═══════════════════════════════════════════════════════════
# 13. Add renderMilestone function before the init line
# ═══════════════════════════════════════════════════════════
milestone_js = """

/* ══════════════════════════════════════════════════════════
   MILESTONE PLANNING (v9.0)
   ══════════════════════════════════════════════════════════ */
function renderMilestone() {
  // M1 Execution Sheet
  const m1El = document.getElementById('m1ExecutionSheet');
  if (m1El) {
    const m1Data = [
      { scope:'🧠 S1', feature:'12 Hard Use Cases', status:'排期中', statusCls:'plan', acceptance:'12 case E2E 跑通', ownerPM:'Sylvia', ownerEng:'JackJun', dep:'—' },
      { scope:'🧠 S1', feature:'Dashboard v1', status:'开发中', statusCls:'dev', acceptance:'首屏<3s, 核心看板可用', ownerPM:'Yi Tan', ownerEng:'Gary', dep:'—' },
      { scope:'🧠 S1', feature:'MCP 工具精简 170→22', status:'开发中', statusCls:'dev', acceptance:'Token 效率提升 50%+', ownerPM:'—', ownerEng:'Regison', dep:'—' },
      { scope:'🧠 S1', feature:'用户认证修复', status:'开发中', statusCls:'dev', acceptance:'Session/Cookie/401 清零', ownerPM:'—', ownerEng:'Gary, Jim', dep:'—' },
      { scope:'💰 S2', feature:'TP/SL v1 → Jupiter V2', status:'开发中', statusCls:'dev', acceptance:'止盈止损功能可用', ownerPM:'Peter', ownerEng:'Ethan, Regison', dep:'Jupiter V2 迁移' },
      { scope:'💰 S2', feature:'Perps 交易对 10→20', status:'开发中', statusCls:'dev', acceptance:'20 对上线', ownerPM:'Peter', ownerEng:'Alex', dep:'—' },
      { scope:'💰 S2', feature:'杠杆持久化', status:'Todo', statusCls:'todo', acceptance:'Per-symbol 杠杆可设', ownerPM:'Peter', ownerEng:'Rui Li', dep:'—' },
      { scope:'🔮 S3', feature:'Knowledge Pipeline P1-P2', status:'规划中', statusCls:'plan', acceptance:'数据基建 + 知识注入层', ownerPM:'Chris', ownerEng:'Jim', dep:'—' },
      { scope:'🛡 S4', feature:'安全漏洞修复 (53个)', status:'开发中', statusCls:'dev', acceptance:'P0/P1 漏洞清零', ownerPM:'—', ownerEng:'Jiagui', dep:'—' },
      { scope:'🛡 S4', feature:'GRPS v1', status:'Todo', statusCls:'todo', acceptance:'风控引擎上线，限额 Guard 生效', ownerPM:'Sylvia', ownerEng:'Rui Li, Jin Xu', dep:'—' },
      { scope:'🛡 S4', feature:'内部权限控制', status:'Todo', statusCls:'todo', acceptance:'防止单人完成资金转移', ownerPM:'—', ownerEng:'JackJun, Regison', dep:'—' },
      { scope:'📊 S5', feature:'Eval Harness v1', status:'开发中', statusCls:'dev', acceptance:'B3/B4 真实后端测试', ownerPM:'Fei', ownerEng:'Fei', dep:'—' },
      { scope:'📊 S5', feature:'E2E CI 自动化', status:'开发中', statusCls:'dev', acceptance:'回归测试 + CI 集成', ownerPM:'—', ownerEng:'Kevin', dep:'—' },
      { scope:'🏗 S7', feature:'K8s 多副本 + PDB', status:'开发中', statusCls:'dev', acceptance:'消除单副本风险', ownerPM:'—', ownerEng:'Wenzhang', dep:'—' },
      { scope:'🏗 S7', feature:'OpenClaw 上游升级', status:'Todo', statusCls:'todo', acceptance:'全量回归', ownerPM:'—', ownerEng:'Wenzhang', dep:'—' },
      { scope:'💳 S8', feature:'计费域模型 + Creem', status:'开发中', statusCls:'dev', acceptance:'四档定价, 支付闭环', ownerPM:'Ye Zou', ownerEng:'Wenzhang', dep:'—' },
      { scope:'💳 S8', feature:'Skill 分层访问', status:'开发中', statusCls:'dev', acceptance:'Pro/Free 权益分层', ownerPM:'Ye Zou', ownerEng:'Jin Xu', dep:'计费模型' },
      { scope:'📣 S9', feature:'Onboarding 优化', status:'开发中', statusCls:'dev', acceptance:'注册引导 + Landing Page', ownerPM:'—', ownerEng:'Gary', dep:'—' }
    ];

    let tableHTML = '<div style="overflow-x:auto"><table class="m1-table"><thead><tr>'
      + '<th>Scope</th><th>Feature / Deliverable</th><th>Status</th><th>验收标准</th><th>Owner (PM / Eng)</th><th>依赖</th>'
      + '</tr></thead><tbody>';

    m1Data.forEach(row => {
      tableHTML += '<tr>'
        + '<td class="m1-scope">' + row.scope + '</td>'
        + '<td class="m1-feature">' + row.feature + '</td>'
        + '<td><span class="m1-status ' + row.statusCls + '">' + row.status + '</span></td>'
        + '<td class="m1-acceptance">' + row.acceptance + '</td>'
        + '<td class="m1-owner">' + row.ownerPM + ' / ' + row.ownerEng + '</td>'
        + '<td class="m1-dep">' + row.dep + '</td>'
        + '</tr>';
    });

    tableHTML += '</tbody></table></div>';

    // Add progress summary
    const devCount = m1Data.filter(r => r.statusCls === 'dev').length;
    const todoCount = m1Data.filter(r => r.statusCls === 'todo').length;
    const planCount = m1Data.filter(r => r.statusCls === 'plan').length;
    const total = m1Data.length;
    const devPct = Math.round((devCount/total)*100);

    const summaryHTML = '<div style="display:flex;gap:var(--space-3);margin-bottom:var(--space-4)">'
      + '<div style="text-align:center;padding:var(--space-2) var(--space-4);background:rgba(245,158,11,.08);border:1px solid rgba(245,158,11,.2);border-radius:var(--radius-sm)"><div style="font-family:var(--font-mono);font-size:1.2rem;font-weight:700;color:var(--warning)">' + devCount + '</div><div style="font-size:0.6rem;color:var(--fg-subtle)">开发中</div></div>'
      + '<div style="text-align:center;padding:var(--space-2) var(--space-4);background:rgba(59,130,246,.08);border:1px solid rgba(59,130,246,.2);border-radius:var(--radius-sm)"><div style="font-family:var(--font-mono);font-size:1.2rem;font-weight:700;color:var(--info)">' + planCount + '</div><div style="font-size:0.6rem;color:var(--fg-subtle)">排期/规划</div></div>'
      + '<div style="text-align:center;padding:var(--space-2) var(--space-4);background:rgba(113,113,122,.08);border:1px solid rgba(113,113,122,.2);border-radius:var(--radius-sm)"><div style="font-family:var(--font-mono);font-size:1.2rem;font-weight:700;color:var(--fg-subtle)">' + todoCount + '</div><div style="font-size:0.6rem;color:var(--fg-subtle)">Todo</div></div>'
      + '<div style="text-align:center;padding:var(--space-2) var(--space-4);background:var(--bg-subtle);border:1px solid var(--border-base);border-radius:var(--radius-sm)"><div style="font-family:var(--font-mono);font-size:1.2rem;font-weight:700">' + devPct + '%</div><div style="font-size:0.6rem;color:var(--fg-subtle)">已启动</div></div>'
      + '</div>';

    m1El.innerHTML = summaryHTML + tableHTML;
  }

  // M2-M4 Roadmap
  const roadmapEl = document.getElementById('milestoneRoadmap');
  if (roadmapEl) {
    roadmapEl.innerHTML = `
      <div class="ms-card m2">
        <h3>M2: Personalization Foundation</h3>
        <div class="ms-dates">4/15 → 5/15 · 30 days</div>
        <div class="ms-core"><strong style="font-size:0.72rem;color:var(--fg-muted)">Core Deliverables:</strong>
          <ul style="margin:var(--space-1) 0;padding-left:var(--space-4)">
            <li>User Profile Schema + 个性化引擎</li>
            <li>Knowledge Pipeline Phase 1-2</li>
            <li>Benchmark & Skill 评测体系</li>
          </ul>
        </div>
        <div class="ms-deps">📌 Depends on: M1 认证修复完成, GRPS v1 上线</div>
        <div class="ms-ns">🎯 North Star: Suggestion Adoption Rate trending up</div>
        <div class="ms-effort">~14 Epics · 重点 S4 S3 S5</div>
      </div>
      <div class="ms-card m3">
        <h3>M3: Constrained Autonomous Execution</h3>
        <div class="ms-dates">5/15 → 7/15 · 60 days</div>
        <div class="ms-core"><strong style="font-size:0.72rem;color:var(--fg-muted)">Core Deliverables:</strong>
          <ul style="margin:var(--space-1) 0;padding-left:var(--space-4)">
            <li>Trust Gradient 三维信任体系</li>
            <li>预案制自动执行</li>
            <li>安全防护 + 熔断机制</li>
            <li>Trading API 升级</li>
          </ul>
        </div>
        <div class="ms-deps">📌 Depends on: M2 Knowledge Pipeline, M2 Trust 积分</div>
        <div class="ms-ns">🎯 North Star: Auto-Execution Trust Retention 70% at Day 30</div>
        <div class="ms-effort">~14 Epics · 重点 S2 S4 S3</div>
      </div>
      <div class="ms-card m4">
        <h3>M4: Self-Evolution Loop</h3>
        <div class="ms-dates">7/15 → 10/15 · 90 days</div>
        <div class="ms-core"><strong style="font-size:0.72rem;color:var(--fg-muted)">Core Deliverables:</strong>
          <ul style="margin:var(--space-1) 0;padding-left:var(--space-4)">
            <li>Eval 派生指标 + 反馈管线</li>
            <li>Population-level risk model</li>
            <li>回测全链路</li>
          </ul>
        </div>
        <div class="ms-deps">📌 Depends on: M3 自动执行稳定运行</div>
        <div class="ms-ns">🎯 North Star: Agent Decision Quality Score 月度提升</div>
        <div class="ms-effort">~10 Epics · 重点 S5 S4</div>
      </div>
    `;
  }

  // Weekly Sync Agenda
  const syncEl = document.getElementById('weeklySyncAgenda');
  if (syncEl) {
    syncEl.innerHTML = `<div class="sync-box">
<span class="sync-title">📅 周二 Milestone Sync（Chris + Jack + Justin，30min）</span>
<span class="sync-sep">━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━</span>
<span class="sync-section">1. 🔴 Blocker Review (5min)</span>
<span class="sync-detail">— 阻塞项 / 跨模块依赖卡点 / 资源冲突</span>

<span class="sync-section">2. 📊 M1 Execution Sheet 逐项过 (15min)</span>
<span class="sync-detail">— 每个 🔴 Must 更新状态 + 验收标准确认</span>
<span class="sync-detail">— 新增/变更的依赖关系</span>
<span class="sync-detail">— 超载人员 triage (&gt;6 issue)</span>

<span class="sync-section">3. 🎯 Top 3 Action Items (5min)</span>
<span class="sync-detail">— 本周必须推进的 3 件事</span>
<span class="sync-detail">— Owner + 截止时间</span>

<span class="sync-section">4. 🗓 下周预告 (5min)</span>
<span class="sync-detail">— 即将进入的 Epic / 需要 kick-off 的模块</span>
<span class="sync-detail">— Milestone 健康度判断（on track / at risk / blocked）</span>

<span class="sync-sep">━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━</span>
<span class="sync-footer">Follow-up: Chris 按 Scope/Epic 追 owner + double check 验收标准</span>
<span class="sync-footer">月底: Milestone Readiness Check（全员）</span>
</div>`;
  }
}

"""

html = html.replace(
    "/* ── Init ──",
    milestone_js + "/* ── Init ──"
)

# ═══════════════════════════════════════════════════════════
# 14. Update chriszhu in nameMap
# ═══════════════════════════════════════════════════════════
html = html.replace(
    "const nameMap = {jackjun:'JackJun',fei:'Fei',xujin:'Jin Xu',gary:'Gary',ethan:'Ethan',alex:'Alex',lirui:'Rui Li',regison:'Regison',wenzhang:'Wenzhang',jiagui:'Jiagui',peter:'Peter',zouye:'Ye Zou',sylvia:'Sylvia',yixintan:'Yi Tan',hanliang:'Liang Han',tao:'Tao Yuan',jim:'Jim',kevin:'Kevin',justin:'Justin',unassigned:'—'};",
    "const nameMap = {jackjun:'JackJun',fei:'Fei',xujin:'Jin Xu',gary:'Gary',ethan:'Ethan',alex:'Alex',lirui:'Rui Li',regison:'Regison',wenzhang:'Wenzhang',jiagui:'Jiagui',peter:'Peter',zouye:'Ye Zou',sylvia:'Sylvia',yixintan:'Yi Tan',hanliang:'Liang Han',tao:'Tao Yuan',jim:'Jim',kevin:'Kevin',justin:'Justin',chriszhu:'Chris Zhu',unassigned:'—'};"
)

# ═══════════════════════════════════════════════════════════
# 15. Fix the priority mapping to handle 'no priority'
# ═══════════════════════════════════════════════════════════
html = html.replace(
    "const priorityColors = {urgent:'#ef4444',high:'#f59e0b',medium:'#3b82f6',low:'#22c55e',none:'#52525b'};",
    "const priorityColors = {urgent:'#ef4444',high:'#f59e0b',medium:'#3b82f6',low:'#22c55e',none:'#52525b','no priority':'#52525b'};"
)

# ═══════════════════════════════════════════════════════════
# Write the result
# ═══════════════════════════════════════════════════════════
with open('/tmp/kanban-update/index.html', 'w') as f:
    f.write(html)

print(f"✅ Generated /tmp/kanban-update/index.html")
print(f"   Size: {len(html):,} chars")

# Quick validation
assert 'v9.0' in html, "Missing v9.0"
assert 'tab-milestone' in html, "Missing milestone tab"
assert 'PRODUCT-2499' in html, "Missing cycle23 issues"
assert 'ENG-1184' in html, "Missing cycle22 issues"
assert 'S1 Core Experience' in html, "Missing 9-scope tree"
assert 'renderMilestone' in html, "Missing milestone render"
assert 'M2: Personalization' in html, "Missing M2 roadmap"
print("   All validations passed ✅")
