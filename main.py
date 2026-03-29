import streamlit as st
import yfinance as yf
import pandas as pd
import requests

# --- 1. CONFIGURATION ---
st.set_page_config(page_title="Oakstream Analysis", layout="wide")
st.title("🌳 Oakstream Analysis: CFO Insights")

@st.cache_data(ttl=86400)
def fetch_financial_data(ticker_symbol):
    session = requests.Session()
    session.headers.update({'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/91.0.4472.124 Safari/537.36'})
    company = yf.Ticker(ticker_symbol, session=session)
    return company.balance_sheet, company.info

def safe_extract(dataframe, metric_name):
    try:
        if metric_name in dataframe.index:
            val = dataframe.loc[metric_name].iloc[0]
            return float(val) if not pd.isna(val) else None
        return None
    except:
        return None

# --- 2. USER INTERFACE ---
st.sidebar.header("Settings")
market = st.sidebar.radio("Market:", ["International (US/Global)", "India (NSE)"])
ticker_input = st.text_input("Enter Ticker:", "AAPL").strip().upper()

ticker = f"{ticker_input}.NS" if (market == "India (NSE)" and not ticker_input.endswith(".NS")) else ticker_input

# --- 3. EXECUTION ---
if st.button("Run CFO Audit"):
    try:
        with st.spinner(f'Auditing {ticker}...'):
            bs, info = fetch_financial_data(ticker)
            
            if bs is None or bs.empty:
                st.error("No data found. Check ticker or try again later.")
            else:
                st.subheader(f"Report: {info.get('longName', ticker)}")
                curr_assets = safe_extract(bs, 'Current Assets')
                curr_liab = safe_extract(bs, 'Current Liabilities')
                total_debt = safe_extract(bs, 'Total Debt')
                total_equity = safe_extract(bs, 'Stockholders Equity')
                
                report = []
                if curr_assets and curr_liab and curr_liab > 0:
                    ratio = curr_assets / curr_liab
                    status = "✅ Healthy" if ratio > 1.5 else "⚠️ Tight" if ratio > 1 else "🚨 Risky"
                    report.append({"Metric": "Liquidity", "Value": f"{ratio:.2f}", "Verdict": status, "Note": "Can they pay bills?"})

                if total_debt is not None and total_equity and total_equity > 0:
                    de_ratio = total_debt / total_equity
                    status = "✅ Safe" if de_ratio < 1 else "⚠️ Leveraged" if de_ratio < 2 else "🚨 High Debt"
                    report.append({"Metric": "Debt-to-Equity", "Value": f"{de_ratio:.2f}", "Verdict": status, "Note": "Risk from loans."})
                
                if not report:
                    st.warning("Insufficient data to generate ratios for this specific company.")
                else:
                    st.table(pd.DataFrame(report))
                st.caption("Data provided by Yahoo Finance. Not financial advice.")

    except Exception as e:
        st.error(f"App Error: {str(e)}")
