import streamlit as st
import pandas as pd
from supabase_client import supabase
from helpers import get_family_id, format_timestamp

def stock_module():
    st.subheader("Stock List")
    family_id = get_family_id()
    if not family_id:
        st.error("No family linked to your account.")
        return

    data = supabase.table("stock_list").select("*, database_items(name)").eq("family_id", family_id).execute()
    stock_items = data.data

    if not stock_items:
        st.info("No items in Stock List")
        return

    # Build aligned table
    df = pd.DataFrame([{
        "Item": s["database_items"]["name"],
        "Quantity": s["quantity"],
        "Purchased": format_timestamp(s.get("purchased_date")),
        "Status": s["status"]
    } for s in stock_items])
    st.dataframe(df, width="stretch")

    # Interactive controls below each row
    for s in stock_items:
        st.markdown(f"---\n**{s['database_items']['name']}**")
        new_qty = st.number_input(
            "Qty", value=float(s["quantity"]), step=1.0,
            key=f"qty_{s['id']}", label_visibility="collapsed"
        )
        new_status = st.selectbox(
            "Status", ["available","reducing","exhausted"],
            index=["available","reducing","exhausted"].index(s["status"]),
            key=f"status_{s['id']}"
        )

        cols = st.columns([1,1])
        if cols[0].button("Update Qty", key=f"update_{s['id']}"):
            supabase.table("stock_list").update({"quantity": new_qty}).eq("id", s["id"]).execute()
            st.success(f"{s['database_items']['name']} stock updated to {new_qty}")

        if new_status != s["status"]:
            supabase.table("stock_list").update({"status": new_status}).eq("id", s["id"]).execute()
            st.success(f"Status updated for {s['database_items']['name']}")

            # ✅ If exhausted, delete entry
            if new_status == "exhausted":
                supabase.table("stock_list").delete().eq("id", s["id"]).execute()
                st.warning(f"{s['database_items']['name']} removed from Stock List (exhausted)")