import streamlit as st

# Page configuration
st.set_page_config(
    page_title="EcoVerse AI",
    page_icon="🌱",
    layout="wide"
)

# App header
st.title("🌍 EcoVerse AI")
st.subheader("AI-powered Sustainability Intelligence Platform")

st.write("""
EcoVerse AI helps students and campuses measure, understand, and improve
their environmental impact using AI-assisted analysis and a virtual
carbon-points economy.
""")

st.markdown("---")

st.write("""
### How to use this app:
- Use the **sidebar** to navigate between pages
- Upload images for AI-based analysis
- Track your carbon footprint
- Earn and redeem sustainability points
""")

st.info("This is an MVP built using Streamlit and AI APIs for educational use.")

