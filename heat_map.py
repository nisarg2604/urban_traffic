import streamlit as st
import pandas as pd
import folium
import random
from folium.plugins import HeatMap
from streamlit_folium import st_folium
from utils.data_loader import load_traffic_data

#Road Coordinates (Real Bengaluru locations)
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

def get_label(level):
    if level >= 75:   return "🔴 High"
    elif level >= 45: return "🟡 Medium"
    else:             return "🟢 Low"

def get_color(level):
    if level >= 75:   return "red"
    elif level >= 45: return "orange"
    else:             return "green"

@st.cache_data
def build_heat_data(area, weather, congestion_filter):
    df = load_traffic_data()

    if area != "All Areas":
        df = df[df["Area Name"] == area]
    if weather != "All Weather":
        df = df[df["Weather Conditions"] == weather]
    if congestion_filter == "🔴 High (≥75)":
        df = df[df["Congestion Level"] >= 75]
    elif congestion_filter == "🟡 Medium (45–74)":
        df = df[(df["Congestion Level"] >= 45) & (df["Congestion Level"] < 75)]
    elif congestion_filter == "🟢 Low (<45)":
        df = df[df["Congestion Level"] < 45]

    # Build heat points with fixed seed so jitter is stable across reruns
    rng = random.Random(42)
    heat_data = []
    for _, row in df.iterrows():
        coords = ROAD_COORDS.get(row["Road/Intersection Name"])
        if not coords:
            continue
        lat, lon = coords
        lat_j = lat + rng.uniform(-0.002, 0.002)
        lon_j = lon + rng.uniform(-0.002, 0.002)
        weight = round(row["Congestion Level"] / 100, 3)
        heat_data.append([lat_j, lon_j, weight])

    # Average per road for pins + table
    avg_cong = (
        df.groupby("Road/Intersection Name")["Congestion Level"]
        .mean().round(1).reset_index()
    )
    avg_cong.columns = ["Road", "Avg Congestion"]

    stats = {
        "total":  len(df),
        "high":   len(df[df["Congestion Level"] >= 75]),
        "medium": len(df[(df["Congestion Level"] >= 45) & (df["Congestion Level"] < 75)]),
        "low":    len(df[df["Congestion Level"] < 45]),
    }

    return heat_data, avg_cong, stats


