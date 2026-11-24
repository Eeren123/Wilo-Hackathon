from __future__ import annotations

import math
from typing import Any

import pandas as pd
import plotly.graph_objects as go
import streamlit as st


st.set_page_config(
    page_title="Wilo HydroCycle | Akıllı Su Optimizasyonu",
    page_icon="💧",
    layout="wide",
    initial_sidebar_state="expanded",
)

NAVY = "#142e49"
TEAL = "#19a898"
BLUE = "#4f96bf"
MINT = "#76d3c5"


def simulate(load: int, flow: int, speed: int, supply: int) -> dict[str, Any]:
    demand = load / 100
    flow_ratio = flow / 70
    speed_ratio = speed / 74
    temp_out = supply + 7.1 + demand * 1.4 - flow_ratio * 0.65
    power = 82 * speed_ratio**3 * (0.7 + demand * 0.3)
    water = 1860 * demand * (0.77 + flow_ratio * 0.23) * (
        1 + max(0, temp_out - 26) * 0.018
    )
    optimized_speed = max(45, min(speed, speed * (0.91 - max(0, flow_ratio - demand) * 0.08)))
    optimized_water = water * (0.91 + demand * 0.035)
    optimized_power = power * (optimized_speed / speed) ** 3
    it_energy_annual = 12_000_000
    current_wue = water * 24 * 365 / it_energy_annual
    optimized_wue = optimized_water * 24 * 365 / it_energy_annual

    points = []
    for index in range(12):
        hour = f"{index * 2:02}:00"
        wave = math.sin(index / 11 * math.pi * 2 - 1.1) * 0.09 + math.sin(index * 1.8) * 0.025
        factor = max(0.72, 1 + wave + (0.06 if 8 < index < 11 else 0))
        points.append(
            {
                "Zaman": hour,
                "Mevcut": round(water * factor),
                "Optimize": round(optimized_water * factor),
            }
        )

    return {
        "temp_in": float(supply),
        "temp_out": round(temp_out, 1),
        "power": round(power),
        "optimized_power": round(optimized_power),
        "water": round(water),
        "optimized_water": round(optimized_water),
        "water_saving": max(0, round((1 - optimized_water / water) * 100)),
        "energy_saving": max(0, round((1 - optimized_power / power) * 100)),
        "wue": round(current_wue, 2),
        "optimized_wue": round(optimized_wue, 2),
        "optimized_speed": round(optimized_speed),
        "anomaly": flow_ratio > demand * 1.25 or temp_out > 28 or speed > 92,
        "points": points,
    }


def format_number(value: float) -> str:
    return f"{value:,.0f}".replace(",", ".")


def make_chart(data: pd.DataFrame) -> go.Figure:
    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=data["Zaman"], y=data["Mevcut"], mode="lines+markers",
            name="Mevcut", line={"color": BLUE, "width": 3},
            marker={"size": 5},
        )
    )
    fig.add_trace(
        go.Scatter(
            x=data["Zaman"], y=data["Optimize"], mode="lines+markers",
            name="Optimize", line={"color": TEAL, "width": 3},
            marker={"size": 5},
        )
    )
    fig.update_layout(
        height=340,
        margin={"l": 8, "r": 12, "t": 18, "b": 8},
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font={"family": "Inter, Segoe UI, sans-serif", "color": "#718598", "size": 10},
        legend={"orientation": "h", "y": 1.12, "x": 0.02, "font": {"size": 10}},
        xaxis={"showgrid": False, "linecolor": "#e6edf1", "tickfont": {"size": 9}},
        yaxis={"title": "Su hacmi · L/sa", "gridcolor": "#edf1f4", "zeroline": False, "title_font": {"size": 9}},
        hovermode="x unified",
    )
    return fig


def section_heading(anchor: str, kicker: str, title: str, description: str) -> None:
    st.markdown(
        f'<div id="{anchor}"></div><div class="section-heading"><div><div class="section-kicker">{kicker}</div><h2 class="section-title">{title}</h2><p class="section-sub">{description}</p></div></div>',
        unsafe_allow_html=True,
    )


def story_card(number: str, title: str, description: str, tone: str) -> str:
    return f'<div class="story-card tone-{tone}"><span class="num">{number}</span><b>{title}</b><p>{description}</p></div>'


