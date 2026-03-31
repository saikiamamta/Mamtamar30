"""AI in Education Survey - Landing Page."""

import streamlit as st
from db.database import init_db, get_response_count

# Initialize database on startup
init_db()

st.set_page_config(
    page_title="AI in Education Survey",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.title("AI in Education Survey")
st.subheader("Understanding How Private School Teachers in India Use AI")

st.markdown(
    """
    Welcome! This survey is designed to understand how private school teachers
    across India are using Artificial Intelligence in their teaching practice.

    **Why this survey?**
    - Most teachers use AI primarily for lesson plans and assessments
    - Some are innovating with creative and unconventional uses
    - We want to capture the full picture and measure the impact on students

    **What you'll be asked about:**
    1. Your background and school details
    2. Which AI tools you use
    3. How often you use AI for different teaching tasks
    4. Any creative or innovative uses you've discovered
    5. The impact you've observed on your students
    6. Challenges you face and support you need
    7. Your future plans with AI

    **The survey takes about 5-7 minutes to complete.**

    ---
    """
)

# Show response count
count = get_response_count()
if count > 0:
    st.info(f"**{count}** teachers have already shared their experiences!")

col1, col2 = st.columns(2)
with col1:
    st.page_link("pages/1_Survey.py", label="Take the Survey", icon="📝")
with col2:
    st.page_link("pages/2_Dashboard.py", label="View Dashboard", icon="📊")
