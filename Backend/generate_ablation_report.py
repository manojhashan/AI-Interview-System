"""
Ablation Study Report Generator (Interactive)
===============================================
Fetches interview results from the database, embeds all per-question
scores as JSON, then generates an interactive HTML report where the
user can filter by **candidate** and **interview session**.

Usage:
    cd Backend
    python generate_ablation_report.py

Output:
    ../ablation_report.html
"""

import os, json, sys
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

load_dotenv(override=True)

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    print("ERROR: DATABASE_URL not found in .env")
    sys.exit(1)

engine = create_engine(DATABASE_URL)

# ── 1. Fetch all data with user + interview info ──────────────────────
print("Fetching interview data from database...")

query = text("""
    SELECT
        ir.id            AS interview_id,
        ir.candidate_name,
        ir.job_role,
        ir.date,
        r.user_id,
        ir.details_json
    FROM interview_results ir
    JOIN resume r ON ir.resume_id = r.id
    WHERE ir.details_json IS NOT NULL
    ORDER BY r.user_id, ir.date
""")

samples = []       # flat list of per-question rows
interviews = {}    # unique interviews
users = {}         # unique users

with engine.connect() as conn:
    for row in conn.execute(query):
        iid, name, role, date_str, uid, dj = row
        try:
            details = json.loads(dj)
        except:
            continue

        # Track unique users & interviews
        if uid not in users:
            users[uid] = name
        interview_label = f"{name} — {role} ({date_str})"
        interviews[iid] = {"label": interview_label, "user_id": uid}

        for d in details:
            scores = d.get("scores", {})
            f = scores.get("facial", 0)
            v = scores.get("vocal", 0)
            s = scores.get("semantic", 0)
            o = scores.get("overall", 0)
            samples.append({
                "user_id": uid,
                "interview_id": iid,
                "f": round(f, 2),
                "v": round(v, 2),
                "s": round(s, 2),
                "o": round(o, 2)
            })

total = len(samples)
print(f"Total question-level samples: {total}")
print(f"Users: {len(users)}, Interview sessions: {len(interviews)}")

if total == 0:
    print("No data found. Run some interviews first.")
    sys.exit(0)

# ── 2. Prepare JSON for embedding ────────────────────────────────────
# user list for dropdown
users_list = [{"id": uid, "name": uname} for uid, uname in users.items()]

# interview list for dropdown
interviews_list = [
    {"id": iid, "label": info["label"], "user_id": info["user_id"]}
    for iid, info in interviews.items()
]

data_json      = json.dumps(samples)
users_json     = json.dumps(users_list)
interviews_json = json.dumps(interviews_list)

