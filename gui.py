"""
gui.py — Streamlit GUI for Social Media Forensics & OSINT Investigation
Place this file in the project root (same level as main.py) and run:
    streamlit run gui.py
"""

import streamlit as st
import streamlit.components.v1 as components
import json
import os
import glob
from datetime import datetime

# ─────────────────────────────────────────────
# Page config (must be first Streamlit call)
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="OSINT Forensics",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────
# Custom CSS
# ─────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Share+Tech+Mono&family=Rajdhani:wght@400;600;700&display=swap');

html, body, [class*="css"] {
    font-family: 'Rajdhani', sans-serif;
    background-color: #0a0c10;
    color: #c9d1d9;
}
section[data-testid="stSidebar"] {
    background: #0d1117;
    border-right: 1px solid #21262d;
}
h1, h2, h3 {
    font-family: 'Share Tech Mono', monospace !important;
    color: #58a6ff !important;
    letter-spacing: 2px;
}
.stTabs [data-baseweb="tab-list"] {
    background: #161b22;
    border-radius: 6px;
    gap: 4px;
}
.stTabs [data-baseweb="tab"] {
    font-family: 'Share Tech Mono', monospace;
    color: #8b949e;
    font-size: 12px;
    letter-spacing: 1px;
}
.stTabs [aria-selected="true"] {
    color: #58a6ff !important;
    background: #1f2937 !important;
    border-radius: 4px;
}
.stButton > button {
    font-family: 'Share Tech Mono', monospace;
    background: #238636;
    color: #ffffff;
    border: 1px solid #2ea043;
    border-radius: 6px;
    letter-spacing: 1px;
    width: 100%;
    padding: 10px;
    font-size: 14px;
    transition: all 0.2s ease;
}
.stButton > button:hover {
    background: #2ea043;
    border-color: #3fb950;
    transform: translateY(-1px);
    box-shadow: 0 4px 12px rgba(46,160,67,0.3);
}
.stTextInput > div > div > input {
    background: #161b22;
    color: #c9d1d9;
    border: 1px solid #30363d;
    border-radius: 6px;
    font-family: 'Share Tech Mono', monospace;
    font-size: 14px;
}
.stTextInput > div > div > input:focus {
    border-color: #58a6ff;
    box-shadow: 0 0 0 3px rgba(88,166,255,0.1);
}
.stCheckbox label {
    font-family: 'Share Tech Mono', monospace;
    font-size: 12px;
    color: #8b949e;
    letter-spacing: 1px;
}
.stDownloadButton > button {
    font-family: 'Share Tech Mono', monospace;
    background: #1f2937;
    color: #58a6ff;
    border: 1px solid #30363d;
    border-radius: 6px;
    font-size: 12px;
    letter-spacing: 1px;
}
[data-testid="metric-container"] {
    background: #161b22;
    border: 1px solid #21262d;
    border-radius: 8px;
    padding: 12px;
}
code {
    font-family: 'Share Tech Mono', monospace;
    background: #161b22;
    color: #79c0ff;
    padding: 2px 6px;
    border-radius: 4px;
    font-size: 12px;
}
.badge-found {
    display: inline-block;
    background: #1a4731;
    color: #3fb950;
    border: 1px solid #2ea043;
    border-radius: 12px;
    padding: 2px 10px;
    font-size: 11px;
    font-family: 'Share Tech Mono', monospace;
    letter-spacing: 1px;
    margin: 2px;
}
.badge-notfound {
    display: inline-block;
    background: #2d1a1a;
    color: #f85149;
    border: 1px solid #da3633;
    border-radius: 12px;
    padding: 2px 10px;
    font-size: 11px;
    font-family: 'Share Tech Mono', monospace;
    letter-spacing: 1px;
    margin: 2px;
}
hr { border-color: #21262d; }
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────
# Session state initialisation
# This persists results when switching tabs
# ─────────────────────────────────────────────
KEYS = ["username_results", "profile_results", "graph_html", "graph_png",
        "cache_results", "report_html", "report_json", "last_username",
        "errors"]

for key in KEYS:
    if key not in st.session_state:
        st.session_state[key] = None

if "errors" not in st.session_state or st.session_state["errors"] is None:
    st.session_state["errors"] = {}


# ─────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────
def ensure_data_dirs():
    for d in ["data/raw", "data/processed", "data/graphs", "data/reports"]:
        os.makedirs(d, exist_ok=True)

def latest_file(pattern):
    files = glob.glob(pattern)
    return max(files, key=os.path.getmtime) if files else None


# ─────────────────────────────────────────────
# Sidebar
# ─────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🔍 OSINT TOOL")
    st.markdown("---")

    username = st.text_input(
        "TARGET USERNAME",
        placeholder="e.g. torvalds",
    )

    st.markdown("### MODULES")
    run_username = st.checkbox("Username Search",    value=True)
    run_profile  = st.checkbox("Profile Extraction", value=True)
    run_graph    = st.checkbox("Network Graph",      value=True)
    run_cache    = st.checkbox("Cache Recovery",     value=True)
    run_report   = st.checkbox("Report Generation",  value=True)

    st.markdown("---")
    run_btn = st.button("▶  RUN INVESTIGATION")

    # Show last investigated username
    if st.session_state["last_username"]:
        st.markdown(
            f"<small style='color:#484f58;font-family:Share Tech Mono,monospace;'>"
            f"Last run: <b style='color:#58a6ff'>{st.session_state['last_username']}</b></small>",
            unsafe_allow_html=True,
        )

    st.markdown("---")
    st.markdown(
        "<small style='color:#484f58;font-family:Share Tech Mono,monospace;'>"
        "For legitimate forensic research only.</small>",
        unsafe_allow_html=True,
    )


# ─────────────────────────────────────────────
# Run investigation — store everything in session_state
# ─────────────────────────────────────────────
if run_btn:
    if not username.strip():
        st.error("Please enter a username in the sidebar.")
        st.stop()

    username = username.strip()
    ensure_data_dirs()

    # Clear previous results
    for key in KEYS:
        st.session_state[key] = None
    st.session_state["errors"] = {}
    st.session_state["last_username"] = username

    # Module 1 — Username Search
    if run_username:
        with st.spinner("Searching platforms..."):
            try:
                from src.osint.username_search import search_username
                st.session_state["username_results"] = search_username(username)
            except Exception as e:
                st.session_state["errors"]["username"] = str(e)

    # Module 2 — Profile Extraction
    if run_profile:
        with st.spinner("Extracting profiles..."):
            try:
                from src.extractor.profile_extractor import ProfileExtractor
                extractor = ProfileExtractor()
                st.session_state["profile_results"] = extractor.extract_all(username)
            except Exception as e:
                st.session_state["errors"]["profile"] = str(e)

    # Module 3 — Network Graph
    if run_graph:
        with st.spinner("Building network graph..."):
            try:
                from src.graph.network_graph import NetworkGraph
                g = NetworkGraph()
                g.load_github_network(username, max_users=10)
                g.load_reddit_network(username, max_posts=10)
                g.detect_suspect_clusters()
                g.visualize()
                g.visualize_interactive()
                g.save_graph_data(username)
                st.session_state["graph_html"] = latest_file("data/graphs/*.html")
                st.session_state["graph_png"]  = latest_file("data/graphs/*.png")
            except Exception as e:
                st.session_state["errors"]["graph"] = str(e)

    # Module 4 — Cache Recovery
    if run_cache:
        with st.spinner("Querying Wayback Machine..."):
            try:
                from src.osint.cache_recovery import CacheRecovery
                c = CacheRecovery()
                st.session_state["cache_results"] = c.recover_all(username)
            except Exception as e:
                st.session_state["errors"]["cache"] = str(e)

    # Module 5 — Report Generation
    if run_report:
        with st.spinner("Generating reports..."):
            try:
                from src.reports.report_generator import ReportGenerator
                r = ReportGenerator()
                r.generate_html(username)
                r.generate_json(username)
                st.session_state["report_html"] = latest_file(f"data/reports/report_{username}*.html")
                st.session_state["report_json"] = latest_file(f"data/reports/report_{username}*.json")
            except Exception as e:
                st.session_state["errors"]["report"] = str(e)

    st.rerun()  # refresh so all tabs render with new data


# ─────────────────────────────────────────────
# Main header
# ─────────────────────────────────────────────
st.markdown("# SOCIAL MEDIA FORENSICS & OSINT")
st.markdown(
    "<p style='font-family:Share Tech Mono,monospace;color:#8b949e;font-size:13px;'>"
    "Archive · Extract · Graph · Recover · Report</p>",
    unsafe_allow_html=True,
)
st.markdown("---")

tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "🌐  USERNAME SEARCH",
    "👤  PROFILE",
    "🕸  NETWORK GRAPH",
    "🗂  CACHE RECOVERY",
    "📄  REPORT",
    "ℹ️  HELP",
])

