import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st

# Streamlit Page Configuration
st.set_page_config(page_title="Stock EMA Chart", layout="wide", initial_sidebar_state="expanded")

st.title("📈 Stock Chart with 50 & 200 EMA")
ticker = st.text_input("Enter a stock ticker (e.g., AAPL, TSLA, MSFT)", "AAPL")

if ticker:
    # Validate input
    if not ticker.isalnum():
        st.error("Invalid ticker format. Please enter a valid alphanumeric ticker.")
    else:
        try:
            # Fetch data from yfinance with caching
            @st.cache_data
            def fetch_data(ticker):
                return yf.download(ticker, period="1y", interval="1d")

            df = fetch_data(ticker)

            if df.empty:
                st.error("No data found for the specified ticker. Please check the ticker.")
            else:
                # Calculate EMAs
                df['EMA50'] = df['Close'].ewm(span=50, adjust=False).mean()
                df['EMA200'] = df['Close'].ewm(span=200, adjust=False).mean()

                # Plotting
                fig, ax = plt.subplots(figsize=(12, 6))
                ax.plot(df.index, df['Close'], label='Closing Price', color='black')
                ax.plot(df.index, df['EMA50'], label='50 EMA', color='blue')
                ax.plot(df.index, df['EMA200'], label='200 EMA', color='red')
                ax.set_title(f"{ticker.upper()} - 50 & 200 EMA")
                ax.set_xlabel("Date")
                ax.set_ylabel("Price (USD)")
                ax.legend()

                st.pyplot(fig)
        except Exception as e:
            st.error(f"Error fetching data: {e}")
