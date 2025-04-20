import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta

# App configuration
st.set_page_config(
    page_title="Stock Analysis App",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS styling
st.markdown("""
    <style>
        .main {background-color: #f8f9fa;}
        .reportview-container .main .block-container {max-width: 95%;}
        h1 {color: #2c3e50;}
        .stTextInput>div>div>input {border: 2px solid #3498db; border-radius: 5px;}
        .st-bb {background-color: white;}
        .st-at {background-color: #3498db;}
        .css-1aumxhk {background-color: #ffffff;}
    </style>
""", unsafe_allow_html=True)

# App header
st.title("📊 Stock Technical Analysis Dashboard")
st.markdown("Visualize stock prices with Exponential Moving Averages (EMAs)")

# Sidebar inputs
with st.sidebar:
    st.header("⚙️ Parameters")
    ticker_symbol = st.text_input(
        "Enter Stock Ticker", 
        value="AAPL",
        placeholder="e.g., AAPL",
        help="Enter a valid stock ticker symbol from Yahoo Finance"
    )
    start_date = st.date_input(
        "Start Date",
        value=datetime.now() - timedelta(days=365),
        max_value=datetime.now() - timedelta(days=1)
    )
    end_date = st.date_input(
        "End Date",
        value=datetime.now(),
        max_value=datetime.now()
    )

# Function to load data
@st.cache_data
def load_data(ticker, start, end):
    try:
        data = yf.download(ticker, start=start, end=end)
        if data.empty:
            return None
        # Calculate EMAs
        data['EMA50'] = data['Close'].ewm(span=50, adjust=False).mean()
        data['EMA200'] = data['Close'].ewm(span=200, adjust=False).mean()
        return data
    except Exception as e:
        st.error(f"Error loading data: {str(e)}")
        return None

# Main content
if ticker_symbol:
    with st.spinner('Loading stock data...'):
        stock_data = load_data(ticker_symbol, start_date, end_date)
    
    if stock_data is not None:
        # Create interactive plot
        fig = go.Figure()
        
        # Add price trace
        fig.add_trace(go.Scatter(
            x=stock_data.index,
            y=stock_data['Close'],
            name='Closing Price',
            line=dict(color='#2ecc71', width=2)
        ))
        
        # Add EMA traces
        fig.add_trace(go.Scatter(
            x=stock_data.index,
            y=stock_data['EMA50'],
            name='50 EMA',
            line=dict(color='#3498db', width=2, dash='dot')
        ))
        
        fig.add_trace(go.Scatter(
            x=stock_data.index,
            y=stock_data['EMA200'],
            name='200 EMA',
            line=dict(color='#e74c3c', width=2, dash='dot')
        ))
        
        # Update layout
        fig.update_layout(
            title=f'{ticker_symbol} Stock Price with EMAs',
            xaxis_title='Date',
            yaxis_title='Price (USD)',
            template='plotly_white',
            hovermode='x unified',
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            ),
            height=600,
            margin=dict(l=50, r=50, b=50, t=80)
        )
        
        # Display the plot
        st.plotly_chart(fig, use_container_width=True)
        
        # Display recent data
        st.subheader("Recent Data Overview")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Latest Close Price", 
                      f"${stock_data['Close'].iloc[-1]:.2f}",
                      f"{stock_data['Close'].iloc[-1] - stock_data['Close'].iloc[-2]:.2f}")
        with col2:
            st.metric("50 EMA Value", 
                      f"${stock_data['EMA50'].iloc[-1]:.2f}",
                      f"{stock_data['EMA50'].iloc[-1] - stock_data['EMA50'].iloc[-2]:.2f}")
        with col3:
            st.metric("200 EMA Value", 
                      f"${stock_data['EMA200'].iloc[-1]:.2f}",
                      f"{stock_data['EMA200'].iloc[-1] - stock_data['EMA200'].iloc[-2]:.2f}")
        
        # Show raw data
        if st.checkbox("Show Raw Data"):
            st.dataframe(stock_data.tail(10), height=300)
else:
    st.warning("Please enter a stock ticker symbol to begin analysis.")

# Footer
st.markdown("---")
st.markdown("ℹ️ Data provided by Yahoo Finance | Made with Streamlit")