def step_card(number: str, title: str, description: str) -> str:
    return f'<div class="step-card tone-{number}"><span class="step">AŞAMA {number}</span><b>{title}</b><p>{description}</p></div>'


st.markdown(
    """
    <style>
      :root { --ink:#14283d; --muted:#75869a; --teal:#16b8a7; --teal-dark:#087f77; --blue:#4c8dff; --violet:#8a68f8; --coral:#ff6b70; --lime:#a5cb51; --line:#e3eaf0; --paper:#f5f6fb; --white:#fff; --radius:16px; --shadow:0 12px 36px rgba(18,43,69,.07); }
      .stApp { background:#f2f5f7; color:var(--ink); font-family:Inter,'Segoe UI',sans-serif; }
      [data-testid="stHeader"], [data-testid="stToolbar"] { visibility:hidden; height:0; }
      [data-testid="stSidebar"] { background:#102b43; border-right:1px solid #29445b; }
      [data-testid="stSidebar"] * { color:#e7eff5; }
      [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p { color:#a9bac8; font-size:12px; }
      [data-testid="stSidebar"] a.sidebar-link { display:flex; align-items:center; gap:11px; padding:11px 12px; margin:5px 0; border:1px solid transparent; border-radius:9px; color:#c3d0da!important; font-size:12px; font-weight:600; letter-spacing:.01em; text-decoration:none; transition:all .18s ease; }
      [data-testid="stSidebar"] a.sidebar-link:hover { color:#fff!important; background:#183c58; border-color:#2b536b; }
      .sidebar-context { margin:20px 4px 22px; padding:14px 13px; border:1px solid #29465e; border-radius:11px; background:#14334d; }
      .sidebar-context .context-kicker,.sidebar-nav-label { color:#8da5b6; font:700 9px Inter,'Segoe UI',sans-serif; letter-spacing:.14em; text-transform:uppercase; }
      .sidebar-context .context-title { color:#f3f7fa; font:700 14px Inter,'Segoe UI',sans-serif; margin-top:8px; letter-spacing:-.02em; }
      .sidebar-context .context-subtitle { color:#9fb4c4; font:400 10px Inter,'Segoe UI',sans-serif; line-height:1.5; margin-top:4px; }
      .sidebar-nav-label { margin:0 12px 8px; }
      .sidebar-link .nav-index { display:inline-flex; align-items:center; justify-content:center; width:25px; height:25px; flex:none; border:1px solid #38546b; border-radius:7px; color:#9dded6; font:700 9px Inter,'Segoe UI',sans-serif; }
      .sidebar-status { display:flex; align-items:center; gap:10px; margin:18px 4px 0; padding:13px 12px; border-top:1px solid #29445b; }
      .sidebar-status .status-dot { width:8px; height:8px; border-radius:50%; background:#65d7b4; box-shadow:0 0 0 4px rgba(101,215,180,.12); }
      .sidebar-status b { display:block; color:#d9e6ed; font:700 10px Inter,'Segoe UI',sans-serif; letter-spacing:.06em; }
      .sidebar-status small { display:block; color:#8fa7b8; font:400 9px Inter,'Segoe UI',sans-serif; margin-top:3px; }
      .block-container { padding-top:1.1rem; padding-bottom:3.5rem; max-width:1360px; }
      .brand { color:#fff; font:800 22px Inter,'Segoe UI',sans-serif; letter-spacing:-.04em; margin:8px 0 22px; white-space:nowrap; }
      .brand .brand-wilo { color:#ff6978; margin-right:6px; }
      .brand .brand-product { color:#8be4da; }
      .brand small { display:block; color:#8ea7ba; font:600 9px 'Segoe UI',sans-serif; letter-spacing:.18em; margin-top:4px; }
      .hero { background:#173c5a; border:1px solid #315872; border-radius:22px; padding:38px 46px; color:white; min-height:340px; position:relative; overflow:hidden; display:grid; grid-template-columns:1.08fr .92fr; align-items:center; box-shadow:0 20px 48px rgba(18,43,69,.13); }
      .hero:before { content:''; position:absolute; width:450px; height:450px; right:-100px; top:-250px; border:1px solid rgba(130,221,209,.11); border-radius:50%; box-shadow:0 0 0 30px rgba(130,221,209,.025),0 0 0 75px rgba(130,221,209,.025),0 0 0 125px rgba(130,221,209,.02); }
      .hero-copy { position:relative; z-index:2; max-width:620px; }
      .hero .eyebrow { display:inline-flex; align-items:center; gap:8px; font-size:9px; font-weight:700; letter-spacing:.15em; color:#87ded1; background:rgba(91,206,191,.1); border:1px solid rgba(126,218,207,.22); border-radius:30px; padding:7px 10px; }
      .hero .eyebrow:before { content:''; width:6px; height:6px; background:#55d4c1; border-radius:50%; box-shadow:0 0 0 4px rgba(85,212,193,.12); }
      .hero h1 { color:white; font:700 clamp(29px,3.4vw,46px)/1.12 Inter,'Segoe UI',sans-serif; margin:18px 0 12px; letter-spacing:-.045em; position:relative; z-index:1; text-shadow:0 4px 13px rgba(2,16,39,.46),0 0 30px rgba(129,202,255,.24); }
      .hero h1 span { color:#8ee0d2!important; }
      .hero p { color:#bfd0dc; font-size:13px; max-width:550px; line-height:1.75; position:relative; z-index:1; }
      .hero-meta { display:flex; align-items:center; gap:9px; margin-top:19px; color:#a9c0cd; font-size:9px; }
      .hero-meta span { padding:7px 10px; border:1px solid rgba(191,221,228,.18); background:rgba(8,25,41,.17); border-radius:7px; }
      .hero-visual { position:relative; z-index:1; display:flex; justify-content:center; align-items:center; min-height:245px; }
      .hero-visual svg { width:min(100%,430px); height:auto; filter:drop-shadow(0 15px 35px rgba(3,18,31,.2)); }
      a.hero-cta { display:inline-flex; align-items:center; gap:9px; position:relative; z-index:2; background:#19b09f; color:white; border-radius:8px; padding:11px 15px; font-size:10px; font-weight:700; text-decoration:none; margin-top:10px; box-shadow:0 7px 18px rgba(8,153,141,.22); transition:transform .18s ease,background .18s ease; }
      a.hero-cta:hover { background:#22c1ae; transform:translateY(-2px); }
      .section-heading { display:flex; align-items:flex-end; justify-content:space-between; gap:18px; margin:44px 0 17px; }
      .section-kicker { color:var(--teal-dark); font:700 9px Inter,'Segoe UI',sans-serif; letter-spacing:.16em; text-transform:uppercase; margin-bottom:7px; }
      .section-title { margin:0; color:var(--ink); font:700 clamp(20px,2vw,25px) Inter,'Segoe UI',sans-serif; letter-spacing:-.035em; }
      .section-sub { margin:6px 0 0; color:var(--muted); font-size:11px; line-height:1.6; }
      .story-card { height:100%; min-height:160px; background:#fff; border:1px solid var(--line); border-top:3px solid var(--card-accent,var(--teal)); border-radius:var(--radius); padding:20px; box-shadow:var(--shadow); transition:transform .18s ease,border-color .18s ease,box-shadow .18s ease; }
      .story-card.tone-coral { --card-accent:var(--coral); --card-wash:#fff0f0; }
      .story-card.tone-blue { --card-accent:var(--blue); --card-wash:#eef4ff; }
      .story-card.tone-violet { --card-accent:var(--violet); --card-wash:#f3efff; }
      .story-card:hover { transform:translateY(-3px); border-color:var(--card-accent); box-shadow:0 16px 34px rgba(18,43,69,.11); }
      .story-card .num { display:flex; align-items:center; gap:8px; color:var(--card-accent); font:700 9px Inter,'Segoe UI',sans-serif; letter-spacing:.12em; }
      .story-card .num:before { content:''; width:23px; height:2px; background:var(--card-accent); }
      .story-card b { display:block; color:#1d344a; font:700 15px Inter,'Segoe UI',sans-serif; margin:17px 0 8px; letter-spacing:-.02em; }
      .story-card p { color:#77899a; font-size:10px; line-height:1.7; margin:0; }
      .step-card { height:100%; min-height:146px; background:#fff; border:1px solid var(--line); border-top:3px solid var(--step-accent,var(--teal)); border-radius:13px; padding:17px 16px; box-shadow:0 8px 22px rgba(18,43,69,.045); }
      .step-card.tone-01 { --step-accent:var(--blue); --step-wash:#edf3ff; }
      .step-card.tone-02 { --step-accent:var(--violet); --step-wash:#f2efff; }
      .step-card.tone-03 { --step-accent:var(--coral); --step-wash:#fff0f0; }
      .step-card.tone-04 { --step-accent:var(--teal); --step-wash:#eaf8f5; }
      .step-card .step { display:inline-block; color:var(--step-accent); background:var(--step-wash); border-radius:6px; padding:5px 7px; font:700 8px Inter,'Segoe UI',sans-serif; letter-spacing:.1em; }
      .step-card b { display:block; color:#1f384f; font:700 13px Inter,'Segoe UI',sans-serif; margin:12px 0 6px; }
      .step-card p { color:#7f90a0; font-size:9px; line-height:1.6; margin:0; }
      .step-arrow { color:#6bbab0; font-size:18px; text-align:center; padding-top:43px; }
      div[data-testid="stVerticalBlockBorderWrapper"] { border:1px solid var(--line); border-radius:var(--radius); background:var(--white); box-shadow:var(--shadow); }
      .panel-title { color:#20394f; font:700 14px Inter,'Segoe UI',sans-serif; margin:0 0 3px; letter-spacing:-.02em; }
      .panel-copy { color:#8393a2; font-size:10px; margin:0 0 14px; line-height:1.5; }
      div[data-testid="stSlider"] label p { color:#4f6578; font-size:10px; font-weight:600; }
      div[data-testid="stSlider"] [data-testid="stThumbValue"] { color:#108b80; }
      div[data-testid="stSlider"] [data-baseweb="slider"] [role="slider"] { background-color:#19a898!important; border-color:#19a898!important; box-shadow:0 0 0 2px rgba(25,168,152,.16)!important; }
      div[data-testid="stSlider"] [data-baseweb="slider"] [role="slider"] [data-testid="stSliderThumbValue"] { background:#19a898!important; color:#fff!important; }
      div[data-testid="stSlider"] [data-baseweb="slider"] div[style*="height: 0.25rem"] { filter:hue-rotate(145deg) saturate(.82); }
      div[data-testid="stMetric"] { height:100%; background:#fff; border:1px solid #e6edf0; border-radius:12px; padding:15px 16px; box-shadow:none; }
      div[data-testid="stMetricLabel"] { color:#75889a; font-size:9px; letter-spacing:.045em; }
      div[data-testid="stMetricValue"] { color:#173650; font:700 clamp(20px,2.5vw,29px) Inter,'Segoe UI',sans-serif; letter-spacing:-.04em; }
      div[data-testid="stMetricDelta"] { font-size:9px; }
      .insight-grid { display:grid; grid-template-columns:repeat(3,1fr); gap:11px; margin-top:10px; }
      .insight-card { border:1px solid #e5ecef; border-radius:12px; background:#fff; padding:14px 16px; min-width:0; }
      .insight-label { color:#7b8e9f; font-size:8px; text-transform:uppercase; font-weight:700; letter-spacing:.12em; }
      .insight-value { color:#183650; font:700 26px Inter,'Segoe UI',sans-serif; letter-spacing:-.045em; margin:7px 0 3px; }
      .insight-detail { color:#8191a0; font-size:8px; line-height:1.45; }
      .notice { border-radius:10px; padding:12px 15px; background:#edf8f5; border:1px solid #d7eee8; color:#377f76; font-size:10px; line-height:1.6; }
      .warn { background:#fff8ed; border:1px solid #f1e5cf; color:#927044; }
      .impact-banner { background:#173c5a; border:1px solid #315872; border-radius:var(--radius); padding:26px 28px; color:#fff; min-height:100%; box-shadow:0 15px 32px rgba(18,43,69,.12); }
      .impact-banner .eyebrow { color:#85d8cb; font-size:8px; font-weight:700; letter-spacing:.15em; }
      .impact-banner b { display:block; font:700 18px/1.3 Inter,'Segoe UI',sans-serif; margin-top:12px; letter-spacing:-.025em; }
      .impact-banner p { color:#bdced8; font-size:10px; line-height:1.75; margin:8px 0 16px; }
      .formula { display:inline-block; border:1px solid rgba(156,215,209,.2); border-radius:8px; padding:10px 12px; background:rgba(7,27,42,.23); color:#dce9ef; font-size:9px; line-height:1.6; }
      .formula b { display:inline; color:#85ded1; font:700 9px Inter,'Segoe UI',sans-serif; margin:0; }
      .small-note { color:#8798a6; font-size:9px; line-height:1.6; }
      .wue-pair { display:grid; grid-template-columns:1fr 1fr; gap:9px; margin:14px 0 9px; }
      .wue-stat { background:#f5f8fa; border:1px solid #e5edf1; border-radius:10px; padding:14px 12px; min-width:0; }
      .wue-stat span { display:block; color:#7d8fa0; font-size:8px; letter-spacing:.08em; font-weight:700; }
      .wue-stat b { display:block; color:#20394f; font:700 23px Inter,'Segoe UI',sans-serif; margin-top:7px; white-space:nowrap; letter-spacing:-.04em; }
      .wue-stat b small { color:#8594a2; font:500 8px 'Segoe UI',sans-serif; margin-left:3px; letter-spacing:0; }
      .wue-stat.opt { background:#e9f7f3; border-color:#cdebe5; }
      .wue-stat.opt b { color:#078c81; }
      .source-chip { height:100%; min-height:105px; border:1px solid var(--line); background:#fff; border-radius:12px; padding:15px 16px; box-shadow:var(--shadow); transition:transform .18s ease,border-color .18s ease; }
      .source-chip:hover { transform:translateY(-2px); border-color:#b7dad4; }
      .source-chip a { color:#203d55; font:700 10px Inter,'Segoe UI',sans-serif; text-decoration:none; }
      .source-chip p { color:#8292a0; font-size:8px; line-height:1.6; margin:7px 0 0; }
      .footer { border-top:1px solid #e2e9ed; padding-top:16px; margin-top:28px; color:#8a99a6; font-size:8px; display:flex; justify-content:space-between; }
      .stButton>button { border-radius:8px; }
      @media(max-width:900px) { .hero { grid-template-columns:1fr .7fr; padding:30px; } .hero-visual { min-height:190px; } .step-arrow { padding-top:46px; } }
      @media(max-width:700px) { .hero { grid-template-columns:1fr; padding:24px 21px; min-height:0; } .hero-visual { min-height:175px; margin-top:8px; } .hero-visual svg { max-width:320px; } .block-container { padding:1rem 1rem 2.5rem; } .section-heading { margin-top:32px; } .insight-grid { grid-template-columns:1fr; } .step-card { min-height:125px; } .footer { flex-direction:column; gap:7px; } }
    </style>
    """,
    unsafe_allow_html=True,
)


