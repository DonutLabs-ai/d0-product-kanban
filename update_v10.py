#!/usr/bin/env python3
"""
Update D0 Product Kanban:
1. CEO 关注线 → 5 areas (成本估算, 商业化+支付闭环, 预置交易策略, 安全+风控, Agent主动性)
2. Milestone → v3 version-based (v1看得清, v2想得明, v3做得住, v4越来越好)
"""

import re

with open('/tmp/kanban-repo/index.html', 'r') as f:
    html = f.read()

# ═══════════════════════════════════════════════════════════
# 1. Replace CEO_FOCUS_AREAS (5 new focus areas)
# ═══════════════════════════════════════════════════════════
old_ceo_start = "const CEO_FOCUS_AREAS = ["
old_ceo_end = "function renderCEOFocus()"

ceo_start_idx = html.index(old_ceo_start)
ceo_end_idx = html.index(old_ceo_end)

new_ceo = """const CEO_FOCUS_AREAS = [
  {
    title: '💵 成本估算 — Infra + LLM 成本实时监控与优化',
    owners: 'JackJun (LLM) + Wenzhang (Infra) + Jiagui (容器)',
    color: '#ef4444',
    keywords: ['成本','cost','billing','token 用量','配额','quota','orphan','prompt cache','model routing','低成本','省','烧钱','infra cost','llm cost'],
    moduleKeys: ['scope7.infra','scope1.core'],
    risks: ['LLM API 日消耗无实时 Dashboard，月底才能看账单','Orphan Container 持续烧钱（TG 解绑后容器不回收）','Prompt Cache Miss 率高 → 每次全量计费','D0 简报系统 8.7 次 LLM 调用/次，月多花 $1,100'],
    criticalPath: ['PRODUCT-2496 线上成本 Tracking (Urgent/Todo)','PRODUCT-2499 模型 API 成本优化 (Urgent/Todo)','PRODUCT-2500 Prompt Cache Miss 修复 (Urgent/Triage)','PRODUCT-2498 简报 LLM 成本优化 (Urgent/Triage)','PRODUCT-2497 Orphan Container 泄漏 (High/In Review)']
  },
  {
    title: '💳 商业化 + 支付闭环 — 计费域 + Creem + Skill 分层',
    owners: 'Ye Zou (PM) + Wenzhang (Backend) + Jin Xu (Skill) + Gary (Frontend)',
    color: '#8b5cf6',
    keywords: ['付费','billing','计费','monetization','payment','subscription','quota','配额','会员','商业化','creem','pricing','skill 分层','membership','pricing page','checkout','plan config'],
    moduleKeys: ['scope8.commercial'],
    risks: ['计费域模型是所有支付功能的 foundation — 正在开发','Creem 第三方支付通道依赖','Skill 分层访问控制需要 AI-Core 配合','Membership Panel + Pricing Page UI 尚未开始'],
    criticalPath: ['PRODUCT-2121 计费域模型 (Urgent/In Progress)','PRODUCT-2122 Creem 支付通道 (High/In Progress)','PRODUCT-2485 Skill 分层访问 (High/In Progress)','PRODUCT-2009 商业化规划 MVP (High/Planning)','PRODUCT-2124 Membership Panel (High/Todo)','PRODUCT-2123 Pricing Page (High/Todo)']
  },
  {
    title: '📊 预置的交易策略 — Strategy Hub + 回测 + 信号生产',
    owners: 'Peter (PM) + Liang Han (量化) + Chris (知识)',
    color: '#f59e0b',
    keywords: ['strategy','策略','回测','backtest','signal','信号','polymarket','预置','preset','pipeline','yield bias','sport trading','news trading','hummingbot','discovery'],
    moduleKeys: ['scope2.trading','scope3.proactive'],
    risks: ['Strategy Hub 仍在 Product Planning 阶段','Polymarket 多个依赖 Epic 分散在不同人手中','预置策略需要量化 + AI + 交易三方协作','回测引擎是策略上线的前置依赖'],
    criticalPath: ['PRODUCT-2185 策略执行层 + 回测引擎 (Urgent/Planning)','PRODUCT-2114 PM 最小闭环 (Urgent/Todo)','PRODUCT-2115 策略信号上线 (High/Todo)','PRODUCT-2014 Polymarket Pipeline (High/Planning)','PRODUCT-2117 PM 订单功能增强 (High/Todo)']
  },
  {
    title: '🛡 安全 + 风控 — 漏洞清零 + GRPS + 权限控制',
    owners: 'Jiagui (容器安全) + Sylvia (GRPS) + JackJun (凭证)',
    color: '#dc2626',
    keywords: ['safety','安全','灾备','风控','grps','container','security','risk','漏洞','权限','隔离','凭证','签名','guard','熔断'],
    moduleKeys: ['scope4.safety'],
    risks: ['53 个安全漏洞中 P0/P1 尚未全部清零','GRPS 风控引擎与 D0 Bot 集成方案未启动','内部权限控制（防单人资金转移）仍在 Todo','K8s 硬编码凭证清理进行中','Agent 签名授权模型未明确'],
    criticalPath: ['PRODUCT-2228 内部权限控制 (Urgent/Todo)','PRODUCT-2207 GRPS v1 风控引擎 (Urgent/Todo)','PRODUCT-2493 GRPS D0 Bot 集成方案 (High/Todo)','PRODUCT-2154 K8s 凭证清理 (Urgent/In Progress)','PRODUCT-2227 容器隔离 (High/In Progress)','PRODUCT-1902 Agent 签名授权 (Urgent/Todo)']
  },
  {
    title: '🤖 Agent 的主动性 — 从 Reactive 到 Proactive',
    owners: 'Chris (Knowledge) + JackJun (AI Core) + Jin Xu (Skill)',
    color: '#3b82f6',
    keywords: ['proactive','主动','daily brief','推送','alert','预警','knowledge','知识','信号学习','记忆','briefing','cron','daily report','discover','signal','regime'],
    moduleKeys: ['scope3.proactive','scope6.personal'],
    risks: ['Knowledge Pipeline 仍在 Planning 阶段，是主动能力的数据基座','Daily Brief CTA 跳转缺失，推送效果无法闭环','信号学习闭环系统 (PRODUCT-1790) 核心但未启动','用户行为记忆系统 v3 在 Review 中，是个性化基础'],
    criticalPath: ['PRODUCT-1872 Knowledge Pipeline Master Plan (Urgent/Planning)','PRODUCT-1790 信号学习闭环 (Urgent/Todo)','PRODUCT-1878 知识提取管线 P2.2 (High/Todo)','PRODUCT-2297 用户行为记忆 v3 (High/In Review)','PRODUCT-2144 TG Bot Daily Brief CTA (Medium/Todo)','PRODUCT-1974 中间信号处理层 (High/In Progress)']
  }
];

"""

