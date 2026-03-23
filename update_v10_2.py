#!/usr/bin/env python3
"""
Update D0 Product Kanban v10.2:
1. Strategic Matrix — add cycle issues to appropriate cells
2. v2/v3/v4 milestone — detailed epic tables with acceptance criteria
3. Risk resolution — remove resolved, move remaining to Sprint Board
4. CEO focus — link to Sprint Board risks
5. Version ↔ Matrix mapping
"""

with open('/tmp/kanban-repo/index.html', 'r') as f:
    html = f.read()

# ═══════════════════════════════════════════════════════════
# 1. STRATEGIC MATRIX — Add issues to cells
# ═══════════════════════════════════════════════════════════

def add_to_cell(html, cell_id, new_items_html):
    """Add items to a matrix cell's <ul> list."""
    marker = f'id="{cell_id}"'
    idx = html.find(marker)
    if idx == -1:
        print(f"  ⚠️ Cell {cell_id} not found")
        return html
    # Find the </ul> within this cell
    ul_end = html.find('</ul>', idx)
    if ul_end == -1:
        print(f"  ⚠️ No </ul> in {cell_id}")
        return html
    html = html[:ul_end] + new_items_html + html[ul_end:]
    return html

def li(text, issue_id=None, status=''):
    """Create a list item with optional issue link."""
    s = ''
    if status:
        cls = 'wip' if status in ('WIP','In Progress') else 'planned' if status == 'planned' else 'done'
        s = f' <span class="{cls}">{status}</span>'
    if issue_id:
        link = f'<a class="card-id" href="https://linear.app/donutbrowser/issue/{issue_id}" target="_blank">{issue_id}</a>'
        return f'\n            <li>{text} — {link}{s}</li>'
    return f'\n            <li>{text}{s}</li>'

# P0×S0 (Reactive × Research) — add core experience issues
html = add_to_cell(html, 'cell-P0-S0',
    li('困难用例 12 场景', 'PRODUCT-1948', 'WIP')
    + li('MCP 精简 170→22', 'PRODUCT-2261', 'WIP')
    + li('Chat 意图识别路由', 'PRODUCT-2308')
    + li('D0 自定义看板', 'PRODUCT-1949', 'WIP')
)

# P0×S1 (Reactive × Guarded) — add trading issues  
html = add_to_cell(html, 'cell-P0-S1',
    li('Jupiter V2 全量迁移', 'PRODUCT-2216', 'WIP')
    + li('杠杆持久化', 'PRODUCT-2492')
    + li('EVM Gas 费预留', 'PRODUCT-1939')
    + li('Polymarket CLOB 修复', 'PRODUCT-2015', 'WIP')
)

# P0×S2 (Reactive × Managed) — add safety issues
html = add_to_cell(html, 'cell-P0-S2',
    li('外部攻击面收敛', 'PRODUCT-2229')
    + li('Agent 签名授权模型', 'PRODUCT-1902')
    + li('数据诚实性加固', 'PRODUCT-1918', 'WIP')
)

# P1×S0 (Monitor × Research) — add knowledge/proactive
html = add_to_cell(html, 'cell-P1-S0',
    li('信号处理层 Regime+Signal', 'PRODUCT-1974', 'WIP')
    + li('用户行为记忆 v3', 'PRODUCT-2297', 'WIP')
    + li('User Profile Schema', 'PRODUCT-1736', 'WIP')
    + li('Explore 页面 MVP', 'PRODUCT-1682', 'WIP')
    + li('Discover 1.0', 'PRODUCT-1970')
)

# P1×S1 (Monitor × Guarded) — add strategy items
html = add_to_cell(html, 'cell-P1-S1',
    li('PM 最小闭环 Yield→下单→止损', 'PRODUCT-2114')
    + li('PM 订单功能增强', 'PRODUCT-2117')
    + li('Skill Hunter 自我进化', 'PRODUCT-1840')
)

# P2×S1 — add strategy planning items
html = add_to_cell(html, 'cell-P2-S1',
    li('策略信号上线 News+Sport', 'PRODUCT-2115')
    + li('PM 策略发现框架', 'PRODUCT-2119')
)

