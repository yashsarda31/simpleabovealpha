import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go

# Set page configuration
st.set_page_config(
    page_title="Stock EMA Visualizer",
    page_icon="📈",
    layout="wide"
)

# Add custom CSS for better appearance
st.markdown("""
<style>
    .main {
        background-color: #f8f9fa;
    }
    h1, h2, h3 {
        color: #2c3e50;
    }
    .stButton>button {
        background-color: #3498db;
        color: white;
        border-radius: 5px;
        padding: 0.5rem 1rem;
    }
    .stButton>button:hover {
        background-color: #2980b9;
    }
</style>
""", unsafe_allow_html=True)

# App title and description
st.title("📈 Stock EMA Visualizer")
st.markdown("### Analyze stock trends with 50 and 200 day Exponential Moving Averages")

# Input section
col1, col2, col3 = st.columns([2, 1, 1])
with col1:
    ticker = st.text_input("Enter Stock Ticker:", "AAPL").upper()
with col2:
    period = st.selectbox(
        "Time Period:", 
        ["1 Month", "3 Months", "6 Months", "1 Year", "2 Years", "5 Years", "Max"],
        index=3
    )
    # Map to yfinance period format
    period_map = {
        "1 Month": "1mo", "3 Months": "3mo", "6 Months": "6mo",
        "1 Year": "1y", "2 Years": "2y", "5 Years": "5y", "Max": "max"
    }
    yf_period = period_map[period]
with col3:
    theme = st.selectbox("Theme", ["Light", "Dark"])
    analyze_button = st.button("Analyze Stock")

# Main section - fetch and display data
if analyze_button or 'data' in st.session_state:
    with st.spinner(f"Fetching data for {ticker}..."):
        try:
            # Get stock data
            stock_data = yf.download(ticker, period=yf_period)
            
            # Calculate EMAs
            stock_data['EMA50'] = stock_data['Close'].ewm(span=50, adjust=False).mean()
            stock_data['EMA200'] = stock_data['Close'].ewm(span=200, adjust=False).mean()
            
            # Get company info
            try:
                stock_info = yf.Ticker(ticker)
                company_name = stock_info.info.get('longName', ticker)
            except:
                company_name = ticker
            
            # Display company name and metrics
            latest_data = stock_data.iloc[-1]
            previous_data = stock_data.iloc[-2] if len(stock_data) > 1 else latest_data
            current_price = latest_data['Close']
            price_change = current_price - previous_data['Close']
            price_change_pct = (price_change / previous_data['Close']) * 100
            
            st.header(f"{company_name} ({ticker})")
            
            # Display metrics
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric(
                    "Current Price", 
                    f"${current_price:.2f}", 
                    f"{price_change:.2f} ({price_change_pct:.2f}%)"
                )
            with col2:
                st.metric("50-Day EMA", f"${latest_data['EMA50']:.2f}")
            with col3:
                st.metric("200-Day EMA", f"${latest_data['EMA200']:.2f}")
            
            # Set theme colors
            if theme == "Dark":
                template = "plotly_dark"
                plot_bg = "#1e1e1e"
                paper_bg = "#1e1e1e"
                text_color = "white"
            else:
                template = "plotly_white"
                plot_bg = "white"
                paper_bg = "white"
                text_color = "black"
            
            # Create plot with Plotly
            fig = go.Figure()
            
            # Add traces
            fig.add_trace(go.Scatter(
                x=stock_data.index,
                y=stock_data['Close'],
                mode='lines',
                name='Stock Price',
                line=dict(color='#3498db', width=2)
            ))
            
            fig.add_trace(go.Scatter(
                x=stock_data.index,
                y=stock_data['EMA50'],
                mode='lines',
                name='50-Day EMA',
                line=dict(color='#e74c3c', width=1.5)
            ))
            
            fig.add_trace(go.Scatter(
                x=stock_data.index,
                y=stock_data['EMA200'],
                mode='lines',
                name='200-Day EMA',
                line=dict(color='#2ecc71', width=1.5)
            ))
            
            # Update layout
            fig.update_layout(
                title=f"{company_name} Stock Chart with EMAs",
                xaxis_title="Date",
                yaxis_title="Price (USD)",
                height=600,
                template=template,
                plot_bgcolor=plot_bg,
                paper_bgcolor=paper_bg,
                font=dict(color=text_color),
                hovermode="x unified"
            )
            
            # Display the chart
            st.plotly_chart(fig, use_container_width=True)
            
            # Technical Analysis Insights
            st.subheader("Technical Analysis")
            
            latest = stock_data.iloc[-1]
            
            # Simple EMA analysis
            if latest['Close'] > latest['EMA50'] and latest['EMA50'] > latest['EMA200']:
                st.success("📈 Strong Uptrend: Price is above both 50 and 200 EMAs, and 50 EMA is above 200 EMA.")
            elif latest['Close'] < latest['EMA50'] and latest['EMA50'] < latest['EMA200']:
                st.error("📉 Strong Downtrend: Price is below both 50 and 200 EMAs, and 50 EMA is below 200 EMA.")
            elif latest['Close'] > latest['EMA50'] and latest['EMA50'] < latest['EMA200']:
                st.info("⚠️ Potential Reversal: Price is above 50 EMA but 50 EMA is below 200 EMA, suggesting possible upward momentum.")
            else:
                st.warning("🔄 Mixed Signals: The indicators are showing conflicting signals.")
                
            # Show data table
            with st.expander("View Data Table"):
                st.dataframe(stock_data[['Close', 'EMA50', 'EMA200']])
                
        except Exception as e:
            st.error(f"Error fetching data: {e}")
            st.info("Please check if the ticker symbol is correct and try again.")

# Footer
st.markdown("---")
st.markdown("*Data provided by Yahoo Finance. This app is for educational purposes only and not financial advice.*")
