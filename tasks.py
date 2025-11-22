import streamlit as st
import pandas as pd
from supabase_client import supabase
from helpers import get_family_id

def tasklist_module():
    st.subheader("Family Task List")
    family_id = get_family_id()
    if not family_id:
        st.error("No family linked to your account.")
        return

    # --- Task Creation ---
    with st.expander("➕ Create New Task"):
        title = st.text_input("Task Title")
        description = st.text_area("Description")
        due_date = st.date_input("Due Date")
        if st.button("Add Task"):
            supabase.table("tasks").insert({
                "title": title,
                "description": description,
                "due_date": due_date.isoformat(),
                "status": "pending",
                "family_id": family_id
            }).execute()
            st.success("Task added successfully")
            st.rerun()

    # --- Show Tasks ---
    data = supabase.table("tasks").select("*").eq("family_id", family_id).execute()
    tasks = data.data

    if not tasks:
        st.info("No tasks yet")
        return

    df = pd.DataFrame([{
        "Title": t["title"],
        "Description": t.get("description",""),
        "Due Date": t.get("due_date",""),
        "Status": t["status"]
    } for t in tasks])
    st.dataframe(df, use_container_width=True)

    # --- Selection for Management ---
    selected_task = st.selectbox(
        "Select a task to manage",
        options=[f"{t['title']} ({t['status']})" for t in tasks],
        index=None,
        placeholder="Choose a task..."
    )

    if selected_task:
        chosen = next(t for t in tasks if selected_task.startswith(t["title"]))
        st.markdown(f"---\n### Manage: **{chosen['title']}**")

        new_status = st.selectbox(
            "Update Status", ["pending","completed"],
            index=["pending","completed"].index(chosen["status"]),
            key=f"status_{chosen['id']}"
        )

        cols = st.columns([1,1])
        if cols[0].button("Update Status", key=f"update_{chosen['id']}"):
            supabase.table("tasks").update({"status": new_status}).eq("id", chosen["id"]).execute()
            st.success(f"Task '{chosen['title']}' updated to {new_status}")
            st.rerun()

        if new_status == "completed" and cols[1].button("Delete Task", key=f"delete_{chosen['id']}"):
            supabase.table("tasks").delete().eq("id", chosen["id"]).execute()
            st.warning(f"Task '{chosen['title']}' deleted (completed)")
            st.rerun()