with st.sidebar:
    st.markdown('<div class="brand"><span class="brand-wilo">Wilo</span><span class="brand-product">HydroCycle</span><small>AKILLI SU YÖNETİMİ</small></div>', unsafe_allow_html=True)
    st.markdown('<div class="sidebar-context"><div class="context-kicker">PROJE</div><div class="context-title">Veri merkezi</div><div class="context-subtitle">Soğutma · su optimizasyonu</div></div>', unsafe_allow_html=True)
    st.markdown('<div class="sidebar-nav-label">GENEL BAKIŞ</div>', unsafe_allow_html=True)
    st.markdown('<a class="sidebar-link" href="#problem"><span class="nav-index">01</span><span>Problem</span></a>', unsafe_allow_html=True)
    st.markdown('<a class="sidebar-link" href="#cozum-akisi"><span class="nav-index">02</span><span>Çözüm akışı</span></a>', unsafe_allow_html=True)
    st.markdown('<a class="sidebar-link" href="#canli-senaryo"><span class="nav-index">03</span><span>Canlı senaryo</span></a>', unsafe_allow_html=True)
    st.markdown('<a class="sidebar-link" href="#beklenen-etki"><span class="nav-index">04</span><span>Beklenen etki</span></a>', unsafe_allow_html=True)
    st.markdown('<div class="sidebar-status"><span class="status-dot"></span><div><b>DEMO MODU</b><small>Simüle edilmiş veriler</small></div></div>', unsafe_allow_html=True)

