from __future__ import annotations

import math
from typing import Any

import pandas as pd
import plotly.graph_objects as go
import streamlit as st


st.set_page_config(
    page_title="Akış Lab | Akıllı Su Optimizasyonu",
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
        height=300,
        margin={"l": 8, "r": 12, "t": 12, "b": 8},
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font={"family": "Segoe UI, sans-serif", "color": "#60758a", "size": 11},
        legend={"orientation": "h", "y": 1.12, "x": 0.02},
        xaxis={"showgrid": False, "linecolor": "#e6edf1"},
        yaxis={"title": "Su hacmi · L/sa", "gridcolor": "#edf1f4", "zeroline": False},
        hovermode="x unified",
    )
    return fig


st.markdown(
    """
    <style>
      .stApp { background:#f4f7fa; color:#1b334d; font-family:'DM Sans','Segoe UI',sans-serif; }
      [data-testid="stHeader"], [data-testid="stToolbar"] { visibility:hidden; height:0; }
      [data-testid="stSidebar"] { background:#122b45; border-right:1px solid #233f5b; }
      [data-testid="stSidebar"] * { color:#e1ebf3; }
      [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p { color:#aebfd0; }
      .block-container { padding-top:1.5rem; padding-bottom:2.5rem; max-width:1500px; }
      .brand { color:#fff; font:800 21px Manrope,sans-serif; letter-spacing:.08em; margin:8px 0 28px; }
      .brand span { color:#78d1c5; }
      .brand small { display:block; color:#92a9bc; font:600 9px 'DM Sans',sans-serif; letter-spacing:.18em; margin-top:3px; }
      .hero { background:linear-gradient(105deg,#142f4b 0%,#193c58 100%); border-radius:14px; padding:38px 42px; color:white; min-height:270px; position:relative; overflow:hidden; display:flex; align-items:center; }
      .hero:after { content:'H₂O'; position:absolute; right:7%; top:5px; font:800 152px Manrope,sans-serif; color:rgba(103,205,190,.10); letter-spacing:-.08em; }
      .eyebrow { font-size:9px; font-weight:700; letter-spacing:.16em; color:#78d1c5; }
      .hero h1 { color:white; font:700 clamp(25px,3vw,36px)/1.2 Manrope,sans-serif; margin:13px 0 8px; letter-spacing:-.035em; position:relative; z-index:1; }
      .hero p { color:#c1cfdb; font-size:13px; max-width:650px; line-height:1.7; position:relative; z-index:1; }
      .section-title { margin:30px 0 3px; color:#1c344e; font:700 21px Manrope,sans-serif; letter-spacing:-.03em; }
      .section-sub { margin:0 0 16px; color:#8796a5; font-size:11px; }
      div[data-testid="stMetric"] { background:#fff; border:1px solid #e8edf1; border-radius:10px; padding:15px 17px; box-shadow:0 2px 8px #18334f08; }
      div[data-testid="stMetricLabel"] { color:#8192a2; font-size:10px; letter-spacing:.08em; }
      div[data-testid="stMetricValue"] { color:#1e3852; font:700 27px Manrope,sans-serif; }
      div[data-testid="stMetricDelta"] { font-size:10px; }
      div[data-testid="stVerticalBlockBorderWrapper"] { border-color:#e7edf1; border-radius:10px; background:#fff; }
      .panel-title { color:#263f58; font:700 13px Manrope,sans-serif; margin:0 0 2px; }
      .panel-copy { color:#92a0ad; font-size:10px; margin:0 0 12px; }
      .notice { border-radius:7px; padding:12px 14px; background:#eff8f6; border:1px solid #dcefeb; color:#43877e; font-size:11px; line-height:1.6; }
      .warn { background:#fff7eb; border:1px solid #f3e6ca; color:#98784c; }
      .source { background:#fff; border:1px solid #e8edf1; border-radius:9px; padding:14px 16px; margin:8px 0; }
      .source b { color:#2a435c; font-size:12px; }
      .source p { color:#8292a1; font-size:10px; line-height:1.6; margin:6px 0 0; }
      .source a { color:#168f85; font-size:10px; }
      .small-note { color:#97a4af; font-size:9px; }
      .formula { display:inline-block; border-radius:6px; padding:10px 13px; background:#1d3b57; color:#dce9f1; font-size:11px; }
      .formula b { color:#77d1c4; }
      .stButton>button { border-radius:6px; }
      .story-label { color:#168f85; font-size:9px; font-weight:700; letter-spacing:.16em; }
      .story-card { min-height:145px; background:#fff; border:1px solid #e7edf1; border-radius:11px; padding:19px; }
      .story-card .num { color:#20a99a; font:700 12px Manrope,sans-serif; }
      .story-card b { display:block; color:#203b55; font:700 13px Manrope,sans-serif; margin:13px 0 6px; }
      .story-card p { color:#8292a1; font-size:10px; line-height:1.65; margin:0; }
      .step-card { background:#fff; border:1px solid #e6edf1; border-radius:10px; padding:16px 14px; min-height:132px; position:relative; }
      .step-card .step { color:#16a898; font:700 10px Manrope,sans-serif; letter-spacing:.12em; }
      .step-card b { display:block; color:#1f3a54; font:700 12px Manrope,sans-serif; margin:10px 0 5px; }
      .step-card p { color:#8796a3; font-size:9px; line-height:1.5; margin:0; }
      .step-arrow { color:#81bdb3; font-size:17px; text-align:center; padding-top:39px; }
      .impact-banner { background:#173650; border-radius:12px; padding:23px 25px; color:#fff; }
      .impact-banner b { font:700 15px Manrope,sans-serif; }
      .impact-banner p { color:#b8cad5; font-size:10px; line-height:1.65; }
      .source-chip { border:1px solid #e3ebef; background:#fff; border-radius:9px; padding:13px; min-height:86px; }
      .source-chip a { color:#203d55; font:700 10px Manrope,sans-serif; text-decoration:none; }
      .source-chip p { color:#8a98a4; font-size:8px; line-height:1.55; margin:6px 0 0; }
      a.hero-cta { display:inline-block; position:relative; z-index:2; background:#17a998; color:white; border-radius:6px; padding:10px 14px; font-size:10px; font-weight:700; text-decoration:none; margin-top:9px; }
      .wue-pair { display:grid; grid-template-columns:1fr 1fr; gap:8px; margin:15px 0 12px; }
      .wue-stat { background:#f4f8fa; border:1px solid #e8eef1; border-radius:8px; padding:13px 11px; min-width:0; }
      .wue-stat span { display:block; color:#8797a5; font-size:8px; letter-spacing:.08em; font-weight:700; }
      .wue-stat b { display:block; color:#213a54; font:700 21px Manrope,sans-serif; margin-top:5px; white-space:nowrap; }
      .wue-stat b small { color:#8797a5; font:500 8px 'DM Sans',sans-serif; margin-left:3px; }
      .wue-stat.opt { background:#eff9f6; border-color:#dcefe9; }
      .wue-stat.opt b { color:#148f82; }
      .section-gap { height:13px; }
      @media(max-width:700px) { .hero { padding:24px 20px; } .hero:after { right:0; top:32px; font-size:80px; } .block-container { padding-left:1rem; padding-right:1rem; } }
    </style>
    """,
    unsafe_allow_html=True,
)


