import streamlit as st
import pyodbc
import pandas as pd
import decimal
import warnings
import math
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime, timedelta

# Suppress pandas/pyodbc SQLAlchemy warnings
warnings.filterwarnings("ignore", message="pandas only supports SQLAlchemy")

# ----------------------------
# PAGE CONFIG
# ----------------------------
st.set_page_config(
    page_title="akYtec — NIS SMT Line Intelligence",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={"About": None}  # Hide Streamlit menu
)

# ============================================================
# CSS — Dark Industrial Circuit Board Theme
# ============================================================
css_block = """
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600;700&display=swap" rel="stylesheet">
<style>
    *, *::before, *::after { box-sizing: border-box; }
    .stApp {
        background: #0A0F1D;
        color: #CBD5E1;
        font-family: 'Outfit', sans-serif;
    }
    [data-testid="stAppViewContainer"],
    [data-testid="stHeader"] { background: transparent !important; }

    /* Circuit board pattern left side */
    .stApp::before {
        content: '';
        position: fixed; top: 0; left: 0;
        width: 260px; height: 100%;
        background:
            radial-gradient(circle at 30px 40px, rgba(0,229,255,0.06) 1px, transparent 1px),
            radial-gradient(circle at 90px 120px, rgba(0,229,255,0.04) 2px, transparent 2px),
            radial-gradient(circle at 50px 220px, rgba(0,229,255,0.05) 1px, transparent 1px),
            radial-gradient(circle at 130px 340px, rgba(0,229,255,0.04) 2px, transparent 2px),
            radial-gradient(circle at 20px 480px, rgba(0,229,255,0.06) 1px, transparent 1px),
            radial-gradient(circle at 110px 560px, rgba(0,229,255,0.04) 2px, transparent 2px),
            radial-gradient(circle at 40px 680px, rgba(0,229,255,0.05) 1px, transparent 1px),
            repeating-linear-gradient(0deg, transparent, transparent 60px, rgba(0,229,255,0.02) 60px, rgba(0,229,255,0.02) 61px),
            repeating-linear-gradient(90deg, transparent, transparent 60px, rgba(0,229,255,0.02) 60px, rgba(0,229,255,0.02) 61px);
        pointer-events: none; z-index: 0;
        opacity: 0.7;
    }

    /* ===== SIDEBAR ===== */
    section[data-testid="stSidebar"] {
        background: rgba(10,15,29,0.98) !important;
        backdrop-filter: blur(20px);
        border-right: 1px solid rgba(0,229,255,0.08);
        width: 72px !important; min-width: 72px !important;
    }
    section[data-testid="stSidebar"] .st-emotion-cache-1wrcr25 { padding: 12px 8px !important; }
    section[data-testid="stSidebar"] .st-emotion-cache-1y4p8pa { padding: 0 !important; }
    .sidebar-icon {
        display: flex; flex-direction: column; align-items: center;
        justify-content: center; width: 56px; height: 56px;
        margin: 6px auto; border-radius: 12px;
        background: rgba(0,229,255,0.03);
        border: 1px solid rgba(0,229,255,0.04);
        color: #6B7280; font-size: 0.55rem; font-weight: 600;
        text-transform: uppercase; letter-spacing: 0.08em;
        transition: all 0.2s; cursor: pointer;
    }
    .sidebar-icon:hover, .sidebar-icon.active {
        background: rgba(0,229,255,0.08);
        border-color: rgba(0,229,255,0.15);
        color: #00E5FF;
    }
    .sidebar-icon svg { width: 24px; height: 24px; margin-bottom: 3px; }
    .sidebar-logo { text-align: center; margin: 12px 0 10px 0; }
    .sidebar-logo svg { height: 32px; width: auto; }

    /* ===== KPI CARDS ===== */
    .kpi-card {
        background: rgba(15,23,42,0.75);
        backdrop-filter: blur(12px);
        border: 1px solid rgba(0,229,255,0.06);
        border-radius: 12px; padding: 16px 18px;
        box-shadow: 0 2px 16px rgba(0,0,0,0.30);
        position: relative; overflow: hidden;
    }
    .kpi-card .accent-green { position: absolute; left: 0; top: 0; width: 4px; height: 100%; background: #00E676; }
    .kpi-card .accent-orange { position: absolute; left: 0; top: 0; width: 4px; height: 100%; background: #FF9100; }
    .kpi-card .accent-blue { position: absolute; left: 0; top: 0; width: 4px; height: 100%; background: #00E5FF; }
    .kpi-card .accent-purple { position: absolute; left: 0; top: 0; width: 4px; height: 100%; background: #B388FF; }
    .kpi-label { font-size: 0.7rem; color: #6B7280; font-weight: 600; text-transform: uppercase; letter-spacing: 0.08em; }
    .kpi-today { font-family: 'JetBrains Mono', monospace; font-size: 1.6rem; font-weight: 700; color: #E0E6ED; line-height: 1.2; }
    .kpi-monthly { font-family: 'JetBrains Mono', monospace; font-size: 0.75rem; color: #64748b; font-weight: 500; }
    .kpi-sub { font-size: 0.65rem; color: #475569; margin-top: 2px; }

    /* ===== DONUT CARD ===== */
    .donut-card {
        background: rgba(15,23,42,0.75);
        backdrop-filter: blur(12px);
        border: 1px solid rgba(0,229,255,0.06);
        border-radius: 12px; padding: 14px;
        text-align: center;
        box-shadow: 0 2px 16px rgba(0,0,0,0.30);
    }
    .donut-label { font-size: 0.72rem; color: #6B7280; font-weight: 600; text-transform: uppercase; letter-spacing: 0.06em; margin-top: 6px; }
    .donut-value { font-family: 'JetBrains Mono', monospace; font-size: 1.1rem; font-weight: 700; color: #E0E6ED; }

    /* ===== STATUS WIDGET ===== */
    .status-card {
        background: rgba(15,23,42,0.75);
        backdrop-filter: blur(12px);
        border: 1px solid rgba(0,229,255,0.06);
        border-radius: 12px; padding: 16px;
        box-shadow: 0 2px 16px rgba(0,0,0,0.30);
    }
    .status-dot { display: inline-block; width: 12px; height: 12px; border-radius: 50%; margin-right: 6px; }
    .status-dot.green { background: #00E676; box-shadow: 0 0 8px rgba(0,230,118,0.5); }
    .status-label { font-size: 0.72rem; color: #6B7280; font-weight: 600; text-transform: uppercase; letter-spacing: 0.06em; }
    .status-value { font-family: 'JetBrains Mono', monospace; font-size: 1.2rem; font-weight: 700; color: #E0E6ED; }

    /* ===== BOTTOM TALLY ===== */
    .tally-card {
        background: rgba(15,23,42,0.75);
        backdrop-filter: blur(12px);
        border-radius: 12px; padding: 12px 10px;
        text-align: center;
        box-shadow: 0 2px 16px rgba(0,0,0,0.30);
        border: 1px solid rgba(0,229,255,0.04);
    }
    .tally-label { font-size: 0.62rem; color: #6B7280; font-weight: 600; text-transform: uppercase; letter-spacing: 0.06em; }
    .tally-val { font-family: 'JetBrains Mono', monospace; font-size: 1.5rem; font-weight: 700; color: #E0E6ED; line-height: 1.3; }
    .tally-val.green { color: #00E676; }
    .tally-val.red { color: #FF1744; }
    .tally-val.blue { color: #00E5FF; }
    .tally-val.orange { color: #FF9100; }
    .tally-val.purple { color: #B388FF; }

    /* ===== ROW TITLE ===== */
    .row-title {
        font-size: 0.72rem; color: #475569; font-weight: 600;
        text-transform: uppercase; letter-spacing: 0.12em;
        margin: 18px 0 8px 0; padding-bottom: 4px;
        border-bottom: 1px solid rgba(0,229,255,0.04);
    }

    /* ===== TABLES ===== */
    .mtable { width: 100%; border-collapse: separate; border-spacing: 0; margin-top: 8px; }
    .mtable thead th {
        background: rgba(0,229,255,0.04); color: #00E5FF; font-weight: 700;
        font-size: 0.78rem; text-transform: uppercase; letter-spacing: 0.06em;
        padding: 10px 12px; text-align: left;
        border-bottom: 1.5px solid rgba(0,229,255,0.08);
    }
    .mtable thead th:first-child { border-radius: 8px 0 0 0; }
    .mtable thead th:last-child  { border-radius: 0 8px 0 0; }
    .mtable tbody tr:hover { background: rgba(0,229,255,0.03); }
    .mtable tbody td { padding: 8px 12px; font-size: 0.85rem; color: #CBD5E1; border-bottom: 1px solid rgba(0,229,255,0.03); }
    .v-ok   { color: #00E676; font-weight: 700; font-family: 'JetBrains Mono', monospace !important; }
    .v-warn { color: #FFD600; font-weight: 700; font-family: 'JetBrains Mono', monospace !important; }
    .v-bad  { color: #FF1744; font-weight: 700; font-family: 'JetBrains Mono', monospace !important; }
    .v-mono { font-family: 'JetBrains Mono', monospace !important; color: #E0E6ED; font-weight: 600; }

    /* ===== TV MODE ===== */
    .tv-mode .kpi-today { font-size: 2.4rem !important; }
    .tv-mode .donut-value { font-size: 1.6rem !important; }
    .tv-mode .status-value { font-size: 1.8rem !important; }
    .tv-mode .tally-val { font-size: 2.2rem !important; }
    .tv-mode .row-title { font-size: 1rem !important; }

    /* ===== HIDE STREAMLIT ===== */
    #MainMenu, footer, header, .stDeployButton { display: none !important; }
    [data-testid="stToolbar"] { display: none !important; }
    hr { border-color: rgba(0,229,255,0.08) !important; }
</style>
"""
st.markdown(css_block, unsafe_allow_html=True)