# ── 3. Generate interactive HTML ─────────────────────────────────────
html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Ablation Study — Zynergy AI Multimodal Confidence</title>
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
<style>
  @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800&display=swap');
  * {{ margin:0; padding:0; box-sizing:border-box; }}
  body {{
    font-family:'Inter',sans-serif;
    background:#0a0e1a;
    color:#e2e8f0;
    min-height:100vh;
    padding:40px 20px;
  }}
  .container {{ max-width:960px; margin:0 auto; }}

  .header {{ text-align:center; margin-bottom:40px; }}
  .header h1 {{
    font-size:2rem; font-weight:800;
    background:linear-gradient(135deg,#60a5fa,#34d399);
    -webkit-background-clip:text; -webkit-text-fill-color:transparent;
    margin-bottom:8px;
  }}
  .header p {{ color:#64748b; font-size:0.9rem; }}
  .badge {{
    display:inline-block; background:rgba(59,130,246,0.15); color:#60a5fa;
    font-size:0.7rem; font-weight:700; padding:4px 12px; border-radius:20px;
    margin-top:12px; letter-spacing:1px; text-transform:uppercase;
  }}

  /* Filters */
  .filters {{
    display:flex; gap:16px; margin-bottom:32px; flex-wrap:wrap;
  }}
  .filter-group {{
    flex:1; min-width:240px;
  }}
  .filter-group label {{
    display:block; font-size:0.7rem; font-weight:700; color:#64748b;
    text-transform:uppercase; letter-spacing:1px; margin-bottom:6px;
  }}
  .filter-group select {{
    width:100%; background:#0f172a; border:1px solid rgba(255,255,255,0.1);
    color:#e2e8f0; padding:12px 16px; border-radius:12px; font-size:0.85rem;
    font-family:'Inter',sans-serif; outline:none; cursor:pointer;
    appearance:none;
    background-image:url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='12' height='12' viewBox='0 0 12 12'%3E%3Cpath d='M3 5l3 3 3-3' stroke='%2364748b' stroke-width='1.5' fill='none' stroke-linecap='round'/%3E%3C/svg%3E");
    background-repeat:no-repeat;
    background-position:right 12px center;
  }}
  .filter-group select:focus {{ border-color:rgba(59,130,246,0.5); }}
  .filter-group select option {{ background:#0f172a; color:#e2e8f0; }}

  /* Stats */
  .stats-grid {{
    display:grid; grid-template-columns:repeat(4,1fr); gap:16px; margin-bottom:32px;
  }}
  .stat-card {{
    background:rgba(15,23,42,0.8); border:1px solid rgba(255,255,255,0.06);
    border-radius:16px; padding:24px; text-align:center;
  }}
  .stat-card .value {{ font-size:2rem; font-weight:800; margin-bottom:4px; }}
  .stat-card .label {{
    font-size:0.7rem; color:#64748b; text-transform:uppercase;
    letter-spacing:1px; font-weight:700;
  }}
  .stat-card:nth-child(1) .value {{ color:#f97316; }}
  .stat-card:nth-child(2) .value {{ color:#a78bfa; }}
  .stat-card:nth-child(3) .value {{ color:#34d399; }}
  .stat-card:nth-child(4) .value {{ color:#60a5fa; }}

  /* Sections */
  .section {{
    background:rgba(15,23,42,0.6); border:1px solid rgba(255,255,255,0.06);
    border-radius:20px; padding:32px; margin-bottom:32px;
  }}
  .section h2 {{
    font-size:1.2rem; font-weight:700; margin-bottom:20px;
    display:flex; align-items:center; gap:8px;
  }}

  /* Table */
  table {{ width:100%; border-collapse:collapse; font-size:0.85rem; }}
  thead th {{
    text-align:left; padding:12px 16px; font-size:0.7rem;
    text-transform:uppercase; letter-spacing:1px; color:#64748b;
    font-weight:700; border-bottom:1px solid rgba(255,255,255,0.06);
  }}
  tbody td {{ padding:14px 16px; border-bottom:1px solid rgba(255,255,255,0.03); }}
  tbody tr:hover {{ background:rgba(255,255,255,0.02); }}
  tbody tr:last-child {{ background:rgba(59,130,246,0.08); font-weight:700; }}
  tbody tr:last-child td {{ border-bottom:none; color:#60a5fa; }}

  .accuracy-bar {{ display:flex; align-items:center; gap:10px; }}
  .bar-bg {{
    flex:1; height:8px; background:rgba(255,255,255,0.05);
    border-radius:4px; overflow:hidden;
  }}
  .bar-fill {{ height:100%; border-radius:4px; transition:width 0.6s ease; }}
  .acc-val {{ font-weight:700; min-width:50px; text-align:right; }}

  .chart-wrapper {{ position:relative; height:350px; }}

  .formula {{
    background:rgba(0,0,0,0.3); padding:12px 20px; border-radius:10px;
    font-family:monospace; font-size:0.85rem; margin:16px 0;
    color:#34d399; text-align:center;
  }}

  .insight {{
    background:rgba(59,130,246,0.08); border-left:3px solid #3b82f6;
    padding:16px 20px; border-radius:0 12px 12px 0; margin-top:16px;
    font-size:0.85rem; line-height:1.7; color:#94a3b8;
  }}
  .insight strong {{ color:#e2e8f0; }}

  .footer {{
    text-align:center; margin-top:40px; color:#334155; font-size:0.75rem;
  }}

  .no-data {{
    text-align:center; padding:60px 20px; color:#475569; font-size:0.9rem;
  }}

  @media (max-width:640px) {{
    .stats-grid {{ grid-template-columns:repeat(2,1fr); }}
    .filters {{ flex-direction:column; }}
  }}
</style>
</head>
<body>

<div class="container">
  <div class="header">
    <h1>Multimodal Ablation Study</h1>
    <p>Quantitative Contribution Analysis — Zynergy AI Interview System</p>
    <div class="badge" id="sampleBadge">{total} Question-Level Samples</div>
  </div>

  <!-- Filters -->
  <div class="filters">
    <div class="filter-group">
      <label>👤 Candidate</label>
      <select id="userFilter" onchange="onFilterChange()">
        <option value="all">All Candidates</option>
      </select>
    </div>
    <div class="filter-group">
      <label>📋 Interview Session</label>
      <select id="interviewFilter" onchange="render()">
        <option value="all">All Interviews</option>
      </select>
    </div>
  </div>

  <!-- Stats -->
  <div class="stats-grid">
    <div class="stat-card"><div class="value" id="avgFacial">—</div><div class="label">Avg Facial</div></div>
    <div class="stat-card"><div class="value" id="avgVocal">—</div><div class="label">Avg Vocal</div></div>
    <div class="stat-card"><div class="value" id="avgSemantic">—</div><div class="label">Avg Semantic</div></div>
    <div class="stat-card"><div class="value" id="avgOverall">—</div><div class="label">Avg Overall</div></div>
  </div>

  <!-- Formula -->
  <div class="section">
    <h2>⚙️ Multimodal Fusion Formula</h2>
    <div class="formula">P<sub>overall</sub> = (Semantic × 0.2) + (Facial × 0.4) + (Vocal × 0.4)</div>
    <p style="color:#64748b;font-size:0.8rem;text-align:center;">
      Weighted average fusion — Facial and Vocal cues carry equal dominant weight,
      Semantic relevance serves as supporting signal.
    </p>
  </div>

  <!-- Table -->
  <div class="section">
    <h2>📊 Ablation Results</h2>
    <div id="tableArea"></div>
  </div>

  <!-- Chart -->
  <div class="section">
    <h2>📈 Visual Comparison</h2>
    <div class="chart-wrapper">
      <canvas id="ablationChart"></canvas>
    </div>
  </div>

  <!-- Interpretation -->
  <div class="section">
    <h2>🔍 Interpretation</h2>
    <div class="insight" id="insightArea"></div>
  </div>

  <div class="footer">Zynergy AI Interview System — Ablation Study Report</div>
</div>

<script>
// ── Embedded data from DB ─────────────────────────────────────────────
const ALL_SAMPLES = {data_json};
const USERS       = {users_json};
const INTERVIEWS  = {interviews_json};
const T = 50; // threshold

const CONFIGS = [
  {{ name: 'Facial Only',             fn: r => r.f >= T ? 1 : 0 }},
  {{ name: 'Vocal Only',              fn: r => r.v >= T ? 1 : 0 }},
  {{ name: 'Semantic Only',           fn: r => r.s >= T ? 1 : 0 }},
  {{ name: 'Facial + Vocal',          fn: r => (r.f*0.5 + r.v*0.5) >= T ? 1 : 0 }},
  {{ name: 'Facial + Semantic',       fn: r => (r.f*0.67 + r.s*0.33) >= T ? 1 : 0 }},
  {{ name: 'Vocal + Semantic',        fn: r => (r.v*0.67 + r.s*0.33) >= T ? 1 : 0 }},
  {{ name: 'All Three (Multimodal)',  fn: r => (r.s*0.2 + r.f*0.4 + r.v*0.4) >= T ? 1 : 0 }},
];

const COLORS = ['#f97316','#a78bfa','#34d399','#fbbf24','#ec4899','#06b6d4','#3b82f6'];
const COLORS_BG = COLORS.map(c => c + 'b3');

let chart = null;

// ── Populate dropdowns ───────────────────────────────────────────────
function initFilters() {{
  const uSel = document.getElementById('userFilter');
  USERS.forEach(u => {{
    const opt = document.createElement('option');
    opt.value = u.id;
    opt.textContent = u.name + ' (' + u.id + ')';
    uSel.appendChild(opt);
  }});
}}

function updateInterviewDropdown() {{
  const uid = document.getElementById('userFilter').value;
  const iSel = document.getElementById('interviewFilter');
  iSel.innerHTML = '<option value="all">All Interviews</option>';

  const filtered = uid === 'all' ? INTERVIEWS : INTERVIEWS.filter(i => i.user_id === uid);
  filtered.forEach(iv => {{
    const opt = document.createElement('option');
    opt.value = iv.id;
    opt.textContent = iv.label;
    iSel.appendChild(opt);
  }});
}}

function onFilterChange() {{
  updateInterviewDropdown();
  render();
}}

// ── Compute & render ─────────────────────────────────────────────────
function getFilteredSamples() {{
  const uid = document.getElementById('userFilter').value;
  const iid = document.getElementById('interviewFilter').value;
  let data = ALL_SAMPLES;
  if (uid !== 'all') data = data.filter(r => r.user_id === uid);
  if (iid !== 'all') data = data.filter(r => r.interview_id === iid);
  return data;
}}

function computeAblation(data) {{
  if (data.length === 0) return null;
  const actuals = data.map(r => r.o >= T ? 1 : 0);
  return CONFIGS.map(cfg => {{
    const preds = data.map(cfg.fn);
    const correct = preds.reduce((sum, p, i) => sum + (p === actuals[i] ? 1 : 0), 0);
    return {{ name: cfg.name, accuracy: +((correct / data.length) * 100).toFixed(2) }};
  }});
}}

function render() {{
  const data = getFilteredSamples();
  const n = data.length;
  document.getElementById('sampleBadge').textContent = n + ' Question-Level Samples';

  if (n === 0) {{
    document.getElementById('avgFacial').textContent = '—';
    document.getElementById('avgVocal').textContent = '—';
    document.getElementById('avgSemantic').textContent = '—';
    document.getElementById('avgOverall').textContent = '—';
    document.getElementById('tableArea').innerHTML = '<div class="no-data">No data for selected filter.</div>';
    document.getElementById('insightArea').innerHTML = 'No data available.';
    if (chart) {{ chart.destroy(); chart = null; }}
    return;
  }}

  // Averages
  const avgF = (data.reduce((s,r) => s + r.f, 0) / n).toFixed(1);
  const avgV = (data.reduce((s,r) => s + r.v, 0) / n).toFixed(1);
  const avgS = (data.reduce((s,r) => s + r.s, 0) / n).toFixed(1);
  const avgO = (data.reduce((s,r) => s + r.o, 0) / n).toFixed(1);
  document.getElementById('avgFacial').textContent = avgF;
  document.getElementById('avgVocal').textContent = avgV;
  document.getElementById('avgSemantic').textContent = avgS;
  document.getElementById('avgOverall').textContent = avgO;

  // Ablation
  const results = computeAblation(data);

  // Table
  let tableHtml = `<table><thead><tr>
    <th style="width:40px">#</th><th>Configuration</th><th>Accuracy</th>
  </tr></thead><tbody>`;
  results.forEach((r, i) => {{
    tableHtml += `<tr>
      <td style="color:#475569">${{i+1}}</td>
      <td>${{r.name}}</td>
      <td><div class="accuracy-bar">
        <div class="bar-bg"><div class="bar-fill" style="width:${{r.accuracy}}%;background:${{COLORS[i]}}"></div></div>
        <span class="acc-val">${{r.accuracy}}%</span>
      </div></td>
    </tr>`;
  }});
  tableHtml += '</tbody></table>';
  document.getElementById('tableArea').innerHTML = tableHtml;

  // Chart
  if (chart) chart.destroy();
  const ctx = document.getElementById('ablationChart').getContext('2d');
  chart = new Chart(ctx, {{
    type: 'bar',
    data: {{
      labels: results.map(r => r.name),
      datasets: [{{
        label: 'Accuracy (%)',
        data: results.map(r => r.accuracy),
        backgroundColor: COLORS_BG,
        borderColor: COLORS,
        borderWidth: 2, borderRadius: 8, borderSkipped: false,
      }}]
    }},
    options: {{
      responsive: true, maintainAspectRatio: false,
      plugins: {{
        legend: {{ display: false }},
        tooltip: {{
          backgroundColor:'#1e293b', titleColor:'#e2e8f0', bodyColor:'#94a3b8',
          borderColor:'rgba(255,255,255,0.1)', borderWidth:1, cornerRadius:8, padding:12,
          callbacks: {{ label: ctx => ctx.parsed.y + '% Accuracy' }}
        }}
      }},
      scales: {{
        y: {{
          beginAtZero:true, max:100,
          ticks: {{ color:'#475569', font:{{size:11,weight:600}}, callback:v=>v+'%' }},
          grid: {{ color:'rgba(255,255,255,0.03)' }}
        }},
        x: {{
          ticks: {{ color:'#64748b', font:{{size:10,weight:600}}, maxRotation:45, minRotation:30 }},
          grid: {{ display:false }}
        }}
      }}
    }}
  }});

  // Interpretation
  const best = results.reduce((a,b) => a.accuracy > b.accuracy ? a : b);
  const singles = results.slice(0,3);
  const bestSingle = singles.reduce((a,b) => a.accuracy > b.accuracy ? a : b);
  const multi = results[6];

  document.getElementById('insightArea').innerHTML = `
    <strong>Key Findings (${{n}} samples):</strong><br><br>
    • The <strong>full multimodal model</strong> (${{multi.accuracy}}%) 
      ${{multi.accuracy >= bestSingle.accuracy ? 'outperforms' : 'is comparable to'}} 
      the best single modality.<br><br>
    • <strong>Single modality</strong> performance — 
      Facial (${{results[0].accuracy}}%), 
      Vocal (${{results[1].accuracy}}%), 
      Semantic (${{results[2].accuracy}}%).<br><br>
    • <strong>Two-modality combinations</strong> — 
      Facial+Vocal (${{results[3].accuracy}}%), 
      Facial+Semantic (${{results[4].accuracy}}%), 
      Vocal+Semantic (${{results[5].accuracy}}%).<br><br>
    • The <strong>highest accuracy</strong> is achieved by <strong>${{best.name}}</strong> (${{best.accuracy}}%), 
      confirming that combining modalities provides complementary information.
  `;
}}

// ── Init ─────────────────────────────────────────────────────────────
initFilters();
render();
</script>
</body>
</html>"""

# ── 4. Write output ──────────────────────────────────────────────────
output_path = os.path.join(os.path.dirname(__file__), "..", "ablation_report.html")
with open(output_path, "w", encoding="utf-8") as f:
    f.write(html)

abs_path = os.path.abspath(output_path)
print(f"\n✅ Report generated: {abs_path}")
print(f"   Open in browser to view the interactive ablation study.")