with st.sidebar:
    st.markdown('<div class="brand">AKIŞ<span>.LAB</span><small>AKILLI SU YÖNETİMİ</small></div>', unsafe_allow_html=True)
    st.markdown("**Hackathon konsepti**  \nVeri merkezi soğutma sistemi")
    st.markdown("---")
    st.markdown('<a href="#problem" style="color:#d8e5ee;text-decoration:none">01 &nbsp; Problem</a>', unsafe_allow_html=True)
    st.markdown('<a href="#cozum-akisi" style="color:#d8e5ee;text-decoration:none">02 &nbsp; Çözüm akışı</a>', unsafe_allow_html=True)
    st.markdown('<a href="#canli-senaryo" style="color:#d8e5ee;text-decoration:none">03 &nbsp; Canlı senaryo</a>', unsafe_allow_html=True)
    st.markdown('<a href="#beklenen-etki" style="color:#d8e5ee;text-decoration:none">04 &nbsp; Beklenen etki</a>', unsafe_allow_html=True)
    st.markdown("---")
    st.markdown("🟢 **Demo simülasyonu**")
    st.caption("Saha verisi ve gerçek AI bağlantısı yok")

st.markdown(
    """
    <div class="hero">
      <div>
        <div class="eyebrow">AI-POWERED SMART WATER OPTIMIZATION</div>
        <h1>Veri merkezlerinin geleceği<br><span style="color:#7fd4c7">daha akıllı, daha sürdürülebilir.</span></h1>
        <p>Soğutma sistemini talebe göre ayarlayan, su kaybı sinyallerini görünür kılan akıllı operasyon katmanı.</p>
        <a class="hero-cta" href="#canli-senaryo">Deneyimi keşfet&nbsp; ↓</a>
      </div>
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown('<div id="problem"></div><div class="section-title">Görünmeyen kaybı görünür kılın</div><p class="section-sub">Veri merkezlerinde soğutma talebi değişirken pompa ayarları çoğu zaman sabit kalır.</p>', unsafe_allow_html=True)
problem_cols = st.columns(3, gap="medium")
problem_cards = [
    ("01 / KAYNAK", "Gereğinden fazla su", "Buharlaşma, tahliye ve değişken yükler su kullanımını izlemeyi zorlaştırır."),
    ("02 / OPERASYON", "Sabit pompa ayarları", "Değişen soğutma ihtiyacına uymayan çalışma noktaları enerji ve su verimini düşürebilir."),
    ("03 / GÖRÜNÜRLÜK", "Geç fark edilen anomali", "Debi, sıcaklık ve basınç sinyalleri birlikte değerlendirilmediğinde kayıp geç görünür."),
]
for column, (number, title, copy) in zip(problem_cols, problem_cards):
    with column:
        st.markdown(f'<div class="story-card"><span class="num">{number}</span><b>{title}</b><p>{copy}</p></div>', unsafe_allow_html=True)

st.markdown('<div id="cozum-akisi"></div><div class="section-title">Nasıl çalışıyor?</div><p class="section-sub">Ölçümden operasyonel etkiye uzanan dört adım.</p>', unsafe_allow_html=True)
steps = [
    ("01", "Veriyi topla", "Sıcaklık, debi, basınç, enerji ve su kullanımını bir araya getir."),
    ("02", "Anomaliyi bul", "Normal çalışma deseninden sapmaları ve olası kayıp sinyallerini belirle."),
    ("03", "Pompayı uyarla", "Soğutma ihtiyacını koruyan daha verimli bir çalışma noktası öner."),
    ("04", "Etkiyi izle", "Su tüketimi ve WUE değişimini senaryolar arasında takip et."),
]
step_cols = st.columns([1, .12, 1, .12, 1, .12, 1], gap="small")
for index, (num, title, copy) in enumerate(steps):
    with step_cols[index * 2]:
        st.markdown(f'<div class="step-card"><span class="step">AŞAMA {num}</span><b>{title}</b><p>{copy}</p></div>', unsafe_allow_html=True)
    if index < 3:
        with step_cols[index * 2 + 1]:
            st.markdown('<div class="step-arrow">→</div>', unsafe_allow_html=True)

st.markdown('<div id="canli-senaryo"></div><div class="section-title">Canlı senaryo laboratuvarı</div><p class="section-sub">Soğutma koşullarını değiştirin; simülasyon önerisinin su ve enerji etkisini anında görün.</p>', unsafe_allow_html=True)
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
    k1, k2, k3 = st.columns(3)
    k1.metric("Tahmini su tasarrufu", f"{result['water_saving']}%", f"{format_number(result['water'])} → {format_number(result['optimized_water'])} L/sa")
    k2.metric("Tahmini enerji tasarrufu", f"{result['energy_saving']}%", f"{format_number(result['power'])} → {format_number(result['optimized_power'])} kW")
    k3.metric("Çalışma sıcaklığı", f"{result['temp_out']:.1f} °C", f"Giriş {result['temp_in']:.0f} °C")

if result["anomaly"]:
    st.markdown('<div class="notice warn">⚠️ Çalışma noktası incelenmeli: seçili yük, debi ve pompa hızı arasında simülasyon kaynaklı verimsizlik sinyali oluştu.</div>', unsafe_allow_html=True)
else:
    st.markdown('<div class="notice">✓ Simüle edilen çalışma noktası tanımlı demo aralığında görünüyor.</div>', unsafe_allow_html=True)

st.markdown('<div id="beklenen-etki"></div><div class="section-title">Beklenen su etkisi</div><p class="section-sub">WUE, su kullanımını BT ekipmanlarının enerji tüketimiyle birlikte değerlendirir.</p>', unsafe_allow_html=True)
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

st.markdown('<div class="section-title">Teknik keşif kaynakları</div><p class="section-sub">Prototipin araştırma aşamasında incelenmesi planlanan veri setleri.</p>', unsafe_allow_html=True)
sources = [
    ("Frontier Supercomputer · 2023", "Soğutma ve çalışma koşulları verisi. Takviye suyu veya buharlaşmayı doğrudan ölçtüğü varsayılmaz.", "https://figshare.com/articles/dataset/Dataset_of_Frontier_supercomputer/24391240/4?file=47812750"),
    ("Water Sustainability Dataset", "OSF üzerinde paylaşılan su sürdürülebilirliği veri seti. Entegrasyondan önce kapsamı doğrulanmalıdır.", "https://osf.io/g3zvd/"),
    ("NREL Data Center Cooling", "Hibrit soğutma sisteminde ölçülmüş sıcaklık ve soğutma gücü serileri; doğrudan su tüketimi değildir.", "https://github.com/M-D-Murphy/Data-Centre-Waste-Heat"),
]
source_cols = st.columns(3, gap="medium")
for column, (title, description, url) in zip(source_cols, sources):
    with column:
        st.markdown(f'<div class="source-chip"><a href="{url}" target="_blank">{title} ↗</a><p>{description}</p></div>', unsafe_allow_html=True)

st.markdown('<div style="height:18px"></div><div class="notice warn">Bu hackathon prototipi simüle edilmiş veriler ve açık optimizasyon varsayımları kullanır. Gerçek sensör bağlantısı, yapay zekâ servisi veya doğrulanmış tasarruf ölçümü yoktur.</div><p class="small-note" style="margin-top:15px">AKIŞ.LAB · Proje konsept tasarımı · Simülasyon modu</p>', unsafe_allow_html=True)
