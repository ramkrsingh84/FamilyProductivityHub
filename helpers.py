import streamlit as st
from datetime import datetime
from supabase_client import supabase

def get_family_id():
    result = supabase.table("app_users").select("family_id").eq("auth_id", st.session_state["user"].id).execute()
    if result.data and result.data[0]["family_id"]:
        return result.data[0]["family_id"]
    return None

def get_app_user():
    result = supabase.table("app_users").select("id, family_id, name, role").eq("auth_id", st.session_state["user"].id).execute()
    if result.data:
        return result.data[0]
    return None

def format_timestamp(ts):
    try:
        return datetime.fromisoformat(ts.replace("Z", "+00:00")).strftime("%d-%m-%Y %H:%M")
    except:
        return ts

def get_user_name():
    result = supabase.table("app_users").select("name").eq("auth_id", st.session_state["user"].id).execute()
    if result.data and result.data[0]["name"]:
        return result.data[0]["name"]
    return st.session_state["user"].email