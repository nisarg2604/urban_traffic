import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
from utils.data_loader import load_traffic_data
from streamlit_autorefresh import st_autorefresh

def dashboard():
    df = load_traffic_data()
    st_autorefresh(interval=30000, key="clock_refresh")

    # Header
    now    = datetime.now()
    f_time = now.strftime("%H:%M")
    f_date = now.strftime("%d %B %Y")

    col_h, col_t = st.columns([3, 1])
    with col_h:
        st.header("🏛️ Traffic Control Center")
        st.caption("Government Dashboard — Bengaluru City Traffic Overview")
    with col_t:
        st.markdown(f"""
            <div style='text-align:right; padding-top:10px;'>
                <div style='font-size:28px; font-weight:700;'>{f_time}</div>
                <div style='font-size:13px; color:#888;'>{f_date}</div>
            </div>
        """, unsafe_allow_html=True)
    st.divider()

    #Metric Cards
    avg_per_road     = df.groupby("Road/Intersection Name")["Congestion Level"].mean().reset_index()
    high_congestion  = avg_per_road[avg_per_road["Congestion Level"] > 75]["Road/Intersection Name"].nunique()
    avg_speed        = round(df["Average Speed"].mean(), 2)
    total_incidents  = int(df["Incident Reports"].sum())
    total_roads      = df["Road/Intersection Name"].nunique()

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("🛣️ Roads Monitored",     total_roads,     "Active")
    c2.metric("🔴 High Congestion Roads", high_congestion, "Active")
    c3.metric("🚗 Average Speed",         f"{avg_speed} km/h", "Active")
    c4.metric("🚑 Total Incidents",        total_incidents, "Recorded")

    st.divider()

    #Top 5 Congested Roads + Congestion by Area
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("🔴 Top 5 Most Congested Roads")
        top5 = avg_per_road.sort_values("Congestion Level", ascending=False).head(5)
        top5.columns = ["Road", "Avg Congestion"]

        fig1 = px.bar(
            top5,
            x="Avg Congestion",
            y="Road",
            orientation="h",
            color="Avg Congestion",
            color_continuous_scale=["#f4a261", "#e63946"],
            text=top5["Avg Congestion"].round(1)
        )
        fig1.update_traces(textposition="outside")
        fig1.update_layout(
            height=320,
            showlegend=False,
            coloraxis_showscale=False,
            margin=dict(l=0, r=20, t=10, b=0),
            yaxis=dict(autorange="reversed"),
            xaxis_title="Avg Congestion Level",
            yaxis_title=""
        )
        st.plotly_chart(fig1, use_container_width=True)

    with col2:
        st.subheader("📍 Congestion by Area")
        area_avg = df.groupby("Area Name")["Congestion Level"].mean().reset_index()
        area_avg.columns = ["Area", "Avg Congestion"]
        area_avg = area_avg.sort_values("Avg Congestion", ascending=False)

        fig2 = px.bar(
            area_avg,
            x="Area",
            y="Avg Congestion",
            color="Avg Congestion",
            color_continuous_scale=["#2a9d8f", "#e63946"],
            text=area_avg["Avg Congestion"].round(1)
        )
        fig2.update_traces(textposition="outside")
        fig2.update_layout(
            height=320,
            showlegend=False,
            coloraxis_showscale=False,
            margin=dict(l=0, r=10, t=10, b=0),
            xaxis_title="",
            yaxis_title="Avg Congestion Level",
            xaxis_tickangle=-30
        )
        st.plotly_chart(fig2, use_container_width=True)

    st.divider()

    #Row 2: Congestion Distribution Pie + Weather Impact
    col3, col4 = st.columns(2)

    with col3:
        st.subheader("🚦 Congestion Level Distribution")

        def classify(val):
            if val < 45:   return "🟢 Low"
            elif val <= 75: return "🟡 Medium"
            else:           return "🔴 High"

        df["Category"] = df["Congestion Level"].apply(classify)
        dist = df["Category"].value_counts().reset_index()
        dist.columns = ["Category", "Count"]

        fig3 = px.pie(
            dist,
            names="Category",
            values="Count",
            color="Category",
            color_discrete_map={
                "🟢 Low"    : "#2a9d8f",
                "🟡 Medium" : "#f4a261",
                "🔴 High"   : "#e63946"
            },
            hole=0.45
        )
        fig3.update_traces(textposition="inside", textinfo="percent+label")
        fig3.update_layout(
            height=320,
            showlegend=True,
            margin=dict(l=0, r=0, t=10, b=0)
        )
        st.plotly_chart(fig3, use_container_width=True)

    with col4:
        st.subheader("🌤️ Weather Impact on Congestion")
        weather_avg = df.groupby("Weather Conditions")["Congestion Level"].mean().reset_index()
        weather_avg.columns = ["Weather", "Avg Congestion"]
        weather_avg = weather_avg.sort_values("Avg Congestion", ascending=False)

        fig4 = px.bar(
            weather_avg,
            x="Weather",
            y="Avg Congestion",
            color="Avg Congestion",
            color_continuous_scale=["#2a9d8f", "#e63946"],
            text=weather_avg["Avg Congestion"].round(1)
        )
        fig4.update_traces(textposition="outside")
        fig4.update_layout(
            height=320,
            showlegend=False,
            coloraxis_showscale=False,
            margin=dict(l=0, r=10, t=10, b=0),
            xaxis_title="",
            yaxis_title="Avg Congestion Level"
        )
        st.plotly_chart(fig4, use_container_width=True)

    st.divider()

    #Monthly Trend + Traffic Volume by Road
    col5, col6 = st.columns(2)

    with col5:
        st.subheader("📈 Monthly Congestion Trend")
        df["Month"] = df["Date"].dt.to_period("M").astype(str)
        monthly = df.groupby("Month")["Congestion Level"].mean().reset_index()
        monthly.columns = ["Month", "Avg Congestion"]

        fig5 = px.line(
            monthly,
            x="Month",
            y="Avg Congestion",
            markers=True,
            line_shape="spline",
            color_discrete_sequence=["#e63946"]
        )
        fig5.update_layout(
            height=300,
            margin=dict(l=0, r=10, t=10, b=0),
            xaxis_title="",
            yaxis_title="Avg Congestion Level",
            xaxis_tickangle=-45
        )
        fig5.update_traces(line_width=2.5, marker_size=5)
        st.plotly_chart(fig5, use_container_width=True)

    with col6:
        st.subheader("🚗 Traffic Volume by Road")
        vol_by_road = df.groupby("Road/Intersection Name")["Traffic Volume"].mean().reset_index()
        vol_by_road.columns = ["Road", "Avg Volume"]
        vol_by_road = vol_by_road.sort_values("Avg Volume", ascending=False).head(8)

        fig6 = px.bar(
            vol_by_road,
            x="Avg Volume",
            y="Road",
            orientation="h",
            color="Avg Volume",
            color_continuous_scale=["#2a9d8f", "#1d3557"],
            text=vol_by_road["Avg Volume"].round(0)
        )
        fig6.update_traces(textposition="outside")
        fig6.update_layout(
            height=300,
            showlegend=False,
            coloraxis_showscale=False,
            margin=dict(l=0, r=20, t=10, b=0),
            yaxis=dict(autorange="reversed"),
            xaxis_title="Avg Traffic Volume",
            yaxis_title=""
        )
        st.plotly_chart(fig6, use_container_width=True)

    st.divider()

    #Recent Data Table
    st.subheader("📋 Recent Records")
    st.caption("Latest 10 entries from the dataset")

    recent = df.sort_values("Date", ascending=False).head(10).reset_index(drop=True)
    recent.index += 1

    def color_congestion(val):
        if val > 75:
            return "background-color: rgba(230,57,70,0.2); color:#e63946; font-weight:600"
        elif val >= 45:
            return "background-color: rgba(244,162,97,0.2); color:orange; font-weight:600"
        else:
            return "background-color: rgba(42,157,143,0.2); color:#2a9d8f; font-weight:600"

    display_cols = ["Date", "Area Name", "Road/Intersection Name",
                    "Traffic Volume", "Average Speed", "Congestion Level",
                    "Weather Conditions", "Incident Reports"]

    styled = recent[display_cols].style.map(color_congestion, subset=["Congestion Level"])
    st.dataframe(styled, use_container_width=True)