# ═══════════════════════════════════════════════════════════
# 2. VERSION ↔ MATRIX MAPPING — Add to milestone timeline
# ═══════════════════════════════════════════════════════════
old_timeline = '''<div class="tl-title">📅 Milestone Timeline</div>
        <div class="tl-row"><span class="tl-when tw-now">NOW</span><span class="tl-coord">P0×S0~S1</span><span class="tl-desc">Reactive + Guarded — 基础交易 + 研究工具已就绪</span></div>
        <div class="tl-row"><span class="tl-when tw-30d">30D</span><span class="tl-coord">P1×S1</span><span class="tl-desc">Monitor + Guarded — Strategy Hub + GRPS + Proactive Alerts</span></div>
        <div class="tl-row"><span class="tl-when tw-3m">3M</span><span class="tl-coord">P2×S2</span><span class="tl-desc">Draft + Managed — Approval Inbox + Portfolio Risk + Audit</span></div>
        <div class="tl-row"><span class="tl-when tw-6m">6M</span><span class="tl-coord">P3×S2</span><span class="tl-desc">Constrained + Managed — Autonomous execution within policy</span></div>
        <div class="tl-row"><span class="tl-when tw-12m">12M</span><span class="tl-coord">P4×S3</span><span class="tl-desc">Adaptive + Continuous — Personalized 24/7 agent</span></div>'''

new_timeline = '''<div class="tl-title">📅 Version ↔ Matrix Mapping</div>
        <div class="tl-row"><span class="tl-when tw-now">v1</span><span class="tl-coord">P0×S0~S1</span><span class="tl-desc">「看得清」Reactive + Guarded — 核心流程跑通，能用敢用愿意付费</span></div>
        <div class="tl-row"><span class="tl-when tw-30d">v2</span><span class="tl-coord">P1×S1~S2</span><span class="tl-desc">「想得明」Monitor + Managed — 个性化基础 + 知识体系 + 评测</span></div>
        <div class="tl-row"><span class="tl-when tw-3m">v3</span><span class="tl-coord">P2~P3×S2</span><span class="tl-desc">「做得住」Draft→Constrained — 自动执行 + 风控闭环 + 审批</span></div>
        <div class="tl-row"><span class="tl-when tw-12m">v4</span><span class="tl-coord">P3~P4×S3</span><span class="tl-desc">「越来越好」Continuous — 质量闭环 + 增长 + 自我进化</span></div>'''

html = html.replace(old_timeline, new_timeline)

# ═══════════════════════════════════════════════════════════
# 3. RISK RESOLUTION — Clean up resolved, restructure
# ═══════════════════════════════════════════════════════════
# Replace the entire risk section content
old_risk_grid_start = '<div class="risk-grid">'
old_risk_grid_end = '</div>\n    <div class="sec"><div class="sec-head"><span class="sec-num">05</span>'

risk_start = html.index(old_risk_grid_start)
risk_end = html.index(old_risk_grid_end)