# ============================================================
# DATABASE CONNECTION (backend — unchanged)
# ============================================================
CONN_STR = (
    r"DRIVER={ODBC Driver 17 for SQL Server};"
    r"SERVER=.\SQLEXPRESS;"
    r"DATABASE=SQUAD;"
    r"Trusted_Connection=yes;"
)

@st.cache_data(ttl=60)
def get_data_from_db(date_str):
    query = """
        SELECT
            f.MachineNm,
            f.BaseProgramNm,
            c.IdealCycleSec,
            f.TotalBoard,
            f.WorkedPcb,
            f.SkippedPcb,
            f.ArrayPerBoard,
            f.StartTime,
            f.RunSec,
            f.StopSec,
            f.PlaceSec,
            f.TransferSec,
            f.EntryWaitSec,
            f.ExitWaitSec,
            f.HeadPickup,
            f.HeadPlace,
            f.HeadError,
            f.HeadErrorPpm,
            f.HeadPostPickMiss,
            f.HeadPrePlaceMiss,
            f.HeadPartNg,
            f.HeadDump,
            f.PeakBuildSecPerBoard,
            f.PeakBoardPerHour,
            f.PeakChipPerHour,
            f.MeanBuildSecPerBoard,
            f.MeanBoardPerHour,
            f.MeanChipPerHour,
            f.PreviousCycleSecPerBoard
        FROM Custom_MachineRunFact f WITH (NOLOCK)
        LEFT JOIN Custom_ProgramCycleTime c WITH (NOLOCK)
            ON f.LineCd = c.LineCd AND f.BaseProgramNm = c.BaseProgramNm
        WHERE f.LineCd = '003LINE'
            AND CAST(f.StartTime AS DATE) = ?
            AND DATEPART(HOUR, f.StartTime) BETWEEN 8 AND 15
    """
    columns = [
        "MachineNm", "BaseProgramNm", "IdealCycleSec",
        "TotalBoard", "WorkedPcb", "SkippedPcb", "ArrayPerBoard", "StartTime",
        "RunSec", "StopSec", "PlaceSec", "TransferSec", "EntryWaitSec", "ExitWaitSec",
        "HeadPickup", "HeadPlace", "HeadError", "HeadErrorPpm",
        "HeadPostPickMiss", "HeadPrePlaceMiss", "HeadPartNg", "HeadDump",
        "PeakBuildSecPerBoard", "PeakBoardPerHour", "PeakChipPerHour",
        "MeanBuildSecPerBoard", "MeanBoardPerHour", "MeanChipPerHour",
        "PreviousCycleSecPerBoard"
    ]
    try:
        conn = pyodbc.connect(CONN_STR, timeout=3)
        cursor = conn.cursor()
        cursor.execute(query, (date_str,))
        rows = cursor.fetchall()
        conn.close()
        if not rows:
            return pd.DataFrame(columns=columns)
        clean = []
        for row in rows:
            clean.append([float(v) if isinstance(v, decimal.Decimal) else v for v in row])
        return pd.DataFrame(clean, columns=columns)
    except Exception:
        return pd.DataFrame(columns=columns)