html = html[:ceo_start_idx] + new_ceo + html[ceo_end_idx:]

# ═══════════════════════════════════════════════════════════
# 2. Update CEO tab header text
# ═══════════════════════════════════════════════════════════
html = html.replace(
    'CEO 重点跟踪的跨团队关注领域 · 聚合相关 Issue 状态 · v9.0',
    'CEO 重点跟踪的 5 条主线 · 聚合相关 Issue 状态 · v10.1'
)
html = html.replace(
    'CEO 重点跟踪的跨团队关注领域 · 聚合相关 Issue 状态 · v10.0',
    'CEO 重点跟踪的 5 条主线 · 聚合相关 Issue 状态 · v10.1'
)
html = html.replace(
    '🎯 CEO 关注线 — 4 条主线',
    '🎯 CEO 关注线 — 5 条主线'
)

# ═══════════════════════════════════════════════════════════
# 3. Replace renderMilestone with v3 version-based structure
# ═══════════════════════════════════════════════════════════
old_milestone_start = "function renderMilestone() {"
old_milestone_end = "/* ── Init ──"

ms_start_idx = html.index(old_milestone_start)
ms_end_idx = html.index(old_milestone_end)

new_milestone = r"""function renderMilestone() {
  // v3 Version-Based Milestone (from PRODUCT-2167)
  const m1El = document.getElementById('m1ExecutionSheet');
  if (m1El) {
    // v1 "看得清" — Epic table with acceptance criteria
    const v1P0 = [
      { epic:'PRODUCT-1948', name:'困难用例', desc:'12 个高频交易场景全部跑通', accept:'12 场景成功率 ≥ 80%', owner:'JackJun', status:'In Progress' },
      { epic:'PRODUCT-2184', name:'Dashboard', desc:'首版 UI 体验基线', accept:'持仓/交易/盈亏可见，加载 ≤ 3s', owner:'Gary + Yi Tan', status:'In Progress' },
      { epic:'PRODUCT-2205', name:'账户认证', desc:'Session/Login/Turnkey 修复', accept:'全流程无阻断，Session 不过期', owner:'Gary', status:'Todo' },
      { epic:'PRODUCT-2149', name:'安全修复', desc:'51 个安全漏洞主体修复', accept:'P0/P1 漏洞全清，安全复扫无 Critical', owner:'Jiagui', status:'In Progress' },
      { epic:'PRODUCT-2207', name:'风控引擎', desc:'链上风控规则 + 参数约束 v1', accept:'GRPS 生效，超限被拦截，有日志', owner:'Sylvia + Rui Li', status:'Todo' },
      { epic:'PRODUCT-2317', name:'合约测试', desc:'Counter/Settlement/Liquidation 覆盖', accept:'三模块覆盖率 ≥ 60%，CI 通过', owner:'Peter + Kevin', status:'In Progress' },
      { epic:'PRODUCT-1813', name:'止盈止损', desc:'TP/SL v1 实现', accept:'触发延迟 ≤ 30s，记录可查', owner:'Peter', status:'In Progress' },
      { epic:'PRODUCT-2009', name:'付费 MVP', desc:'Stripe 接入 + 四档定价', accept:'订阅/升级/取消全流程跑通', owner:'Ye Zou', status:'Planning' },
      { epic:'PRODUCT-1768', name:'Launch Plan', desc:'种子用户获取 Phase 0-2', accept:'50+ 注册，首批付费用户', owner:'Ruqi Hu', status:'In Progress' }
    ];
    const v1P1 = [
      { epic:'PRODUCT-2197', name:'MCP 整合', desc:'170→22 工具合并', accept:'功能无退化，token 降 ≥ 30%', owner:'Regison', status:'In Review' },
      { epic:'PRODUCT-2206', name:'AI 行为规则', desc:'D0 性格 + TG Bot 行为', accept:'10 条对话测试通过', owner:'Jin Xu', status:'In Progress' },
      { epic:'PRODUCT-2296', name:'策略逻辑校准', desc:'Poly/Ruki 交易逻辑', accept:'采纳率较校准前提升', owner:'Chris', status:'Planning' },
      { epic:'PRODUCT-2216', name:'Jupiter V2', desc:'链上 Adapter 重构 + 签名', accept:'成功率 ≥ 90%，无安全漏洞', owner:'Ethan', status:'In Progress' },
      { epic:'PRODUCT-2208', name:'AI 可信性', desc:'置信度标注，减幻觉', accept:'高置信准确率 ≥ 85%', owner:'JackJun', status:'In Progress' },
      { epic:'PRODUCT-2413', name:'Beta Tester', desc:'社区交易员验证策略', accept:'≥ 10 交易员参与', owner:'Melvin', status:'Todo' },
      { epic:'PRODUCT-2215', name:'Onboarding', desc:'注册引导 + Landing Page', accept:'≤ 3 步，转化率可追踪', owner:'Justin', status:'In Progress' }
    ];

    let tableHTML = '<div style="font-family:var(--font-display);font-size:1.6rem;font-weight:400;margin-bottom:var(--space-1)">v1「看得清」— 核心流程跑通</div>';
    tableHTML += '<div style="font-family:var(--font-mono);font-size:0.68rem;color:var(--fg-subtle);margin-bottom:var(--space-4)">用户能用、敢用、愿意付费 · P0: ' + v1P0.length + ' Epics · P1: ' + v1P1.length + ' Epics</div>';

    function makeTable(items, priorityLabel) {
      let h = '<div style="margin-bottom:var(--space-4)"><div style="font-family:var(--font-mono);font-size:0.68rem;font-weight:600;color:' + (priorityLabel==='P0'?'var(--error)':'var(--warning)') + ';margin-bottom:var(--space-2)">' + priorityLabel + '</div>';
      h += '<div style="overflow-x:auto"><table class="m1-table"><thead><tr><th>Epic</th><th>做什么</th><th>验收标准</th><th>负责人</th><th>Status</th></tr></thead><tbody>';
      items.forEach(function(r) {
        var stCls = r.status==='In Progress'||r.status==='In Review'?'dev':r.status==='Todo'?'todo':'plan';
        h += '<tr><td class="m1-scope"><a class="card-id" href="https://linear.app/donutbrowser/issue/' + r.epic + '" target="_blank">' + r.epic + '</a></td>';
        h += '<td class="m1-feature">' + r.name + '<br><span style="font-size:0.68rem;color:var(--fg-subtle)">' + r.desc + '</span></td>';
        h += '<td class="m1-acceptance">' + r.accept + '</td>';
        h += '<td class="m1-owner">' + r.owner + '</td>';
        h += '<td><span class="m1-status ' + stCls + '">' + r.status + '</span></td></tr>';
      });
      h += '</tbody></table></div></div>';
      return h;
    }

    tableHTML += makeTable(v1P0, 'P0');
    tableHTML += makeTable(v1P1, 'P1');

    // Progress summary for v1
    var allV1 = v1P0.concat(v1P1);
    var inProgress = allV1.filter(function(r){return r.status==='In Progress'||r.status==='In Review'}).length;
    var todo = allV1.filter(function(r){return r.status==='Todo'}).length;
    var planning = allV1.filter(function(r){return r.status==='Planning'}).length;
    var pct = Math.round((inProgress/allV1.length)*100);

    var summaryHTML = '<div style="display:flex;gap:var(--space-3);margin-bottom:var(--space-6)">'
      + '<div style="text-align:center;padding:var(--space-2) var(--space-4);background:rgba(245,158,11,.08);border:1px solid rgba(245,158,11,.2);border-radius:var(--radius-sm)"><div style="font-family:var(--font-mono);font-size:1.2rem;font-weight:700;color:var(--warning)">' + inProgress + '</div><div style="font-size:0.6rem;color:var(--fg-subtle)">开发/Review</div></div>'
      + '<div style="text-align:center;padding:var(--space-2) var(--space-4);background:rgba(113,113,122,.08);border:1px solid rgba(113,113,122,.2);border-radius:var(--radius-sm)"><div style="font-family:var(--font-mono);font-size:1.2rem;font-weight:700;color:var(--fg-subtle)">' + todo + '</div><div style="font-size:0.6rem;color:var(--fg-subtle)">Todo</div></div>'
      + '<div style="text-align:center;padding:var(--space-2) var(--space-4);background:rgba(59,130,246,.08);border:1px solid rgba(59,130,246,.2);border-radius:var(--radius-sm)"><div style="font-family:var(--font-mono);font-size:1.2rem;font-weight:700;color:var(--info)">' + planning + '</div><div style="font-size:0.6rem;color:var(--fg-subtle)">规划中</div></div>'
      + '<div style="text-align:center;padding:var(--space-2) var(--space-4);background:var(--bg-subtle);border:1px solid var(--border-base);border-radius:var(--radius-sm)"><div style="font-family:var(--font-mono);font-size:1.2rem;font-weight:700">' + pct + '%</div><div style="font-size:0.6rem;color:var(--fg-subtle)">已启动</div></div></div>';

    m1El.innerHTML = summaryHTML + tableHTML;
  }

  // v2-v4 Roadmap Cards
  const roadmapEl = document.getElementById('milestoneRoadmap');
  if (roadmapEl) {
    roadmapEl.innerHTML = '<div class="ms-card m2">'
      + '<h3>v2「想得明」— 个性化 + 知识体系</h3>'
      + '<div class="ms-dates">版本制 · 功能通过验收即上线</div>'
      + '<div class="ms-core"><strong style="font-size:0.72rem;color:var(--fg-muted)">P0 Core:</strong>'
      + '<ul style="margin:var(--space-1) 0;padding-left:var(--space-4)">'
      + '<li><a class="card-id" href="https://linear.app/donutbrowser/issue/PRODUCT-2209" target="_blank">PRODUCT-2209</a> 用户画像 + 30天行为推断风险偏好</li>'
      + '<li><a class="card-id" href="https://linear.app/donutbrowser/issue/PRODUCT-1872" target="_blank">PRODUCT-1872</a> 知识体系 Phase 1-2 — 数据采集 + 知识注入</li>'
      + '<li><a class="card-id" href="https://linear.app/donutbrowser/issue/PRODUCT-2211" target="_blank">PRODUCT-2211</a> 评测体系 — Eval Harness + Skill 质量</li>'
      + '<li><a class="card-id" href="https://linear.app/donutbrowser/issue/PRODUCT-2198" target="_blank">PRODUCT-2198</a> Dashboard 功能深化</li>'
      + '</ul></div>'
      + '<div class="ms-ns">🎯 验收: 不同用户收到不同建议 · Eval 覆盖 ≥ 10 Skill · 知识检索命中 ≥ 50%</div>'
      + '<div class="ms-effort">P0: 4 Epics · P1: 7 Epics</div>'
      + '</div>'

      + '<div class="ms-card m3">'
      + '<h3>v3「做得住」— 自动执行 + 风控闭环</h3>'
      + '<div class="ms-dates">版本制 · 功能通过验收即上线</div>'
      + '<div class="ms-core"><strong style="font-size:0.72rem;color:var(--fg-muted)">P0 Core:</strong>'
      + '<ul style="margin:var(--space-1) 0;padding-left:var(--space-4)">'
      + '<li><a class="card-id" href="https://linear.app/donutbrowser/issue/PRODUCT-2199" target="_blank">PRODUCT-2199</a> 限额 Guard + 熔断 + 大额审批</li>'
      + '<li><a class="card-id" href="https://linear.app/donutbrowser/issue/PRODUCT-2017" target="_blank">PRODUCT-2017</a> D0 Bot ↔ GRPS 全链路集成</li>'
      + '<li><a class="card-id" href="https://linear.app/donutbrowser/issue/PRODUCT-1958" target="_blank">PRODUCT-1958</a> 复合下单 + 幂等 + AI 合约策略</li>'
      + '<li><a class="card-id" href="https://linear.app/donutbrowser/issue/PRODUCT-1872" target="_blank">PRODUCT-1872</a> 知识体系 Phase 3-4 — 分析框架 + 闭环</li>'
      + '</ul></div>'
      + '<div class="ms-ns">🎯 验收: 超限被拦截 · 每笔过 GRPS 校验 · 复合下单成功率 ≥ 95%</div>'
      + '<div class="ms-effort">P0: 4 Epics · P1: 4 Epics</div>'
      + '</div>'

      + '<div class="ms-card m4">'
      + '<h3>v4「越来越好」— 质量闭环 + 增长 + 自我进化</h3>'
      + '<div class="ms-dates">版本制 · 功能通过验收即上线</div>'
      + '<div class="ms-core"><strong style="font-size:0.72rem;color:var(--fg-muted)">P0 Core:</strong>'
      + '<ul style="margin:var(--space-1) 0;padding-left:var(--space-4)">'
      + '<li><a class="card-id" href="https://linear.app/donutbrowser/issue/PRODUCT-1830" target="_blank">PRODUCT-1830</a> 质量漏斗 / 看板 / 告警</li>'
      + '<li><a class="card-id" href="https://linear.app/donutbrowser/issue/PRODUCT-1576" target="_blank">PRODUCT-1576</a> 用户反馈自动进入迭代</li>'
      + '<li><a class="card-id" href="https://linear.app/donutbrowser/issue/PRODUCT-1591" target="_blank">PRODUCT-1591</a> 执行可回溯 — 完整决策链</li>'
      + '</ul></div>'
      + '<div class="ms-ns">🎯 验收: 质量异常自动告警 · 反馈→issue ≤ 72h · 决策链完整可查</div>'
      + '<div class="ms-effort">P0: 3 Epics · P1: 5 Epics · P2: 2 Epics</div>'
      + '</div>';
  }

  // Milestone section header update
  const syncEl = document.getElementById('weeklySyncAgenda');
  if (syncEl) {
    syncEl.innerHTML = '<div class="sync-box">'
      + '<span class="sync-title">📖 v3 版本制说明</span>'
      + '<span class="sync-sep">━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━</span>'
      + '<span class="sync-section">版本不绑日历。</span>'
      + '<span class="sync-detail">每个 Epic 通过验收标准 = 该功能上线</span>'
      + '<span class="sync-detail">版本内所有 P0 验收通过 = 该版本达成</span>'
      + '<span class="sync-sep">━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━</span>'
      + '<span class="sync-section">北极星指标: 7 日交易用户留存率</span>'
      + '<span class="sync-sep">━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━</span>'
      + '<span class="sync-section">Cycle Planning 怎么用:</span>'
      + '<span class="sync-detail">1. PM 从当前版本 P0/P1 选取本 cycle 要推的 Epic</span>'
      + '<span class="sync-detail">2. 每个 Epic 拆成 cycle issue，带验收标准</span>'
      + '<span class="sync-detail">3. 版本无关的大块工作 → Strategic Matrix 检查</span>'
      + '<span class="sync-detail">4. 两个维度都不符合 → 单独拎出来讨论</span>'
      + '<span class="sync-sep">━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━</span>'
      + '<span class="sync-section">人员速查: 看 v3 原文</span>'
      + '<span class="sync-detail">→ <a class="card-id" href="https://linear.app/donutbrowser/issue/PRODUCT-2167/milestone-d0-里程碑规划-核心护城河与-4-阶段产品路线图#comment-f80d90c8" target="_blank">PRODUCT-2167 v3 comment</a></span>'
      + '</div>';
  }
}

"""

