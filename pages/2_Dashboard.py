"""Analytics dashboard for AI in Education survey responses."""

import streamlit as st
from db.database import init_db, get_all_responses, get_response_count
from utils.charts import (
    pie_chart,
    bar_chart,
    multi_select_bar,
    frequency_heatmap,
    likert_stacked_bar,
    impact_radar,
)
from utils.export import create_excel_download

init_db()

st.set_page_config(page_title="Survey Dashboard", page_icon="📊", layout="wide")

st.title("📊 Survey Dashboard")

# Refresh button
if st.button("🔄 Refresh Data"):
    st.rerun()

# Load data
df = get_all_responses()
total = len(df)

if total == 0:
    st.warning("No responses yet. Share the survey to start collecting data!")
    st.page_link("pages/1_Survey.py", label="Take the Survey", icon="📝")
    st.stop()

# --- KPI Cards ---
col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Total Responses", total)

with col2:
    if "school_board" in df.columns:
        top_board = df["school_board"].mode().iloc[0] if not df["school_board"].isna().all() else "N/A"
        board_pct = (df["school_board"] == top_board).sum() / total * 100
        st.metric("Most Common Board", f"{top_board}", f"{board_pct:.0f}%")

with col3:
    if "ai_usage_duration" in df.columns:
        duration_mode = df["ai_usage_duration"].mode().iloc[0] if not df["ai_usage_duration"].isna().all() else "N/A"
        st.metric("Most Common AI Duration", duration_mode)

st.divider()

# --- Tabs ---
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "👤 Demographics",
    "🤖 AI Usage",
    "📈 Student Impact",
    "🚧 Barriers & Future",
    "📋 Raw Data & Export",
])

# --- Tab 1: Demographics ---
with tab1:
    col1, col2 = st.columns(2)
    with col1:
        if "school_board" in df.columns:
            st.plotly_chart(pie_chart(df, "school_board", "School Board Distribution"), use_container_width=True)
    with col2:
        if "city_tier" in df.columns:
            st.plotly_chart(pie_chart(df, "city_tier", "City Tier Distribution"), use_container_width=True)

    col1, col2 = st.columns(2)
    with col1:
        if "subjects_taught" in df.columns:
            st.plotly_chart(multi_select_bar(df, "subjects_taught", "Subjects Taught"), use_container_width=True)
    with col2:
        if "grade_levels" in df.columns:
            st.plotly_chart(multi_select_bar(df, "grade_levels", "Grade Levels Taught"), use_container_width=True)

    col1, col2 = st.columns(2)
    with col1:
        if "experience_years" in df.columns:
            st.plotly_chart(bar_chart(df, "experience_years", "Teaching Experience", horizontal=False), use_container_width=True)

# --- Tab 2: AI Usage ---
with tab2:
    col1, col2 = st.columns(2)
    with col1:
        if "ai_tools_used" in df.columns:
            st.plotly_chart(multi_select_bar(df, "ai_tools_used", "AI Tools Used (Ranked)"), use_container_width=True)
    with col2:
        if "discovery_channel" in df.columns:
            st.plotly_chart(pie_chart(df, "discovery_channel", "How Teachers Discovered AI"), use_container_width=True)

    col1, col2 = st.columns(2)
    with col1:
        if "ai_usage_duration" in df.columns:
            st.plotly_chart(bar_chart(df, "ai_usage_duration", "Duration of AI Usage", horizontal=False), use_container_width=True)
    with col2:
        if "innovative_uses" in df.columns:
            st.plotly_chart(multi_select_bar(df, "innovative_uses", "Innovative / Creative Uses"), use_container_width=True)

    st.plotly_chart(frequency_heatmap(df), use_container_width=True)

# --- Tab 3: Student Impact ---
with tab3:
    st.plotly_chart(likert_stacked_bar(df), use_container_width=True)

    col1, col2 = st.columns([1, 1])
    with col1:
        st.plotly_chart(impact_radar(df), use_container_width=True)
    with col2:
        st.markdown("### How to Read the Impact Scores")
        st.markdown(
            """
            - **1** = Strongly Disagree
            - **2** = Disagree
            - **3** = Neutral
            - **4** = Agree
            - **5** = Strongly Agree

            The radar chart shows the **average score** across all respondents
            for each impact dimension. A score above 3.5 suggests teachers
            generally perceive a positive impact.
            """
        )

# --- Tab 4: Barriers & Future ---
with tab4:
    col1, col2 = st.columns(2)
    with col1:
        if "barriers" in df.columns:
            st.plotly_chart(multi_select_bar(df, "barriers", "Biggest Challenges"), use_container_width=True)
    with col2:
        if "support_needed" in df.columns:
            st.plotly_chart(multi_select_bar(df, "support_needed", "Support Needed"), use_container_width=True)

    col1, col2 = st.columns(2)
    with col1:
        if "future_likelihood" in df.columns:
            st.plotly_chart(pie_chart(df, "future_likelihood", "Likelihood to Increase AI Use"), use_container_width=True)
    with col2:
        if "future_priority" in df.columns:
            st.plotly_chart(bar_chart(df, "future_priority", "Future Priority Areas", horizontal=True), use_container_width=True)

# --- Tab 5: Raw Data & Export ---
with tab5:
    st.markdown("### All Survey Responses")
    st.dataframe(df, use_container_width=True, hide_index=True)

    st.divider()

    excel_data = create_excel_download(df)
    st.download_button(
        label="📥 Download as Excel",
        data=excel_data,
        file_name="ai_education_survey_responses.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )

    # Show open-text innovative descriptions if any
    if "innovative_desc" in df.columns:
        descriptions = df["innovative_desc"].dropna()
        descriptions = descriptions[descriptions.str.strip() != ""]
        if len(descriptions) > 0:
            st.divider()
            st.markdown("### Innovative Use Descriptions (Open Text)")
            for i, desc in enumerate(descriptions, 1):
                st.markdown(f"**{i}.** {desc}")
