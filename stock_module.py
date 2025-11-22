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

    data = supabase.table("stock_list").select("*, groceries(name)").eq("family_id", family_id).execute()
    stock_items = data.data

    if not stock_items:
        st.info("No items in Stock List")
        return

    # Build aligned table
    df = pd.DataFrame([{
        "Item": s["groceries"]["name"] if s.get("groceries") else s["name"],
        "Quantity": s["quantity"],
        "Unit Type": s.get("unit_type", ""),
        "Weight Unit": s.get("weight_unit", ""),
        "Purchased": format_timestamp(s.get("purchased_date")),
        "Status": s["status"]
    } for s in stock_items])
    st.dataframe(df, width="stretch")

    # Selection dropdown
    selected_item = st.selectbox(
        "Select an item to manage",
        options=[f"{(s['groceries']['name'] if s.get('groceries') else s['name'])} "
                 f"(Qty: {s['quantity']}, {s.get('unit_type','')} {s.get('weight_unit','')})"
                 for s in stock_items],
        index=None,
        placeholder="Choose an item..."
    )

    if selected_item:
        chosen = next(s for s in stock_items if selected_item.startswith(
            s["groceries"]["name"] if s.get("groceries") else s["name"]
        ))

        st.markdown(f"---\n### Manage: **{chosen['groceries']['name'] if chosen.get('groceries') else chosen['name']}**")

        # Quantity update
        new_qty = st.number_input(
            "Qty", value=float(chosen["quantity"]), step=1.0,
            key=f"qty_{chosen['id']}", label_visibility="collapsed"
        )

        # Status update
        new_status = st.selectbox(
            "Status", ["available","reducing","exhausted"],
            index=["available","reducing","exhausted"].index(chosen["status"]),
            key=f"status_{chosen['id']}"
        )

        cols = st.columns([1,1])
        if cols[0].button("Update Qty", key=f"update_{chosen['id']}"):
            supabase.table("stock_list").update({"quantity": new_qty}).eq("id", chosen["id"]).execute()
            st.success(f"{chosen['name']} stock updated to {new_qty}")
            st.rerun()

        if cols[1].button("Update Status", key=f"statusbtn_{chosen['id']}"):
            supabase.table("stock_list").update({"status": new_status}).eq("id", chosen["id"]).execute()
            st.success(f"Status updated for {chosen['name']}")

            # ✅ If exhausted, delete entry
            if new_status == "exhausted":
                supabase.table("stock_list").delete().eq("id", chosen["id"]).execute()
                st.warning(f"{chosen['name']} removed from Stock List (exhausted)")
            st.rerun()