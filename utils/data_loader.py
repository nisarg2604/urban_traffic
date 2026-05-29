import pandas as pd
import streamlit as st
import os

CHAT_FILE = "chat_history.csv"

@st.cache_data
def load_traffic_data():
    df = pd.read_csv("Bangalore_traffic_Dataset.csv")
    df["Date"] = pd.to_datetime(df["Date"], format='mixed', errors='coerce')
    df['Month'] = df['Date'].dt.month
    df['DayOfWeek'] = df['Date'].dt.dayofweek
    df['Day'] = df['Date'].dt.day
    return df

def load_users():
    """Load users from st.secrets instead of user.csv"""
    users = st.secrets.get("users", {})
    rows = []
    for username, data in users.items():
        rows.append({
            "Username": username,
            "Password": data["password"],
            "Role": data["role"]
        })
    return pd.DataFrame(rows)

def save_user(new_user):
    """Signup disabled on cloud - users managed via secrets"""
    st.warning("⚠️ New registrations are managed by the administrator on this hosted version.")

def save_new_password(username, email, hashed_password):
    """Password reset disabled on cloud"""
    st.warning("⚠️ Password reset is not available on the hosted version. Contact the administrator.")

def load_chat_history(username):
    if not os.path.exists(CHAT_FILE):
        pd.DataFrame(columns=["Username", "Role", "Content"]).to_csv(CHAT_FILE, index=False)
    df = pd.read_csv(CHAT_FILE)
    user_chats = df[df["Username"] == username]
    messages = []
    for index, row in user_chats.iterrows():
        messages.append({"role": row["Role"], "content": row["Content"]})
    return messages

def save_chat_message(username, role, content):
    if not os.path.exists(CHAT_FILE):
        pd.DataFrame(columns=["Username", "Role", "Content"]).to_csv(CHAT_FILE, index=False)
    df = pd.read_csv(CHAT_FILE)
    new_message = {"Username": username, "Role": role, "Content": content}
    df = pd.concat([df, pd.DataFrame([new_message])], ignore_index=True)
    df.to_csv(CHAT_FILE, index=False)
