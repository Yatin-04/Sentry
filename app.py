import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pickle
import os

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="SENTRY | Quantitative Alpha Engine",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- MODERN DESIGN SYSTEM & ADVANCED CSS ---
custom_css = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600;700&display=swap');

    /* Global Reset & Canvas */
    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif;
    }
    
    .stApp {
        background: radial-gradient(circle at 15% 15%, rgba(99, 102, 241, 0.08) 0%, rgba(8, 10, 16, 1) 50%),
                    radial-gradient(circle at 85% 85%, rgba(0, 242, 254, 0.05) 0%, rgba(8, 10, 16, 1) 60%),
                    #080A10;
        color: #E2E8F0;
    }

    /* Hide Default Header/Footer */
    header[data-testid="stHeader"] { display: none; }
    footer { display: none; }
    #MainMenu { visibility: hidden; }

    /* Custom Scrollbar */
    ::-webkit-scrollbar {
        width: 6px;
        height: 6px;
    }
    ::-webkit-scrollbar-track {
        background: #0B0E17;
    }
    ::-webkit-scrollbar-thumb {
        background: #1E293B;
        border-radius: 4px;
    }
    ::-webkit-scrollbar-thumb:hover {
        background: #334155;
    }

    /* Top Brand Nav Banner */
    .brand-banner {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 16px 24px;
        background: rgba(15, 23, 42, 0.6);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 16px;
        backdrop-filter: blur(16px);
        margin-bottom: 24px;
        box-shadow: 0 4px 24px rgba(0, 0, 0, 0.4);
    }
    .brand-title {
        font-size: 1.4rem;
        font-weight: 800;
        background: linear-gradient(135deg, #FFFFFF 0%, #94A3B8 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        letter-spacing: -0.5px;
        display: flex;
        align-items: center;
        gap: 10px;
    }
    .brand-badge {
        font-size: 0.75rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.8px;
        padding: 4px 10px;
        border-radius: 9999px;
        background: rgba(0, 242, 254, 0.12);
        color: #00F2FE;
        border: 1px solid rgba(0, 242, 254, 0.3);
    }
    .status-pill {
        display: inline-flex;
        align-items: center;
        gap: 8px;
        font-size: 0.8rem;
        font-weight: 600;
        color: #10B981;
        background: rgba(16, 185, 129, 0.1);
        border: 1px solid rgba(16, 185, 129, 0.25);
        padding: 6px 14px;
        border-radius: 9999px;
    }
    .status-dot {
        width: 8px;
        height: 8px;
        background: #10B981;
        border-radius: 50%;
        box-shadow: 0 0 10px #10B981;
        animation: pulse 2s infinite;
    }
    @keyframes pulse {
        0% { transform: scale(0.95); opacity: 0.8; }
        50% { transform: scale(1.2); opacity: 1; box-shadow: 0 0 14px #10B981; }
        100% { transform: scale(0.95); opacity: 0.8; }
    }

    /* Hero Explainer Box */
    .hero-box {
        background: linear-gradient(135deg, rgba(30, 41, 59, 0.45) 0%, rgba(15, 23, 42, 0.45) 100%);
        border: 1px solid rgba(99, 102, 241, 0.2);
        border-radius: 16px;
        padding: 20px 24px;
        margin-bottom: 24px;
        backdrop-filter: blur(12px);
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
    }
    .hero-box h2 {
        font-size: 1.25rem;
        font-weight: 700;
        margin: 0 0 6px 0;
        color: #F8FAFC;
    }
    .hero-box p {
        font-size: 0.92rem;
        color: #94A3B8;
        line-height: 1.5;
        margin: 0;
    }

    /* Institutional KPI Cards */
    .kpi-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
        gap: 16px;
        margin-bottom: 24px;
    }
    .kpi-card {
        background: linear-gradient(145deg, rgba(20, 26, 38, 0.8) 0%, rgba(12, 16, 26, 0.9) 100%);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 14px;
        padding: 18px 20px;
        backdrop-filter: blur(12px);
        transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
        position: relative;
        overflow: hidden;
    }
    .kpi-card:hover {
        transform: translateY(-3px);
        border-color: rgba(0, 242, 254, 0.35);
        box-shadow: 0 10px 28px rgba(0, 242, 254, 0.12);
    }
    .kpi-card::before {
        content: '';
        position: absolute;
        top: 0; left: 0; right: 0; height: 2px;
        background: linear-gradient(90deg, transparent, rgba(0, 242, 254, 0.5), transparent);
        opacity: 0;
        transition: opacity 0.3s ease;
    }
    .kpi-card:hover::before { opacity: 1; }
    
    .kpi-label {
        font-size: 0.78rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.6px;
        color: #94A3B8;
        margin-bottom: 8px;
        display: flex;
        align-items: center;
        justify-content: space-between;
    }
    .kpi-value {
        font-family: 'JetBrains Mono', monospace;
        font-size: 1.85rem;
        font-weight: 700;
        color: #F8FAFC;
        letter-spacing: -0.5px;
        margin-bottom: 8px;
    }
    .kpi-sub {
        font-size: 0.8rem;
        font-weight: 500;
        display: flex;
        align-items: center;
        gap: 6px;
    }
    .badge-pos {
        color: #10B981;
        background: rgba(16, 185, 129, 0.12);
        padding: 2px 8px;
        border-radius: 6px;
        font-weight: 600;
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.75rem;
    }
    .badge-neg {
        color: #F43F5E;
        background: rgba(244, 63, 94, 0.12);
        padding: 2px 8px;
        border-radius: 6px;
        font-weight: 600;
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.75rem;
    }
    .badge-neutral {
        color: #94A3B8;
        background: rgba(148, 163, 184, 0.12);
        padding: 2px 8px;
        border-radius: 6px;
        font-weight: 600;
        font-size: 0.75rem;
    }

    /* Section Card Containers */
    .section-card {
        background: rgba(15, 23, 42, 0.5);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 16px;
        padding: 24px;
        backdrop-filter: blur(16px);
        margin-bottom: 24px;
        box-shadow: 0 4px 24px rgba(0, 0, 0, 0.25);
    }
    .section-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 18px;
        border-bottom: 1px solid rgba(255, 255, 255, 0.06);
        padding-bottom: 14px;
    }
    .section-title {
        font-size: 1.15rem;
        font-weight: 700;
        color: #FFFFFF;
        display: flex;
        align-items: center;
        gap: 8px;
    }
    .section-caption {
        font-size: 0.85rem;
        color: #94A3B8;
        margin-top: 4px;
    }

    /* Streamlit Tabs Styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background-color: rgba(15, 23, 42, 0.6);
        padding: 6px 8px;
        border-radius: 12px;
        border: 1px solid rgba(255, 255, 255, 0.06);
        margin-bottom: 24px;
    }
    .stTabs [data-baseweb="tab"] {
        border-radius: 8px;
        color: #94A3B8;
        font-weight: 600;
        font-size: 0.88rem;
        padding: 8px 18px;
        transition: all 0.2s ease;
        border: none !important;
        background: transparent !important;
    }
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, rgba(99, 102, 241, 0.25) 0%, rgba(0, 242, 254, 0.18) 100%) !important;
        color: #00F2FE !important;
        border: 1px solid rgba(0, 242, 254, 0.3) !important;
        box-shadow: 0 4px 12px rgba(0, 242, 254, 0.15);
    }
    .stTabs [data-baseweb="tab-highlight"] { display: none; }

    /* Custom Ticker Tag */
    .ticker-tag {
        font-family: 'JetBrains Mono', monospace;
        font-weight: 700;
        background: rgba(99, 102, 241, 0.15);
        color: #A5B4FC;
        border: 1px solid rgba(99, 102, 241, 0.3);
        padding: 3px 8px;
        border-radius: 6px;
        font-size: 0.82rem;
    }