new_risk_section = '''<div style="background:rgba(34,197,94,.06);border:1px solid rgba(34,197,94,.2);border-radius:var(--radius-lg);padding:var(--space-3) var(--space-4);margin-bottom:var(--space-4);font-size:0.78rem">
      <span style="color:var(--success);font-weight:600">✅ 已解决 (本轮清除)</span>
      <ul style="margin:var(--space-2) 0 0;padding-left:var(--space-4);color:var(--fg-muted)">
        <li><del>AI 层两核心模块无 Owner (1834/1800)</del> — 两个 issue 已 Canceled，方向调整</li>
        <li><del>Jiagui Sprint 过载 (15 issues)</del> — 已 triage 到 4 个 active issue</li>
        <li><del>商业化关键路径未启动</del> — PRODUCT-2121 计费域模型已 In Progress</li>
      </ul>
    </div>
    <div class="risk-grid">
      <div class="risk-item"><div><div class="ri-sev high">HIGH</div></div><div class="ri-problem"><strong>Ethan = Agents 单点故障</strong><br>agents-backend sole owner. 多链资产/Deposit/Withdraw/Transfer + Polymarket 全压一人。<br><span style="font-family:var(--font-mono);font-size:0.62rem;color:var(--fg-subtle)">→ Sprint Board: Ethan 名下 issue 查看</span></div><div class="ri-fix"><strong>行动:</strong> Regison 做 buddy reviewer (Jupiter V2 进行中) · Ethan 输出架构文档</div></div>
      <div class="risk-item"><div><div class="ri-sev high">HIGH</div></div><div class="ri-problem"><strong>d0-cli 工具精简进行中</strong><br>MCP 170→22 合并 (PRODUCT-2261) 在 In Review，但全量验证未完成。<br><span style="font-family:var(--font-mono);font-size:0.62rem;color:var(--fg-subtle)">→ Sprint Board: PRODUCT-2261 状态</span></div><div class="ri-fix"><strong>行动:</strong> Regison Review 中 · 验证功能无退化 + token 降 30%</div></div>
      <div class="risk-item"><div><div class="ri-sev high">HIGH</div></div><div class="ri-problem"><strong>交易三路径无统一标准</strong><br>Perps(Java)/Spot(TS)/Agents(Go) 体验不一致。Peter 标准文档仍未输出。<br><span style="font-family:var(--font-mono);font-size:0.62rem;color:var(--fg-subtle)">→ CEO 关注线: 预置交易策略</span></div><div class="ri-fix"><strong>行动:</strong> Peter 交易体验标准 → Alex/Regison/Ethan 对齐</div></div>
      <div class="risk-item"><div><div class="ri-sev med">MEDIUM</div></div><div class="ri-problem"><strong>Jiagui = Safety 单点</strong><br>容器安全 + 隔离 sole owner（4 个 active issue）。<br><span style="font-family:var(--font-mono);font-size:0.62rem;color:var(--fg-subtle)">→ Sprint Board: Jiagui 名下查看</span></div><div class="ri-fix"><strong>行动:</strong> Jin Xu 或 Gary 做 buddy · 文档化</div></div>
      <div class="risk-item"><div><div class="ri-sev med">MEDIUM</div></div><div class="ri-problem"><strong>多副本改造进行中</strong><br>Wenzhang 在做 K8s PDB (PRODUCT-2043)，Perps 多副本 (PRODUCT-2189) 未开始。<br><span style="font-family:var(--font-mono);font-size:0.62rem;color:var(--fg-subtle)">→ Sprint Board: PRODUCT-2043 / 2189</span></div><div class="ri-fix"><strong>行动:</strong> Wenzhang 总 owner · 优先级: Perps > Backend > Wallet</div></div>
      <div class="risk-item"><div><div class="ri-sev high">HIGH · NEW</div></div><div class="ri-problem"><strong>成本监控缺失</strong><br>LLM API 日消耗无实时 Dashboard · Orphan Container 持续烧钱 · Prompt Cache Miss 率高。<br><span style="font-family:var(--font-mono);font-size:0.62rem;color:var(--fg-subtle)">→ CEO 关注线: 成本估算</span></div><div class="ri-fix"><strong>行动:</strong> PRODUCT-2496 成本 Tracking (JackJun) · PRODUCT-2497 Container 回收 (Jiagui) · PRODUCT-2499 模型路由 (—)</div></div>
      <div class="risk-item"><div><div class="ri-sev high">HIGH · NEW</div></div><div class="ri-problem"><strong>策略基座未就绪</strong><br>Strategy Hub (PRODUCT-2185) 仍在 Planning · 回测引擎未开始 · PM Pipeline 分散。<br><span style="font-family:var(--font-mono);font-size:0.62rem;color:var(--fg-subtle)">→ CEO 关注线: 预置交易策略</span></div><div class="ri-fix"><strong>行动:</strong> Peter kick-off 2185 · Liang Han 2114 PM 闭环 · Chris 策略校准</div></div>
      <div class="risk-item"><div><div class="ri-sev high">HIGH · NEW</div></div><div class="ri-problem"><strong>Knowledge Pipeline 全在 Planning</strong><br>PRODUCT-1872 Master Plan + 1790 信号学习 + 1878 知识提取 = 主动能力的数据基座，全部 Todo/Planning。<br><span style="font-family:var(--font-mono);font-size:0.62rem;color:var(--fg-subtle)">→ CEO 关注线: Agent 主动性</span></div><div class="ri-fix"><strong>行动:</strong> Chris kick-off 1872 · Jim 行为记忆 v3 先行 · JackJun 信号处理层</div></div>
    </div>'''

html = html[:risk_start] + new_risk_section + html[risk_end:]

# ═══════════════════════════════════════════════════════════
# 4. Challenge 决议 — Update resolved items
# ═══════════════════════════════════════════════════════════
# Update Challenge #7 (AI层空缺 → resolved)
html = html.replace(
    '<div class="cr-num">7</div><div class="cr-text" contenteditable><strong>AI 层两核心空缺</strong> → 1834 + 1800 需 Sprint P0 指派</div><div class="cr-resolution action" onclick="cycleRes(this)">→ 需指派</div>',
    '<div class="cr-num">7</div><div class="cr-text" contenteditable><strong>AI 层两核心空缺</strong> → 1834 + 1800 已 Canceled，方向调整为知识管线 + 信号处理层</div><div class="cr-resolution resolved" onclick="cycleRes(this)">✓ 已关闭</div>'
)

