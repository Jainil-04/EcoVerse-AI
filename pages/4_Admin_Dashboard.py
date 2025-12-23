import streamlit as st
import json
import os

USERS_FILE = "data/users.json"
TRANSACTIONS_FILE = "data/transactions.json"
REWARDS_FILE = "data/rewards.json"

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
transactions = load_json(TRANSACTIONS_FILE, [])
rewards = load_json(REWARDS_FILE, [])

# -----------------------------
# UI
# -----------------------------
st.title("🔒 Admin Dashboard")

st.markdown("---")

# =============================
# SECTION 1: Campus Metrics
# =============================
st.header("📊 Campus Sustainability Metrics")

total_points = sum(user["points"] for user in users.values())
total_users = len(users)
total_transactions = len(transactions)

st.metric("Total Users", total_users)
st.metric("Total Carbon Points Issued", total_points)
st.metric("Total Transactions Logged", total_transactions)

st.markdown("---")

# =============================
# SECTION 2: Leaderboard
# =============================
st.header("🏆 Leaderboard")

sorted_users = sorted(
    users.items(),
    key=lambda x: x[1]["points"],
    reverse=True
)

for rank, (user_id, user_data) in enumerate(sorted_users, start=1):
    st.write(f"{rank}. **{user_data['name']}** — {user_data['points']} points")

st.markdown("---")

# =============================
# SECTION 3: Pending Reward Approvals
# =============================
st.header("⏳ Pending Reward Approvals")

pending = [
    t for t in transactions
    if t.get("status") == "pending"
]

if not pending:
    st.success("No pending approvals.")
else:
    for idx, txn in enumerate(pending):
        with st.container():
            st.write(f"User: {txn['user']}")
            st.write(f"Reward: {txn['reward']}")
            st.write(f"Points Spent: {txn['points_spent']}")
            st.write(f"Timestamp: {txn['timestamp']}")

            if st.button("Approve", key=f"approve_{idx}"):
                txn["status"] = "approved"
                save_json(TRANSACTIONS_FILE, transactions)
                st.success("Reward approved successfully.")
                st.experimental_rerun()

            st.markdown("---")

# =============================
# SECTION 4: Audit Log
# =============================
st.header("📜 Full Transaction Audit Log")

for txn in transactions[::-1]:
    st.write(txn)

