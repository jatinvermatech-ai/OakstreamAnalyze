import streamlit as st
import yfinance as yf

st.title("🌍 Global CFO Analyzer")

# User chooses the market
market = st.radio("Select Market:", ["International (US)", "India (NSE)"])

ticker_input = st.text_input("Enter Company Ticker:", "AAPL")

# The logic that handles the "Suffix" automatically
if market == "India (NSE)":
    # If the user forgot to type .NS, the app adds it for them
    if not ticker_input.endswith(".NS"):
        ticker = f"{ticker_input.upper()}.NS"
    else:
        ticker = ticker_input.upper()
else:
    ticker = ticker_input.upper()

st.write(f"Analyzing: **{ticker}**")

# Now pull the data
try:
    company = yf.Ticker(ticker)
    # Pulling the Balance Sheet
    balance_sheet = company.balance_sheet
    
    if balance_sheet.empty:
        st.error("Could not find data. Please check the ticker symbol.")
    else:
        st.success(f"Data for {ticker} loaded successfully!")
        # Your CFO Formula logic goes here...
except Exception as e:
    st.error(f"Error: {e}")