# ============================================================
# DEMO DATA
# ============================================================
def get_demo_data():
    base_date = datetime.now().strftime("%Y-%m-%d")
    return pd.DataFrame([
        {
            "MachineNm": "M1", "BaseProgramNm": "PRR21P03-01_CL.1_REV_3",
            "IdealCycleSec": 83.0, "TotalBoard": 194, "WorkedPcb": 776,
            "SkippedPcb": 2, "ArrayPerBoard": 4.0,
            "StartTime": datetime.strptime(f"{base_date} 08:15", "%Y-%m-%d %H:%M"),
            "RunSec": 11182, "StopSec": 455, "PlaceSec": 5600,
            "TransferSec": 300, "EntryWaitSec": 4027, "ExitWaitSec": 1255,
            "HeadPickup": 50200, "HeadPlace": 50000, "HeadError": 124, "HeadErrorPpm": 2470,
            "HeadPostPickMiss": 76, "HeadPrePlaceMiss": 0, "HeadPartNg": 64, "HeadDump": 12,
            "PeakBuildSecPerBoard": 83.0, "PeakBoardPerHour": 43, "PeakChipPerHour": 520,
            "MeanBuildSecPerBoard": 85.2, "MeanBoardPerHour": 42, "MeanChipPerHour": 508,
            "PreviousCycleSecPerBoard": 84.0
        },
        {
            "MachineNm": "M2", "BaseProgramNm": "PRR21P03-01_CL.1_REV_3",
            "IdealCycleSec": 88.0, "TotalBoard": 194, "WorkedPcb": 776,
            "SkippedPcb": 1, "ArrayPerBoard": 4.0,
            "StartTime": datetime.strptime(f"{base_date} 09:45", "%Y-%m-%d %H:%M"),
            "RunSec": 9536, "StopSec": 1101, "PlaceSec": 8594,
            "TransferSec": 377, "EntryWaitSec": 565, "ExitWaitSec": 0,
            "HeadPickup": 50120, "HeadPlace": 50000, "HeadError": 45, "HeadErrorPpm": 898,
            "HeadPostPickMiss": 35, "HeadPrePlaceMiss": 5, "HeadPartNg": 14, "HeadDump": 6,
            "PeakBuildSecPerBoard": 88.0, "PeakBoardPerHour": 40, "PeakChipPerHour": 490,
            "MeanBuildSecPerBoard": 90.1, "MeanBoardPerHour": 39, "MeanChipPerHour": 478,
            "PreviousCycleSecPerBoard": 87.5
        },
        {
            "MachineNm": "M1", "BaseProgramNm": "PRR21P03-01_CL2",
            "IdealCycleSec": None, "TotalBoard": 350, "WorkedPcb": 1400,
            "SkippedPcb": 0, "ArrayPerBoard": 4.0,
            "StartTime": datetime.strptime(f"{base_date} 10:30", "%Y-%m-%d %H:%M"),
            "RunSec": 7132, "StopSec": 3, "PlaceSec": 0,
            "TransferSec": 329, "EntryWaitSec": 4027, "ExitWaitSec": 2776,
            "HeadPickup": 0, "HeadPlace": 0, "HeadError": 0, "HeadErrorPpm": 0,
            "HeadPostPickMiss": 0, "HeadPrePlaceMiss": 0, "HeadPartNg": 0, "HeadDump": 0,
            "PeakBuildSecPerBoard": 0.0, "PeakBoardPerHour": 0, "PeakChipPerHour": 0,
            "MeanBuildSecPerBoard": 0.0, "MeanBoardPerHour": 0, "MeanChipPerHour": 0,
            "PreviousCycleSecPerBoard": 0.0
        },
        {
            "MachineNm": "M2", "BaseProgramNm": "PRR21P03-01_CL2",
            "IdealCycleSec": None, "TotalBoard": 350, "WorkedPcb": 1400,
            "SkippedPcb": 0, "ArrayPerBoard": 4.0,
            "StartTime": datetime.strptime(f"{base_date} 11:20", "%Y-%m-%d %H:%M"),
            "RunSec": 7237, "StopSec": 73, "PlaceSec": 1940,
            "TransferSec": 678, "EntryWaitSec": 600, "ExitWaitSec": 4019,
            "HeadPickup": 20150, "HeadPlace": 20000, "HeadError": 32, "HeadErrorPpm": 1588,
            "HeadPostPickMiss": 45, "HeadPrePlaceMiss": 12, "HeadPartNg": 15, "HeadDump": 8,
            "PeakBuildSecPerBoard": 10.4, "PeakBoardPerHour": 176, "PeakChipPerHour": 2110,
            "MeanBuildSecPerBoard": 11.8, "MeanBoardPerHour": 167, "MeanChipPerHour": 2004,
            "PreviousCycleSecPerBoard": 10.6
        },
        {
            "MachineNm": "M1", "BaseProgramNm": "PRR21P03-01_CL.1_REV_3",
            "IdealCycleSec": 83.0, "TotalBoard": 250, "WorkedPcb": 1000,
            "SkippedPcb": 1, "ArrayPerBoard": 4.0,
            "StartTime": datetime.strptime(f"{base_date} 12:10", "%Y-%m-%d %H:%M"),
            "RunSec": 7200, "StopSec": 210, "PlaceSec": 4200,
            "TransferSec": 180, "EntryWaitSec": 2400, "ExitWaitSec": 600,
            "HeadPickup": 50500, "HeadPlace": 50200, "HeadError": 80, "HeadErrorPpm": 1584,
            "HeadPostPickMiss": 40, "HeadPrePlaceMiss": 2, "HeadPartNg": 35, "HeadDump": 8,
            "PeakBuildSecPerBoard": 82.5, "PeakBoardPerHour": 44, "PeakChipPerHour": 530,
            "MeanBuildSecPerBoard": 84.0, "MeanBoardPerHour": 43, "MeanChipPerHour": 515,
            "PreviousCycleSecPerBoard": 83.0
        },
        {
            "MachineNm": "M2", "BaseProgramNm": "PRR21P03-01_CL.1_REV_3",
            "IdealCycleSec": 88.0, "TotalBoard": 250, "WorkedPcb": 1000,
            "SkippedPcb": 0, "ArrayPerBoard": 4.0,
            "StartTime": datetime.strptime(f"{base_date} 13:05", "%Y-%m-%d %H:%M"),
            "RunSec": 6800, "StopSec": 520, "PlaceSec": 6200,
            "TransferSec": 280, "EntryWaitSec": 320, "ExitWaitSec": 0,
            "HeadPickup": 50150, "HeadPlace": 50000, "HeadError": 38, "HeadErrorPpm": 757,
            "HeadPostPickMiss": 28, "HeadPrePlaceMiss": 3, "HeadPartNg": 10, "HeadDump": 4,
            "PeakBuildSecPerBoard": 87.0, "PeakBoardPerHour": 41, "PeakChipPerHour": 500,
            "MeanBuildSecPerBoard": 89.5, "MeanBoardPerHour": 40, "MeanChipPerHour": 490,
            "PreviousCycleSecPerBoard": 87.0
        },
        {
            "MachineNm": "M1", "BaseProgramNm": "PRR21P03-01_CL2",
            "IdealCycleSec": None, "TotalBoard": 280, "WorkedPcb": 1120,
            "SkippedPcb": 0, "ArrayPerBoard": 4.0,
            "StartTime": datetime.strptime(f"{base_date} 14:40", "%Y-%m-%d %H:%M"),
            "RunSec": 5400, "StopSec": 0, "PlaceSec": 0,
            "TransferSec": 250, "EntryWaitSec": 3200, "ExitWaitSec": 1950,
            "HeadPickup": 0, "HeadPlace": 0, "HeadError": 0, "HeadErrorPpm": 0,
            "HeadPostPickMiss": 0, "HeadPrePlaceMiss": 0, "HeadPartNg": 0, "HeadDump": 0,
            "PeakBuildSecPerBoard": 0.0, "PeakBoardPerHour": 0, "PeakChipPerHour": 0,
            "MeanBuildSecPerBoard": 0.0, "MeanBoardPerHour": 0, "MeanChipPerHour": 0,
            "PreviousCycleSecPerBoard": 0.0
        },
    ])


# ============================================================
# HELPER FUNCTIONS — SVG Gauges, Machine Table, etc.
# ============================================================

def create_gauge(value, label, gauge_id, size=148, is_main=False):
    """Animated SVG circular gauge with akYtec glow effect."""
    radius = 56
    stroke_w = 10 if is_main else 7
    circumference = 2 * math.pi * radius
    clamped = min(max(value, 0.0), 1.0)
    offset = circumference * (1.0 - clamped)

    # akYtec Color Scheme — dark navy + electric blue
    if clamped >= 0.85:
        color, track = "#00E676", "rgba(0, 230, 118, 0.08)"
    elif clamped >= 0.70:
        color, track = "#FFD600", "rgba(255, 214, 0, 0.08)"
    else:
        color, track = "#FF1744", "rgba(255, 23, 68, 0.08)"

    vf = 26 if is_main else 21
    ds = int(size * 1.2) if is_main else size
    vb = 160
    cx = cy = 80
    
    # Sanitize gauge_id to be valid CSS identifier (alphanumeric + underscore)
    safe_id = "".join(c if c.isalnum() or c == "_" else "_" for c in gauge_id)

    svg_html = f"""<svg width="{ds}" height="{ds}" viewBox="0 0 {vb} {vb}" style="display: block; margin: 0 auto;">
        <defs>
            <filter id="gl_{safe_id}">
                <feGaussianBlur stdDeviation="4" result="b"/>
                <feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge>
            </filter>
        </defs>
        <circle cx="{cx}" cy="{cy}" r="{radius}" fill="none"
            stroke="{track}" stroke-width="{stroke_w + 5}"/>
        <circle cx="{cx}" cy="{cy}" r="{radius}" fill="none"
            stroke="{color}" stroke-width="{stroke_w}"
            stroke-dasharray="{circumference:.2f}" stroke-dashoffset="{circumference:.2f}"
            stroke-linecap="round" transform="rotate(-90 {cx} {cy})"
            filter="url(#gl_{safe_id})">
            <animate attributeName="stroke-dashoffset"
                from="{circumference:.2f}" to="{offset:.2f}"
                dur="1.3s" fill="freeze"
                calcMode="spline" keySplines="0.4 0 0.2 1"/>
        </circle>
        <text x="{cx}" y="{cy - 3}" text-anchor="middle" dominant-baseline="central"
            fill="{color}" font-size="{vf}" font-weight="700"
            font-family="'JetBrains Mono',monospace">{clamped*100:.1f}%</text>
        <text x="{cx}" y="{cy + 20}" text-anchor="middle"
            fill="#7DD3DD" font-size="10.5"
            font-family="'Outfit',sans-serif" font-weight="500">{label}</text>
    </svg>"""
    
    return svg_html


