import streamlit as st
from utils.data_loader import load_users

def profile_page():
    role     = st.session_state.role
    username = st.session_state.username
    color    = "#e63946" if role == "Government" else "#2a9d8f"
    icon     = "🏛️" if role == "Government" else "🙋"

    # ── Load user
    df       = load_users()
    user_row = df[df["Username"] == username].iloc[0]
    first    = user_row["First Name"]
    last     = user_row["Last Name"]
    email    = user_row["Email"]
    phone    = str(user_row["Phone"])
    initials = f"{first[0]}{last[0]}".upper()
    fullname = f"{first} {last}"


    st.markdown(f"""
    <style>
    .pf-banner {{
        background: linear-gradient(135deg, {color}22 0%, {color}08 100%);
        border: 1px solid {color}33;
        border-radius: 16px;
        padding: 24px 28px;
        display: flex;
        align-items: center;
        gap: 24px;
        margin-bottom: 20px;
    }}
    .pf-avatar {{
        width: 80px; height: 80px;
        border-radius: 50%;
        background: linear-gradient(135deg, {color}, {color}99);
        display: flex; align-items: center; justify-content: center;
        font-size: 28px; font-weight: 700; color: white;
        box-shadow: 0 4px 16px {color}44;
        flex-shrink: 0;
    }}
    .pf-banner-name {{
        font-size: 22px; font-weight: 700;
        margin-bottom: 4px;
    }}
    .pf-banner-username {{
        font-size: 13px; color: #888;
        margin-bottom: 8px;
    }}
    .pf-role-badge {{
        display: inline-block;
        background: {color}22; color: {color};
        font-size: 11px; font-weight: 700;
        padding: 3px 12px; border-radius: 20px;
        letter-spacing: 0.8px; text-transform: uppercase;
        border: 1px solid {color}44;
    }}
    .pf-info-card {{
        border: 1px solid {color}33;
        border-radius: 16px;
        padding: 24px 28px;
        margin-bottom: 20px;
    }}
    .pf-info-row {{
        display: flex;
        gap: 24px;
        margin-bottom: 16px;
    }}
    .pf-info-item {{
        flex: 1;
    }}
    .pf-info-label {{
        font-size: 11px; font-weight: 600;
        text-transform: uppercase; letter-spacing: 1px;
        color: #888; margin-bottom: 6px;
    }}
    .pf-info-value {{
        font-size: 15px; font-weight: 500;
        padding: 10px 14px;
        border-radius: 10px;
        border: 1px solid {color}22;
        background: {color}08;
    }}
    .pf-section-title {{
        font-size: 13px; font-weight: 700;
        text-transform: uppercase; letter-spacing: 1.5px;
        color: {color};
        border-bottom: 2px solid {color}22;
        padding-bottom: 8px;
        margin-bottom: 18px;
    }}
    </style>
    """, unsafe_allow_html=True)

    # ── Page Title ────────────────────────────
    st.title("👤 My Profile")
    st.caption("Your account information — go to Settings to make changes.")

    # ── Banner ────────────────────────────────
    st.markdown(f"""
        <div class="pf-banner">
            <div class="pf-avatar">{initials}</div>
            <div>
                <div class="pf-banner-name">{fullname}</div>
                <div class="pf-banner-username">@{username}</div>
                <div class="pf-role-badge">{icon} {role}</div>
            </div>
        </div>
    """, unsafe_allow_html=True)

    # ── Static Info Card
    st.markdown(f"""
        <div class="pf-info-card">
            <div class="pf-section-title">Personal Information</div>
            <div class="pf-info-row">
                <div class="pf-info-item">
                    <div class="pf-info-label">First Name</div>
                    <div class="pf-info-value">{first}</div>
                </div>
                <div class="pf-info-item">
                    <div class="pf-info-label">Last Name</div>
                    <div class="pf-info-value">{last}</div>
                </div>
            </div>
            <div class="pf-info-row">
                <div class="pf-info-item">
                    <div class="pf-info-label">Email</div>
                    <div class="pf-info-value">{email}</div>
                </div>
                <div class="pf-info-item">
                    <div class="pf-info-label">Phone Number</div>
                    <div class="pf-info-value">{phone}</div>
                </div>
            </div>
            <div class="pf-info-row">
                <div class="pf-info-item">
                    <div class="pf-info-label">Username</div>
                    <div class="pf-info-value">{username}</div>
                </div>
                <div class="pf-info-item">
                    <div class="pf-info-label">Account Type</div>
                    <div class="pf-info-value">{icon} {role}</div>
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)

    st.info("💡 To edit your information or change your password, go to **Settings** from the sidebar.")