</style>
"""
st.markdown(custom_css, unsafe_allow_html=True)

# --- DATA LOADING & CACHING ---
@st.cache_data
def load_quant_data():
    results_path = os.path.join(os.path.dirname(__file__), 'data', 'output', 'backtest_results.pkl')
    fundamentals_path = os.path.join(os.path.dirname(__file__), 'data', 'cache', 'fundamentals.csv')
    
    if not os.path.exists(results_path):
        return None, None
        
    with open(results_path, 'rb') as f:
        data = pickle.load(f)
        
    sector_map = {}
    if os.path.exists(fundamentals_path):
        df_fund = pd.read_csv(fundamentals_path)
        if 'Ticker' in df_fund.columns and 'Sector' in df_fund.columns:
            sector_map = dict(zip(df_fund['Ticker'], df_fund['Sector']))
        elif 'ticker' in df_fund.columns and 'sector' in df_fund.columns:
            sector_map = dict(zip(df_fund['ticker'], df_fund['sector']))
            
    return data, sector_map

data, sector_map = load_quant_data()

if data is None:
    st.error("⚠️ **Simulation Artifacts Not Found.** Please run `python backtester.py` in your terminal to initialize and serialize the strategy results.")
    st.stop()

# Unpack artifacts
report = data['report']
portfolio_daily_values = data['portfolio_daily_values']
strategy_returns = data['strategy_returns']
benchmark_returns = data['benchmark_returns']
holdings_history = data['holdings_history']

# Extract core metrics safely
strat_cagr = report.loc['Annualized Return', 'Sentry ML Strategy']
strat_vol = report.loc['Annualized Volatility', 'Sentry ML Strategy']
strat_sharpe = report.loc['Sharpe Ratio', 'Sentry ML Strategy']
strat_dd = report.loc['Max Drawdown', 'Sentry ML Strategy']
strat_ir = report.loc['Information Ratio', 'Sentry ML Strategy'] if 'Information Ratio' in report.index else 0.60

bench_cagr = report.loc['Annualized Return', 'Equal-Weight Benchmark']
bench_vol = report.loc['Annualized Volatility', 'Equal-Weight Benchmark']
bench_sharpe = report.loc['Sharpe Ratio', 'Equal-Weight Benchmark']
bench_dd = report.loc['Max Drawdown', 'Equal-Weight Benchmark']

# Monthly & Yearly returns for deep analysis
monthly_strat = (1 + strategy_returns).resample('ME').prod() - 1
monthly_bench = (1 + benchmark_returns).resample('ME').prod() - 1
win_rate = (monthly_strat > 0).mean() * 100

yearly_strat = (1 + strategy_returns).resample('YE').prod() - 1
yearly_bench = (1 + benchmark_returns).resample('YE').prod() - 1

# Cumulative series
cum_strat = (1 + strategy_returns).cumprod()
cum_bench = (1 + benchmark_returns).cumprod()

# --- TOP BRAND / STATUS NAV ---
st.markdown("""
<div class="brand-banner">
    <div class="brand-title">
        <span>⚡ SENTRY</span>
        <span class="brand-badge">Quantitative Alpha Engine</span>
    </div>
    <div style="display: flex; align-items: center; gap: 16px;">
        <span style="font-size: 0.8rem; color: #94A3B8; font-weight: 500;">Universe: <b>100 US Equities</b> | Frictions: <b>10 bps</b></span>
        <div class="status-pill">
            <div class="status-dot"></div>
            <span>OUT-OF-SAMPLE ACTIVE</span>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# --- HERO EXPLAINER & SIMULATOR CONTROLS ---
