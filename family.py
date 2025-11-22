import streamlit as st
from supabase_client import supabase
from helpers import get_app_user

def family_module():
    st.subheader("Family Management")

    # Create Family
    fam_name = st.text_input("Family Name")
    if st.button("Create Family"):
        family = supabase.table("families").insert({
            "name": fam_name,
            "created_by": st.session_state["user"].id
        }).execute()

        if family.data:
            fam_id = family.data[0]["id"]
            supabase.table("app_users").update({
                "family_id": fam_id,
                "role": "admin"
            }).eq("auth_id", st.session_state["user"].id).execute()
            st.success(f"Family '{fam_name}' created! Share ID: {fam_id}")

    # Request to Join Family
    families = supabase.table("families").select("id, name").execute()
    fam_options = {f["name"]: f["id"] for f in families.data} if families.data else {}
    fam_choice = st.selectbox("Select Family to request join", list(fam_options.keys())) if fam_options else None

    if st.button("Request to Join"):
        if fam_choice:
            fam_id = fam_options[fam_choice]
            app_user = get_app_user()
            supabase.table("family_requests").insert({
                "family_id": fam_id,
                "requester_id": app_user["id"],
                "status": "pending"
            }).execute()
            st.success("Join request submitted. Awaiting admin approval.")

    # Admin Approval
    app_user = get_app_user()
    if app_user and app_user["role"] == "admin":
        requests = supabase.table("family_requests").select("id, requester_id, status").eq("family_id", app_user["family_id"]).eq("status", "pending").execute()
        if requests.data:
            st.write("Pending Join Requests:")
            for r in requests.data:
                requester = supabase.table("app_users").select("name").eq("id", r["requester_id"]).execute()
                requester_name = requester.data[0]["name"] if requester.data else "Unknown"

                col1, col2 = st.columns(2)
                with col1:
                    if st.button(f"Approve {requester_name}", key=f"approve_{r['id']}"):
                        supabase.table("app_users").update({
                            "family_id": app_user["family_id"],
                            "role": "member"
                        }).eq("id", r["requester_id"]).execute()
                        supabase.table("family_requests").update({"status": "approved"}).eq("id", r["id"]).execute()
                        st.success(f"{requester_name} added to family.")
                with col2:
                    if st.button(f"Reject {requester_name}", key=f"reject_{r['id']}"):
                        supabase.table("family_requests").update({"status": "rejected"}).eq("id", r["id"]).execute()
                        st.warning(f"{requester_name}'s request rejected.")