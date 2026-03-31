"""Plotly chart builder functions for the dashboard."""

import json

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


THEME_COLORS = px.colors.qualitative.Set2


def explode_json_column(df: pd.DataFrame, column: str) -> pd.Series:
    """Explode a JSON-encoded list column into value counts."""
    all_values = []
    for val in df[column].dropna():
        try:
            items = json.loads(val)
            if isinstance(items, list):
                all_values.extend(items)
        except (json.JSONDecodeError, TypeError):
            if val:
                all_values.append(val)
    return pd.Series(all_values).value_counts()


def pie_chart(df: pd.DataFrame, column: str, title: str) -> go.Figure:
    """Create a pie chart for a single-choice column."""
    counts = df[column].dropna().value_counts()
    fig = px.pie(
        names=counts.index,
        values=counts.values,
        title=title,
        color_discrete_sequence=THEME_COLORS,
    )
    fig.update_traces(textposition="inside", textinfo="percent+label")
    fig.update_layout(showlegend=False, margin=dict(t=40, b=20, l=20, r=20))
    return fig


def bar_chart(df: pd.DataFrame, column: str, title: str, horizontal: bool = True) -> go.Figure:
    """Create a bar chart for a single-choice column."""
    counts = df[column].dropna().value_counts()
    if horizontal:
        fig = px.bar(
            x=counts.values,
            y=counts.index,
            orientation="h",
            title=title,
            color_discrete_sequence=THEME_COLORS,
        )
        fig.update_layout(yaxis_title="", xaxis_title="Count")
    else:
        fig = px.bar(
            x=counts.index,
            y=counts.values,
            title=title,
            color_discrete_sequence=THEME_COLORS,
        )
        fig.update_layout(xaxis_title="", yaxis_title="Count")
    fig.update_layout(margin=dict(t=40, b=20, l=20, r=20))
    return fig


def multi_select_bar(df: pd.DataFrame, column: str, title: str) -> go.Figure:
    """Create a horizontal bar chart for a multi-select (JSON list) column."""
    counts = explode_json_column(df, column)
    if counts.empty:
        return _empty_fig(title)
    fig = px.bar(
        x=counts.values,
        y=counts.index,
        orientation="h",
        title=title,
        color_discrete_sequence=THEME_COLORS,
    )
    fig.update_layout(
        yaxis_title="",
        xaxis_title="Number of Responses",
        margin=dict(t=40, b=20, l=20, r=20),
    )
    return fig


def frequency_heatmap(df: pd.DataFrame) -> go.Figure:
    """Create a heatmap showing frequency of AI usage across different tasks."""
    freq_columns = {
        "freq_lesson_plans": "Lesson Plans",
        "freq_assessments": "Assessments",
        "freq_personalized": "Personalized Materials",
        "freq_content": "Classroom Content",
        "freq_admin": "Administrative Tasks",
        "freq_engagement": "Engagement Activities",
        "freq_grading": "Grading & Feedback",
        "freq_parent_comm": "Parent Communication",
    }
    freq_order = ["Never", "Rarely (once a month)", "Sometimes (weekly)", "Often (multiple times a week)", "Daily"]

    heatmap_data = []
    for col_key, label in freq_columns.items():
        if col_key in df.columns:
            counts = df[col_key].value_counts()
            row = [counts.get(freq, 0) for freq in freq_order]
            heatmap_data.append(row)

    if not heatmap_data:
        return _empty_fig("AI Usage Frequency")

    fig = go.Figure(
        data=go.Heatmap(
            z=heatmap_data,
            x=["Never", "Rarely", "Sometimes", "Often", "Daily"],
            y=list(freq_columns.values()),
            colorscale="Blues",
            text=heatmap_data,
            texttemplate="%{text}",
            hovertemplate="Task: %{y}<br>Frequency: %{x}<br>Count: %{z}<extra></extra>",
        )
    )
    fig.update_layout(
        title="AI Usage Frequency Across Teaching Tasks",
        margin=dict(t=40, b=20, l=20, r=20),
    )
    return fig


def likert_stacked_bar(df: pd.DataFrame) -> go.Figure:
    """Create a stacked horizontal bar chart for Likert-scale impact questions."""
    impact_columns = {
        "impact_learning": "Improved Learning Outcomes",
        "impact_engagement": "Increased Engagement",
        "impact_individual": "Addressed Individual Weaknesses",
        "impact_performance": "Improved Exam Performance",
        "impact_creativity": "Encouraged Creativity",
    }
    likert_order = ["Strongly Disagree", "Disagree", "Neutral", "Agree", "Strongly Agree"]
    colors = ["#d32f2f", "#ff9800", "#9e9e9e", "#4caf50", "#1b5e20"]

    fig = go.Figure()

    for i, likert_val in enumerate(likert_order):
        counts = []
        for col_key in impact_columns:
            if col_key in df.columns:
                counts.append((df[col_key] == likert_val).sum())
            else:
                counts.append(0)
        fig.add_trace(
            go.Bar(
                y=list(impact_columns.values()),
                x=counts,
                name=likert_val,
                orientation="h",
                marker_color=colors[i],
            )
        )

    fig.update_layout(
        barmode="stack",
        title="Student Impact — Teacher Agreement Levels",
        xaxis_title="Number of Responses",
        yaxis_title="",
        legend_title="Agreement",
        margin=dict(t=40, b=20, l=20, r=20),
    )
    return fig


def impact_radar(df: pd.DataFrame) -> go.Figure:
    """Create a radar chart showing average impact scores."""
    impact_columns = {
        "impact_learning": "Learning\nOutcomes",
        "impact_engagement": "Student\nEngagement",
        "impact_individual": "Individual\nAttention",
        "impact_performance": "Exam\nPerformance",
        "impact_creativity": "Creativity &\nCritical Thinking",
    }
    likert_map = {
        "Strongly Disagree": 1,
        "Disagree": 2,
        "Neutral": 3,
        "Agree": 4,
        "Strongly Agree": 5,
    }

    averages = []
    labels = []
    for col_key, label in impact_columns.items():
        if col_key in df.columns:
            numeric = df[col_key].map(likert_map).dropna()
            avg = numeric.mean() if len(numeric) > 0 else 0
            averages.append(round(avg, 2))
            labels.append(label)

    if not averages:
        return _empty_fig("Impact Radar")

    # Close the radar
    averages.append(averages[0])
    labels.append(labels[0])

    fig = go.Figure(
        data=go.Scatterpolar(
            r=averages,
            theta=labels,
            fill="toself",
            line_color="#1E88E5",
        )
    )
    fig.update_layout(
        polar=dict(radialaxis=dict(visible=True, range=[0, 5])),
        title="Average Student Impact Scores (1-5)",
        margin=dict(t=60, b=20, l=60, r=60),
    )
    return fig


def _empty_fig(title: str) -> go.Figure:
    """Return an empty figure with a message."""
    fig = go.Figure()
    fig.update_layout(
        title=title,
        annotations=[
            dict(
                text="No data available yet",
                xref="paper",
                yref="paper",
                showarrow=False,
                font=dict(size=16),
            )
        ],
    )
    return fig
