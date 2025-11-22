import streamlit as st
from components import render_item_row
from supabase_client import supabase
from helpers import get_family_id

def stock_module():
    st.subheader("Stock List")
    family_id = get_family_id()
    if not family_id:
        st.error("No family linked to your account.")
        return

    data = supabase.table("stock_list").select("*").eq("family_id", family_id).execute()
    stock_items = data.data

    for s in stock_items:
        user_lookup = supabase.table("app_users").select("name").eq("id", s["added_by"]).execute()
        s["added_by_name"] = user_lookup.data[0]["name"] if user_lookup.data else "Unknown"

    # Table header
    header = st.columns([2, 2, 2, 2, 2, 2])
    header[0].markdown("**Item**")
    header[1].markdown("**Quantity**")
    header[2].markdown("**Purchased Date**")
    header[3].markdown("**Status**")
    header[4].markdown("**Added By**")
    header[5].markdown("**Action**")

    for s in stock_items:
        render_item_row(s, mode="stock")