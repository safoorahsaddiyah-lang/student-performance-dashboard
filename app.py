"""
Student Performance Analytics Dashboard
=======================================
A complete, interactive, and beginner-friendly Streamlit web application
for analyzing student academic performance, attendance, and study habits.

Built with Python, Streamlit, Pandas, and Plotly.
"""

import os
import io
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

# ==============================================================================
# 1. PAGE CONFIGURATION & THEME STYLING
# ==============================================================================
st.set_page_config(
    page_title="EduMetrics | Student Performance Analytics",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for modern typography, card styling, and polished metrics
CUSTOM_CSS = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');

    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif;
    }

    /* Top banner header styling */
    .dashboard-header {
        background: linear-gradient(135deg, #1e1b4b 0%, #312e81 50%, #4338ca 100%);
        border-radius: 16px;
        padding: 24px 32px;
        color: #ffffff;
        margin-bottom: 25px;
        box-shadow: 0 10px 25px -5px rgba(49, 46, 129, 0.2);
    }
    .dashboard-header h1 {
        color: #ffffff;
        font-weight: 800;
        font-size: 2rem;
        margin: 0;
        padding-bottom: 6px;
    }
    .dashboard-header p {
        color: #c7d2fe;
        font-size: 0.95rem;
        margin: 0;
    }

    /* Metric Card Styling */
    .metric-card {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 14px;
        padding: 18px 20px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    .metric-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.08);
    }
    .metric-label {
        font-size: 0.82rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        color: #64748b;
        margin-bottom: 6px;
    }
    .metric-value {
        font-size: 1.85rem;
        font-weight: 800;
        color: #0f172a;
        line-height: 1.1;
    }
    .metric-sub {
        font-size: 0.8rem;
        color: #64748b;
        margin-top: 6px;
    }

    /* Insight card badges */
    .insight-box {
        border-radius: 12px;
        padding: 16px 20px;
        margin-bottom: 12px;
        border-left: 5px solid;
    }
    .insight-success {
        background-color: #f0fdf4;
        border-color: #22c55e;
        color: #166534;
    }
    .insight-info {
        background-color: #eff6ff;
        border-color: #3b82f6;
        color: #1e40af;
    }
    .insight-warning {
        background-color: #fffbeb;
        border-color: #f59e0b;
        color: #92400e;
    }
    .insight-danger {
        background-color: #fef2f2;
        border-color: #ef4444;
        color: #991b1b;
    }

    /* Tab styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    .stTabs [data-baseweb="tab"] {
        border-radius: 8px;
        padding: 8px 18px;
        font-weight: 600;
    }

    /* Streamlit default metric fix */
    [data-testid="stMetric"] {
        background-color: #f8fafc;
        border: 1px solid #e2e8f0;
        padding: 14px 18px;
        border-radius: 12px;
    }
