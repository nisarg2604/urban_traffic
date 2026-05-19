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

@st.cache_data
def load_users():
    df = pd.read_csv("user.csv")
    return df

def save_user(new_user):
    df = pd.read_csv("user.csv")
    df = pd.concat([df, pd.DataFrame([new_user])], ignore_index=True)
    df.to_csv("user.csv", index=False)
    st.cache_data.clear()

def save_new_password(username,email,hashed_password):
    df = pd.read_csv("user.csv")
    df.loc[(df["Username"] == username)&
           (df["Email"] == email),
            "Password"] = hashed_password
    df.to_csv("user.csv", index=False)
    st.cache_data.clear()

def load_chat_history(username):
    # Create file if it does not exist
    if not os.path.exists(CHAT_FILE):
        pd.DataFrame(columns=["Username", "Role", "Content"]).to_csv(CHAT_FILE, index=False)
    df = pd.read_csv(CHAT_FILE)
    # Filter only the messages for this username
    user_chats = df[df["Username"] == username]
    messages = []
    for index, row in user_chats.iterrows():
        messages.append({"role": row["Role"], "content": row["Content"]})
    return messages

def save_chat_message(username, role, content):
    # Create file if it does not exist
    if not os.path.exists(CHAT_FILE):
        pd.DataFrame(columns=["Username", "Role", "Content"]).to_csv(CHAT_FILE, index=False)
    df = pd.read_csv(CHAT_FILE)
    # Create new row and add it using concat (matching your pattern)
    new_message = {"Username": username, "Role": role, "Content": content}
    df = pd.concat([df, pd.DataFrame([new_message])], ignore_index=True)
    df.to_csv(CHAT_FILE, index=False)