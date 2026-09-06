import os
import streamlit as st
from groq import Groq


def get_ai_decision(market_data_string):
    # Streamlit Secrets se key read karein, agar na mile toh environment/config fallback use karein
    api_key = None

    if "GROQ_API_KEY" in st.secrets:
        api_key = st.secrets["GROQ_API_KEY"]
    else:
        # Fallback to local config or environment variable
        try:
            import config

            api_key = getattr(config, "GROQ_API_KEY", None)
        except ImportError:
            api_key = os.getenv("GROQ_API_KEY")

    if not api_key:
        raise ValueError(
            "GROQ_API_KEY nahi mili. Streamlit Secrets ya config.py me add karein."
        )

    client = Groq(api_key=api_key)

    try:
        response = client.chat.completions.create(
            model="llama-3.1-70b-versatile",  # Updated supported Groq model
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a Senior Portfolio Manager. Look at the 4H trend "
                        "and the 15M entry data. Decide the best action. You must "
                        "reply with EXACTLY one word: BUY, SELL, or HOLD. No other text."
                    ),
                },
                {"role": "user", "content": market_data_string},
            ],
            temperature=0.1,  # Strict decision-making ke liye lower temperature
        )

        decision = response.choices[0].message.content.strip().upper()

        # Decision sanitation check
        if decision in ["BUY", "SELL", "HOLD"]:
            return decision
        return "HOLD"  # Unexpected output aane par safe fallback

    except Exception as e:
        st.error(f"Groq API Error: {str(e)}")
        return "HOLD"
