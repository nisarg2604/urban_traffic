import streamlit as st
from datetime import datetime

def homepage():
    
    now = datetime.now()
    f_time = now.strftime("%H:%M")
    f_date = now.strftime("%d %B %Y")

    col_h, col_t = st.columns([3.5, 0.5])
    with col_h:
        st.title("Urban Traffic Congestion Prediction System")
        st.caption("Bangalore City Mobility Optimization")
    with col_t:
        st.markdown(f"""
                <div style='text-align:right; padding-top:10px;'>
                    <div style='font-size:28px; font-weight:700;'>{f_time}</div>
                    <div style='font-size:13px; color:#888;'>{f_date}</div>
                </div>
            """, unsafe_allow_html=True)
    st.divider()

    st.write("""
            ### Welcome to the Urban Traffic Platform
            This platform leverages machine learning and data analytics 
            to solve urban traffic congestion challenges in Bangalore. 
    
            **System Objectives:**
            - **Commuter Intelligence:** Providing citizens with route advisory and real-time traffic awareness.
            - **Infrastructural Planning:** Equipping authorities with diagnostic tools for data-driven decisions.
    
            **Core Intelligence Modules:**
            - **Traffic Assistant:** Conversational AI for location-specific traffic inquiries.
            - **Predictive Engine:** Forecasting traffic volume and congestion levels.
            - **Infrastructure Optimizer:** AI recommendations for flyovers, underpasses, and expansions.
            """)

    st.info("Navigation: Use the sidebar to access platform modules based on your authorized role.")