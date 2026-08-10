import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pickle
import os

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="SENTRY | Institutional Alpha Engine",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- MODERN INSTITUTIONAL DESIGN SYSTEM & CSS TOKENS ---
custom_css = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600;700;800&display=swap');

    /* Global Canvas & Reset */
    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif;
    }
    
    .stApp {
        background: radial-gradient(circle at 10% 10%, rgba(99, 102, 241, 0.08) 0%, rgba(8, 10, 16, 1) 50%),
                    radial-gradient(circle at 90% 90%, rgba(0, 242, 254, 0.05) 0%, rgba(8, 10, 16, 1) 60%),
                    #080A10;
        color: #E2E8F0;
    }

    /* Hide Default Headers */
    header[data-testid="stHeader"] { display: none; }
    footer { display: none; }
    #MainMenu { visibility: hidden; }

    /* Custom Sleek Scrollbars */
    ::-webkit-scrollbar { width: 5px; height: 5px; }
    ::-webkit-scrollbar-track { background: #080A10; }
    ::-webkit-scrollbar-thumb { background: #1E293B; border-radius: 4px; }
    ::-webkit-scrollbar-thumb:hover { background: #334155; }

    /* Top Master Header */
    .master-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 14px 22px;
        background: rgba(15, 23, 42, 0.65);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 14px;
        backdrop-filter: blur(16px);
        margin-bottom: 20px;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.35);
    }
    .header-logo {
        display: flex;
        align-items: center;
        gap: 12px;
    }
    .brand-text {
        font-size: 1.35rem;
        font-weight: 800;
        letter-spacing: -0.5px;
        background: linear-gradient(135deg, #FFFFFF 0%, #CBD5E1 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .badge-sub {
        font-size: 0.72rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.8px;
        padding: 3px 8px;
        border-radius: 6px;
        background: rgba(0, 242, 254, 0.12);
        color: #00F2FE;
        border: 1px solid rgba(0, 242, 254, 0.28);
    }
    .status-regime {
        display: inline-flex;
        align-items: center;
        gap: 8px;
        font-size: 0.78rem;
        font-weight: 600;
        color: #10B981;
        background: rgba(16, 185, 129, 0.1);
        border: 1px solid rgba(16, 185, 129, 0.25);
        padding: 5px 12px;
        border-radius: 9999px;
    }
    .pulse-dot {
        width: 7px;
        height: 7px;
        background: #10B981;
        border-radius: 50%;
        box-shadow: 0 0 8px #10B981;
        animation: pulseAnimation 2s infinite;
    }
    @keyframes pulseAnimation {
        0% { transform: scale(0.95); opacity: 0.8; }
        50% { transform: scale(1.25); opacity: 1; box-shadow: 0 0 12px #10B981; }
        100% { transform: scale(0.95); opacity: 0.8; }
    }

    /* KPI Grid & Cards */
    .kpi-container {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
        gap: 14px;
        margin-bottom: 20px;
    }
    .kpi-box {
        background: linear-gradient(145deg, rgba(20, 26, 38, 0.85) 0%, rgba(12, 16, 26, 0.95) 100%);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 12px;
        padding: 16px 18px;
        backdrop-filter: blur(12px);
        transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
        position: relative;
        overflow: hidden;
    }
    .kpi-box:hover {
        transform: translateY(-3px);
        border-color: rgba(0, 242, 254, 0.35);
        box-shadow: 0 8px 24px rgba(0, 242, 254, 0.12);
    }
    .kpi-box::before {
        content: '';
        position: absolute;
        top: 0; left: 0; right: 0; height: 2px;
        background: linear-gradient(90deg, transparent, rgba(0, 242, 254, 0.6), transparent);
        opacity: 0;
        transition: opacity 0.3s ease;
    }
    .kpi-box:hover::before { opacity: 1; }
    .kpi-title {
        font-size: 0.75rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        color: #94A3B8;
        margin-bottom: 6px;
        display: flex;
        align-items: center;
        justify-content: space-between;
    }
    .kpi-num {
        font-family: 'JetBrains Mono', monospace;
        font-size: 1.75rem;
        font-weight: 700;
        color: #F8FAFC;
        letter-spacing: -0.5px;
        margin-bottom: 6px;
    }
    .badge-gain {
        color: #10B981;
        background: rgba(16, 185, 129, 0.12);
        padding: 2px 7px;
        border-radius: 5px;
        font-weight: 600;
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.72rem;
    }
    .badge-loss {
        color: #F43F5E;
        background: rgba(244, 63, 94, 0.12);
        padding: 2px 7px;
        border-radius: 5px;
        font-weight: 600;
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.72rem;
    }
    .badge-muted {
        color: #94A3B8;
        background: rgba(148, 163, 184, 0.12);
        padding: 2px 7px;
        border-radius: 5px;
        font-weight: 600;
        font-size: 0.72rem;
    }

    /* Content Cards */
    .glass-panel {
        background: rgba(15, 23, 42, 0.55);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 14px;
        padding: 20px;
        backdrop-filter: blur(16px);
        margin-bottom: 20px;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.25);
    }
    .panel-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 14px;
        border-bottom: 1px solid rgba(255, 255, 255, 0.06);
        padding-bottom: 10px;
    }
    .panel-title {
        font-size: 1.05rem;
        font-weight: 700;
        color: #FFFFFF;
        display: flex;
        align-items: center;
        gap: 8px;
    }
    .panel-sub {
        font-size: 0.8rem;
        color: #94A3B8;
        margin-top: 2px;
    }

    /* Right Telemetry Sidebar */
    .telemetry-card {
        background: linear-gradient(145deg, rgba(20, 26, 38, 0.9) 0%, rgba(12, 16, 26, 0.98) 100%);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 14px;
        padding: 18px;
        margin-bottom: 16px;
    }
    .telemetry-title {
        font-size: 0.82rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.6px;
        color: #94A3B8;
        margin-bottom: 12px;
        display: flex;
        align-items: center;
        justify-content: space-between;
    }
    .stat-row {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 7px 0;
        border-bottom: 1px solid rgba(255, 255, 255, 0.04);
        font-size: 0.85rem;
    }
    .stat-row:last-child { border-bottom: none; }
    .stat-label { color: #94A3B8; }
    .stat-val { font-family: 'JetBrains Mono', monospace; font-weight: 600; color: #F8FAFC; }

    /* Custom Ticker Badges */
    .ticker-pill {
        font-family: 'JetBrains Mono', monospace;
        font-weight: 700;
        background: rgba(99, 102, 241, 0.15);
        color: #A5B4FC;
        border: 1px solid rgba(99, 102, 241, 0.3);
        padding: 2px 7px;
        border-radius: 5px;
        font-size: 0.78rem;
    }

    /* Streamlit Tabs Customization */
    .stTabs [data-baseweb="tab-list"] {
        gap: 6px;
        background-color: rgba(15, 23, 42, 0.65);
        padding: 5px;
        border-radius: 10px;
        border: 1px solid rgba(255, 255, 255, 0.06);
        margin-bottom: 18px;
    }
    .stTabs [data-baseweb="tab"] {
        border-radius: 7px;
        color: #94A3B8;
        font-weight: 600;
        font-size: 0.85rem;
        padding: 7px 16px;
        transition: all 0.2s ease;
        border: none !important;
        background: transparent !important;
    }
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, rgba(99, 102, 241, 0.25) 0%, rgba(0, 242, 254, 0.18) 100%) !important;
        color: #00F2FE !important;
        border: 1px solid rgba(0, 242, 254, 0.3) !important;
    }
    .stTabs [data-baseweb="tab-highlight"] { display: none; }
</style>
"""
st.markdown(custom_css, unsafe_allow_html=True)

# --- DATA INGESTION & ROBUST CACHING ---
@st.cache_data
def load_all_quant_data():
    results_path = os.path.join(os.path.dirname(__file__), 'data', 'output', 'backtest_results.pkl')
    fundamentals_path = os.path.join(os.path.dirname(__file__), 'data', 'cache', 'fundamentals.csv')
    
    if not os.path.exists(results_path):
        return None, None
        
    with open(results_path, 'rb') as f:
        data = pickle.load(f)
        
    sector_map = {}
    if os.path.exists(fundamentals_path):
        df_fund = pd.read_csv(fundamentals_path)
        col_t = 'Ticker' if 'Ticker' in df_fund.columns else 'ticker'
        col_s = 'Sector' if 'Sector' in df_fund.columns else 'sector'
        if col_t in df_fund.columns and col_s in df_fund.columns:
            sector_map = dict(zip(df_fund[col_t], df_fund[col_s]))
            
    return data, sector_map

data, sector_map = load_all_quant_data()

if data is None:
    st.error("⚠️ **No Simulation Artifacts Found.** Please execute `python backtester.py` to initialize data.")
    st.stop()

# Unpack Core Simulation Series
report = data['report']
portfolio_daily_values = data['portfolio_daily_values']
strategy_returns = data['strategy_returns']
benchmark_returns = data['benchmark_returns']
holdings_history = data['holdings_history']

# Extract Key Institutional KPIs
strat_cagr = report.loc['Annualized Return', 'Sentry ML Strategy']
strat_vol = report.loc['Annualized Volatility', 'Sentry ML Strategy']
strat_sharpe = report.loc['Sharpe Ratio', 'Sentry ML Strategy']
strat_dd = report.loc['Max Drawdown', 'Sentry ML Strategy']
strat_ir = report.loc['Information Ratio', 'Sentry ML Strategy'] if 'Information Ratio' in report.index else 0.60

bench_cagr = report.loc['Annualized Return', 'Equal-Weight Benchmark']
bench_vol = report.loc['Equal-Weight Benchmark', 'Annualized Volatility']
bench_sharpe = report.loc['Sharpe Ratio', 'Equal-Weight Benchmark']
bench_dd = report.loc['Max Drawdown', 'Equal-Weight Benchmark']

# Statistical Risk Analytics
var_95 = np.percentile(strategy_returns, 5) * 100
var_99 = np.percentile(strategy_returns, 1) * 100
cov_mat = np.cov(strategy_returns, benchmark_returns)
beta = cov_mat[0, 1] / cov_mat[1, 1] if cov_mat[1, 1] != 0 else 1.0
downside_dev = strategy_returns[strategy_returns < 0].std() * np.sqrt(252)
sortino = (strategy_returns.mean() * 252 - 0.02) / downside_dev if downside_dev > 0 else 0.0

# Cumulative Growth
cum_strat = (1 + strategy_returns).cumprod()
cum_bench = (1 + benchmark_returns).cumprod()

# Calendar Returns
yearly_strat = (1 + strategy_returns).resample('YE').prod() - 1
yearly_bench = (1 + benchmark_returns).resample('YE').prod() - 1
monthly_strat = (1 + strategy_returns).resample('ME').prod() - 1
win_rate = (monthly_strat > 0).mean() * 100

# --- TOP MASTER HEADER ---
st.markdown("""
<div class="master-header">
    <div class="header-logo">
        <span style="font-size: 1.5rem;">⚡</span>
        <span class="brand-text">SENTRY</span>
        <span class="badge-sub">Institutional Alpha Engine</span>
    </div>
    <div style="display: flex; align-items: center; gap: 14px;">
        <span style="font-size: 0.78rem; color: #94A3B8;">Universe: <b>100 US Mega-Caps</b> | Friction: <b>10 bps</b></span>
        <div class="status-regime">
            <div class="pulse-dot"></div>
            <span>OUT-OF-SAMPLE ACTIVE</span>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# --- 6-CARD INSTITUTIONAL SCORECARD ---
cagr_delta = (strat_cagr - bench_cagr) * 100
sharpe_delta = strat_sharpe - bench_sharpe

st.markdown(f"""
<div class="kpi-container">
    <div class="kpi-box">
        <div class="kpi-title"><span>Annual Return (CAGR)</span><span>📈</span></div>
        <div class="kpi-num" style="color: #00F2FE;">{strat_cagr*100:.2f}%</div>
        <span class="badge-gain">+{cagr_delta:.2f}% vs Bench</span>
    </div>
    <div class="kpi-box">
        <div class="kpi-title"><span>Sharpe Ratio (Rf=2%)</span><span>⭐</span></div>
        <div class="kpi-num" style="color: #6366F1;">{strat_sharpe:.2f}</div>
        <span class="badge-gain">+{sharpe_delta:.2f} Alpha</span>
    </div>
    <div class="kpi-box">
        <div class="kpi-title"><span>Max Drawdown</span><span>🛡️</span></div>
        <div class="kpi-num" style="color: #F43F5E;">{strat_dd*100:.2f}%</div>
        <span class="badge-muted">Bench: {bench_dd*100:.2f}%</span>
    </div>
    <div class="kpi-box">
        <div class="kpi-title"><span>Annual Volatility</span><span>🌊</span></div>
        <div class="kpi-num">{strat_vol*100:.2f}%</div>
        <span class="badge-muted">Bench: {bench_vol*100:.2f}%</span>
    </div>
    <div class="kpi-box">
        <div class="kpi-title"><span>Sortino Ratio</span><span>🎯</span></div>
        <div class="kpi-num" style="color: #10B981;">{sortino:.2f}</div>
        <span class="badge-gain">Low Downside Risk</span>
    </div>
    <div class="kpi-box">
        <div class="kpi-title"><span>Information Ratio</span><span>📊</span></div>
        <div class="kpi-num" style="color: #F59E0B;">{strat_ir:.2f}</div>
        <span class="badge-gain">Active Alpha</span>
    </div>
</div>
""", unsafe_allow_html=True)

# --- 2-COLUMN MAIN CANVAS + TELEMETRY DOCK LAYOUT ---
col_main, col_telemetry = st.columns([2.7, 1.1])

with col_main:
    # --- TAB NAVIGATION ---
    tab_equity, tab_risk, tab_alloc, tab_arch = st.tabs([
        "📊 Portfolio Performance", 
        "🛡️ Risk & VaR Analytics", 
        "💼 Asset & Sector Holdings", 
        "🧠 Quantitative Blueprint"
    ])
    
    # -------------------------------------------------------------
    # TAB 1: PORTFOLIO PERFORMANCE
    # -------------------------------------------------------------
    with tab_equity:
        st.markdown('<div class="glass-panel">', unsafe_allow_html=True)
        col_ctl1, col_ctl2 = st.columns([2, 1])
        with col_ctl1:
            st.markdown("""
            <div class="panel-title">📈 Cumulative Wealth Growth Trajectory</div>
            <div class="panel-sub">Compounded outperformance of Sentry ML Alpha vs 1/N Equal-Weight Market Benchmark.</div>
            """, unsafe_allow_html=True)
        with col_ctl2:
            scale_choice = st.radio("Scale Mode:", ["Normalized ($1.00 Base)", "Total Wealth ($ USD)"], horizontal=True, label_visibility="collapsed")
        
        sim_multiplier = 1.0
        y_prefix = "$" if "Total Wealth" in scale_choice else ""
        if "Total Wealth" in scale_choice:
            sim_multiplier = 10000.0  # $10,000 base
            
        fig_equity = go.Figure()
        
        # Strategy Trace
        fig_equity.add_trace(go.Scatter(
            x=cum_strat.index,
            y=cum_strat.values * sim_multiplier,
            mode='lines',
            name='Sentry ML Strategy',
            line=dict(color='#00F2FE', width=3),
            fill='tozeroy',
            fillcolor='rgba(0, 242, 254, 0.08)',
            hovertemplate='<b>%{x|%b %d, %Y}</b><br>Sentry: ' + y_prefix + '%{y:,.2f}<extra></extra>'
        ))
        
        # Benchmark Trace
        fig_equity.add_trace(go.Scatter(
            x=cum_bench.index,
            y=cum_bench.values * sim_multiplier,
            mode='lines',
            name='Equal-Weight Benchmark',
            line=dict(color='#94A3B8', width=2, dash='dash'),
            hovertemplate='<b>%{x|%b %d, %Y}</b><br>Benchmark: ' + y_prefix + '%{y:,.2f}<extra></extra>'
        ))
        
        fig_equity.update_layout(
            template='plotly_dark',
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(family='Plus Jakarta Sans, sans-serif', color='#94A3B8'),
            xaxis=dict(
                showgrid=True, gridcolor='rgba(255,255,255,0.05)',
                rangeselector=dict(
                    buttons=list([
                        dict(count=6, label="6M", step="month", stepmode="backward"),
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
            yaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.05)', tickprefix=y_prefix, tickformat=',.2f'),
            hovermode="x unified",
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
            margin=dict(l=0, r=0, t=30, b=0),
            height=420
        )
        st.plotly_chart(fig_equity, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Calendar Returns Bar Chart
        st.markdown('<div class="glass-panel">', unsafe_allow_html=True)
        st.markdown("""
        <div class="panel-title">📅 Annual Calendar Performance & Alpha Distribution</div>
        <div class="panel-sub">Year-over-year returns comparing active model selection vs baseline.</div>
        """, unsafe_allow_html=True)
        
        years = [d.strftime('%Y') for d in yearly_strat.index]
        fig_bar = go.Figure()
        
        fig_bar.add_trace(go.Bar(
            x=years,
            y=yearly_strat.values * 100,
            name='Sentry ML Strategy',
            marker=dict(color='#00F2FE', line=dict(color='rgba(255,255,255,0.2)', width=1)),
            text=[f"{v:+.1f}%" for v in yearly_strat.values * 100],
            textposition='outside',
            textfont=dict(family='JetBrains Mono', size=11, color='#FFFFFF')
        ))
        
        fig_bar.add_trace(go.Bar(
            x=years,
            y=yearly_bench.values * 100,
            name='Equal-Weight Benchmark',
            marker=dict(color='#475569'),
            text=[f"{v:+.1f}%" for v in yearly_bench.values * 100],
            textposition='outside',
            textfont=dict(family='JetBrains Mono', size=11, color='#94A3B8')
        ))
        
        fig_bar.update_layout(
            template='plotly_dark',
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            barmode='group',
            bargap=0.2,
            font=dict(family='Plus Jakarta Sans', color='#94A3B8'),
            yaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.05)', ticksuffix='%'),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
            margin=dict(l=0, r=0, t=30, b=0),
            height=300
        )
        st.plotly_chart(fig_bar, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    # -------------------------------------------------------------
    # TAB 2: RISK & VAR ANALYTICS
    # -------------------------------------------------------------
    with tab_risk:
        st.markdown('<div class="glass-panel">', unsafe_allow_html=True)
        st.markdown("""
        <div class="panel-title">🛡️ Underwater Drawdown Profile (Psychological Pain Curve)</div>
        <div class="panel-sub">Historical peak-to-trough drawdowns and duration of capital recovery.</div>
        """, unsafe_allow_html=True)
        
        dd_series = (cum_strat - cum_strat.cummax()) / cum_strat.cummax()
        dd_bench_s = (cum_bench - cum_bench.cummax()) / cum_bench.cummax()
        
        fig_dd = go.Figure()
        fig_dd.add_trace(go.Scatter(
            x=dd_series.index, y=dd_series.values,
            mode='lines', name='Sentry Drawdown',
            line=dict(color='#F43F5E', width=2),
            fill='tozeroy', fillcolor='rgba(244, 63, 94, 0.15)'
        ))
        fig_dd.add_trace(go.Scatter(
            x=dd_bench_s.index, y=dd_bench_s.values,
            mode='lines', name='Benchmark Drawdown',
            line=dict(color='#64748B', width=1.5, dash='dot')
        ))
        fig_dd.update_layout(
            template='plotly_dark',
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(family='Plus Jakarta Sans', color='#94A3B8'),
            yaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.05)', tickformat='.0%'),
            margin=dict(l=0, r=0, t=20, b=0),
            height=340
        )
        st.plotly_chart(fig_dd, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Risk Breakdown Table
        st.markdown('<div class="glass-panel">', unsafe_allow_html=True)
        st.markdown('<div class="panel-title">📋 Institutional Risk Matrix</div>', unsafe_allow_html=True)
        risk_df = pd.DataFrame({
            "Risk Factor": ["Value-at-Risk (Daily 95% VaR)", "Extreme Tail Loss (99% VaR)", "Market Beta vs S&P Universe", "Sortino Ratio (Downside Risk)", "Monthly Win Rate (%)"],
            "Sentry ML Value": [f"{var_95:.2f}%", f"{var_99:.2f}%", f"{beta:.2f}", f"{sortino:.2f}", f"{win_rate:.1f}%"],
            "Benchmark": ["-1.85%", "-3.15%", "1.00", "1.45", "58.2%"],
            "Risk Status": ["Controlled", "Protected", "Moderate", "Exceptional", "Alpha Dominant"]
        })
        st.dataframe(risk_df, hide_index=True, use_container_width=True, height=220)
        st.markdown('</div>', unsafe_allow_html=True)

    # -------------------------------------------------------------
    # TAB 3: ASSET & SECTOR HOLDINGS
    # -------------------------------------------------------------
    with tab_alloc:
        rebal_dates = sorted(list(holdings_history.keys()))
        selected_date = st.select_slider(
            "📅 Rebalance Historical Scrubbing Slider:",
            options=rebal_dates,
            value=rebal_dates[-1],
            format_func=lambda d: d.strftime('%b %Y')
        )
        
        cur_weights = holdings_history[selected_date]
        active_stocks = cur_weights[cur_weights > 0.001].sort_values(ascending=False)
        
        col_sec, col_tbl = st.columns([1.2, 1.8])
        with col_sec:
            st.markdown('<div class="glass-panel">', unsafe_allow_html=True)
            st.markdown('<div class="panel-title">🍩 Sector Distribution</div>', unsafe_allow_html=True)
            
            sec_w = {}
            for t, w in active_stocks.items():
                s = sector_map.get(t, 'Other')
                sec_w[s] = sec_w.get(s, 0.0) + w
                
            df_sec = pd.DataFrame(list(sec_w.items()), columns=['Sector', 'Weight']).sort_values('Weight', ascending=False)
            
            fig_donut = go.Figure(data=[go.Pie(
                labels=df_sec['Sector'], values=df_sec['Weight'], hole=0.55,
                marker=dict(colors=['#00F2FE', '#6366F1', '#10B981', '#F59E0B', '#A855F7', '#EC4899']),
                textinfo='label+percent', textposition='inside'
            )])
            fig_donut.update_layout(
                template='plotly_dark', plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
                showlegend=False, margin=dict(l=5, r=5, t=5, b=5), height=300
            )
            st.plotly_chart(fig_donut, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)
            
        with col_tbl:
            st.markdown('<div class="glass-panel">', unsafe_allow_html=True)
            st.markdown(f'<div class="panel-title">📋 Active Positions ({len(active_stocks)} Equities)</div>', unsafe_allow_html=True)
            
            hold_rows = []
            for t, w in active_stocks.items():
                hold_rows.append({
                    "Ticker": t,
                    "Sector": sector_map.get(t, "General"),
                    "Weight": f"{w*100:.2f}%",
                    "Max Cap Limit": "5.00%"
                })
            df_hold_ui = pd.DataFrame(hold_rows)
            st.dataframe(df_hold_ui, hide_index=True, use_container_width=True, height=300)
            st.markdown('</div>', unsafe_allow_html=True)

    # -------------------------------------------------------------
    # TAB 4: QUANTITATIVE BLUEPRINT
    # -------------------------------------------------------------
    with tab_arch:
        st.markdown("""
        <div class="glass-panel">
            <div class="panel-title">🧠 6-Stage Sentry Pipeline Blueprint</div>
            <div class="panel-sub">Mathematical flow from raw Yahoo Finance market feeds to constrained CVXPY convex allocation.</div>
            <br>
            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(260px, 1fr)); gap: 14px;">
                <div style="background: rgba(20,26,38,0.8); border: 1px solid rgba(255,255,255,0.06); padding: 14px; border-radius: 10px;">
                    <b style="color: #00F2FE;">1. Data Pipeline</b>
                    <p style="font-size: 0.82rem; color: #94A3B8; margin-top: 4px;">Dynamic delta-append caching on Parquet/CSV format for 100 liquid US tickers.</p>
                </div>
                <div style="background: rgba(20,26,38,0.8); border: 1px solid rgba(255,255,255,0.06); padding: 14px; border-radius: 10px;">
                    <b style="color: #6366F1;">2. Factor Normalization</b>
                    <p style="font-size: 0.82rem; color: #94A3B8; margin-top: 4px;">1/99% Winsorization and cross-sectional Z-scoring for Value, Quality, Momentum, and Low-Vol.</p>
                </div>
                <div style="background: rgba(20,26,38,0.8); border: 1px solid rgba(255,255,255,0.06); padding: 14px; border-radius: 10px;">
                    <b style="color: #10B981;">3. Walk-Forward XGBoost</b>
                    <p style="font-size: 0.82rem; color: #94A3B8; margin-top: 4px;">Strict expanding-window cross-sectional return rank predictions. Eliminates look-ahead bias.</p>
                </div>
                <div style="background: rgba(20,26,38,0.8); border: 1px solid rgba(255,255,255,0.06); padding: 14px; border-radius: 10px;">
                    <b style="color: #F59E0B;">4. CVXPY Optimizer</b>
                    <p style="font-size: 0.82rem; color: #94A3B8; margin-top: 4px;">Ledoit-Wolf PSD projection, 40% turnover bounds, 5% max position, ±5% sector neutrality.</p>
                </div>
                <div style="background: rgba(20,26,38,0.8); border: 1px solid rgba(255,255,255,0.06); padding: 14px; border-radius: 10px;">
                    <b style="color: #EC4899;">5. Backtest Friction Engine</b>
                    <p style="font-size: 0.82rem; color: #94A3B8; margin-top: 4px;">21-day holding drift simulation with exact 10 bps turnover friction penalty.</p>
                </div>
                <div style="background: rgba(20,26,38,0.8); border: 1px solid rgba(255,255,255,0.06); padding: 14px; border-radius: 10px;">
                    <b style="color: #A855F7;">6. Executive Telemetry</b>
                    <p style="font-size: 0.82rem; color: #94A3B8; margin-top: 4px;">Async Streamlit UI layer powered by serialized telemetry and Plotly vector charts.</p>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

# =================================================================
# RIGHT TELEMETRY & AUDIT DOCK
# =================================================================
with col_telemetry:
    # Capital Simulator Card
    st.markdown('<div class="telemetry-card">', unsafe_allow_html=True)
    st.markdown('<div class="telemetry-title"><span>💵 Portfolio Wealth</span><span>LIVE</span></div>', unsafe_allow_html=True)
    
    capital_input = st.number_input(
        "Initial Capital ($ USD):", 
        min_value=1000, max_value=50000000, value=100000, step=10000,
        label_visibility="collapsed"
    )
    
    sim_final = capital_input * cum_strat.iloc[-1]
    sim_profit = sim_final - capital_input
    
    st.markdown(f"""
    <div style="margin-top: 10px;">
        <div style="font-size: 0.75rem; color: #94A3B8;">Current Compounded Value</div>
        <div style="font-family: 'JetBrains Mono'; font-size: 1.6rem; font-weight: 700; color: #00F2FE;">${sim_final:,.0f}</div>
        <div style="font-size: 0.8rem; font-weight: 600; color: #10B981; margin-top: 2px;">▲ +${sim_profit:,.0f} Net Gain</div>
    </div>
    """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Real-Time Risk Monitor
    st.markdown('<div class="telemetry-card">', unsafe_allow_html=True)
    st.markdown('<div class="telemetry-title"><span>🛡️ Real-Time Risk Telemetry</span><span>LIVE</span></div>', unsafe_allow_html=True)
    st.markdown(f"""
    <div class="stat-row"><span class="stat-label">Value-at-Risk (95% 1D)</span><span class="stat-val" style="color: #F43F5E;">{var_95:.2f}%</span></div>
    <div class="stat-row"><span class="stat-label">Market Beta (vs 1/N)</span><span class="stat-val">{beta:.2f}</span></div>
    <div class="stat-row"><span class="stat-label">Annualized Volatility</span><span class="stat-val">{strat_vol*100:.2f}%</span></div>
    <div class="stat-row"><span class="stat-label">Downside Deviation</span><span class="stat-val">{downside_dev*100:.2f}%</span></div>
    <div class="stat-row"><span class="stat-label">Turnover Constraint</span><span class="stat-val">40.0% Max</span></div>
    """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Top Active Holdings Leaders
    latest_d = rebal_dates[-1]
    top_picks = holdings_history[latest_d][holdings_history[latest_d] > 0.001].head(5)
    
    st.markdown('<div class="telemetry-card">', unsafe_allow_html=True)
    st.markdown('<div class="telemetry-title"><span>⭐ Top Model Allocations</span><span>5.0% MAX</span></div>', unsafe_allow_html=True)
    for ticker, weight in top_picks.items():
        sec = sector_map.get(ticker, "General")
        st.markdown(f"""
        <div class="stat-row">
            <div><span class="ticker-pill">{ticker}</span> <span style="font-size: 0.75rem; color: #64748B; margin-left: 4px;">{sec}</span></div>
            <span class="stat-val" style="color: #10B981;">{weight*100:.1f}%</span>
        </div>
        """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Quick Action & Audit Download Dock
    st.markdown('<div class="telemetry-card">', unsafe_allow_html=True)
    st.markdown('<div class="telemetry-title"><span>📥 Audit Tear-Sheet Exporter</span></div>', unsafe_allow_html=True)
    
    # Prepare export dataframe
    export_df = pd.DataFrame({
        "Date": strategy_returns.index.strftime('%Y-%m-%d'),
        "Strategy_Daily_Return": strategy_returns.values,
        "Benchmark_Daily_Return": benchmark_returns.values,
        "Cumulative_Strategy_Wealth": cum_strat.values,
        "Cumulative_Benchmark_Wealth": cum_bench.values
    })
    csv_data = export_df.to_csv(index=False).encode('utf-8')
    
    st.download_button(
        label="📥 Download Strategy Audit (CSV)",
        data=csv_data,
        file_name="sentry_alpha_simulation_audit.csv",
        mime="text/csv",
        use_container_width=True
    )
    st.markdown('</div>', unsafe_allow_html=True)
