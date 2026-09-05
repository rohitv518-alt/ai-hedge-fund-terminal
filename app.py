import streamlit as st

from data_engine import get_market_data
from ai_brain import get_ai_decision
from execution import execute_trade


st.set_page_config(
    page_title="Autonomous AI Hedge Fund Terminal",
    page_icon="📈",
    layout="wide"
)

st.markdown(
    """
    <style>
        .main-title {
            text-align: center;
            font-size: 42px;
            font-weight: 800;
            margin-bottom: 30px;
        }

        .decision {
            text-align: center;
            font-size: 72px;
            font-weight: 900;
            margin: 25px 0;
        }

        .stButton > button {
            width: 100%;
            height: 80px;
            font-size: 28px;
            font-weight: 800;
            border-radius: 12px;
        }
    </style>
    """,
    unsafe_allow_html=True
)

st.markdown(
    '<div class="main-title">Autonomous AI Hedge Fund Terminal</div>',
    unsafe_allow_html=True
)

st.subheader("Trading Configuration")

symbol = st.text_input(
    "Trading Symbol",
    value="BTCUSD#",
    max_chars=20
).strip().upper()

st.write("")

if st.button("🚀 Start Analysis & Execute", use_container_width=True):
    if not symbol:
        st.error("Please enter a trading symbol.")
        st.stop()

    try:
        with st.status(
            "Data Analyst is fetching data...",
            expanded=True
        ) as status:
            st.write(f"Fetching market data for **{symbol}**...")
            market_data = get_market_data(symbol)
            status.update(
                label="Market data fetched successfully.",
                state="complete"
            )

        with st.status(
            "Senior Portfolio Manager is thinking...",
            expanded=True
        ) as status:
            st.write("Analyzing the 4H trend and 15M entry data...")
            decision = get_ai_decision(market_data)
            status.update(
                label="Portfolio decision completed.",
                state="complete"
            )

        st.markdown(
            f'<div class="decision">{decision}</div>',
            unsafe_allow_html=True
        )

        with st.status(
            "Risk Manager is executing...",
            expanded=True
        ) as status:
            if decision in ("BUY", "SELL"):
                st.write(f"Executing **{decision}** order for **{symbol}**...")
            else:
                st.write("Decision is HOLD. No trade will be executed.")

            result = execute_trade(symbol, decision)

            status.update(
                label="Execution process completed.",
                state="complete"
            )

        if result.startswith("SUCCESS"):
            st.success(result)
        elif result.startswith("HOLD"):
            st.info(result)
        else:
            st.error(result)

    except Exception as e:
        st.error(f"System Error: {e}")