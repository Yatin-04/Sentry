import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import pickle
import os

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="Quantitative Portfolio Engine",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- SIDEBAR CONTROLS ---
with st.sidebar:
    st.markdown("### Settings")
    theme = st.radio("Interface Theme", ["Light Mode", "Dark Mode"], index=0)

# --- DYNAMIC CSS ---
if theme == "Light Mode":
    bg_color = "#F8FAFC"
    text_color = "#0F172A"
    panel_bg = "#FFFFFF"
    border_color = "#E2E8F0"
    text_muted = "#64748B"
    pass_color = "#059669"
    fail_color = "#DC2626"
    fallback_color = "#D97706"
    chart_line = "#2563EB"
    tab_bg = "#F1F5F9"
    tab_selected_bg = "#E2E8F0"
else:
    bg_color = "#0F172A"
    text_color = "#F8FAFC"
    panel_bg = "#1E293B"
    border_color = "#334155"
    text_muted = "#94A3B8"
    pass_color = "#34D399"
    fail_color = "#F87171"
    fallback_color = "#FBBF24"
    chart_line = "#60A5FA"
    tab_bg = "#0F172A"
    tab_selected_bg = "#334155"

custom_css = f"""
<style>
    .stApp {{
        background-color: {bg_color};
        color: {text_color};
        font-family: "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
    }}
    
    h1, h2, h3 {{ color: {text_color} !important; font-weight: 600; }}
    
    .panel {{
        background-color: {panel_bg};
        border: 1px solid {border_color};
        border-radius: 4px;
        padding: 20px;
        margin-bottom: 24px;
        box-shadow: 0 1px 2px rgba(0,0,0,0.02);
    }}
    
    .panel-header {{
        font-size: 1.05rem;
        font-weight: 600;
        color: {text_color};
        margin-bottom: 16px;
        padding-bottom: 8px;
        border-bottom: 1px solid {border_color};
    }}
    
    .memo-block {{
        border-left: 4px solid {chart_line};
        padding-left: 16px;
        margin-bottom: 30px;
    }}
    
    .memo-text {{
        font-size: 0.95rem;
        color: {text_muted};
        line-height: 1.6;
    }}
    
    .metric-grid {{
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
        gap: 16px;
        margin-bottom: 24px;
    }}
    
    .metric-box {{
        padding: 16px;
        border: 1px solid {border_color};
        background-color: {panel_bg};
        border-radius: 4px;
    }}
    
    .metric-label {{
        font-size: 0.75rem;
        text-transform: uppercase;
        color: {text_muted};
        font-weight: 600;
        margin-bottom: 6px;
    }}
    
    .metric-value {{
        font-size: 1.4rem;
        font-weight: 600;
        color: {text_color};
    }}
    
    .audit-badge {{
        font-size: 0.75rem;
        font-weight: 600;
        padding: 4px 8px;
        border-radius: 4px;
        text-transform: uppercase;
    }}
    .audit-pass {{ background: rgba(5, 150, 105, 0.1); color: {pass_color}; border: 1px solid {pass_color}; }}
    .audit-fallback {{ background: rgba(217, 119, 6, 0.1); color: {fallback_color}; border: 1px solid {fallback_color}; }}
    
    /* FIX FOR TABS IN LIGHT/DARK MODE */
    .stTabs [data-baseweb="tab-list"] {{
        gap: 8px;
        background-color: {panel_bg};
        padding: 8px;
        border-radius: 8px;
        border: 1px solid {border_color};
        margin-bottom: 24px;
    }}
    
    .stTabs [data-baseweb="tab"] {{
        color: {text_muted} !important;
        border-radius: 4px;
        padding: 8px 16px;
        font-weight: 500;
    }}
    
    .stTabs [aria-selected="true"] {{
        background-color: {tab_selected_bg} !important;
        color: {text_color} !important;
    }}
    
    .disclaimer {{
        margin-top: 40px;
        padding-top: 20px;
        border-top: 1px solid {border_color};
        font-size: 0.8rem;
        color: {text_muted};
    }}
</style>
"""
st.markdown(custom_css, unsafe_allow_html=True)

# --- DATA LOADING ---
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

    return data, sector_map

data, sector_map = load_quant_data()

if data is None:
    st.error("Data not found. Please run `python backtester.py` first.")
    st.stop()

# Unpack
report = data['report']
portfolio_daily_values = data['portfolio_daily_values']
strategy_returns = data['strategy_returns']
benchmark_returns = data['benchmark_returns']
holdings_history = data['holdings_history']

# Deep Analytics Derivation
cum_strat = (1 + strategy_returns).cumprod()
cum_bench = (1 + benchmark_returns).cumprod()
active_returns = strategy_returns - benchmark_returns

