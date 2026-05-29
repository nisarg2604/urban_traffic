import streamlit as st
import re
import hashlib
from utils.data_loader import load_users

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def settings_page():
    role     = st.session_state.role
    username = st.session_state.username
    color    = "#e63946" if role == "Government" else "#2a9d8f"

    # Load user
    df       = load_users()
    user_row = df[df["Username"] == username].iloc[0]
    first    = user_row["First Name"]
    last     = user_row["Last Name"]
    email    = user_row["Email"]
    phone    = str(user_row["Phone"])


    #  Page Title
    st.title("⚙️ Settings")
    st.caption("Manage your preferences, account details and password.")
    st.divider()

    # Tabs
    tab1, tab2= st.tabs(["👤  Edit Profile", "🔒  Change Password"])


    # TAB 1 — Edit Profile
    with tab1:
        st.subheader("Edit Personal Information")
        st.caption("Update your account details below.")

        col1, col2 = st.columns(2)
        with col1:
            new_first = st.text_input("First Name", value=first)
        with col2:
            new_last = st.text_input("Last Name", value=last)

        col3, col4 = st.columns(2)
        with col3:
            new_email = st.text_input("Email", value=email)
        with col4:
            new_phone = st.text_input("Phone Number", value=phone)

        col5, col6 = st.columns(2)
        with col5:
            st.text_input("Username", value=username, disabled=True,
                          help="Username cannot be changed")
        with col6:
            st.text_input("Role", value=role, disabled=True,
                          help="Role cannot be changed")

        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("💾  Save Changes", type="primary",
                     use_container_width=True, key="save_profile"):
            errors = []
            if not new_first or not new_last or not new_email or not new_phone:
                errors.append("⚠️ Please fill all fields")
            elif not re.match(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$", new_email):
                errors.append("⚠️ Invalid email format")
            elif not re.match(r"^\d{10}$", new_phone):
                errors.append("⚠️ Phone number must be exactly 10 digits")

            if errors:
                for e in errors:
                    st.error(e)
            else:
                df.loc[df["Username"] == username, "First Name"] = new_first
                df.loc[df["Username"] == username, "Last Name"]  = new_last
                df.loc[df["Username"] == username, "Email"]      = new_email
                df.loc[df["Username"] == username, "Phone"]      = new_phone
                df.to_csv("user.csv", index=False)
                st.cache_data.clear()
                st.success("✅ Profile updated successfully!")
                st.rerun()


    # TAB 2 — Change Password

    with tab2:
        st.subheader("Change Password")
        st.caption("Enter your current password to verify identity before changing.")

        col1, col2 = st.columns(2)
        with col1:
            current_password = st.text_input("Current Password", type="password",
                                             placeholder="Enter current password")
        with col2:
            st.info("🔒 Your current password is required for security verification.")

        col3, col4 = st.columns(2)
        with col3:
            new_password = st.text_input("New Password", type="password",
                                         placeholder="Enter new password")
        with col4:
            confirm_password = st.text_input("Confirm New Password", type="password",
                                             placeholder="Re-enter new password")

        if new_password:
            st.caption("Password Strength:")
            c1, c2, c3, c4 = st.columns(4)
            c1.caption("✅ 8+ chars"  if len(new_password) >= 8                    else "❌ 8+ chars")
            c2.caption("✅ Uppercase" if re.search(r"[A-Z]",       new_password)  else "❌ Uppercase")
            c3.caption("✅ Number"    if re.search(r"[0-9]",       new_password)  else "❌ Number")
            c4.caption("✅ Special"   if re.search(r"[!@#$%^&*]", new_password)  else "❌ Special (!@#$%^&*)")

        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("🔐  Update Password", type="primary",
                     use_container_width=True, key="save_password"):
            errors = []
            if not current_password or not new_password or not confirm_password:
                errors.append("⚠️ Please fill all password fields")
            elif df.loc[df["Username"] == username, "Password"].values[0] != hash_password(current_password):
                errors.append("❌ Current password is incorrect")
            elif new_password != confirm_password:
                errors.append("⚠️ New passwords do not match")
            elif len(new_password) < 8:
                errors.append("⚠️ Password must be at least 8 characters")
            elif not re.search(r"[A-Z]", new_password):
                errors.append("⚠️ Must contain at least one uppercase letter")
            elif not re.search(r"[!@#$%^&*]", new_password):
                errors.append("⚠️ Must contain at least one special character")
            elif not re.search(r"[0-9]", new_password):
                errors.append("⚠️ Must contain at least one number")

            if errors:
                for e in errors:
                    st.error(e)
            else:
                df.loc[df["Username"] == username, "Password"] = hash_password(new_password)
                df.to_csv("user.csv", index=False)
                st.cache_data.clear()
                st.success("✅ Password updated successfully!")
                st.rerun()

