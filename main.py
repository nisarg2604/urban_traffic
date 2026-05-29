import streamlit as st
from streamlit_option_menu import option_menu
import pandas as pd
import time
import os
import re
import hashlib
import joblib
from utils.data_loader import load_users, save_user, save_new_password, load_traffic_data
import plotly.express as px
import numpy as np

# Page config
st.set_page_config(
    page_title="Bengaluru Traffic System",
    page_icon="🚦",
    layout="wide"
)

# ================== FILE CONFIG ==================
DATASET_FILE = "Bangalore_traffic_Dataset.csv"
MODEL_FILE = "traffic_model.joblib"
ENCODERS_FILE = "encoders.joblib"
SCALER_FILE = "scaler.joblib"
FILE_NAME = "user.csv"

#Create CSV if missing
if not os.path.exists(FILE_NAME):
    pd.DataFrame(columns=[
        "First Name", "Last Name", "Email", "Phone",
        "Username", "Password", "Role"
    ]).to_csv(FILE_NAME, index=False)

#Session state defaults
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = ""
if "role" not in st.session_state:
    st.session_state.role = ""

# Restore session from query params on refresh
# This runs BEFORE current_page is read so state is correct when routing
if "user" in st.query_params and not st.session_state.logged_in:
    df = load_users()
    matched = df[df["Username"] == st.query_params["user"]]
    if not matched.empty:
        st.session_state.logged_in = True
        st.session_state.username  = st.query_params["user"]
        st.session_state.role      = matched.iloc[0]["Role"]

# Read current page AFTER session is restored
if "page" not in st.query_params:
    st.query_params["page"] = "Login"

current_page = st.query_params["page"]

#Password hashing
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