st.markdown(
    """
    <div class="hero">
      <div class="hero-copy">
        <div class="eyebrow">AKILLI SOĞUTMA · SU OPTİMİZASYONU</div>
        <h1>Veri merkezlerinin geleceği<br><span>daha akıllı, daha sürdürülebilir.</span></h1>
        <p>Soğutma sistemini talebe göre ayarlayan, su kaybı sinyallerini görünür kılan akıllı operasyon katmanı.</p>
        <a class="hero-cta" href="#canli-senaryo">Deneyimi keşfet&nbsp; ↓</a>
        <div class="hero-meta"><span>PROTOTİP SİMÜLASYONU</span><span>WUE ODAKLI</span><span>VERİ MERKEZİ 01</span></div>
      </div>
      <div class="hero-visual" aria-hidden="true">
        <svg viewBox="0 0 450 280" fill="none" xmlns="http://www.w3.org/2000/svg">
          <defs>
            <pattern id="dots" width="18" height="18" patternUnits="userSpaceOnUse"><circle cx="1" cy="1" r="1" fill="#b2e6df" fill-opacity=".12"/></pattern>
          </defs>
          <rect x="20" y="22" width="410" height="236" rx="20" fill="#0d263d" fill-opacity=".24" stroke="#a5d9d2" stroke-opacity=".15"/>
          <rect x="20" y="22" width="410" height="236" rx="20" fill="url(#dots)"/>
          <rect x="42" y="57" width="72" height="151" rx="8" fill="#244760" stroke="#8bb8c2" stroke-opacity=".42"/>
          <rect x="124" y="57" width="72" height="151" rx="8" fill="#244760" stroke="#8bb8c2" stroke-opacity=".42"/>
          <rect x="206" y="57" width="72" height="151" rx="8" fill="#244760" stroke="#8bb8c2" stroke-opacity=".42"/>
          <g stroke="#87aeb9" stroke-opacity=".45">
            <path d="M51 79h54M51 100h54M51 121h54M51 142h54M51 163h54M51 184h54"/>
            <path d="M133 79h54M133 100h54M133 121h54M133 142h54M133 163h54M133 184h54"/>
            <path d="M215 79h54M215 100h54M215 121h54M215 142h54M215 163h54M215 184h54"/>
          </g>
          <g fill="#65d7c7"><circle cx="99" cy="70" r="2.2"/><circle cx="181" cy="70" r="2.2"/><circle cx="263" cy="70" r="2.2"/></g>
          <path d="M55 224h228c17 0 27-10 27-26v-17c0-13 9-22 22-22h20" stroke="#49c3b4" stroke-width="4" stroke-linecap="round"/>
          <path d="M55 224h228c17 0 27-10 27-26v-17c0-13 9-22 22-22h20" stroke="#8ce8dc" stroke-opacity=".3" stroke-width="12" stroke-linecap="round"/>
          <circle cx="351" cy="159" r="25" fill="#15485a" stroke="#67d8c9" stroke-opacity=".7"/>
          <path d="M351 145c-6 8-10 12-10 18a10 10 0 1 0 20 0c0-6-4-10-10-18Z" fill="#8ce5d7"/>
          <rect x="314" y="62" width="92" height="40" rx="8" fill="#f6fbfb" fill-opacity=".96"/>
          <circle cx="328" cy="82" r="5" fill="#1ab09e"/>
          <text x="340" y="79" fill="#25435b" font-family="Segoe UI, sans-serif" font-size="8" font-weight="700" letter-spacing=".7">AKILLI AKIŞ</text>
          <text x="340" y="91" fill="#8495a3" font-family="Segoe UI, sans-serif" font-size="7">talebe göre dengelenir</text>
          <text x="43" y="242" fill="#94b7c3" font-family="Segoe UI, sans-serif" font-size="7" letter-spacing="1.2">SOĞUTMA DÖNGÜSÜ · DİJİTAL KONSEPT</text>
        </svg>
      </div>
    </div>
    """,
    unsafe_allow_html=True,
)

