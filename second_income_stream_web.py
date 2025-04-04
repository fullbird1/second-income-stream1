import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import yfinance as yf
import datetime
import os
from forex_python.converter import CurrencyRates

# Set page configuration
st.set_page_config(
    page_title="Second Income Stream",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Add custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1E3A8A;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.8rem;
        font-weight: bold;
        color: #2563EB;
        margin-top: 1rem;
        margin-bottom: 0.5rem;
    }
    .card {
        background-color: #F3F4F6;
        border-radius: 0.5rem;
        padding: 1rem;
        margin-bottom: 1rem;
    }
    .metric-value {
        font-size: 1.8rem;
        font-weight: bold;
        color: #1E3A8A;
    }
    .metric-label {
        font-size: 1rem;
        color: #4B5563;
    }
    .highlight {
        background-color: #DBEAFE;
        padding: 0.5rem;
        border-radius: 0.25rem;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'currency' not in st.session_state:
    st.session_state.currency = "USD"
    st.session_state.exchange_rate = 7.82  # USD to HKD rate
    st.session_state.total_investment = 165000
    st.session_state.refresh_data = False
    st.session_state.stocks_data = None  # Will be initialized later
    st.session_state.summary_data = None  # Will be initialized later
    st.session_state.dividend_schedule = None  # Will be initialized later
    st.session_state.show_add_stock = False
    st.session_state.edit_mode = False

# Function to format currency
def format_currency(amount, currency="USD"):
    if currency == "USD":
        return f"${amount:,.2f}"
    elif currency == "HKD":
        return f"HK${amount:,.2f}"

# Function to convert currency
def convert_currency(amount, from_currency="USD", to_currency="USD"):
    if from_currency == to_currency:
        return amount
    elif from_currency == "USD" and to_currency == "HKD":
        return amount * st.session_state.exchange_rate
    elif from_currency == "HKD" and to_currency == "USD":
        return amount / st.session_state.exchange_rate

# Function to fetch stock data
@st.cache_data(ttl=3600)  # Cache for 1 hour
def fetch_stock_data(symbol):
    try:
        stock = yf.Ticker(symbol)
        hist = stock.history(period="1mo")
        if not hist.empty:
            current_price = hist['Close'].iloc[-1]
            return current_price
        return None
    except Exception as e:
        st.error(f"Error fetching data for {symbol}: {e}")
        return None

# Initialize stock data
def initialize_stock_data():
    # If we already have stock data in session state, use that
    if st.session_state.stocks_data is not None:
        return st.session_state.stocks_data, st.session_state.summary_data, st.session_state.dividend_schedule
    
    # Define the stocks data
    stocks_data = {
        'Tier 1': [
            # Mandatory Starting Positions (60% of Anchor Allocation)
            {'Symbol': 'CLM', 'Name': 'Cornerstone Strategic Value Fund', 'Dividend Yield (%)': 17.88, 'Allocation (%)': 16.50, 'Allocation Amount ($)': 27225},
            {'Symbol': 'CRF', 'Name': 'Cornerstone Total Return Fund', 'Dividend Yield (%)': 19.55, 'Allocation (%)': 16.50, 'Allocation Amount ($)': 27225},
            # Other Anchor Funds (40% of Anchor Allocation)
            {'Symbol': 'YYY', 'Name': 'YieldShares High Income ETF', 'Dividend Yield (%)': 10.25, 'Allocation (%)': 2.45, 'Allocation Amount ($)': 4037.78},
            {'Symbol': 'REM', 'Name': 'iShares Mortgage Real Estate ETF', 'Dividend Yield (%)': 9.85, 'Allocation (%)': 2.45, 'Allocation Amount ($)': 4037.78},
            {'Symbol': 'GOF', 'Name': 'Guggenheim Strategic Opportunities Fund', 'Dividend Yield (%)': 12.75, 'Allocation (%)': 2.45, 'Allocation Amount ($)': 4037.78},
            {'Symbol': 'ECC', 'Name': 'Eagle Point Credit Company', 'Dividend Yield (%)': 15.32, 'Allocation (%)': 2.45, 'Allocation Amount ($)': 4037.78},
            {'Symbol': 'USA', 'Name': 'Liberty All-Star Equity Fund', 'Dividend Yield (%)': 9.12, 'Allocation (%)': 2.45, 'Allocation Amount ($)': 4037.78},
            {'Symbol': 'GUT', 'Name': 'Gabelli Utility Trust', 'Dividend Yield (%)': 8.95, 'Allocation (%)': 2.45, 'Allocation Amount ($)': 4037.78},
            {'Symbol': 'BXMT', 'Name': 'Blackstone Mortgage Trust', 'Dividend Yield (%)': 11.45, 'Allocation (%)': 2.45, 'Allocation Amount ($)': 4037.78},
            {'Symbol': 'PSEC', 'Name': 'Prospect Capital Corporation', 'Dividend Yield (%)': 12.65, 'Allocation (%)': 2.45, 'Allocation Amount ($)': 4037.78},
            {'Symbol': 'BCAT', 'Name': 'BlackRock Capital Allocation Trust', 'Dividend Yield (%)': 9.35, 'Allocation (%)': 2.45, 'Allocation Amount ($)': 4037.78}
        ],
        'Tier 2': [
            # Recommended Starting Positions (70% of Tier 2 Allocation)
            {'Symbol': 'QQQY', 'Name': 'YieldMax NASDAQ 100 ETF', 'Dividend Yield (%)': 90.06, 'Allocation (%)': 5.83, 'Allocation Amount ($)': 9625},
            {'Symbol': 'WDTE', 'Name': 'WisdomTree Efficient Gold Plus Equity Strategy Fund', 'Dividend Yield (%)': 65.00, 'Allocation (%)': 5.83, 'Allocation Amount ($)': 9625},
            {'Symbol': 'IWMY', 'Name': 'iShares MSCI International Developed Momentum Factor ETF', 'Dividend Yield (%)': 73.08, 'Allocation (%)': 5.83, 'Allocation Amount ($)': 9625},
            # Other Tier 2 Funds (30% of Tier 2 Allocation)
            {'Symbol': 'SPYT', 'Name': 'SPDR Portfolio S&P 500 High Dividend ETF', 'Dividend Yield (%)': 45.25, 'Allocation (%)': 2.50, 'Allocation Amount ($)': 4125},
            {'Symbol': 'QQQT', 'Name': 'Invesco NASDAQ 100 ETF', 'Dividend Yield (%)': 52.35, 'Allocation (%)': 2.50, 'Allocation Amount ($)': 4125},
            {'Symbol': 'USOY', 'Name': 'United States Oil Fund LP', 'Dividend Yield (%)': 38.75, 'Allocation (%)': 2.50, 'Allocation Amount ($)': 4125}
        ],
        'Tier 3': [
            {'Symbol': 'YMAX', 'Name': 'YieldMax TSLA Option Income Strategy ETF', 'Dividend Yield (%)': 68.44, 'Allocation (%)': 1.67, 'Allocation Amount ($)': 2750},
            {'Symbol': 'YMAG', 'Name': 'YieldMax MAGNIFI Option Income Strategy ETF', 'Dividend Yield (%)': 38.65, 'Allocation (%)': 1.67, 'Allocation Amount ($)': 2750},
            {'Symbol': 'ULTY', 'Name': 'T-Rex 2X Long Utilities Index Daily Target ETF', 'Dividend Yield (%)': 77.62, 'Allocation (%)': 1.66, 'Allocation Amount ($)': 2750}
        ],
        'Additional': [
            {'Symbol': 'RDTE', 'Name': 'Robo Defense Tech ETF', 'Dividend Yield (%)': 22.45, 'Allocation (%)': 0, 'Allocation Amount ($)': 0},
            {'Symbol': 'GOOGL', 'Name': 'Alphabet Inc.', 'Dividend Yield (%)': 0.0, 'Allocation (%)': 0, 'Allocation Amount ($)': 0},
            {'Symbol': 'AMZN', 'Name': 'Amazon.com Inc.', 'Dividend Yield (%)': 0.0, 'Allocation (%)': 0, 'Allocation Amount ($)': 0},
            {'Symbol': 'SCHG', 'Name': 'Schwab U.S. Large-Cap Growth ETF', 'Dividend Yield (%)': 0.52, 'Allocation (%)': 0, 'Allocation Amount ($)': 0},
            {'Symbol': 'PLTY', 'Name': 'Playtech PLC', 'Dividend Yield (%)': 3.25, 'Allocation (%)': 0, 'Allocation Amount ($)': 0},
            {'Symbol': 'MSTY', 'Name': 'Mosaic Company', 'Dividend Yield (%)': 2.78, 'Allocation (%)': 0, 'Allocation Amount ($)': 0},
            {'Symbol': 'TSYY', 'Name': 'Trane Technologies PLC', 'Dividend Yield (%)': 1.15, 'Allocation (%)': 0, 'Allocation Amount ($)': 0},
            {'Symbol': 'AIPI', 'Name': 'AI Powered International Equity ETF', 'Dividend Yield (%)': 1.87, 'Allocation (%)': 0, 'Allocation Amount ($)': 0},
            {'Symbol': 'HOOD', 'Name': 'Robinhood Markets Inc.', 'Dividend Yield (%)': 0.0, 'Allocation (%)': 0, 'Allocation Amount ($)': 0},
            {'Symbol': 'HIMS', 'Name': 'Hims & Hers Health Inc.', 'Dividend Yield (%)': 0.0, 'Allocation (%)': 0, 'Allocation Amount ($)': 0},
            {'Symbol': 'S', 'Name': 'SentinelOne Inc.', 'Dividend Yield (%)': 0.0, 'Allocation (%)': 0, 'Allocation Amount ($)': 0},
            {'Symbol': 'NFLP', 'Name': 'Neuberger Berman Flexible Real Estate Income Fund', 'Dividend Yield (%)': 12.35, 'Allocation (%)': 0, 'Allocation Amount ($)': 0},
            {'Symbol': 'SVOL', 'Name': 'Simplify Volatility Premium ETF', 'Dividend Yield (%)': 15.42, 'Allocation (%)': 0, 'Allocation Amount ($)': 0},
            {'Symbol': 'NBIS', 'Name': 'Neuberger Berman Income Strategy ETF', 'Dividend Yield (%)': 8.76, 'Allocation (%)': 0, 'Allocation Amount ($)': 0},
            {'Symbol': 'BX', 'Name': 'Blackstone Inc.', 'Dividend Yield (%)': 3.45, 'Allocation (%)': 0, 'Allocation Amount ($)': 0},
            {'Symbol': 'AMDL', 'Name': 'Advanced Micro Devices Inc.', 'Dividend Yield (%)': 0.0, 'Allocation (%)': 0, 'Allocation Amount ($)': 0},
            {'Symbol': 'UPRO', 'Name': 'ProShares UltraPro S&P 500 ETF', 'Dividend Yield (%)': 0.32, 'Allocation (%)': 0, 'Allocation Amount ($)': 0},
            {'Symbol': 'MSTU', 'Name': 'MicroSectors U.S. Big Oil Index 3X Leveraged ETN', 'Dividend Yield (%)': 0.0, 'Allocation (%)': 0, 'Allocation Amount ($)': 0},
            {'Symbol': 'XYZY', 'Name': 'XYZ Yield ETF (Placeholder)', 'Dividend Yield (%)': 5.75, 'Allocation (%)': 0, 'Allocation Amount ($)': 0}
        ]
    }
    
    # Update allocation amounts based on current investment amount
    stocks_data = recalculate_allocations(stocks_data, st.session_state.total_investment)
    
    # Create summary data
    summary_data = calculate_summary_data(stocks_data, st.session_state.total_investment)
    
    # Create dividend payment schedule
    dividend_schedule = generate_dividend_schedule(stocks_data)
    
    # Store in session state
    st.session_state.stocks_data = stocks_data
    st.session_state.summary_data = summary_data
    st.session_state.dividend_schedule = dividend_schedule
    
    return stocks_data, summary_data, dividend_schedule

# Function to recalculate allocations based on investment amount
def recalculate_allocations(stocks_data, investment_amount):
    # Calculate total allocation percentage for each tier
    tier_allocations = {
        'Tier 1': 55,
        'Tier 2': 25,
        'Tier 3': 5,
        'Additional': 0
    }
    
    # Cash reserve is 15% of total investment
    cash_reserve = investment_amount * 0.15
    investable_amount = investment_amount - cash_reserve
    
    # Recalculate allocation amounts for each stock
    for tier, stocks in stocks_data.items():
        tier_amount = investable_amount * (tier_allocations[tier] / 100)
        
        # Calculate total allocation percentage within tier
        total_tier_allocation_pct = sum(stock['Allocation (%)'] for stock in stocks)
        
        if total_tier_allocation_pct > 0:
            # Update allocation amounts proportionally
            for stock in stocks:
                stock['Allocation Amount ($)'] = tier_amount * (stock['Allocation (%)'] / total_tier_allocation_pct)
    
    return stocks_data

# Function to calculate summary data
def calculate_summary_data(stocks_data, investment_amount):
    # Calculate total allocation and income for each tier
    tier_totals = {
        'Tier 1': {'allocation': 0, 'income': 0},
        'Tier 2': {'allocation': 0, 'income': 0},
        'Tier 3': {'allocation': 0, 'income': 0}
    }
    
    for tier, stocks in stocks_data.items():
        if tier != 'Additional':
            for stock in stocks:
                tier_totals[tier]['allocation'] += stock['Allocation Amount ($)']
                tier_totals[tier]['income'] += stock['Allocation Amount ($)'] * stock['Dividend Yield (%)'] / 100
    
    # Cash reserve (15% of total investment)
    cash_reserve = investment_amount * 0.15
    
    # Create summary data
    total_allocation = sum(tier['allocation'] for tier in tier_totals.values()) + cash_reserve
    total_income = sum(tier['income'] for tier in tier_totals.values())
    
    summary_data = {
        'Category': ['Tier 1 (Anchor Funds)', 'Tier 2 (Index-Based Funds)', 'Tier 3 (High-Yield Funds)', 'Cash Reserve', 'Total'],
        'Allocation (%)': [
            round(tier_totals['Tier 1']['allocation'] / investment_amount * 100, 2),
            round(tier_totals['Tier 2']['allocation'] / investment_amount * 100, 2),
            round(tier_totals['Tier 3']['allocation'] / investment_amount * 100, 2),
            round(cash_reserve / investment_amount * 100, 2),
            100
        ],
        'Allocation Amount ($)': [
            tier_totals['Tier 1']['allocation'],
            tier_totals['Tier 2']['allocation'],
            tier_totals['Tier 3']['allocation'],
            cash_reserve,
            investment_amount
        ],
        'Expected Annual Income ($)': [
            tier_totals['Tier 1']['income'],
            tier_totals['Tier 2']['income'],
            tier_totals['Tier 3']['income'],
            0,
            total_income
        ],
        'Yield on Allocation (%)': [
            round(tier_totals['Tier 1']['income'] / tier_totals['Tier 1']['allocation'] * 100, 2) if tier_totals['Tier 1']['allocation'] > 0 else 0,
            round(tier_totals['Tier 2']['income'] / tier_totals['Tier 2']['allocation'] * 100, 2) if tier_totals['Tier 2']['allocation'] > 0 else 0,
            round(tier_totals['Tier 3']['income'] / tier_totals['Tier 3']['allocation'] * 100, 2) if tier_totals['Tier 3']['allocation'] > 0 else 0,
            0,
            round(total_income / investment_amount * 100, 2)
        ]
    }
    
    return summary_data

# Function to generate dividend schedule
def generate_dividend_schedule(stocks_data):
    dividend_schedule = []
    current_date = datetime.datetime.now()
    
    # Generate dividend payments for the next 12 months
    for tier, stocks in stocks_data.items():
        if tier != 'Additional':
            for stock in stocks:
                symbol = stock['Symbol']
                dividend_yield = stock['Dividend Yield (%)']
                allocation = stock['Allocation Amount ($)']
                
                # Calculate monthly dividend amount
                monthly_dividend = (allocation * dividend_yield / 100) / 12
                
                # Generate payment dates (simplified - one payment per month)
                for i in range(1, 13):
                    payment_date = current_date + datetime.timedelta(days=30*i)
                    dividend_schedule.append({
                        'Symbol': symbol,
                        'Payment Date': payment_date.strftime('%Y-%m-%d'),
                        'Amount': monthly_dividend,
                        'Tier': tier
                    })
    
    return dividend_schedule

# Function to add a new stock
def add_stock(tier, symbol, name, dividend_yield, allocation_pct):
    # Get current stocks data
    stocks_data, summary_data, dividend_schedule = initialize_stock_data()
    
    # Create new stock entry
    new_stock = {
        'Symbol': symbol,
        'Name': name,
        'Dividend Yield (%)': float(dividend_yield),
        'Allocation (%)': float(allocation_pct),
        'Allocation Amount ($)': 0  # Will be calculated in recalculate_allocations
    }
    
    # Add to appropriate tier
    stocks_data[tier].append(new_stock)
    
    # Recalculate allocations
    stocks_data = recalculate_allocations(stocks_data, st.session_state.total_investment)
    
    # Update summary data
    summary_data = calculate_summary_data(stocks_data, st.session_state.total_investment)
    
    # Update dividend schedule
    dividend_schedule = generate_dividend_schedule(stocks_data)
    
    # Update session state
    st.session_state.stocks_data = stocks_data
    st.session_state.summary_data = summary_data
    st.session_state.dividend_schedule = dividend_schedule
    
    retur
(Content truncated due to size limit. Use line ranges to read in chunks)