import streamlit as st
from datetime import datetime
from supabase_client import supabase

# --- Task Management ---
def task_module():
    st.subheader("Task Management")
    title = st.text_input("Task title")
    description = st.text_area("Description")
    due_date = st.date_input("Due date")
    status = st.selectbox("Status", ["pending", "completed"])

    family_id = get_family_id()

    # Dropdown of family members
    members = supabase.table("app_users").select("id, name").eq("family_id", family_id).execute()
    member_options = {m["name"]: m["id"] for m in members.data} if members.data else {}
    assigned_to_name = st.selectbox("Assign to", list(member_options.keys())) if member_options else None

    if st.button("Add Task"):
        if family_id and assigned_to_name:
            supabase.table("tasks").insert({
                "title": title,
                "description": description,
                "due_date": str(due_date),
                "assigned_to": member_options[assigned_to_name],
                "family_id": family_id,
                "status": status
            }).execute()
            st.success("Task added!")
        else:
            st.error("No family linked to your account or no members found.")

    st.write("My Tasks:")
    if family_id:
        data = supabase.table("tasks").select("*").eq("family_id", family_id).execute()
        tasks = data.data

        for t in tasks:
            # Lookup family name
            fam_lookup = supabase.table("families").select("name").eq("id", t["family_id"]).execute()
            t["family_name"] = fam_lookup.data[0]["name"] if fam_lookup.data else "Unknown"

            # Lookup assigned user name
            if t["assigned_to"]:
                user_lookup = supabase.table("app_users").select("name").eq("id", t["assigned_to"]).execute()
                t["assigned_to"] = user_lookup.data[0]["name"] if user_lookup.data else "Unknown"

            # Format timestamp
            t["created_at"] = format_timestamp(t["created_at"])

        df = pd.DataFrame(tasks)
        df = df.drop(columns=["id", "family_id"], errors="ignore")
        st.dataframe(df)