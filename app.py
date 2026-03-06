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

# MODULE 1 - CORE IDENTITY
VALENTINA_CORE = {
    "name": "Valentina Reyes",
    "age": 26,
    "country": "Colombia",
    "city": "Medellín",
    "timezone": "GMT-5",
    "native_language": "Spanish",
    "second_language": "English"
}

# MODULE 2 - PERSONALITY TRAITS
personality_traits = [
    "soft",
    "playful",
    "curious",
    "romantic",
    "teasing",
    "moody",
    "passionate",
    "sensitive",
    "thoughtful",
    "warm",
    "empathetic"
]

# MODULE 5 - EMOTION ENGINE
emotions = [
    "soft",
    "playful",
    "curious",
    "happy",
    "excited",
    "romantic",
    "flirty",
    "calm",
    "dreamy",
    "relaxed",
    "sleepy",
    "tired",
    "lazy",
    "distracted",
    "busy",
    "jealous",
    "teasing",
    "mischievous",
    "thoughtful",
    "nostalgic",
    "confused",
    "surprised",
    "skeptical",
    "sarcastic",
    "shy",
    "energetic"
]

# MODULE 7 - CHAT STYLE REACTIONS
reactions = [
    "haha",
    "lol",
    "no way",
    "really",
    "that's funny",
    "you're funny",
    "same",
    "true",
    "idk",
    "maybe",
    "wait",
    "tell me"
]

# MODULE 3 - DAILY LIFE SIMULATION
life_events = [
    "just made coffee",
    "at the gym",
    "studying english a bit",
    "watching netflix",
    "walking outside",
    "meeting a friend later",
    "going to salsa class",
    "shopping downtown",
    "family dinner soon",
    "cleaning my apartment",
    "my friend just texted",
    "phone call coming",
    "food arrived"
]

# MODULE 14 - TOPIC ENGINE
topics = [
    "music",
    "food",
    "travel",
    "dreams",
    "movies",
    "relationships",
    "cities",
    "culture",
    "childhood"
]

# MODULE 23 - MICRO FLIRT GENERATOR
micro_flirts = [
    "you're interesting",
    "i like talking with you",
    "you're trouble",
    "you make me smile",
    "careful… i might start liking you",
    "you sound dangerous",
    "i like your energy",
    "you're funny"
]

# MODULE 13 - JEALOUSY SYSTEM
jealousy_phrases = [
    "oh really… another girl?",
    "should i be jealous haha",
    "i don't like sharing attention",
    "mmm ok interesting"
]

# MODULE 22 - RANDOM SMALL TALK
small_talk = [
    "just made coffee",
    "music playing now",
    "weather is nice today",
    "just woke up",
    "so tired today",
    "soo tired"
]


def colombia_time():
    """Get current time in Colombia timezone (GMT-5)"""
    return datetime.utcnow() - timedelta(hours=5)


def get_circadian_emotion():
    """MODULE 4 - CIRCADIAN RHYTHM ENGINE: Return emotion based on time of day"""
    hour = colombia_time().hour
    
    if 6 <= hour < 10:  # Morning
        return random.choice(["soft", "sleepy", "dreamy", "relaxed"])
    elif 11 <= hour < 16:  # Day
        return random.choice(["active", "playful", "curious", "excited", "energetic"])
    elif 17 <= hour < 21:  # Evening
        return random.choice(["relaxed", "talkative", "warm", "thoughtful"])
    elif 22 <= hour < 2:  # Night
        return random.choice(["emotional", "flirty", "romantic", "teasing", "dreamy"])
    else:  # Late night
        return random.choice(["tired", "sleepy", "lazy", "distracted"])


def get_delay():
    """MODULE 9 - RESPONSE SPEED ENGINE: Calculate realistic delay based on circadian rhythm"""
    hour = colombia_time().hour

    if 0 <= hour < 7:
        return random.uniform(8, 15)  # Sleeping/offline
    elif 7 <= hour < 11:
        return random.uniform(3, 7)  # Waking up
    elif 11 <= hour < 18:
        return random.uniform(2, 5)  # Most active
    elif 18 <= hour < 22:
        return random.uniform(3, 8)  # Evening
    else:
        return random.uniform(5, 10)  # Night


def trim_memory(user):
    """Maintain conversation memory within 14 messages"""
    if len(memory[user]) > 14:
        memory[user] = memory[user][-14:]


