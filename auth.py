import streamlit as st
from supabase_client import supabase

def login():
    st.subheader("Login")
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        try:
            user = supabase.auth.sign_in_with_password({"email": email, "password": password})
            if user.user:
                st.session_state["user"] = user.user
                st.success("Logged in successfully!")
                st.rerun()
            else:
                st.error("Login failed: No user returned")
        except Exception as e:
            st.error(f"Login failed: {e}")

def register():
    st.subheader("Register")
    name = st.text_input("Full Name")
    email = st.text_input("Email (register)")
    password = st.text_input("Password (register)", type="password")

    if st.button("Register"):
        try:
            user = supabase.auth.sign_up({"email": email, "password": password})
            if user.user:
                auth_id = user.user.id
                supabase.table("app_users").insert({
                    "auth_id": auth_id,
                    "name": name if name else email.split("@")[0],
                    "role": "member",
                    "family_id": None
                }).execute()
                st.success("Registered successfully! Please login.")
            else:
                st.error("Registration failed: No user returned from Supabase.")
        except Exception as e:
            st.error(f"Registration failed: {e}")