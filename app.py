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
        color: white; /* White text */
        background-color: #4F8BF9; /* Blue background */
        border: none; /* No border */
        border-radius: 50px; /* Rounded corners */
        padding: 0.75em 1.5em; /* Padding */
        font-weight: bold;
        transition: background-color 0.3s ease; /* Smooth hover effect */
        width: 100%; /* Make button fill column width */
        margin-top: 1.8em; /* Add some space above the button */
    }
    .stButton>button:hover {
        background-color: #3A6CB4; /* Darker blue on hover */
        color: white;
    }
    .stTextInput>div>div>input {
        border-radius: 10px; /* Rounded input field */
        border: 1px solid #ccc;
    }
    .stDateInput>div>div>input {
        border-radius: 10px; /* Rounded date input */
        border: 1px solid #ccc;
    }
    h1 {
        color: #2c3e50; /* Darker title color */
        text-align: center; /* Center title */
        padding-bottom: 0.5em;
    }
    .stPlotlyChart { /* If using Plotly */
        border-radius: 10px;
        overflow: hidden; /* Ensures border radius applies */
    }
     /* Style the headers for data table */
    .dataframe th {
        background-color: #4F8BF9;
        color: white;
        text-align: left;
    }
    /* Style the dataframe rows */
    .dataframe tr:nth-child(even) {
        background-color: #f2f2f2;
    }
</style>
""", unsafe_allow_html=True)

# --- App Title ---
st.title("📈 Simple Stock Price Viewer")
st.write("Enter a stock ticker symbol to see its price chart with 50 & 200 Day EMAs.")
st.markdown("---") # Divider

# --- User Input Area ---
col1, col2, col3 = st.columns([2, 1, 1]) # Create columns for layout

with col1:
    ticker_symbol = st.text_input(
        "Stock Ticker Symbol:",
        value="AAPL", # Default value
        placeholder="E.g., AAPL, GOOGL, MSFT",
        help="Enter the stock ticker symbol from Yahoo Finance."
    ).upper() # Convert to uppercase

# Sensible default date range (e.g., last 3 years)
end_date = datetime.now().date()
start_date = end_date - timedelta(days=3*365)

with col2:
    start_date_input = st.date_input(
        "Start Date",
        value=start_date,
        max_value=end_date - timedelta(days=1) # Cannot select today as start if end is today
    )

with col3:
    end_date_input = st.date_input(
        "End Date",
        value=end_date,
        min_value=start_date_input + timedelta(days=1), # Cannot select before start date
        max_value=end_date
    )

# --- Fetch Data Button ---
# Place button in its own centered column or span columns if needed
col_button_mid = st.columns([1, 1, 1])[1] # Center the button in a 3-column layout

fetch_button = col_button_mid.button("📊 Fetch & Plot Data")

st.markdown("---") # Divider

# --- Data Fetching and Plotting Logic ---
if fetch_button and ticker_symbol:
    try:
        # Add a spinner for better UX during data fetching
        with st.spinner(f"Fetching data for {ticker_symbol}..."):
            # Fetch data from yfinance
            stock_data = yf.download(
                ticker_symbol,
                start=start_date_input,
                end=end_date_input,
                progress=False # Hide yfinance progress bar
            )

        if stock_data.empty:
            st.warning(f"No data found for ticker '{ticker_symbol}' in the selected date range. Check the ticker or dates.")
        else:
            st.subheader(f"{ticker_symbol} Stock Price")
            st.write(f"Displaying data from {start_date_input.strftime('%Y-%m-%d')} to {end_date_input.strftime('%Y-%m-%d')}")

            # Calculate EMAs
            stock_data['EMA_50'] = stock_data['Close'].ewm(span=50, adjust=False).mean()
            stock_data['EMA_200'] = stock_data['Close'].ewm(span=200, adjust=False).mean()

            # --- Plotting with Matplotlib ---
            fig, ax = plt.subplots(figsize=(12, 6)) # Adjust figure size

            ax.plot(stock_data.index, stock_data['Close'], label='Close Price', color='lightblue', linewidth=1.5)
            ax.plot(stock_data.index, stock_data['EMA_50'], label='50-Day EMA', color='orange', linewidth=1.5)
            ax.plot(stock_data.index, stock_data['EMA_200'], label='200-Day EMA', color='purple', linewidth=1.5)

            # Customize the plot
            ax.set_title(f'{ticker_symbol} Closing Price and EMAs', fontsize=16)
            ax.set_xlabel('Date', fontsize=12)
            ax.set_ylabel('Price (USD)', fontsize=12)
            ax.legend(fontsize=10)
            ax.grid(True, linestyle='--', alpha=0.6) # Add grid lines
            plt.xticks(rotation=45) # Rotate x-axis labels for better readability
            plt.tight_layout() # Adjust layout to prevent labels overlapping

            # Display the plot in Streamlit
            st.pyplot(fig)

           