PLACEHOLDER = (
    "<p style='color:#484f58;font-family:Share Tech Mono,monospace;font-size:13px;'>"
    "Enter a username in the sidebar and click ▶ RUN INVESTIGATION.</p>"
)

# ── Tab 1: Username Search ─────────────────────────────────────
with tab1:
    if st.session_state["errors"].get("username"):
        st.error(f"Username search failed: {st.session_state['errors']['username']}")
    elif st.session_state["username_results"]:
        results = st.session_state["username_results"]
        st.markdown(f"### USERNAME SEARCH — `{st.session_state['last_username']}`")
        found     = {k: v for k, v in results.items() if v.get("found")}
        not_found = {k: v for k, v in results.items() if not v.get("found")}

        col1, col2, col3 = st.columns(3)
        col1.metric("Platforms Checked", len(results))
        col2.metric("Found",             len(found))
        col3.metric("Not Found",         len(not_found))

        st.markdown("#### PLATFORM RESULTS")
        badges = ""
        for platform, data in results.items():
            reason = data.get("reason", "")
            if data.get("found"):
                badges += f'<span class="badge-found">✓ {platform}</span> '
            else:
                badges += f'<span class="badge-notfound">✗ {platform}</span> '
        st.markdown(badges, unsafe_allow_html=True)

        st.markdown("#### REASONS")
        for platform, data in results.items():
            st.markdown(
                f"<code>{platform}</code>&nbsp;&nbsp;"
                f"<span style='color:#8b949e;font-size:12px;font-family:Share Tech Mono,monospace'>"
                f"{data.get('reason','')}</span>",
                unsafe_allow_html=True,
            )

        with st.expander("VIEW RAW JSON"):
            st.json(results)
    else:
        st.markdown(PLACEHOLDER, unsafe_allow_html=True)