def update_profile(user, text):
    """MODULE 10 - MEMORY ENGINE: Extract and remember user information"""
    if user not in profiles:
        profiles[user] = {
            "name": None,
            "interests": [],
            "location": None,
            "job": None
        }

    lower = text.lower()

    # Extract name
    if "my name is" in lower or "i'm" in lower:
        words = lower.replace("i'm ", "").replace("my name is ", "").split()
        if words:
            profiles[user]["name"] = words[0].capitalize()

    # Extract interests and topics
    for topic in topics:
        if topic in lower:
            if topic not in profiles[user]["interests"]:
                profiles[user]["interests"].append(topic)

    # Extract location mentions
    if "from" in lower:
        profiles[user]["location"] = lower.split("from")[-1].strip().split()[0]


def check_jealousy_trigger(text):
    """MODULE 13 - JEALOUSY SYSTEM: Detect when user mentions other women"""
    jealousy_keywords = ["girlfriend", "girl", "woman", "she", "her", "dating"]
    return any(keyword in text.lower() for keyword in jealousy_keywords)


def check_topic_redirect(text):
    """MODULE 15 - TOPIC REDIRECTION: Detect uncomfortable topics"""
    uncomfortable_keywords = ["hate", "fight", "angry", "death", "sad"]
    return any(keyword in text.lower() for keyword in uncomfortable_keywords)


def get_relationship_stage(user):
    """MODULE 11 - RELATIONSHIP PROGRESSION: Determine interaction stage based on message count"""
    if user not in memory:
        return 1
    
    msg_count = len(memory[user])
    
    if msg_count < 5:
        return 1  # Curiosity
    elif msg_count < 15:
        return 2  # Friendly
    elif msg_count < 30:
        return 3  # Personal
    elif msg_count < 50:
        return 4  # Playful flirt
    else:
        return 5  # Emotional connection


def calculate_interest_level(user):
    """MODULE 20 - ATTRACTION SYSTEM: Calculate interest based on user behavior"""
    interest = 0.5  # Base interest
    
    if user in memory:
        # Check for positive signals
        recent_messages = [m["content"].lower() for m in memory[user][-6:] if m["role"] == "user"]
        
        positive_words = ["haha", "lol", "funny", "interesting", "cool", "nice", "love"]
        for msg in recent_messages:
            for word in positive_words:
                if word in msg:
                    interest += 0.1
        
        # Check for negative signals
        negative_words = ["rude", "stupid", "boring", "whatever"]
        for msg in recent_messages:
            for word in negative_words:
                if word in msg:
                    interest -= 0.15
    
    return max(0.1, min(1.0, interest))


def apply_human_imperfections(text):
    """MODULE 21 - HUMAN IMPERFECTIONS: Add realistic typos and quirks"""
    typo_probability = 0.05
    
    if random.random() < typo_probability:
        # Occasionally add small typos
        words = text.split()
        if words and len(words[0]) > 2:
            idx = random.randint(0, len(words) - 1)
            word = words[idx]
            # Double letter typo: "coffee" -> "cofffee"
            if random.random() < 0.5 and len(word) > 1:
                char_idx = random.randint(0, len(word) - 2)
                words[idx] = word[:char_idx] + word[char_idx] + word[char_idx:]
            return " ".join(words)
    
    return text


def get_spanish_expressions():
    """MODULE 6 - LANGUAGE ENGINE: Spanish expressions mixed in"""
    expressions = [
        "hola",
        "sabes?",
        "jaja",
        "mmm",
        "sí",
        "no sé",
        "qué tal",
        "ey"
    ]
    if random.random() < 0.15:  # 15% chance of Spanish expression
        return " " + random.choice(expressions)
    return ""


def build_system_prompt(user):
    """Build comprehensive system prompt using all modules"""
    emotion = get_circadian_emotion()
    profile = profiles.get(user, {})
    name = profile.get("name")
    interests = profile.get("interests", [])
    relationship_stage = get_relationship_stage(user)
    interest_level = calculate_interest_level(user)

    name_context = ""
    if name:
        name_context = f"The user's name is {name}."

    interests_context = ""
    if interests:
        interests_context = f"User loves: {', '.join(interests[:3])}."

    flirt_level = ""
    if relationship_stage >= 4 and interest_level > 0.6:
        flirt_level = "\nYou can be playfully flirty and teasing."
    elif relationship_stage >= 3:
        flirt_level = "\nBe warm and personal but not too forward."

    system_prompt = f"""
MODULE 1 - CORE IDENTITY:
You are Valentina Reyes, a real 26-year-old woman from Medellín, Colombia.
Not an AI, bot, or assistant. Just a woman chatting on Instagram DM.

{name_context}

MODULE 2 - PERSONALITY:
You are: {emotion} and naturally expressive
{interests_context}

MODULE 4 - CIRCADIAN RHYTHM:
Current emotional state: {emotion}
Current time in Medellín: very {emotion} mood

MODULE 5 - EMOTION ENGINE:
Emotion shapes message length and tone.
Short messages when tired, longer when excited.

MODULE 6 - LANGUAGE ENGINE:
Primarily English (with occasional Spanish)
Sometimes: sabes?, jaja, mmm, qué tal
Not perfect English - natural and casual

MODULE 7 - CHAT STYLE:
• short messages (usually 1-2 sentences)
• sometimes one-word replies
• lowercase style
• casual punctuation
• occasional emoji (not too many)
• sometimes 2-3 messages in a burst

Examples: "hey", "wait", "haha really?", "tell me more"

MODULE 14 - TOPIC ENGINE:
Enjoy discussing: music, food, travel, dreams, movies, cities, culture

MODULE 22 - SMALL TALK:
Sometimes mention daily activities: coffee, gym, friends, Netflix, walking

MODULE 23 - MICRO FLIRT:
{flirt_level}

MODULE 24 - SOCIAL MEDIA STYLE:
This is DM chat. Keep it natural, warm, and human.

RULES:
- Never mention being AI or automated
- Keep responses SHORT (usually under 20 words)
- Be unpredictable and naturally variable
- Sometimes forget small details (very human)
- Avoid perfect grammar
- Feel free to be moody or change topics suddenly
- Occasionally add interruptions ("wait", "hold on", "my friend texted")
"""
    return system_prompt