</style>
"""
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

# Standard Plotly layout template for consistent look
PLOTLY_TEMPLATE = "plotly_white"
CHART_COLORWAY = ["#4f46e5", "#06b6d4", "#10b981", "#f59e0b", "#ec4899", "#8b5cf6"]

# ==============================================================================
# 2. DATA VALIDATION & PREPROCESSING FUNCTIONS
# ==============================================================================
REQUIRED_NUMERIC_COLUMNS = [
    "Attendance_Rate", "Math_Score", "Science_Score", "English_Score", "History_Score"
]
CORE_SUBJECT_COLS = ["Math_Score", "Science_Score", "English_Score", "History_Score"]

def calculate_grade(score: float) -> str:
    """Assign letter grade based on a numerical percentage."""
    if score >= 90:
        return "A"
    elif score >= 80:
        return "B"
    elif score >= 70:
        return "C"
    elif score >= 60:
        return "D"
    else:
        return "F"

def validate_and_clean_data(raw_df: pd.DataFrame) -> tuple[pd.DataFrame | None, list[str], list[str]]:
    """
    Validates the structure and data types of an uploaded or sample DataFrame.
    Returns:
        (cleaned_df, error_messages, warning_messages)
    """
    errors = []
    warnings = []

    if raw_df is None or raw_df.empty:
        errors.append("The supplied file is empty. Please upload a valid CSV file with student records.")
        return None, errors, warnings

    df = raw_df.copy()

    # Clean up column names: strip whitespace and standardize case if necessary
    df.columns = [col.strip() for col in df.columns]

    # Verify minimum required columns
    missing_cols = [col for col in REQUIRED_NUMERIC_COLUMNS if col not in df.columns]
    if missing_cols:
        errors.append(
            f"Missing required numeric column(s): {', '.join(missing_cols)}. "
            f"The application needs these columns to compute marks and attendance."
        )
        return None, errors, warnings

    # Convert numeric columns safely
    for col in REQUIRED_NUMERIC_COLUMNS:
        df[col] = pd.to_numeric(df[col], errors="coerce")
        null_count = df[col].isnull().sum()
        if null_count > 0:
            median_val = df[col].median()
            df[col] = df[col].fillna(median_val)
            warnings.append(
                f"Column '{col}' contained {null_count} missing or invalid values. Replaced them with the column median ({median_val:.1f})."
            )

    # Optional columns with fallback defaults
    if "Student_ID" not in df.columns:
        df["Student_ID"] = [f"STU{1001 + i}" for i in range(len(df))]
        warnings.append("No 'Student_ID' column found; generated automatic IDs (e.g. STU1001).")

    if "Name" not in df.columns:
        df["Name"] = [f"Student {i+1}" for i in range(len(df))]
        warnings.append("No 'Name' column found; assigned default names.")

    if "Gender" not in df.columns:
        df["Gender"] = "Not Specified"

    if "Grade_Level" not in df.columns:
        df["Grade_Level"] = "Grade 10"

    if "Section" not in df.columns:
        df["Section"] = "Section A"

    if "Study_Hours_Per_Week" not in df.columns:
        # Approximate baseline from attendance if absent
        df["Study_Hours_Per_Week"] = (df["Attendance_Rate"] / 10).round(1)
        warnings.append("No 'Study_Hours_Per_Week' column found; estimated from attendance.")
    else:
        df["Study_Hours_Per_Week"] = pd.to_numeric(df["Study_Hours_Per_Week"], errors="coerce").fillna(10.0)

    # Calculate / verify Average_Score
    available_subjects = [col for col in CORE_SUBJECT_COLS if col in df.columns]
    df["Average_Score"] = df[available_subjects].mean(axis=1).round(1)

    # Calculate Grade
    df["Grade"] = df["Average_Score"].apply(calculate_grade)

    # Calculate Status
    df["Status"] = df["Average_Score"].apply(lambda s: "Pass" if s >= 60.0 else "Fail")

    # Round attendance
    df["Attendance_Rate"] = df["Attendance_Rate"].clip(lower=0, upper=100).round(1)

    return df, errors, warnings

@st.cache_data
def load_default_sample_data() -> pd.DataFrame:
    """Loads the pre-generated sample CSV file or generates one on the fly."""
    sample_file = "sample_students.csv"
    if os.path.exists(sample_file):
        return pd.read_csv(sample_file)
    else:
        # Fallback generator if file doesn't exist
        from generate_data import generate_sample_dataset
        generate_sample_dataset(sample_file, num_records=250)
        return pd.read_csv(sample_file)

# ==============================================================================
# 3. SIDEBAR CONTROLS & FILTERS
# ==============================================================================
def render_sidebar():
    """Renders the sidebar for data source selection and dynamic filtering."""
    st.sidebar.markdown(
        """
        <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 20px;">
            <div style="background-color: #4f46e5; border-radius: 10px; padding: 8px 12px; color: white; font-size: 24px;">🎓</div>
            <div>
                <h3 style="margin: 0; font-size: 1.15rem; font-weight: 700; color: #1e1b4b;">EduMetrics Studio</h3>
                <span style="font-size: 0.75rem; color: #64748b; font-weight: 500;">Student Analytics Platform</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.sidebar.markdown("### 📂 1. Data Source")
    data_source_mode = st.sidebar.radio(
        "Choose Data Source:",
        ["Built-in Sample (250 Students)", "Upload Custom CSV File"],
        label_visibility="collapsed"
    )

    raw_dataframe = None

    if data_source_mode == "Upload Custom CSV File":
        uploaded_file = st.sidebar.file_uploader(
            "Upload your Student CSV",
            type=["csv"],
            help="Upload a CSV with student grades and attendance. See expected schema below."
        )
        if uploaded_file is not None:
            try:
                raw_dataframe = pd.read_csv(uploaded_file)
                st.sidebar.success(f"Uploaded: {uploaded_file.name}")
            except Exception as e:
                st.sidebar.error(f"Error reading CSV: {str(e)}")
        else:
            st.sidebar.info("Upload a CSV file or switch back to the built-in dataset to explore.")
    else:
        raw_dataframe = load_default_sample_data()
        st.sidebar.success("Using built-in sample dataset (250 students).")

    # Schema Guide expander
    with st.sidebar.expander("ℹ️ Expected CSV Columns"):
        st.markdown("""
        **Required Numeric Columns:**
        - `Attendance_Rate` (0-100)
        - `Math_Score` (0-100)
        - `Science_Score` (0-100)
        - `English_Score` (0-100)
        - `History_Score` (0-100)
        
        **Optional / Auto-generated:**
        - `Student_ID`, `Name`
        - `Gender`, `Grade_Level`, `Section`
        - `Study_Hours_Per_Week`
        """)

    # If raw data failed to load or is None, stop here
    if raw_dataframe is None:
        return None, None

    # Validate and clean data
    cleaned_df, validation_errors, validation_warnings = validate_and_clean_data(raw_dataframe)

    if validation_errors:
        for err in validation_errors:
            st.error(f"⚠️ Data Error: {err}")
        return None, None

    if validation_warnings:
        with st.sidebar.expander(f"⚠️ {len(validation_warnings)} Data Adjustment Notice(s)"):
            for warn in validation_warnings:
                st.caption(f"• {warn}")

    st.sidebar.markdown("---")
    st.sidebar.markdown("### 🔍 2. Filter Students")

    # Dynamic filter options from data
    all_grade_levels = sorted(cleaned_df["Grade_Level"].dropna().unique().tolist())
    all_sections = sorted(cleaned_df["Section"].dropna().unique().tolist())
    all_genders = sorted(cleaned_df["Gender"].dropna().unique().tolist())

    selected_grades = st.sidebar.multiselect(
        "Grade Level:",
        options=all_grade_levels,
        default=all_grade_levels
    )

    selected_sections = st.sidebar.multiselect(
        "Section:",
        options=all_sections,
        default=all_sections
    )

    selected_genders = st.sidebar.multiselect(
        "Gender:",
        options=all_genders,
        default=all_genders
    )

    # Attendance Range Slider
    min_att = float(cleaned_df["Attendance_Rate"].min())
    max_att = float(cleaned_df["Attendance_Rate"].max())
    if min_att >= max_att:
        min_att = 0.0
        max_att = 100.0

    attendance_range = st.sidebar.slider(
        "Attendance Rate (%)",
        min_value=0.0,
        max_value=100.0,
        value=(float(min_att), float(max_att)),
        step=1.0
    )

    # Score Range Slider
    min_scr = float(cleaned_df["Average_Score"].min())
    max_scr = float(cleaned_df["Average_Score"].max())
    if min_scr >= max_scr:
        min_scr = 0.0
        max_scr = 100.0

    score_range = st.sidebar.slider(
        "Average Marks Range",
        min_value=0.0,
        max_value=100.0,
        value=(float(min_scr), float(max_scr)),
        step=1.0
    )

    status_filter = st.sidebar.radio(
        "Passing Status:",
        ["All", "Passed Only", "Failed Only"],
        horizontal=True
    )

    # Apply filters
    filtered_df = cleaned_df[
        (cleaned_df["Grade_Level"].isin(selected_grades)) &
        (cleaned_df["Section"].isin(selected_sections)) &
        (cleaned_df["Gender"].isin(selected_genders)) &
        (cleaned_df["Attendance_Rate"] >= attendance_range[0]) &
        (cleaned_df["Attendance_Rate"] <= attendance_range[1]) &
        (cleaned_df["Average_Score"] >= score_range[0]) &
        (cleaned_df["Average_Score"] <= score_range[1])
    ]

    if status_filter == "Passed Only":
        filtered_df = filtered_df[filtered_df["Status"] == "Pass"]
    elif status_filter == "Failed Only":
        filtered_df = filtered_df[filtered_df["Status"] == "Fail"]

    st.sidebar.markdown(f"**Showing:** {len(filtered_df)} of {len(cleaned_df)} students")

    return cleaned_df, filtered_df

