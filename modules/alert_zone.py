import streamlit as st
import plotly.express as px
from utils.data_loader import load_traffic_data

def alert_zone():
    st.title("⚠️ System Alerts")
    st.caption("Critical Notifications and Mitigation Recommendations")

    traffic_df = load_traffic_data()
    if traffic_df is not None:

        # High congestion zones
        st.subheader("High Congestion Zones (Historical)")
        high_congestion = traffic_df[traffic_df['Congestion Level'] > 80].groupby(
            ['Area Name', 'Road/Intersection Name']
        ).agg({
            'Congestion Level': 'mean',
            'Traffic Volume': 'mean',
            'Incident Reports': 'sum'
        }).round(2).sort_values('Congestion Level', ascending=False).head(10)

        if not high_congestion.empty:
            st.dataframe(high_congestion, use_container_width=True)

        st.divider()

        # Recommendations
        st.subheader("Mobility Recommendations")

        # Best travel times
        col1, col2 = st.columns(2)

        with col1:
            st.write("**Best Days to Travel:**")
            day_names = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
            best_days = traffic_df.groupby('DayOfWeek')['Congestion Level'].mean().sort_values().head(3)
            for idx, (day_idx, congestion) in enumerate(best_days.items(), 1):
                st.write(f"{idx}. {day_names[day_idx]} (Avg Congestion: {congestion:.1f}%)")

        with col2:
            st.write("**Least Congested Areas:**")
            best_areas = traffic_df.groupby('Area Name')['Congestion Level'].mean().sort_values().head(3)
            for idx, (area, congestion) in enumerate(best_areas.items(), 1):
                st.write(f"{idx}. {area} (Avg Congestion: {congestion:.1f}%)")

        st.divider()

        # Weather advisories
        st.subheader("Weather Impact Advisory")
        weather_impact = traffic_df.groupby('Weather Conditions')['Congestion Level'].mean().sort_values(
            ascending=False)

        worst_weather = weather_impact.idxmax()
        best_weather = weather_impact.idxmin()

        st.info(f"**Highest congestion during:** {worst_weather} weather ({weather_impact[worst_weather]:.1f}% avg)")
        st.success(f"**Lowest congestion during:** {best_weather} weather ({weather_impact[best_weather]:.1f}% avg)")

        # Incident hotspots
        st.divider()
        st.subheader("Incident Hotspots")
        incident_hotspots = traffic_df.groupby('Area Name')['Incident Reports'].sum().sort_values(ascending=False)

        fig = px.pie(values=incident_hotspots.values, names=incident_hotspots.index,
                     title='Incident Distribution by Area')
        st.plotly_chart(fig, use_container_width=True)
