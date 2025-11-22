import streamlit as st
from supabase_client import supabase
from helpers import get_user_id

def family_module():
    st.subheader("Family Groups")

    user_id = get_user_id()
    if not user_id:
        st.error("No user logged in.")
        return

    # Get current user record
    user_data = supabase.table("app_users").select("*").eq("id", user_id).execute()
    if not user_data.data:
        st.error("User not found.")
        return
    user = user_data.data[0]

    # Show current family if any
    if user.get("family_id"):
        fam_data = supabase.table("families").select("*").eq("id", user["family_id"]).execute()
        current_family = fam_data.data[0] if fam_data.data else None
        if current_family:
            st.success(f"You are already part of family: **{current_family['name']}**")
    else:
        st.info("You are not part of any family yet.")

    # Show all families
    families = supabase.table("families").select("*").execute().data
    if not families:
        st.info("No families created yet.")
        return

    st.write("### Available Families")
    for f in families:
        st.write(f"**{f['name']}**")
        # Only show join option if user not already in this family
        if user.get("family_id") != f["id"]:
            if st.button(f"Join {f['name']}", key=f"join_{f['id']}"):
                supabase.table("family_requests").insert({
                    "family_id": f["id"],
                    "requester_id": user["id"],
                    "status": "pending"
                }).execute()
                st.success(f"Join request sent to {f['name']}")