# Update pending box
html = html.replace(
    '待决: ① PRODUCT-1834 / 1800 owner 指派 ② Peter 交易标准文档 ③ Ethan buddy reviewer 确认 ④ Jiagui Extension 文档化',
    '待决: ① Peter 交易体验标准文档 ② Ethan buddy reviewer 确认 ③ Jiagui Extension buddy 文档化 ④ PRODUCT-2185 策略基座 kick-off'
)

# ═══════════════════════════════════════════════════════════
# 5. MILESTONE v2/v3/v4 — Detailed epic tables
# ═══════════════════════════════════════════════════════════
old_milestone_fn = "function renderMilestone() {"
ms_fn_start = html.index(old_milestone_fn)
ms_fn_end = html.index("/* ── Init ──")

# Build the new comprehensive renderMilestone function
new_milestone_fn = r'''function renderMilestone() {
  // ═══ v1「看得清」═══
  var m1El = document.getElementById('m1ExecutionSheet');
  if (m1El) {
    var v1P0 = [
      { epic:'PRODUCT-1948', name:'困难用例', desc:'12 个高频交易场景全部跑通', accept:'12 场景成功率 ≥ 80%', owner:'JackJun', status:'In Progress' },
      { epic:'PRODUCT-2184', name:'Dashboard', desc:'首版 UI 体验基线', accept:'持仓/交易/盈亏可见，加载 ≤ 3s', owner:'Gary + Yi Tan', status:'In Progress' },
      { epic:'PRODUCT-2205', name:'账户认证', desc:'Session/Login/Turnkey 修复', accept:'全流程无阻断', owner:'Gary', status:'Todo' },
      { epic:'PRODUCT-2149', name:'安全修复', desc:'51 个安全漏洞主体修复', accept:'P0/P1 全清，复扫无 Critical', owner:'Jiagui', status:'In Progress' },
      { epic:'PRODUCT-2207', name:'风控引擎', desc:'链上风控规则 + 参数约束 v1', accept:'GRPS 生效，超限被拦截', owner:'Sylvia + Rui Li', status:'Todo' },
      { epic:'PRODUCT-2317', name:'合约测试', desc:'Counter/Settlement/Liquidation', accept:'覆盖率 ≥ 60%，CI 通过', owner:'Peter + Kevin', status:'In Progress' },
      { epic:'PRODUCT-1813', name:'止盈止损', desc:'TP/SL v1 实现', accept:'触发延迟 ≤ 30s', owner:'Peter', status:'In Progress' },
      { epic:'PRODUCT-2009', name:'付费 MVP', desc:'Stripe 接入 + 四档定价', accept:'订阅/升级/取消全流程', owner:'Ye Zou', status:'Planning' },
      { epic:'PRODUCT-1768', name:'Launch Plan', desc:'种子用户获取', accept:'50+ 注册，首批付费', owner:'Ruqi Hu', status:'In Progress' }
    ];
    var v1P1 = [
      { epic:'PRODUCT-2197', name:'MCP 整合', desc:'170→22 工具合并', accept:'功能无退化，token 降 ≥ 30%', owner:'Regison', status:'In Review' },
      { epic:'PRODUCT-2206', name:'AI 行为规则', desc:'D0 性格 + TG Bot 行为', accept:'10 条对话测试通过', owner:'Jin Xu', status:'In Progress' },
      { epic:'PRODUCT-2296', name:'策略逻辑校准', desc:'Poly/Ruki 交易逻辑', accept:'采纳率提升', owner:'Chris', status:'Planning' },
      { epic:'PRODUCT-2216', name:'Jupiter V2', desc:'链上 Adapter 重构', accept:'成功率 ≥ 90%', owner:'Ethan', status:'In Progress' },
      { epic:'PRODUCT-2208', name:'AI 可信性', desc:'置信度标注', accept:'高置信准确率 ≥ 85%', owner:'JackJun', status:'In Progress' },
      { epic:'PRODUCT-2413', name:'Beta Tester', desc:'社区交易员验证', accept:'≥ 10 人参与', owner:'Melvin', status:'Todo' },
      { epic:'PRODUCT-2215', name:'Onboarding', desc:'注册引导 + Landing', accept:'≤ 3 步，可追踪', owner:'Justin', status:'In Progress' }
    ];

    function makeTable(items, prioLabel) {
      var pc = prioLabel==='P0'?'var(--error)':'var(--warning)';
      var h = '<div style="margin-bottom:var(--space-4)"><div style="font-family:var(--font-mono);font-size:0.68rem;font-weight:600;color:'+pc+';margin-bottom:var(--space-2)">'+prioLabel+'</div>';
      h += '<div style="overflow-x:auto"><table class="m1-table"><thead><tr><th>Epic</th><th>做什么</th><th>验收标准</th><th>负责人</th><th>Status</th></tr></thead><tbody>';
      items.forEach(function(r) {
        var stCls = (r.status==='In Progress'||r.status==='In Review')?'dev':r.status==='Todo'?'todo':'plan';
        h += '<tr><td class="m1-scope"><a class="card-id" href="https://linear.app/donutbrowser/issue/'+r.epic+'" target="_blank">'+r.epic+'</a></td>';
        h += '<td class="m1-feature">'+r.name+'<br><span style="font-size:0.68rem;color:var(--fg-subtle)">'+r.desc+'</span></td>';
        h += '<td class="m1-acceptance">'+r.accept+'</td>';
        h += '<td class="m1-owner">'+r.owner+'</td>';
        h += '<td><span class="m1-status '+stCls+'">'+r.status+'</span></td></tr>';
      });
      h += '</tbody></table></div></div>';
      return h;
    }

    function versionGate(label, ns, gate) {
      return '<div style="background:var(--bg-subtle);border:1px solid var(--border-base);border-radius:var(--radius-lg);padding:var(--space-3) var(--space-4);margin-bottom:var(--space-4)">'
        + '<div style="display:flex;justify-content:space-between;align-items:center">'
        + '<div><span style="font-family:var(--font-display);font-size:1.1rem">'+label+'</span></div>'
        + '<div style="font-family:var(--font-mono);font-size:0.62rem;color:var(--info);background:rgba(59,130,246,.08);padding:var(--space-1) var(--space-3);border-radius:100px">🎯 '+ns+'</div></div>'
        + '<div style="font-family:var(--font-mono);font-size:0.68rem;color:var(--fg-muted);margin-top:var(--space-2)">✅ 版本达成门槛: '+gate+'</div></div>';
    }

    function progressSummary(items) {
      var ip = items.filter(function(r){return r.status==='In Progress'||r.status==='In Review'}).length;
      var td = items.filter(function(r){return r.status==='Todo'}).length;
      var pl = items.filter(function(r){return r.status==='Planning'}).length;
      var pct = Math.round((ip/items.length)*100);
      return '<div style="display:flex;gap:var(--space-3);margin-bottom:var(--space-4)">'
        + '<div style="text-align:center;padding:var(--space-2) var(--space-4);background:rgba(245,158,11,.08);border:1px solid rgba(245,158,11,.2);border-radius:var(--radius-sm)"><div style="font-family:var(--font-mono);font-size:1.1rem;font-weight:700;color:var(--warning)">'+ip+'</div><div style="font-size:0.58rem;color:var(--fg-subtle)">开发/Review</div></div>'
        + '<div style="text-align:center;padding:var(--space-2) var(--space-4);background:rgba(113,113,122,.08);border:1px solid rgba(113,113,122,.2);border-radius:var(--radius-sm)"><div style="font-family:var(--font-mono);font-size:1.1rem;font-weight:700;color:var(--fg-subtle)">'+td+'</div><div style="font-size:0.58rem;color:var(--fg-subtle)">Todo</div></div>'
        + '<div style="text-align:center;padding:var(--space-2) var(--space-4);background:rgba(59,130,246,.08);border:1px solid rgba(59,130,246,.2);border-radius:var(--radius-sm)"><div style="font-family:var(--font-mono);font-size:1.1rem;font-weight:700;color:var(--info)">'+pl+'</div><div style="font-size:0.58rem;color:var(--fg-subtle)">规划中</div></div>'
        + '<div style="text-align:center;padding:var(--space-2) var(--space-4);background:var(--bg-subtle);border:1px solid var(--border-base);border-radius:var(--radius-sm)"><div style="font-family:var(--font-mono);font-size:1.1rem;font-weight:700">'+pct+'%</div><div style="font-size:0.58rem;color:var(--fg-subtle)">已启动</div></div></div>';
    }

    var out = '';
    // v1 Gate
    out += versionGate('v1「看得清」— 核心流程跑通', '北极星: 7日交易用户留存率', '全部 P0 Epic 验收通过 = v1 达成');
    out += '<div style="font-family:var(--font-mono);font-size:0.62rem;color:var(--fg-subtle);margin-bottom:var(--space-2)">矩阵对应: P0×S0~S1 (Reactive + Guarded)</div>';
    out += progressSummary(v1P0.concat(v1P1));
    out += makeTable(v1P0, 'P0');
    out += makeTable(v1P1, 'P1');

    m1El.innerHTML = out;
  }

  // ═══ v2/v3/v4 Roadmap ═══
  var roadmapEl = document.getElementById('milestoneRoadmap');
  if (roadmapEl) {
    // v2
    var v2P0 = [
      { epic:'PRODUCT-2209', name:'用户画像', desc:'Persona 定制 + 30天行为推断风险偏好', accept:'保守型/激进型收到不同建议；可查看/修改偏好', owner:'Justin + Sylvia', status:'Planning' },
      { epic:'PRODUCT-1872', name:'知识体系 P1-P2', desc:'数据采集 + 知识注入 + Crypto 前沿', accept:'知识检索命中率 ≥ 50%；回答最近 7 天行业动态', owner:'Chris + JackJun', status:'Planning' },
      { epic:'PRODUCT-2211', name:'评测体系', desc:'模型基准 + Skill 质量验证 + 自动化评测', accept:'Eval Harness 可运行；覆盖 ≥ 10 Skill；有基线分数', owner:'Fei', status:'In Progress' },
      { epic:'PRODUCT-2198', name:'Dashboard 功能', desc:'看板 + 自动化配置 + 金融数据展示', accept:'用户可配自动化规则；持仓/盈亏/历史一页可见', owner:'Ethan', status:'Todo' }
    ];
    var v2P1 = [
      { epic:'PRODUCT-2201', name:'主动推送', desc:'行情异动 Alert + 多语言推送', accept:'异动后 ≤ 60s 推送；支持中/英', owner:'JackJun', status:'Todo' },
      { epic:'PRODUCT-2210', name:'E2E 测试', desc:'CI 管线 + 压力测试', accept:'E2E 在 CI 自动运行；核心流程覆盖 ≥ 70%', owner:'Kevin', status:'In Progress' },
      { epic:'PRODUCT-1696', name:'数据埋点', desc:'后端行为埋点', accept:'关键操作有埋点；PostHog 可查', owner:'Fei', status:'Todo' },
      { epic:'PRODUCT-2008', name:'用户反馈', desc:'160 条 Beta 反馈消化', accept:'全部归类；P0 反馈转 issue', owner:'Sylvia', status:'Todo' },
      { epic:'PRODUCT-2217', name:'交易体验', desc:'持仓展示 + 委托单 + DeFi/跨链', accept:'持仓数据准确实时；≥ 3 链 DeFi 可用', owner:'Ethan', status:'Todo' },
      { epic:'PRODUCT-2214', name:'社区运营', desc:'KOL 合作启动', accept:'≥ 5 KOL 合作落地', owner:'Ruqi Hu', status:'Todo' },
      { epic:'PRODUCT-2129', name:'UI 收尾', desc:'v1 遗留 UI 问题修复', accept:'设计走查遗留清零', owner:'Yi Tan', status:'Todo' }
    ];
    var v2P2 = [
      { epic:'PRODUCT-2007', name:'图表方案', desc:'K 线技术选型', accept:'选型文档 + Demo 验证', owner:'Sylvia', status:'Todo' },
      { epic:'PRODUCT-1887', name:'财务看板', desc:'Finance Dashboard', accept:'收支按日/周/月查看', owner:'Ginger', status:'Todo' }
    ];

    // v3
    var v3P0 = [
      { epic:'PRODUCT-2199', name:'安全防护', desc:'限额 Guard + 熔断 + 大额审批', accept:'超限被拦截；极端行情自动降级；大额需二次确认', owner:'Jiagui + Rui Li', status:'Todo' },
      { epic:'PRODUCT-2017', name:'风控集成', desc:'D0 Bot 调用 GRPS 服务', accept:'每笔自动执行经 GRPS 校验；拒绝记录可查', owner:'Peter', status:'Todo' },
      { epic:'PRODUCT-1958', name:'交易升级', desc:'复合下单 + 幂等 + AI 合约策略', accept:'成功率 ≥ 95%；无重复交易', owner:'Peter', status:'Todo' },
      { epic:'PRODUCT-1872', name:'知识体系续', desc:'Phase 3-4 分析框架 + 反馈闭环', accept:'命中率 ≥ 70%；空白自动标记入队', owner:'Chris + JackJun', status:'Planning' }
    ];
    var v3P1 = [
      { epic:'PRODUCT-2217', name:'交易体验优化', desc:'委托单管理 + AI 分析理由链', accept:'完整委托单；理由链展示', owner:'Ethan', status:'Todo' },
      { epic:'PRODUCT-2204', name:'链上交易', desc:'DeFi / Staking / 跨链', accept:'≥ 5 DeFi 协议可用', owner:'Ethan', status:'Todo' },
      { epic:'PRODUCT-2014', name:'Polymarket', desc:'信号→策略→执行 pipeline', accept:'端到端自动化；盈亏可追踪', owner:'Hanliang', status:'Planning' },
      { epic:'PRODUCT-1959', name:'事件推送', desc:'Event Pipeline', accept:'执行状态实时通知用户', owner:'Peter', status:'Todo' }
    ];

    // v4
    var v4P0 = [
      { epic:'PRODUCT-1830', name:'质量看板', desc:'质量漏斗 / 看板 / 告警', accept:'异常自动告警；漏斗按日查看', owner:'Fei', status:'Todo' },
      { epic:'PRODUCT-1576', name:'反馈管线', desc:'用户反馈自动进入迭代', accept:'收集到 issue 全自动；≤ 72h', owner:'Fei', status:'In Progress' },
      { epic:'PRODUCT-1591', name:'执行埋点', desc:'每次执行可回溯', accept:'完整决策链可查', owner:'Fei', status:'In Progress' }
    ];
    var v4P1 = [
      { epic:'PRODUCT-1348', name:'回测流程', desc:'回测→模拟→实盘', accept:'全链路；偏差 ≤ 15%', owner:'Sylvia + Hanliang', status:'Todo' },
      { epic:'PRODUCT-2213', name:'产品优化', desc:'反馈驱动改进', accept:'Top 10 痛点有改进', owner:'Ruqi Hu', status:'Todo' },
      { epic:'PRODUCT-2438', name:'增长引擎', desc:'SEO + UGC + LLM 搜索', accept:'≥ 1 渠道月活 > 0', owner:'Quqiaochu', status:'Todo' },
      { epic:'PRODUCT-2442', name:'情报跟踪', desc:'竞品持续跟踪', accept:'周报；≥ 5 竞品监控', owner:'Quqiaochu', status:'Todo' },
      { epic:'ACADEMY-189', name:'组织改进', desc:'Sprint 复盘 + 协作优化', accept:'action items 完成率 ≥ 70%', owner:'Chris', status:'Todo' }
    ];

    function versionCard(ver, subtitle, matrixCoord, ns, gate, p0, p1, p2) {
      var cls = ver==='v2'?'m2':ver==='v3'?'m3':'m4';
      var h = '<div class="ms-card '+cls+'">';
      h += '<h3>'+ver+'「'+subtitle+'」</h3>';
      h += '<div class="ms-dates">矩阵: '+matrixCoord+' · 版本制，验收即上线</div>';
      h += '<div class="ms-ns">🎯 '+ns+'</div>';
      h += '<div style="background:rgba(34,197,94,.06);border:1px solid rgba(34,197,94,.15);border-radius:var(--radius-sm);padding:var(--space-2) var(--space-3);margin-bottom:var(--space-3);font-family:var(--font-mono);font-size:0.65rem;color:var(--success)">✅ 版本门槛: '+gate+'</div>';

      function epicList(items, label) {
        var lh = '<div style="margin-bottom:var(--space-3)"><div style="font-family:var(--font-mono);font-size:0.6rem;font-weight:600;color:'+(label==='P0'?'var(--error)':'var(--warning)')+';margin-bottom:var(--space-1)">'+label+' ('+items.length+' Epics)</div>';
        lh += '<div style="overflow-x:auto"><table style="width:100%;border-collapse:collapse;font-size:0.72rem"><tbody>';
        items.forEach(function(r) {
          lh += '<tr style="border-bottom:1px solid var(--border-base)">';
          lh += '<td style="padding:3px 6px;white-space:nowrap"><a class="card-id" href="https://linear.app/donutbrowser/issue/'+r.epic+'" target="_blank">'+r.epic+'</a></td>';
          lh += '<td style="padding:3px 6px;font-weight:500">'+r.name+'</td>';
          lh += '<td style="padding:3px 6px;color:var(--fg-muted);font-size:0.68rem">'+r.accept+'</td>';
          lh += '<td style="padding:3px 6px;font-family:var(--font-mono);font-size:0.62rem;color:var(--fg-subtle)">'+r.owner+'</td>';
          lh += '</tr>';
        });
        lh += '</tbody></table></div></div>';
        return lh;
      }

      h += epicList(p0, 'P0');
      h += epicList(p1, 'P1');
      if (p2 && p2.length) h += epicList(p2, 'P2');
      h += '</div>';
      return h;
    }

    roadmapEl.style.gridTemplateColumns = '1fr';
    roadmapEl.innerHTML = versionCard('v2','想得明','P1×S1~S2',
      '北极星: Suggestion Adoption Rate 随时长上升',
      '全部 P0 验收通过: 不同用户收到不同建议 + 知识检索命中 ≥ 50% + Eval 覆盖 ≥ 10 Skill',
      v2P0, v2P1, v2P2)
    + versionCard('v3','做得住','P2~P3×S2',
      '北极星: Auto-Execution Trust Retention 70% at Day 30',
      '全部 P0 验收通过: 超限被拦截 + 每笔过 GRPS + 复合下单成功率 ≥ 95% + 知识命中 ≥ 70%',
      v3P0, v3P1, [])
    + versionCard('v4','越来越好','P3~P4×S3',
      '北极星: Agent Decision Quality Score 月度提升',
      '全部 P0 验收通过: 异常自动告警 + 反馈→issue ≤ 72h + 决策链完整可查',
      v4P0, v4P1, []);
  }

  // Usage guide
  var syncEl = document.getElementById('weeklySyncAgenda');
  if (syncEl) {
    syncEl.innerHTML = '<div class="sync-box">'
      + '<span class="sync-title">📖 版本制规则</span>'
      + '<span class="sync-sep">━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━</span>'
      + '<span class="sync-section">版本不绑日历，验收即上线。</span>'
      + '<span class="sync-detail">每个 Epic 通过验收标准 = 该功能上线</span>'
      + '<span class="sync-detail">版本内全部 P0 验收通过 = 版本达成</span>'
      + '<span class="sync-sep">━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━</span>'
      + '<span class="sync-section">Version ↔ Matrix 对应:</span>'
      + '<span class="sync-detail">v1 = P0×S0~S1 (Reactive + Guarded)</span>'
      + '<span class="sync-detail">v2 = P1×S1~S2 (Monitor + Managed)</span>'
      + '<span class="sync-detail">v3 = P2~P3×S2 (Draft→Constrained)</span>'
      + '<span class="sync-detail">v4 = P3~P4×S3 (Continuous)</span>'
      + '<span class="sync-sep">━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━</span>'
      + '<span class="sync-section">Cycle Planning:</span>'
      + '<span class="sync-detail">1. PM 从当前版本 P0/P1 选 Epic → 拆成 cycle issue</span>'
      + '<span class="sync-detail">2. 每个 issue 进 Strategic Matrix 检查对齐度</span>'
      + '<span class="sync-detail">3. 两个维度都不符合 → 单独讨论</span>'
      + '<span class="sync-sep">━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━</span>'
      + '<span class="sync-detail">→ <a class="card-id" href="https://linear.app/donutbrowser/issue/PRODUCT-2167#comment-f80d90c8" target="_blank">v3 原文: PRODUCT-2167</a></span>'
      + '</div>';
  }
}

'''

