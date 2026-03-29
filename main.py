import streamlit as st
import yfinance as yf
import pandas as pd

# 1. PAGE SETUP
st.set_page_config(page_title="Oakstream Analysis", layout="wide")
st.title("🌳 Oakstream Analysis: CFO Insights")

# 2. CACHED DATA FETCHING
@st.cache_data(ttl=3600)
def fetch_financial_data(ticker_symbol):
    # We removed the 'session' part entirely to satisfy the new API requirement
    company = yf.Ticker(ticker_symbol)
    return company.balance_sheet, company.info

def safe_extract(dataframe, metric_name):
    try:
        if metric_name in dataframe.index:
            val = dataframe.loc[metric_name].iloc[0]
            return float(val) if not pd.isna(val) else None
        return None
    except:
        return None

# 3. SIDEBAR & INPUT
st.sidebar.header("Settings")
market = st.sidebar.radio("Market:", ["International (US/Global)", "India (NSE)"])
ticker_input = st.text_input("Enter Ticker:", "AAPL").strip().upper()

ticker = f"{ticker_input}.NS" if (market == "India (NSE)" and not ticker_input.endswith(".NS")) else ticker_input

# 4. RUN ANALYSIS
if st.button("Run CFO Audit"):
    try:
        with st.spinner(f'Auditing {ticker}...'):
            bs, info = fetch_financial_data(ticker)
            
            if bs is None or bs.empty:
                st.error("No Balance Sheet found. Yahoo Finance might be blocking the request or the ticker is wrong.")
            else:
                st.subheader(f"Report: {info.get('longName', ticker)}")
                
                # Extracting raw data
                curr_assets = safe_extract(bs, 'Current Assets')
                curr_liab = safe_extract(bs, 'Current Liabilities')
                total_debt = safe_extract(bs, 'Total Debt')
                total_equity = safe_extract(bs, 'Stockholders Equity')
                
                report = []
                
                # Liquidity Ratio
                if curr_assets and curr_liab and curr_liab > 0:
                    ratio = curr_assets / curr_liab
                    status = "✅ Healthy" if ratio > 1.5 else "⚠️ Tight" if ratio > 1 else "🚨 Risky"
                    report.append({"Metric": "Liquidity", "Value": f"{ratio:.2f}", "Verdict": status, "Note": "Can they pay short-term bills?"})

                # Debt to Equity
                if total_debt is not None and total_equity and total_equity > 0:
                    de_ratio = total_debt / total_equity
                    status = "✅ Safe" if de_ratio < 1 else "⚠️ Leveraged" if de_ratio < 2 else "🚨 High Debt"
                    report.append({"Metric": "Debt-to-Equity", "Value": f"{de_ratio:.2f}", "Verdict": status, "Note": "Risk from borrowed money."})
                
                if report:
                    st.table(pd.DataFrame(report))
                else:
                    st.warning("Data found, but standard ratios couldn't be calculated for this specific sector.")
                
                st.caption("Disclaimer: Raw data from Yahoo Finance. Not financial advice.")

    except Exception as e:
        st.error(f"App Error: {str(e)}")