html = html[:ms_start_idx] + new_milestone + html[ms_end_idx:]

# ═══════════════════════════════════════════════════════════
# 4. Update milestone tab header
# ═══════════════════════════════════════════════════════════
html = html.replace(
    'M1 执行看板 + M2-M4 路线图 + 周二 Sync 议程 · v9.0',
    'v3 版本制 — v1 看得清 · v2 想得明 · v3 做得住 · v4 越来越好'
)

# Update milestone tab panel header
html = html.replace(
    '<h2>🗓 Milestone Planning — 里程碑规划</h2>',
    '<h2>🗓 Milestone — 版本制规划 (v3)</h2>'
)

# Update M1 header in tab panel
html = html.replace(
    '<div style="font-family:var(--font-display);font-size:1.6rem;font-weight:400;margin-bottom:var(--space-2);color:var(--fg-base)">M1: Foundation Sprint</div>',
    '<div style="font-family:var(--font-display);font-size:1.6rem;font-weight:400;margin-bottom:var(--space-2);color:var(--fg-base)">v1「看得清」— 核心流程跑通</div>'
)
html = html.replace(
    '<div style="font-family:var(--font-mono);font-size:0.68rem;color:var(--fg-subtle);margin-bottom:var(--space-4)">3/16 → 4/15 · 30 days · 18 deliverables across 9 scopes</div>',
    '<div style="font-family:var(--font-mono);font-size:0.68rem;color:var(--fg-subtle);margin-bottom:var(--space-4)">版本制 · P0 全部验收通过 = v1 达成 · 9 P0 + 7 P1 Epics</div>'
)

