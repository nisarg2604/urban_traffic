import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
from utils.data_loader import load_traffic_data

# ── Road Coordinates ───────────────────────────────────────────────────────────
ROAD_COORDS = {
    "100 Feet Road":            (12.9784, 77.6408),
    "CMH Road":                 (12.9698, 77.6400),
    "Marathahalli Bridge":      (12.9591, 77.7014),
    "Sony World Junction":      (12.9352, 77.6245),
    "Sarjapur Road":            (12.9180, 77.6770),
    "Trinity Circle":           (12.9762, 77.6033),
    "Anil Kumble Circle":       (12.9774, 77.5950),
    "Jayanagar 4th Block":      (12.9258, 77.5833),
    "South End Circle":         (12.9315, 77.5757),
    "Hebbal Flyover":           (13.0450, 77.5970),
    "Ballari Road":             (13.0350, 77.5900),
    "Yeshwanthpur Circle":      (13.0275, 77.5540),
    "Tumkur Road":              (13.0200, 77.5350),
    "ITPL Main Road":           (12.9857, 77.7272),
    "Silk Board Junction":      (12.9170, 77.6226),
    "Hosur Road":               (12.8990, 77.6350),
}

def get_color(level):
    if level >= 75:   return "#e63946"
    elif level >= 45: return "#f4a261"
    else:             return "#2a9d8f"

def get_status(level):
    if level >= 75:   return "🔴 Avoid"
    elif level >= 45: return "🟡 Caution"
    else:             return "🟢 Safe"

def get_radius(level):
    if level >= 75:   return 14
    elif level >= 45: return 11
    else:             return 9


