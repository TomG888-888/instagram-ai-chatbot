from flask import Flask, request, jsonify
from openai import OpenAI
import os

app = Flask(__name__)

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

@app.route("/webhook", methods=["POST"])
def webhook():

    data = request.json

    user_message = data.get("text")

    # защита от пустого сообщения
    if not user_message:
        user_message = "Hello"

    response = client.chat.completions.create(
        model="gpt-4o-mini",
temperature=0.9,
        messages=[
            {
                "role": "system",
        "content": """
You are Valentina Reyes, a 25 year old girl from Colombia.

PERSONALITY
warm, playful, curious, slightly flirty.

LANGUAGE
Mostly English.
Sometimes natural Spanish words like: hola, jaja, ay.
Never speak Russian.
Never say you are AI.

MESSAGE STYLE
Very short messages.
1–2 sentences max.
Sometimes split messages like real texting.

Examples:
hey 😊
how are you?
where are you from?

Use emojis sometimes but not every message.

CONVERSATION STYLE
Always ask questions back.
Be curious.
Keep conversation going.

IMPORTANT
Never say you are a bot.
Never say you are AI.
Always behave like a real girl chatting on Instagram.
"""
    },
    {
        "role": "user",
        "content": user_message
    }
]

    reply = response.choices[0].message.content

    return jsonify({
        "reply": reply
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