# Update M2-M4 header
html = html.replace(
    '<div style="font-family:var(--font-display);font-size:1.3rem;font-weight:400;margin-bottom:var(--space-4)">M2 → M4 Roadmap</div>',
    '<div style="font-family:var(--font-display);font-size:1.3rem;font-weight:400;margin-bottom:var(--space-4)">v2 → v4 路线图</div>'
)

# Update Weekly Sync header
html = html.replace(
    '<div style="font-family:var(--font-display);font-size:1.3rem;font-weight:400;margin-bottom:var(--space-4)">📅 周二 Milestone Sync Template</div>',
    '<div style="font-family:var(--font-display);font-size:1.3rem;font-weight:400;margin-bottom:var(--space-4)">📖 版本制使用说明</div>'
)

# ═══════════════════════════════════════════════════════════
# 5. Version bump
# ═══════════════════════════════════════════════════════════
html = html.replace(
    'D0 Product Dashboard v10.0',
    'D0 Product Dashboard v10.1'
)
html = html.replace(
    'v10.0 · 2026-03-23',
    'v10.1 · 2026-03-23'
)

# ═══════════════════════════════════════════════════════════
# Write
# ═══════════════════════════════════════════════════════════
with open('/tmp/kanban-repo/index.html', 'w') as f:
    f.write(html)

print(f"✅ Updated /tmp/kanban-repo/index.html ({len(html):,} chars)")

# Validation
checks = [
    ('CEO 成本估算', '成本估算' in html),
    ('CEO 商业化+支付', '商业化 + 支付闭环' in html),
    ('CEO 预置策略', '预置的交易策略' in html),
    ('CEO 安全+风控', '安全 + 风控' in html),
    ('CEO Agent主动性', 'Agent 的主动性' in html),
    ('5 CEO areas', html.count("title: '") >= 5),  # at least 5 focus areas
    ('v1 看得清', '看得清' in html),
    ('v2 想得明', '想得明' in html),
    ('v3 做得住', '做得住' in html),
    ('v4 越来越好', '越来越好' in html),
    ('v10.1', 'v10.1' in html),
    ('renderMilestone exists', 'renderMilestone' in html),
    ('renderCEOFocus exists', 'renderCEOFocus' in html),
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