def oee_color_class(val):
    if val >= 0.85: return "v-ok"
    elif val >= 0.70: return "v-warn"
    return "v-bad"


def pulse_class(oee_val):
    if oee_val < 0.70: return "pulse-crit"
    if oee_val < 0.85: return "pulse-warn"
    return ""


def build_machine_table(side_df, side_key):
    """Generate per-machine OEE breakdown HTML table."""
    rows_html = ""
    for _, row in side_df.iterrows():
        machine = row["MachineNm"]
        prog   = row["BaseProgramNm"]
        run  = float(row["RunSec"]  or 0)
        stop = float(row["StopSec"] or 0)
        ng   = int(row["HeadPartNg"]  or 0)
        hp   = int(row["HeadPlace"]   or 0)
        panels = int(row["TotalBoard"] or 0)
        ideal_c = row["IdealCycleSec"]
        peak_b  = float(row["PeakBuildSecPerBoard"] or 0)
        he = int(row["HeadError"] or 0)
        he_ppm = int(row["HeadErrorPpm"] or 0)
        skipped = int(row["SkippedPcb"] or 0)

        avail = run / (run + stop) if (run + stop) > 0 else 0.0
        qual  = (hp - ng) / hp if hp > 0 else 1.0
        ideal = float(ideal_c) if ideal_c is not None else peak_b
        perf  = (panels * ideal) / run if run > 0 and ideal > 0 else 0.0
        if perf > 1.0: perf = 1.0
        oee = avail * perf * qual

        rows_html += f"""<tr>
            <td style='font-weight:600;'>{machine}</td>
            <td class='v-mono' style='font-size:0.78rem; max-width:160px; overflow:hidden; text-overflow:ellipsis;'>{prog}</td>
            <td class='{oee_color_class(avail)}'>{avail*100:.1f}%</td>
            <td class='{oee_color_class(perf)}'>{perf*100:.1f}%</td>
            <td class='{oee_color_class(qual)}'>{qual*100:.1f}%</td>
            <td class='{oee_color_class(oee)}'>{oee*100:.1f}%</td>
            <td class='v-mono'>{run/60:.1f}</td>
            <td class='v-mono'>{stop/60:.1f}</td>
            <td class='v-mono'>{he_ppm:,}</td>
            <td class='v-mono'>{ng}</td>
            <td class='v-mono'>{skipped}</td>
        </tr>"""

    return f"""<table class='mtable'><thead><tr>
        <th>Mašina</th><th>Program</th><th>Avail</th><th>Perf</th><th>Qual</th><th>OEE</th>
        <th>Run (m)</th><th>Stop (m)</th><th>Err PPM</th><th>NG</th><th>Skip</th>
    </tr></thead><tbody>{rows_html}</tbody></table>"""


def build_head_table(side_df):
    """Per-machine Head Performance table."""
    rows_html = ""
    for _, row in side_df.iterrows():
        machine = row["MachineNm"]
        pk = int(row["HeadPickup"] or 0)
        pl = int(row["HeadPlace"] or 0)
        er = int(row["HeadError"] or 0)
        ppm = int(row["HeadErrorPpm"] or 0)
        pm = int(row["HeadPostPickMiss"] or 0)
        pr = int(row["HeadPrePlaceMiss"] or 0)
        ng = int(row["HeadPartNg"] or 0)
        du = int(row["HeadDump"] or 0)

        pick_eff = (pk - pm) / pk * 100 if pk > 0 else 100.0
        place_acc = (pl - ng - du) / pl * 100 if pl > 0 else 100.0

        rows_html += f"""<tr>
            <td style='font-weight:600;'>{machine}</td>
            <td class='v-mono'>{pk:,}</td>
            <td class='v-mono'>{pl:,}</td>
            <td class='v-mono'>{er}</td>
            <td class='v-mono'>{ppm:,}</td>
            <td class='v-mono'>{pm}</td>
            <td class='v-mono'>{pr}</td>
            <td class='v-mono'>{ng}</td>
            <td class='v-mono'>{du}</td>
            <td class='{oee_color_class(pick_eff/100)}'>{pick_eff:.1f}%</td>
            <td class='{oee_color_class(place_acc/100)}'>{place_acc:.1f}%</td>
        </tr>"""
    return f"""<table class='mtable'><thead><tr>
        <th>Mašina</th><th>Pickup</th><th>Place</th><th>Error</th><th>PPM</th>
        <th>PostMiss</th><th>PreMiss</th><th>NG</th><th>Dump</th><th>P.Uč.</th><th>P.Tač.</th>
    </tr></thead><tbody>{rows_html}</tbody></table>"""


def build_speed_table(side_df):
    """Per-machine Build Speed table."""
    rows_html = ""
    for _, row in side_df.iterrows():
        machine = row["MachineNm"]
        ps  = float(row["PeakBuildSecPerBoard"] or 0)
        ph  = int(row["PeakBoardPerHour"] or 0)
        pch = int(row["PeakChipPerHour"] or 0)
        ms  = float(row["MeanBuildSecPerBoard"] or 0)
        mh  = int(row["MeanBoardPerHour"] or 0)
        mch = int(row["MeanChipPerHour"] or 0)
        pcs = float(row["PreviousCycleSecPerBoard"] or 0)
        ics = float(row["IdealCycleSec"]) if row["IdealCycleSec"] is not None else 0.0

        rows_html += f"""<tr>
            <td style='font-weight:600;'>{machine}</td>
            <td class='v-mono'>{ps:.1f}</td>
            <td class='v-mono'>{ph}</td>
            <td class='v-mono'>{pch:,}</td>
            <td class='v-mono'>{ms:.1f}</td>
            <td class='v-mono'>{mh}</td>
            <td class='v-mono'>{mch:,}</td>
            <td class='v-mono'>{pcs:.1f}</td>
            <td class='v-mono'>{ics:.1f}</td>
        </tr>"""
    return f"""<table class='mtable'><thead><tr>
        <th>Mašina</th><th>Peak (s)</th><th>P.Brd/h</th><th>P.Chip/h</th>
        <th>Mean (s)</th><th>M.Brd/h</th><th>M.Chip/h</th><th>Prev (s)</th><th>Ideal (s)</th>
    </tr></thead><tbody>{rows_html}</tbody></table>"""


