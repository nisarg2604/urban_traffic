import streamlit as st
import pandas as pd
from sklearn.preprocessing import LabelEncoder
from utils.data_loader import load_traffic_data

def dataset_page():

    st.title("🗃️ Bangalore Traffic Dataset")
    st.caption("Explore and filter the raw traffic dataset across all 16 roads and 8 areas.")
    st.divider()

    # Load Data
    df = load_traffic_data()

    #Filters
    st.subheader("🔽 Filter Dataset")
    col1, col2, col3 = st.columns(3)

    with col1:
        areas = ["All Areas"] + sorted(df["Area Name"].unique().tolist())
        selected_area = st.selectbox("📍 Area", areas)
    with col2:
        if selected_area != "All Areas":
            roads = ["All Roads"] + sorted(df[df["Area Name"] == selected_area]["Road/Intersection Name"].unique().tolist())
        else:
            roads = ["All Roads"] + sorted(df["Road/Intersection Name"].unique().tolist())
        selected_road = st.selectbox("🛣️ Road", roads)
    with col3:
        weather_options = ["All Weather"] + sorted(df["Weather Conditions"].unique().tolist())
        selected_weather = st.selectbox("🌤️ Weather", weather_options)

    col4, col5, col6 = st.columns(3)
    with col4:
        selected_roadwork = st.selectbox("🚧 Roadwork Activity", ["All", "Yes", "No"])
    with col5:
        congestion_filter = st.selectbox("🚦 Congestion Level", ["All", "🟢 Low (< 45)", "🟡 Medium (45–75)", "🔴 High (> 75)"])

    with col6:
        date_min = df["Date"].min().date()
        date_max = df["Date"].max().date()
        date_range = st.date_input("📅 Date Range", value=(date_min, date_max), min_value=date_min, max_value=date_max)

    # Apply Filters
    filtered = df.copy()

    if selected_area != "All Areas":
        filtered = filtered[filtered["Area Name"] == selected_area]

    if selected_road != "All Roads":
        filtered = filtered[filtered["Road/Intersection Name"] == selected_road]

    if selected_weather != "All Weather":
        filtered = filtered[filtered["Weather Conditions"] == selected_weather]

    if selected_roadwork != "All":
        filtered = filtered[filtered["Roadwork and Construction Activity"] == selected_roadwork]

    if congestion_filter == "🟢 Low (< 45)":
        filtered = filtered[filtered["Congestion Level"] < 45]
    elif congestion_filter == "🟡 Medium (45–75)":
        filtered = filtered[(filtered["Congestion Level"] >= 45) & (filtered["Congestion Level"] <= 75)]
    elif congestion_filter == "🔴 High (> 75)":
        filtered = filtered[filtered["Congestion Level"] > 75]

    if isinstance(date_range, (list, tuple)) and len(date_range) == 2:
        start_date, end_date = date_range
        filtered = filtered[(filtered["Date"].dt.date >= start_date) & (filtered["Date"].dt.date <= end_date)]
    elif isinstance(date_range, (list, tuple)) and len(date_range) == 1:
        filtered = filtered[filtered["Date"].dt.date >= date_range[0]]

    st.divider()

    # ── Dataset Table
    if len(filtered) == 0:
        st.warning("⚠️ No records match the selected filters. Please adjust your filters.")
    else:
        def color_congestion(val):
            if val > 75:
                return "background-color: rgba(230,57,70,0.2); color: #e63946; font-weight:600"
            elif val >= 45:
                return "background-color: rgba(255,165,0,0.2); color: orange; font-weight:600"
            else:
                return "background-color: rgba(40,167,69,0.2); color: #28a745; font-weight:600"

        display_df = filtered.reset_index(drop=True)
        display_df.index += 1

        styled = display_df.style.applymap(color_congestion, subset=["Congestion Level"])
        st.dataframe(styled, use_container_width=True, height=500)

        st.divider()

        # ── Filtered Metric Cards
        r1, r2, r3, r4 = st.columns(4)
        r1.metric("📋 Filtered Records",  f"{len(filtered):,}")
        r2.metric("📊 Avg Congestion",    f"{filtered['Congestion Level'].mean():.1f}")
        r3.metric("🚗 Avg Speed",         f"{filtered['Average Speed'].mean():.1f} km/h")
        r4.metric("⚠️ Total Incidents",   f"{int(filtered['Incident Reports'].sum())}")

        st.divider()

        # Download dataset
        csv = filtered.to_csv(index=False).encode("utf-8")
        st.download_button(
            label="⬇️ Download Filtered Dataset as CSV",
            data=csv,
            file_name="bangalore_traffic_filtered.csv",
            mime="text/csv",
            use_container_width=True,
            type="primary"
        )
    st.divider()

    # Encode
    check  = st.checkbox("Show Encoded Data")

    if check:
        label_transformer = LabelEncoder()

        df["Area Name"] = label_transformer.fit_transform(df["Area Name"])
        df["Road/Intersection Name"] = label_transformer.fit_transform(df["Road/Intersection Name"])
        df["Weather Conditions"] = label_transformer.fit_transform(df["Weather Conditions"])
        df["Roadwork and Construction Activity"] = label_transformer.fit_transform(df["Roadwork and Construction Activity"])
        display_df = df.reset_index(drop=True)
        display_df.index += 1
        st.dataframe(display_df)
        encode_csv = display_df.to_csv(index=False).encode("utf-8")
        st.download_button(
            label="⬇️ Download Filtered Dataset as CSV",
            data=encode_csv,
            file_name="Encoded_bangalore_traffic_filtered.csv",
            mime="text/csv",
            use_container_width=True,
            type="primary"
        )