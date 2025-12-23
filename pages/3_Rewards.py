import streamlit as st
import json
import os
from datetime import datetime

USER_ID = "demo_user"

USERS_FILE = "data/users.json"
REWARDS_FILE = "data/rewards.json"
TRANSACTIONS_FILE = "data/transactions.json"

# -----------------------------
# Helper functions
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
# Load data
# -----------------------------
users = load_json(USERS_FILE, {})
rewards = load_json(REWARDS_FILE, [])
transactions = load_json(TRANSACTIONS_FILE, [])

user_points = users.get(USER_ID, {}).get("points", 0)

# -----------------------------
# UI
# -----------------------------
st.title("🎁 Rewards & Redemption")

st.write(f"### Your Current Points: **{user_points}**")

st.markdown("---")

# -----------------------------
# Rewards Catalog
# -----------------------------
st.subheader("Available Rewards")

for reward in rewards:
    with st.container():
        st.write(f"**{reward['name']}**")
        st.write(f"Points Required: {reward['points_required']}")
        st.write(f"Type: {reward['type']}")

        if user_points >= reward["points_required"]:
            if st.button(f"Redeem {reward['name']}", key=reward["id"]):
                # Deduct points
                users[USER_ID]["points"] -= reward["points_required"]

                # Log transaction
                transactions.append({
                    "user": USER_ID,
                    "reward": reward["name"],
                    "points_spent": reward["points_required"],
                    "timestamp": datetime.now().isoformat(),
                    "status": "approved" if reward["approved"] else "pending"
                })

                save_json(USERS_FILE, users)
                save_json(TRANSACTIONS_FILE, transactions)

                if reward["approved"]:
                    st.success("Reward redeemed successfully!")
                else:
                    st.warning("Reward redemption pending admin approval.")

                st.experimental_rerun()
        else:
            st.info("Not enough points to redeem this reward.")

        st.markdown("---")