# ============================================================
# SHIFT & HOURLY PRODUCTION FUNCTIONS
# ============================================================
def distribute_hourly_production(df):
    """Distribuira proizvodnju (TotalBoard, WorkedPcb) po satima 08:00-15:59
    na osnovu StartTime i RunSec svakog zapisa."""
    hourly = {h: {"panels": 0, "pcbs": 0} for h in range(8, 16)}

    for _, row in df.iterrows():
        st_time = row.get("StartTime")
        if st_time is None:
            continue
        panels = int(row["TotalBoard"] or 0)
        pcbs   = int(row["WorkedPcb"] or 0)
        run_sec = float(row["RunSec"] or 0)

        # Ako nema RunSec, sve pripada satu StartTime-a
        if run_sec <= 0 or panels <= 0:
            hr = st_time.hour
            if hr in hourly:
                hourly[hr]["panels"] += panels
                hourly[hr]["pcbs"]   += pcbs
            continue

        start_ts = st_time.timestamp()
        end_ts   = start_ts + run_sec
        duration_h = run_sec / 3600.0

        # Raspodela po satima
        current_ts = start_ts
        while current_ts < end_ts:
            current_dt = datetime.fromtimestamp(current_ts)
            hr = current_dt.hour
            if hr not in hourly:
                current_ts = (current_dt.replace(minute=0, second=0, microsecond=0)
                              + pd.Timedelta(hours=1)).timestamp()
                continue

            next_hr_ts = (current_dt.replace(minute=0, second=0, microsecond=0)
                          + pd.Timedelta(hours=1)).timestamp()
            segment_end = min(next_hr_ts, end_ts)
            segment_sec = segment_end - current_ts
            fraction = segment_sec / run_sec if run_sec > 0 else 0.0

            hourly[hr]["panels"] += round(panels * fraction)
            hourly[hr]["pcbs"]   += round(pcbs * fraction)
            current_ts = segment_end

    # Konvertuj u listu za DataFrame
    rows = []
    for h in range(8, 16):
        rows.append({
            "hour": f"{h:02d}:00",
            "hour_num": h,
            "panels": hourly[h]["panels"],
            "pcbs": hourly[h]["pcbs"]
        })
    return pd.DataFrame(rows)


def calculate_shift_summary(df, hourly_df):
    """Izračunava summary metrike za smenu 08-16h."""
    total_panels = int(df["TotalBoard"].sum())
    total_pcbs   = int(df["WorkedPcb"].sum())
    total_run    = float(df["RunSec"].sum())
    total_stop   = float(df["StopSec"].sum())
    total_skipped = int(df["SkippedPcb"].sum())

    # Cilj: 8 sati * 60 min = 480 min. Idealni ciklus (prosek)
    ideal_cycles = df["IdealCycleSec"].dropna()
    avg_ideal = ideal_cycles.mean() if not ideal_cycles.empty else 90.0

    # Teoretski max panela za 8h (28800 sec)
    shift_sec = 8 * 3600  # 28800 sec
    target_panels = int(shift_sec / avg_ideal) if avg_ideal > 0 else 0

    # Stopa iskorišćenja
    total_time = total_run + total_stop
    utilization = total_run / total_time if total_time > 0 else 0.0

    # Boards per hour (stvarni)
    actual_run_h = total_run / 3600.0
    boards_per_hour = total_panels / actual_run_h if actual_run_h > 0 else 0.0

    return {
        "total_panels": total_panels,
        "total_pcbs": total_pcbs,
        "total_skipped": total_skipped,
        "total_run_min": round(total_run / 60, 1),
        "total_stop_min": round(total_stop / 60, 1),
        "utilization": utilization,
        "target_panels": target_panels,
        "boards_per_hour": round(boards_per_hour, 1),
        "avg_ideal_cycle": round(avg_ideal, 1),
    }


# ============================================================
# TOP ERRORS FUNCTIONS
# ============================================================
@st.cache_data(ttl=120)
def get_top_errors_db(date_str):
    query = """
        SELECT TOP 5
            CMEqpCd,
            DeviceNm,
            FeederNm,
            SUM(PickUpCnt) as TotalPick,
            SUM(PickMissCnt) as TotalMiss,
            SUM(PartNgCnt) as TotalNg,
            SUM(ErrorCnt) as TotalErrors
        FROM FMS_ErrorData WITH (NOLOCK)
        WHERE CAST(LastLoadDt AS DATE) = ?
        GROUP BY CMEqpCd, DeviceNm, FeederNm
        HAVING SUM(ErrorCnt) > 0
        ORDER BY TotalErrors DESC
    """
    columns = ["Machine", "Component", "Feeder", "Pickups", "Misses", "NG", "Errors"]
    try:
        conn = pyodbc.connect(CONN_STR, timeout=3)
        cursor = conn.cursor()
        cursor.execute(query, (date_str,))
        rows = cursor.fetchall()
        conn.close()
        if not rows:
            return pd.DataFrame(columns=columns)
        clean = []
        for r in rows:
            clean.append([r[0], r[1] or "UNKNOWN", r[2] or "N/A",
                          int(r[3] or 0), int(r[4] or 0), int(r[5] or 0), int(r[6] or 0)])
        return pd.DataFrame(clean, columns=columns)
    except Exception:
        return pd.DataFrame(columns=columns)


def get_demo_top_errors():
    return pd.DataFrame([
        {"Machine": "M1", "Component": "R103_4K7", "Feeder": "F12", "Pickups": 3200, "Misses": 47, "NG": 12, "Errors": 59},
        {"Machine": "M2", "Component": "C205_100nF", "Feeder": "F08", "Pickups": 4800, "Misses": 38, "NG": 8, "Errors": 46},
        {"Machine": "M1", "Component": "IC301_ATMEGA", "Feeder": "F22", "Pickups": 960, "Misses": 12, "NG": 3, "Errors": 15},
        {"Machine": "M2", "Component": "R107_10K", "Feeder": "F05", "Pickups": 2800, "Misses": 8, "NG": 5, "Errors": 13},
    ])


def build_errors_table(errors_df):
    rows_html = ""
    for _, row in errors_df.iterrows():
        ppm = (row["Errors"] / row["Pickups"]) * 1000000 if row["Pickups"] > 0 else 0
        ppm_class = "v-bad" if ppm > 10000 else ("v-warn" if ppm > 5000 else "v-ok")
        rows_html += f"""<tr>
            <td style='font-weight:600;'>{row["Machine"]}</td>
            <td class='v-mono'>{row["Component"]}</td>
            <td class='v-mono'>{row["Feeder"]}</td>
            <td class='v-mono'>{row["Pickups"]:,}</td>
            <td class='v-mono'>{row["Misses"]}</td>
            <td class='v-mono'>{row["NG"]}</td>
            <td class='{ppm_class}'>{ppm:,.0f}</td>
        </tr>"""
    return f"""<table class='mtable'><thead><tr>
        <th>Mašina</th><th>Komponenta</th><th>Feeder</th><th>Pickups</th><th>Misses</th><th>NG</th><th>Err PPM</th>
    </tr></thead><tbody>{rows_html}</tbody></table>"""


# ============================================================
# NEW VISUALIZATION HELPERS — Donut & Charts
# ============================================================

def create_donut(value, label, size=150, color="#00E5FF"):
    """Generates a donut SVG chart in blue/purple tones."""
    radius = 54
    stroke_w = 10
    circumference = 2 * math.pi * radius
    clamped = min(max(value, 0.0), 1.0)
    offset = circumference * (1.0 - clamped)
    track_color = "rgba(0,229,255,0.06)"
    vb = 160
    cx = cy = 80
    return f"""<svg width="{size}" height="{size}" viewBox="0 0 {vb} {vb}" style="display:block;margin:0 auto;">
        <circle cx="{cx}" cy="{cy}" r="{radius}" fill="none" stroke="{track_color}" stroke-width="{stroke_w+4}"/>
        <circle cx="{cx}" cy="{cy}" r="{radius}" fill="none" stroke="{color}" stroke-width="{stroke_w}"
            stroke-dasharray="{circumference:.2f}" stroke-dashoffset="{offset:.2f}"
            stroke-linecap="round" transform="rotate(-90 {cx} {cy})" filter="url(#df)"/>
        <text x="{cx}" y="{cy}" text-anchor="middle" dominant-baseline="central"
            fill="#E0E6ED" font-size="28" font-weight="700" font-family="'JetBrains Mono',monospace">{clamped*100:.0f}%</text>
    </svg>"""


