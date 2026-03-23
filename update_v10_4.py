#!/usr/bin/env python3
"""
v10.4 — 5 fixes from Chris:
1. Page padding (matrix/milestone overflow)
2. Risk → Sprint Board (filterable by person)
3. Product panorama readability
4. v2/v3/v4 progress bars + status like v1
5. v1-v4 labels on top of capability matrix
"""

with open('/tmp/kanban-repo/index.html', 'r') as f:
    html = f.read()

# ═══════════════════════════════════════════════════════════
# 1. FIX PADDING — matrix and tables overflow on narrow screens
# ═══════════════════════════════════════════════════════════
# The .page has max-width:1280px and padding, but the matrix-grid 
# and tables inside tabs can overflow. Add overflow-x:auto wrapper.
# Also ensure tab-panel has proper padding.
css_fix = '''
/* ══ v10.4 Layout Fixes ═══════════════════════════════ */
.tab-panel { padding: 0 var(--space-2) }
.matrix-wrap { overflow-x: auto; -webkit-overflow-scrolling: touch; padding-bottom: var(--space-2) }
.m1-table { margin: 0 }
.ms-card { margin-bottom: var(--space-4) }
#milestoneRoadmap { grid-template-columns: 1fr !important }
'''
html = html.replace('/* ── Reset ─', css_fix + '/* ── Reset ─')

# ═══════════════════════════════════════════════════════════
# 2. RISK → SPRINT BOARD (remove risk tab, move content)
# ═══════════════════════════════════════════════════════════

# 2a. Remove risk tab button
html = html.replace(
    "    <button class=\"tab-btn\" onclick=\"switchTab('risk')\">⚠️ 风险</button>\n",
    ""
)

# 2b. Extract risk content to inject into Sprint Board
# Find risk tab content
risk_tab_start = html.index('<div id="tab-risk" class="tab-panel">')
risk_tab_end_marker = '\n\n  <!-- ═'
risk_tab_end = html.index(risk_tab_end_marker, risk_tab_start)
risk_tab_close = html.rfind('</div>', risk_tab_start, risk_tab_end)

# Extract just the risk grid (without the tab wrapper and section header)
risk_content_start = html.index('<div style="background:rgba(34,197,94,.06)', risk_tab_start)
risk_content_end = html.index('</div>\n  </div>', risk_content_start) + len('</div>')
risk_content = html[risk_content_start:risk_content_end]

# 2c. Remove the entire risk tab
risk_tab_full = html[risk_tab_start:risk_tab_end]
html = html.replace(risk_tab_full, '')

# 2d. Inject risks at top of Sprint Board, in a collapsible section
risk_sprint_html = f'''
    <!-- ══ Sprint Risks (v10.4: moved from risk tab) ══ -->
    <div id="sprintRiskSection" style="margin-bottom:var(--space-6)">
      <div style="display:flex;align-items:center;justify-content:space-between;cursor:pointer;padding:var(--space-3) 0;border-bottom:1px solid var(--border-base);margin-bottom:var(--space-3)" onclick="var el=document.getElementById('riskContent');el.style.display=el.style.display==='none'?'block':'none';this.querySelector('.risk-toggle').textContent=el.style.display==='none'?'▸':'▾'">
        <div style="display:flex;align-items:center;gap:var(--space-2)">
          <span style="font-size:1.1rem">⚠️</span>
          <span style="font-family:var(--font-display);font-size:1.2rem;font-weight:400">Sprint 风险</span>
          <span style="font-family:var(--font-mono);font-size:0.62rem;color:var(--fg-subtle)">8 items</span>
        </div>
        <span class="risk-toggle" style="font-family:var(--font-mono);font-size:0.82rem;color:var(--fg-subtle)">▾</span>
      </div>
      <div id="riskContent">
        {risk_content}
      </div>
    </div>
'''

# Insert after the cycle selector in Sprint Board
cycle_selector_end = '<div id="sprintGrid"></div>'
html = html.replace(cycle_selector_end, risk_sprint_html + '\n    ' + cycle_selector_end)

# ═══════════════════════════════════════════════════════════
# 3. PRODUCT PANORAMA — improve readability
# ═══════════════════════════════════════════════════════════
# The panorama is rendered by renderProductPanorama(). 
# Update the rendering to use a card grid instead of plain list.
# Find and replace the panorama render function
old_panorama_render_start = 'function renderProductPanorama()'
old_panorama_render_end = 'function renderRepoCatalog()'
pano_start = html.index(old_panorama_render_start)
pano_end = html.index(old_panorama_render_end)