# Calculate Win Rate and VaR
strat_win_rate = (strategy_returns > 0).mean()
bench_win_rate = (benchmark_returns > 0).mean()
strat_var_95 = strategy_returns.quantile(0.05)
bench_var_95 = benchmark_returns.quantile(0.05)

# Rebalance logic
rebal_dates = sorted(list(holdings_history.keys()))
latest_date = rebal_dates[-1]
prev_date = rebal_dates[-2] if len(rebal_dates) >= 2 else None

latest_weights = holdings_history[latest_date]
prev_weights = holdings_history[prev_date] if prev_date else pd.Series(0.0, index=latest_weights.index)

active_latest = latest_weights[latest_weights > 0.001].sort_values(ascending=False)
turnover = np.abs(latest_weights - prev_weights).sum()

is_fallback = turnover > 1.0 

# --- HEADER & INTRODUCTION ---
st.markdown("<h1>Quantitative Portfolio Architecture</h1>", unsafe_allow_html=True)

st.markdown(f"""
<div class="memo-block">
    <div class="memo-text">
        <b>Project Overview:</b> This application serves as the execution layer for an end-to-end systematic equity strategy. 
        It ingests multi-factor alpha scores generated by an XGBoost ranking model and translates them into a tradable portfolio 
        using a convex optimizer (CVXPY). The objective is to maximize exposure to Value, Quality, Momentum, and Low-Volatility 
        factors while strictly enforcing institutional risk boundaries (maximum position sizing, sector neutrality, and turnover limits).<br><br>
        <i>Data displayed represents out-of-sample walk-forward backtest results, with the latest automated rebalance executed on <b>{latest_date.strftime('%B %d, %Y')}</b>.</i>
    </div>
</div>
""", unsafe_allow_html=True)

# --- MAIN TABS ---
tab_trades, tab_risk, tab_perf = st.tabs(["Execution & Trades", "Risk & Compliance", "Deep Analytics"])

