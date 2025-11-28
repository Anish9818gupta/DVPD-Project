import streamlit as st
import pandas as pd
import plotly.express as px
import json
import base64
import os

# -------------------- CONFIG --------------------
st.set_page_config(
    page_title="University Research Dashboard",
    layout="wide",
    initial_sidebar_state="expanded",
)

# -------------------- CACHED LOADERS --------------------
@st.cache_data
def load_csv_safe(path):
    try:
        df = pd.read_csv(path)
        return df
    except Exception:
        return pd.DataFrame()

# -------------------- FILE NAMES (expected) --------------------
ECE_FILE = "ece_department_faculty.csv"
CSE_FILE = "cse_department_faculty.csv"
MECH_FILE = "mechanical_department_faculty.csv"
TEXTILE_FILE = "textile_department_faculty.csv"
DEPT_STATS_FILE = "department_external_statistics.csv"
UNI_OVERVIEW_FILE = "university_external_overview.csv"
HERO_IMAGE = "image.png"  # must be in same folder

# -------------------- LOAD DATA --------------------
files = {
    "Electronics & Comm (ECE)": load_csv_safe(ECE_FILE),
    "Computer Sci & Eng (CSE)": load_csv_safe(CSE_FILE),
    "Mechanical Engg": load_csv_safe(MECH_FILE),
    "Textile Tech": load_csv_safe(TEXTILE_FILE),
}
dept_stats = load_csv_safe(DEPT_STATS_FILE)
uni_stats = load_csv_safe(UNI_OVERVIEW_FILE)

# combine faculty files if present (attach a Department column by file key)
faculty_all = pd.concat(
    [df.assign(Department=name) for name, df in files.items() if not df.empty],
    ignore_index=True
) if any(not df.empty for df in files.values()) else pd.DataFrame()

# -------------------- UTILITIES --------------------
def download_link_df(df: pd.DataFrame, filename: str, link_text: str = "Download"):
    """Create a link to download a dataframe as CSV"""
    csv = df.to_csv(index=False).encode("utf-8")
    b64 = base64.b64encode(csv).decode()
    href = f'<a href="data:file/csv;base64,{b64}" download="{filename}">{link_text}</a>'
    return href

def safe_int(x):
    try:
        return int(x)
    except Exception:
        return x

# -------------------- LIGHT THEME CSS (clean professional) --------------------
st.markdown(
    """
    <style>
    /* General */
    .stApp { background: #ffffff; color: #0b1726; }
    .sidebar .sidebar-content { background: #f7fbff; }
    /* Headings */
    h1, h2, h3, h4, h5, h6 { color: #0b1726; }
    /* Card / metric style */
    .metric-card {
        padding: 12px;
        border-radius: 10px;
        background: linear-gradient(180deg, #ffffff, #f1f7ff);
        box-shadow: 0 6px 18px rgba(14, 30, 50, 0.06);
        border: 1px solid rgba(13, 60, 150, 0.06);
    }
    .section-title {
        font-size: 20px;
        font-weight: 700;
        color: #0b1726;
        margin-bottom: 6px;
    }
    .accent {
        width: 48px;
        height: 6px;
        background: #1f6feb;
        border-radius: 4px;
        margin-bottom: 10px;
    }
    a { color: #1f6feb; }
    .small-muted { color: #6b7280; font-size: 13px; }
    </style>
    """,
    unsafe_allow_html=True
)

# -------------------- SIDEBAR --------------------
st.sidebar.markdown("## 🔎 Dashboard")
st.sidebar.markdown("Light theme • Clean metrics • Multi-page")
page = st.sidebar.radio(
    "Navigate",
    ["Overview", "Department Comparison", "Per-Department", "Faculty Explorer", "Advanced Charts", "Data & Downloads"]
)

# quick helper to fetch uni metrics by keyword
def get_uni_val(keyword):
    if uni_stats.empty:
        return "N/A"
    mask = uni_stats['Category'].astype(str).str.contains(keyword, case=False, na=False)
    if mask.any():
        return uni_stats.loc[mask, 'Value'].iloc[0]
    return "N/A"