section_heading("problem", "01 · PROBLEM", "Görünmeyen kaybı görünür kılın", "Veri merkezlerinde soğutma talebi değişirken pompa ayarları çoğu zaman sabit kalır.")
problem_cols = st.columns(3, gap="medium")
problem_cards = [
    ("01 / KAYNAK", "Gereğinden fazla su", "Buharlaşma, tahliye ve değişken yükler su kullanımını izlemeyi zorlaştırır.", "coral"),
    ("02 / OPERASYON", "Sabit pompa ayarları", "Değişen soğutma ihtiyacına uymayan çalışma noktaları enerji ve su verimini düşürebilir.", "blue"),
    ("03 / GÖRÜNÜRLÜK", "Geç fark edilen anomali", "Debi, sıcaklık ve basınç sinyalleri birlikte değerlendirilmediğinde kayıp geç görünür.", "violet"),
]
for column, (number, title, copy, tone) in zip(problem_cols, problem_cards):
    with column:
        st.markdown(story_card(number, title, copy, tone), unsafe_allow_html=True)

section_heading("cozum-akisi", "02 · ÇÖZÜM AKIŞI", "Ölçümden eyleme, tek bir akıllı döngü", "Sistem sinyalleri anlamlandırır, öneri üretir ve su etkisini aynı akışta izler.")
steps = [
    ("01", "Veriyi topla", "Sıcaklık, debi, basınç, enerji ve su kullanımını bir araya getir."),
    ("02", "Anomaliyi bul", "Normal çalışma deseninden sapmaları ve olası kayıp sinyallerini belirle."),
    ("03", "Pompayı uyarla", "Soğutma ihtiyacını koruyan daha verimli bir çalışma noktası öner."),
    ("04", "Etkiyi izle", "Su tüketimi ve WUE değişimini senaryolar arasında takip et."),
]
step_cols = st.columns([1, .12, 1, .12, 1, .12, 1], gap="small")
for index, (num, title, copy) in enumerate(steps):
    with step_cols[index * 2]:
        st.markdown(step_card(num, title, copy), unsafe_allow_html=True)
    if index < 3:
        with step_cols[index * 2 + 1]:
            st.markdown('<div class="step-arrow">→</div>', unsafe_allow_html=True)

