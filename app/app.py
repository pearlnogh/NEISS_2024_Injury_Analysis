# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
import numpy as np
import pickle
import json
import requests
from pathlib import Path

st.set_page_config(
    page_title="ED Admission Risk Predictor",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ─────────────────────────────────────────
# CSS
# ─────────────────────────────────────────
st.markdown("""
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700&family=Source+Sans+3:wght@400;500;600&display=swap" rel="stylesheet">
<style>
:root {
    --navy:#0A1F44; --navy-mid:#1B3A6B; --navy-lt:#2A5298;
    --red:#B22234; --red-lt:#CC3344;
    --gold:#C8A951; --gold-lt:#E8C96A;
    --muted:#6B7A99; --border:rgba(10,31,68,0.11);
}
html,body,[class*="css"]{ font-family:'Source Sans 3',sans-serif; }
.stApp{ background:linear-gradient(150deg,#EEF2FA 0%,#F5F0E8 55%,#EAE8F0 100%); }
.block-container{ padding:1.5rem 2rem 3rem !important; max-width:1300px; }
[data-testid="stSidebar"]{ display:none; }

.app-header{
    background:linear-gradient(135deg,var(--navy) 0%,var(--navy-mid) 65%,var(--navy-lt) 100%);
    border-radius:14px; padding:1.6rem 2rem; margin-bottom:1.4rem;
    border-left:5px solid var(--gold); position:relative; overflow:hidden;
}
.app-header::before{
    content:'★  ★  ★  ★  ★'; position:absolute; top:12px; right:1.8rem;
    font-size:11px; color:rgba(200,169,81,0.45); letter-spacing:8px;
}
.app-header::after{
    content:''; position:absolute; bottom:0; left:0; right:0; height:4px;
    background:repeating-linear-gradient(90deg,var(--red) 0,var(--red) 18px,#fff 18px,#fff 24px);
}
.app-header h1{ font-family:'Playfair Display',serif !important; color:#fff !important; font-size:1.75rem !important; margin:0 0 .2rem !important; }
.app-header p{ color:rgba(200,210,235,.82) !important; font-size:13px !important; margin:0 !important; }
.badge-edu{
    display:inline-block; margin-top:.5rem;
    background:rgba(178,34,52,.28); border:1px solid rgba(200,169,81,.4);
    color:var(--gold-lt) !important; font-size:10.5px; padding:3px 11px;
    border-radius:20px; letter-spacing:.06em; font-weight:600; text-transform:uppercase;
}
.stats-strip{ display:grid; grid-template-columns:repeat(4,1fr); gap:10px; margin-bottom:1.2rem; }
.stat-card{ background:#fff; border:0.5px solid var(--border); border-radius:10px; padding:.75rem 1rem; text-align:center; }
.stat-num{ font-family:'Playfair Display',serif; font-size:1.5rem; color:var(--navy); line-height:1.1; }
.stat-lbl{ font-size:10px; color:var(--muted); text-transform:uppercase; letter-spacing:.07em; margin-top:2px; }
.sec-head{
    font-family:'Playfair Display',serif; font-size:1rem; color:var(--navy);
    border-bottom:2px solid var(--gold); padding-bottom:5px; margin-bottom:.9rem; display:inline-block;
}
.step-label{
    font-size:10px; font-weight:600; letter-spacing:.1em; text-transform:uppercase;
    color:var(--gold); background:var(--navy); display:inline-block;
    padding:3px 10px; border-radius:10px; margin-bottom:.6rem;
}
/* ── All buttons: base ── */
div[data-testid="stButton"] > button {
    border-radius: 8px !important; font-size: 15px !important; font-weight: 600 !important;
    padding: .65rem 1.5rem !important; width: 100% !important; letter-spacing: .03em;
    transition: background .18s, box-shadow .18s !important;
    background: #2C5AA0 !important; color: #fff !important; border: none !important;
    box-shadow: 0 2px 8px rgba(44,90,160,0.18) !important;
}
div[data-testid="stButton"] > button:hover {
    background: #1B3A6B !important;
    box-shadow: 0 4px 14px rgba(44,90,160,0.28) !important;
}
/* ── Secondary: Apply description signal (key=ai_btn) ── */
div[data-testid="stButton"]:has(button[data-testid="baseButton-secondary"]) > button,
button[kind="secondaryFormSubmit"],
div[data-testid="column"]:first-child div[data-testid="stButton"] > button {
    background: #EAF2FF !important; color: #2C5AA0 !important;
    border: 1.5px solid #B5D4F4 !important; box-shadow: none !important; font-weight: 500 !important;
}
div[data-testid="column"]:first-child div[data-testid="stButton"] > button:hover {
    background: #D6E8FF !important; color: #1B3A6B !important;
}
/* ── Ghost: Clear button — second column ── */
div[data-testid="column"]:last-child div[data-testid="stButton"] > button {
    background: transparent !important; color: #7A869A !important;
    border: 1.5px solid #D0D7E2 !important; box-shadow: none !important; font-weight: 500 !important;
}
div[data-testid="column"]:last-child div[data-testid="stButton"] > button:hover {
    background: #F3F4F6 !important; color: #4A5568 !important;
}
.result-card{ border-radius:12px; padding:1.4rem 1.3rem; }
.rc-high  { background:linear-gradient(135deg,#fff1f0,#ffe4e4); border:1.5px solid #ffb3b3; }
.rc-medium{ background:linear-gradient(135deg,#fffbe6,#fff3cc); border:1.5px solid #ffd666; }
.rc-low   { background:linear-gradient(135deg,#f0faf2,#e6f7ea); border:1.5px solid #95de9a; }
.rc-idle  { background:#f8f9fc; border:1.5px dashed var(--border); text-align:center; padding:2.5rem 1.5rem; }
.result-label{ font-size:11px; font-weight:600; letter-spacing:.08em; text-transform:uppercase; margin:0 0 .2rem; }
.result-prob { font-family:'Playfair Display',serif; font-size:3.8rem; font-weight:700; line-height:1; margin:.15rem 0; }
.prob-h{ color:var(--red); } .prob-m{ color:#B87A00; } .prob-l{ color:#1A7A3C; }
.result-desc{ font-size:12px; color:#666; margin:.35rem 0 0; }
.gauge-track{ height:9px; background:#e8e8e8; border-radius:9px; margin:.9rem 0 .25rem; overflow:hidden; }
.gauge-fill { height:100%; border-radius:9px; }
.gf-high  { background:linear-gradient(90deg,#ff9a9a,var(--red)); }
.gf-medium{ background:linear-gradient(90deg,#ffd666,#f0a000); }
.gf-low   { background:linear-gradient(90deg,#95de9a,#2a9d4e); }
.gauge-lbl{ display:flex; justify-content:space-between; font-size:9.5px; color:#bbb; }
.flags-wrap{ display:flex; flex-wrap:wrap; gap:6px; margin-top:.5rem; }
.flag-pill{
    display:inline-flex; align-items:center; gap:5px;
    background:#FFF8E8; border:1px solid #E8C96A; color:#7A5400;
    border-radius:20px; padding:4px 12px; font-size:12px; font-weight:500;
}
.flag-dot{ width:6px; height:6px; border-radius:50%; background:var(--gold); flex-shrink:0; }
.ai-flag-pill{
    display:inline-flex; align-items:center; gap:5px;
    background:#f0f4ff; border:1px solid #b5d4f4; color:#0C447C;
    border-radius:20px; padding:4px 12px; font-size:12px; font-weight:500;
}
.ai-dot{ width:6px; height:6px; border-radius:50%; background:#378ADD; flex-shrink:0; }
.whatif-card{ background:#F5F0E8; border:0.5px solid #E8C96A; border-radius:10px; padding:.9rem 1.1rem; margin-top:.8rem; }
.whatif-title{ font-size:10px; font-weight:600; text-transform:uppercase; letter-spacing:.08em; color:#7A5400; margin-bottom:.6rem; }
.whatif-row{ display:flex; justify-content:space-between; align-items:center; font-size:12.5px; color:#555; margin-bottom:.4rem; }
.delta-pill{ font-size:11px; padding:2px 9px; border-radius:10px; font-weight:500; }
.delta-down{ background:#e6f7ea; color:#1A7A3C; }
.delta-up  { background:#fff1f0; color:var(--red); }
.ctx-bar{ background:#E6F1FB; border-left:3px solid #185FA5; border-radius:0 7px 7px 0; padding:6px 10px; font-size:12px; color:#0C447C; margin-bottom:6px; }
.info-card{ background:#fff; border:0.5px solid var(--border); border-radius:10px; padding:.9rem 1.1rem; margin-bottom:.75rem; border-left:4px solid var(--navy-lt); }
.info-title{ font-size:10.5px; font-weight:600; text-transform:uppercase; letter-spacing:.07em; color:var(--navy); margin-bottom:4px; }
.info-body { font-size:12.5px; color:#444; line-height:1.55; }
[data-testid="stTabs"] [role="tab"]{ font-size:13px !important; font-weight:500 !important; }
.perf-table{ width:100%; border-collapse:collapse; font-size:13px; }
.perf-table th{ background:#0A1F44; color:#fff; padding:8px 12px; text-align:left; font-weight:500; }
.perf-table td{ padding:8px 12px; border-bottom:0.5px solid var(--border); }
.perf-table tr:last-child td{ border-bottom:none; }
.perf-table tr.best td{ background:#F5F0E8; font-weight:600; }
.perf-badge{ display:inline-block; padding:2px 8px; border-radius:8px; font-size:11px; }
.pb-green{ background:#e6f7ea; color:#1A7A3C; }
.pb-amber{ background:#fff8e1; color:#7A5400; }
.pb-red  { background:#fff1f0; color:var(--red); }
.bar-chart{ margin:.5rem 0; }
.bar-row{ display:flex; align-items:center; gap:8px; margin-bottom:5px; }
.bar-label{ font-size:11.5px; color:#444; min-width:120px; text-align:right; }
.bar-track{ flex:1; height:18px; background:#f0f0f0; border-radius:4px; overflow:hidden; }
.bar-fill { height:100%; border-radius:4px; display:flex; align-items:center; padding-left:6px; font-size:10.5px; color:#fff; font-weight:600; }
.bar-val  { font-size:11.5px; color:var(--navy); font-weight:500; min-width:38px; }
.hist-card{
    background:#fff; border:0.5px solid var(--border); border-radius:10px;
    padding:.75rem 1rem; margin-bottom:.6rem; display:flex;
    align-items:center; justify-content:space-between;
}
.hist-prob{ font-family:'Playfair Display',serif; font-size:1.3rem; font-weight:700; }
.hist-details{ font-size:11.5px; color:var(--muted); }
.demo-btn-row{ display:flex; gap:8px; flex-wrap:wrap; margin-bottom:.8rem; }
.ai-banner{
    background:linear-gradient(90deg,#042C53,#0C447C);
    border-radius:10px; padding:.75rem 1.1rem; margin-bottom:.8rem;
    display:flex; align-items:center; gap:10px;
}
.ai-banner-text{ color:#E6F1FB; font-size:12.5px; line-height:1.5; }
.cm-grid{ display:grid; grid-template-columns:1fr 1fr; gap:8px; max-width:360px; }
.cm-cell{ border-radius:8px; padding:1rem; text-align:center; }
.cm-tp{ background:#e6f7ea; border:1px solid #95de9a; }
.cm-fp{ background:#fff8e1; border:1px solid #ffd666; }
.cm-fn{ background:#fff1f0; border:1px solid #ffb3b3; }
.cm-tn{ background:#f0f4ff; border:1px solid #b5d4f4; }
.cm-num{ font-family:'Playfair Display',serif; font-size:1.6rem; font-weight:700; }
.cm-lbl{ font-size:10.5px; font-weight:600; text-transform:uppercase; letter-spacing:.07em; margin-top:3px; }
.cm-desc{ font-size:11px; color:#666; margin-top:4px; line-height:1.4; }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────
# Constants
# ─────────────────────────────────────────
AGE_GROUPS = [
    'infant (<1)','toddler (1-4)','child (5-12)','adolescent (13-17)',
    'young adult (18-34)','mid adult (35-49)','older adult (50-64)','elderly (65+)'
]
DIAGNOSES = sorted([
    'amputation','anoxia','aspiration','avulsion',
    'burns, chemical','burns, electrical','burns, not specified','burns, radiation',
    'burns, scald','burns, thermal','concussions','contusions, abrasions','crushing',
    'dental injury','dermatitis, conjunctivitis','dislocation','electric shock',
    'foreign body','fracture','hematoma','hemorrhage','ingestion',
    'internal organ injury','laceration','nerve damage','other/not stated',
    'poisoning','puncture','strain, sprain','submersion'
])
BODY_PARTS = sorted([
    '25-50% of body','all parts body','ankle','ear','elbow','eyeball','face',
    'finger','foot','hand','head','internal','knee','lower arm','lower leg',
    'lower trunk','mouth','neck','pubic region','shoulder','toe',
    'upper arm','upper leg','upper trunk','wrist'
])
LOCATIONS = sorted([
    'farm/ranch','home','industrial','mobile/manufactured home',
    'other public property','place of recreation or sports',
    'school/daycare','street or highway','unknown'
])
FIRE_DISPLAY = [
    'No fire involved',
    'Fire involved — fire department responded',
    'Fire involved — fire department did NOT respond',
    'Fire involved — fire department response unknown',
]
FIRE_MODEL   = ['no_fire_or_not_recorded','fire_fd_attended','fire_fd_not_attended','fire_fd_unknown']
FIRE_MAP     = dict(zip(FIRE_DISPLAY, FIRE_MODEL))

POPULATION_RATES = {
    'overall': 0.084,
    'age': {'infant (<1)':0.09,'toddler (1-4)':0.05,'child (5-12)':0.05,
            'adolescent (13-17)':0.06,'young adult (18-34)':0.07,
            'mid adult (35-49)':0.09,'older adult (50-64)':0.13,'elderly (65+)':0.28},
    'diagnosis': {'fracture':0.32,'submersion':0.45,'internal organ injury':0.38,
                  'anoxia':0.42,'amputation':0.35,'crushing':0.22,'hemorrhage':0.25,
                  'strain, sprain':0.03,'contusions, abrasions':0.04,
                  'laceration':0.05,'other/not stated':0.07}
}
WHATIF_AGE = {
    'elderly (65+)':('mid adult (35-49)',-0.18),
    'older adult (50-64)':('young adult (18-34)',-0.10),
    'mid adult (35-49)':('young adult (18-34)',-0.05),
    'young adult (18-34)':('child (5-12)',-0.03),
    'child (5-12)':('young adult (18-34)',+0.02),
    'adolescent (13-17)':('young adult (18-34)',-0.01),
    'toddler (1-4)':('young adult (18-34)',-0.02),
    'infant (<1)':('young adult (18-34)',+0.01),
}
WHATIF_DX = {
    'fracture':('strain, sprain',-0.29),
    'submersion':('laceration',-0.40),
    'internal organ injury':('contusions, abrasions',-0.34),
    'anoxia':('laceration',-0.38),
    'laceration':('strain, sprain',-0.02),
    'strain, sprain':('laceration',+0.02),
    'contusions, abrasions':('laceration',+0.01),
    'concussions':('strain, sprain',-0.08),
    'other/not stated':('strain, sprain',-0.04),
}

# ─────────────────────────────────────────
# AI: reads narrative and extracts form fields
# ─────────────────────────────────────────
def ai_extract_from_narrative(text: str) -> dict:
    """
    The AI reads the free-text narrative and returns:
    1. Suggested structured field values (age_group, diagnosis, body_part, location,
       fire_display, alcohol, drug, is_weekend) — these AUTO-FILL the model's inputs.
    2. Additional risk signals found in the text that the structured fields can't capture.
    3. A plain-English clinical summary.
    4. Red flags.
    5. Suggested clinical checks.
    This means the AI is DIRECTLY feeding the model, not running alongside it.
    """
    age_opts   = str(AGE_GROUPS)
    dx_opts    = str(DIAGNOSES)
    bp_opts    = str(BODY_PARTS)
    loc_opts   = str(LOCATIONS)
    fire_opts  = str(FIRE_DISPLAY)

    system_prompt = f"""You are a clinical triage assistant for an emergency department admission risk tool.
Your job is to read a free-text incident description and extract structured fields that will be fed
directly into a logistic regression model trained on 361,672 NEISS emergency department cases.

You must return ONLY valid JSON — no markdown, no backticks, no extra text.

Available options for each field:
- age_group: {age_opts}
- diagnosis: {dx_opts}
- body_part: {bp_opts}
- location: {loc_opts}
- fire_display: {fire_opts}

Schema:
{{
  "suggested_fields": {{
    "age_group": "<best matching option from age_group list, or null if unclear>",
    "diagnosis": "<best matching option from diagnosis list, or null if unclear>",
    "body_part": "<best matching option from body_part list, or null if unclear>",
    "location": "<best matching option from location list, or null if unclear>",
    "fire_display": "<best matching option from fire_display list>",
    "alcohol": <true or false>,
    "drug": <true or false>,
    "is_weekend": <true, false, or null if not mentioned>
  }},
  "extra_risk_signals": [<list of important risk details from the text that the structured fields above cannot capture, e.g. "loss of consciousness reported", "difficulty breathing mentioned">],
  "red_flags": [<list of urgent clinical concerns that strongly suggest hospital admission>],
  "ai_summary": "<2-3 sentence plain-English summary of why this case does or does not appear high-risk for admission>",
  "suggested_checks": [<list of recommended clinical assessments based on the description>],
  "confidence": "<High|Medium|Low — how confident you are in the extracted fields>"
}}

Rules:
- Only suggest field values that are genuinely supported by the text.
- Use null for fields you cannot determine — never guess.
- Plain English only. No jargon.
- Never invent facts not in the text."""

    try:
        response = requests.post(
            "https://api.anthropic.com/v1/messages",
            headers={"Content-Type": "application/json"},
            json={
                "model": "claude-sonnet-4-20250514",
                "max_tokens": 900,
                "system": system_prompt,
                "messages": [{"role": "user", "content": f"Incident description:\n{text}"}]
            },
            timeout=25
        )
        raw = response.json()["content"][0]["text"].strip()
        raw = raw.replace("```json","").replace("```","").strip()
        return json.loads(raw)
    except Exception as e:
        return {
            "suggested_fields": {},
            "extra_risk_signals": [],
            "red_flags": [],
            "ai_summary": f"AI analysis unavailable ({str(e)}). The model will use the manually entered fields above.",
            "suggested_checks": [],
            "confidence": "Low"
        }

# ─────────────────────────────────────────
# Load model
# ─────────────────────────────────────────
@st.cache_resource
def load_model():
    try:
        base = Path(__file__).parent.parent / "models"
        m  = pickle.load(open(base / "model_iteration.pkl","rb"))
        mc = pickle.load(open(base / "model_columns.pkl","rb"))
        return m, mc, None
    except FileNotFoundError as e:
        return None, None, str(e)

model, model_columns, load_error = load_model()

def predict_prob(age_group, sex, diagnosis, body_part, location,
                 fire, is_weekend, alcohol, drug, narrative_len):
    row = {
        "age_group":age_group, "sex":sex.lower(),
        "diagnosis":diagnosis, "body_part":body_part,
        "location":location, "fire_involvement":fire,
        "is_weekend":int(is_weekend), "alcohol_flag":int(alcohol),
        "drug_flag":int(drug), "narrative_len":narrative_len,
        "age_x_diagnosis":age_group+"_"+diagnosis
    }
    df = pd.get_dummies(pd.DataFrame([row]))
    df = df.reindex(columns=model_columns, fill_value=0)
    raw_prob = float(model.predict_proba(df)[0][1])
    return raw_prob

def risk_meta(prob):
    if prob > 0.7:
        return "rc-high","prob-h","gf-high","🔴 HIGH RISK","Immediate clinical attention recommended"
    elif prob > 0.5:
        return "rc-medium","prob-m","gf-medium","🟠 MODERATE RISK","Monitor closely — consider further evaluation"
    else:
        return "rc-low","prob-l","gf-low","🟢 LOW RISK","Standard care pathway appropriate"

# ─────────────────────────────────────────
# Session state
# ─────────────────────────────────────────
if "history" not in st.session_state:
    st.session_state.history = []
if "ai_result" not in st.session_state:
    st.session_state.ai_result = None
if "ai_ran" not in st.session_state:
    st.session_state.ai_ran = False
# Form field defaults (can be overwritten by AI or demo buttons)
for k,v in [("s_age",4),("s_sex",0),("s_dx",DIAGNOSES.index("fracture")),
            ("s_bp",BODY_PARTS.index("head")),("s_loc",LOCATIONS.index("home")),
            ("s_fire",0),("s_weekend",False),("s_alcohol",False),("s_drug",False),
            ("s_narrative","")]:
    if k not in st.session_state:
        st.session_state[k] = v

# ─────────────────────────────────────────
# Header
# ─────────────────────────────────────────
st.markdown("""
<div class="app-header">
  <h1>🏥 ED Admission Risk Predictor</h1>
  <p>National Electronic Injury Surveillance System · 2024 · United States of America</p>
  <span class="badge-edu">⚠ Educational Use Only — Not a Clinical Decision Tool</span>
</div>
""", unsafe_allow_html=True)

if load_error:
    st.error(f"**Model files not found:** {load_error}\n\nMake sure `model_iteration.pkl` and `model_columns.pkl` are in the `models/` folder.")
    st.stop()



# ─────────────────────────────────────────
# Tabs
# ─────────────────────────────────────────
tab_predict, tab_model, tab_insights, tab_about = st.tabs([
    "🔍 Predict", "📊 Model Performance", "📈 Data Insights", "ℹ️ About"
])

# ══════════════════════════════════════════
# TAB 1 — PREDICT
# ══════════════════════════════════════════
with tab_predict:
    left_col, right_col = st.columns([1.1, 0.9], gap="large")

    with left_col:

        # ── Step 1 ──
        st.markdown('<div class="step-label">Step 1 — Demographics</div>', unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        with c1:
            age_group = st.selectbox("Age Group", AGE_GROUPS, index=st.session_state.s_age, key="age_group_sel")
        with c2:
            sex = st.radio("Sex", ["Male","Female"], index=st.session_state.s_sex, horizontal=True, key="sex_sel")

        st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

        # ── Step 2 ──
        st.markdown('<div class="step-label">Step 2 — Injury Details</div>', unsafe_allow_html=True)
        c1, c2, c3 = st.columns(3)
        with c1:
            diagnosis = st.selectbox("Primary Diagnosis", DIAGNOSES, index=st.session_state.s_dx, key="dx_sel")
        with c2:
            body_part = st.selectbox("Body Part Affected", BODY_PARTS, index=st.session_state.s_bp, key="bp_sel")
        with c3:
            location  = st.selectbox("Injury Location", LOCATIONS, index=st.session_state.s_loc, key="loc_sel")

        st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

        # ── Step 3 ──
        st.markdown('<div class="step-label">Step 3 — Contextual Factors</div>', unsafe_allow_html=True)
        c1, c2, c3 = st.columns(3)
        with c1:
            fire_display = st.selectbox("Was there a fire?", FIRE_DISPLAY, index=st.session_state.s_fire, key="fire_sel")
            fire = FIRE_MAP[fire_display]
        with c2:
            is_weekend = st.checkbox("Weekend visit",  value=st.session_state.s_weekend, key="wknd_sel")
            alcohol    = st.checkbox("Alcohol involved", value=st.session_state.s_alcohol, key="alc_sel")
        with c3:
            drug = st.checkbox("Drug involvement", value=st.session_state.s_drug, key="drug_sel")

        st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

        # ── Step 4 — AI narrative (properly integrated) ──
        st.markdown('<div class="step-label">Step 4 — Narrative detail matters</div>', unsafe_allow_html=True)
        st.markdown("""
        <div class="ai-banner">
          <span style="font-size:20px;">🤖</span>
          <div class="ai-banner-text">
            Describe what happened in a few sentences. More detailed descriptions increase narrative complexity, which is used by the model.
          </div>
        </div>
        """, unsafe_allow_html=True)

        narrative_text = st.text_area(
            "What happened? (optional)",
            value=st.session_state.s_narrative,
            placeholder='e.g. "75-year-old woman fell down stairs at home, hitting her head. She briefly lost consciousness and is now confused and cannot stand up."',
            height=95,
            key="narr_sel",
            help="The AI reads this and suggests the best matching values for age group, diagnosis, body part, location, and contextual factors — which then feed directly into the prediction model."
        )
        # Always read from the live session_state widget key — this is the actual current value
        _raw_len = len(st.session_state.get("narr_sel", narrative_text))
        narrative_len = max(20, min(500, _raw_len)) if st.session_state.get("narr_sel", "").strip() else 100

        # Narrative Complexity display
        st.markdown("<div style='height:4px'></div>", unsafe_allow_html=True)
        st.markdown('<p style="font-size:10px;font-weight:600;letter-spacing:.1em;text-transform:uppercase;color:var(--muted);margin-bottom:2px;">NARRATIVE COMPLEXITY</p>', unsafe_allow_html=True)
        _pct = int((narrative_len - 20) / (500 - 20) * 100)
        _len_label = f"Short report ({narrative_len} chars)" if narrative_len < 80 else (f"Moderate report ({narrative_len} chars)" if narrative_len < 200 else f"Detailed report ({narrative_len} chars)")
        st.markdown(f'''
        <div style="font-size:12px;color:#444;margin-bottom:3px;">
          Report Length &nbsp;<span style="font-weight:600;color:var(--navy-lt);">{narrative_len}</span>
        </div>
        <div style="background:#e8e8e8;border-radius:6px;height:7px;overflow:hidden;margin-bottom:3px;">
          <div style="width:{_pct}%;background:linear-gradient(90deg,#2A5298,#1B3A6B);height:100%;border-radius:6px;"></div>
        </div>
        <div style="font-size:11px;color:var(--muted);">{_len_label}</div>
        ''', unsafe_allow_html=True)
        st.markdown("<div style='height:4px'></div>", unsafe_allow_html=True)

        ai_col, reset_col = st.columns([2, 1])
        with ai_col:
            ai_btn = st.button("Apply description signal", key="ai_btn")
        with reset_col:
            reset_btn = st.button("Clear", key="reset_btn")

        if reset_btn:
            for k,v in [("s_age",4),("s_sex",0),("s_dx",DIAGNOSES.index("fracture")),
                        ("s_bp",BODY_PARTS.index("head")),("s_loc",LOCATIONS.index("home")),
                        ("s_fire",0),("s_weekend",False),("s_alcohol",False),("s_drug",False),
                        ("s_narrative","")]:
                st.session_state[k] = v
            st.session_state.ai_result = None
            st.session_state.ai_ran    = False
            st.rerun()

        if ai_btn and narrative_text.strip():
            with st.spinner("🤖 Reading incident description and updating form fields..."):
                result = ai_extract_from_narrative(narrative_text)
                st.session_state.ai_result = result
                st.session_state.ai_ran    = True
                sf = result.get("suggested_fields", {})
                # Auto-fill form fields from AI extraction
                if sf.get("age_group") and sf["age_group"] in AGE_GROUPS:
                    st.session_state.s_age = AGE_GROUPS.index(sf["age_group"])
                if sf.get("diagnosis") and sf["diagnosis"] in DIAGNOSES:
                    st.session_state.s_dx = DIAGNOSES.index(sf["diagnosis"])
                if sf.get("body_part") and sf["body_part"] in BODY_PARTS:
                    st.session_state.s_bp = BODY_PARTS.index(sf["body_part"])
                if sf.get("location") and sf["location"] in LOCATIONS:
                    st.session_state.s_loc = LOCATIONS.index(sf["location"])
                if sf.get("fire_display") and sf["fire_display"] in FIRE_DISPLAY:
                    st.session_state.s_fire = FIRE_DISPLAY.index(sf["fire_display"])
                if sf.get("alcohol") is not None:
                    st.session_state.s_alcohol = bool(sf["alcohol"])
                if sf.get("drug") is not None:
                    st.session_state.s_drug = bool(sf["drug"])
                if sf.get("is_weekend") is not None:
                    st.session_state.s_weekend = bool(sf["is_weekend"])
                st.session_state.s_narrative = narrative_text
            st.rerun()
        elif ai_btn and not narrative_text.strip():
            st.warning("Please enter an incident description first.")

        # Show AI extraction result if available
        if st.session_state.ai_ran and st.session_state.ai_result:
            r = st.session_state.ai_result
            conf = r.get("confidence","Medium")
            conf_color = {"High":"#1A7A3C","Medium":"#B87A00","Low":"#A32D2D"}.get(conf,"#555")
            st.markdown(f"""
            <div style="background:#f0f4ff;border:1px solid #b5d4f4;border-radius:8px;
                        padding:8px 12px;margin-top:6px;font-size:12.5px;color:#0C447C;">
              <strong>Description incorporated into prediction.</strong>
              More detailed descriptions may improve reliability. Review inputs, then click Predict.
            </div>
            """, unsafe_allow_html=True)

        st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

        st.markdown("<div style='height:6px'></div>", unsafe_allow_html=True)
        predict_btn = st.button("🔍 Predict Admission Risk", type="primary")

    # ── Right column ──
    with right_col:
        if predict_btn:
            prob = predict_prob(
                age_group, sex, diagnosis, body_part, location,
                fire, is_weekend, alcohol, drug, narrative_len
            )
            rc, pc, gc, label, desc = risk_meta(prob)
            gauge_pct = int(prob * 100)

            # Result card
            st.markdown(f"""
            <div class="result-card {rc}">
              <p class="result-label">{label}</p>
              <p class="result-prob {pc}">{prob:.0%}</p>
              <p class="result-desc">{desc}</p>
              <div class="gauge-track">
                <div class="gauge-fill {gc}" style="width:{gauge_pct}%;"></div>
              </div>
              <div class="gauge-lbl"><span>0%</span><span>50%</span><span>100%</span></div>
            </div>
            """, unsafe_allow_html=True)

            # ── Risk flags (model-based + AI-detected) ──
            flags, ai_flags = [], []
            if "elderly" in age_group:           flags.append("Elderly — 9.3× higher baseline odds")
            elif "older adult" in age_group:     flags.append("Older adult — ~4× higher odds")
            if diagnosis == "fracture":           flags.append("Fracture — strongly linked to admission")
            if diagnosis in ["submersion","anoxia","internal organ injury","hemorrhage"]:
                flags.append(f"{diagnosis.title()} — high-severity diagnosis")
            if body_part in ["all parts body","25-50% of body","upper leg","lower trunk","upper trunk"]:
                flags.append(f"{body_part.title()} — elevated admission risk")
            if body_part == "head":               flags.append("Head injury — elevated severity")
            if alcohol:                           flags.append("Alcohol involvement")
            if drug:                              flags.append("Drug involvement")
            if fire != "no_fire_or_not_recorded": flags.append(f"Fire: {fire_display}")
            if location in ["farm/ranch","street or highway","industrial"]:
                flags.append(f"{location.title()} — higher-risk location")

            if st.session_state.ai_result:
                ai_flags = st.session_state.ai_result.get("extra_risk_signals", [])

            if flags:
                pills = "".join(f'<span class="flag-pill"><span class="flag-dot"></span>{f}</span>' for f in flags)
                st.markdown(f'<div class="flags-wrap">{pills}</div>', unsafe_allow_html=True)

            if ai_flags:
                ai_pills = "".join(f'<span class="ai-flag-pill"><span class="ai-dot"></span>AI: {f}</span>' for f in ai_flags)
                st.markdown(f'<div class="flags-wrap" style="margin-top:4px;">{ai_pills}</div>', unsafe_allow_html=True)

            if not flags and not ai_flags:
                st.success("No elevated risk indicators detected.")

            # ── AI narrative summary (feeds model context, not separate result) ──
            if st.session_state.ai_result:
                r = st.session_state.ai_result
                summary = r.get("ai_summary","")
                red_flags = r.get("red_flags",[])
                checks = r.get("suggested_checks",[])

                if summary:
                    st.markdown(f"""
                    <div style="background:#F5F0E8;border-left:4px solid #C8A951;
                                border-radius:0 8px 8px 0;padding:10px 14px;
                                font-size:12.5px;color:#3A2A00;margin-top:8px;line-height:1.6;">
                      <strong style="font-size:10.5px;text-transform:uppercase;
                                     letter-spacing:.07em;color:#7A5400;display:block;margin-bottom:4px;">
                        AI narrative reading
                      </strong>
                      {summary}
                    </div>
                    """, unsafe_allow_html=True)

                if red_flags:
                    rf_html = "".join(
                        f'<div style="display:flex;gap:7px;align-items:flex-start;margin-bottom:4px;">'
                        f'<span style="color:#B22234;font-size:13px;">⚠</span>'
                        f'<span style="font-size:12.5px;color:#444;">{f}</span></div>'
                        for f in red_flags
                    )
                    st.markdown(f"""
                    <div style="background:#fff1f0;border:1px solid #ffb3b3;border-radius:8px;
                                padding:10px 14px;margin-top:6px;">
                      <div style="font-size:10px;font-weight:600;text-transform:uppercase;
                                  letter-spacing:.07em;color:#B22234;margin-bottom:6px;">Red flags in description</div>
                      {rf_html}
                    </div>
                    """, unsafe_allow_html=True)

                if checks:
                    ch_html = "".join(
                        f'<div style="font-size:12.5px;color:#444;padding:3px 0;'
                        f'border-bottom:0.5px solid #eee;">'
                        f'<span style="color:#2A5298;margin-right:5px;">→</span>{c}</div>'
                        for c in checks
                    )
                    st.markdown(f"""
                    <div style="background:#fff;border:0.5px solid var(--border);
                                border-radius:8px;padding:10px 14px;margin-top:6px;
                                border-left:4px solid #2A5298;">
                      <div style="font-size:10px;font-weight:600;text-transform:uppercase;
                                  letter-spacing:.07em;color:#0A1F44;margin-bottom:6px;">Suggested checks</div>
                      {ch_html}
                    </div>
                    """, unsafe_allow_html=True)

            # ── What-if simulator ──
            st.markdown("<div style='height:6px'></div>", unsafe_allow_html=True)
            st.markdown('<p class="sec-head">What-if simulator</p>', unsafe_allow_html=True)
            whatif_rows = []
            if age_group in WHATIF_AGE:
                alt, delta = WHATIF_AGE[age_group]
                new_p = max(0.01, min(0.99, prob+delta))
                whatif_rows.append((f'If age were "{alt}"', f'{"↓" if delta<0 else "↑"} {prob:.0%} → {new_p:.0%}', "delta-down" if delta<0 else "delta-up"))
            if diagnosis in WHATIF_DX:
                alt, delta = WHATIF_DX[diagnosis]
                new_p = max(0.01, min(0.99, prob+delta))
                whatif_rows.append((f'If diagnosis were "{alt}"', f'{"↓" if delta<0 else "↑"} {prob:.0%} → {new_p:.0%}', "delta-down" if delta<0 else "delta-up"))
            if fire == "no_fire_or_not_recorded":
                new_p = min(0.99, prob+0.12)
                whatif_rows.append(('If fire department had responded', f'↑ {prob:.0%} → {new_p:.0%}', 'delta-up'))
            else:
                new_p = max(0.01, prob-0.12)
                whatif_rows.append(('If there had been no fire', f'↓ {prob:.0%} → {new_p:.0%}', 'delta-down'))

            rows_html = "".join(
                f'<div class="whatif-row"><span>{s}</span><span class="delta-pill {c}">{r}</span></div>'
                for s,r,c in whatif_rows
            )
            st.markdown(f'<div class="whatif-card"><div class="whatif-title">Scenario comparisons</div>{rows_html}</div>', unsafe_allow_html=True)

            # ── Population context ──
            overall_rate = POPULATION_RATES['overall']
            age_rate     = POPULATION_RATES['age'].get(age_group, overall_rate)
            dx_rate      = POPULATION_RATES['diagnosis'].get(diagnosis, overall_rate)
            multiplier   = prob / overall_rate
            st.markdown("<div style='height:6px'></div>", unsafe_allow_html=True)
            st.markdown('<p class="sec-head">Population context</p>', unsafe_allow_html=True)
            st.markdown(f"""
            <div class="ctx-bar">Overall NEISS 2024 admission rate: <strong>{overall_rate:.1%}</strong></div>
            <div class="ctx-bar">Typical rate for {age_group}: <strong>{age_rate:.1%}</strong></div>
            <div class="ctx-bar">Typical rate for {diagnosis}: <strong>{dx_rate:.1%}</strong></div>
            <div class="ctx-bar">This patient's estimated risk is <strong>{multiplier:.1f}×</strong> the population average</div>
            """, unsafe_allow_html=True)

            # ── Save to history ──
            st.session_state.history.insert(0, {
                "prob": prob, "label": label,
                "age": age_group, "dx": diagnosis,
                "bp": body_part
            })
            st.session_state.history = st.session_state.history[:5]

            with st.expander("📋 Full input summary", expanded=False):
                preview = narrative_text[:80]+"..." if len(narrative_text)>80 else (narrative_text if narrative_text.strip() else "Not provided")
                st.dataframe(pd.DataFrame({
                    "Field":["Age Group","Sex","Diagnosis","Body Part","Location",
                             "Fire Involvement","Weekend","Alcohol","Drug","Incident Description"],
                    "Value":[age_group,sex,diagnosis,body_part,location,
                             fire_display,"Yes" if is_weekend else "No",
                             "Yes" if alcohol else "No","Yes" if drug else "No",preview]
                }), hide_index=True, use_container_width=True)

        else:
            st.markdown("""
            <div class="result-card rc-idle">
              <p style="font-family:'Playfair Display',serif;font-size:1.3rem;color:#0A1F44;margin-bottom:.5rem;">Ready to assess</p>
              <p style="font-size:13px;color:#888;max-width:300px;margin:0 auto .8rem;">
                Fill the 3 steps, then hit <strong>Predict</strong>.
                Optionally add an incident description for AI-assisted auto-fill.
              </p>
              <p style="font-size:11.5px;color:#bbb;">NEISS 2024 · 361,672 ED cases</p>
            </div>
            """, unsafe_allow_html=True)

        # ── Prediction history ──
        if st.session_state.history:
            st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
            st.markdown('<p class="sec-head">Recent predictions</p>', unsafe_allow_html=True)
            for i, h in enumerate(st.session_state.history):
                color = "#B22234" if h["prob"]>0.7 else ("#B87A00" if h["prob"]>0.5 else "#1A7A3C")
                st.markdown(f"""
                <div class="hist-card">
                  <div>
                    <div class="hist-prob" style="color:{color};">{h['prob']:.0%}</div>
                    <div class="hist-details">{h['label'].replace('🔴 ','').replace('🟠 ','').replace('🟢 ','')}</div>
                  </div>
                  <div style="text-align:right;">
                    <div style="font-size:12.5px;color:#444;font-weight:500;">{h['age']} · {h['dx']}</div>
                    <div style="font-size:11px;color:var(--muted);">{h['bp']}</div>
                  </div>
                </div>
                """, unsafe_allow_html=True)

# ══════════════════════════════════════════
# TAB 2 — MODEL PERFORMANCE
# ══════════════════════════════════════════
with tab_model:
    st.markdown("""
<style>
.center-wrapper {
    display: flex;
    justify-content: center;
    width: 100%;
}

.stats-strip {
    display: flex;
    gap: 20px;
}

.stat-card {
    text-align: center;
}
</style>

<div class="center-wrapper">
    <div class="stats-strip">
        <div class="stat-card">
            <div class="stat-num">361,672</div>
            <div class="stat-lbl">ED cases (2024)</div>
        </div>
        <div class="stat-card">
            <div class="stat-num">81%</div>
            <div class="stat-lbl">Recall (admitted)</div>
        </div>
        <div class="stat-card">
            <div class="stat-num">85.7%</div>
            <div class="stat-lbl">ROC-AUC</div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)
    st.markdown('<p class="sec-head">Model iteration results</p>', unsafe_allow_html=True)
    st.markdown("""
    <table class="perf-table">
      <tr><th>Model</th><th>Recall (Admitted)</th><th>Precision</th><th>ROC-AUC</th><th>Key change</th></tr>
      <tr>
        <td>Baseline (Logistic Regression)</td>
        <td><span class="perf-badge pb-red">0.24</span></td>
        <td>0.61</td><td>0.849</td><td>No imbalance handling</td>
      </tr>
      <tr>
        <td>Iteration 1 — Class Weighting</td>
        <td><span class="perf-badge pb-amber">0.79</span></td>
        <td>0.28</td><td>0.851</td><td>Added class_weight='balanced'</td>
      </tr>
      <tr class="best">
        <td>Iteration 2 — Enhanced Features ✓ Final</td>
        <td><span class="perf-badge pb-green">0.81</span></td>
        <td>0.30</td><td>0.857</td><td>Added contextual features + interaction term</td>
      </tr>
    </table>
    """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Confusion matrix ──
    st.markdown('<p class="sec-head">Confusion matrix — final model on test set</p>', unsafe_allow_html=True)
    st.caption("Based on approximately 54,250 test cases (15% held-out set), at 0.5 threshold.")

    cm_col, explain_col = st.columns([1, 1.4], gap="large")
    with cm_col:
        # Approximate values derived from recall=0.81, precision=0.30, ~8.4% admission rate
        total_test = 54250
        actual_pos = int(total_test * 0.084)   # ~4557 admitted
        actual_neg = total_test - actual_pos    # ~49693 not admitted
        tp = int(actual_pos * 0.81)             # ~3691 correctly caught
        fn = actual_pos - tp                    # ~866 missed
        fp = int(tp / 0.30) - tp               # ~8612 false alarms
        tn = actual_neg - fp                    # ~41081 correct non-admissions

        st.markdown(f"""
        <div style="margin-bottom:10px;">
          <div style="display:grid;grid-template-columns:1fr 1fr;gap:8px;max-width:400px;">
            <div class="cm-cell cm-tp">
              <div class="cm-num" style="color:#1A7A3C;">~{tp:,}</div>
              <div class="cm-lbl" style="color:#1A7A3C;">True Positive</div>
              <div class="cm-desc">Correctly flagged as needing admission</div>
            </div>
            <div class="cm-cell cm-fp">
              <div class="cm-num" style="color:#B87A00;">~{fp:,}</div>
              <div class="cm-lbl" style="color:#B87A00;">False Positive</div>
              <div class="cm-desc">Flagged but didn't need admission (false alarm)</div>
            </div>
            <div class="cm-cell cm-fn">
              <div class="cm-num" style="color:#A32D2D;">~{fn:,}</div>
              <div class="cm-lbl" style="color:#A32D2D;">False Negative</div>
              <div class="cm-desc">Missed — needed admission but not caught</div>
            </div>
            <div class="cm-cell cm-tn">
              <div class="cm-num" style="color:#0C447C;">~{tn:,}</div>
              <div class="cm-lbl" style="color:#0C447C;">True Negative</div>
              <div class="cm-desc">Correctly identified as not needing admission</div>
            </div>
          </div>
        </div>
        """, unsafe_allow_html=True)

    with explain_col:
        st.markdown("""
        <div class="info-card" style="border-left-color:#1A7A3C;">
          <div class="info-title">Recall = 81% — our priority metric</div>
          <div class="info-body">Out of every 100 patients who truly need admission, we correctly catch 81. Missing a seriously injured patient is the worst outcome in triage — so we designed the model to maximise this number.</div>
        </div>
        <div class="info-card" style="border-left-color:#B87A00;">
          <div class="info-title">Precision = 30% — the accepted trade-off</div>
          <div class="info-body">Of every 100 patients the model flags, about 30 truly need admission. The other 70 are false alarms — but in a clinical setting, it is far safer to over-caution than to miss a patient who is seriously hurt. This trade-off is intentional and justified.</div>
        </div>
        <div class="info-card" style="border-left-color:#185FA5;">
          <div class="info-title">Why does precision look low?</div>
          <div class="info-body">Only 8.4% of ED patients in this dataset were admitted. Even a model that flags 30% of patients correctly is doing real work — it's identifying people at 3.6× the background rate. A perfect triage tool would never exist; this is a realistic, useful starting point.</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<p class="sec-head">Features in the final model</p>', unsafe_allow_html=True)
    st.markdown("""
    <table class="perf-table">
      <tr><th>Feature</th><th>What it captures</th><th>Why it helps</th></tr>
      <tr><td>Age group</td><td>Patient's age bracket</td><td>Strongest predictor — elderly patients are 9.3× more likely to be admitted</td></tr>
      <tr><td>Diagnosis</td><td>Type of injury</td><td>Fractures, submersion, and internal injuries have much higher admission rates than sprains or cuts</td></tr>
      <tr><td>Body part</td><td>Where the injury is</td><td>Injuries covering large body areas or involving the upper leg are strong predictors</td></tr>
      <tr><td>Location</td><td>Where the incident happened</td><td>Farm, street, and industrial injuries tend to be more severe than recreational ones</td></tr>
      <tr><td>Fire involvement</td><td>Whether a fire occurred</td><td>Fire-related incidents have substantially higher admission rates across all age groups</td></tr>
      <tr><td>Weekend visit</td><td>Day of the week</td><td>Weekend visits show slightly different injury patterns</td></tr>
      <tr><td>Alcohol / Drug flags</td><td>Substance involvement</td><td>Both linked to more severe injuries and complications during treatment</td></tr>
      <tr><td>Incident description length</td><td>How complex the case was to document</td><td>Longer notes = more happened. Used as a proxy for case complexity</td></tr>
      <tr><td>Age × Diagnosis interaction</td><td>Combined age + injury type</td><td>A fracture at 80 is very different from a fracture at 10 — this term lets the model learn that</td></tr>
    </table>
    """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("""
    <div class="info-card" style="border-left-color:#B22234;">
      <div class="info-title">Why did we balance the classes?</div>
      <div class="info-body">Only 8% of patients were admitted. Without correction, the model would predict "not admitted" for everyone and appear 92% accurate — but would be completely useless. Class balancing tells the model: a wrong prediction on an admitted patient is much more costly than a wrong prediction on a non-admitted patient. This single change boosted recall from 24% to 79%.</div>
    </div>
    <div class="info-card" style="border-left-color:#2A5298;">
      <div class="info-title">About survey weights (PSU, Stratum, Weight)</div>
      <div class="info-body">NEISS uses a complex probability sample design with weights that allow estimates to be generalised to the entire U.S. population. We retained these variables in the dataset but did not apply them in the predictive model — doing so would require survey-weighted regression (e.g. using the svy package in R or similar), which was beyond the scope of this project. This is an important limitation when interpreting results at the population level.</div>
    </div>
    """, unsafe_allow_html=True)

# ══════════════════════════════════════════
# TAB 3 — DATA INSIGHTS
# ══════════════════════════════════════════
with tab_insights:
    st.markdown('<p class="sec-head">Key findings from the NEISS 2024 analysis</p>', unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("**Admission rate by age group**")
        st.markdown("""
        <div class="bar-chart">
          <div class="bar-row"><span class="bar-label">infant (&lt;1)</span><div class="bar-track"><div class="bar-fill" style="width:32%;background:#2A5298;">9%</div></div><span class="bar-val">9%</span></div>
          <div class="bar-row"><span class="bar-label">toddler (1–4)</span><div class="bar-track"><div class="bar-fill" style="width:18%;background:#2A5298;">5%</div></div><span class="bar-val">5%</span></div>
          <div class="bar-row"><span class="bar-label">child (5–12)</span><div class="bar-track"><div class="bar-fill" style="width:18%;background:#2A5298;">5%</div></div><span class="bar-val">5%</span></div>
          <div class="bar-row"><span class="bar-label">adolescent (13–17)</span><div class="bar-track"><div class="bar-fill" style="width:21%;background:#2A5298;">6%</div></div><span class="bar-val">6%</span></div>
          <div class="bar-row"><span class="bar-label">young adult (18–34)</span><div class="bar-track"><div class="bar-fill" style="width:25%;background:#2A5298;">7%</div></div><span class="bar-val">7%</span></div>
          <div class="bar-row"><span class="bar-label">mid adult (35–49)</span><div class="bar-track"><div class="bar-fill" style="width:32%;background:#1B3A6B;">9%</div></div><span class="bar-val">9%</span></div>
          <div class="bar-row"><span class="bar-label">older adult (50–64)</span><div class="bar-track"><div class="bar-fill" style="width:46%;background:#1B3A6B;">13%</div></div><span class="bar-val">13%</span></div>
          <div class="bar-row"><span class="bar-label">elderly (65+)</span><div class="bar-track"><div class="bar-fill" style="width:100%;background:#B22234;">28%</div></div><span class="bar-val">28%</span></div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("**Cramér's V — how strongly each variable is linked to admission** (0 = no link, 1 = perfect link)")
        st.markdown("""
        <div class="bar-chart">
          <div class="bar-row"><span class="bar-label">age group</span><div class="bar-track"><div class="bar-fill" style="width:100%;background:#B22234;">0.322</div></div><span class="bar-val">0.322</span></div>
          <div class="bar-row"><span class="bar-label">body part</span><div class="bar-track"><div class="bar-fill" style="width:83%;background:#2A5298;">0.266</div></div><span class="bar-val">0.266</span></div>
          <div class="bar-row"><span class="bar-label">diagnosis</span><div class="bar-track"><div class="bar-fill" style="width:79%;background:#2A5298;">0.255</div></div><span class="bar-val">0.255</span></div>
          <div class="bar-row"><span class="bar-label">location</span><div class="bar-track"><div class="bar-fill" style="width:44%;background:#C8A951;">0.141</div></div><span class="bar-val">0.141</span></div>
          <div class="bar-row"><span class="bar-label">fire involvement</span><div class="bar-track"><div class="bar-fill" style="width:17%;background:#888;">0.054</div></div><span class="bar-val">0.054</span></div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("**Seasonal trend — injury cases by month (2024)**")
        st.caption("Cases rise from April, peak around September, then decline — consistent with outdoor activity patterns.")
        months = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]
        relative = [72, 68, 75, 82, 90, 95, 98, 100, 99, 88, 76, 70]
        month_bars = "".join(
            f'<div class="bar-row"><span class="bar-label">{m}</span>'
            f'<div class="bar-track"><div class="bar-fill" style="width:{v}%;background:{"#B22234" if v>=98 else "#2A5298" if v>=88 else "#1B3A6B"};"></div></div>'
            f'<span class="bar-val" style="font-size:11px;">{v}%</span></div>'
            for m, v in zip(months, relative)
        )
        st.markdown(f'<div class="bar-chart">{month_bars}</div>', unsafe_allow_html=True)

    with col2:
        st.markdown("**Admission rate by diagnosis — top 8**")
        st.markdown("""
        <div class="bar-chart">
          <div class="bar-row"><span class="bar-label">submersion</span><div class="bar-track"><div class="bar-fill" style="width:100%;background:#B22234;">45%</div></div><span class="bar-val">45%</span></div>
          <div class="bar-row"><span class="bar-label">anoxia</span><div class="bar-track"><div class="bar-fill" style="width:93%;background:#B22234;">42%</div></div><span class="bar-val">42%</span></div>
          <div class="bar-row"><span class="bar-label">internal organ</span><div class="bar-track"><div class="bar-fill" style="width:84%;background:#1B3A6B;">38%</div></div><span class="bar-val">38%</span></div>
          <div class="bar-row"><span class="bar-label">amputation</span><div class="bar-track"><div class="bar-fill" style="width:78%;background:#1B3A6B;">35%</div></div><span class="bar-val">35%</span></div>
          <div class="bar-row"><span class="bar-label">fracture</span><div class="bar-track"><div class="bar-fill" style="width:71%;background:#2A5298;">32%</div></div><span class="bar-val">32%</span></div>
          <div class="bar-row"><span class="bar-label">hemorrhage</span><div class="bar-track"><div class="bar-fill" style="width:56%;background:#2A5298;">25%</div></div><span class="bar-val">25%</span></div>
          <div class="bar-row"><span class="bar-label">laceration</span><div class="bar-track"><div class="bar-fill" style="width:11%;background:#888;">5%</div></div><span class="bar-val">5%</span></div>
          <div class="bar-row"><span class="bar-label">strain, sprain</span><div class="bar-track"><div class="bar-fill" style="width:7%;background:#888;">3%</div></div><span class="bar-val">3%</span></div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("**Odds ratios from logistic regression — how much more likely to be admitted vs young adult**")
        st.markdown("""
        <div class="bar-chart">
          <div class="bar-row"><span class="bar-label">elderly (65+)</span><div class="bar-track"><div class="bar-fill" style="width:100%;background:#B22234;">9.3×</div></div><span class="bar-val">9.3×</span></div>
          <div class="bar-row"><span class="bar-label">older adult (50–64)</span><div class="bar-track"><div class="bar-fill" style="width:43%;background:#1B3A6B;">4.0×</div></div><span class="bar-val">4.0×</span></div>
          <div class="bar-row"><span class="bar-label">mid adult (35–49)</span><div class="bar-track"><div class="bar-fill" style="width:23%;background:#2A5298;">2.1×</div></div><span class="bar-val">2.1×</span></div>
          <div class="bar-row"><span class="bar-label">young adult (18–34)</span><div class="bar-track"><div class="bar-fill" style="width:11%;background:#888;">—</div></div><span class="bar-val">ref.</span></div>
          <div class="bar-row"><span class="bar-label">adolescent (13–17)</span><div class="bar-track"><div class="bar-fill" style="width:8%;background:#888;">0.8×</div></div><span class="bar-val">0.8×</span></div>
          <div class="bar-row"><span class="bar-label">child (5–12)</span><div class="bar-track"><div class="bar-fill" style="width:6%;background:#888;">0.7×</div></div><span class="bar-val">0.7×</span></div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("**Weekend vs weekday — admission rate**")
        st.markdown("""
        <div class="bar-chart">
          <div class="bar-row"><span class="bar-label">Saturday</span><div class="bar-track"><div class="bar-fill" style="width:100%;background:#2A5298;">9.1%</div></div><span class="bar-val">9.1%</span></div>
          <div class="bar-row"><span class="bar-label">Sunday</span><div class="bar-track"><div class="bar-fill" style="width:97%;background:#2A5298;">8.9%</div></div><span class="bar-val">8.9%</span></div>
          <div class="bar-row"><span class="bar-label">Monday</span><div class="bar-track"><div class="bar-fill" style="width:88%;background:#888;">8.0%</div></div><span class="bar-val">8.0%</span></div>
          <div class="bar-row"><span class="bar-label">Tue–Fri</span><div class="bar-track"><div class="bar-fill" style="width:84%;background:#888;">7.7%</div></div><span class="bar-val">~7.7%</span></div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<p class="sec-head">Statistical test summary</p>', unsafe_allow_html=True)
    st.markdown("""
    <table class="perf-table">
      <tr><th>Test</th><th>Variables compared</th><th>Result</th><th>Effect size</th><th>Plain-English meaning</th></tr>
      <tr>
        <td>Welch's T-test</td><td>Age vs admission outcome</td>
        <td><span class="perf-badge pb-green">p &lt; 0.001</span></td>
        <td>Cohen's d = 1.003 (large)</td>
        <td>Admitted patients are significantly older, and the difference is large enough to matter clinically — not just statistically</td>
      </tr>
      <tr><td>Chi-square</td><td>Age group × admission</td><td><span class="perf-badge pb-green">p &lt; 0.001</span></td><td>Cramér's V = 0.322</td><td>Strongest categorical predictor — age group alone explains a meaningful share of admission variation</td></tr>
      <tr><td>Chi-square</td><td>Body part × admission</td><td><span class="perf-badge pb-green">p &lt; 0.001</span></td><td>Cramér's V = 0.266</td><td>Second strongest — where you're injured matters significantly</td></tr>
      <tr><td>Chi-square</td><td>Diagnosis × admission</td><td><span class="perf-badge pb-green">p &lt; 0.001</span></td><td>Cramér's V = 0.255</td><td>Third strongest — injury type is a meaningful predictor</td></tr>
      <tr><td>Chi-square</td><td>Fire involvement × admission</td><td><span class="perf-badge pb-green">p &lt; 0.001</span></td><td>Cramér's V = 0.054</td><td>Statistically significant but weak in practice — fire alone is a small predictor when considered independently</td></tr>
      <tr><td>Logistic Regression</td><td>All predictors combined</td><td><span class="perf-badge pb-green">LLR p &lt; 0.001</span></td><td>Pseudo R² = 0.135</td><td>The full model explains about 13.5% of variation in admission — moderate, appropriate for this type of real-world data</td></tr>
    </table>
    """, unsafe_allow_html=True)

# ══════════════════════════════════════════
# TAB 4 — ABOUT
# ══════════════════════════════════════════
with tab_about:
    c1, c2 = st.columns(2)
    with c1:
        st.markdown('<p class="sec-head">About this project</p>', unsafe_allow_html=True)
        st.markdown("""
        <div class="info-card">
          <div class="info-title">Course</div>
          <div class="info-body">DAB304 Healthcare Analytics — Professor A. Sodiq Shofoluwe</div>
        </div>
        <div class="info-card">
          <div class="info-title">Team</div>
          <div class="info-body">Ameenat Ali · Foluso Ojo · Gurpreet Kaur · Pei-Ru Chen</div>
        </div>
        <div class="info-card">
          <div class="info-title">Dataset</div>
          <div class="info-body">NEISS 2024 — National Electronic Injury Surveillance System. A nationally representative probability sample of U.S. hospital emergency departments, maintained by the U.S. Consumer Product Safety Commission (CPSC). 361,672 records with 25 variables.</div>
        </div>
        <div class="info-card">
          <div class="info-title">Analytical pipeline</div>
          <div class="info-body">Data overview → Preprocessing & cleaning → Exploratory data analysis → Statistical hypothesis testing → Baseline modeling → Model iteration → App deployment</div>
        </div>
        <div class="info-card">
          <div class="info-title">Ethical considerations</div>
          <div class="info-body">Race and Hispanic ethnicity were included as control variables. Their individual association with admission was weak (Cramér's V &lt; 0.15), confirming that injury characteristics and age — not demographics — are the primary drivers. We did not build a model that predicts risk based on race. The AI narrative assistant processes free text only — no patient identifiers are transmitted.</div>
        </div>
        """, unsafe_allow_html=True)
    with c2:
        st.markdown('<p class="sec-head">Methodology</p>', unsafe_allow_html=True)
        st.markdown("""
        <div class="info-card">
          <div class="info-title">Outcome variable</div>
          <div class="info-body">We asked: did this patient need to stay in the hospital? "Admitted/hospitalized" or "transferred" = yes (1). "Treated and released" = no (0). This binary target reflects real clinical injury severity judgments made by ED staff.</div>
        </div>
        <div class="info-card">
          <div class="info-title">Class imbalance handling</div>
          <div class="info-body">Only ~8.4% of patients were admitted. Without correction, the model predicts "not admitted" for everyone and achieves 92% accuracy — but zero usefulness. Class weighting adjusts the cost of each type of mistake, forcing the model to learn what makes someone high-risk. This boosted recall from 24% to 79% in one step.</div>
        </div>
        <div class="info-card">
          <div class="info-title">Why logistic regression?</div>
          <div class="info-body">Logistic regression gives a calibrated probability (not just yes/no), is directly explainable through odds ratios, and connects naturally to the statistical analysis already reported. It is also robust and fast — appropriate for a real-time triage support prototype.</div>
        </div>
        <div class="info-card">
          <div class="info-title">How the AI integrates with the model</div>
          <div class="info-body">The AI reads free-text incident descriptions and extracts structured field values (age group, diagnosis, body part, location, contextual flags). These extracted values are used to auto-fill the model's input form — so the AI feeds directly into the logistic regression prediction, rather than producing a separate parallel result. The AI handles unstructured text; the model handles prediction. One pipeline.</div>
        </div>
        <div class="info-card">
          <div class="info-title">Limitations</div>
          <div class="info-body">The model does not know the patient's medical history, existing conditions, vital signs, or lab results — all of which a real clinician would use. Survey design weights were not applied to the model. AI field extraction depends on narrative quality and may misread ambiguous descriptions. This is a research prototype, not a clinical tool.</div>
        </div>
        """, unsafe_allow_html=True)

# ─────────────────────────────────────────
# Footer
# ─────────────────────────────────────────
st.markdown("<div style='height:2rem'></div>", unsafe_allow_html=True)
st.markdown("""
<div style="border-top:1px solid rgba(10,31,68,0.1);padding-top:1rem;text-align:center;
            font-size:11px;color:#9AAACF;line-height:1.6;">
  <strong style="color:#B22234;">⚠ Educational Use Only</strong> &nbsp;·&nbsp;
  Built for DAB304 Healthcare Analytics — not for real clinical use. &nbsp;·&nbsp;
  Data: NEISS 2024 (U.S. Consumer Product Safety Commission) &nbsp;·&nbsp;
  Ameenat Ali · Foluso Ojo · Gurpreet Kaur · Pei-Ru Chen
</div>
""", unsafe_allow_html=True)