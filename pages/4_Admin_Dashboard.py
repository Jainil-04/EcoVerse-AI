import streamlit as st
import json
import os
import pandas as pd
os.makedirs("data", exist_ok=True)

# ==============================
# STEP 6.3 — Admin-only access
# ==============================

if not st.session_state.get("logged_in"):
    st.error("🔒 Please login to access the Admin Dashboard.")
    st.stop()

if st.session_state.get("role") != "admin":
    st.error("🚫 Access denied. Admins only.")
    st.stop()



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
# =========================
# Chart 1: Points by User
# =========================
st.subheader("📊 Carbon Points Distribution")

if users:
    points_df = pd.DataFrame([
        {"User": user_data["name"], "Points": user_data["points"]}
        for user_data in users.values()
    ])

    st.bar_chart(points_df.set_index("User"))
else:
    st.info("No user data available for chart.")

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
# =========================
# Chart 2: Transactions Over Time
# =========================
st.subheader("🕒 Transactions Over Time")

if transactions:
    txn_df = pd.DataFrame(transactions)

    txn_df["timestamp"] = pd.to_datetime(txn_df["timestamp"])
    txn_df["date"] = txn_df["timestamp"].dt.date

    daily_txns = txn_df.groupby("date").size()

    st.line_chart(daily_txns)
else:
    st.info("No transactions available.")

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
        st.markdown("### 🎁 Reward Request")
        st.write(f"👤 User: **{txn['user']}**")
        st.write(f"🏆 Reward: **{txn['reward']}**")
        st.write(f"💰 Points Spent: **{txn['points_spent']}**")
        st.write(f"🕒 Time: {txn['timestamp']}")

        col1, col2 = st.columns(2)

        # ---------- APPROVE ----------
        with col1:
            if st.button("✅ Approve", key=f"approve_{idx}"):
                txn["status"] = "approved"
                save_json(TRANSACTIONS_FILE, transactions)
                st.success("Reward approved successfully!")
                st.rerun()

        # ---------- REJECT ----------
        with col2:
            if st.button("❌ Reject", key=f"reject_{idx}"):
                txn["status"] = "rejected"

                # Refund points
                user_id = txn["user"]
                if user_id in users:
                    users[user_id]["points"] += txn["points_spent"]
                    save_json(USERS_FILE, users)

                save_json(TRANSACTIONS_FILE, transactions)
                st.warning("Reward rejected and points refunded.")
                st.rerun()

        st.markdown("---")

# =========================
# Chart 3: Reward Approval Status
# =========================
st.markdown("---")
st.subheader("🎁 Reward Approval Status")

if transactions:
    status_df = pd.DataFrame(transactions)

    if "status" in status_df.columns:
        status_counts = status_df["status"].value_counts()
        st.bar_chart(status_counts)
    else:
        st.info("No reward status data found.")
else:
    st.info("No reward transactions yet.")

# =============================
# SECTION 4: Audit Log
# =============================
st.header("📜 Full Transaction Audit Log")

for txn in transactions[::-1]:
    st.write(txn)

