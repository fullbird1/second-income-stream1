import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import yfinance as yf
from forex_python.converter import CurrencyRates
from datetime import datetime, timedelta
import random

# Set page configuration
st.set_page_config(
    page_title="Second Income Stream",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1E88E5;
        text-align: center;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.5rem;
        color: #1E88E5;
        margin-bottom: 0.5rem;
    }
    .tier-header {
        font-size: 1.8rem;
        color: #1E88E5;
        margin-bottom: 0.5rem;
    }
    .dashboard-metric {
        font-size: 1.2rem;
        font-weight: bold;
    }
    .dashboard-value {
        font-size: 2rem;
        font-weight: bold;
        color: #1E88E5;
    }
    .positive {
        color: #4CAF50;
    }
    .negative {
        color: #F44336;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'total_investment' not in st.session_state:
    st.session_state.total_investment = 165000.0

if 'stocks_data' not in st.session_state:
    st.session_state.stocks_data = None

if 'summary_data' not in st.session_state:
    st.session_state.summary_data = None

if 'dividend_schedule' not in st.session_state:
    st.session_state.dividend_schedule = None

if 'refresh_data' not in st.session_state:
    st.session_state.refresh_data = False

if 'edit_mode' not in st.session_state:
    st.session_state.edit_mode = False

# Function to initialize stock data
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
            {'Symbol': 'SCHG', 'Name': 'Schwab U.S. Large-Cap Growth ETF', 'Dividend Yield (%)': 0.58, 'Allocation (%)': 0, 'Allocation Amount ($)': 0},
            {'Symbol': 'PLTY', 'Name': 'Playtech plc', 'Dividend Yield (%)': 3.25, 'Allocation (%)': 0, 'Allocation Amount ($)': 0},
            {'Symbol': 'MSTY', 'Name': 'Misty Robotics Inc.', 'Dividend Yield (%)': 0.0, 'Allocation (%)': 0, 'Allocation Amount ($)': 0},
            {'Symbol': 'TSYY', 'Name': 'Treasury Yield ETF', 'Dividend Yield (%)': 4.85, 'Allocation (%)': 0, 'Allocation Amount ($)': 0},
            {'Symbol': 'AIPI', 'Name': 'AI Powered Innovation ETF', 'Dividend Yield (%)': 0.12, 'Allocation (%)': 0, 'Allocation Amount ($)': 0},
            {'Symbol': 'HOOD', 'Name': 'Robinhood Markets Inc.', 'Dividend Yield (%)': 0.0, 'Allocation (%)': 0, 'Allocation Amount ($)': 0},
            {'Symbol': 'HIMS', 'Name': 'Hims & Hers Health Inc.', 'Dividend Yield (%)': 0.0, 'Allocation (%)': 0, 'Allocation Amount ($)': 0},
            {'Symbol': 'S', 'Name': 'SentinelOne Inc.', 'Dividend Yield (%)': 0.0, 'Allocation (%)': 0, 'Allocation Amount ($)': 0},
            {'Symbol': 'NFLP', 'Name': 'Netflix Partners LLC', 'Dividend Yield (%)': 0.0, 'Allocation (%)': 0, 'Allocation Amount ($)': 0},
            {'Symbol': 'SVOL', 'Name': 'Simplify Volatility Premium ETF', 'Dividend Yield (%)': 15.75, 'Allocation (%)': 0, 'Allocation Amount ($)': 0},
            {'Symbol': 'NBIS', 'Name': 'Neuberger Berman InnovAsia Fund', 'Dividend Yield (%)': 2.35, 'Allocation (%)': 0, 'Allocation Amount ($)': 0},
            {'Symbol': 'BX', 'Name': 'Blackstone Inc.', 'Dividend Yield (%)': 3.85, 'Allocation (%)': 0, 'Allocation Amount ($)': 0},
            {'Symbol': 'AMDL', 'Name': 'Advanced Micro Devices Leveraged ETF', 'Dividend Yield (%)': 0.0, 'Allocation (%)': 0, 'Allocation Amount ($)': 0},
            {'Symbol': 'UPRO', 'Name': 'ProShares UltraPro S&P 500 ETF', 'Dividend Yield (%)': 0.65, 'Allocation (%)': 0, 'Allocation Amount ($)': 0},
            {'Symbol': 'MSTU', 'Name': 'MicroStrategy Ultra ETF', 'Dividend Yield (%)': 0.0, 'Allocation (%)': 0, 'Allocation Amount ($)': 0},
            {'Symbol': 'XYZY', 'Name': 'XYZ Yield Corp', 'Dividend Yield (%)': 8.45, 'Allocation (%)': 0, 'Allocation Amount ($)': 0}
        ]
    }
    
    # Calculate summary data
    summary_data = calculate_summary_data(stocks_data, st.session_state.total_investment)
    
    # Generate dividend schedule
    dividend_schedule = generate_dividend_schedule(stocks_data)
    
    # Store in session state
    st.session_state.stocks_data = stocks_data
    st.session_state.summary_data = summary_data
    st.session_state.dividend_schedule = dividend_schedule
    
    return stocks_data, summary_data, dividend_schedule

# Function to delete a stock
def delete_stock(tier, symbol):
    # Get current stocks data
    stocks_data, summary_data, dividend_schedule = initialize_stock_data()
    
    # Find and remove the stock
    stocks_data[tier] = [stock for stock in stocks_data[tier] if stock['Symbol'] != symbol]
    
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

