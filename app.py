from flask import Flask, request, jsonify
from openai import OpenAI
import os
import time
import random
from datetime import datetime, timedelta

app = Flask(__name__)

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

memory = {}
profiles = {}

# реакции
reactions = [
    "lol",
    "haha",
    "nice",
    "same",
    "true",
    "idk",
    "maybe",
    "😄"
]

# короткие вопросы
questions = [
    "you?",
    "why?",
    "how so?",
    "really?",
    "what happened?"
]

# перевод UTC → Colombia
def colombia_time():
    return datetime.utcnow() - timedelta(hours=5)


# задержка ответа
def get_delay():

    hour = colombia_time().hour

    if 0 <= hour < 7:
        return random.uniform(6,12)

    if 7 <= hour < 10:
        return random.uniform(3,7)

    if 10 <= hour < 18:
        return random.uniform(2,5)

    if 18 <= hour < 22:
        return random.uniform(3,7)

    return random.uniform(4,8)


# ограничение памяти
def trim_memory(user_id):

    if len(memory[user_id]) > 12:
        memory[user_id] = memory[user_id][-12:]


# обновление профиля
def update_profile(user_id, text):

    if user_id not in profiles:
        profiles[user_id] = {}

    lower = text.lower()

    if "my name is" in lower:
        name = lower.split("my name is")[-1].strip().split(" ")[0]
        profiles[user_id]["name"] = name


@app.route("/webhook", methods=["POST"])
def webhook():

    data = request.json or {}

    user_message = data.get("text")
    user_id = data.get("user_id", "default")

    if not user_message:
        return jsonify({"reply": "hey 🙂"})

    if user_id not in memory:
        memory[user_id] = []

    update_profile(user_id, user_message)

    memory[user_id].append({
        "role": "user",
        "content": user_message
    })

    trim_memory(user_id)

    # задержка
    time.sleep(get_delay())

    # тип ответа
    r = random.random()

    # 40% реакции
    if r < 0.4:

        reply = random.choice(reactions)

        memory[user_id].append({
            "role": "assistant",
            "content": reply
        })

        return jsonify({"reply": reply})

    # 20% короткий вопрос
    if r < 0.6:

        reply = random.choice(questions)

        memory[user_id].append({
            "role": "assistant",
            "content": reply
        })

        return jsonify({"reply": reply})

    # 40% AI ответ

    profile = profiles.get(user_id, {})

    name = profile.get("name", "")

    name_info = ""
    if name:
        name_info = f"The user's name is {name}."

    messages = [
        {
            "role": "system",
            "content": f"""
You are Valentina living in Colombia.

STYLE

Instagram texting style.

Short messages only.

Usually 1 short sentence.
Sometimes just 1-4 words.

Examples

hey 🙂
just chilling
same here
nice
lol

RULES

• keep messages short
• casual tone
• sometimes lowercase
• do not write long sentences
• do not explain things

Sometimes mention:

coffee
gym
music
friends

{ name_info }

Never say you are AI unless asked directly.
"""
        }
    ] + memory[user_id]

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        temperature=0.9,
        messages=messages
    )

    reply = response.choices[0].message.content.strip()

    # ограничение длины ответа
    words = reply.split()

    if len(words) > 8:
        reply = " ".join(words[:6])

    memory[user_id].append({
        "role": "assistant",
        "content": reply
    })

    trim_memory(user_id)

    # иногда второе сообщение
    if random.random() < 0.15:

        second = random.choice(reactions)

        return jsonify({
            "reply": reply + "\n\n" + second
        })

    return jsonify({
        "reply": reply
    })


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
