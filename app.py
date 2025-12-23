import streamlit as st
import json
import os
os.makedirs("data", exist_ok=True)
# ===============================
# GLOBAL SESSION STATE INIT
# ===============================
DEFAULT_SESSION_STATE = {
    "logged_in": False,
    "role": None,
    "user": None,
    "DEMO_MODE": True,
    "dark_mode": False,
}

for key, value in DEFAULT_SESSION_STATE.items():
    if key not in st.session_state:
        st.session_state[key] = value


# ===============================
# GLOBAL SESSION STATE INIT
# ===============================
if "DEMO_MODE" not in st.session_state:
    st.session_state.DEMO_MODE = True   # default ON (safe for demo)

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "role" not in st.session_state:
    st.session_state.role = None

if "user" not in st.session_state:
    st.session_state.user = "demo_user"

# ===============================
# PAGE CONFIG (MUST BE FIRST)
# ===============================
st.set_page_config(
    page_title="EcoVerse AI",
    page_icon="🌱",
    layout="wide"
)

# ===============================
# SESSION STATE INITIALIZATION
# ===============================
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "role" not in st.session_state:
    st.session_state.role = None

if "user" not in st.session_state:
    st.session_state.user = None

if "DEMO_MODE" not in st.session_state:
    st.session_state.DEMO_MODE = True

if "dark_mode" not in st.session_state:
    st.session_state.dark_mode = False


# ===============================
# APP HEADER
# ===============================
st.title("🌍 EcoVerse AI")

# ===============================
# SIDEBAR — APPEARANCE
# ===============================
st.sidebar.markdown("---")
st.sidebar.subheader("🌗 Appearance")

st.sidebar.toggle(
    "Dark Mode (Mobile Friendly)",
    key="dark_mode"
)

# ===============================
# THEME CSS (SAFE)
# ===============================
if st.session_state.dark_mode:
    st.markdown("""
    <style>
    .stApp { background: linear-gradient(180deg,#0f172a,#020617); color:#e5e7eb; }
    h1,h2,h3 { color:#a7f3d0; }
    section[data-testid="stSidebar"] { background:#020617; }
    [data-testid="stMetric"] { background:#020617; color:#e5e7eb; border-radius:12px; }
    button[kind="primary"] { background:#22c55e; color:black; }
    </style>
    """, unsafe_allow_html=True)
else:
    st.markdown("""
    <style>
    .stApp { background: linear-gradient(180deg,#f5fff7,#ffffff); color:#14532d; }
    h1,h2,h3 { color:#14532d; }
    section[data-testid="stSidebar"] { background:#f0fdf4; }
    [data-testid="stMetric"] { background:#ecfdf5; border-radius:12px; }
    button[kind="primary"] { background:#16a34a; color:white; }
    </style>
    """, unsafe_allow_html=True)

# ===============================
# MOBILE + FLOATING BAR CSS
# ===============================
st.markdown("""
<style>
@media (max-width:768px){
  .block-container{padding-bottom:90px;}
  h1{font-size:1.6rem;}
  h2{font-size:1.3rem;}
  button{width:100%;padding:14px;border-radius:12px;}
}
.mobile-action-bar{
  position:fixed;bottom:0;left:0;right:0;
  background:#ffffff;
  border-top:1px solid #ddd;
  display:flex;
  justify-content:space-around;
  padding:10px;
  z-index:9999;
}
.mobile-action-bar a{
  text-decoration:none;
  font-weight:600;
  color:#14532d;
}
@media(min-width:769px){
  .mobile-action-bar{display:none;}
}
</style>
""", unsafe_allow_html=True)

# ===============================
# FLOATING MOBILE BAR (HTML)
# ===============================
st.markdown("""
<div class="mobile-action-bar">
  <a href="#">🏠 Home</a>
  <a href="#">➕ Add</a>
  <a href="#">🎁 Rewards</a>
</div>
""", unsafe_allow_html=True)

# ===============================
# HIDE ADMIN PAGE (NON-ADMIN)
# ===============================
if st.session_state.role != "admin":
    st.markdown("""
    <style>
    [data-testid="stSidebarNav"] li:has(a[href*="Admin"]) {
        display:none;
    }
    </style>
    """, unsafe_allow_html=True)

# ===============================
# SIDEBAR — DEMO MODE
# ===============================
st.sidebar.markdown("## ⚙️ App Mode")

st.sidebar.toggle(
    "Demo Mode (Safe for presentation)",
    key="DEMO_MODE"
)

if st.session_state.DEMO_MODE:
    st.sidebar.success("🟢 Demo Mode Enabled")
else:
    st.sidebar.warning("🔴 Live Mode Enabled")

# ===============================
# DEMO RESET
# ===============================
if st.session_state.DEMO_MODE:
    st.sidebar.markdown("---")
    st.sidebar.subheader("🧪 Demo Controls")

    if st.sidebar.button("🔄 Reset Demo Data"):
        os.makedirs("data", exist_ok=True)

        with open("data/users.json","w") as f:
            json.dump({"demo_user":{"name":"Demo User","points":0}},f,indent=2)

        with open("data/transactions.json","w") as f:
            json.dump([],f,indent=2)

        st.sidebar.success("✅ Demo data reset")
        st.rerun()

# ===============================
# LOGIN SYSTEM
# ===============================
st.sidebar.markdown("---")
st.sidebar.subheader("🔐 Login")

if not st.session_state.logged_in:

    role = st.sidebar.selectbox("Login as",["User","Admin"])
    username = st.sidebar.text_input("Username")

    admin_password = ""
    if role == "Admin":
        admin_password = st.sidebar.text_input("Admin Password",type="password")

    if st.sidebar.button("Login"):
        if role == "Admin":
            if admin_password == "admin123":
                st.session_state.logged_in = True
                st.session_state.role = "admin"
                st.session_state.user = username or "Admin"
                st.rerun()
            else:
                st.sidebar.error("❌ Wrong admin password")
        else:
            if username:
                st.session_state.logged_in = True
                st.session_state.role = "user"
                st.session_state.user = username
                st.rerun()
            else:
                st.sidebar.warning("Enter username")

else:
    st.sidebar.success(
        f"Logged in as **{st.session_state.user}** ({st.session_state.role})"
    )
    if st.sidebar.button("Logout"):
        st.session_state.logged_in = False
        st.session_state.role = None
        st.session_state.user = None
        st.rerun()

# ===============================
# MAIN CONTENT
# ===============================
st.subheader("AI-powered Sustainability Intelligence Platform")

st.write("""
EcoVerse AI helps students and campuses measure, understand, and improve
their environmental impact using AI-assisted analysis and a virtual
carbon-points economy.
""")

st.markdown("---")

st.write("""
### How to use this app
- Navigate using the **sidebar**
- Track carbon footprint
- Earn sustainability points
- Admins can approve & analyze data
""")

st.info("This is an educational MVP built using Streamlit and AI APIs.")