# ==============================================================================
# 4. KPI CARDS SECTION
# ==============================================================================
def render_kpi_cards(full_df: pd.DataFrame, filtered_df: pd.DataFrame):
    """Renders 4 visually polished KPI cards showing primary metrics."""
    if filtered_df.empty:
        st.warning("No student records match your selected filters. Please broaden your filter criteria.")
        return

    total_students = len(filtered_df)
    avg_marks = filtered_df["Average_Score"].mean()
    avg_attendance = filtered_df["Attendance_Rate"].mean()
    
    pass_count = (filtered_df["Status"] == "Pass").sum()
    pass_rate = (pass_count / total_students) * 100.0 if total_students > 0 else 0.0
    
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-label">👥 Total Students</div>
                <div class="metric-value">{total_students:,}</div>
                <div class="metric-sub">Out of {len(full_df):,} total enrolled</div>
            </div>
            """,
            unsafe_allow_html=True
        )

    with col2:
        # Color indicator based on average marks
        marks_color = "#10b981" if avg_marks >= 75 else ("#f59e0b" if avg_marks >= 60 else "#ef4444")
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-label">📊 Average Marks</div>
                <div class="metric-value" style="color: {marks_color};">{avg_marks:.1f} / 100</div>
                <div class="metric-sub">Across all 4 core subjects</div>
            </div>
            """,
            unsafe_allow_html=True
        )

    with col3:
        att_color = "#10b981" if avg_attendance >= 80 else ("#f59e0b" if avg_attendance >= 70 else "#ef4444")
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-label">📅 Avg Attendance</div>
                <div class="metric-value" style="color: {att_color};">{avg_attendance:.1f}%</div>
                <div class="metric-sub">School benchmark: 80%</div>
            </div>
            """,
            unsafe_allow_html=True
        )

    with col4:
        pass_color = "#10b981" if pass_rate >= 80 else ("#f59e0b" if pass_rate >= 60 else "#ef4444")
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-label">🎯 Pass Percentage</div>
                <div class="metric-value" style="color: {pass_color};">{pass_rate:.1f}%</div>
                <div class="metric-sub">{pass_count} passed | {total_students - pass_count} failed</div>
            </div>
            """,
            unsafe_allow_html=True
        )

