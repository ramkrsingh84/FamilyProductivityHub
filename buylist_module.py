import streamlit as st
import pandas as pd
from supabase_client import supabase
from helpers import get_family_id

def buylist_module():
    st.subheader("Buy List")
    family_id = get_family_id()
    if not family_id:
        st.error("No family linked to your account.")
        return

    data = supabase.table("buy_list").select("*, database_items(name)").eq("family_id", family_id).execute()
    buy_items = data.data

    if not buy_items:
        st.info("No items in Buy List")
        return

    # Build a DataFrame for aligned display
    df = pd.DataFrame([{
        "Item": b["database_items"]["name"],
        "Quantity": b["quantity"],
        "Update Qty": "",       # placeholder for widget
        "Action": ""            # placeholder for widget
    } for b in buy_items])

    st.write("### Current Buy List")
    st.table(df)  # static aligned table

    # Interactive controls below the table
    for b in buy_items:
        st.markdown("---")
        st.write(f"**{b['database_items']['name']}**")
        new_qty = st.number_input(
            "Qty", 
            value=float(b["quantity"]), 
            step=1.0, 
            key=f"qty_{b['id']}", 
            label_visibility="collapsed"
        )
        cols = st.columns([1,1])
        if cols[0].button("Update", key=f"update_{b['id']}"):
            supabase.table("buy_list").update({"quantity": new_qty}).eq("id", b["id"]).execute()
            st.success(f"{b['database_items']['name']} quantity updated")
        if cols[1].button("Mark Purchased", key=f"purchase_{b['id']}"):
            supabase.table("stock_list").insert({
                "item_id": b["item_id"],
                "name": b["database_items"]["name"],
                "quantity": b["quantity"],
                "unit_type": b.get("unit_type", "piece"),
                "weight_unit": b.get("weight_unit"),
                "family_id": b["family_id"]
            }).execute()
            supabase.table("buy_list").delete().eq("id", b["id"]).execute()
            st.success(f"{b['database_items']['name']} moved to Stock List")