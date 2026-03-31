"""Chatbot-style survey page for AI in Education survey."""

import streamlit as st
from config.questions import SECTIONS
from db.database import init_db, save_response

init_db()

st.set_page_config(page_title="Take the Survey", page_icon="📝", layout="centered")

# Initialize session state
if "current_section" not in st.session_state:
    st.session_state.current_section = 0
if "answers" not in st.session_state:
    st.session_state.answers = {}
if "submitted" not in st.session_state:
    st.session_state.submitted = False

TOTAL_SECTIONS = len(SECTIONS)


def go_next():
    st.session_state.current_section += 1


def go_prev():
    st.session_state.current_section -= 1


def reset_survey():
    st.session_state.current_section = 0
    st.session_state.answers = {}
    st.session_state.submitted = False


# --- Submitted State ---
if st.session_state.submitted:
    st.balloons()
    st.success("Thank you for completing the survey! Your response has been recorded.")
    st.markdown(
        "Your insights will help us understand how AI is being used in Indian schools "
        "and what support teachers need."
    )
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Submit Another Response"):
            reset_survey()
            st.rerun()
    with col2:
        st.page_link("pages/2_Dashboard.py", label="View Dashboard", icon="📊")
    st.stop()

# --- Survey Header ---
st.title("📝 AI in Education Survey")

# Progress bar
progress = st.session_state.current_section / TOTAL_SECTIONS
st.progress(progress, text=f"Section {st.session_state.current_section + 1} of {TOTAL_SECTIONS}")

# --- Show Previous Answers as Chat History ---
for i in range(st.session_state.current_section):
    section = SECTIONS[i]
    with st.chat_message("assistant"):
        st.markdown(f"**Section {section['id']}: {section['title']}** ✅")
    with st.chat_message("user"):
        for q in section["questions"]:
            key = q["key"]
            if key in st.session_state.answers:
                val = st.session_state.answers[key]
                if isinstance(val, list):
                    val = ", ".join(val) if val else "None selected"
                if val:
                    st.markdown(f"**{q['question']}**\n\n{val}")

# --- Current Section ---
idx = st.session_state.current_section
section = SECTIONS[idx]

with st.chat_message("assistant"):
    st.markdown(f"### Section {section['id']}: {section['title']}")
    st.markdown(section["description"])

with st.chat_message("user"):
    with st.form(key=f"section_{section['id']}_form"):
        form_values = {}

        for q in section["questions"]:
            key = q["key"]
            qtype = q["type"]
            st.markdown(f"**{q['question']}**")

            if qtype == "single_choice":
                default_idx = 0
                if key in st.session_state.answers:
                    try:
                        default_idx = q["options"].index(st.session_state.answers[key])
                    except ValueError:
                        default_idx = 0
                form_values[key] = st.radio(
                    q["question"],
                    options=q["options"],
                    index=default_idx,
                    key=f"radio_{key}",
                    label_visibility="collapsed",
                )

            elif qtype == "multi_choice":
                default = st.session_state.answers.get(key, [])
                form_values[key] = st.multiselect(
                    q["question"],
                    options=q["options"],
                    default=default,
                    key=f"multi_{key}",
                    label_visibility="collapsed",
                )

            elif qtype in ("frequency", "likert"):
                default_idx = 0
                if key in st.session_state.answers:
                    try:
                        default_idx = q["options"].index(st.session_state.answers[key])
                    except ValueError:
                        default_idx = 0
                form_values[key] = st.select_slider(
                    q["question"],
                    options=q["options"],
                    value=q["options"][default_idx],
                    key=f"slider_{key}",
                    label_visibility="collapsed",
                )

            elif qtype == "text":
                default = st.session_state.answers.get(key, "")
                form_values[key] = st.text_area(
                    q["question"],
                    value=default,
                    key=f"text_{key}",
                    label_visibility="collapsed",
                    height=100,
                )

            st.divider()

        # Navigation buttons
        col1, col2, col3 = st.columns([1, 1, 1])

        with col1:
            if idx > 0:
                go_back = st.form_submit_button("⬅ Previous")
            else:
                go_back = False

        with col3:
            if idx < TOTAL_SECTIONS - 1:
                go_forward = st.form_submit_button("Next ➡", type="primary")
                submit = False
            else:
                go_forward = False
                submit = st.form_submit_button("✅ Submit Survey", type="primary")

        # Handle navigation
        if go_back:
            # Save current answers before going back
            for key, val in form_values.items():
                st.session_state.answers[key] = val
            go_prev()
            st.rerun()

        if go_forward:
            # Validate required multi-choice fields
            valid = True
            for q in section["questions"]:
                if q.get("required", False) and q["type"] == "multi_choice":
                    if not form_values.get(q["key"]):
                        st.error(f"Please select at least one option for: {q['question']}")
                        valid = False
            if valid:
                for key, val in form_values.items():
                    st.session_state.answers[key] = val
                go_next()
                st.rerun()

        if submit:
            # Validate required multi-choice fields in last section
            valid = True
            for q in section["questions"]:
                if q.get("required", False) and q["type"] == "multi_choice":
                    if not form_values.get(q["key"]):
                        st.error(f"Please select at least one option for: {q['question']}")
                        valid = False
            if valid:
                for key, val in form_values.items():
                    st.session_state.answers[key] = val
                # Save to database
                save_response(st.session_state.answers)
                st.session_state.submitted = True
                st.rerun()