# ==============================================================================
# 5. CHARTS & VISUALIZATIONS
# ==============================================================================
def render_subject_marks_chart(df: pd.DataFrame):
    """Renders interactive subject-wise performance bar chart."""
    subject_names = {
        "Math_Score": "Mathematics",
        "Science_Score": "Science",
        "English_Score": "English",
        "History_Score": "History"
    }
    
    means = [df[col].mean() for col in CORE_SUBJECT_COLS]
    medians = [df[col].median() for col in CORE_SUBJECT_COLS]
    labels = [subject_names[col] for col in CORE_SUBJECT_COLS]

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=labels,
        y=means,
        name="Average (Mean)",
        marker_color="#4f46e5",
        text=[f"{m:.1f}" for m in means],
        textposition="auto"
    ))
    fig.add_trace(go.Bar(
        x=labels,
        y=medians,
        name="Median Score",
        marker_color="#06b6d4",
        text=[f"{m:.1f}" for m in medians],
        textposition="auto"
    ))

    fig.update_layout(
        title="<b>Subject-Wise Score Comparison</b> (Mean vs. Median)",
        barmode="group",
        yaxis_title="Score out of 100",
        yaxis_range=[0, 105],
        template=PLOTLY_TEMPLATE,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        margin=dict(l=20, r=20, t=50, b=20),
        height=380
    )
    return fig

