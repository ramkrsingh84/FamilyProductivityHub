import streamlit as st
from supabase_client import supabase
from helpers import format_timestamp

def render_item_row(item, mode="grocery"):
    if mode == "grocery":
        col1, col2, col3, col4, col5, col6, col7 = st.columns([2,2,2,2,2,2,2])
        col1.write(item["name"])
        col2.write(item["quantity"])
        col3.write(item.get("weight_unit") or "piece")
        col4.write(item.get("added_by_name","Unknown"))

        # Inline quantity modification
        new_qty = col5.number_input("Qty", min_value=0.0, value=float(item["quantity"]), step=1.0, key=f"qty_{item['id']}")
        if col6.button("Update", key=f"update_{item['id']}"):
            supabase.table("groceries").update({"quantity": new_qty}).eq("id", item["id"]).execute()
            st.success(f"{item['name']} quantity updated to {new_qty}")

        # Mark purchased
        if col7.button("Mark Purchased", key=f"purchase_{item['id']}"):
            supabase.table("stock_list").insert({
                "grocery_id": item["id"],
                "name": item["name"],
                "quantity": item["quantity"],
                "unit_type": item["unit_type"],
                "weight_unit": item.get("weight_unit"),
                "family_id": item["family_id"],
                "added_by": item["added_by"]
            }).execute()
            supabase.table("groceries").delete().eq("id", item["id"]).execute()
            st.success(f"{item['name']} moved to Stock List")

    elif mode == "stock":
        col1, col2, col3, col4, col5, col6, col7 = st.columns([2,2,2,2,2,2,2])
        col1.write(item["name"])
        col2.write(item["quantity"])
        col3.write(format_timestamp(item.get("purchased_date")))

        # Status dropdown
        status = item.get("status","available")
        new_status = col4.selectbox(
            "Status", ["available","reducing","exhausted"],
            index=["available","reducing","exhausted"].index(status),
            key=f"status_{item['id']}"
        )
        if new_status != status:
            supabase.table("stock_list").update({"status": new_status}).eq("id", item["id"]).execute()
            st.success(f"Status updated for {item['name']}")

        col5.write(item.get("added_by_name","Unknown"))

        # Inline quantity modification
        new_qty = col6.number_input("Qty", min_value=0.0, value=float(item["quantity"]), step=1.0, key=f"stockqty_{item['id']}")
        if col7.button("Update", key=f"stockupdate_{item['id']}"):
            supabase.table("stock_list").update({"quantity": new_qty}).eq("id", item["id"]).execute()
            st.success(f"{item['name']} stock updated to {new_qty}")

        # Move back to buy list if exhausted
        if new_status == "exhausted":
            if st.button("Move Back", key=f"moveback_{item['id']}"):
                supabase.table("groceries").insert({
                    "name": item["name"],
                    "quantity": item["quantity"],
                    "unit_type": item["unit_type"],
                    "weight_unit": item.get("weight_unit"),
                    "must_buy_next": True,
                    "family_id": item["family_id"],
                    "added_by": item["added_by"]
                }).execute()
                supabase.table("stock_list").delete().eq("id", item["id"]).execute()
                st.warning(f"{item['name']} moved back to Buy List")