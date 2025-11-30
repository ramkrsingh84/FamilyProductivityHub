import streamlit as st
import pandas as pd
from supabase_client import supabase
from helpers import get_family_id, format_timestamp

CATEGORIES = [
    "Vegetables","Fruits","Bakery","Meat & Seafood","Dairy & Eggs",
    "Frozen Food","Pantry/Staples","Snacks","Beverages","Condiments & Sauces",
    "Household","Personal Care","Baby Products","Pet Supplies",
    "Breakfast & Grains","Other"
]

def stock_module():
    st.subheader("Stock List")
    family_id = get_family_id()
    if not family_id:
        st.error("No family linked to your account.")
        return

    data = supabase.table("stock_list").select("*").eq("family_id", family_id).execute()
    stock_items = data.data
    if not stock_items:
        st.info("No items in Stock List")
        return
    
    # 🔎 Category filter
    filter_cat = st.selectbox("Filter by Category", ["All"] + CATEGORIES)
    if filter_cat != "All":
        stock_items = [s for s in stock_items if s.get("category") == filter_cat]

    # Build aligned table
    df = pd.DataFrame([{
        "Item": s["name"],
        "Quantity": s["quantity"],
        "Unit Type": s.get("unit_type",""),
        "Weight Unit": s.get("weight_unit",""),
        "Purchased": format_timestamp(s.get("purchased_date")),
        "Status": s["status"],
        "Category": s.get("category","Other")
    } for s in stock_items])
    st.dataframe(df, width="stretch")

    # Selection dropdown
    selected_item = st.selectbox(
        "Select an item to manage",
        options=[f"{s['name']} ({s.get('category','Other')})" for s in stock_items],
        index=None,
        placeholder="Choose an item..."
    )

    if selected_item:
        chosen = next(s for s in stock_items if selected_item.startswith(s["name"]))
        st.markdown(f"---\n### Manage: **{chosen['name']}**")

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

        # Category update
        new_category = st.selectbox(
            "Edit Category", CATEGORIES,
            index=CATEGORIES.index(chosen.get("category","Other")),
            key=f"cat_{chosen['id']}"
        )

        cols = st.columns([1,1,1])
        if cols[0].button("Update Qty", key=f"update_{chosen['id']}"):
            supabase.table("stock_list").update({
                "quantity": new_qty,
                "category": new_category
            }).eq("id", chosen["id"]).execute()
            st.success(f"{chosen['name']} stock updated")
            st.rerun()

        if cols[1].button("Update Status", key=f"statusbtn_{chosen['id']}"):
            supabase.table("stock_list").update({
                "status": new_status,
                "category": new_category
            }).eq("id", chosen["id"]).execute()
            st.success(f"Status updated for {chosen['name']}")

            # ✅ If exhausted, delete entry
            if new_status == "exhausted":
                supabase.table("stock_list").delete().eq("id", chosen["id"]).execute()
                st.warning(f"{chosen['name']} removed from Stock List (exhausted)")
            st.rerun()

        if cols[2].button("Delete", key=f"delete_{chosen['id']}"):
            supabase.table("stock_list").delete().eq("id", chosen["id"]).execute()
            st.warning(f"{chosen['name']} deleted from Stock List")
            st.rerun()