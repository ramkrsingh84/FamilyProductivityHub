import streamlit as st
import pandas as pd
from supabase_client import supabase
from helpers import get_family_id, format_timestamp

def task_module():
    st.subheader("Tasks")
    family_id = get_family_id()
    if not family_id:
        st.error("No family linked to your account.")
        return

    data = supabase.table("tasks").select("*").eq("family_id", family_id).execute()
    tasks = data.data

    # Format timestamp
    for t in tasks:
        t["created_at"] = format_timestamp(t["created_at"])

    # ✅ Pandas DataFrame now works
    df = pd.DataFrame(tasks)
    df = df.drop(columns=["id", "family_id"], errors="ignore")
    st.dataframe(df)