import yfinance as yf
import pandas as pd
import numpy as np
import streamlit as st
import plotly.graph_objects as go

# Title of the widget
st.title("MarketRogues: Nifty 50 Volatility Analysis")

# Fetch Data
st.subheader("Fetching Data...")
try:
    nifty = yf.download("^NSEI", period="1y", interval="1d")
    nifty['Daily Returns'] = nifty['Close'].pct_change()

    # Drop NaN values to avoid calculation errors
    nifty = nifty.dropna()

    st.success("Data fetched successfully!")
except Exception as e:
    st.error(f"Error fetching data: {e}")

# Historical Volatility
st.subheader("Volatility Insights")
try:
    periods = [10, 20, 30]

    # Calculate rolling standard deviation and annualize it
    for period in periods:
        nifty[f"HV_{period}"] = nifty['Daily Returns'].rolling(window=period).std() * np.sqrt(252) * 100  # Annualized volatility

    # Drop NaN values that might appear due to the rolling window
    nifty = nifty.dropna()

    # Line Chart for HV
    fig = go.Figure()
    for period in periods:
        fig.add_trace(go.Scatter(x=nifty.index, y=nifty[f"HV_{period}"],
                                 mode='lines', name=f"HV ({period}-Day)", line=dict(width=2)))

    fig.update_layout(
        title="Historical Volatility (HV)",
        xaxis_title="Date",
        yaxis_title="Volatility (%)",
        template="plotly_white"
    )
    st.plotly_chart(fig)

    # Latest HV Values
    latest_hv_values = {f"{period}-Day": nifty[f"HV_{period}"].iloc[-1] for period in periods}

    # Reversed Line Chart for Latest HV Values
    line_fig = go.Figure()
    sorted_periods = [30, 20, 10]  # Reversed order (30, 20, 10)
    line_fig.add_trace(go.Scatter(
        x=[f"{period}-Day" for period in sorted_periods],
        y=[latest_hv_values[f"{period}-Day"] for period in sorted_periods],
        mode='lines+markers',
        marker=dict(color='orange', size=8),
        name="Latest HV Values"
    ))

    line_fig.update_layout(
        title="Latest Historical Volatility (HV) Values",
        xaxis_title="Period",
        yaxis_title="Volatility (%)",
        template="plotly_white"
    )
    st.plotly_chart(line_fig)

    # Insights - Rising or Falling Volatility
    st.write("**Current Volatilities:**")
    for period, value in latest_hv_values.items():
        st.write(f"- {period} HV: {value:.2f}%")

    st.write("""
        **Rising or Falling Volatility?**
        - **Rising Volatility**: If the shorter-term volatility (10-day) is higher than the longer-term volatility (20 or 30-day), it suggests increasing uncertainty in the market, potentially due to short-term market events or reactions.
        - **Falling Volatility**: If the shorter-term volatility is lower than the longer-term volatility, it indicates stabilizing conditions in the market, with reduced uncertainty and less potential for large price swings.
    """)

except Exception as e:
    st.error(f"Error calculating HV: {e}")