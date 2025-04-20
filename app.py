import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime

# Page configuration
st.set_page_config(
    page_title="Stock EMA Analyzer",
    page_icon="📈",
    layout="wide"
)

# App title and description
st.title("📈 Stock EMA Analyzer")
st.markdown("Visualize stock prices with 50 & 200 day Exponential Moving Averages")

# Sidebar for user inputs
with st.sidebar:
    st.header("Chart Settings")
    
    # Ticker input with default value
    ticker = st.text_input("Enter Stock Ticker Symbol", "AAPL").upper()
    
    # Time period selection
    period = st.selectbox(
        "Select Time Period",
        options=["1mo", "3mo", "6mo", "1y", "2y", "5y", "max"],
        index=3  # Default to 1 year
    )
    
    # Analysis button
    analyze_button = st.button("Analyze Stock", type="primary", use_container_width=True)
    
    # Information about EMAs
    st.markdown("---")
    st.markdown("### About EMAs")
    st.info("""
    - **50 EMA (Blue)**: Medium-term trend
    - **200 EMA (Red)**: Long-term trend
    - **Golden Cross**: 50 EMA crosses above 200 EMA (bullish)
    - **Death Cross**: 50 EMA crosses below 200 EMA (bearish)
    """)

# Function to analyze and display stock data
def analyze_stock(ticker_symbol, time_period):
    # Show loading message
    with st.spinner(f"Fetching data for {ticker_symbol}..."):
        try:
            # Get stock data
            stock_data = yf.download(ticker_symbol, period=time_period)
            
            if stock_data.empty:
                st.error(f"No data found for ticker symbol: {ticker_symbol}")
                return
            
            # Calculate EMAs
            stock_data['EMA50'] = stock_data['Close'].ewm(span=50, adjust=False).mean()
            stock_data['EMA200'] = stock_data['Close'].ewm(span=200, adjust=False).mean()
            
            # Get company name
            try:
                ticker_info = yf.Ticker(ticker_symbol)
                company_name = ticker_info.info.get('longName', ticker_symbol)
            except:
                company_name = ticker_symbol
            
            # Display company info
            st.header(f"{company_name} ({ticker_symbol})")
            
            # Show key metrics
            col1, col2, col3 = st.columns(3)
            
            latest_price = stock_data['Close'].iloc[-1]
            price_change = stock_data['Close'].iloc[-1] - stock_data['Close'].iloc[-2]
            price_change_pct = (price_change / stock_data['Close'].iloc[-2]) * 100
            
            col1.metric(
                label="Current Price",
                value=f"${latest_price:.2f}",
                delta=f"{price_change:.2f} ({price_change_pct:.2f}%)"
            )
            
            ema_50 = stock_data['EMA50'].iloc[-1]
            col2.metric(
                label="50-Day EMA",
                value=f"${ema_50:.2f}",
                delta=f"{((latest_price - ema_50) / ema_50) * 100:.2f}% from price"
            )
            
            ema_200 = stock_data['EMA200'].iloc[-1]
            col3.metric(
                label="200-Day EMA",
                value=f"${ema_200:.2f}",
                delta=f"{((latest_price - ema_200) / ema_200) * 100:.2f}% from price"
            )
            
            # Create price chart with EMAs
            fig = go.Figure()
            
            # Add candlestick chart
            fig.add_trace(
                go.Candlestick(
                    x=stock_data.index,
                    open=stock_data['Open'],
                    high=stock_data['High'],
                    low=stock_data['Low'],
                    close=stock_data['Close'],
                    name="Price",
                    increasing_line_color='#26a69a', 
                    decreasing_line_color='#ef5350'
                )
            )
            
            # Add 50-day EMA
            fig.add_trace(
                go.Scatter(
                    x=stock_data.index,
                    y=stock_data['EMA50'],
                    mode='lines',
                    line=dict(color='#2196F3', width=2),
                    name='50-Day EMA'
                )
            )
            
            # Add 200-day EMA
            fig.add_trace(
                go.Scatter(
                    x=stock_data.index,
                    y=stock_data['EMA200'],
                    mode='lines',
                    line=dict(color='#F44336', width=2),
                    name='200-Day EMA'
                )
            )
            
            # Update layout
            fig.update_layout(
                title=f"{ticker_symbol} Price with 50 & 200 Day EMAs",
                xaxis_title="Date",
                yaxis_title="Price (USD)",
                height=600,
                template="plotly_white",
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
                margin=dict(l=0, r=0, t=50, b=0)
            )
            
            # Add range slider and buttons
            fig.update_xaxes(
                rangeslider_visible=True,
                rangeselector=dict(
                    buttons=list([
                        dict(count=1, label="1m", step="month", stepmode="backward"),
                        dict(count=3, label="3m", step="month", stepmode="backward"),
                        dict(count=6, label="6m", step="month", stepmode="backward"),
                        dict(count=1, label="1y", step="year", stepmode="backward"),
                        dict(step="all")
                    ])
                )
            )
            
            # Display the chart
            st.plotly_chart(fig, use_container_width=True)
            
            # Technical analysis section
            st.subheader("Technical Analysis")
            
            # Check for Golden Cross or Death Cross in the last 30 days
            if len(stock_data) > 200:
                recent_data = stock_data.tail(30)
                golden_cross = False
                death_cross = False
                cross_date = None
                
                for i in range(1, len(recent_data)):
                    # Golden Cross detection
                    if (recent_data['EMA50'].iloc[i-1] <= recent_data['EMA200'].iloc[i-1] and 
                        recent_data['EMA50'].iloc[i] > recent_data['EMA200'].iloc[i]):
                        golden_cross = True
                        cross_date = recent_data.index[i].strftime('%Y-%m-%d')
                    
                    # Death Cross detection
                    if (recent_data['EMA50'].iloc[i-1] >= recent_data['EMA200'].iloc[i-1] and 
                        recent_data['EMA50'].iloc[i] < recent_data['EMA200'].iloc[i]):
                        death_cross = True
                        cross_date = recent_data.index[i].strftime('%Y-%m-%d')
            
            # Display trend analysis
            col1, col2 = st.columns(2)
            
            with col1:
                if stock_data['EMA50'].iloc[-1] > stock_data['EMA200'].iloc[-1]:
                    st.success("BULLISH: 50-day EMA is above 200-day EMA")
                else:
                    st.error("BEARISH: 50-day EMA is below 200-day EMA")
            
            with col2:
                if 'golden_cross' in locals() and golden_cross:
                    st.success(f"Golden Cross detected on {cross_date}!")
                elif 'death_cross' in locals() and death_cross:
                    st.error(f"Death Cross detected on {cross_date}!")
                else:
                    st.info("No EMA crosses detected in the last 30 days")
            
            # Add volume chart
            st.subheader("Trading Volume")
            volume_fig = go.Figure()
            volume_fig.add_trace(
                go.Bar(
                    x=stock_data.index,
                    y=stock_data['Volume'],
                    marker=dict(color='rgba(100, 100, 100, 0.7)')
                )
            )
            
            volume_fig.update_layout(
                height=250,
                template="plotly_white",
                margin=dict(l=0, r=0, t=10, b=0),
                xaxis_rangeslider_visible=False
            )
            
            st.plotly_chart(volume_fig, use_container_width=True)
            
        except Exception as e:
            st.error(f"Error: {e}")
            st.info("Please check if the ticker symbol is correct and try again.")

# Run the analysis when button is clicked or by default on first run
if analyze_button or 'initialized' not in st.session_state:
    st.session_state.initialized = True
    analyze_stock(ticker, period)

# Add educational information
with st.expander("How to Interpret EMAs"):
    st.write("""
    Exponential Moving Averages (EMAs) are popular technical indicators that help identify trends:

    - **50-Day EMA (Blue Line)**: Shows the medium-term trend
    - **200-Day EMA (Red Line)**: Shows the long-term trend

    **Key Signals:**
    - **Golden Cross**: When the 50-day EMA crosses above the 200-day EMA (bullish)
    - **Death Cross**: When the 50-day EMA crosses below the 200-day EMA (bearish)
    - **Price Above Both EMAs**: Often indicates a strong bullish trend
    - **Price Below Both EMAs**: Often indicates a strong bearish trend
    """)

# Add disclaimer
st.caption("**Disclaimer:** This tool is for informational purposes only and not intended as investment advice. Past performance does not guarantee future results.")