def map_page():
    st.header("🗺️ Bengaluru Road Map")
    st.caption("Check current road conditions before you travel — click any marker for details.")
    st.divider()

    df = load_traffic_data()

    # ── Filters ────────────────────────────────────────────────────────────────
    col1, col2 = st.columns(2)
    with col1:
        areas = ["All Areas"] + sorted(df["Area Name"].unique().tolist())
        selected_area = st.selectbox("📍 Filter by Area", areas)
    with col2:
        status_filter = st.selectbox(
            "🚦 Show Roads",
            ["All Roads", "🟢 Safe Roads Only", "🟡 Caution Roads", "🔴 Avoid Roads"]
        )

    # ── Filter data ────────────────────────────────────────────────────────────
    filtered = df.copy()
    if selected_area != "All Areas":
        filtered = filtered[filtered["Area Name"] == selected_area]

    avg_cong = (
        filtered.groupby("Road/Intersection Name")
        .agg(
            Avg_Congestion=("Congestion Level",  "mean"),
            Avg_Speed     =("Average Speed",      "mean"),
            Total_Incidents=("Incident Reports",  "sum"),
            Area          =("Area Name",          "first")
        )
        .round(1)
        .reset_index()
    )
    avg_cong.columns = ["Road", "Avg Congestion", "Avg Speed", "Total Incidents", "Area"]

    if status_filter == "🟢 Safe Roads Only":
        avg_cong = avg_cong[avg_cong["Avg Congestion"] < 45]
    elif status_filter == "🟡 Caution Roads":
        avg_cong = avg_cong[
            (avg_cong["Avg Congestion"] >= 45) &
            (avg_cong["Avg Congestion"] < 75)
        ]
    elif status_filter == "🔴 Avoid Roads":
        avg_cong = avg_cong[avg_cong["Avg Congestion"] >= 75]

    # ── Metric Cards ───────────────────────────────────────────────────────────
    safe    = len(avg_cong[avg_cong["Avg Congestion"] < 45])
    caution = len(avg_cong[(avg_cong["Avg Congestion"] >= 45) & (avg_cong["Avg Congestion"] < 75)])
    avoid   = len(avg_cong[avg_cong["Avg Congestion"] >= 75])

    c1, c2, c3 = st.columns(3)
    c1.metric("🟢 Safe to Travel",       safe)
    c2.metric("🟡 Travel with Caution",  caution)
    c3.metric("🔴 Avoid These Roads",    avoid)
    st.divider()

    # ── Map + Table ────────────────────────────────────────────────────────────
    map_col, table_col = st.columns([2, 1])

    with map_col:
        m = folium.Map(
            location=[12.9716, 77.5946],
            zoom_start=12,
            tiles="CartoDB positron"
        )

        for _, row in avg_cong.iterrows():
            road      = row["Road"]
            level     = row["Avg Congestion"]
            speed     = row["Avg Speed"]
            incidents = row["Total Incidents"]
            area      = row["Area"]
            coords    = ROAD_COORDS.get(road)
            if not coords:
                continue

            lat, lon = coords
            color    = get_color(level)
            status   = get_status(level)
            radius   = get_radius(level)

            folium.CircleMarker(
                location=[lat, lon],
                radius=radius,
                color=color,
                fill=True,
                fill_color=color,
                fill_opacity=0.85,
                weight=2,
                tooltip=folium.Tooltip(
                    f"<div style='font-family:Arial;font-size:13px'>"
                    f"<b>{road}</b><br>"
                    f"Status: {status}<br>"
                    f"Congestion: <b>{level}</b>"
                    f"</div>"
                ),
                popup=folium.Popup(
                    f"""
                    <div style='font-family:Arial;min-width:220px;padding:8px'>
                        <h4 style='margin:0 0 8px 0;color:{color}'>{road}</h4>
                        <table style='width:100%;font-size:12px;border-collapse:collapse'>
                            <tr style='border-bottom:1px solid #eee'>
                                <td style='padding:4px'><b>Status</b></td>
                                <td style='padding:4px'>{status}</td>
                            </tr>
                            <tr style='border-bottom:1px solid #eee'>
                                <td style='padding:4px'><b>Congestion</b></td>
                                <td style='padding:4px'>{level} / 100</td>
                            </tr>
                            <tr style='border-bottom:1px solid #eee'>
                                <td style='padding:4px'><b>Avg Speed</b></td>
                                <td style='padding:4px'>{speed} km/h</td>
                            </tr>
                            <tr style='border-bottom:1px solid #eee'>
                                <td style='padding:4px'><b>Area</b></td>
                                <td style='padding:4px'>{area}</td>
                            </tr>
                            <tr>
                                <td style='padding:4px'><b>Incidents</b></td>
                                <td style='padding:4px'>{int(incidents)}</td>
                            </tr>
                        </table>
                    </div>
                    """,
                    max_width=280
                )
            ).add_to(m)

            folium.Marker(
                location=[lat, lon],
                icon=folium.DivIcon(
                    html=(
                        f'<div style="font-size:9px;font-weight:bold;color:#333;'
                        f'background:rgba(255,255,255,0.75);padding:2px 4px;'
                        f'border-radius:3px;white-space:nowrap;'
                        f'margin-top:-28px;margin-left:10px">'
                        f'{road}</div>'
                    ),
                    icon_size=(180, 20),
                    icon_anchor=(0, 10)
                )
            ).add_to(m)

        # ── Legend — dark background, white text ───────────────────────────────
        legend_html = """
        <div style="position:fixed; bottom:30px; right:30px; z-index:1000;
                    background:rgba(20,20,20,0.88); padding:14px 18px; border-radius:10px;
                    box-shadow:0 4px 15px rgba(0,0,0,0.5);
                    font-family:Arial; font-size:13px; color:white;">
            <b style="font-size:14px">🚦 Road Status</b><br><br>
            <div style="display:flex;align-items:center;margin-bottom:7px">
                <div style="width:14px;height:14px;background:#2a9d8f;
                     border-radius:50%;margin-right:10px;flex-shrink:0"></div>
                <span>Safe to Travel (&lt; 45)</span>
            </div>
            <div style="display:flex;align-items:center;margin-bottom:7px">
                <div style="width:14px;height:14px;background:#f4a261;
                     border-radius:50%;margin-right:10px;flex-shrink:0"></div>
                <span>Caution (45 – 74)</span>
            </div>
            <div style="display:flex;align-items:center;margin-bottom:10px">
                <div style="width:14px;height:14px;background:#e63946;
                     border-radius:50%;margin-right:10px;flex-shrink:0"></div>
                <span>Avoid (&#x2265; 75)</span>
            </div>
            
        </div>
        """
        m.get_root().html.add_child(folium.Element(legend_html))

        st_folium(m, width=None, height=530, use_container_width=True)

    # ── Road Status Table ──────────────────────────────────────────────────────
    with table_col:
        st.subheader("📋 Road Status")

        display = avg_cong.copy()
        display["Status"] = display["Avg Congestion"].apply(get_status)
        display = (
            display[["Road", "Avg Congestion", "Avg Speed", "Status"]]
            .sort_values("Avg Congestion", ascending=False)
            .reset_index(drop=True)
        )
        display.index += 1

        def color_status(val):
            if "Avoid" in str(val):
                return "color:#e63946;font-weight:600"
            elif "Caution" in str(val):
                return "color:#f4a261;font-weight:600"
            else:
                return "color:#2a9d8f;font-weight:600"

        styled = display.style.map(color_status, subset=["Status"])
        st.dataframe(styled, use_container_width=True, height=500)

    st.divider()

    # ── Travel Recommendation ──────────────────────────────────────────────────
    if not avg_cong.empty:
        best  = avg_cong.loc[avg_cong["Avg Congestion"].idxmin()]
        worst = avg_cong.loc[avg_cong["Avg Congestion"].idxmax()]

        r1, r2 = st.columns(2)
        r1.success(
            f"✅ **Best Road to Take**\n\n"
            f"**{best['Road']}**\n\n"
            f"Congestion: {best['Avg Congestion']} | "
            f"Speed: {best['Avg Speed']} km/h"
        )
        r2.error(
            f"🚫 **Road to Avoid**\n\n"
            f"**{worst['Road']}**\n\n"
            f"Congestion: {worst['Avg Congestion']} | "
            f"Speed: {worst['Avg Speed']} km/h"
        )