section_heading("canli-senaryo", "03 · ETKİLEŞİMLİ DEMO", "Sistemin kararını deneyimleyin", "Koşulları değiştirin; su kullanımı, pompa enerjisi ve WUE tahmininin nasıl etkilendiğini görün.")
with st.container(border=True):
    st.markdown('<div class="panel-title">Çalışma koşulları</div><p class="panel-copy">Kontrolleri değiştirin; senaryo grafiği ve etki metrikleri anında güncellensin.</p>', unsafe_allow_html=True)
    sim_cols = st.columns(4, gap="medium")
    with sim_cols[0]:
        load = st.slider("Soğutma yükü", 30, 100, 72, format="%d%%")
    with sim_cols[1]:
        flow = st.slider("Pompa debisi", 35, 100, 68, format="%d m³/sa")
    with sim_cols[2]:
        speed = st.slider("Pompa hızı", 40, 100, 74, format="%d%%")
    with sim_cols[3]:
        supply = st.slider("Giriş sıcaklığı", 12, 24, 18, format="%d °C")

result = simulate(load, flow, speed, supply)
with st.container(border=True):
    st.markdown('<div class="panel-title">Mevcut çalışma → optimizasyon önerisi</div><p class="panel-copy">Temsili senaryo karşılaştırması · saha sonucu değildir</p>', unsafe_allow_html=True)
    chart_df = pd.DataFrame(result["points"])
    st.plotly_chart(make_chart(chart_df), use_container_width=True, config={"displayModeBar": False})
    st.markdown(
        f'<div class="insight-grid"><div class="insight-card"><div class="insight-label">Su tasarrufu · tahmini</div><div class="insight-value">{result["water_saving"]}%</div><div class="insight-detail">{format_number(result["water"])} → {format_number(result["optimized_water"])} L/sa</div></div><div class="insight-card"><div class="insight-label">Enerji tasarrufu · tahmini</div><div class="insight-value">{result["energy_saving"]}%</div><div class="insight-detail">{format_number(result["power"])} → {format_number(result["optimized_power"])} kW</div></div><div class="insight-card"><div class="insight-label">Çıkış sıcaklığı</div><div class="insight-value">{result["temp_out"]:.1f}<span style="font-size:12px"> °C</span></div><div class="insight-detail">Giriş sıcaklığı {result["temp_in"]:.0f} °C</div></div></div>',
        unsafe_allow_html=True,
    )