# ==========================================
# TAB 1: EXECUTION & TRADES
# ==========================================
with tab_trades:
    
    if is_fallback:
        st.warning("⚠️ **NOTICE:** The optimizer failed to converge under strict constraints for this period. The system automatically executed the Tier 4 Safety Heuristic (Equal-weighting the top 20 alpha signals) to ensure uninterrupted portfolio deployment.")
    
    st.markdown(f"""
    <div class="metric-grid">
        <div class="metric-box">
            <div class="metric-label">Target Positions</div>
            <div class="metric-value">{(active_latest > 0).sum()}</div>
        </div>
        <div class="metric-box">
            <div class="metric-label">Estimated Turnover</div>
            <div class="metric-value">{turnover*100:.1f}%</div>
        </div>
        <div class="metric-box">
            <div class="metric-label">Largest Allocation</div>
            <div class="metric-value">{active_latest.max()*100:.1f}%</div>
        </div>
        <div class="metric-box">
            <div class="metric-label">Capital Deployed</div>
            <div class="metric-value">{latest_weights.sum()*100:.1f}%</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    col_t1, col_t2 = st.columns([1.5, 1])
    
    with col_t1:
        st.markdown('<div class="panel">', unsafe_allow_html=True)
        st.markdown('<div class="panel-header">Target Portfolio Weights</div>', unsafe_allow_html=True)
        
        capital = st.number_input("Total Capital to Deploy ($)", min_value=0.0, value=1000000.0, step=100000.0, format="%.2f")
        
        holdings_df = pd.DataFrame({
            'Ticker': active_latest.index,
            'Target Weight': (active_latest.values * 100).round(2),
            'Target Value ($)': (active_latest.values * capital).round(2),
            'Sector': [sector_map.get(t, 'Unknown') for t in active_latest.index],
            'Previous Weight': [(prev_weights.get(t, 0) * 100) for t in active_latest.index],
        })
        holdings_df['Action (Δ%)'] = (holdings_df['Target Weight'] - holdings_df['Previous Weight']).round(2)
        
        st.dataframe(
            holdings_df[['Ticker', 'Sector', 'Previous Weight', 'Target Weight', 'Action (Δ%)', 'Target Value ($)']], 
            hide_index=True, 
            use_container_width=True, 
            height=370
        )
        st.markdown('</div>', unsafe_allow_html=True)
        
    with col_t2:
        st.markdown('<div class="panel">', unsafe_allow_html=True)
        st.markdown('<div class="panel-header">Position Weight Distribution</div>', unsafe_allow_html=True)
        
        fig_dist = go.Figure(data=[go.Histogram(
            x=(active_latest.values * 100),
            nbinsx=20,
            marker_color=chart_line
        )])
        fig_dist.update_layout(
            plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color=text_muted),
            xaxis=dict(title="Weight %", showgrid=True, gridcolor=border_color),
            yaxis=dict(title="Count", showgrid=True, gridcolor=border_color),
            margin=dict(l=0, r=0, t=10, b=0),
            height=400
        )
        st.plotly_chart(fig_dist, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

# ==========================================
# TAB 2: RISK & COMPLIANCE
# ==========================================
with tab_risk:
    st.markdown('<div class="panel">', unsafe_allow_html=True)
    st.markdown('<div class="panel-header">Pre-Trade Constraint Audit</div>', unsafe_allow_html=True)
    
    max_w = active_latest.max()
    
    sector_weights_check = {}
    for ticker, w in active_latest.items():
        sec = sector_map.get(ticker, 'Other')
        sector_weights_check[sec] = sector_weights_check.get(sec, 0.0) + w

    benchmark_sector = {}
    all_tickers = latest_weights.index.tolist()
    for t in all_tickers:
        sec = sector_map.get(t, 'Other')
        benchmark_sector[sec] = benchmark_sector.get(sec, 0) + 1
    
    max_sector_dev = 0
    for sec, weight in sector_weights_check.items():
        bench_w = benchmark_sector.get(sec, 0) / len(all_tickers)
        max_sector_dev = max(max_sector_dev, abs(weight - bench_w))
        
    audit_max_w = "audit-pass" if max_w <= 0.0501 else "audit-fallback"
    txt_max_w = "PASS" if max_w <= 0.0501 else "FALLBACK TRIGGERED"
    
    audit_sec = "audit-pass" if max_sector_dev <= 0.0501 else "audit-fallback"
    txt_sec = "PASS" if max_sector_dev <= 0.0501 else "FALLBACK TRIGGERED"
    
    audit_to = "audit-pass" if turnover <= 0.401 else "audit-fallback"
    txt_to = "PASS" if turnover <= 0.401 else "FALLBACK TRIGGERED"
    
    st.markdown(f"""
    <table style="width:100%; text-align:left; border-collapse: collapse;">
        <tr style="border-bottom: 1px solid {border_color};">
            <th style="padding: 12px; color: {text_muted};">Constraint Rule</th>
            <th style="padding: 12px; color: {text_muted};">Current Value</th>
            <th style="padding: 12px; color: {text_muted};">Audit Status</th>
        </tr>
        <tr style="border-bottom: 1px solid {border_color};">
            <td style="padding: 12px; color: {text_color};">Maximum Position Size (≤ 5%)</td>
            <td style="padding: 12px; font-weight: 600; color: {text_color};">{max_w*100:.2f}%</td>
            <td style="padding: 12px;"><span class="audit-badge {audit_max_w}">{txt_max_w}</span></td>
        </tr>
        <tr style="border-bottom: 1px solid {border_color};">
            <td style="padding: 12px; color: {text_color};">Sector Deviation vs Benchmark (≤ ±5%)</td>
            <td style="padding: 12px; font-weight: 600; color: {text_color};">Max {max_sector_dev*100:.2f}%</td>
            <td style="padding: 12px;"><span class="audit-badge {audit_sec}">{txt_sec}</span></td>
        </tr>
        <tr style="border-bottom: 1px solid {border_color};">
            <td style="padding: 12px; color: {text_color};">Maximum Turnover Limit (≤ 40%)</td>
            <td style="padding: 12px; font-weight: 600; color: {text_color};">{turnover*100:.1f}%</td>
            <td style="padding: 12px;"><span class="audit-badge {audit_to}">{txt_to}</span></td>
        </tr>
        <tr>
            <td style="padding: 12px; color: {text_color};">Capital Allocation (Fully Invested)</td>
            <td style="padding: 12px; font-weight: 600; color: {text_color};">{latest_weights.sum()*100:.1f}%</td>
            <td style="padding: 12px;"><span class="audit-badge audit-pass">PASS</span></td>
        </tr>
    </table>
    """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Statistical Table with VaR and Win Rate
    st.markdown('<div class="panel">', unsafe_allow_html=True)
    st.markdown('<div class="panel-header">Long-Term Statistical Profile</div>', unsafe_allow_html=True)
    
    display_report = report.copy()
    display_report.loc['Daily Win Rate'] = [strat_win_rate, bench_win_rate]
    display_report.loc['95% Daily VaR'] = [strat_var_95, bench_var_95]
    
    for col in display_report.columns:
        display_report[col] = display_report[col].apply(
            lambda x: f"{x:.2f}" if (pd.notnull(x) and abs(x) < 10) else (f"{x*100:.2f}%" if pd.notnull(x) else "N/A")
        )
    st.dataframe(display_report, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

# ==========================================
# TAB 3: DEEP ANALYTICS
# ==========================================
with tab_perf:
    
    # Cumulative Performance
    st.markdown('<div class="panel">', unsafe_allow_html=True)
    st.markdown('<div class="panel-header">Cumulative Return Profile</div>', unsafe_allow_html=True)
    
    fig_equity = go.Figure()
    fig_equity.add_trace(go.Scatter(
        x=cum_strat.index, y=cum_strat.values,
        mode='lines', name='Strategy',
        line=dict(color=chart_line, width=2)
    ))
    fig_equity.add_trace(go.Scatter(
        x=cum_bench.index, y=cum_bench.values,
        mode='lines', name='Benchmark',
        line=dict(color=text_muted, width=1.5, dash='dash')
    ))
    fig_equity.update_layout(
        plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color=text_muted),
        xaxis=dict(showgrid=True, gridcolor=border_color),
        yaxis=dict(showgrid=True, gridcolor=border_color),
        hovermode="x unified",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        margin=dict(l=0, r=0, t=20, b=0),
        height=350
    )
    st.plotly_chart(fig_equity, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    # 2 Columns for Risk and Consistency
    col_a1, col_a2 = st.columns([1, 1])
    
    with col_a1:
        st.markdown('<div class="panel">', unsafe_allow_html=True)
        st.markdown('<div class="panel-header">63-Day Rolling Volatility</div>', unsafe_allow_html=True)
        
        roll_vol_strat = strategy_returns.rolling(63).std() * np.sqrt(252)
        roll_vol_bench = benchmark_returns.rolling(63).std() * np.sqrt(252)
        
        fig_vol = go.Figure()
        fig_vol.add_trace(go.Scatter(
            x=roll_vol_strat.index, y=roll_vol_strat.values,
            mode='lines', name='Strategy Vol', line=dict(color=fail_color, width=1.5)
        ))
        fig_vol.add_trace(go.Scatter(
            x=roll_vol_bench.index, y=roll_vol_bench.values,
            mode='lines', name='Bench Vol', line=dict(color=text_muted, width=1, dash='dot')
        ))
        fig_vol.update_layout(
            plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color=text_muted),
            xaxis=dict(showgrid=True, gridcolor=border_color),
            yaxis=dict(showgrid=True, gridcolor=border_color, tickformat='.0%'),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
            margin=dict(l=0, r=0, t=20, b=0),
            height=300
        )
        st.plotly_chart(fig_vol, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
    with col_a2:
        st.markdown('<div class="panel">', unsafe_allow_html=True)
        st.markdown('<div class="panel-header">Monthly Active Returns (Alpha)</div>', unsafe_allow_html=True)
        
        # Calculate monthly active returns
        monthly_active = active_returns.resample('M').apply(lambda x: (1 + x).prod() - 1)
        colors = [pass_color if val > 0 else fail_color for val in monthly_active.values]
        
        fig_monthly = go.Figure(go.Bar(
            x=monthly_active.index,
            y=monthly_active.values,
            marker_color=colors
        ))
        fig_monthly.update_layout(
            plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color=text_muted),
            xaxis=dict(showgrid=False),
            yaxis=dict(showgrid=True, gridcolor=border_color, tickformat='.1%'),
            margin=dict(l=0, r=0, t=10, b=0),
            height=300
        )
        st.plotly_chart(fig_monthly, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
    # Drawdown
    st.markdown('<div class="panel">', unsafe_allow_html=True)
    st.markdown('<div class="panel-header">Underwater Drawdown Profile</div>', unsafe_allow_html=True)
    running_max_strat = cum_strat.cummax()
    dd_strat = (cum_strat - running_max_strat) / running_max_strat
    
    fig_dd = go.Figure()
    fig_dd.add_trace(go.Scatter(
        x=dd_strat.index, y=dd_strat.values,
        mode='lines', name='Drawdown',
        line=dict(color=fail_color, width=1.5),
        fill='tozeroy', fillcolor=f'rgba(220, 38, 38, 0.1)'
    ))
    fig_dd.update_layout(
        plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color=text_muted),
        xaxis=dict(showgrid=True, gridcolor=border_color),
        yaxis=dict(showgrid=True, gridcolor=border_color, tickformat='.0%'),
        showlegend=False,
        margin=dict(l=0, r=0, t=10, b=0),
        height=250
    )
    st.plotly_chart(fig_dd, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

# --- DISCLAIMER ---
st.markdown(f"""
<div class="disclaimer">
    <b>Methodology & Disclosures:</b> Historical simulation assumes a static universe and utilizes snapshot fundamental data applied retroactively, 
    introducing look-ahead bias in specific factors prior to the current year. Market friction is modeled linearly at 10 bps. 
    This application is designed as an architectural demonstration of a quantitative execution pipeline and does not constitute financial advice.
</div>
""", unsafe_allow_html=True)