# -------------------- PAGE: OVERVIEW --------------------
if page == "Overview":
    st.markdown("<div style='display:flex; align-items:center; gap:12px;'>"
                "<div style='font-size:28px; font-weight:700;'>🏛️ University Research Overview</div>"
                "</div>", unsafe_allow_html=True)

    # HERO IMAGE (full-width)
    if os.path.exists(HERO_IMAGE):
        st.image(HERO_IMAGE, use_column_width=True, caption="Institution research snapshot", clamp=True)
    else:
        st.warning(f"'{HERO_IMAGE}' not found in the app folder. Place the image in same folder and restart the app.")

    st.markdown("<div class='accent'></div>", unsafe_allow_html=True)

    # Key metrics row
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown("<div class='metric-card'>", unsafe_allow_html=True)
        st.markdown("**Total publications**")
        st.markdown(f"<h2 style='margin:4px 0 0 0; color:#0b1726;'>{get_uni_val('Publications')}</h2>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
    with col2:
        st.markdown("<div class='metric-card'>", unsafe_allow_html=True)
        st.markdown("**Total citations**")
        st.markdown(f"<h2 style='margin:4px 0 0 0; color:#0b1726;'>{get_uni_val('Total Citations')}</h2>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
    with col3:
        st.markdown("<div class='metric-card'>", unsafe_allow_html=True)
        st.markdown("**Scopus citations**")
        st.markdown(f"<h2 style='margin:4px 0 0 0; color:#0b1726;'>{get_uni_val('Scopus')}</h2>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
    with col4:
        st.markdown("<div class='metric-card'>", unsafe_allow_html=True)
        st.markdown("**Patents**")
        st.markdown(f"<h2 style='margin:4px 0 0 0; color:#0b1726;'>{get_uni_val('Patents')}</h2>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("<div class='section-title'>Publication composition</div>", unsafe_allow_html=True)

    if not dept_stats.empty:
        comp_cols = [c for c in ["Journal Articles", "Conference / Proceedings", "Books / Chapters", "Books", "Other"] if c in dept_stats.columns]
        comp = dept_stats[comp_cols].sum().reset_index()
        comp.columns = ["Type", "Count"]
        fig = px.pie(comp, names="Type", values="Count", title="Overall publication composition", hole=0.35)
        fig.update_traces(textposition='inside', textinfo='percent+label')
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Upload department_external_statistics.csv to enable composition chart.")

# -------------------- PAGE: DEPARTMENT COMPARISON --------------------
elif page == "Department Comparison":
    st.markdown("<div class='section-title'>Department Comparison</div>", unsafe_allow_html=True)
    st.markdown("<div class='small-muted'>Compare departments across different metrics.</div>", unsafe_allow_html=True)
    st.markdown("<div class='accent'></div>", unsafe_allow_html=True)

    if dept_stats.empty:
        st.warning("department_external_statistics.csv not found.")
    else:
        metrics = [c for c in dept_stats.columns if c != "Department"]
        metric = st.selectbox("Select metric", metrics, index=0)
        fig = px.bar(
            dept_stats.sort_values(metric, ascending=False),
            x="Department", y=metric, color=metric,
            text=metric, height=520
        )
        fig.update_layout(showlegend=False, xaxis_tickangle=25)
        st.plotly_chart(fig, use_container_width=True)

        st.markdown("### Heatmap (departments vs core metrics)")
        core = [c for c in ["Journal Articles", "Conference / Proceedings", "Citations", "h-index"] if c in dept_stats.columns]
        if core:
            heat = dept_stats.set_index("Department")[core].fillna(0)
            fig2 = px.imshow(heat, labels=dict(x="Metric", y="Department", color="Value"), aspect="auto")
            st.plotly_chart(fig2, use_container_width=True)

# -------------------- PAGE: PER-DEPARTMENT --------------------
elif page == "Per-Department":
    st.markdown("<div class='section-title'>Per-Department Insight</div>", unsafe_allow_html=True)
    st.markdown("<div class='small-muted'>Select a department to view detailed metrics and faculty.</div>", unsafe_allow_html=True)
    st.markdown("<div class='accent'></div>", unsafe_allow_html=True)

    if dept_stats.empty:
        st.warning("department_external_statistics.csv not found.")
    else:
        dept_list = dept_stats["Department"].tolist()
        dept_choice = st.selectbox("Choose department", dept_list)
        row = dept_stats[dept_stats["Department"] == dept_choice].iloc[0]

        # summary cards
        cols = st.columns(4)
        for i, colname in enumerate(["Journal Articles", "Conference / Proceedings", "Books / Chapters", "Books"]):
            if colname in dept_stats.columns:
                cols[i].markdown("<div class='metric-card'>", unsafe_allow_html=True)
                cols[i].markdown(f"**{colname}**")
                cols[i].markdown(f"<h3 style='margin:4px 0 0 0;'>{safe_int(row[colname])}</h3>", unsafe_allow_html=True)
                cols[i].markdown("</div>", unsafe_allow_html=True)

        # other metrics
        cols2 = st.columns(3)
        if "Other" in dept_stats.columns:
            cols2[0].markdown("<div class='metric-card'>", unsafe_allow_html=True)
            cols2[0].markdown("**Other**")
            cols2[0].markdown(f"<h3>{safe_int(row['Other'])}</h3>", unsafe_allow_html=True)
            cols2[0].markdown("</div>", unsafe_allow_html=True)
        if "Citations" in dept_stats.columns:
            cols2[1].markdown("<div class='metric-card'>", unsafe_allow_html=True)
            cols2[1].markdown("**Citations**")
            cols2[1].markdown(f"<h3>{safe_int(row['Citations'])}</h3>", unsafe_allow_html=True)
            cols2[1].markdown("</div>", unsafe_allow_html=True)
        if "h-index" in dept_stats.columns:
            cols2[2].markdown("<div class='metric-card'>", unsafe_allow_html=True)
            cols2[2].markdown("**h-index**")
            cols2[2].markdown(f"<h3>{safe_int(row['h-index'])}</h3>", unsafe_allow_html=True)
            cols2[2].markdown("</div>", unsafe_allow_html=True)

        st.markdown("---")
        # breakdown bar
        metrics = [c for c in ["Journal Articles", "Conference / Proceedings", "Books / Chapters", "Books", "Other", "Citations", "Scopus Citations", "h-index"] if c in dept_stats.columns]
        values = [row[c] for c in metrics]
        df_break = pd.DataFrame({"Metric": metrics, "Value": values})
        fig = px.bar(df_break, x="Metric", y="Value", text="Value", height=420)
        st.plotly_chart(fig, use_container_width=True)

        st.markdown("#### Faculty (if available)")
        fac = faculty_all[faculty_all["Department"].str.contains(dept_choice.split()[0], case=False, na=False)] if not faculty_all.empty else pd.DataFrame()
        # fallback: show all faculty if no direct mapping
        if fac.empty and not faculty_all.empty:
            st.info("No exact faculty mapping found; showing all faculty.")
            st.dataframe(faculty_all, use_container_width=True)
        elif not fac.empty:
            st.dataframe(fac, use_column_width=True)
            st.markdown(download_link_df(fac, f"faculty_{dept_choice}.csv", "Download this department's faculty"), unsafe_allow_html=True)

# -------------------- PAGE: FACULTY EXPLORER --------------------
elif page == "Faculty Explorer":
    st.markdown("<div class='section-title'>Faculty Explorer</div>", unsafe_allow_html=True)
    st.markdown("<div class='small-muted'>Search and filter faculty across departments.</div>", unsafe_allow_html=True)
    st.markdown("<div class='accent'></div>", unsafe_allow_html=True)

    if faculty_all.empty:
        st.warning("No faculty CSVs found in folder (expected ece/cse/mech/textile files).")
    else:
        c1, c2 = st.columns((3,1))
        with c1:
            query = st.text_input("Search by name, research area, or position (contains)")
        with c2:
            pos_choices = sorted(faculty_all['Position'].dropna().unique()) if 'Position' in faculty_all.columns else []
            pos_filter = st.multiselect("Position filter", options=pos_choices)

        df = faculty_all.copy()
        if query:
            mask = df.apply(lambda r: query.lower() in " ".join(r.astype(str).values).lower(), axis=1)
            df = df[mask]
        if pos_filter:
            df = df[df['Position'].isin(pos_filter)]

        st.dataframe(df, use_container_width=True)
        st.markdown(download_link_df(df, "faculty_filtered.csv", "Download filtered faculty data"), unsafe_allow_html=True)

# -------------------- PAGE: ADVANCED CHARTS --------------------
elif page == "Advanced Charts":
    st.markdown("<div class='section-title'>Advanced Visualizations</div>", unsafe_allow_html=True)
    st.markdown("<div class='small-muted'>Scatter, Bubble, Heatmap, and Highcharts-style embed.</div>", unsafe_allow_html=True)
    st.markdown("<div class='accent'></div>", unsafe_allow_html=True)

    if dept_stats.empty:
        st.warning("department_external_statistics.csv not found.")
    else:
        # Scatter: publications vs citations
        if "Journal Articles" in dept_stats.columns and "Citations" in dept_stats.columns:
            st.subheader("Publications vs Citations (bubble = h-index)")
            fig = px.scatter(
                dept_stats,
                x="Journal Articles",
                y="Citations",
                size="h-index" if "h-index" in dept_stats.columns else None,
                hover_name="Department",
                height=520
            )
            st.plotly_chart(fig, use_container_width=True)

        st.markdown("---")
        # Bubble chart: journal vs conference
        if "Conference / Proceedings" in dept_stats.columns:
            st.subheader("Journal vs Conference (bubble = citations)")
            fig2 = px.scatter(
                dept_stats,
                x="Journal Articles",
                y="Conference / Proceedings",
                size="Citations" if "Citations" in dept_stats.columns else None,
                hover_name="Department",
                height=520
            )
            st.plotly_chart(fig2, use_container_width=True)

        st.markdown("---")
        # Heatmap of core metrics
        core = [c for c in ["Journal Articles", "Conference / Proceedings", "Citations", "h-index"] if c in dept_stats.columns]
        if core:
            st.subheader("Heatmap (department x metric)")
            heat = dept_stats.set_index("Department")[core].fillna(0)
            fig3 = px.imshow(heat, labels=dict(x="Metric", y="Department", color="Value"), aspect="auto")
            st.plotly_chart(fig3, use_container_width=True)

        st.markdown("---")
        st.subheader("HighCharts-style interactive chart")

        # prepare series
        categories = dept_stats["Department"].tolist()
        series = []
        for m in ["Journal Articles", "Citations", "h-index"]:
            if m in dept_stats.columns:
                series.append({"name": m, "data": dept_stats[m].fillna(0).tolist()})

        hc_html = f"""
        <!doctype html>
        <html>
        <head>
        <meta charset="utf-8"/>
        <script src="https://code.highcharts.com/highcharts.js"></script>
        </head>
        <body>
        <div id="hc" style="width:100%; height:520px;"></div>
        <script>
        Highcharts.chart('hc', {{
            chart: {{ type: 'column' }},
            title: {{ text: 'Department Comparison (HighCharts)' }},
            xAxis: {{ categories: {json.dumps(categories)} }},
            yAxis: {{ title: {{ text: 'Value' }} }},
            series: {json.dumps(series)}
        }});
        </script>
        </body>
        </html>
        """
        st.components.v1.html(hc_html, height=560)

# -------------------- PAGE: DATA & DOWNLOADS --------------------
elif page == "Data & Downloads":
    st.markdown("<div class='section-title'>Data & Downloads</div>", unsafe_allow_html=True)
    st.markdown("<div class='small-muted'>Inspect and download source CSVs powering this dashboard.</div>", unsafe_allow_html=True)
    st.markdown("<div class='accent'></div>", unsafe_allow_html=True)

    if not dept_stats.empty:
        st.subheader("Department External Statistics")
        st.dataframe(dept_stats, use_container_width=True)
        st.markdown(download_link_df(dept_stats, "department_external_statistics.csv", "Download department_external_statistics.csv"), unsafe_allow_html=True)
    else:
        st.info("department_external_statistics.csv not found.")

    if not uni_stats.empty:
        st.subheader("University Overview")
        st.dataframe(uni_stats, use_container_width=True)
        st.markdown(download_link_df(uni_stats, "university_external_overview.csv", "Download university_external_overview.csv"), unsafe_allow_html=True)
    else:
        st.info("university_external_overview.csv not found.")

    if not faculty_all.empty:
        st.subheader("Combined Faculty Data")
        st.dataframe(faculty_all, use_container_width=True)
        st.markdown(download_link_df(faculty_all, "faculty_all.csv", "Download faculty_all.csv"), unsafe_allow_html=True)
    else:
        st.info("No faculty CSVs found (expected ece/cse/mech/textile).")

# -------------------- FOOTER --------------------
st.sidebar.markdown("---")
st.sidebar.caption("Place the CSV files and image.png in the same folder as app.py. Refresh the app after updating files.")