html = html[:ms_fn_start] + new_milestone_fn + html[ms_fn_end:]

# ═══════════════════════════════════════════════════════════
# 6. Version bump
# ═══════════════════════════════════════════════════════════
html = html.replace('v10.1 · 2026-03-23', 'v10.2 · 2026-03-23')
html = html.replace('D0 Product Dashboard v10.1', 'D0 Product Dashboard v10.2')

# ═══════════════════════════════════════════════════════════
# Write
# ═══════════════════════════════════════════════════════════
with open('/tmp/kanban-repo/index.html', 'w') as f:
    f.write(html)

print(f"✅ Updated /tmp/kanban-repo/index.html ({len(html):,} chars)")

# Validation
checks = [
    ('Strategic Matrix P0S0 issues', 'PRODUCT-1948' in html and 'cell-P0-S0' in html),
    ('Strategic Matrix P1S0 issues', 'PRODUCT-1974' in html and 'cell-P1-S0' in html),
    ('Version gates', '版本达成门槛' in html),
    ('v2 epics', 'PRODUCT-2209' in html and '想得明' in html),
    ('v3 epics', 'PRODUCT-2199' in html and '做得住' in html),
    ('v4 epics', 'PRODUCT-1830' in html and '越来越好' in html),
    ('Risk resolved', '已解决' in html),
    ('New risks', '成本监控缺失' in html and '策略基座' in html),
    ('Matrix mapping', 'Version ↔ Matrix Mapping' in html),
    ('Challenge 7 resolved', '已关闭' in html),
    ('v10.2', 'v10.2' in html),
]

all_pass = True
for name, ok in checks:
    status = '✅' if ok else '❌'
    if not ok: all_pass = False
    print(f"  {status} {name}")

if all_pass:
    print("\n  All validations passed ✅")
else:
    print("\n  ⚠️ Some validations failed!")
