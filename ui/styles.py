"""Custom CSS for hackathon-grade Streamlit UI."""

CUSTOM_CSS = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500&display=swap');

    html, body, [class*="css"] { font-family: 'Plus Jakarta Sans', sans-serif; }
    .stApp {
        background: linear-gradient(160deg, #f8fafc 0%, #eef2ff 35%, #ecfdf5 100%);
    }

    #MainMenu, footer, header { visibility: hidden; }

    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #ffffff 0%, #f8fafc 100%);
        border-right: 1px solid #e2e8f0;
        box-shadow: 4px 0 24px rgba(15, 23, 42, 0.04);
    }

    .brand-header {
        background: linear-gradient(135deg, #0f172a 0%, #1e3a5f 40%, #0d9488 100%);
        border-radius: 20px;
        padding: 32px 36px;
        margin-bottom: 28px;
        color: white;
        box-shadow: 0 20px 50px rgba(15, 23, 42, 0.2);
        position: relative;
        overflow: hidden;
    }
    .brand-header::after {
        content: '';
        position: absolute; right: -30px; top: -30px;
        width: 180px; height: 180px;
        background: rgba(255,255,255,0.08);
        border-radius: 50%;
    }
    .brand-header h1 {
        margin: 0;
        font-size: 2rem;
        font-weight: 800;
        letter-spacing: -0.03em;
    }
    .brand-header p { margin: 10px 0 0; opacity: 0.92; font-size: 1.05rem; max-width: 720px; }
    .brand-badge {
        display: inline-block;
        background: rgba(255,255,255,0.15);
        border: 1px solid rgba(255,255,255,0.25);
        border-radius: 999px;
        padding: 4px 14px;
        font-size: 0.75rem;
        font-weight: 600;
        margin-bottom: 12px;
        letter-spacing: 0.04em;
        text-transform: uppercase;
    }

    div[data-testid="stMetric"] {
        background: white;
        border: 1px solid #e2e8f0;
        border-radius: 16px;
        padding: 18px 20px;
        box-shadow: 0 4px 16px rgba(0,0,0,0.04);
        transition: transform 0.15s ease;
    }
    div[data-testid="stMetric"]:hover { transform: translateY(-2px); }
    div[data-testid="stMetric"] label { color: #64748b !important; font-weight: 600; font-size: 0.8rem; }
    div[data-testid="stMetric"] [data-testid="stMetricValue"] {
        color: #0f172a !important;
        font-weight: 800;
    }

    .user-bubble {
        background: linear-gradient(135deg, #1e40af, #3b82f6);
        color: white;
        padding: 14px 20px;
        border-radius: 18px 18px 4px 18px;
        margin: 12px 0 12px 60px;
        box-shadow: 0 8px 24px rgba(37, 99, 235, 0.2);
        line-height: 1.5;
    }
    .bubble-label {
        font-size: 0.65rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        opacity: 0.85;
        margin-bottom: 4px;
    }

    .insight-card {
        background: linear-gradient(135deg, #eff6ff, #ecfdf5);
        border: 1px solid #bfdbfe;
        border-radius: 14px;
        padding: 18px 22px;
        color: #1e3a5f;
        line-height: 1.65;
        margin: 12px 0;
    }
    .insight-card strong { color: #0d9488; }

    .sql-block {
        background: #0f172a;
        color: #5eead4;
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.8rem;
        padding: 16px 20px;
        border-radius: 12px;
        border-left: 4px solid #14b8a6;
        white-space: pre-wrap;
        word-break: break-word;
        margin: 8px 0;
    }

    .step-timeline { margin: 8px 0; }
    .step-item {
        display: flex;
        align-items: flex-start;
        gap: 12px;
        padding: 10px 0;
        border-bottom: 1px solid #f1f5f9;
    }
    .step-dot {
        width: 28px; height: 28px;
        border-radius: 50%;
        display: flex; align-items: center; justify-content: center;
        font-size: 0.7rem; font-weight: 700;
        flex-shrink: 0;
    }
    .dot-done { background: #d1fae5; color: #047857; }
    .dot-error { background: #fee2e2; color: #b91c1c; }
    .dot-pending { background: #f1f5f9; color: #94a3b8; }

    .sample-chip {
        background: white;
        border: 1px solid #e2e8f0;
        border-radius: 12px;
        padding: 10px 14px;
        font-size: 0.85rem;
        color: #334155;
        margin: 4px 0;
        cursor: pointer;
        transition: all 0.15s;
    }
    .sample-chip:hover {
        border-color: #3b82f6;
        background: #eff6ff;
        color: #1d4ed8;
    }

    .history-item {
        font-size: 0.8rem;
        color: #475569;
        padding: 6px 0;
        border-bottom: 1px dashed #e2e8f0;
    }

    @keyframes pulse-ring {
        0% { opacity: 1; }
        50% { opacity: 0.5; }
        100% { opacity: 1; }
    }
    .loading-pulse { animation: pulse-ring 1.5s ease-in-out infinite; }

    .stButton > button[kind="primary"] {
        background: linear-gradient(135deg, #1e40af, #0d9488) !important;
        border: none !important;
        border-radius: 12px !important;
        font-weight: 700 !important;
    }
</style>
"""
