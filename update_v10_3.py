#!/usr/bin/env python3
"""
Update D0 Product Kanban v10.3:
1. Delete 五层架构 Q2 规划 + Challenge 决议 from risk tab
2. Merge Milestone + Strategic Matrix into one tab (matrix on top, v1-v4 below)
"""

with open('/tmp/kanban-repo/index.html', 'r') as f:
    html = f.read()

# ═══════════════════════════════════════════════════════════
# 1. DELETE 五层架构 + Challenge 决议 from risk tab
#    Keep only the 风险消解 content, remove everything after it
# ═══════════════════════════════════════════════════════════

# Find where the risk grid ends and 五层架构 begins
marker_start = '    <div class="sec"><div class="sec-head"><span class="sec-num">05</span><h2>五层架构 Q2 规划</h2></div></div>'
marker_end = '    <div class="pending-box" contenteditable>待决:'

# Find the end of pending box through to closing </div> of tab-risk
pending_start = html.index(marker_start)
# Find the </div> that closes tab-risk after the pending box
pending_box_end = html.index('</div>\n\n  <!-- ═', pending_start)

# Remove everything from 五层架构 to end of challenge section (keep the tab-risk closing </div>)
# The content between marker_start and the closing </div> of tab-risk needs to go
section_to_remove = html[pending_start:pending_box_end]
html = html.replace(section_to_remove, '')

print(f"  Removed 五层架构 + Challenge 决议 ({len(section_to_remove)} chars)")

# ═══════════════════════════════════════════════════════════
# 2. MERGE Milestone + Strategic Matrix into ONE tab
#    Matrix on top, then v1 v2 v3 v4 below
# ═══════════════════════════════════════════════════════════

# Step 2a: Remove separate milestone and matrix tab buttons, add combined one
html = html.replace(
    "    <button class=\"tab-btn\" onclick=\"switchTab('milestone')\">🗓 Milestone</button>\n    <button class=\"tab-btn\" onclick=\"switchTab('matrix')\">🎯 Strategic Matrix</button>",
    "    <button class=\"tab-btn\" onclick=\"switchTab('roadmap')\">🗺 Roadmap</button>"
)

# Step 2b: Extract the strategic matrix content (between tab-matrix open and close)
matrix_tab_start = html.index('<div id="tab-matrix" class="tab-panel">')
matrix_tab_inner_start = html.index('\n', matrix_tab_start) + 1
# Find the closing </div> for tab-matrix
# The matrix tab ends before the footer
matrix_tab_end = html.index('  <div class="footer">')
# Actually need to find the exact end of tab-matrix
# Look for the closing </div> that matches tab-matrix
# tab-matrix content ends with </div>\n\n  before footer
import re
# Find all the content between <div id="tab-matrix"...> and its closing </div>
# The matrix has: opening div, then content, then </div> before footer

# Let's find the matrix content more carefully
matrix_content_start = html.index('<div class="sec"><div class="sec-head"><span class="sec-num">09</span>', matrix_tab_start)
# Find the end - it's the </div> that closes tab-matrix, right before footer
footer_pos = html.index('\n  <div class="footer">')
# Go back to find the </div> closing tab-matrix
tab_matrix_close = html.rfind('</div>', matrix_tab_start, footer_pos)
# The content we want is from the sec header to just before the tab close
matrix_inner = html[matrix_content_start:tab_matrix_close]

# Step 2c: Extract milestone content
milestone_tab_start = html.index('<div id="tab-milestone" class="tab-panel">')
milestone_tab_end = html.index('<div id="tab-matrix" class="tab-panel">')
milestone_inner_start = html.index('<div class="sec"><div class="sec-head"><span class="sec-num">08</span>', milestone_tab_start)
milestone_inner_end = milestone_tab_end - len('\n\n  ')
# Get milestone inner content
milestone_close = html.rfind('</div>', milestone_tab_start, milestone_tab_end)
milestone_inner = html[milestone_inner_start:milestone_close]

# Step 2d: Build the combined tab
combined_tab = f'''<div id="tab-roadmap" class="tab-panel">
    <!-- Strategic Matrix (top) -->
    {matrix_inner}

    <!-- Separator -->
    <div style="margin:var(--space-8) 0;border-top:2px solid var(--border-emphasis)"></div>

    <!-- Milestone Versions (below) -->
    {milestone_inner}
  </div>'''

# Step 2e: Replace both old tabs with the combined one
old_milestone_to_matrix_end = html[milestone_tab_start:tab_matrix_close + len('</div>')]
html = html.replace(old_milestone_to_matrix_end, combined_tab)

# Step 2f: Update switchTab JS to handle 'roadmap'
# The switchTab function just shows/hides tabs by id, so 'roadmap' will work automatically
# But we also need to update renderMilestone trigger
html = html.replace(
    "if (tab==='ceo') renderCEOFocus();\n  if (tab==='milestone') renderMilestone();",
    "if (tab==='ceo') renderCEOFocus();\n  if (tab==='roadmap') { renderMilestone(); }"
)

# Also handle the old milestone/matrix tab triggers (in case they exist elsewhere)
html = html.replace(
    "if (tab==='milestone') renderMilestone();",
    "if (tab==='roadmap') renderMilestone();"
)

# ═══════════════════════════════════════════════════════════
# 3. Update section numbers and labels
# ═══════════════════════════════════════════════════════════
# Renumber the milestone section
html = html.replace(
    '<span class="sec-num">08</span><h2>🗓 Milestone — 版本制规划 (v3)</h2>',
    '<span class="sec-num">08</span><h2>🗓 版本制规划 (v3)</h2>'
)

# Update hint
html = html.replace(
    'v3 版本制 — v1 看得清 · v2 想得明 · v3 做得住 · v4 越来越好',
    '版本不绑日历 · Epic 验收即上线 · 全 P0 通过 = 版本达成'
)

# ═══════════════════════════════════════════════════════════
# 4. Clean up risk tab — rename since 五层架构 and Challenge are gone
# ═══════════════════════════════════════════════════════════
html = html.replace(
    "<button class=\"tab-btn\" onclick=\"switchTab('risk')\">⚠️ 风险 &amp; 规划</button>",
    "<button class=\"tab-btn\" onclick=\"switchTab('risk')\">⚠️ 风险</button>"
)

# ═══════════════════════════════════════════════════════════
# 5. Version bump
# ═══════════════════════════════════════════════════════════
html = html.replace('v10.2 · 2026-03-23', 'v10.3 · 2026-03-23')
html = html.replace('D0 Product Dashboard v10.2', 'D0 Product Dashboard v10.3')

# ═══════════════════════════════════════════════════════════
# Write
# ═══════════════════════════════════════════════════════════
with open('/tmp/kanban-repo/index.html', 'w') as f:
    f.write(html)

print(f"✅ Updated to v10.3 ({len(html):,} chars)")

# Validation
checks = [
    ('No 五层架构', '五层架构' not in html),
    ('No Challenge 决议', 'Challenge 决议' not in html),
    ('No pending-box', 'pending-box' not in html),
    ('Combined roadmap tab', 'tab-roadmap' in html),
    ('Roadmap button', "switchTab('roadmap')" in html),
    ('No separate milestone tab', 'tab-milestone' not in html),
    ('No separate matrix tab', 'tab-matrix' not in html),
    ('Matrix content preserved', 'Proactive × High-Stake' in html),
    ('Milestone content preserved', 'm1ExecutionSheet' in html),
    ('Risk tab simplified', '⚠️ 风险</button>' in html),
    ('v10.3', 'v10.3' in html),
    ('renderMilestone on roadmap', "tab==='roadmap'" in html),
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