def heat_map_page():
    st.header("🗺️ Bengaluru Traffic Heat Map")
    st.caption("Congestion intensity built from all 8,936 data records — brighter red = heavier congestion.")
    st.divider()

    df = load_traffic_data()

    #Filters─
    col1, col2, col3 = st.columns(3)
    with col1:
        areas = ["All Areas"] + sorted(df["Area Name"].unique().tolist())
        selected_area = st.selectbox("📍 Filter by Area", areas)
    with col2:
        weather_options = ["All Weather"] + sorted(df["Weather Conditions"].unique().tolist())
        selected_weather = st.selectbox("🌤️ Filter by Weather", weather_options)
    with col3:
        congestion_filter = st.selectbox("🚦 Filter by Congestion Level",
                                         ["All", "🔴 High (≥75)", "🟡 Medium (45–74)", "🟢 Low (<45)"])

    # Load cached data
    heat_data, avg_cong, stats = build_heat_data(selected_area, selected_weather, congestion_filter)

    # Metric Cards
    st.divider()
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("📋 Total Records",  stats["total"])
    c2.metric("🔴 High Records",   stats["high"])
    c3.metric("🟡 Medium Records", stats["medium"])
    c4.metric("🟢 Low Records",    stats["low"])
    st.divider()

    # Map + Table
    map_col, table_col = st.columns([2, 1])

    with map_col:
        m = folium.Map(
            location=[12.9716, 77.5946],
            zoom_start=12,
            tiles="CartoDB dark_matter"
        )

        if heat_data:
            HeatMap(
                heat_data,
                min_opacity=0.3,
                max_opacity=0.95,
                radius=25,
                blur=20,
                max_zoom=14,
                gradient={
                    0.0:  "#0000ff",
                    0.3:  "#00ff00",
                    0.5:  "#ffff00",
                    0.7:  "#ff8800",
                    0.85: "#ff2200",
                    1.0:  "#ff0000",
                }
            ).add_to(m)

        # Road pins
        for _, row in avg_cong.iterrows():
            road  = row["Road"]
            level = row["Avg Congestion"]
            coords = ROAD_COORDS.get(road)
            if not coords:
                continue
            lat, lon = coords
            label = get_label(level)
            color = get_color(level)

            folium.CircleMarker(
                location=[lat, lon],
                radius=6,
                color="white",
                fill=True,
                fill_color=color,
                fill_opacity=1.0,
                weight=2,
                tooltip=folium.Tooltip(
                    f"<div style='font-family:Arial;font-size:13px'>"
                    f"<b>{road}</b><br>"
                    f"Avg Congestion: <b>{level}</b><br>"
                    f"Status: {label}</div>"
                ),
                popup=folium.Popup(
                    f"""
                    <div style='font-family:Arial;min-width:210px;padding:8px'>
                        <h4 style='margin:0 0 8px 0;color:{color}'>🚦 {road}</h4>
                        <table style='width:100%;font-size:12px'>
                            <tr><td><b>Avg Congestion</b></td><td>{level}</td></tr>
                            <tr><td><b>Status</b></td><td>{label}</td></tr>
                            <tr><td><b>Area</b></td><td>{selected_area}</td></tr>
                            <tr><td><b>Weather</b></td><td>{selected_weather}</td></tr>
                        </table>
                    </div>
                    """,
                    max_width=260
                )
            ).add_to(m)

            folium.Marker(
                location=[lat, lon],
                icon=folium.DivIcon(
                    html=(
                        f'<div style="font-size:9px;font-weight:bold;color:white;'
                        f'background:rgba(0,0,0,0.6);padding:2px 5px;border-radius:3px;'
                        f'white-space:nowrap;margin-top:-30px;margin-left:10px">'
                        f'{road}</div>'
                    ),
                    icon_size=(180, 24),
                    icon_anchor=(0, 12)
                )
            ).add_to(m)

        # Legend
        legend_html = """
        <div style="position:fixed;bottom:30px;left:30px;z-index:1000;
                    background:rgba(15,15,15,0.88);padding:14px 18px;border-radius:10px;
                    box-shadow:0 4px 15px rgba(0,0,0,0.6);font-family:Arial;font-size:13px;color:white;">
            <b style="font-size:14px">🌡️ Congestion Heat Scale</b><br><br>
            <div style="display:flex;align-items:center;margin-bottom:8px">
                <div style="width:80px;height:12px;border-radius:6px;margin-right:10px;
                     background:linear-gradient(to right,#0000ff,#00ff00,#ffff00,#ff8800,#ff0000)"></div>
                <span style="font-size:11px">Low → High</span>
            </div>
            <div style="display:flex;align-items:center;margin-bottom:5px">
                <div style="width:14px;height:14px;background:#ff0000;border-radius:3px;margin-right:8px"></div>
                <span>High (≥ 75)</span>
            </div>
            <div style="display:flex;align-items:center;margin-bottom:5px">
                <div style="width:14px;height:14px;background:#ff8800;border-radius:3px;margin-right:8px"></div>
                <span>Medium (45–74)</span>
            </div>
            <div style="display:flex;align-items:center;margin-bottom:5px">
                <div style="width:14px;height:14px;background:#ffff00;border-radius:3px;margin-right:8px"></div>
                <span>Low-Med (30–44)</span>
            </div>
            <div style="display:flex;align-items:center;margin-bottom:8px">
                <div style="width:14px;height:14px;background:#0000ff;border-radius:3px;margin-right:8px"></div>
                <span>Low (< 30)</span>
            </div>
            <span style="font-size:10px;color:#aaa">Built from 8,936 traffic records<br>● Click pin for road details</span>
        </div>
        """
        m.get_root().html.add_child(folium.Element(legend_html))
        st_folium(m, width=None, height=560, use_container_width=True)

    #Table
    with table_col:
        st.subheader("📋 Road-wise Summary")
        st.caption(f"Based on {stats['total']:,} filtered records")

        display = avg_cong.copy()
        display["Status"] = display["Avg Congestion"].apply(get_label)
        display = display.sort_values("Avg Congestion", ascending=False).reset_index(drop=True)
        display.index += 1

        def color_row(val):
            if val >= 75:
                return "background-color:rgba(255,0,0,0.15);color:#e63946;font-weight:600"
            elif val >= 45:
                return "background-color:rgba(255,136,0,0.15);color:orange;font-weight:600"
            else:
                return "background-color:rgba(0,200,0,0.1);color:#28a745;font-weight:600"

        styled = display.style.applymap(color_row, subset=["Avg Congestion"])
        st.dataframe(styled, use_container_width=True, height=520)

    st.divider()

    # Insight Bar
    if not avg_cong.empty:
        worst = avg_cong.loc[avg_cong["Avg Congestion"].idxmax(), "Road"]
        best  = avg_cong.loc[avg_cong["Avg Congestion"].idxmin(), "Road"]
        avg   = round(avg_cong["Avg Congestion"].mean(), 1)
        i1, i2, i3 = st.columns(3)
        i1.error(f"🔴 **Most Congested:** {worst}")
        i2.success(f"🟢 **Least Congested:** {best}")
        i3.info(f"📊 **Overall Avg Congestion:** {avg}")
