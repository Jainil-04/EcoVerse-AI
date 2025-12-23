import streamlit as st
import json
import os
from datetime import datetime, date, timedelta
import pandas as pd
from openai import OpenAI
os.makedirs("data", exist_ok=True)

client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# ===============================
# ACCESS CONTROL
# ===============================
if not st.session_state.get("logged_in"):
    st.warning("Please login to access Carbon Tracker.")
    st.stop()

USER = st.session_state.get("user", "demo_user")

# ===============================
# PAGE HEADER
# ===============================
st.header("🌱 Carbon Footprint Tracker")
st.caption("Log daily activities, track emissions, earn EcoPoints.")

# ===============================
# FILE PATHS
# ===============================
DATA_DIR = "data"
CARBON_FILE = f"{DATA_DIR}/carbon_records.json"
USERS_FILE = f"{DATA_DIR}/users.json"
TXN_FILE = f"{DATA_DIR}/transactions.json"
BADGE_FILE = f"{DATA_DIR}/badges.json"

os.makedirs(DATA_DIR, exist_ok=True)

# ===============================
# HELPERS
# ===============================
def load_json(path, default):
    if not os.path.exists(path):
        return default
    try:
        with open(path, "r") as f:
            return json.load(f)
    except:
        return default

def save_json(path, data):
    with open(path, "w") as f:
        json.dump(data, f, indent=2)


carbon_data = load_json(CARBON_FILE, [])
users = load_json(USERS_FILE, {})
transactions = load_json(TXN_FILE, [])
badges = load_json(BADGE_FILE, {})

users.setdefault(USER, {"name": USER, "points": 0})
badges.setdefault(USER, [])


def predict_future_emissions(records, days=7):
    """
    Predict future CO2 emissions using moving average.
    Simple, explainable, no ML training.
    """
    if len(records) < 3:
        return None

    # Take last 7 days (or fewer if not available)
    recent = records[-7:]

    values = []
    for r in recent:
        if "co2_total" in r:
            values.append(r["co2_total"])

    if not values:
        return None

    avg = sum(values) / len(values)

    predictions = []
    for i in range(days):
        # small upward trend (2% per day)
        predicted = round(avg * (1 + i * 0.02), 2)
        predictions.append(predicted)

    return predictions

#=========================
#AI RECOMMENDATION FUNCTION
#==========================
# ===============================
# 🤖 AI RECOMMENDATION FUNCTION (SAFE)
# ===============================
def get_ai_sustainability_advice(user_records):
    if not user_records:
        return "Start logging your activities to receive AI-powered sustainability advice 🌱"

    recent = user_records[-7:]
    avg_co2 = sum(r["co2"] for r in recent) / len(recent)

    prompt = f"""
You are a sustainability AI assistant.

User's recent average daily carbon emission: {avg_co2:.2f} kg CO₂.

Give:
1. A clear assessment of the user's carbon behavior
2. 3 practical improvement suggestions
3. A short motivational message

Keep it simple, student-friendly, and actionable.
"""

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.6,
            max_tokens=200
        )

        return response.choices[0].message.content

    except Exception:
        return "⚠️ AI service temporarily unavailable. Please try again later."



# ====================================
# 🔮 AI CARBON PREDICTION FUNCTION
# ====================================
def predict_future_carbon(user_records):
    if len(user_records) < 3:
        return "Not enough data to predict future emissions. Log at least 3 days of activity."

    recent = user_records[-7:]  # last 7 days
    avg_co2 = sum(r["co2"] for r in recent) / len(recent)

    prompt = f"""
You are an environmental data analyst AI.

User's recent daily CO2 emissions (kg):
{[r['co2'] for r in recent]}

Average: {avg_co2:.2f} kg/day

Predict:
1. Expected average daily CO2 for next 7 days
2. Whether emissions are increasing, stable, or decreasing
3. One early warning or encouragement message
"""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.4,
        max_tokens=180
    )

    return response.choices[0].message.content

# ===============================
# EMISSION FACTORS (Demo)
# ===============================
FACTORS = {
    "Car": 0.21,
    "Bus": 0.10,
    "Train": 0.04,
    "Bike": 0.0,
    "Walk": 0.0,
    "Electricity": 0.85
}

