import streamlit as st
import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime, timedelta

# --- Page Configuration (Optional but Recommended) ---
st.set_page_config(
    page_title="Simple Stock Chart",
    page_icon="📈", # You can use emojis
    layout="wide" # Use wide layout for better chart display
)

# --- Styling (Optional - Add some custom CSS) ---
st.markdown("""
<style>
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        padding-left: 3rem;
        padding-right: 3rem;
    }
    .stButton>button {
        color: #4F8BF9;
        border-radius: 50px;
        height: 3em;
        width: 100%; /* Make button wider */
    }
    .stTextInput>div>div>input {
        border-radius: 10px;
    }
    h1 {
        color: #4F8BF9; /* Title color */
    }
</style>
""", unsafe_allow_html=True)

# --- App Title ---
st.title("📈 Simple Stock Price Viewer")
st.write("Enter a stock ticker symbol to see its price chart with 50 & 200 EMA.")

# --- User Input Area ---
col1, col2 = st.columns([2, 1]) # Create columns for layout

with col1:
    ticker_symbol = st.text_input(
        "Enter Stock Ticker Symbol:",
        value="AAPL", # Default value
        help="E.g., AAPL, GOOGL, MSFT,