# ── Tab 2: Profile ─────────────────────────────────────────────
with tab2:
    if st.session_state["errors"].get("profile"):
        st.error(f"Profile extraction failed: {st.session_state['errors']['profile']}")
    elif st.session_state["profile_results"]:
        data = st.session_state["profile_results"]
        st.markdown(f"### PROFILE EXTRACTION — `{st.session_state['last_username']}`")
        github_data = data.get("github") or data.get("GitHub") or {}
        reddit_data = data.get("reddit") or data.get("Reddit") or {}

        col1, col2 = st.columns(2)
        with col1:
            st.markdown("#### GITHUB")
            if github_data:
                for k, v in github_data.items():
                    if v is not None:
                        st.markdown(
                            f"<code>{k}</code>&nbsp;&nbsp;"
                            f"<span style='color:#c9d1d9'>{v}</span>",
                            unsafe_allow_html=True,
                        )
            else:
                st.warning("No GitHub data found.")
        with col2:
            st.markdown("#### REDDIT")
            if reddit_data:
                for k, v in reddit_data.items():
                    if v is not None:
                        st.markdown(
                            f"<code>{k}</code>&nbsp;&nbsp;"
                            f"<span style='color:#c9d1d9'>{v}</span>",
                            unsafe_allow_html=True,
                        )
            else:
                st.warning("No Reddit data found.")

        with st.expander("VIEW FULL JSON"):
            st.json(data)
    else:
        st.markdown(PLACEHOLDER, unsafe_allow_html=True)

# ── Tab 3: Network Graph ───────────────────────────────────────
with tab3:
    if st.session_state["errors"].get("graph"):
        st.error(f"Network graph failed: {st.session_state['errors']['graph']}")
    elif st.session_state["graph_html"] or st.session_state["graph_png"]:
        st.markdown(f"### NETWORK GRAPH — `{st.session_state['last_username']}`")
        if st.session_state["graph_html"]:
            st.markdown("#### INTERACTIVE GRAPH")
            with open(st.session_state["graph_html"], "r", encoding="utf-8") as f:
                components.html(f.read(), height=600, scrolling=True)
            with open(st.session_state["graph_html"], "rb") as f:
                st.download_button(
                    "⬇  Download Interactive Graph (HTML)", f,
                    file_name=os.path.basename(st.session_state["graph_html"]),
                    mime="text/html",
                )
        if st.session_state["graph_png"]:
            st.markdown("#### STATIC GRAPH")
            st.image(st.session_state["graph_png"], use_column_width=True)
    else:
        st.markdown(PLACEHOLDER, unsafe_allow_html=True)