# ===============================
# DAILY INPUT FORM
# ===============================
st.subheader("📅 Log Today’s Carbon Activity")

with st.form("carbon_form"):
    c1, c2 = st.columns(2)

    with c1:
        mode = st.selectbox("Travel Mode", list(FACTORS.keys())[:-1])
        km = st.number_input("Distance (km)", min_value=0.0, step=0.5)

    with c2:
        electricity = st.number_input("Electricity (kWh)", min_value=0.0, step=0.1)
        lifestyle = st.slider("Lifestyle Impact", 0.0, 1.0, 0.3)

    submit = st.form_submit_button("✅ Save Entry")

# ===============================
# PROCESS ENTRY
# ===============================
if submit:
    travel_co2 = km * FACTORS[mode]
    electricity_co2 = electricity * FACTORS["Electricity"]
    lifestyle_co2 = lifestyle * 2.0

    total_co2 = round(travel_co2 + electricity_co2 + lifestyle_co2, 2)

    entry = {
        "user": USER,
        "date": date.today().isoformat(),
        "timestamp": datetime.now().isoformat(),
        "travel_mode": mode,
        "co2": total_co2
    }

    carbon_data.append(entry)
    save_json(CARBON_FILE, carbon_data)

    # ===============================
    # ECOPOINTS ENGINE
    # ===============================
    points = max(0, int(50 - total_co2 * 5))
    users[USER]["points"] += points

    transactions.append({
        "user": USER,
        "type": "carbon_entry",
        "co2": total_co2,
        "points": points,
        "timestamp": datetime.now().isoformat()
    })

    save_json(USERS_FILE, users)
    save_json(TXN_FILE, transactions)

    st.success(f"Saved! CO₂: {total_co2} kg | Points: +{points}")
    st.rerun()

# ===============================
# HISTORY & CHART
# ===============================
st.markdown("---")
st.subheader("📊 Your Carbon History")

user_records = [r for r in carbon_data if r["user"] == USER]

if user_records:
    df = pd.DataFrame(user_records)
    df["date"] = pd.to_datetime(df["date"])
    st.line_chart(df.set_index("date")["co2"])

# ===============================
# STREAKS & BADGES
# ===============================
st.markdown("---")
st.subheader("🏆 Green Streaks & Badges")

today = date.today()
dates = sorted({date.fromisoformat(r["date"]) for r in user_records})
streak = 0

for i in range(len(dates)-1, -1, -1):
    if dates[i] == today - timedelta(days=streak):
        streak += 1
    else:
        break

st.metric("Current Green Streak", f"{streak} day(s)")

# Award badges
def award_badge(name):
    if name not in badges[USER]:
        badges[USER].append(name)

if streak >= 3:
    award_badge("🌿 3-Day Green Streak")
if streak >= 7:
    award_badge("🔥 7-Day Eco Champion")

save_json(BADGE_FILE, badges)

if badges[USER]:
    st.write("Your badges:")
    for b in badges[USER]:
        st.success(b)

# ===============================
# AI RECOMMENDATIONS (RULE-BASED)
# ===============================
# ==================================
# 🤖 AI RECOMMENDATIONS (OPENAI POWERED)
# ==================================
st.markdown("---")
st.subheader("🤖 AI Sustainability Assistant")

if user_records:
    with st.spinner("Analyzing your carbon footprint with AI..."):
        advice = get_ai_sustainability_advice(user_records)

    st.success(advice)
else:
    st.info("Log some carbon data to unlock AI-powered insights 🌱")

# ====================================
# 🔮 CARBON PREDICTION (FUTURE)
# ====================================
st.markdown("---")
st.subheader("🔮 Carbon Emission Forecast")

if user_records:
    with st.spinner("Predicting your future carbon emissions..."):
        prediction = predict_future_carbon(user_records)

    st.info(prediction)
else:
    st.info("Log some carbon data to enable future emission prediction 📈")

# 


# ===============================
# REWARDS CONNECTION NOTE
# ===============================
st.markdown("---")
st.info("🎁 EcoPoints earned here can be redeemed in the Rewards page.")