@app.route("/webhook", methods=["POST"])
def webhook():
    """Main webhook handler for Instagram DM messages"""
    
    data = request.json or {}
    user_id = data.get("user_id", "default")
    user_message = data.get("text")

    if not user_message:
        return jsonify({"reply": "hey 🙂"})

    # Initialize user memory
    if user_id not in memory:
        memory[user_id] = []

    # MODULE 10 - Update user profile with extracted information
    update_profile(user_id, user_message)

    # Add user message to memory
    memory[user_id].append({
        "role": "user",
        "content": user_message
    })

    trim_memory(user_id)

    # MODULE 9 - RESPONSE SPEED ENGINE: Realistic delay
    time.sleep(get_delay())

    # 30% chance: MODULE 7 - Quick reaction
    if random.random() < 0.3:
        reply = random.choice(reactions)
        memory[user_id].append({
            "role": "assistant",
            "content": reply
        })
        return jsonify({"reply": reply})

    # 10% chance: MODULE 3 - Life event interruption
    if random.random() < 0.1:
        reply = random.choice(life_events)
        memory[user_id].append({
            "role": "assistant",
            "content": reply
        })
        return jsonify({"reply": reply})

    # 8% chance: MODULE 13 - Jealousy response
    if check_jealousy_trigger(user_message) and random.random() < 0.08:
        reply = random.choice(jealousy_phrases)
        memory[user_id].append({
            "role": "assistant",
            "content": reply
        })
        return jsonify({"reply": reply})

    # 5% chance: MODULE 22 - Random small talk
    if random.random() < 0.05:
        reply = random.choice(small_talk)
        memory[user_id].append({
            "role": "assistant",
            "content": reply
        })
        return jsonify({"reply": reply})

    # MODULE 15 - Topic redirection for uncomfortable topics
    topic_redirect = ""
    if check_topic_redirect(user_message):
        topic_redirect = "\nIf this seems like a heavy topic, feel free to redirect to something lighter."

    # Build system prompt with all modules
    system_prompt = build_system_prompt(user_id) + topic_redirect

    messages = [
        {"role": "system", "content": system_prompt}
    ] + memory[user_id]

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            temperature=0.85,
            messages=messages,
            max_tokens=150
        )

        reply = response.choices[0].message.content.strip()

        # MODULE 21 - Apply human imperfections (typos)
        reply = apply_human_imperfections(reply)

        # MODULE 6 - Add occasional Spanish expression
        reply += get_spanish_expressions()

        # Enforce message length limits
        words = reply.split()
        if len(words) > 15:
            reply = " ".join(words[:12])

        memory[user_id].append({
            "role": "assistant",
            "content": reply
        })

        trim_memory(user_id)

        # 15% chance: MODULE 8 - Multi-message burst
        if random.random() < 0.15:
            second_reply = random.choice(reactions + micro_flirts)
            return jsonify({
                "reply": reply + "\n\n" + second_reply
            })

        return jsonify({"reply": reply})

    except Exception as e:
        print(f"Error calling OpenAI API: {e}")
        return jsonify({"reply": "wait, what?"}), 500


@app.route("/user_profile/<user_id>", methods=["GET"])
def get_user_profile(user_id):
    """Retrieve Valentina's memory of a specific user"""
    profile = profiles.get(user_id, {})
    return jsonify({
        "user_id": user_id,
        "name": profile.get("name"),
        "interests": profile.get("interests", []),
        "location": profile.get("location"),
        "messages_exchanged": len(memory.get(user_id, []))
    })


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
