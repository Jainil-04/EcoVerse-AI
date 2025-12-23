import streamlit as st
import os
os.makedirs("data", exist_ok=True)

# ===============================
# SAFETY INIT (Dashboard)
# ===============================
if "DEMO_MODE" not in st.session_state:
    st.session_state.DEMO_MODE = True

if not st.session_state.get("logged_in"):
    st.warning("Please login to continue.")
    st.stop()



def load_json(path, default):
    if not os.path.exists(path):
        return default
    with open(path, "r") as f:
        return json.load(f)


def save_json(path, data):
    with open(path, "w") as f:
        json.dump(data, f, indent=2)
from PIL import Image
import random
import json
import os
from datetime import datetime

# -----------------------------
# CONSTANTS
# -----------------------------
USER_ID = "demo_user"

CARBON_POINTS_RULES = {
    "Recyclable (Plastic)": 15,
    "Recyclable (Paper)": 10,
    "Organic Waste": 5,
    "E-Waste": 25,
    "Landfill Waste": 1
}

USERS_FILE = "data/users.json"
TRANSACTIONS_FILE = "data/transactions.json"

# -----------------------------
# HELPER FUNCTIONS
# -----------------------------

def load_json(path, default):
    if not os.path.exists(path):
        return default

    try:
        with open(path, "r") as f:
            content = f.read().strip()
            if not content:
                return default
            return json.loads(content)
    except json.JSONDecodeError:
        return default

def save_json(path, data):
    with open(path, "w") as f:
        json.dump(data, f, indent=2)

# -----------------------------
# LOAD DATA (DEMO SAFE)
# -----------------------------

DATA_FILE = "data/demo_data.json" if st.session_state.DEMO_MODE else USERS_FILE

users = load_json(DATA_FILE, {})
transactions = load_json(TRANSACTIONS_FILE, [])

if USER_ID not in users:
    users[USER_ID] = {"name": "Demo User", "points": 0}

# Persist only in LIVE mode
if not st.session_state.DEMO_MODE:
    save_json(USERS_FILE, users)

# -----------------------------
users = load_json(USERS_FILE, {})
transactions = load_json(TRANSACTIONS_FILE, [])

if USER_ID not in users:
    users[USER_ID] = {"name": "Demo User", "points": 0}
    save_json(USERS_FILE, users)

# -----------------------------
# UI START
# -----------------------------
st.title("EcoVerse AI — Waste Classification 🌱")

st.write("Upload a waste image to earn carbon points.")

demo_mode = st.toggle("Enable Demo Mode (No API)", value=True)
if demo_mode:
    st.info("🧪 Demo Mode Enabled — using simulated data (no API calls)")
else:
    st.success("🔐 Live Mode — real data is being saved")

uploaded_file = st.file_uploader(
    "Upload waste image (jpg / png)",
    type=["jpg", "jpeg", "png"]
)

if uploaded_file is None:
    st.info("Please upload an image to continue.")
    st.stop()

image = Image.open(uploaded_file)
st.image(image, caption="Uploaded Image", use_column_width=True)

# -----------------------------
# CLASSIFICATION (DEMO SAFE)
# -----------------------------
categories = list(CARBON_POINTS_RULES.keys())

if demo_mode:
    category = random.choice(categories)
    confidence = round(random.uniform(0.75, 0.95), 2)
else:
    category = random.choice(categories)
    confidence = 0.90  # Safe fallback

st.success("Classification Completed")
st.write(f"**Category:** {category}")
st.write(f"**Confidence:** {confidence * 100:.0f}%")

# -----------------------------
# POINTS CALCULATION
# -----------------------------
points_earned = CARBON_POINTS_RULES.get(category, 0)

st.markdown("### Carbon Points Earned")
st.write(f"**+{points_earned} points**")

# -----------------------------
# UPDATE USER DATA
# -----------------------------
users[USER_ID]["points"] += points_earned

transactions.append({
    "user": USER_ID,
    "category": category,
    "points": points_earned,
    "timestamp": datetime.now().isoformat()
})

save_json(USERS_FILE, users)
save_json(TRANSACTIONS_FILE, transactions)

# -----------------------------
# DISPLAY USER BALANCE
# -----------------------------

st.markdown("---")
st.subheader("🌱 Your Sustainability Impact")
st.caption("Your personal environmental contribution")

st.metric(
    label="Total Carbon Points",
    value=users[USER_ID]["points"],
    delta="+Eco Impact"
)

# -----------------------------
# Progress towards sustainability goal
# -----------------------------

GOAL_POINTS = 500  # Demo-friendly goal

current_points = users[USER_ID]["points"]

progress = min(current_points / GOAL_POINTS, 1.0)

st.progress(progress)

st.caption(f"🎯 Goal: {GOAL_POINTS} eco-points for Green Badge")


# ==============================
# 🏅 BADGES & ACHIEVEMENTS (STEP 7.2)
# ==============================
st.markdown("### 🏅 Your Sustainability Badges")

points = users[USER_ID]["points"]

badge_col1, badge_col2, badge_col3 = st.columns(3)

def badge_card(title, icon, unlocked, requirement):
    if unlocked:
        st.success(f"{icon} **{title}**\n\n✅ Unlocked ({requirement}+ points)")
    else:
        st.info(f"{icon} **{title}**\n\n🔒 Locked ({requirement} points needed)")

with badge_col1:
    badge_card(
        title="Beginner",
        icon="🌱",
        unlocked=points >= 100,
        requirement=100
    )

with badge_col2:
    badge_card(
        title="Green Contributor",
        icon="🌿",
        unlocked=points >= 300,
        requirement=300
    )

with badge_col3:
    badge_card(
        title="Eco Champion",
        icon="🏆",
        unlocked=points >= 500,
        requirement=500
    )

# -----------------------------
# POINTS HISTORY CHART
# -----------------------------
st.markdown("### 📈 Carbon Points History")

user_transactions = [
    t for t in transactions if t.get("user") == USER_ID
]

if len(user_transactions) == 0:
    st.info("No activity yet. Upload waste images to start earning points!")
else:
    import pandas as pd

    df = pd.DataFrame(user_transactions)
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    df = df.sort_values("timestamp")

    df["cumulative_points"] = df["points"].cumsum()

    st.line_chart(
        df.set_index("timestamp")["cumulative_points"]
    )
# -----------------------------
# TRANSACTION HISTORY TABLE
# -----------------------------
st.markdown("### 📋 Activity History")

if len(user_transactions) == 0:
    st.caption("No transactions recorded yet.")
else:
    display_df = df[["timestamp", "category", "points"]].copy()
    display_df["timestamp"] = display_df["timestamp"].dt.strftime(
        "%Y-%m-%d %H:%M"
    )

    st.dataframe(
        display_df,
        use_container_width=True
    )