#SIGNUP PAGE
def signup_page():
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.title("🚦 Sign Up")
        st.caption("Create your account to access the Bengaluru Traffic System")
        st.divider()

        df = load_users()
        with st.form(key="signup"):
            col_a, col_b = st.columns(2)
            with col_a:
                first_name = st.text_input("First Name")
            with col_b:
                last_name = st.text_input("Last Name")

            email    = st.text_input("Email")
            phone    = st.text_input("Phone Number")
            username = st.text_input("Username")

            col_c, col_d = st.columns(2)
            with col_c:
                password    = st.text_input("Password", type="password")
            with col_d:
                re_password = st.text_input("Re-Password", type="password")

            role   = st.selectbox("Select Role", ["Government", "User"],
                                  index=None, placeholder="Choose your role...")
            submit = st.form_submit_button("Register", use_container_width=True,
                                           type="primary")

        if st.button("Already Registered? Go to Login", use_container_width=True):
            st.query_params["page"] = "Login"
            st.rerun()

        if submit:
            if not first_name or not last_name or not email or not username \
                    or not password or not re_password or not role:
                st.error("⚠️ Please fill all fields")
            elif not re.match(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$", email):
                st.error("⚠️ Invalid email format")
            elif not re.match(r"^\d{10}$", phone):
                st.error("⚠️ Phone number must be exactly 10 digits")
            elif password != re_password:
                st.error("⚠️ Passwords do not match")
            elif len(password) < 8:
                st.error("⚠️ Password must be at least 8 characters")
            elif not re.search(r"[A-Z]", password):
                st.error("⚠️ Password must contain at least one uppercase letter")
            elif not re.search(r"[!@#$%^&*]", password):
                st.error("⚠️ Password must contain at least one special character (!@#$%^&*)")
            elif not re.search(r"[0-9]", password):
                st.error("⚠️ Password must contain at least one number")
            elif username in df["Username"].values:
                st.error("⚠️ Username already exists")
            elif email in df["Email"].values:
                st.error("⚠️ Email already registered")
            else:
                save_user({
                    "First Name": first_name,
                    "Last Name":  last_name,
                    "Email":      email,
                    "Phone":      phone,
                    "Username":   username,
                    "Password":   hash_password(password),
                    "Role":       role
                })
                st.success("✅ Registered successfully! Redirecting to login...")
                time.sleep(1)
                st.query_params["page"] = "Login"
                st.rerun()

#LOGIN PAGE
def login_page():
    col1, col2, col3 = st.columns([1, 1.5, 1])
    with col2:
        st.title("🚦 Bengaluru Traffic System")
        st.caption("AI-Driven Urban Traffic Congestion Prediction")
        st.divider()

        st.title("Login")
        username = st.text_input("Username", placeholder="Enter your username")
        password = st.text_input("Password", type="password",
                                 placeholder="Enter your password")
        role     = st.selectbox("Select Role", ["Government", "User"],
                                index=None, placeholder="Select your role...")

        if st.button("Login", use_container_width=True, type="primary"):
            if not username or not password or not role:
                st.error("⚠️ Please fill all fields")
            else:
                df   = load_users()
                user = df[
                    (df["Username"] == username) &
                    (df["Password"] == hash_password(password)) &
                    (df["Role"]     == role)
                ]
                if not user.empty:
                    st.session_state.logged_in = True
                    st.session_state.username  = username
                    st.session_state.role      = role
                    st.query_params["page"]    = "Home"
                    st.query_params["user"]    = username
                    st.rerun()
                else:
                    st.error("❌ Invalid credentials. Please check username, password and role.")

        st.divider()
        col1, col2 = st.columns(2)
        with col1:
            if st.button("New User? Register Here", use_container_width=True):
                st.query_params["page"] = "SignUp"
                st.rerun()
        with col2:
            if st.button("Forget Password?", use_container_width=True):
                st.query_params["page"] = "Forget"
                st.rerun()

# forget password
def forget_password():
    col1, col2, col3 = st.columns([1, 1.5, 1])
    with col2:
        st.title("🚦 Bengaluru Traffic System")
        st.caption("AI-Driven Urban Traffic Congestion Prediction")
        st.divider()
        st.title("Forgot Password")
        df = load_users()

        username = st.text_input("Username", placeholder="Enter your username")
        email = st.text_input("Email", placeholder="Enter your email")
        new_password = st.text_input("New Password", type="password")
        re_password = st.text_input("Confirm Password", type="password")

        if st.button("Reset Password", type="primary", use_container_width=True):
            if not all([username, email, new_password, re_password]):
                st.error("⚠️ All fields are required")
            elif username not in df["Username"].values:
                st.error("⚠️ Username does not exist")
            elif email not in df["Email"].values:
                st.error("⚠️ Email does not exist")
            elif new_password != re_password:
                st.error("⚠️ Passwords do not match")
            elif len(new_password) < 8:
                st.error("⚠️ Password must be at least 8 characters")
            elif not re.search(r"[A-Z]", new_password):
                st.error("⚠️ Password must contain at least one capital letter")
            elif not re.search(r"[0-9]", new_password):
                st.error("⚠️ Password must contain at least one digit")
            elif not re.search(r"[!@#$%^&*]", new_password):
                st.error("⚠️ Password must contain at least one special character")
            else:
                save_new_password(username, email, hash_password(new_password))
                st.success("✅ Password reset successful! Redirecting to login...")
                time.sleep(1)
                st.query_params["page"] = "Login"
                st.rerun()

        st.divider()
        if st.button("Back to Login", use_container_width=True):
            st.query_params["page"] = "Login"
            st.rerun()

#GOVERNMENT DASHBOARD
def government_dashboard():
    gov_page = ["Home","Dashboard","About", "Dataset", "Heat Map", "Chatbot",
             "Prediction Model", "Infrastructure Recommendation", "Alert Zone",
             "Profile", "Settings", "Logout"]
    gov_icons = ["house-fill","kanban","info-circle-fill", "database-fill", "map-fill", "robot",
                "graph-up-arrow", "building-fill", "bell-fill",
                "person-fill", "gear-fill", "box-arrow-right"
            ]
    default_idx = gov_page.index(current_page) if current_page in gov_page else 0
    with st.sidebar:
        select = option_menu(
            "🚦 Menu",
            options=gov_page,
            icons= gov_icons,
            menu_icon="🚦",
            default_index=default_idx,
            styles={"nav-link-selected": {"background-color": "#e63946"}}
        )
        st.divider()
        st.caption(f"👤 {st.session_state.username}")
        st.caption("🏛️ Role: Government")
    if select !=  current_page:
        st.query_params["page"] = select
        st.rerun()
    if select == "Home":
        from modules.home_page import homepage
        homepage()
    elif select == "Dashboard":
        from modules.dashboard import dashboard
        dashboard()
    elif select == "About":
        from modules.about import about_page
        about_page()
    elif select == "Dataset":
        from modules.dataset import dataset_page
        dataset_page()
    elif select == "Heat Map":
        from modules.heat_map import heat_map_page
        heat_map_page()
    elif select == "Chatbot":
        # st.title("🤖 Traffic Chatbot")
        # st.info("Chatbot module coming soon!")
        from modules.chatbot import chatbot_page
        chatbot_page()
    elif select == "Prediction Model":
        # st.title("📈 Congestion Prediction Model")
        # st.info("Prediction module coming soon!")
        st.title("🔮 Predictive Intelligence")
        st.caption("Machine Learning-Based Traffic Congestion Forecasting")

        # Check if model exists
        if not os.path.exists(MODEL_FILE):
            st.warning("Model not trained yet. Training model...")
            from modules.prediction_model import train_model
            train_model()
            st.success("Model trained successfully!")
            st.rerun()

        # Load model
        model = joblib.load(MODEL_FILE)
        encoders = joblib.load(ENCODERS_FILE)
        scaler = joblib.load(SCALER_FILE)

        traffic_df = load_traffic_data()

        st.subheader("Enter Traffic Parameters")

        col1, col2 = st.columns(2)

        with col1:
            area_name = st.selectbox("Area Name", encoders['Area Name'].classes_)
            road_name = st.selectbox("Road/Intersection", encoders['Road/Intersection Name'].classes_)
            weather = st.selectbox("Weather Conditions", encoders['Weather Conditions'].classes_)
            roadwork = st.selectbox("Roadwork Activity", encoders['Roadwork and Construction Activity'].classes_)

        with col2:
            traffic_volume = st.number_input("Traffic Volume", min_value=0, max_value=10000, value=5000)
            avg_speed = st.number_input("Average Speed (km/h)", min_value=0.0, max_value=100.0, value=30.0)
            travel_time_index = st.number_input("Travel Time Index", min_value=0.0, max_value=5.0, value=1.5)
            road_capacity = st.number_input("Road Capacity Utilization (%)", min_value=0.0, max_value=100.0, value=70.0)

        col3, col4 = st.columns(2)

        with col3:
            incidents = st.number_input("Incident Reports", min_value=0, max_value=50, value=0)
            env_impact = st.number_input("Environmental Impact", min_value=0.0, max_value=100.0, value=50.0)
            public_transport = st.number_input("Public Transport Usage (%)", min_value=0.0, max_value=100.0, value=30.0)

        with col4:
            signal_compliance = st.number_input("Signal Compliance (%)", min_value=0.0, max_value=100.0, value=80.0)
            parking_usage = st.number_input("Parking Usage (%)", min_value=0.0, max_value=100.0, value=50.0)
            pedestrian_count = st.number_input("Pedestrian Count", min_value=0, max_value=5000, value=500)

        day = st.slider("Day of Month", 1, 31, 15)
        month = st.slider("Month", 1, 12, 6)
        day_of_week = st.slider("Day of Week (0=Mon, 6=Sun)", 0, 6, 2)

        if st.button("Predict Congestion", type="primary"):
            # Encode inputs
            area_encoded = encoders['Area Name'].transform([area_name])[0]
            road_encoded = encoders['Road/Intersection Name'].transform([road_name])[0]
            weather_encoded = encoders['Weather Conditions'].transform([weather])[0]
            roadwork_encoded = encoders['Roadwork and Construction Activity'].transform([roadwork])[0]

            features = np.array([[
                area_encoded, road_encoded,
                traffic_volume, avg_speed, travel_time_index, road_capacity,
                incidents, env_impact, public_transport, signal_compliance,
                parking_usage, pedestrian_count, weather_encoded, roadwork_encoded,
                day, month, day_of_week
            ]])

            features_scaled = scaler.transform(features)
            prediction = model.predict(features_scaled)
            probability = model.predict_proba(features_scaled)[0]

            congestion_level = encoders['target'].inverse_transform(prediction)[0]

            st.divider()
            st.subheader("Prediction Result")

            col1, col2, col3 = st.columns(3)

            # Color based on congestion level
            if congestion_level == "Low":
                color = "green"
            elif congestion_level == "Medium":
                color = "orange"
            else:
                color = "red"

            with col1:
                st.metric("Predicted Congestion", congestion_level)
            with col2:
                st.metric("Confidence", f"{max(probability) * 100:.1f}%")
            with col3:
                st.metric("Risk Level", "High" if congestion_level == "High" else "Normal")

            # Probability breakdown
            st.write("**Probability Distribution:**")
            prob_df = pd.DataFrame({
                'Level': encoders['target'].classes_,
                'Probability': probability
            })
            fig = px.bar(prob_df, x='Level', y='Probability', color='Level',
                         color_discrete_map={'Low': 'green', 'Medium': 'orange', 'High': 'red'})
            st.plotly_chart(fig, use_container_width=True)

    elif select == "Infrastructure Recommendation":
        from modules.infrastructure import infrastructure_page
        infrastructure_page()
    elif select == "Alert Zone":
        # st.title("🔔 Alert Zones")
        # st.info("Alert module coming soon!")
        from modules.alert_zone import alert_zone
        alert_zone()
    elif select == "Profile":
        from modules.profile import profile_page
        profile_page()
    elif select == "Settings":
        from modules.setting import settings_page
        settings_page()
    elif select == "Logout":
        st.session_state.logged_in = False
        st.session_state.username  = ""
        st.session_state.role      = ""
        if "messages" in st.session_state:
            del st.session_state["messages"]
        st.query_params.clear()
        st.query_params["page"] = "Login"
        st.rerun()

#USER DASHBOARD
def user_dashboard():
    user_page = ["Home", "About", "Chatbot", "Route Finder", "Map",
             "Profile", "Settings", "Logout"]
    user_icons = ["house-fill", "info-circle-fill", "robot",
                "signpost-split-fill", "map-fill",
                "person-fill", "gear-fill", "box-arrow-right"]
    default_idx = user_page.index(current_page) if current_page in user_page else 0
    with st.sidebar:
        selected = option_menu(
            "🚦 Menu",
             options = user_page,
            icons=user_icons,
            menu_icon="🚦",
            default_index= default_idx,
            styles={"nav-link-selected": {"background-color": "#2a9d8f"}}
        )
        st.divider()
        st.caption(f"👤 {st.session_state.username}")
        st.caption("🙋 Role: User")

    if selected != current_page:
        st.query_params["page"] = selected
        st.rerun()

    if selected == "Home":
        from modules.home_page import homepage
        homepage()
    elif selected == "About":
        from modules.about import about_page
        about_page()
    elif selected == "Chatbot":
        from modules.chatbot import chatbot_page
        chatbot_page()
    elif selected == "Route Finder":
        # st.title("🛣️ Route Finder")
        # st.info("Enter source and destination to find the best route. (Coming soon)")
        st.title("🚶 Travel Advisory")
        st.caption("Route Optimization and Mobility Guidance for Citizens")

        traffic_df = load_traffic_data()
        if traffic_df is not None:

            st.header("🗺️ Journey Planning")

            col1, col2 = st.columns(2)
            with col1:
                start_location = st.selectbox("Start Location", traffic_df['Area Name'].unique())
            with col2:
                end_location = st.selectbox("Destination", traffic_df['Area Name'].unique())

            col3, col4 = st.columns(2)
            with col3:
                travel_date = st.date_input("Travel Date")
            with col4:
                travel_time = st.time_input("Travel Time")

            weather_condition = st.selectbox("Expected Weather", traffic_df['Weather Conditions'].unique())

            if st.button("Plan Journey", type="primary"):
                st.divider()

                # ---- Auto-render Map & Route (Single Submit Rule) ----
                from modules.user_route import geocode_location, get_route, get_route_info, create_route_map
                from streamlit_folium import st_folium

                with st.spinner("Calculating optimal route..."):
                    start_coords = geocode_location(start_location)
                    end_coords = geocode_location(end_location)

                    if start_coords and end_coords:
                        route_coords = get_route(start_coords, end_coords)
                        route_info = get_route_info(start_coords, end_coords)

                        if route_info:
                            # 1️⃣ ROUTE SUMMARY (ABOVE MAP)
                            col1, col2, col3 = st.columns(3)
                            with col1:
                                st.metric("Distance", f"{route_info['distance_km']} km")
                            with col2:
                                st.metric("Duration", f"{int(route_info['duration_min'])} min")
                            with col3:
                                st.metric("Avg Speed",
                                          f"{route_info['distance_km'] / (route_info['duration_min'] / 60):.0f} km/h")

                        # 2️⃣ INTERACTIVE MAP (MIDDLE)
                        route_map = create_route_map(
                            start_coords, end_coords, route_coords,
                            start_location, end_location
                        )
                        st_folium(route_map, width=None, height=450, returned_objects=[])
                    else:
                        st.error("Unable to calculate route for the selected locations. Please try nearby landmarks.")

                st.divider()

                # Get congestion data for start and end for AI Advisory
                start_data = traffic_df[traffic_df['Area Name'] == start_location]
                end_data = traffic_df[traffic_df['Area Name'] == end_location]

                # Calculate congestion levels
                start_congestion = start_data['Congestion Level'].mean()
                end_congestion = end_data['Congestion Level'].mean()
                route_congestion = (start_congestion + end_congestion) / 2

                # Determine congestion category
                if route_congestion > 70:
                    congestion_cat = "High Congestion"
                    congestion_color = "red"
                elif route_congestion > 40:
                    congestion_cat = "Medium Congestion"
                    congestion_color = "orange"
                else:
                    congestion_cat = "Low Congestion"
                    congestion_color = "green"

                # Display prediction
                st.subheader("Route Analysis")

                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Congestion Level", congestion_cat)
                with col2:
                    avg_speed = start_data['Average Speed'].mean()
                    est_time = 30 + (route_congestion / 5)  # Simplified estimate
                    st.metric("Est. Travel Time", f"{est_time:.0f} mins")
                with col3:
                    delay = max(0, (route_congestion - 50) / 3)
                    st.metric("Expected Delay", f"{delay:.0f} mins")

                st.divider()

                # Reason for prediction
                st.subheader("Why This Prediction?")

                day_of_week = travel_date.weekday()
                day_names = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']

                reasons = []
                if day_of_week < 5:
                    reasons.append(
                        f"- **Weekday ({day_names[day_of_week]})**: Higher traffic expected during work hours")
                else:
                    reasons.append(f"- **Weekend ({day_names[day_of_week]})**: Generally lower traffic")

                hour = travel_time.hour
                if 8 <= hour <= 10 or 17 <= hour <= 20:
                    reasons.append("- **Peak Hours**: Rush hour traffic expected")
                else:
                    reasons.append("- **Off-Peak Hours**: Lower traffic expected")

                weather_impact = traffic_df[traffic_df['Weather Conditions'] == weather_condition][
                    'Congestion Level'].mean()
                if weather_impact > 75:
                    reasons.append(f"- **Weather ({weather_condition})**: Increases congestion significantly")

                if start_data['Incident Reports'].sum() > start_data['Incident Reports'].mean() * 1.5:
                    reasons.append(f"- **{start_location}**: History of incidents in this area")

                for reason in reasons:
                    st.write(reason)

                st.divider()

                # Alternate Routes
                st.subheader("Alternate Routes")

                # Get areas sorted by congestion
                all_areas = traffic_df.groupby('Area Name')['Congestion Level'].mean().sort_values()

                # Find alternate routes through less congested areas
                alternate_areas = [a for a in all_areas.index if a not in [start_location, end_location]][:3]

                for i, alt_area in enumerate(alternate_areas, 1):
                    alt_congestion = all_areas[alt_area]
                    if alt_congestion > 70:
                        alt_cat = "High"
                        alt_color = "FAILED"
                    elif alt_congestion > 40:
                        alt_cat = "Medium"
                        alt_color = "WARNING"
                    else:
                        alt_cat = "Low"
                        alt_color = "success"

                    with st.container(border=True):
                        st.write(f"**Route {i}**: {start_location} â†’ {alt_area} â†’ {end_location}")
                        st.write(f"Congestion: **{alt_cat}** ({alt_congestion:.1f}%)")
                        if i == 1 and alt_congestion < route_congestion:
                            st.success("RECOMMENDED - Best Route")

                st.divider()

                # Smart AI Tips
                st.subheader("Smart Travel Tips")

                tips = []

                # Best time to travel
                day_data = traffic_df[traffic_df['DayOfWeek'] == day_of_week]['Congestion Level']
                if day_data.mean() > 70:
                    tips.append("**Best Time**: Consider traveling before 7 AM or after 8 PM to avoid peak congestion")
                else:
                    tips.append("**Best Time**: Traffic is generally manageable throughout the day")

                # Fuel efficiency
                if route_congestion > 60:
                    tips.append(
                        "**Fuel Saving**: High congestion increases fuel consumption. Consider public transport")
                else:
                    tips.append("**Fuel Saving**: Maintain steady speed for optimal fuel efficiency")

                # Eco-friendly
                public_transport = traffic_df['Public Transport Usage'].mean()
                if public_transport > 30:
                    tips.append("**Eco-Friendly**: Good public transport availability in this route")

                # Safety
                if start_data['Incident Reports'].sum() > 10:
                    tips.append("**Safety**: Stay alert - higher incident reports in this area")

                for tip in tips:
                    st.info(tip)
    elif selected == "Map":
        from modules.user_map import map_page
        map_page()
    elif selected == "Profile":
        from modules.profile import profile_page
        profile_page()
    elif selected == "Settings":
        from modules.setting import settings_page
        settings_page()
    elif selected == "Logout":
        st.session_state.logged_in = False
        st.session_state.username  = ""
        st.session_state.role      = ""
        if "messages" in st.session_state:
            del st.session_state["messages"]
        st.query_params.clear()
        st.query_params["page"] = "Login"
        st.rerun()

# HOME PAGE ROUTER
def home_page_router():
    if st.session_state.role == "Government":
        government_dashboard()
    elif st.session_state.role == "User":
        user_dashboard()
    else:
        st.session_state.logged_in = False
        st.query_params.clear()
        st.query_params["page"] = "Login"
        st.rerun()

#MAIN PAGE ROUTER
if current_page == "Login":
    if st.session_state.logged_in:
        home_page_router()
    else:
        login_page()
elif current_page == "SignUp":
    signup_page()
elif current_page == "Forget":
    forget_password()
else:
    if st.session_state.logged_in:
        home_page_router()
    else:
        st.query_params["page"] = "Login"
        st.rerun()