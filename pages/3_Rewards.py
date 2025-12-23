import streamlit as st
import json
import os
from datetime import datetime
os.makedirs("data", exist_ok=True)

# ===============================
# 🔐 ACCESS CONTROL
# ===============================
if not st.session_state.get("logged_in"):
    st.warning("Please login to continue.")
    st.stop()

USER_ID = st.session_state.get("user", "demo_user")

# ===============================
# 📂 FILE PATHS
# ===============================
USERS_FILE = "data/users.json"
REWARDS_FILE = "data/rewards.json"
TRANSACTIONS_FILE = "data/transactions.json"

os.makedirs("data", exist_ok=True)

# ===============================
# 🧰 HELPERS
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

# ===============================
# 📥 LOAD DATA
# ===============================
users = load_json(USERS_FILE, {})
rewards = load_json(REWARDS_FILE, [])
transactions = load_json(TRANSACTIONS_FILE, [])

users.setdefault(USER_ID, {"name": USER_ID, "points": 0})
user_points = users[USER_ID]["points"]

# ===============================
# 🏆 PAGE HEADER
# ===============================
st.title("🎁 Rewards & Redemption")
st.write(f"### 🌱 Your Current EcoPoints: **{user_points}**")

st.markdown("---")

# ==============================
# 🏅 PART 1 — Animated Badges
# ==============================
st.markdown("""
<style>
.badge {
    display: inline-block;
    padding: 16px 20px;
    margin: 10px 12px 10px 0;
    border-radius: 14px;
    background: linear-gradient(135deg, #22c55e, #16a34a);
    color: white;
    font-weight: 600;
    font-size: 16px;
    box-shadow: 0 8px 20px rgba(34,197,94,0.3);
    animation: pop 0.6s ease-out;
}
.locked {
    background: #e5e7eb;
    color: #6b7280;
    box-shadow: none;
}
@keyframes pop {
    0% { transform: scale(0.8); opacity: 0; }
    100% { transform: scale(1); opacity: 1; }
}
</style>
""", unsafe_allow_html=True)

st.subheader("🏅 Your Badges")

BADGES = [
    ("🌱 Green Starter", 100),
    ("🌿 Eco Warrior", 300),
    ("🌳 Sustainability Champion", 500),
]

for name, threshold in BADGES:
    if user_points >= threshold:
        st.markdown(f'<div class="badge">✅ {name}</div>', unsafe_allow_html=True)
    else:
        st.markdown(
            f'<div class="badge locked">🔒 {name} — {threshold} pts</div>',
            unsafe_allow_html=True
        )

st.markdown("---")

# ===============================
# 🎁 PART 2 — Rewards Catalog
# ===============================
st.subheader("🛍️ Available Rewards")

if not rewards:
    st.info("No rewards available yet.")
else:
    for reward in rewards:
        with st.container(border=True):
            col1, col2 = st.columns([3, 1])

            with col1:
                st.markdown(f"### 🎁 {reward['name']}")
                st.write(f"**Type:** {reward.get('type', 'General')}")
                st.write(f"**Points Required:** {reward['points_required']}")

                if reward.get("description"):
                    st.caption(reward["description"])

                if reward.get("approved"):
                    st.success("✅ Auto-approved reward")
                else:
                    st.warning("⏳ Requires admin approval")

            with col2:
                if user_points >= reward["points_required"]:
                    if st.button(
                        "Redeem",
                        key=f"redeem_{reward['id']}",
                        use_container_width=True
                    ):
                        # Deduct points
                        users[USER_ID]["points"] -= reward["points_required"]

                        # Log transaction
                        transactions.append({
                            "user": USER_ID,
                            "reward": reward["name"],
                            "points_spent": reward["points_required"],
                            "timestamp": datetime.now().isoformat(),
                            "status": "approved" if reward.get("approved") else "pending"
                        })

                        save_json(USERS_FILE, users)
                        save_json(TRANSACTIONS_FILE, transactions)

                        if reward.get("approved"):
                            st.success("🎉 Reward redeemed successfully!")
                        else:
                            st.info("🛂 Redemption pending admin approval")

                        st.rerun()
                else:
                    st.button(
                        "Not enough points",
                        disabled=True,
                        key=f"disabled_{reward['id']}",
                        use_container_width=True
                    )

st.markdown("---")

# ===============================
# 📜 PART 3 — Redemption History
# ===============================
st.subheader("📜 Redemption History")

history = [
    t for t in transactions
    if t.get("user") == USER_ID
]

if history:
    for h in reversed(history):
        st.info(
            f"🎁 {h['reward']} | "
            f"-{h['points_spent']} pts | "
            f"{h['status']} | "
            f"{h['timestamp'][:19]}"
        )
else:
    st.info("No redemptions yet.")

st.markdown("---")
st.caption("EcoPoints are earned via Carbon Tracker and sustainability actions.")