# Function to add a stock
def add_stock(tier, symbol, name, dividend_yield, allocation_percentage):
    # Get current stocks data
    stocks_data, summary_data, dividend_schedule = initialize_stock_data()
    
    # Calculate allocation amount
    allocation_amount = (allocation_percentage / 100) * st.session_state.total_investment
    
    # Add the new stock
    new_stock = {
        'Symbol': symbol,
        'Name': name,
        'Dividend Yield (%)': dividend_yield,
        'Allocation (%)': allocation_percentage,
        'Allocation Amount ($)': allocation_amount
    }
    
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

# Function to recalculate allocations
def recalculate_allocations(stocks_data, total_investment):
    # Calculate total allocation percentage for each tier
    tier_percentages = {
        'Tier 1': 55,
        'Tier 2': 25,
        'Tier 3': 5
    }
    
    for tier, percentage in tier_percentages.items():
        if tier in stocks_data and stocks_data[tier]:
            # Count stocks in tier
            num_stocks = len(stocks_data[tier])
            
            if num_stocks > 0:
                # Distribute allocation evenly
                allocation_per_stock = percentage / num_stocks
                
                # Update each stock
                for stock in stocks_data[tier]:
                    stock['Allocation (%)'] = allocation_per_stock
                    stock['Allocation Amount ($)'] = (allocation_per_stock / 100) * total_investment
    
    return stocks_data

# Function to calculate summary data
def calculate_summary_data(stocks_data, total_investment):
    summary_data = {
        'Total Investment': total_investment,
        'Cash Reserve': total_investment * 0.15,  # 15% cash reserve
        'Tier Allocations': {
            'Tier 1': {
                'Percentage': 55,
                'Amount': total_investment * 0.55,
                'Annual Income': 0,
                'Yield': 0
            },
            'Tier 2': {
                'Percentage': 25,
                'Amount': total_investment * 0.25,
                'Annual Income': 0,
                'Yield': 0
            },
            'Tier 3': {
                'Percentage': 5,
                'Amount': total_investment * 0.05,
                'Annual Income': 0,
                'Yield': 0
            }
        },
        'Total Annual Income': 0,
        'Overall Yield': 0
    }
    
    # Calculate income and yield for each tier
    for tier in ['Tier 1', 'Tier 2', 'Tier 3']:
        tier_annual_income = 0
        
        for stock in stocks_data[tier]:
            stock_annual_income = (stock['Allocation Amount ($)'] * stock['Dividend Yield (%)']) / 100
            tier_annual_income += stock_annual_income
        
        summary_data['Tier Allocations'][tier]['Annual Income'] = tier_annual_income
        
        # Calculate tier yield
        if summary_data['Tier Allocations'][tier]['Amount'] > 0:
            summary_data['Tier Allocations'][tier]['Yield'] = (tier_annual_income / summary_data['Tier Allocations'][tier]['Amount']) * 100
        
        # Add to total income
        summary_data['Total Annual Income'] += tier_annual_income
    
    # Calculate overall yield
    if total_investment > 0:
        summary_data['Overall Yield'] = (summary_data['Total Annual Income'] / total_investment) * 100
    
    return summary_data

# Function to generate dividend schedule
def generate_dividend_schedule(stocks_data):
    # Create a schedule for the next 12 months
    today = datetime.now()
    schedule = {}
    
    # Define payment frequencies for different stocks
    frequencies = {
        'Monthly': 1,
        'Quarterly': 3,
        'Semi-Annual': 6,
        'Annual': 12
    }
    
    # Assign random payment frequencies to stocks
    for tier in ['Tier 1', 'Tier 2', 'Tier 3']:
        for stock in stocks_data[tier]:
            # Determine frequency based on tier
            if tier == 'Tier 1':
                # Tier 1 stocks are mostly monthly or quarterly
                frequency = random.choice(['Monthly', 'Monthly', 'Quarterly'])
            elif tier == 'Tier 2':
                # Tier 2 stocks are mostly quarterly
                frequency = random.choice(['Monthly', 'Quarterly', 'Quarterly'])
            else:
                # Tier 3 stocks have varied frequencies
                frequency = random.choice(['Monthly', 'Quarterly', 'Semi-Annual'])
            
            # Determine next payment date (random day in next month)
            next_month = today.month % 12 + 1
            next_year = today.year + (1 if next_month < today.month else 0)
            next_payment = datetime(next_year, next_month, min(28, today.day))
            
            # Calculate monthly income
            annual_income = (stock['Allocation Amount ($)'] * stock['Dividend Yield (%)']) / 100
            monthly_income = annual_income / 12
            
            # Calculate payment amount based on frequency
            payment_amount = monthly_income * frequencies[frequency]
            
            # Add to schedule
            for i in range(12):
                # Calculate payment month
                payment_month = (next_payment.month - 1 + i * frequencies[frequency]) % 12 + 1
                payment_year = next_payment.year + (payment_month < next_payment.month or 
                                                  (payment_month == next_payment.month and 
                                                   i * frequencies[frequency] > 0))
                
                # Skip if not a payment month for this frequency
                if i % frequencies[frequency] != 0:
                    continue
                
                # Create month key
                month_key = f"{payment_year}-{payment_month:02d}"