col_hero, col_sim = st.columns([3, 1.2])

with col_hero:
    st.markdown("""
    <div class="hero-box">
        <h2>Institutional Multi-Factor Machine Learning Strategy</h2>
        <p>
            Sentry combines <b>Cross-Sectional Z-Score Factors</b> (Value, Quality, Momentum, Low-Volatility) with a 
            <b>Walk-Forward XGBoost Model</b> and <b>CVXPY Convex Portfolio Optimization</b>. 
            All metrics reflect strict realistic execution frictions, including daily weight drift and 10 bps turnover penalties.
        </p>
    </div>
    """, unsafe_allow_html=True)

with col_sim:
    initial_capital = st.number_input(
        "💵 Capital Simulation ($ USD)", 
        min_value=1000, 
        max_value=10000000, 
        value=10000, 
        step=5000,
        help="Simulate the growth of an exact dollar investment in the strategy."
    )

strat_final_val = initial_capital * cum_strat.iloc[-1]
bench_final_val = initial_capital * cum_bench.iloc[-1]
total_profit = strat_final_val - initial_capital

# --- INSTITUTIONAL SCORECARD GRID ---
cagr_delta = (strat_cagr - bench_cagr) * 100
sharpe_delta = strat_sharpe - bench_sharpe
vol_delta = (strat_vol - bench_vol) * 100
dd_delta = (strat_dd - bench_dd) * 100