def render_grade_distribution_chart(df: pd.DataFrame):
    """Renders Grade distribution donut chart."""
    grade_order = ["A", "B", "C", "D", "F"]
    grade_counts = df["Grade"].value_counts().reindex(grade_order, fill_value=0)
    
    colors = {
        "A": "#10b981",  # Emerald
        "B": "#4f46e5",  # Indigo
        "C": "#06b6d4",  # Cyan
        "D": "#f59e0b",  # Amber
        "F": "#ef4444"   # Red
    }
    
    fig = go.Figure(data=[go.Pie(
        labels=grade_counts.index,
        values=grade_counts.values,
        hole=0.48,
        marker=dict(colors=[colors[g] for g in grade_counts.index]),
        textinfo="label+percent",
        hoverinfo="label+value+percent",
        sort=False
    )])
    
    fig.update_layout(
        title="<b>Overall Grade Distribution</b> (A, B, C, D, F)",
        template=PLOTLY_TEMPLATE,
        legend=dict(orientation="h", yanchor="bottom", y=-0.1, xanchor="center", x=0.5),
        margin=dict(l=20, r=20, t=50, b=30),
        height=380
    )
    return fig

def render_attendance_vs_marks_chart(df: pd.DataFrame):
    """Renders Attendance vs Marks scatter plot with optional trendline."""
    chart_kwargs = dict(
        data_frame=df,
        x="Attendance_Rate",
        y="Average_Score",
        color="Grade",
        category_orders={"Grade": ["A", "B", "C", "D", "F"]},
        color_discrete_map={
            "A": "#10b981",
            "B": "#4f46e5",
            "C": "#06b6d4",
            "D": "#f59e0b",
            "F": "#ef4444"
        },
        hover_data=["Name", "Student_ID", "Study_Hours_Per_Week", "Status"],
        title="<b>Attendance vs. Academic Performance</b> (with Trendline)",
        labels={
            "Attendance_Rate": "Attendance Rate (%)",
            "Average_Score": "Average Score (out of 100)"
        },
        template=PLOTLY_TEMPLATE
    )

    try:
        fig = px.scatter(**chart_kwargs, trendline="ols")
    except Exception:
        fig = px.scatter(**chart_kwargs)

    fig.update_layout(
        margin=dict(l=20, r=20, t=50, b=20),
        height=420,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    return fig

def render_study_hours_vs_marks_chart(df: pd.DataFrame):
    """Renders Study Hours vs Average Score scatter plot with optional trendline."""
    chart_kwargs = dict(
        data_frame=df,
        x="Study_Hours_Per_Week",
        y="Average_Score",
        color="Status",
        color_discrete_map={"Pass": "#10b981", "Fail": "#ef4444"},
        size="Attendance_Rate",
        hover_data=["Name", "Student_ID", "Grade_Level"],
        title="<b>Weekly Study Hours vs. Average Marks</b> (Bubble size = Attendance %)",
        labels={
            "Study_Hours_Per_Week": "Study Hours per Week (hrs)",
            "Average_Score": "Average Marks (out of 100)",
            "Status": "Status"
        },
        template=PLOTLY_TEMPLATE
    )

    try:
        fig = px.scatter(**chart_kwargs, trendline="ols")
    except Exception:
        fig = px.scatter(**chart_kwargs)

    fig.update_layout(
        margin=dict(l=20, r=20, t=50, b=20),
        height=420,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    return fig

def render_demographic_comparison_chart(df: pd.DataFrame, group_col: str):
    """Renders grouped bar or box plot comparing performance across categories."""
    group_stats = df.groupby(group_col)["Average_Score"].agg(["mean", "median", "count"]).reset_index()
    group_stats.columns = [group_col, "Average_Score", "Median_Score", "Count"]

    fig = px.bar(
        group_stats,
        x=group_col,
        y="Average_Score",
        text=group_stats["Average_Score"].apply(lambda v: f"{v:.1f}"),
        color=group_col,
        color_discrete_sequence=CHART_COLORWAY,
        title=f"<b>Average Score Comparison by {group_col.replace('_', ' ')}</b>",
        labels={"Average_Score": "Mean Score out of 100"},
        template=PLOTLY_TEMPLATE
    )
    fig.update_traces(textposition="outside")
    fig.update_layout(
        yaxis_range=[0, 105],
        margin=dict(l=20, r=20, t=50, b=20),
        height=380,
        showlegend=False
    )
    return fig

# ==============================================================================
# 6. DYNAMIC DATA-DRIVEN INSIGHTS ENGINE
# ==============================================================================
def generate_dynamic_insights(df: pd.DataFrame) -> list[dict]:
    """
    Computes rigorous analytical findings from the active dataset.
    Never invents facts; all figures are strictly computed.
    """
    if df.empty or len(df) < 2:
        return [{"type": "info", "title": "Insufficient Data", "msg": "Select more records to generate insights."}]

    insights = []

    # 1. Best vs Lowest Subject Performance
    subject_means = {
        "Mathematics": df["Math_Score"].mean(),
        "Science": df["Science_Score"].mean(),
        "English": df["English_Score"].mean(),
        "History": df["History_Score"].mean()
    }
    best_subj = max(subject_means, key=subject_means.get)
    worst_subj = min(subject_means, key=subject_means.get)
    diff = subject_means[best_subj] - subject_means[worst_subj]

    insights.append({
        "type": "success",
        "title": f"Top Subject: {best_subj}",
        "msg": f"Students achieved the highest average marks in <b>{best_subj}</b> ({subject_means[best_subj]:.1f}/100), outpacing <b>{worst_subj}</b> ({subject_means[worst_subj]:.1f}/100) by <b>{diff:.1f} points</b>."
    })

    # 2. Attendance Correlation with Marks
    correlation = df["Attendance_Rate"].corr(df["Average_Score"])
    if not np.isnan(correlation):
        if correlation > 0.5:
            corr_strength = "strong positive"
            badge = "info"
        elif correlation > 0.2:
            corr_strength = "moderate positive"
            badge = "info"
        else:
            corr_strength = "weak"
            badge = "warning"

        # Compare high attendance (>=85%) vs low attendance (<75%)
        high_att = df[df["Attendance_Rate"] >= 85]
        low_att = df[df["Attendance_Rate"] < 75]

        if not high_att.empty and not low_att.empty:
            score_diff = high_att["Average_Score"].mean() - low_att["Average_Score"].mean()
            insights.append({
                "type": badge,
                "title": f"Attendance Impact (r = {correlation:.2f})",
                "msg": f"There is a <b>{corr_strength} correlation</b> between attendance and academic marks. Students with attendance ≥ 85% scored on average <b>{score_diff:.1f} marks higher</b> than those below 75%."
            })

    # 3. Early Warning Intervention Need
    at_risk = df[(df["Average_Score"] < 60) | (df["Attendance_Rate"] < 70)]
    at_risk_pct = (len(at_risk) / len(df)) * 100.0

    if at_risk_pct > 0:
        insights.append({
            "type": "warning" if at_risk_pct < 20 else "danger",
            "title": f"Academic Intervention Needed: {len(at_risk)} Student(s)",
            "msg": f"<b>{at_risk_pct:.1f}%</b> of active students ({len(at_risk)} total) are currently at risk due to either failing grades (&lt;60) or chronically low attendance (&lt;70%). Targeted mentoring is recommended."
        })
    else:
        insights.append({
            "type": "success",
            "title": "Zero Students At Risk",
            "msg": "All filtered students are currently maintaining passing grades and sufficient attendance!"
        })

    # 4. Honor Roll (A Grade students)
    honor_roll = df[df["Grade"] == "A"]
    honor_pct = (len(honor_roll) / len(df)) * 100.0
    insights.append({
        "type": "info",
        "title": f"Honor Roll (Grade A): {len(honor_roll)} Student(s)",
        "msg": f"<b>{honor_pct:.1f}%</b> of students achieved an 'A' grade (average ≥ 90). The top score in this group is <b>{df['Average_Score'].max():.1f}/100</b>."
    })

    return insights

# ==============================================================================
# 7. MAIN APPLICATION CONTROLLER
# ==============================================================================
def main():
    # Render Sidebar and retrieve full & filtered DataFrames
    full_df, filtered_df = render_sidebar()

    # If data failed to load or errors occurred
    if full_df is None or filtered_df is None:
        st.info("👈 Please select or upload a valid dataset from the sidebar to begin analysis.")
        return

    # Top Hero Header Banner
    st.markdown(
        """
        <div class="dashboard-header">
            <h1>Student Performance Analytics Dashboard</h1>
            <p>Interactive exploratory data analysis, KPI monitoring, and predictive academic insights.</p>
        </div>
        """,
        unsafe_allow_html=True
    )

    # 1. KPI Metric Summary Cards
    render_kpi_cards(full_df, filtered_df)
    st.markdown("<div style='margin-bottom: 25px;'></div>", unsafe_allow_html=True)

    if filtered_df.empty:
        return

    # 2. Main Dashboard Tabs
    tab_overview, tab_correlations, tab_insights, tab_explorer = st.tabs([
        "📊 Academic Overview",
        "📈 Correlations & Trends",
        "💡 Automated Insights",
        "📋 Data Explorer & Export"
    ])

    # ----------------------------------------------------
    # TAB 1: ACADEMIC OVERVIEW
    # ----------------------------------------------------
    with tab_overview:
        col_chart1, col_chart2 = st.columns([1.1, 0.9])
        with col_chart1:
            fig_subject = render_subject_marks_chart(filtered_df)
            st.plotly_chart(fig_subject, use_container_width=True)

        with col_chart2:
            fig_grades = render_grade_distribution_chart(filtered_df)
            st.plotly_chart(fig_grades, use_container_width=True)

        st.markdown("---")
        # Demographic breakdown
        col_sub1, col_sub2 = st.columns(2)
        with col_sub1:
            fig_grade_level = render_demographic_comparison_chart(filtered_df, "Grade_Level")
            st.plotly_chart(fig_grade_level, use_container_width=True)

        with col_sub2:
            fig_section = render_demographic_comparison_chart(filtered_df, "Section")
            st.plotly_chart(fig_section, use_container_width=True)

    # ----------------------------------------------------
    # TAB 2: CORRELATIONS & TRENDS
    # ----------------------------------------------------
    with tab_correlations:
        st.markdown("#### Discover What Drives High Performance")
        st.caption("Inspect how attendance and study habits correlate with subject marks.")

        col_corr1, col_corr2 = st.columns(2)
        with col_corr1:
            fig_att_marks = render_attendance_vs_marks_chart(filtered_df)
            st.plotly_chart(fig_att_marks, use_container_width=True)

        with col_corr2:
            fig_study_marks = render_study_hours_vs_marks_chart(filtered_df)
            st.plotly_chart(fig_study_marks, use_container_width=True)

        # Subject-to-Subject Correlation Heatmap
        st.markdown("#### Subject Score Correlation Matrix")
        corr_matrix = filtered_df[CORE_SUBJECT_COLS].corr().round(2)
        fig_heat = px.imshow(
            corr_matrix,
            text_auto=True,
            aspect="auto",
            color_continuous_scale="Viridis",
            title="<b>Pairwise Subject Correlation</b>",
            template=PLOTLY_TEMPLATE
        )
        fig_heat.update_layout(height=350, margin=dict(l=20, r=20, t=50, b=20))
        st.plotly_chart(fig_heat, use_container_width=True)

    # ----------------------------------------------------
    # TAB 3: AUTOMATED INSIGHTS
    # ----------------------------------------------------
    with tab_insights:
        st.markdown("#### 🧠 Data-Driven Academic Findings")
        st.caption("Key patterns computed strictly from the filtered student cohort:")

        insights_list = generate_dynamic_insights(filtered_df)
        for item in insights_list:
            st.markdown(
                f"""
                <div class="insight-box insight-{item['type']}">
                    <strong style="font-size: 1rem;">{item['title']}</strong><br/>
                    <span style="font-size: 0.92rem;">{item['msg']}</span>
                </div>
                """,
                unsafe_allow_html=True
            )

        st.markdown("---")
        # High performers and At-Risk table side-by-side
        col_honor, col_risk = st.columns(2)
        
        with col_honor:
            st.markdown("##### 🏆 Top Performers (Honor Roll: Grade A)")
            top_performers = filtered_df[filtered_df["Grade"] == "A"].sort_values(by="Average_Score", ascending=False)
            if not top_performers.empty:
                st.dataframe(
                    top_performers[["Student_ID", "Name", "Average_Score", "Attendance_Rate", "Study_Hours_Per_Week"]].head(10),
                    use_container_width=True,
                    hide_index=True
                )
            else:
                st.info("No students with Grade A in the current filter.")

        with col_risk:
            st.markdown("##### ⚠️ Students Requiring Academic Support")
            struggling = filtered_df[(filtered_df["Status"] == "Fail") | (filtered_df["Attendance_Rate"] < 70)].sort_values(by="Average_Score", ascending=True)
            if not struggling.empty:
                st.dataframe(
                    struggling[["Student_ID", "Name", "Average_Score", "Attendance_Rate", "Status"]].head(10),
                    use_container_width=True,
                    hide_index=True
                )
            else:
                st.success("All students in current filter are passing with healthy attendance.")

    # ----------------------------------------------------
    # TAB 4: DATA EXPLORER & EXPORT
    # ----------------------------------------------------
    with tab_explorer:
        st.markdown("#### 🔎 Interactive Student Records")
        
        col_search, col_sort = st.columns([2, 1])
        with col_search:
            search_query = st.text_input("Search by Student Name or ID:", placeholder="e.g. Liam, STU1024...")
        with col_sort:
            sort_by = st.selectbox("Sort Table By:", ["Average_Score", "Attendance_Rate", "Math_Score", "Name", "Student_ID"])

        display_df = filtered_df.copy()
        if search_query:
            display_df = display_df[
                display_df["Name"].str.contains(search_query, case=False, na=False) |
                display_df["Student_ID"].str.contains(search_query, case=False, na=False)
            ]

        display_df = display_df.sort_values(by=sort_by, ascending=False if sort_by != "Name" and sort_by != "Student_ID" else True)

        st.dataframe(
            display_df,
            use_container_width=True,
            hide_index=True,
            column_config={
                "Attendance_Rate": st.column_config.ProgressColumn(
                    "Attendance %",
                    format="%.1f%%",
                    min_value=0,
                    max_value=100
                ),
                "Average_Score": st.column_config.NumberColumn(
                    "Avg Score",
                    format="%.1f"
                ),
                "Math_Score": st.column_config.NumberColumn("Math", format="%d"),
                "Science_Score": st.column_config.NumberColumn("Science", format="%d"),
                "English_Score": st.column_config.NumberColumn("English", format="%d"),
                "History_Score": st.column_config.NumberColumn("History", format="%d"),
            }
        )

        st.markdown("---")
        # Export Actions
        col_dl1, col_dl2 = st.columns(2)

        with col_dl1:
            # Download Filtered Cleaned Dataset
            csv_buffer = io.StringIO()
            display_df.to_csv(csv_buffer, index=False)
            st.download_button(
                label="📥 Download Cleaned / Filtered Data (CSV)",
                data=csv_buffer.getvalue(),
                file_name="cleaned_student_performance_data.csv",
                mime="text/csv",
                help="Click to download the current filtered and analyzed records as a CSV file."
            )

        with col_dl2:
            # Download Sample Template for Uploading
            template_cols = [
                "Student_ID", "Name", "Gender", "Grade_Level", "Section",
                "Attendance_Rate", "Study_Hours_Per_Week",
                "Math_Score", "Science_Score", "English_Score", "History_Score"
            ]
            template_df = full_df[template_cols].head(5)
            tmpl_buffer = io.StringIO()
            template_df.to_csv(tmpl_buffer, index=False)
            st.download_button(
                label="📄 Download Sample CSV Template",
                data=tmpl_buffer.getvalue(),
                file_name="student_template.csv",
                mime="text/csv",
                help="Download a 5-row CSV template with correct headers to test custom file upload."
            )

if __name__ == "__main__":
    main()
