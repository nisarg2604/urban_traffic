import streamlit as st

def about_page():
    st.header("About This Project")
    st.divider()

    #Project Overview
    st.subheader("Project Overview")
    st.write("""
    The **AI-Driven Urban Traffic Congestion Prediction and Mobility Optimization System** is an 
    intelligent traffic analytics platform developed for **Bengaluru**, one of India's most 
    traffic-congested cities. The system leverages historical traffic data and machine learning 
    to predict congestion levels and support smarter mobility decisions for both city authorities 
    and daily commuters.
    """)
    st.divider()

    # Problem Statement
    st.subheader("Problem Statement")
    st.write("""
    Bengaluru faces severe urban traffic congestion, leading to increased travel times, fuel 
    wastage, air pollution, and reduced productivity. Traditional traffic management systems 
    rely on manual monitoring and reactive measures, which are insufficient for a rapidly 
    growing metropolitan city. There is a critical need for a data-driven, predictive system 
    that can forecast congestion before it occurs and assist planners and commuters in making 
    informed decisions.
    """)
    st.divider()

    # Objectives
    st.subheader("Objectives")
    objectives = [
        "Collect and integrate historical traffic data including accident reports, weather conditions, and road network information.",
        "Analyze traffic flow patterns, peak hours, and recurring congestion zones using Exploratory Data Analysis.",
        "Develop machine learning and time-series models to predict congestion levels — Low, Medium, and High.",
        "Generate congestion forecasts and predictive alerts for congestion-prone areas.",
        "Provide interactive dashboards and heat maps for predictive monitoring and trend analysis.",
        "Support proactive traffic signal optimization, route planning, and urban mobility decisions.",
        "Enhance overall traffic flow efficiency, reduce delays, and improve urban transportation planning.",
    ]
    for obj in objectives:
        st.markdown(f"{obj}")
    st.divider()

    # Dataset
    st.subheader("Dataset")
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Records", "8,936")
    col2.metric("Roads Covered", "16")
    col3.metric("Areas Covered", "8")
    col4.metric("Time Period", "Jan 2022 – Sep 2023")

    st.write("""
    The system uses the **Bangalore City Traffic Dataset** sourced from Kaggle. It contains 
    16 columns of traffic data including congestion level, average speed, traffic volume, 
    weather conditions, incident reports, and road work activity across 16 major roads in 
    8 Bengaluru areas.
    """)

    st.divider()

    # Key Features
    st.subheader("Key Features")

    col_a, col_b = st.columns(2)

    with col_a:
        st.markdown("**🏛️ Government Role**")
        gov_features = [
            "Real-time metric dashboard with congestion analytics",
            "Interactive Folium heat map across all 16 roads",
            "Alert Zone for high-congestion road warnings",
            "Dataset Explorer with dynamic filters and CSV export",
            "Infrastructure Recommendation engine",
            "Six Plotly charts — area-wise, weather impact, incident tracking",
        ]
        for f in gov_features:
            st.markdown(f"- {f}")

    with col_b:
        st.markdown("**👤 User (Commuter) Role**")
        user_features = [
            "Live traffic status overview",
            "Route Finder based on predicted congestion",
            "Map View of current road conditions",
            "Area-wise congestion summary",
        ]
        for f in user_features:
            st.markdown(f"- {f}")

        st.markdown("**Common Features**")
        common_features = [
            "View-only Profile page",
            "Settings — edit profile, change password, theme",
            "SHA-256 hashed authentication with role-based routing",
        ]
        for f in common_features:
            st.markdown(f"- {f}")

    st.divider()

    #Tools & Technologies
    st.subheader("Tools & Technologies")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("**Frontend**")
        st.markdown("""
        - Streamlit
        - Plotly
        - Folium
        - Matplotlib 
        """)

    with col2:
        st.markdown("**Backend & Data**")
        st.markdown("""
        - Python 3.x
        - Pandas & NumPy
        - Scikit-learn
        - CSV (file-based storage)
        """)

    with col3:
        st.markdown("**ML & Analytics**")
        st.markdown("""
        - Random Forest / Decision Tree
        - Time-Series Forecasting
        - Exploratory Data Analysis
        - Feature Engineering
        """)

    st.divider()

    # System Architecture
    st.subheader("System Architecture")
    st.write("""
    The system follows a **modular monolithic architecture** built entirely in Python using Streamlit. 
    Each functional module (Heat Map, Dashboard, Alert Zone, Dataset, etc.) is an independent Python 
    file stored in the `modules/` directory, imported dynamically via `main.py` based on the 
    authenticated user's role and sidebar selection.
    """)

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("""
        **Project Structure**
```
        project/
        ├── main.py
        ├── utils/
        │   ├── data_loader.py
        │   └── auth.py
        ├── modules/
        │   ├── home.py
        │   ├── heat_map.py
        │   ├── alert_zone.py
        │   ├── dataset_page.py
        │   ├── profile.py
        │   └── settings.py
        └── data/
            ├── Bangalore_traffic_Dataset.csv
            └── users.csv
```
        """)
    with col2:
        st.markdown("""
        **Data Flow**
```
        User Login
             ↓
        Role Detection (Government / User)
             ↓
        Sidebar Navigation
             ↓
        Module Loaded Dynamically
             ↓
        data_loader.py (cached CSV read)
             ↓
        Analytics / Prediction / Visualization
             ↓
        Rendered in Streamlit UI
```
        """)

    st.divider()

    # Development Team
    st.subheader("Development Team")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("""
        | Detail | Info |
        |--------|------|
        | **Student** | Nisarg Mayankkumar Patel |
        | **Enrollment No.** | 230673107027 |
        | **Guide** | Ms. Komal Thummar |
        | **Department** | Computer Engineering |
        | **Institute** | SAL Institute of Technology and Engineering Research |
        """)
    with col2:
        st.markdown("""
        | Detail | Info |
        |--------|------|
        | **Company** | InfoLabz IT Services Pvt. Ltd. |
        | **Location** | Navrangpura, Ahmedabad |
        | **Domain** | AI & Machine Learning |
        | **Project Type** | Final Year Project |
        | **Academic Year** | 2024 – 2025 |
        """)

    st.divider()

    # References
    st.subheader("References")
    st.markdown("""
    - [Bangalore City Traffic Dataset – Kaggle](https://www.kaggle.com/datasets/preethamgouda/banglore-city-traffic-dataset)
    - [TomTom Traffic Index – Global Rankings](https://www.tomtom.com/traffic-index/ranking/)
    - [Karnataka Traffic Congestion Map](https://btp.karnataka.gov.in/188/congestion-map/en)
    - [Scikit-Learn Documentation](https://scikit-learn.org/stable/user_guide.html)
    - [Streamlit Documentation](https://docs.streamlit.io/)
    - [Folium Documentation](https://python-visualization.github.io/folium/)
    - [UCI Metro Interstate Traffic Volume Dataset](https://archive.ics.uci.edu/ml/datasets/Metro+Interstate+Traffic+Volume)
    """)

    st.divider()
    st.caption("AI-Driven Urban Traffic Congestion Prediction and Mobility Optimization System · SAL Institute of Technology · 2024–2025")