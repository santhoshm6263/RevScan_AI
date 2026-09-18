"""Streamlit Dashboard for RevScan AI (Spec 10, Spec 11 - Member 4).
Supports arbitrary custom apps, Google Play Store apps, and Microsoft Store apps with live resolution.
"""
import json
import time
import streamlit as st
from dashboard.components import (
    api_client,
    inject_styles,
    render_header,
    render_status_badge,
    render_metric_card,
    render_store_app_card,
    generate_graphviz_dot
)

# Page configuration
st.set_page_config(
    page_title="RevScan AI - Autonomous App Explorer",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Inject styling and contrast fixes
inject_styles()

# Sidebar Navigation
st.sidebar.title("⚡ RevScan AI")
st.sidebar.caption("Autonomous App Knowledge Generator")

nav_page = st.sidebar.radio(
    "Navigation",
    ["Dashboard", "App Map", "Screens", "Knowledge Pack"],
    index=0
)

# Auto-refresh status
status_data = api_client.get_status()
current_status = status_data.get("status", "idle")

if current_status == "running":
    st.sidebar.info("🔄 Scan in progress... Auto-refreshing status.")
    time.sleep(1)
    st.rerun()

# -------------------------------------------------------------
# 10.1 Dashboard Page
# -------------------------------------------------------------
if nav_page == "Dashboard":
    render_header(
        title="Dashboard",
        subtitle="Autonomous Android & Multi-Platform Application Exploration Control Center"
    )

    pack_data = api_client.get_knowledge_pack()
    presets = api_client.get_presets()

    # Control Panel
    with st.container():
        st.markdown('<div class="content-card">', unsafe_allow_html=True)
        st.subheader("Select or Input Target Application")

        tab_play, tab_ms, tab_custom = st.tabs([
            "📱 Google Play Store App",
            "🪟 Microsoft Store App",
            "⚙️ Custom Local / APK App"
        ])

        target_package = ""
        target_platform = "android"
        target_name = ""

        # Tab 1: Google Play Store
        with tab_play:
            st.write("Explore Android applications from Google Play Store using real store metadata and UI structures.")
            col_preset, col_input = st.columns([1, 1])

            with col_preset:
                play_options = ["Custom Input / URL"] + [
                    f"{p['name']} ({p['package']})" for p in presets.get("play_store", [])
                ]
                selected_play_preset = st.selectbox("Popular Play Store Apps", play_options, key="play_preset_select")

            with col_input:
                if selected_play_preset == "Custom Input / URL":
                    play_input = st.text_input(
                        "Play Store URL or Package ID",
                        value="com.spotify.music",
                        placeholder="e.g. com.whatsapp or https://play.google.com/store/apps/details?id=...",
                        key="play_custom_input"
                    )
                else:
                    # Extract package ID from preset string
                    pkg_id = selected_play_preset.split("(")[-1].rstrip(")")
                    play_input = pkg_id

            if play_input:
                target_package = play_input
                target_platform = "android"

        # Tab 2: Microsoft Store
        with tab_ms:
            st.write("Explore Windows desktop and UWP applications from Microsoft Store.")
            col_ms_preset, col_ms_input = st.columns([1, 1])

            with col_ms_preset:
                ms_options = ["Custom Input / URL"] + [
                    f"{p['name']} ({p['package']})" for p in presets.get("ms_store", [])
                ]
                selected_ms_preset = st.selectbox("Popular Windows Apps", ms_options, key="ms_preset_select")

            with col_ms_input:
                if selected_ms_preset == "Custom Input / URL":
                    ms_input = st.text_input(
                        "Microsoft Store URL or Product ID",
                        value="9N0DX20HK701",
                        placeholder="e.g. 9WZDNCRFJ3Q8 or https://apps.microsoft.com/detail/...",
                        key="ms_custom_input"
                    )
                else:
                    pkg_id = selected_ms_preset.split("(")[-1].rstrip(")")
                    ms_input = pkg_id

            if ms_input and tab_ms:
                # If user switched tab or chose MS store
                pass

        # Tab 3: Custom Local App
        with tab_custom:
            st.write("Explore arbitrary local Android applications or running test packages.")
            custom_input = st.text_input(
                "Local Android Package Name",
                value="com.example.demo",
                placeholder="e.g. com.example.myapp",
                key="custom_app_input"
            )

        # Resolve active app
        active_query = target_package or "com.example.demo"
        if tab_ms and 'ms_input' in locals() and ms_input and selected_ms_preset != "Custom Input / URL":
            active_query = ms_input
            target_platform = "windows"
        elif tab_custom and 'custom_input' in locals() and custom_input and custom_input != "com.example.demo":
            active_query = custom_input
            target_platform = "custom"

        resolved_app = api_client.resolve_app(active_query, platform=target_platform)

        # Render Rich Store Preview Card
        st.markdown("#### App Profile & Metadata")
        render_store_app_card(resolved_app)

        # Action Buttons
        col_btn1, col_btn2, col_status = st.columns([2, 2, 3])
        with col_btn1:
            if st.button(
                "🚀 START AUTONOMOUS SCAN",
                type="primary",
                use_container_width=True,
                disabled=(current_status == "running")
            ):
                if api_client.start_scan(
                    package_name=resolved_app.get("package", active_query),
                    platform=resolved_app.get("platform", target_platform),
                    app_name=resolved_app.get("name")
                ):
                    st.success(f"Started autonomous scan for {resolved_app.get('name')}")
                    time.sleep(0.5)
                    st.rerun()
                else:
                    st.error("Failed to start scan. Ensure FastAPI backend is running.")

        with col_btn2:
            if st.button(
                "⏹️ STOP SCAN",
                use_container_width=True,
                disabled=(current_status != "running")
            ):
                if api_client.stop_scan():
                    st.warning("Stopped scan.")
                    time.sleep(0.5)
                    st.rerun()
                else:
                    st.error("Failed to stop scan.")

        with col_status:
            status_html = render_status_badge(current_status)
            st.markdown(f"<div style='margin-top:0.4rem;'><strong>Scan Status:</strong> {status_html}</div>", unsafe_allow_html=True)

        st.markdown('</div>', unsafe_allow_html=True)

    # Exploration Metrics (Spec 10.1)
    st.subheader("Exploration Overview")
    m_col1, m_col2, m_col3, m_col4 = st.columns(4)

    screens_found = status_data.get("screens_found", len(pack_data.get("screens", [])))
    elements_found = pack_data.get("scan", {}).get("elements_found", sum(len(s.get("elements", [])) for s in pack_data.get("screens", [])))
    journeys_count = len(pack_data.get("journeys", []))
    actions_executed = status_data.get("actions_executed", pack_data.get("scan", {}).get("steps", 0))

    with m_col1:
        render_metric_card("Discovered Screens", screens_found)
    with m_col2:
        render_metric_card("Elements Found", elements_found)
    with m_col3:
        render_metric_card("User Journeys", journeys_count)
    with m_col4:
        render_metric_card("Actions Executed", actions_executed)

# -------------------------------------------------------------
# 10.2 App Map Page
# -------------------------------------------------------------
elif nav_page == "App Map":
    render_header(title="App Map", subtitle="Discovered application screen hierarchy and transition paths")

    pack_data = api_client.get_knowledge_pack()
    transitions = pack_data.get("transitions", [])
    screens = pack_data.get("screens", [])

    st.markdown('<div class="content-card">', unsafe_allow_html=True)
    st.subheader("Visual Screen Hierarchy & Graph")

    dot_string = generate_graphviz_dot(transitions, screens)
    st.graphviz_chart(dot_string, use_container_width=True)

    if not transitions and not screens:
        st.info("Showing sample exploration graph above. Launch an autonomous scan from the Dashboard to build your live App Map.")

    st.markdown('</div>', unsafe_allow_html=True)

    if transitions:
        st.markdown('<div class="content-card">', unsafe_allow_html=True)
        st.subheader("Discovered Screen Transitions")
        trans_table = [
            {
                "From Screen": t.get("from", "Unknown"),
                "Action Taken": t.get("action", "action"),
                "To Screen": t.get("to", "Unknown")
            }
            for t in transitions
        ]
        st.dataframe(trans_table, use_container_width=True)
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
                    img_url = api_client.get_screenshot_url(screenshot_path)
                    if img_url:
                        st.image(img_url, caption=f"Screen Screenshot: {selected_screen.get('name')}", use_container_width=True)

                st.markdown("#### Interactive Elements")
                elems = selected_screen.get("elements", [])
                if elems:
                    st.dataframe(elems, use_container_width=True)
                else:
                    st.caption("No elements recorded for this screen.")

                st.markdown("#### Next Screens & Outward Transitions")
                next_s = selected_screen.get("next_screens", [])
                if next_s:
                    st.write(", ".join([f"`{ns}`" for ns in next_s]))
                else:
                    st.caption("No outward transitions discovered yet.")

                st.markdown('</div>', unsafe_allow_html=True)

# -------------------------------------------------------------
# 10.4 Knowledge Pack Page
# -------------------------------------------------------------
elif nav_page == "Knowledge Pack":
    render_header(title="Knowledge Pack", subtitle="Compact, structured, AI-readable application representation")

    pack_data = api_client.get_knowledge_pack()

    col1, col2, col3 = st.columns(3)
    with col1:
        render_metric_card("Screen Count", pack_data.get("scan", {}).get("screens_found", len(pack_data.get("screens", []))))
    with col2:
        render_metric_card("Element Count", pack_data.get("scan", {}).get("elements_found", 0))
    with col3:
        render_metric_card("Journey Count", len(pack_data.get("journeys", [])))

    st.markdown('<div class="content-card">', unsafe_allow_html=True)
    st.subheader("Knowledge Pack JSON Preview")

    json_str = json.dumps(pack_data, indent=2)
    st.download_button(
        label="📥 Download Knowledge Pack (JSON)",
        data=json_str,
        file_name="knowledge-pack.json",
        mime="application/json",
        type="primary"
    )

    st.json(pack_data)
    st.markdown('</div>', unsafe_allow_html=True)