new_panorama_render = '''function renderProductPanorama() {
  var el = document.getElementById('panoGrid');
  if (!el) return;
  el.innerHTML = PANORAMA_DATA.map(function(scope) {
    var moduleCards = scope.modules.map(function(m) {
      return '<div style="background:var(--bg-muted);border-radius:var(--radius-sm);padding:var(--space-2) var(--space-3);margin-bottom:var(--space-1)">'
        + '<div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:2px">'
        + '<span style="font-family:var(--font-mono);font-size:0.62rem;color:var(--fg-subtle)">' + m.name.split(':')[0] + '</span>'
        + '<span style="font-family:var(--font-mono);font-size:0.58rem;color:var(--fg-subtle)">' + m.owner + '</span></div>'
        + '<div style="font-size:0.76rem;font-weight:500;line-height:1.3">' + (m.name.split(': ')[1]||m.name) + '</div>'
        + '<div style="font-size:0.65rem;color:var(--fg-muted);margin-top:2px">' + m.desc + '</div>'
        + '</div>';
    }).join('');

    return '<div style="background:var(--bg-subtle);border:1px solid var(--border-base);border-radius:var(--radius-lg);padding:var(--space-4);margin-bottom:var(--space-4)">'
      + '<div style="display:flex;align-items:center;gap:var(--space-2);margin-bottom:var(--space-3)">'
      + '<span style="font-size:1.1rem">' + scope.icon + '</span>'
      + '<span style="font-family:var(--font-display);font-size:1.1rem;font-weight:400">' + scope.name + '</span>'
      + '<span style="font-family:var(--font-mono);font-size:0.6rem;color:var(--fg-subtle)">' + scope.modules.length + ' modules</span>'
      + '</div>'
      + '<div style="display:grid;grid-template-columns:repeat(auto-fill,minmax(320px,1fr));gap:var(--space-2)">' + moduleCards + '</div>'
      + '</div>';
  }).join('');
}

'''

html = html[:pano_start] + new_panorama_render + html[pano_end:]

# ═══════════════════════════════════════════════════════════
# 4. v2/v3/v4 PROGRESS BARS — update renderMilestone
#    Each version gets progress summary like v1
# ═══════════════════════════════════════════════════════════
# The renderMilestone function already exists. We need to update
# the roadmap section to show progress bars for v2/v3/v4.
# Replace the versionCard function to include progressSummary.

# Find the roadmap rendering section in renderMilestone
old_roadmap_section = "roadmapEl.style.gridTemplateColumns = '1fr';"
if old_roadmap_section in html:
    # Already set to 1fr, good. Now update the versionCard function
    # to include progress summary. The function is defined inside renderMilestone.
    
    # Replace the versionCard function to include progress
    old_version_card = "function versionCard(ver, subtitle, matrixCoord, ns, gate, p0, p1, p2) {"
    vc_start = html.index(old_version_card)
    vc_end = html.index("roadmapEl.style", vc_start)
    
    new_version_card = """function versionCard(ver, subtitle, matrixCoord, ns, gate, p0, p1, p2) {
      var cls = ver==='v2'?'m2':ver==='v3'?'m3':'m4';
      var allItems = p0.concat(p1).concat(p2||[]);
      var ip = allItems.filter(function(r){return r.status==='In Progress'||r.status==='In Review'}).length;
      var td = allItems.filter(function(r){return r.status==='Todo'}).length;
      var pl = allItems.filter(function(r){return r.status==='Planning'}).length;
      var dn = allItems.filter(function(r){return r.status==='Done'}).length;
      var total = allItems.length;
      var startedPct = total>0?Math.round(((ip+dn)/total)*100):0;
      
      var h = '<div class="ms-card '+cls+'" style="margin-bottom:var(--space-6)">';
      h += '<h3>'+ver+'「'+subtitle+'」</h3>';
      h += '<div class="ms-dates">矩阵: '+matrixCoord+' · 版本制，验收即上线</div>';
      h += '<div class="ms-ns">🎯 '+ns+'</div>';
      h += '<div style="background:rgba(34,197,94,.06);border:1px solid rgba(34,197,94,.15);border-radius:var(--radius-sm);padding:var(--space-2) var(--space-3);margin-bottom:var(--space-3);font-family:var(--font-mono);font-size:0.65rem;color:var(--success)">✅ 版本门槛: '+gate+'</div>';
      
      // Progress summary
      h += '<div style="display:flex;gap:var(--space-3);margin-bottom:var(--space-4);flex-wrap:wrap">';
      h += '<div style="text-align:center;padding:var(--space-2) var(--space-4);background:rgba(245,158,11,.08);border:1px solid rgba(245,158,11,.2);border-radius:var(--radius-sm)"><div style="font-family:var(--font-mono);font-size:1.1rem;font-weight:700;color:var(--warning)">'+ip+'</div><div style="font-size:0.58rem;color:var(--fg-subtle)">开发/Review</div></div>';
      h += '<div style="text-align:center;padding:var(--space-2) var(--space-4);background:rgba(113,113,122,.08);border:1px solid rgba(113,113,122,.2);border-radius:var(--radius-sm)"><div style="font-family:var(--font-mono);font-size:1.1rem;font-weight:700;color:var(--fg-subtle)">'+td+'</div><div style="font-size:0.58rem;color:var(--fg-subtle)">Todo</div></div>';
      h += '<div style="text-align:center;padding:var(--space-2) var(--space-4);background:rgba(59,130,246,.08);border:1px solid rgba(59,130,246,.2);border-radius:var(--radius-sm)"><div style="font-family:var(--font-mono);font-size:1.1rem;font-weight:700;color:var(--info)">'+pl+'</div><div style="font-size:0.58rem;color:var(--fg-subtle)">规划中</div></div>';
      h += '<div style="text-align:center;padding:var(--space-2) var(--space-4);background:var(--bg-subtle);border:1px solid var(--border-base);border-radius:var(--radius-sm)"><div style="font-family:var(--font-mono);font-size:1.1rem;font-weight:700">'+startedPct+'%</div><div style="font-size:0.58rem;color:var(--fg-subtle)">已启动</div></div>';
      h += '</div>';

      function epicList(items, label) {
        if (!items || !items.length) return '';
        var lh = '<div style="margin-bottom:var(--space-3)"><div style="font-family:var(--font-mono);font-size:0.6rem;font-weight:600;color:'+(label==='P0'?'var(--error)':'label'==='P1'?'var(--warning)':'var(--info)')+';margin-bottom:var(--space-1)">'+label+' ('+items.length+' Epics)</div>';
        lh += '<div style="overflow-x:auto"><table class="m1-table"><thead><tr><th>Epic</th><th>做什么</th><th>验收标准</th><th>负责人</th><th>Status</th></tr></thead><tbody>';
        items.forEach(function(r) {
          var stCls = (r.status==='In Progress'||r.status==='In Review')?'dev':r.status==='Todo'?'todo':'plan';
          lh += '<tr><td class="m1-scope"><a class="card-id" href="https://linear.app/donutbrowser/issue/'+r.epic+'" target="_blank">'+r.epic+'</a></td>';
          lh += '<td class="m1-feature">'+r.name+'<br><span style="font-size:0.68rem;color:var(--fg-subtle)">'+r.desc+'</span></td>';
          lh += '<td class="m1-acceptance">'+r.accept+'</td>';
          lh += '<td class="m1-owner">'+r.owner+'</td>';
          lh += '<td><span class="m1-status '+stCls+'">'+r.status+'</span></td></tr>';
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

    """
    
    html = html[:vc_start] + new_version_card + html[vc_end:]