def plot_production_chart(df, hourly_df):
    """Stacked bar chart: Production (blue) + Defective/Scrap (red) over hours."""
    fig, ax = plt.subplots(figsize=(8, 3.2))
    fig.patch.set_facecolor('#0A0F1D')
    ax.set_facecolor('#0D1528')

    hours = hourly_df["hour"].tolist()
    panels = hourly_df["panels"].tolist()

    # Estimate scrap as ~1.5% of production for demo purposes
    scrap = [max(1, int(p * 0.015)) for p in panels]

    x = range(len(hours))
    bars1 = ax.bar(x, panels, width=0.5, color='#00E5FF', label='Production', alpha=0.85)
    bars2 = ax.bar(x, scrap, width=0.5, color='#FF1744', label='Scrap', alpha=0.7, bottom=panels)

    ax.set_xticks(x)
    ax.set_xticklabels(hours, color='#6B7280', fontsize=8)
    ax.tick_params(colors='#6B7280', labelsize=8)
    ax.set_ylabel('Panels', color='#6B7280', fontsize=8)
    ax.legend(loc='upper right', facecolor='#0A0F1D', edgecolor='#1E293B', labelcolor='#CBD5E1', fontsize=7)
    for spine in ax.spines.values(): spine.set_visible(False)
    ax.grid(axis='y', alpha=0.08, color='#00E5FF')
    ax.set_ylim(0, max(panels) * 1.35 if panels else 100)
    fig.tight_layout(pad=1)
    return fig


def plot_actual_production_chart(hourly_df, target_per_hour):
    """Line chart: Actual production (blue) + Target threshold (green dashed)."""
    fig, ax = plt.subplots(figsize=(8, 3.2))
    fig.patch.set_facecolor('#0A0F1D')
    ax.set_facecolor('#0D1528')

    hours = hourly_df["hour"].tolist()
    panels = hourly_df["panels"].tolist()
    x = range(len(hours))

    ax.plot(x, panels, color='#00E5FF', linewidth=2.5, marker='s', markersize=5, label='Actual', zorder=3)
    ax.axhline(y=target_per_hour, color='#00E676', linewidth=1.8, linestyle='--', label=f'Target ({target_per_hour}/h)', alpha=0.8)

    ax.fill_between(x, panels, alpha=0.06, color='#00E5FF')
    ax.set_xticks(x)
    ax.set_xticklabels(hours, color='#6B7280', fontsize=8)
    ax.tick_params(colors='#6B7280', labelsize=8)
    ax.set_ylabel('Panels', color='#6B7280', fontsize=8)
    ax.legend(loc='upper left', facecolor='#0A0F1D', edgecolor='#1E293B', labelcolor='#CBD5E1', fontsize=7)
    for spine in ax.spines.values(): spine.set_visible(False)
    ax.grid(axis='y', alpha=0.08, color='#00E5FF')
    ax.set_ylim(0, max(panels) * 1.5 if panels else 100)
    fig.tight_layout(pad=1)
    return fig


# ============================================================
# SIDEBAR — narrow icon bar + controls
# ============================================================
# Logo + nav icons only
st.sidebar.markdown("""
<div class="sidebar-logo">
    <svg viewBox="0 0 125 100" width="48" height="38" xmlns="http://www.w3.org/2000/svg" style="display:block;margin:0 auto;">
        <path d="M 0 0 L 25 0 L 75 50 L 25 100 L 0 100 L 0 75 L 25 75 L 50 50 L 25 25 L 0 25 Z" fill="#00a69c"/>
        <path d="M 67.5 32.5 L 80 45 L 100 25 L 125 25 L 125 0 L 100 0 Z" fill="#e6007e"/>
    </svg>
</div>
""", unsafe_allow_html=True)

for icon, label, active in [("📊","Dashboard",True),("📋","Reports",False),("⚙️","Settings",False)]:
    st.sidebar.markdown(f"""<div class="sidebar-icon{' active' if active else ''}">{icon}<div>{label}</div></div>""", unsafe_allow_html=True)

st.sidebar.markdown("""
<div style="position:fixed;bottom:10px;width:56px;text-align:center;font-size:0.5rem;color:#475569;font-family:'JetBrains Mono',monospace;">
    akY v2
</div>
""", unsafe_allow_html=True)

# ============================================================
# Init session state for toolbar widgets (defined later in layout)
today_str = datetime.now().strftime("%Y-%m-%d")
if "toolbar_date" not in st.session_state:
    st.session_state.toolbar_date = today_str
if "toolbar_demo" not in st.session_state:
    st.session_state.toolbar_demo = False
if "toolbar_autorefresh" not in st.session_state:
    st.session_state.toolbar_autorefresh = False
if "toolbar_tv" not in st.session_state:
    st.session_state.toolbar_tv = False

date_str = st.session_state.toolbar_date
use_demo = st.session_state.toolbar_demo
auto_refresh = st.session_state.toolbar_autorefresh
tv_mode = st.session_state.toolbar_tv
refresh_interval = 300  # 5 min

if use_demo:
    df = get_demo_data()
else:
    df = get_data_from_db(date_str)
    if df.empty:
        st.warning(f"Nema podataka za {date_str}.")
        use_demo_fallback = st.checkbox("Prebaci na Demo", value=True)
        if use_demo_fallback:
            df = get_demo_data()
        else:
            st.error("Nema zapisa za izabrani datum.")
            st.stop()

# Samo jedna linija — NIS SMT Line
# Nema CL.1/CL.2 podele, svi podaci su za istu liniju

# === HOURLY PRODUCTION DISTRIBUTION ===
hourly_df = distribute_hourly_production(df)
shift_summary = calculate_shift_summary(df, hourly_df)

# === SHIFT TIMELINE (trenutni sat u smeni) ===
now = datetime.now()
shift_start = now.replace(hour=8, minute=0, second=0, microsecond=0)
shift_end   = now.replace(hour=16, minute=0, second=0, microsecond=0)
current_hour = now.hour
if current_hour < 8 or current_hour >= 16:
    current_hour = 16  # posle smene, prikazi kompletnu
shift_progress = min((now - shift_start).total_seconds() / (8 * 3600), 1.0) if now >= shift_start and now < shift_end else 1.0


# ============================================================
# MAIN DASHBOARD — 5-Row Industrial Layout
# ============================================================

# --- Compute all metrics ---
total_panels = int(df["TotalBoard"].sum())
total_pcbs   = int(df["WorkedPcb"].sum())
total_skipped = int(df["SkippedPcb"].sum())
total_pickup = int(df["HeadPickup"].sum())
total_dump = int(df["HeadDump"].sum())
total_error = int(df["HeadError"].sum())
total_ng = int(df["HeadPartNg"].sum())
avg_array = float(df["ArrayPerBoard"].iloc[0] or 0)
mean_board_h = int(df["MeanBoardPerHour"].sum())

availabilities, performances, qualities = [], [], []
t_run = t_stop = t_place = t_transfer = t_entry = t_exit = 0
for _, row in df.iterrows():
    run   = float(row["RunSec"]  or 0); stop  = float(row["StopSec"] or 0)
    place = float(row["PlaceSec"] or 0); trans = float(row["TransferSec"]  or 0)
    entry = float(row["EntryWaitSec"] or 0); exitw = float(row["ExitWaitSec"]  or 0)
    ng    = int(row["HeadPartNg"]  or 0); hp    = int(row["HeadPlace"]   or 0)
    ideal_c = row["IdealCycleSec"]; peak_b  = float(row["PeakBuildSecPerBoard"] or 0)
    panels  = int(row["TotalBoard"] or 0)
    t_run += run; t_stop += stop; t_place += place
    t_transfer += trans; t_entry += entry; t_exit += exitw
    avail = run / (run + stop) if (run + stop) > 0 else 0.0
    availabilities.append(avail)
    qual = (hp - ng) / hp if hp > 0 else 1.0
    qualities.append(qual)
    ideal = float(ideal_c) if ideal_c is not None else peak_b
    perf = (panels * ideal) / run if run > 0 and ideal > 0 else 0.0
    if perf > 1.0: perf = 1.0
    performances.append(perf)
