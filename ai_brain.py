import config
from groq import Groq


def get_ai_decision(market_data_string):
    client = Groq(api_key=config.GROQ_API_KEY)

    response = client.chat.completions.create(
        model="openai/gpt-oss-20b",
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a Senior Portfolio Manager. Look at the 4H trend "
                    "and the 15M entry data. Decide the best action. You must "
                    "reply with EXACTLY one word: BUY, SELL, or HOLD. No other text."
                )
            },
            {
                "role": "user",
                "content": market_data_string
            }
        ]
    )

    return response.choices[0].message.content.strip()