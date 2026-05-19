import streamlit as st
import pandas as pd
from groq import Groq
from utils.data_loader import load_chat_history, save_chat_message

# Put your Groq API key here
# GROQ_API_KEY = "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"
os.environ["GROQ_API_KEY"] = st.secrets["GROQ_API_KEY"]

def get_traffic_context():
    """Reads the dataset and creates a short summary for the AI."""
    try:
        df = pd.read_csv("Bangalore_traffic_Dataset.csv")

        # Group data by area to get averages
        summary = df.groupby('Area Name').agg({
            'Congestion Level': 'mean',
            'Average Speed': 'mean',
            'Incident Reports': 'sum'
        }).reset_index()

        context = "Current Bengaluru Traffic Data Context:\n"
        for _, row in summary.iterrows():
            area = row['Area Name']
            congestion = round(row['Congestion Level'], 2)
            speed = round(row['Average Speed'], 2)
            incidents = row['Incident Reports']

            # Simple logic for alerts
            alert = "High Alert!" if congestion > 80 or incidents > 0 else "Normal"
            context += f"- {area}: Congestion Level {congestion}/100, Speed {speed} km/h, Incidents: {incidents}. Status: {alert}\n"

        return context
    except Exception as e:
        return "Traffic data is currently unavailable."


def chatbot_page():
    st.title("🤖 Traffic AI Assistant")
    st.caption("Powered by Groq. Your chat history is saved securely.")
    st.divider()

    # Setup the Groq client
    client = Groq(api_key=GROQ_API_KEY)

    # Get the username of the person logged in
    current_user = st.session_state.username

    # 👇 ADDED SAFETY: Check if we have messages AND if they belong to this exact user
    if "messages" not in st.session_state or st.session_state.get("chat_user") != current_user:

        # Save the current user to memory so we know whose chat this is
        st.session_state.chat_user = current_user

        traffic_data = get_traffic_context()
        system_prompt = f"""You are a helpful AI Traffic Assistant. Answer in simple English.
        You have access to live traffic data. Here is the data: 
        {traffic_data}
        """

        # Load past messages from the CSV file
        past_messages = load_chat_history(current_user)

        if len(past_messages) > 0:
            # If they talked before, load their old chat
            st.session_state.messages = [{"role": "system", "content": system_prompt}] + past_messages
        else:
            # If this is their first time, greet them
            first_msg = "Hello! I am your Bengaluru Traffic AI. How can I help you today?"
            st.session_state.messages = [
                {"role": "system", "content": system_prompt},
                {"role": "assistant", "content": first_msg}
            ]
            # Save the first greeting
            save_chat_message(current_user, "assistant", first_msg)

    # Show all messages on the screen
    for message in st.session_state.messages:
        if message["role"] != "system":  # Hide the system instructions from the user
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

    # Box for user to type their message
    user_input = st.chat_input("Ask about traffic in Koramangala or Whitefield...")

    if user_input:
        # 1. Show user message on screen
        st.chat_message("user").markdown(user_input)
        st.session_state.messages.append({"role": "user", "content": user_input})

        # 2. Save user message to CSV
        save_chat_message(current_user, "user", user_input)

        # 3. Get reply from AI
        try:
            with st.spinner("Thinking..."):
                chat_completion = client.chat.completions.create(
                    messages=st.session_state.messages,
                    model="llama-3.3-70b-versatile",
                    temperature=0.5,
                    max_tokens=500,
                )

                ai_response = chat_completion.choices[0].message.content

                # Show AI message on screen
                with st.chat_message("assistant"):
                    st.markdown(ai_response)
                st.session_state.messages.append({"role": "assistant", "content": ai_response})

                # 4. Save AI message to CSV
                save_chat_message(current_user, "assistant", ai_response)

        except Exception as e:
            st.error(f"Error connecting to AI: {e}")