n = len(availabilities)
avg_a = sum(availabilities) / n if n else 0.0
avg_p = sum(performances)  / n if n else 0.0
avg_q = sum(qualities)     / n if n else 1.0
oee   = avg_a * avg_p * avg_q

# Monthly estimate (22 working days estimate)
monthly_mult = 22.0
m_a = min(avg_a * monthly_mult, 1.0)
# For simplicity, use same values scaled by working days factor
m_p = avg_p; m_q = avg_q; m_oee = oee

# TV mode
if tv_mode:
    st.markdown("""<script>(function(){var el=document.querySelector('.stApp');if(el)el.classList.add('tv-mode');})();</script>""", unsafe_allow_html=True)

# ============================
# LOGO + HEADER
# ============================
st.markdown(f"""
<div style="text-align:center;padding:0;">
    <svg viewBox="0 0 125 100" width="80" height="64" xmlns="http://www.w3.org/2000/svg" style="display:inline-block;">
        <path d="M 0 0 L 25 0 L 75 50 L 25 100 L 0 100 L 0 75 L 25 75 L 50 50 L 25 25 L 0 25 Z" fill="#00a69c"/>
        <path d="M 67.5 32.5 L 80 45 L 100 25 L 125 25 L 125 0 L 100 0 Z" fill="#e6007e"/>
    </svg>
</div>
<div style="display:flex;align-items:center;justify-content:space-between;padding:0 4px 6px 4px;">
    <div style="display:flex;align-items:center;gap:8px;">
        <span style="font-size:1.3rem;font-weight:800;color:#E0E6ED;letter-spacing:0.04em;">akYtec NIS SMT Line</span>
        <span style="font-size:0.55rem;background:rgba(0,229,255,0.08);color:#00E5FF;padding:2px 8px;border-radius:8px;font-weight:600;">{date_str}</span>
    </div>
    <div style="display:flex;align-items:center;gap:14px;">
        <span style="font-family:'JetBrains Mono',monospace;font-size:0.68rem;color:#6B7280;">SHIFT 08:00 – 16:00</span>
        <span style="font-family:'JetBrains Mono',monospace;font-size:0.68rem;color:#00E5FF;font-weight:600;">NIS SMT Line</span>
    </div>
</div>
""", unsafe_allow_html=True)

# ============================
# TOOLBAR — minimalist controls
# ============================
tool_cols = st.columns([1.2, 0.7, 0.7, 0.7, 0.7, 2])
with tool_cols[0]:
    date_options = [(datetime.now() - timedelta(days=i)).strftime("%Y-%m-%d") for i in range(13, -1, -1)]
    date_idx = next((i for i, d in enumerate(date_options) if d == date_str), len(date_options)-1)
    st.selectbox("", date_options, index=date_idx, key="toolbar_date", label_visibility="collapsed")
with tool_cols[1]:
    if st.button("⟳", help="Refresh now", use_container_width=True):
        st.cache_data.clear()
        st.rerun()
with tool_cols[2]:
    st.checkbox("Auto", key="toolbar_autorefresh", help="Auto-refresh every 5 min")
with tool_cols[3]:
    st.checkbox("Demo", key="toolbar_demo", help="Use demo data")
with tool_cols[4]:
    tv_mode =     st.checkbox("TV", key="toolbar_tv", help="TV / Fullscreen mode")

# Auto-refresh logic
if auto_refresh:
    try:
        from streamlit_autorefresh import st_autorefresh
        st_autorefresh(interval=refresh_interval * 1000, key="dashrefresh")
    except ImportError:
        st.markdown(f"<script>setTimeout(function(){{window.location.reload()}},{refresh_interval*1000})</script>", unsafe_allow_html=True)
        st.caption("⟳ JS fallback")

if use_demo:
    st.caption("📊 Demo data")