# ── Tab 4: Cache Recovery ──────────────────────────────────────
# ── Tab 4: Cache Recovery ──────────────────────────────────────
with tab4:
    if st.session_state["errors"].get("cache"):
        st.error(f"Cache recovery failed: {st.session_state['errors']['cache']}")
    elif st.session_state["cache_results"]:
        data = st.session_state["cache_results"]
        st.markdown(f"### CACHE RECOVERY — `{st.session_state['last_username']}`")

        # Aggregate across all platforms
        total_snapshots = 0
        total_deleted   = 0
        for platform, pdata in data.items():
            if isinstance(pdata, dict):
                total_snapshots += len(pdata.get("snapshot_history", []))
                total_deleted   += len(pdata.get("deleted_content",  []))

        col1, col2 = st.columns(2)
        col1.metric("Snapshots Found",     total_snapshots)
        col2.metric("Deleted Items Found", total_deleted)

        # Render per-platform
        for platform, pdata in data.items():
            if not isinstance(pdata, dict):
                continue
            st.markdown(f"#### {platform.upper()}")

            availability = pdata.get("availability", {})
            if availability:
                ts  = availability.get("timestamp", "—")
                url = availability.get("url", pdata.get("url", "—"))
                st.markdown(
                    f"<code>Latest snapshot</code>&nbsp;&nbsp;"
                    f"<span style='color:#3fb950'>{ts}</span>&nbsp;&nbsp;"
                    f"<a href='{url}' target='_blank' style='color:#58a6ff;font-size:12px;font-family:Share Tech Mono,monospace'>open ↗</a>",
                    unsafe_allow_html=True,
                )

            snapshots = pdata.get("snapshot_history", [])
            if snapshots:
                st.markdown("**Snapshot History**")
                st.json(snapshots)

            deleted = pdata.get("deleted_content", [])
            if deleted:
                st.markdown("**⚠ Deleted / Modified Content**")
                st.json(deleted)

            if not snapshots and not deleted:
                st.info(f"No snapshots or deleted content found for {platform}.")

            st.markdown("---")

        with st.expander("VIEW FULL RAW DATA"):
            st.json(data)
    else:
        st.markdown(PLACEHOLDER, unsafe_allow_html=True)
# ── Tab 5: Report ──────────────────────────────────────────────
with tab5:
    if st.session_state["errors"].get("report"):
        st.error(f"Report generation failed: {st.session_state['errors']['report']}")
    elif st.session_state["report_html"] or st.session_state["report_json"]:
        st.markdown(f"### REPORT — `{st.session_state['last_username']}`")

        if st.session_state["report_html"]:
            st.markdown("#### HTML REPORT PREVIEW")
            with open(st.session_state["report_html"], "r", encoding="utf-8") as f:
                raw_html = f.read()

            # Inject a base tag so all links open in a new tab
            # and a small script to force target=_blank on every anchor
            patched_html = raw_html.replace(
                "<head>",
                """<head>
                <base target="_blank">
                <script>
                document.addEventListener('DOMContentLoaded', function() {
                    document.querySelectorAll('a').forEach(function(a) {
                    a.setAttribute('target', '_blank');
                    a.setAttribute('rel', 'noopener noreferrer');
                    });
                });
                </script>""",
                1  # only replace the first occurrence
            )
        # Fallback if report has no <head> tag
        if "<head>" not in raw_html:
            patched_html = '<base target="_blank">' + raw_html

        components.html(patched_html, height=600, scrolling=True)

        if st.session_state["report_json"]:
            with open(st.session_state["report_json"], "r", encoding="utf-8") as f:
                json_data = json.load(f)
            with st.expander("VIEW JSON REPORT"):
                st.json(json_data)
            with open(st.session_state["report_json"], "rb") as f:
                st.download_button(
                    "⬇  Download JSON Report", f,
                    file_name=os.path.basename(st.session_state["report_json"]),
                    mime="application/json",
                )
    else:
        st.markdown(PLACEHOLDER, unsafe_allow_html=True)

# ── Tab 6: Help ────────────────────────────────────────────────
with tab6:
    st.markdown("### HOW TO USE")
    st.markdown("""
1. Enter a **target username** in the sidebar (e.g. `torvalds`)
2. Select which **modules** to run
3. Click **▶ RUN INVESTIGATION**
4. Switch between tabs freely — results are saved until you run again

### MODULES

| Module | What it does |
|---|---|
| Username Search | Checks GitHub, Reddit, Twitter, Instagram |
| Profile Extraction | Pulls bio, stats, repos from GitHub & Reddit |
| Network Graph | Builds follower/following relationship graph |
| Cache Recovery | Queries Wayback Machine for deleted content |
| Report Generation | Saves HTML + JSON forensic report to `data/reports/` |

### SUPPORTED PLATFORMS

| Platform | Search | Profile | Graph | Cache |
|---|---|---|---|---|
| GitHub | ✅ | ✅ | ✅ | ✅ |
| Reddit | ✅ | ✅ | ✅ | ✅ |
| Twitter | ✅ | — | — | ✅ |
| Instagram | ✅ | — | — | ✅ |
""")