import streamlit as st
import yfinance as yf
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import pandas as pd

# Page config
st.set_page_config(page_title="Stock EMA Chart", page_icon="📈", layout="centered")

# Custom CSS for styling
st.markdown("""
    <style>
    .main { background-color: #F3F6FA; }
    .stTextInput>div>div>input { background-color: #e6f0ff; }
    .stButton>button { background-color: #4F8BF9; color: white; font-weight: bold;}
    .stPlotlyChart, .stImage { border-radius: 12px; }
    </style>
""", unsafe_allow_html=True)

# Title and description
st.title("📈 Stock EMA Visualizer")
st.markdown("""
Enter a stock ticker to visualize its closing price along with **50 EMA** and **200 EMA**.<br>
*Example: `AAPL`, `MSFT`, `TSLA`, `GOOGL`, `NVDA`*  
""", unsafe_allow_html=True)

# User input
ticker = st.text_input("Enter Stock Ticker", value="AAPL", max_chars=10).upper()

# Date range
col1, col2 = st.columns(2)
with col1:
    start_date = st.date_input("Start Date", pd.to_datetime("2022-01-01"))
with col2:
    end_date = st.date_input("End Date", pd.to_datetime("today"))

if st.button("Fetch & Plot Data"):
    try:
        # Fetch data
        data = yf.download(ticker, start=start_date, end=end_date)
        if data.empty:
            st.error(f"No data found for ticker `{ticker}`.")
        else:
            # Calculate EMAs
            data["EMA50"] = data["Close"].ewm(span=50, adjust=False).mean()
            data["EMA200"] = data["Close"].ewm(span=200, adjust=False).mean()
            
            # Plot
            fig, ax = plt.subplots(figsize=(10, 6))
            ax.plot(data.index, data["Close"], label="Close Price", color="#0072B2", linewidth=2)
            ax.plot(data.index, data["EMA50"], label="50 EMA", color="#FF9800", linewidth=2, linestyle="--")
            ax.plot(data.index, data["EMA200"], label="200 EMA", color="#E91E63", linewidth=2, linestyle="--")
            ax.set_title(f"{ticker} Price with 50 EMA & 200 EMA", fontsize=18, fontweight='bold')
            ax.set_xlabel("Date")
            ax.set_ylabel("Price (USD)")
            ax.legend()
            ax.grid(alpha=0.2)
            ax.xaxis.set_major_locator(mdates.MonthLocator())
            ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))
            plt.xticks(rotation=30)
            plt.tight_layout()

            st.pyplot(fig)
    except Exception as e:
        st.error(f"An error occurred: {e}")

st.markdown("""
---
*Made with ❤️ using [Streamlit](https://streamlit.io/) & [yfinance](https://pypi.org/project/yfinance/)*
""")