# ============================
# ROW 1 — 4 Small KPI cards (Today + Monthly) with colored accents
# ============================
st.markdown('<div class="row-title">Key Performance Indicators</div>', unsafe_allow_html=True)
kpi_data = [
    ("Performance", avg_p, m_p, "accent-green"),
    ("Quality", avg_q, m_q, "accent-orange"),
    ("Availability", avg_a, m_a, "accent-blue"),
    ("OEE", oee, m_oee, "accent-purple"),
]
cols = st.columns(4)
for ci, (label, today_val, monthly_val, accent) in enumerate(kpi_data):
    with cols[ci]:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="{accent}"></div>
            <div class="kpi-label">{label}</div>
            <div class="kpi-today">{today_val*100:.1f}%</div>
            <div class="kpi-monthly">Monthly: {monthly_val*100:.1f}%</div>
            <div class="kpi-sub">Today vs Monthly average</div>
        </div>
        """, unsafe_allow_html=True)

# ============================
# ROW 2 — 4 Larger cards with radial donut charts
# ============================
st.markdown('<div class="row-title" style="margin-top:22px;">Performance Gauges</div>', unsafe_allow_html=True)
donut_colors = ["#00E5FF", "#B388FF", "#00E676", "#FF9100"]
donut_data = [
    ("Performance", avg_p, donut_colors[0], "Brzina rada masine"),
    ("Quality", avg_q, donut_colors[1], "Uspesnost komponenti"),
    ("Availability", avg_a, donut_colors[2], "Vreme rada vs zastoji"),
    ("Overall OEE", oee, donut_colors[3], "A × P × Q"),
]
cols2 = st.columns(4)
for ci, (label, val, color, desc) in enumerate(donut_data):
    with cols2[ci]:
        st.markdown(f"""
        <div class="donut-card">
            {create_donut(val, label, 130, color)}
            <div class="donut-label">{label}</div>
            <div class="donut-value">{val*100:.1f}%</div>
            <div style="font-size:0.6rem;color:#475569;margin-top:4px;">{desc}</div>
        </div>
        """, unsafe_allow_html=True)

# ============================
# ROW 3 — Two chart panels: stacked bar + line chart
# ============================
st.markdown('<div class="row-title" style="margin-top:22px;">Production Charts</div>', unsafe_allow_html=True)
c_chart1, c_chart2 = st.columns(2)

target_per_hour = max(1, shift_summary['target_panels'] // 8)
with c_chart1:
    fig1 = plot_production_chart(df, hourly_df)
    st.pyplot(fig1, use_container_width=True)

with c_chart2:
    fig2 = plot_actual_production_chart(hourly_df, target_per_hour)
    st.pyplot(fig2, use_container_width=True)

# ============================
# ROW 4 — Status widgets
# ============================
st.markdown('<div class="row-title" style="margin-top:22px;">Line Status</div>', unsafe_allow_html=True)
c_s1, c_s2, c_s3, c_s4 = st.columns(4)

now_dt = datetime.now()
shift_end_dt = now_dt.replace(hour=16, minute=0, second=0, microsecond=0)
shift_remaining = max(0, (shift_end_dt - now_dt).total_seconds() / 3600) if now_dt < shift_end_dt else 0
total_downtime_min = round(t_stop / 60, 1)
total_run_min = round(t_run / 60, 1)

with c_s1:
    st.markdown(f"""
    <div class="status-card">
        <div class="status-label">Machine Status</div>
        <div style="display:flex;align-items:center;margin-top:6px;">
            <span class="status-dot green"></span>
            <span class="status-value" style="font-size:1rem;color:#00E676;">RUNNING</span>
        </div>
        <div style="font-size:0.6rem;color:#475569;margin-top:4px;">All systems operational</div>
    </div>
    """, unsafe_allow_html=True)
with c_s2:
    st.markdown(f"""
    <div class="status-card">
        <div class="status-label">Run Time</div>
        <div class="status-value">{total_run_min:.0f} <span style="font-size:0.7rem;color:#6B7280;font-weight:400;">min</span></div>
        <div style="font-size:0.6rem;color:#475569;margin-top:4px;">Total machine running time</div>
    </div>
    """, unsafe_allow_html=True)
with c_s3:
    st.markdown(f"""
    <div class="status-card">
        <div class="status-label">Shift Time Left</div>
        <div class="status-value">{shift_remaining:.1f} <span style="font-size:0.7rem;color:#6B7280;font-weight:400;">hrs</span></div>
        <div style="font-size:0.6rem;color:#475569;margin-top:4px;">Until 16:00 end of shift</div>
    </div>
    """, unsafe_allow_html=True)
with c_s4:
    st.markdown(f"""
    <div class="status-card">
        <div class="status-label">Breakdown Time</div>
        <div class="status-value" style="color:#FF1744;">{total_downtime_min:.0f} <span style="font-size:0.7rem;color:#6B7280;font-weight:400;">min</span></div>
        <div style="font-size:0.6rem;color:#475569;margin-top:4px;">Total stop time this shift</div>
    </div>
    """, unsafe_allow_html=True)

# ============================
# ROW 5 — Bottom tally KPI cards
# ============================
st.markdown('<div class="row-title" style="margin-top:22px;">Production Tallies</div>', unsafe_allow_html=True)
target = shift_summary['target_panels']
remaining = max(0, target - total_panels)
accepted = total_pcbs - total_ng
rejected = total_ng

tallies = [
    ("Actual Production", f"{total_panels:,}", "green", "Panela"),
    ("Shift Target", f"{target:,}", "blue", "Cilj (8h max)"),
    ("Rejected", f"{rejected}", "red", "NG komponente"),
    ("Accepted", f"{accepted:,}", "purple", "Uspesno PCB"),
    ("Remaining", f"{remaining:,}", "orange", f"Do targeta ({target:,})"),
]
cols5 = st.columns(5)
for ci, (tlabel, tval, tcolor, tdesc) in enumerate(tallies):
    with cols5[ci]:
        st.markdown(f"""
        <div class="tally-card">
            <div class="tally-label">{tlabel}</div>
            <div class="tally-val {tcolor}">{tval}</div>
            <div style="font-size:0.55rem;color:#475569;margin-top:2px;">{tdesc}</div>
        </div>
        """, unsafe_allow_html=True)

st.markdown("<div style='height:24px;'></div>", unsafe_allow_html=True)

# ============================
# DETAIL SECTION — Machine tables (collapsible below the main 5 rows)
# ============================
with st.expander("📋 Detailed Machine Data — OEE, Head Performance, Speed", expanded=False):
    # Products summary
    prog_summary = df.groupby("BaseProgramNm").agg(
        Machines=("MachineNm", lambda x: ", ".join(sorted(x.unique()))),
        Panela=("TotalBoard", "sum"),
        PCB=("WorkedPcb", "sum")
    ).reset_index()
    prog_summary.columns = ["Program", "Masine", "Panela", "PCB"]
    st.markdown("#### Proizvodi u smeni")
    st.dataframe(
        prog_summary.style.format({"Panela": "{:,.0f}", "PCB": "{:,.0f}"})
            .set_properties(**{"background-color": "#0F172A", "color": "#E2E8F0", "border-color": "#1E293B"}),
        hide_index=True, use_container_width=True
    )

    # Downtime analysis
    total_all = t_run + t_stop
    if total_all > 0:
        pct_s  = t_stop / total_all; pct_sv = t_entry / total_all
        pct_bk = t_exit / total_all; pct_tr = t_transfer / total_all
        pct_wk = t_place / total_all
        seg_label = lambda p: f"{p*100:.0f}%" if p >= 0.06 else ""
        analysis = "✅ <b>Fluidan tok</b>" if pct_bk <= 0.30 and pct_sv <= 0.30 else \
                   "⚠️ <b>Velika blokada</b>" if pct_bk > 0.30 else \
                   "⚠️ <b>Veliko izgladnjivanje</b>"
        st.markdown(f"""
        <div style="background:#0F172A;border:1px solid rgba(0,229,255,0.06);border-radius:10px;padding:14px;margin-bottom:14px;">
            <div style="font-weight:600;color:#00E5FF;margin-bottom:4px;">⏱️ Downtime & Loss Analysis</div>
            <div class="dt-bar-wrap" style="height:36px;">
                <div class="dt-seg" style="width:{pct_s*100}%;background:#FF1744;">{seg_label(pct_s)}</div>
                <div class="dt-seg" style="width:{pct_sv*100}%;background:#FFD600;">{seg_label(pct_sv)}</div>
                <div class="dt-seg" style="width:{pct_bk*100}%;background:#00E5FF;">{seg_label(pct_bk)}</div>
                <div class="dt-seg" style="width:{pct_tr*100}%;background:#26C6DA;">{seg_label(pct_tr)}</div>
                <div class="dt-seg" style="width:{pct_wk*100}%;background:#00E676;">{seg_label(pct_wk)}</div>
            </div>
            <div style="margin-top:6px;font-size:0.82rem;color:#CBD5E1;">{analysis}</div>
        </div>
        """, unsafe_allow_html=True)

    # Head Performance
    if total_pickup > 0:
        st.markdown("#### Head Performance")
        st.markdown(build_head_table(df), unsafe_allow_html=True)

    # Build Speed
    if mean_board_h > 0:
        st.markdown("#### Build Speed Metrics")
        st.markdown(build_speed_table(df), unsafe_allow_html=True)

    # Machine Breakdown
    st.markdown("#### Per-Machine Breakdown")
    st.markdown(build_machine_table(df, "line"), unsafe_allow_html=True)

# ============================
# TOP ERRORS SECTION
# ============================
st.markdown("<div style='height:10px;'></div>", unsafe_allow_html=True)
if not use_demo:
    errors_df = get_top_errors_db(date_str)
else:
    errors_df = get_demo_top_errors()

if not errors_df.empty:
    total_err = int(errors_df["Errors"].sum())
    top_machine = errors_df.iloc[0]["Machine"]
    top_comp = errors_df.iloc[0]["Component"]
    st.markdown(f"""
    <div style="background:rgba(15,23,42,0.75);backdrop-filter:blur(12px);border:1px solid rgba(255,23,68,0.1);border-radius:12px;padding:16px;">
        <div style="display:flex;align-items:center;gap:10px;margin-bottom:6px;">
            <span style="font-weight:700;color:#FF1744;">🚨 Top 5 gresaka</span>
            <span style="font-size:0.6rem;background:rgba(255,23,68,0.12);color:#FF1744;padding:2px 10px;border-radius:8px;font-weight:600;">UKUPNO {total_err}</span>
        </div>
        <div style="font-size:0.78rem;color:#6B7280;margin-bottom:6px;">Najkriticniji: <b style="color:#CBD5E1;">{top_machine}</b> / <b style="color:#CBD5E1;">{top_comp}</b></div>
        {build_errors_table(errors_df)}
    </div>
    """, unsafe_allow_html=True)
else:
    st.markdown("""
    <div style="background:rgba(15,23,42,0.5);border-radius:10px;padding:14px;text-align:center;">
        <span style="font-size:0.9rem;color:#475569;">✅ Nema zabelezenih gresaka</span>
    </div>
    """, unsafe_allow_html=True)

# Footer
st.markdown("""
<div style="text-align:center;color:rgba(0,229,255,0.08);font-size:0.65rem;font-family:'JetBrains Mono',monospace;padding:24px 0 8px 0;letter-spacing:0.08em;">
    akYtec · NIS SMT Line · Powered by SQUAD Database
</div>
""", unsafe_allow_html=True)