if result["anomaly"]:
    st.markdown('<div class="notice warn">⚠️ Çalışma noktası incelenmeli: seçili yük, debi ve pompa hızı arasında simülasyon kaynaklı verimsizlik sinyali oluştu.</div>', unsafe_allow_html=True)
else:
    st.markdown('<div class="notice">✓ Simüle edilen çalışma noktası tanımlı demo aralığında görünüyor.</div>', unsafe_allow_html=True)

section_heading("beklenen-etki", "04 · BEKLENEN ETKİ", "Su verimliliğini ölçülebilir kılın", "WUE, tesisin su kullanımını BT ekipmanlarının enerji tüketimiyle birlikte değerlendirir.")
impact_col, wue_col = st.columns([1.25, 1], gap="medium")
with impact_col:
    st.markdown(
        f"""
        <div class="impact-banner">
          <div class="eyebrow">SU VERİMLİLİĞİ GÖSTERGESİ</div>
          <b>Her litreyi ölç, her pompa kararını iyileştir.</b>
          <p>WUE değerindeki düşüş, aynı BT enerji tüketimi için daha az su kullanıldığını gösterir. Uzun vadeli hedef; geri kazanım ve yeniden kullanım verisini de optimizasyon döngüsüne katmaktır.</p>
          <div class="formula">WUE = <b>Yıllık su tüketimi (L)</b> ÷ BT ekipmanlarının yıllık enerji tüketimi (kWh)</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
with wue_col:
    with st.container(border=True):
        st.markdown('<div class="panel-title">Senaryo WUE tahmini</div><p class="panel-copy">Demo modeli · ölçülmüş tesis verisi değildir</p>', unsafe_allow_html=True)
        st.markdown(f'<div class="wue-pair"><div class="wue-stat"><span>MEVCUT</span><b>{result["wue"]:.2f}<small>L/kWh</small></b></div><div class="wue-stat opt"><span>OPTİMİZE TAHMİNİ</span><b>{result["optimized_wue"]:.2f}<small>L/kWh</small></b></div></div><p class="small-note">Tahmini değişim: −{result["water_saving"]}%</p>', unsafe_allow_html=True)
        st.markdown('<p class="small-note">Gerçek WUE hesabı için doğrudan ölçülmüş yıllık su tüketimi ve BT enerji verisi gerekir.</p>', unsafe_allow_html=True)

section_heading("kaynaklar", "ARAŞTIRMA TEMELİ", "Referans veri kaynakları", "Entegrasyon kapsamı veri sözlükleri ve ölçüm tanımları incelendikten sonra netleştirilmelidir.")
sources = [
    ("Frontier Supercomputer · 2023", "Soğutma ve çalışma koşulları verisi. Takviye suyu veya buharlaşmayı doğrudan ölçtüğü varsayılmaz.", "https://figshare.com/articles/dataset/Dataset_of_Frontier_supercomputer/24391240/4?file=47812750"),
    ("Water Sustainability Dataset", "OSF üzerinde paylaşılan su sürdürülebilirliği veri seti. Entegrasyondan önce kapsamı doğrulanmalıdır.", "https://osf.io/g3zvd/"),
    ("NREL Data Center Cooling", "Hibrit soğutma sisteminde ölçülmüş sıcaklık ve soğutma gücü serileri; doğrudan su tüketimi değildir.", "https://github.com/M-D-Murphy/Data-Centre-Waste-Heat"),
]
source_cols = st.columns(3, gap="medium")
for column, (title, description, url) in zip(source_cols, sources):
    with column:
        st.markdown(f'<div class="source-chip"><a href="{url}" target="_blank">{title} ↗</a><p>{description}</p></div>', unsafe_allow_html=True)

st.markdown('<div style="height:18px"></div><div class="notice warn">Bu hackathon prototipi simüle edilmiş veriler ve açık optimizasyon varsayımları kullanır. Gerçek sensör bağlantısı, yapay zekâ servisi veya doğrulanmış tasarruf ölçümü yoktur.</div><p class="small-note" style="margin-top:15px">Wilo HydroCycle · Proje konsept tasarımı · Simülasyon modu</p>', unsafe_allow_html=True)
