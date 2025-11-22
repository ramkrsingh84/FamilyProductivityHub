import streamlit as st
from supabase_client import supabase
from helpers import format_timestamp

def render_item_row(item, mode="grocery"):
    col1, col2, col3, col4, col5, col6 = st.columns([2, 2, 2, 2, 2, 2])

    # Common fields
    name = item["name"]
    quantity = item["quantity"]
    unit = item.get("weight_unit") or "piece"
    added_by = item.get("added_by_name", "Unknown")

    # Grocery view
    if mode == "grocery":
        col1.write(name)
        col2.write(quantity)
        col3.write(unit)
        col4.write(added_by)
        col5.write("—")
        if col6.button("Mark Purchased", key=f"purchase_{item['id']}"):
            supabase.table("stock_list").insert({
                "grocery_id": item["id"],
                "name": name,
                "quantity": quantity,
                "unit_type": item["unit_type"],
                "weight_unit": item.get("weight_unit"),
                "family_id": item["family_id"],
                "added_by": item["added_by"]
            }).execute()
            supabase.table("groceries").delete().eq("id", item["id"]).execute()
            st.success(f"{name} moved to Stock List")

    # Stock view
    elif mode == "stock":
        purchased_date = format_timestamp(item.get("purchased_date"))
        status = item.get("status", "available")
        col1.write(name)
        col2.write(quantity)
        col3.write(purchased_date)
        new_status = col4.selectbox(
            "", ["available", "reducing", "exhausted"],
            index=["available", "reducing", "exhausted"].index(status),
            key=f"status_{item['id']}"
        )
        if new_status != status:
            supabase.table("stock_list").update({"status": new_status}).eq("id", item["id"]).execute()
            st.success(f"Status updated for {name}")
        col5.write(added_by)
        if col6.button("Move Back", key=f"moveback_{item['id']}"):
            supabase.table("groceries").insert({
                "name": name,
                "quantity": quantity,
                "unit_type": item["unit_type"],
                "weight_unit": item.get("weight_unit"),
                "must_buy_next": True,
                "family_id": item["family_id"],
                "added_by": item["added_by"]
            }).execute()
            supabase.table("stock_list").delete().eq("id", item["id"]).execute()
            st.warning(f"{name} moved back to Buy List")