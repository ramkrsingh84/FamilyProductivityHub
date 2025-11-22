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

    data = supabase.table("buy_list").select("*, database_items(name, default_unit, default_weight_unit)").eq("family_id", family_id).execute()
    buy_items = data.data

    if not buy_items:
        st.info("No items in Buy List")
        return

    # Build aligned table with unit info
    df = pd.DataFrame([{
        "Item": b["database_items"]["name"],
        "Quantity": b["quantity"],
        "Unit Type": b.get("unit_type", b["database_items"].get("default_unit", "")),
        "Weight Unit": b.get("weight_unit", b["database_items"].get("default_weight_unit", ""))
    } for b in buy_items])
    st.dataframe(df, width="stretch")

    # Selection dropdown
    selected_item = st.selectbox(
        "Select an item to manage",
        options=[f"{b['database_items']['name']} (Qty: {b['quantity']}, {b.get('unit_type', b['database_items'].get('default_unit',''))} {b.get('weight_unit', b['database_items'].get('default_weight_unit',''))})" for b in buy_items],
        index=None,
        placeholder="Choose an item..."
    )

    if selected_item:
        # Find the matching entry
        chosen = next(b for b in buy_items if selected_item.startswith(b["database_items"]["name"]))

        st.markdown(f"---\n### Manage: **{chosen['database_items']['name']}**")
        new_qty = st.number_input(
            "Qty", value=float(chosen["quantity"]), step=1.0,
            key=f"qty_{chosen['id']}", label_visibility="collapsed"
        )
        cols = st.columns([1,1,1])
        if cols[0].button("Update", key=f"update_{chosen['id']}"):
            supabase.table("buy_list").update({"quantity": new_qty}).eq("id", chosen["id"]).execute()
            st.success(f"{chosen['database_items']['name']} quantity updated")
            st.rerun()

        if cols[1].button("Mark Purchased", key=f"purchase_{chosen['id']}"):
            supabase.table("stock_list").insert({
                "item_id": chosen["item_id"],
                "name": chosen["database_items"]["name"],
                "quantity": chosen["quantity"],
                "unit_type": chosen.get("unit_type", "piece"),
                "weight_unit": chosen.get("weight_unit"),
                "family_id": chosen["family_id"]
            }).execute()
            supabase.table("buy_list").delete().eq("id", chosen["id"]).execute()
            st.success(f"{chosen['database_items']['name']} moved to Stock List")
            st.rerun()

        if cols[2].button("Delete", key=f"delete_{chosen['id']}"):
            supabase.table("buy_list").delete().eq("id", chosen["id"]).execute()
            st.warning(f"{chosen['database_items']['name']} deleted from Buy List")
            st.rerun()