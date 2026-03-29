import streamlit as st
import yfinance as yf
import pandas as pd
import requests

# --- 1. CONFIGURATION ---
st.set_page_config(page_title="Oakstream Analysis", layout="wide")
st.title("🌳 Oakstream Analysis: CFO Insights")
st.markdown("### Evaluate Global Balance Sheets with Seasoned Precision")

# --- 2. THE ENGINE (Caching & Rate Limit Protection) ---
# The @st.cache_data tells the app to remember this data for 24 hours (86400 seconds)
@st.cache_data(ttl=86400)
def fetch_financial_data(ticker_symbol):
    """Fetches data securely and caches it so Yahoo doesn't ban us."""
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/91.0.4472.124 Safari/537.36'
    })
    
    company = yf.Ticker(ticker_symbol, session=session)
    # We return the raw dataframes to be cached
    return company.balance_sheet, company.info

def safe_extract(dataframe, metric_name):
    """Safely pulls a number from the balance sheet without crashing."""
    try:
        if metric_name in dataframe.index:
            val = dataframe.loc[metric_name].iloc[0]
            if pd.isna(val): # Checks if Yahoo returned a blank 'NaN'
                return None
            return float(val)
        return None
    except Exception:
        return None

# --- 3. USER INTERFACE ---
st.sidebar.header("Analysis Settings")
market = st.sidebar.radio("Select Market:", ["International (US/Global)", "India (NSE)"])

ticker_input = st.text_input("Enter Ticker (e.g. AAPL, RELIANCE, TCS):", "AAPL").strip().upper()

# Smart Suffix Logic
if market == "India (NSE)" and not ticker_input.endswith(".NS"):
    ticker = f"{ticker_input}.NS"
else:
    ticker = ticker_input

# --- 4. THE EXECUTION ---
if st.button("Run CFO Audit"):
    try:
        with st.spinner(f'Fetching and auditing {ticker}...'):
            # Pull from Cache or Download if new
            bs, info = fetch_financial_data(ticker)
            
            if bs is None or bs.empty:
                st.warning(f"Could not find Balance Sheet data for {ticker}. The company might be delisted, or the ticker is incorrect.")
            else:
                st.subheader(f"Final Report: {info.get('longName', ticker)}")
                
                # Safely extract data
                curr_assets = safe_extract(bs, 'Current Assets')
                curr_liab = safe_extract(bs, 'Current Liabilities')
                total_debt = safe_extract(bs, 'Total Debt')
                total_equity = safe_extract(bs, 'Stockholders Equity')
                
                report_data = []

                # --- LIQUIDITY MATH ---
                if curr_assets is not None and curr_liab is not None and curr_liab > 0:
                    current_ratio = curr_assets / curr_liab
                    report_data.append({
                        "Metric": "Liquidity (Current Ratio)",
                        "Value": f"{current_ratio:.2f}",
                        "CFO Verdict": "✅ Healthy" if current_ratio > 1.5 else "⚠️ Tight" if current_ratio > 1 else "🚨 Risky",
                        "Explanation": "Can they pay short-term bills? (>1.5 is ideal)."
                    })
                else:
                    report_data.append({
                        "Metric": "Liquidity (Current Ratio)",
                        "Value": "N/A",
                        "CFO Verdict": "Info",
                        "Explanation": "Data unavailable (Common for Banks/Financials)."
                    })

                # --- SOLVENCY MATH ---
                if total_debt is not None and total_equity is not None and total_equity > 0:
                    debt_to_equity = total_debt / total_equity
                    report_data.append({
                        "Metric": "Debt-to-Equity",
                        "Value": f"{debt_to_equity:.2f}",
                        "CFO Verdict": "✅ Safe" if debt_to_equity < 1 else "⚠️ Leveraged" if debt_to_equity < 2 else "🚨 High Debt",
                        "Explanation": "Risk level from borrowed money vs owned equity."
                    })
                elif total_debt is None and total_equity is not None:
                    # If total debt isn't listed, it might be zero
                    report_data.append({
                        "Metric": "Debt-to-Equity",
                        "Value": "0.00",
                        "CFO Verdict": "✅ Safe",
                        "Explanation": "Company appears to have zero long-term debt listed."
                    })

                # --- RENDER TABLE ---
                st.table(pd.DataFrame(report_data))
                
                # Disclaimer
                st.caption("Disclaimer: This tool provides automated raw data analysis based on standard financial formulas. It is not licensed financial advice. Always conduct your own due diligence before investing.")

    except Exception as e:
        if "Too Many Requests" in str(e):
            st.error("Yahoo Finance is temporarily overwhelmed. Take a breath, wait 60 seconds, and