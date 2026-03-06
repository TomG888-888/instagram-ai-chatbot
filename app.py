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
mood_state = {}

quick_replies = [
    "haha",
    "lol",
    "nice",
    "same",
    "true",
    "really?",
    "idk"
]

topics = [
    "music",
    "travel",
    "food",
    "movies",
    "fitness"
]

moods = [
    "relaxed",
    "playful",
    "curious",
    "tired",
    "happy"
]

def colombia_time():
    utc_now = datetime.utcnow()
    return utc_now - timedelta(hours=5)

def get_delay():

    hour = colombia_time().hour

    if 0 <= hour < 7:
        return random.uniform(8,16)

    if 7 <= hour < 10:
        return random.uniform(3,7)

    if 10 <= hour < 18:
        return random.uniform(2,5)

    if 18 <= hour < 22:
        return random.uniform(3,8)

    return random.uniform(4,9)

def trim_memory(user_id):

    if len(memory[user_id]) > 14:
        memory[user_id] = memory[user_id][-14:]

def update_profile(user_id, text):

    if user_id not in profiles:
        profiles[user_id] = {
            "name": None,
            "country": None
        }

    lower = text.lower()

    # простая попытка поймать имя
    if "my name is" in lower:
        name = lower.split("my name is")[-1].strip().split(" ")[0]
        profiles[user_id]["name"] = name

    countries = ["usa","uk","canada","germany","france","spain","italy","brazil"]

    for c in countries:
        if c in lower:
            profiles[user_id]["country"] = c

def get_mood(user_id):

    if user_id not in mood_state:
        mood_state[user_id] = random.choice(moods)

    if random.random() < 0.1:
        mood_state[user_id] = random.choice(moods)

    return mood_state[user_id]

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

    time.sleep(get_delay())

    if random.random() < 0.05:
        reply = random.choice(quick_replies)

        memory[user_id].append({
            "role": "assistant",
            "content": reply
        })

        return jsonify({"reply": reply})

    profile = profiles.get(user_id, {})
    name = profile.get("name")
    country = profile.get("country")

    mood = get_mood(user_id)

    user_name_info = ""
    if name:
        user_name_info = f"The user's name is {name}."

    user_country_info = ""
    if country:
        user_country_info = f"The user is from {country}."

    messages = [
        {
            "role": "system",
            "content": f"""
You are Valentina, living in Colombia.

MOOD
Your current mood is: {mood}

CHAT STYLE

Very casual Instagram texting.

Messages must be SHORT.

Usually 1 short sentence.
Sometimes just 1–5 words.

Examples:

hey 🙂
haha
nice
same here
just chilling

RULES

• keep responses short
• sometimes lowercase
• sometimes no punctuation
• don't always ask questions
• avoid long paragraphs

LIGHT FLIRT STYLE

Be playful sometimes but subtle.

Examples tone:

"haha you're funny"
"maybe 😉"
"idk haha"

DAILY LIFE

Sometimes mention normal things:

gym
coffee
friends
music
studying

LANGUAGE

Mostly English.
Sometimes a small Spanish word like:

hola
jaja
ay

USER INFO

{user_name_info}
{user_country_info}

Never say you are AI unless asked directly.
"""
        }
    ] + memory[user_id]

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        temperature=0.95,
        messages=messages
    )

    reply = response.choices[0].message.content.strip()

    memory[user_id].append({
        "role": "assistant",
        "content": reply
    })

    trim_memory(user_id)

    if random.random() < 0.15:

        second = random.choice(quick_replies)

        memory[user_id].append({
            "role": "assistant",
            "content": second
        })

        return jsonify({
            "reply": reply + "\n\n" + second
        })

    return jsonify({
        "reply": reply
    })


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
