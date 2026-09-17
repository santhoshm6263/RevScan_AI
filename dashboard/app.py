"""Streamlit Dashboard for RevScan AI (Spec 10, Spec 11 - Member 4)."""
import json
import streamlit as st
from dashboard.components import (
    api_client,
    inject_styles,
    render_header,
    render_status_badge,
    render_metric_card
)

# Page configuration
st.set_page_config(
    page_title="RevScan AI - Autonomous Android Explorer",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Inject styling
inject_styles()

# Sidebar Navigation
st.sidebar.title("⚡ RevScan AI")
st.sidebar.caption("App Exploration & Knowledge Pack")

nav_page = st.sidebar.radio(
    "Navigation",
    ["Dashboard", "App Map", "Screens", "Knowledge Pack"],
    index=0
)

# -------------------------------------------------------------
# 10.1 Dashboard Page
# -------------------------------------------------------------
if nav_page == "Dashboard":
    render_header(title="Dashboard", subtitle="Autonomous Android application exploration control center")

    status_data = api_client.get_status()
    pack_data = api_client.get_knowledge_pack()
    current_status = status_data.get("status", "idle")

    # Control Panel
    with st.container():
        st.markdown('<div class="content-card">', unsafe_allow_html=True)
        st.subheader("Target Application & Scan Control")

        col1, col2 = st.columns([3, 1])
        with col1:
            package_name = st.text_input(
                "Target Android Package Name",
                value="com.example.demo",
                placeholder="e.g. com.android.settings or com.example.app",
                help="Enter the package name of the Android app running on the emulator."
            )
        with col2:
            st.markdown("<br>", unsafe_allow_html=True)
            status_html = render_status_badge(current_status)
            st.markdown(f"**Scan Status:** {status_html}", unsafe_allow_html=True)

        btn_col1, btn_col2, _ = st.columns([2, 2, 4])
        with btn_col1:
            if st.button("START AUTONOMOUS SCAN", type="primary", use_container_width=True, disabled=(current_status == "running")):
                if api_client.start_scan(package_name):
                    st.success(f"Started autonomous scan for {package_name}")
                    st.rerun()
                else:
                    st.error("Failed to start scan. Ensure FastAPI backend is running.")

        with btn_col2:
            if st.button("STOP SCAN", use_container_width=True, disabled=(current_status != "running")):
                if api_client.stop_scan():
                    st.warning("Stopped scan.")
                    st.rerun()
                else:
                    st.error("Failed to stop scan.")

        st.markdown('</div>', unsafe_allow_html=True)

    # Exploration Metrics (Spec 10.1)
    st.subheader("Exploration Overview")
    m_col1, m_col2, m_col3, m_col4 = st.columns(4)

    with m_col1:
        render_metric_card("Discovered Screens", status_data.get("screens_found", 0))
    with m_col2:
        render_metric_card("Elements Found", pack_data.get("scan", {}).get("elements_found", 0))
    with m_col3:
        render_metric_card("Journeys", len(pack_data.get("journeys", [])))
    with m_col4:
        render_metric_card("Actions Executed", status_data.get("actions_executed", 0))

# -------------------------------------------------------------
# 10.2 App Map Page
# -------------------------------------------------------------
elif nav_page == "App Map":
    render_header(title="App Map", subtitle="Discovered application screen hierarchy and transition paths")

    pack_data = api_client.get_knowledge_pack()
    transitions = pack_data.get("transitions", [])
    screens = pack_data.get("screens", [])

    st.markdown('<div class="content-card">', unsafe_allow_html=True)
    st.subheader("Visual Screen Hierarchy")

    if not transitions and not screens:
        st.info("No screen transitions discovered yet. Start a scan to build the App Map.")
        # Render demonstration hierarchy as per spec
        st.markdown("```text\nLogin\n  ↓\nHome ├── Products\n     │     ↓\n     │   Details\n     └── Profile\n```")
    else:
        st.markdown("#### Discovered Screen Transitions")
        for t in transitions:
            from_s = t.get("from", "Unknown")
            action = t.get("action", "action")
            to_s = t.get("to", "Unknown")
            st.markdown(f"- **{from_s}** ──`[{action}]`──▶ **{to_s}**")

    st.markdown('</div>', unsafe_allow_html=True)

# -------------------------------------------------------------
# 10.3 Screens Page
# -------------------------------------------------------------
elif nav_page == "Screens":
    render_header(title="Screens", subtitle="Discovered screens, interactive elements, and details")

    screens_list = api_client.get_screens()
    pack_data = api_client.get_knowledge_pack()
    pack_screens = {s.get("id"): s for s in pack_data.get("screens", [])}

    if not screens_list and not pack_screens:
        st.info("No screens discovered yet. Launch an autonomous scan from the Dashboard.")
    else:
        col_list, col_detail = st.columns([1, 2])

        all_screen_ids = list(pack_screens.keys()) if pack_screens else [s["id"] for s in screens_list]
        selected_id = col_list.radio(
            "Select Screen",
            all_screen_ids,
            format_func=lambda sid: f"{sid} ({pack_screens.get(sid, {}).get('name', 'Screen')})"
        )

        with col_detail:
            selected_screen = pack_screens.get(selected_id) or api_client.get_screen(selected_id)
            if selected_screen:
                st.markdown('<div class="content-card">', unsafe_allow_html=True)
                st.subheader(f"{selected_screen.get('name', 'Screen')} (`{selected_screen.get('id')}`)")
                st.write(f"**Purpose:** {selected_screen.get('purpose', 'N/A')}")

                screenshot_path = selected_screen.get("screenshot")
                if screenshot_path:
                    st.image(screenshot_path, caption=f"Screen: {selected_screen.get('name')}", use_container_width=True)

                st.markdown("#### Elements")
                elems = selected_screen.get("elements", [])
                if elems:
                    st.dataframe(elems, use_container_width=True)
                else:
                    st.caption("No elements recorded for this screen.")

                st.markdown("#### Next Screens")
                next_s = selected_screen.get("next_screens", [])
                if next_s:
                    st.write(", ".join(next_s))
                else:
                    st.caption("No outward transitions discovered.")

                st.markdown('</div>', unsafe_allow_html=True)

# -------------------------------------------------------------
# 10.4 Knowledge Pack Page
# -------------------------------------------------------------
elif nav_page == "Knowledge Pack":
    render_header(title="Knowledge Pack", subtitle="Compact, structured, AI-readable application representation")

    pack_data = api_client.get_knowledge_pack()

    col1, col2, col3 = st.columns(3)
    with col1:
        render_metric_card("Screen Count", pack_data.get("scan", {}).get("screens_found", 0))
    with col2:
        render_metric_card("Element Count", pack_data.get("scan", {}).get("elements_found", 0))
    with col3:
        render_metric_card("Journey Count", len(pack_data.get("journeys", [])))

    st.markdown('<div class="content-card">', unsafe_allow_html=True)
    st.subheader("Knowledge Pack JSON Preview")

    json_str = json.dumps(pack_data, indent=2)
    st.download_button(
        label="Download Knowledge Pack (JSON)",
        data=json_str,
        file_name="knowledge-pack.json",
        mime="application/json",
        type="primary"
    )

    st.json(pack_data)
    st.markdown('</div>', unsafe_allow_html=True)
