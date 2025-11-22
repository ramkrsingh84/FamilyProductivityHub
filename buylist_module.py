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

    # Build aligned table
    df = pd.DataFrame([{
        "Item": b["database_items"]["name"],
        "Quantity": b["quantity"]
    } for b in buy_items])
    st.dataframe(df, use_container_width=True)

    # Interactive controls below each row
    for b in buy_items:
        st.markdown(f"---\n**{b['database_items']['name']}**")
        new_qty = st.number_input(
            "Qty", value=float(b["quantity"]), step=1.0,
            key=f"qty_{b['id']}", label_visibility="collapsed"
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