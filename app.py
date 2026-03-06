from flask import Flask, request, jsonify
from openai import OpenAI
import os
import random
import time
from datetime import datetime, timedelta

app = Flask(__name__)

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

memory = {}
profiles = {}

# реакции
reactions = [
    "haha",
    "lol",
    "nice",
    "really?",
    "same",
    "true",
    "idk",
    "maybe"
]

# события жизни
life_events = [
    "just made coffee",
    "at the gym",
    "studying a bit",
    "watching netflix",
    "walking outside",
    "meeting a friend later",
]

# эмоции
emotions = [
    "playful",
    "curious",
    "relaxed",
    "sleepy",
    "happy",
    "dreamy",
    "thoughtful"
]

# темы
topics = [
    "music",
    "travel",
    "food",
    "movies",
    "cities",
    "culture"
]

def colombia_time():
    return datetime.utcnow() - timedelta(hours=5)


def get_delay():

    hour = colombia_time().hour

    if 0 <= hour < 7:
        return random.uniform(8,15)

    if 7 <= hour < 11:
        return random.uniform(3,7)

    if 11 <= hour < 18:
        return random.uniform(2,5)

    if 18 <= hour < 22:
        return random.uniform(3,8)

    return random.uniform(5,10)


def trim_memory(user):

    if len(memory[user]) > 14:
        memory[user] = memory[user][-14:]


def update_profile(user, text):

    if user not in profiles:
        profiles[user] = {}

    lower = text.lower()

    if "my name is" in lower:
        name = lower.split("my name is")[-1].strip().split(" ")[0]
        profiles[user]["name"] = name


@app.route("/webhook", methods=["POST"])
def webhook():

    data = request.json or {}

    user_id = data.get("user_id", "default")
    user_message = data.get("text")

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

    time.sleep(get_delay())

    # 30% реакция
    if random.random() < 0.3:

        reply = random.choice(reactions)

        memory[user_id].append({
            "role": "assistant",
            "content": reply
        })

        return jsonify({"reply": reply})

    # 10% событие жизни
    if random.random() < 0.1:

        reply = random.choice(life_events)

        memory[user_id].append({
            "role": "assistant",
            "content": reply
        })

        return jsonify({"reply": reply})

    emotion = random.choice(emotions)
    topic = random.choice(topics)

    profile = profiles.get(user_id, {})
    name = profile.get("name")

    name_context = ""
    if name:
        name_context = f"The user's name is {name}."

    system_prompt = f"""
You are Valentina, a conversational AI persona inspired by a woman living in Medellín, Colombia.

Current emotional tone: {emotion}

Chat style:

• short messages
• casual social media tone
• sometimes one-word replies
• sometimes two short messages
• occasional emoji

Languages:

Mostly English.
Sometimes small Spanish expressions like:

hola
jaja
mmm

Conversation topics you enjoy:

music
travel
food
movies
cities
culture

Sometimes mention normal daily things:

coffee
gym
friends
studying
walking outside

{ name_context }

Keep messages natural and short.
Avoid long explanations.
"""

    messages = [
        {"role": "system", "content": system_prompt}
    ] + memory[user_id]

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        temperature=0.9,
        messages=messages
    )

    reply = response.choices[0].message.content.strip()

    # ограничиваем длину
    words = reply.split()

    if len(words) > 10:
        reply = " ".join(words[:8])

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

    return jsonify({"reply": reply})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