# Fix the JS syntax error in epicList color logic
html = html.replace(
    "+(label==='P0'?'var(--error)':'label'==='P1'?'var(--warning)':'var(--info)')+",
    "+(label==='P0'?'var(--error)':label==='P1'?'var(--warning)':'var(--info)')+",
)

# ═══════════════════════════════════════════════════════════
# 5. v1-v4 LABELS ON TOP OF MATRIX
# ═══════════════════════════════════════════════════════════
# Add a version timeline strip above the matrix grid
version_strip = '''
      <!-- Version ↔ Matrix mapping strip (v10.4) -->
      <div style="display:grid;grid-template-columns:80px repeat(5, 1fr);gap:2px;margin-bottom:var(--space-2);font-family:var(--font-mono);font-size:0.6rem">
        <div></div>
        <div style="text-align:center;padding:var(--space-1) var(--space-2);background:rgba(34,197,94,.12);border-radius:var(--radius-sm);color:var(--success);font-weight:600">← v1「看得清」→</div>
        <div style="text-align:center;padding:var(--space-1) var(--space-2);background:rgba(59,130,246,.12);border-radius:var(--radius-sm);color:var(--info);font-weight:600">← v2「想得明」→</div>
        <div style="text-align:center;padding:var(--space-1) var(--space-2);background:rgba(245,158,11,.12);border-radius:var(--radius-sm);color:var(--warning);font-weight:600">← v3「做得住」→</div>
        <div style="text-align:center;padding:var(--space-1) var(--space-2);background:rgba(167,139,250,.12);border-radius:var(--radius-sm);color:#a78bfa;font-weight:600" colspan="2">← v4「越来越好」→</div>
      </div>

'''

# Insert before the matrix-grid
html = html.replace(
    '<div class="matrix-grid">',
    version_strip + '      <div class="matrix-grid">'
)

# ═══════════════════════════════════════════════════════════
# 6. Version bump
# ═══════════════════════════════════════════════════════════
html = html.replace('v10.3 · 2026-03-23', 'v10.4 · 2026-03-23')
html = html.replace('D0 Product Dashboard v10.3', 'D0 Product Dashboard v10.4')

# ═══════════════════════════════════════════════════════════
# Write
# ═══════════════════════════════════════════════════════════
with open('/tmp/kanban-repo/index.html', 'w') as f:
    f.write(html)

print(f"✅ Updated to v10.4 ({len(html):,} chars)")

# Validation
checks = [
    ('No risk tab button', "switchTab('risk')" not in html),
    ('Risk in Sprint Board', 'sprintRiskSection' in html),
    ('v2/v3/v4 progress', 'startedPct' in html),
    ('Version strip on matrix', '看得清' in html and 'matrix-grid' in html),
    ('Panorama card grid', 'grid-template-columns:repeat(auto-fill' in html),
    ('Tab padding CSS', '.tab-panel { padding' in html),
    ('v10.4', 'v10.4' in html),
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
