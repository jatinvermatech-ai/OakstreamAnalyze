import streamlit as st
import yfinance as yf
import pandas as pd

# 1. Page Configuration
st.set_page_config(page_title="Oakstream Analysis", layout="wide")
st.title("🌳 Oakstream Analysis: CFO Insights")
st.markdown("### Evaluate Global Balance Sheets with Seasoned Precision")

# 2. Sidebar for User Liberty
st.sidebar.header("Analysis Settings")
market = st.sidebar.radio("Select Market:", ["International (US/Global)", "India (NSE)"])
method = st.sidebar.selectbox("Methodology:", ["Standard Health Audit", "Liquidity Scrutiny"])

# 3. Ticker Input Logic
ticker_input = st.text_input("Enter Ticker (e.g. AAPL or RELIANCE):", "AAPL").strip().upper()

if market == "India (NSE)" and not ticker_input.endswith(".NS"):
    ticker = f"{ticker_input}.NS"
else:
    ticker = ticker_input

# 4. Data Fetching & Analysis
if st.button("Run CFO Audit"):
    try:
        with st.spinner(f'Fetching data for {ticker}...'):
            company = yf.Ticker(ticker)
            # Fetching Balance Sheet
            bs = company.balance_sheet
            info = company.info
            
            if bs.empty:
                st.error("No Balance Sheet data found. Try a different ticker.")
            else:
                # RAW DATA CALCULATIONS
                # We use .iloc[0] to get the most recent year's data
                curr_assets = bs.loc['Current Assets'].iloc[0]
                curr_liab = bs.loc['Current Liabilities'].iloc[0]
                total_debt = bs.loc.get('Total Debt', pd.Series([0])).iloc[0]
                total_equity = bs.loc['Stockholders Equity'].iloc[0]
                
                # Formulas
                current_ratio = curr_assets / curr_liab
                debt_to_equity = total_debt / total_equity
                
                # 5. THE LAYMAN REPORT TABLE
                st.subheader(f"Final Report: {info.get('longName', ticker)}")
                
                report_data = [
                    {
                        "Metric": "Liquidity (Current Ratio)",
                        "Value": f"{current_ratio:.2f}",
                        "CFO Verdict": "✅ Healthy" if current_ratio > 1.5 else "⚠️ Tight" if current_ratio > 1 else "🚨 Risky",
                        "Layman Explanation": "Can they pay short-term bills? (Above 1.5 is ideal)."
                    },
                    {
                        "Metric": "Debt-to-Equity",
                        "Value": f"{debt_to_equity:.2f}",
                        "CFO Verdict": "✅ Safe" if debt_to_equity < 1 else "⚠️ Leveraged" if debt_to_equity < 2 else "🚨 High Debt",
                        "Layman Explanation": "How much does the company rely on loans vs its own money?"
                    },
                    {
                        "Metric": "Cash Position",
                        "Value": f"{info.get('totalCash', 0):,}",
                        "CFO Verdict": "Info",
                        "Layman Explanation": "Total raw cash sitting in the bank."
                    }
                ]
                
                st.table(pd.DataFrame(report_data))
                
                # Education Section
                with st.expander("📚 How to read this like a Pro"):
                    st.write("""
                    - **Current Ratio:** If this is below 1, the company might struggle to pay immediate debts.
                    - **Debt-to-Equity:** A 'Seasoned CFO' looks for companies that grow using their own profit, not just borrowing.
                    - **Note:** This is raw data analysis, not financial advice.
                    """)
                    
    except Exception as e:
        st.error(f"An error occurred: {e}. Check if the ticker symbol is correct for the selected market.")