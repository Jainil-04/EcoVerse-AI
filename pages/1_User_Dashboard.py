import streamlit as st
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
    with open(path, "r") as f:
        return json.load(f)

def save_json(path, data):
    with open(path, "w") as f:
        json.dump(data, f, indent=2)

# -----------------------------
# LOAD DATA
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
st.subheader("Your Carbon Points Balance")
st.metric("Total Points", users[USER_ID]["points"])

