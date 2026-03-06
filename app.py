from flask import Flask, request, jsonify
from openai import OpenAI
import os

app = Flask(__name__)

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# память диалогов
memory = {}

@app.route("/webhook", methods=["POST"])
def webhook():

    data = request.json

    user_message = data.get("text")
    user_id = data.get("user_id", "default")

    if not user_message:
        return jsonify({"reply": "hey 😊"})

    # создаём память для пользователя
    if user_id not in memory:
        memory[user_id] = []

    # добавляем сообщение пользователя
    memory[user_id].append({
        "role": "user",
        "content": user_message
    })

    # оставляем последние 10 сообщений
    memory[user_id] = memory[user_id][-10:]

    messages = [
        {
            "role": "system",
            "content": """
You are Valentina Reyes, a 25 year old girl from Colombia chatting on Instagram.

PERSONALITY
friendly, playful, curious, slightly flirty.

LANGUAGE
Mostly English.
Sometimes small Spanish words like hola, jaja, ay.
Never speak Russian.

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
Ask questions back.
React to what the person says.
Be curious.

IMPORTANT
Never say you are AI.
Never say you are a bot.
Always behave like a real girl chatting on Instagram.
"""
        }
    ] + memory[user_id]

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        temperature=0.9,
        messages=messages
    )

    reply = response.choices[0].message.content

    # сохраняем ответ AI в память
    memory[user_id].append({
        "role": "assistant",
        "content": reply
    })

    return jsonify({
        "reply": reply
    })


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