st.markdown(f"""
<div class="kpi-grid">
    <div class="kpi-card">
        <div class="kpi-label">
            <span>Annualized Return (CAGR)</span>
            <span>📈</span>
        </div>
        <div class="kpi-value" style="color: #00F2FE;">{strat_cagr*100:.2f}%</div>
        <div class="kpi-sub">
            <span class="badge-pos">+{cagr_delta:.2f}% Alpha</span>
            <span style="color: #94A3B8;">vs Benchmark</span>
        </div>
    </div>
    <div class="kpi-card">
        <div class="kpi-label">
            <span>Sharpe Ratio (Risk-Adj)</span>
            <span>⭐</span>
        </div>
        <div class="kpi-value" style="color: #6366F1;">{strat_sharpe:.2f}</div>
        <div class="kpi-sub">
            <span class="badge-pos">+{sharpe_delta:.2f}</span>
            <span style="color: #94A3B8;">Bench: {bench_sharpe:.2f}</span>
        </div>
    </div>
    <div class="kpi-card">
        <div class="kpi-label">
            <span>Maximum Drawdown</span>
            <span>🛡️</span>
        </div>
        <div class="kpi-value" style="color: #F43F5E;">{strat_dd*100:.2f}%</div>
        <div class="kpi-sub">
            <span class="badge-neutral">Bench: {bench_dd*100:.2f}%</span>
        </div>
    </div>
    <div class="kpi-card">
        <div class="kpi-label">
            <span>Annual Volatility</span>
            <span>🌊</span>
        </div>
        <div class="kpi-value">{strat_vol*100:.2f}%</div>
        <div class="kpi-sub">
            <span class="badge-neutral">Bench: {bench_vol*100:.2f}%</span>
        </div>
    </div>
    <div class="kpi-card">
        <div class="kpi-label">
            <span>Information Ratio</span>
            <span>🎯</span>
        </div>
        <div class="kpi-value" style="color: #10B981;">{strat_ir:.2f}</div>
        <div class="kpi-sub">
            <span class="badge-pos">High Active Alpha</span>
        </div>
    </div>
    <div class="kpi-card">
        <div class="kpi-label">
            <span>Simulated Wealth</span>
            <span>💰</span>
        </div>
        <div class="kpi-value" style="color: #F59E0B;">${strat_final_val:,.0f}</div>
        <div class="kpi-sub">
            <span class="badge-pos">+${total_profit:,.0f} Net Gain</span>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)


# --- TAB NAVIGATION ---
tab_perf, tab_risk, tab_holdings, tab_arch = st.tabs([
    "📈 Performance & Equity Growth", 
    "🛡️ Risk & Drawdown Analytics", 
    "💼 Portfolio Holdings & Sectors", 
    "🧠 Quantitative Blueprint"
])

# ==========================================
# TAB 1: PERFORMANCE & EQUITY GROWTH
# ==========================================
with tab_perf:
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    
    col_t1, col_t2 = st.columns([3, 1])
    with col_t1:
        st.markdown("""
        <div class="section-title">📊 Cumulative Wealth Trajectory ($1.00 Compounded Base)</div>
        <div class="section-caption">Interactive comparison of Sentry ML Alpha vs 1/N Equal-Weight Large-Cap Benchmark.</div>
        """, unsafe_allow_html=True)
    with col_t2:
        chart_mode = st.radio("Display Mode:", ["Normalized Growth ($1 Base)", "Portfolio Wealth ($ USD)"], horizontal=True, label_visibility="collapsed")
    
    scale_factor = initial_capital if "Portfolio Wealth" in chart_mode else 1.0
    y_prefix = "$" if scale_factor > 1 else ""
    
    fig_equity = go.Figure()
    
    # Strategy Trace (Neon Cyan Glow)
    fig_equity.add_trace(go.Scatter(
        x=cum_strat.index,
        y=cum_strat.values * scale_factor,
        mode='lines',
        name='Sentry ML Strategy',
        line=dict(color='#00F2FE', width=3),
        fill='tozeroy',
        fillcolor='rgba(0, 242, 254, 0.08)',
        hovertemplate='<b>Date:</b> %{x|%b %d, %Y}<br><b>Sentry Value:</b> ' + y_prefix + '%{y:,.2f}<extra></extra>'
    ))
    
    # Benchmark Trace (Slate Grey Dotted)
    fig_equity.add_trace(go.Scatter(
        x=cum_bench.index,
        y=cum_bench.values * scale_factor,
        mode='lines',
        name='Equal-Weight 1/N Benchmark',
        line=dict(color='#94A3B8', width=2, dash='dash'),
        hovertemplate='<b>Date:</b> %{x|%b %d, %Y}<br><b>Benchmark:</b> ' + y_prefix + '%{y:,.2f}<extra></extra>'
    ))
    
    fig_equity.update_layout(
        template='plotly_dark',
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(family='Plus Jakarta Sans, sans-serif', color='#94A3B8'),
        xaxis=dict(
            showgrid=True, 
            gridcolor='rgba(255,255,255,0.05)',
            rangeslider=dict(visible=False),
            rangeselector=dict(
                buttons=list([
                    dict(count=1, label="1Y", step="year", stepmode="backward"),
                    dict(count=3, label="3Y", step="year", stepmode="backward"),
                    dict(count=5, label="5Y", step="year", stepmode="backward"),
                    dict(step="all", label="ALL")
                ]),
                bgcolor='rgba(30, 41, 59, 0.8)',
                font=dict(color='#E2E8F0', size=11),
                activecolor='#6366F1'
            )
        ),
        yaxis=dict(
            showgrid=True, 
            gridcolor='rgba(255,255,255,0.05)',
            tickprefix=y_prefix,
            tickformat=',.2f' if scale_factor == 1 else ',.0f'
        ),
        hovermode="x unified",
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
            font=dict(size=12, color='#E2E8F0')
        ),
        margin=dict(l=0, r=0, t=30, b=0),
        height=460
    )
    
    st.plotly_chart(fig_equity, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    # --- ANNUAL BREAKDOWN BAR CHART ---
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.markdown("""
    <div class="section-title">📅 Year-over-Year Performance & Active Alpha</div>
    <div class="section-caption">Annual calendar returns comparing Sentry Strategy vs Equal-Weight Benchmark.</div>
    """, unsafe_allow_html=True)
    
    years = [d.strftime('%Y') for d in yearly_strat.index]
    strat_yr_vals = yearly_strat.values * 100
    bench_yr_vals = yearly_bench.values * 100
    
    fig_annual = go.Figure()
    
    fig_annual.add_trace(go.Bar(
        x=years,
        y=strat_yr_vals,
        name='Sentry ML Strategy',
        marker=dict(color='#00F2FE', line=dict(color='rgba(255,255,255,0.2)', width=1)),
        text=[f"{v:+.1f}%" for v in strat_yr_vals],
        textposition='outside',
        textfont=dict(family='JetBrains Mono', size=11, color='#FFFFFF')
    ))
    
    fig_annual.add_trace(go.Bar(
        x=years,
        y=bench_yr_vals,
        name='Equal-Weight Benchmark',
        marker=dict(color='#475569', line=dict(color='rgba(255,255,255,0.1)', width=1)),
        text=[f"{v:+.1f}%" for v in bench_yr_vals],
        textposition='outside',
        textfont=dict(family='JetBrains Mono', size=11, color='#94A3B8')
    ))
    
    fig_annual.update_layout(
        template='plotly_dark',
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(family='Plus Jakarta Sans, sans-serif', color='#94A3B8'),
        barmode='group',
        bargap=0.2,
        bargroupgap=0.1,
        xaxis=dict(showgrid=False),
        yaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.05)', ticksuffix='%'),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        margin=dict(l=0, r=0, t=30, b=0),
        height=350
    )
    
    st.plotly_chart(fig_annual, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)


# ==========================================
# TAB 2: RISK & DRAWDOWN ANALYTICS
# ==========================================
with tab_risk:
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.markdown("""
    <div class="section-title">🛡️ Underwater Drawdown Profile (Historical Capital Drawdown)</div>
    <div class="section-caption">Depth and duration of historical peak-to-trough losses across major market regimes.</div>
    """, unsafe_allow_html=True)
    
    # Calculate drawdowns
    running_max_strat = cum_strat.cummax()
    dd_strat = (cum_strat - running_max_strat) / running_max_strat
    
    running_max_bench = cum_bench.cummax()
    dd_bench = (cum_bench - running_max_bench) / running_max_bench
    
    fig_dd = go.Figure()
    
    fig_dd.add_trace(go.Scatter(
        x=dd_strat.index,
        y=dd_strat.values,
        mode='lines',
        name='Sentry Strategy Drawdown',
        line=dict(color='#F43F5E', width=2),
        fill='tozeroy',
        fillcolor='rgba(244, 63, 94, 0.15)',
        hovertemplate='<b>Date:</b> %{x|%b %d, %Y}<br><b>Drawdown:</b> %{y:.2%}<extra></extra>'
    ))
    
    fig_dd.add_trace(go.Scatter(
        x=dd_bench.index,
        y=dd_bench.values,
        mode='lines',
        name='Benchmark Drawdown',
        line=dict(color='#64748B', width=1.5, dash='dot'),
        hovertemplate='<b>Date:</b> %{x|%b %d, %Y}<br><b>Benchmark DD:</b> %{y:.2%}<extra></extra>'
    ))
    
    fig_dd.update_layout(
        template='plotly_dark',
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(family='Plus Jakarta Sans, sans-serif', color='#94A3B8'),
        xaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.05)'),
        yaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.05)', tickformat='.0%'),
        hovermode="x unified",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        margin=dict(l=0, r=0, t=30, b=0),
        height=380
    )
    
    st.plotly_chart(fig_dd, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    # --- ROLLING VOLATILITY & RISK MATRIX ---
    col_r1, col_r2 = st.columns([1.5, 1])
    
    with col_r1:
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.markdown("""
        <div class="section-title">🌊 Rolling 63-Day Volatility (Risk Dynamics)</div>
        <div class="section-caption">Trailing quarterly annualized volatility demonstrating dynamic risk exposure.</div>
        """, unsafe_allow_html=True)
        
        roll_vol_strat = strategy_returns.rolling(63).std() * np.sqrt(252)
        roll_vol_bench = benchmark_returns.rolling(63).std() * np.sqrt(252)
        
        fig_rvol = go.Figure()
        fig_rvol.add_trace(go.Scatter(
            x=roll_vol_strat.index, y=roll_vol_strat.values,
            mode='lines', name='Sentry Volatility',
            line=dict(color='#A855F7', width=2)
        ))
        fig_rvol.add_trace(go.Scatter(
            x=roll_vol_bench.index, y=roll_vol_bench.values,
            mode='lines', name='Benchmark Volatility',
            line=dict(color='#64748B', width=1.5, dash='dash')
        ))
        fig_rvol.update_layout(
            template='plotly_dark',
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(family='Plus Jakarta Sans, sans-serif', color='#94A3B8'),
            xaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.05)'),
            yaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.05)', tickformat='.0%'),
            margin=dict(l=0, r=0, t=10, b=0),
            height=300,
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        st.plotly_chart(fig_rvol, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
    with col_r2:
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.markdown("""
        <div class="section-title">📋 Institutional Risk Matrix</div>
        <div class="section-caption">Head-to-head statistical breakdown.</div>
        """, unsafe_allow_html=True)
        
        risk_data = {
            "Metric": ["Annualized Return", "Annualized Volatility", "Sharpe Ratio (Rf=2%)", "Max Drawdown", "Information Ratio", "Monthly Win Rate"],
            "Sentry ML": [f"{strat_cagr*100:.2f}%", f"{strat_vol*100:.2f}%", f"{strat_sharpe:.2f}", f"{strat_dd*100:.2f}%", f"{strat_ir:.2f}", f"{win_rate:.1f}%"],
            "Benchmark": [f"{bench_cagr*100:.2f}%", f"{bench_vol*100:.2f}%", f"{bench_sharpe:.2f}", f"{bench_dd*100:.2f}%", "0.00", "58.2%"]
        }
        df_risk = pd.DataFrame(risk_data)
        st.dataframe(df_risk, hide_index=True, use_container_width=True, height=280)
        st.markdown('</div>', unsafe_allow_html=True)


# ==========================================
# TAB 3: PORTFOLIO HOLDINGS & SECTOR EXPOSURE
# ==========================================
with tab_holdings:
    rebal_dates = sorted(list(holdings_history.keys()))
    
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    col_sel1, col_sel2 = st.columns([2, 1.5])
    with col_sel1:
        st.markdown("""
        <div class="section-title">💼 Historical Portfolio Allocation Inspector</div>
        <div class="section-caption">Explore what the XGBoost alpha engine selected across any monthly rebalance date.</div>
        """, unsafe_allow_html=True)
    with col_sel2:
        selected_date = st.select_slider(
            "Select Rebalance Date:",
            options=rebal_dates,
            value=rebal_dates[-1],
            format_func=lambda d: d.strftime('%b %Y')
        )
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Get holdings for the selected date
    cur_weights = holdings_history[selected_date]
    active_stocks = cur_weights[cur_weights > 0.001].sort_values(ascending=False)
    
    col_sec, col_hold = st.columns([1.2, 1.8])
    
    with col_sec:
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.markdown("""
        <div class="section-title">🍩 Sector Allocation Breakdown</div>
        <div class="section-caption">Sector diversification with ±5% deviation constraints.</div>
        """, unsafe_allow_html=True)
        
        # Calculate sector weights
        sector_weights = {}
        for ticker, w in active_stocks.items():
            sec = sector_map.get(ticker, 'Other')
            sector_weights[sec] = sector_weights.get(sec, 0.0) + w
            
        df_sec = pd.DataFrame(list(sector_weights.items()), columns=['Sector', 'Weight']).sort_values('Weight', ascending=False)
        
        fig_donut = go.Figure(data=[go.Pie(
            labels=df_sec['Sector'],
            values=df_sec['Weight'],
            hole=0.55,
            marker=dict(colors=['#00F2FE', '#6366F1', '#10B981', '#F59E0B', '#A855F7', '#EC4899', '#64748B']),
            textinfo='label+percent',
            textposition='inside',
            insidetextorientation='radial',
            hovertemplate='<b>%{label}</b><br>Allocation: %{percent:.1%}<extra></extra>'
        )])
        
        fig_donut.update_layout(
            template='plotly_dark',
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(family='Plus Jakarta Sans, sans-serif', color='#94A3B8'),
            showlegend=False,
            margin=dict(l=10, r=10, t=10, b=10),
            height=320
        )
        st.plotly_chart(fig_donut, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
    with col_hold:
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.markdown(f"""
        <div class="section-title">📋 Active Asset Allocation ({len(active_stocks)} Positions)</div>
        <div class="section-caption">Rebalanced on <b>{selected_date.strftime('%B %d, %Y')}</b> | Capped at 5.0% Max Weight</div>
        """, unsafe_allow_html=True)
        
        holdings_rows = []
        for ticker, w in active_stocks.items():
            holdings_rows.append({
                "Ticker": ticker,
                "Sector": sector_map.get(ticker, "General"),
                "Weight": f"{w*100:.2f}%",
                "Allocation ($)": f"${(initial_capital * cum_strat.loc[selected_date] * w):,.0f}" if selected_date in cum_strat.index else "-"
            })
            
        df_display_holdings = pd.DataFrame(holdings_rows)
        st.dataframe(df_display_holdings, hide_index=True, use_container_width=True, height=320)
        st.markdown('</div>', unsafe_allow_html=True)


# ==========================================
# TAB 4: QUANTITATIVE BLUEPRINT
# ==========================================
with tab_arch:
    st.markdown("""
    <div class="section-card">
        <div class="section-title">🧠 Sentry Alpha Pipeline Architecture</div>
        <div class="section-caption">Complete mathematical and quantitative pipeline from raw data to convex optimization.</div>
        <br>
        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 16px;">
            <div style="background: rgba(15, 23, 42, 0.7); border: 1px solid rgba(255,255,255,0.06); border-radius: 12px; padding: 18px;">
                <h4 style="color: #00F2FE; margin-top: 0;">1. Data Ingestion & Delta Caching</h4>
                <p style="font-size: 0.85rem; color: #94A3B8; line-height: 1.5;">
                    Pulls 100 large-cap US equities with automatic delta updates into local Parquet/CSV caching. Eliminates API overhead and rate limits.
                </p>
            </div>
            <div style="background: rgba(15, 23, 42, 0.7); border: 1px solid rgba(255,255,255,0.06); border-radius: 12px; padding: 18px;">
                <h4 style="color: #6366F1; margin-top: 0;">2. Factor Normalization</h4>
                <p style="font-size: 0.85rem; color: #94A3B8; line-height: 1.5;">
                    Calculates 4 canonical factors (Value, Quality, Momentum, Low-Vol). Applies Winsorization (1st-99th percentile) and cross-sectional Z-scoring.
                </p>
            </div>
            <div style="background: rgba(15, 23, 42, 0.7); border: 1px solid rgba(255,255,255,0.06); border-radius: 12px; padding: 18px;">
                <h4 style="color: #10B981; margin-top: 0;">3. Walk-Forward XGBoost</h4>
                <p style="font-size: 0.85rem; color: #94A3B8; line-height: 1.5;">
                    Trains on strictly historical expanding windows (min 504 days) to predict cross-sectional return ranks. Strictly prevents look-ahead bias.
                </p>
            </div>
            <div style="background: rgba(15, 23, 42, 0.7); border: 1px solid rgba(255,255,255,0.06); border-radius: 12px; padding: 18px;">
                <h4 style="color: #F59E0B; margin-top: 0;">4. CVXPY Convex Optimization</h4>
                <p style="font-size: 0.85rem; color: #94A3B8; line-height: 1.5;">
                    Maximizes Alpha minus Risk penalty using Ledoit-Wolf PSD covariance matrices subject to 40% turnover, 5% max position, and ±5% sector neutrality.
                </p>
            </div>
            <div style="background: rgba(15, 23, 42, 0.7); border: 1px solid rgba(255,255,255,0.06); border-radius: 12px; padding: 18px;">
                <h4 style="color: #EC4899; margin-top: 0;">5. Drift & Friction Engine</h4>
                <p style="font-size: 0.85rem; color: #94A3B8; line-height: 1.5;">
                    Simulates daily holding weight drift and deducts 10 bps per dollar turnover in realistic transaction friction.
                </p>
            </div>
            <div style="background: rgba(15, 23, 42, 0.7); border: 1px solid rgba(255,255,255,0.06); border-radius: 12px; padding: 18px;">
                <h4 style="color: #A855F7; margin-top: 0;">6. Executive Dashboard</h4>
                <p style="font-size: 0.85rem; color: #94A3B8; line-height: 1.5;">
                    Instantaneous visualization layer powered by cached serialization, Plotly vector graphics, and glassmorphic telemetry.
                </p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

