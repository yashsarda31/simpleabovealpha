
import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from datetime import date, timedelta

# -------------------------------
# Streamlit Page Configuration
# -------------------------------
st.set_page_config(
    page_title="Stock EMA Visualizer",
    page_icon="📈",
    layout="centered"
)

# -------------------------------
# App Title
# -------------------------------
st.title("📈 Stock EMA Visualizer")
st.markdown("Enter a stock ticker symbol below to see the 50-day and 200-day EMA plotted with the closing price.")

# -------------------------------
# Input Section
# -------------------------------
ticker = st.text_input("Enter a stock ticker (e.g., AAPL, MSFT, TSLA):", value="AAPL").upper()

# Date range (last 1 year)
end_date = date.today()
start_date = end_date - timedelta(days=365)

# -------------------------------
# Fetch & Process Data
# -------------------------------
@st.cache_data
def get_stock_data(ticker_symbol):
    data = yf.download(ticker_symbol, start=start_date, end=end_date)
    if data.empty:
        return None
    data['50 EMA'] = data['Close'].ewm(span=50, adjust=False).mean()
    data['200 EMA'] = data['Close'].ewm(span=200, adjust=False).mean()
    return data

# Fetch data
data = get_stock_data(ticker)

# -------------------------------
# Display Chart
# -------------------------------
if data is None:
    st.error("⚠️ Failed to fetch data. Please check the ticker symbol.")
else:
    fig = go.Figure()

    fig.add_trace(go.Scatter(x=data.index, y=data['Close'], mode='lines', name='Close Price', line=dict(color='blue')))
    fig.add_trace(go.Scatter(x=data.index, y=data['50 EMA'], mode='lines', name='50 EMA', line=dict(color='orange')))
    fig.add_trace(go.Scatter(x=data.index, y=data['200 EMA'], mode='lines', name='200 EMA', line=dict(color='green')))

    fig.update_layout(
        title=f"{ticker} Price with 50 & 200 EMA",
        xaxis_title="Date",
        yaxis_title="Price (USD)",
        template="plotly_white",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )

    st.plotly_chart(fig, use_container_width=True)

# -------------------------------
# Footer
# -------------------------------
st.markdown("---")
st.markdown("Made with ❤️ using [Streamlit](https://streamlit.io/) and [yfinance](https://pypi.org/project/yfinance/)")
