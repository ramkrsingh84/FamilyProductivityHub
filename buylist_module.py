import streamlit as st
import pandas as pd
from supabase_client import supabase
from helpers import get_family_id

CATEGORIES = [
    "Fresh Produce","Bakery","Meat & Seafood","Dairy & Eggs","Frozen Food",
    "Pantry/Staples","Snacks","Beverages","Condiments","Household",
    "Personal Care","Baby Products","Pet Supplies","Other"
]

def buylist_module():
    st.subheader("Buy List")
    family_id = get_family_id()
    if not family_id:
        st.error("No family linked to your account.")
        return

    # Fetch items
    data = supabase.table("buy_list").select("*").eq("family_id", family_id).execute()
    buy_items = data.data
    if not buy_items:
        st.info("No items in Buy List")
        return

    # 🔎 Category filter
    filter_cat = st.selectbox("Filter by Category", ["All"] + CATEGORIES)
    if filter_cat != "All":
        buy_items = [b for b in buy_items if b.get("category") == filter_cat]

    # Build aligned table with safe .get()
    df = pd.DataFrame([{
        "Item": b.get("name","Unknown"),
        "Quantity": b.get("quantity",0),
        "Unit Type": b.get("unit_type",""),
        "Weight Unit": b.get("weight_unit",""),
        "Category": b.get("category","Other")
    } for b in buy_items])
    st.dataframe(df, width="stretch")

    # Selection dropdown
    selected_item = st.selectbox(
        "Select an item to manage",
        options=[f"{b.get('name','Unknown')} ({b.get('category','Other')})" for b in buy_items],
        index=None,
        placeholder="Choose an item..."
    )

    if selected_item:
        chosen = next(b for b in buy_items if selected_item.startswith(b.get("name","Unknown")))
        st.markdown(f"---\n### Manage: **{chosen.get('name','Unknown')}**")

        new_qty = st.number_input(
            "Qty", value=float(chosen.get("quantity",0)), step=1.0,
            key=f"qty_{chosen['id']}", label_visibility="collapsed"
        )
        new_category = st.selectbox(
            "Edit Category", CATEGORIES,
            index=CATEGORIES.index(chosen.get("category","Other")),
            key=f"cat_{chosen['id']}"
        )

        cols = st.columns([1,1,1])
        if cols[0].button("Update", key=f"update_{chosen['id']}"):
            supabase.table("buy_list").update({
                "quantity": new_qty,
                "category": new_category
            }).eq("id", chosen["id"]).execute()
            st.success(f"{chosen.get('name','Unknown')} updated")
            st.rerun()

        if cols[1].button("Mark Purchased", key=f"purchase_{chosen['id']}"):
            supabase.table("stock_list").insert({
                "item_id": chosen.get("item_id"),
                "name": chosen.get("name","Unknown"),   # ✅ ensure name is copied
                "quantity": chosen.get("quantity",0),
                "unit_type": chosen.get("unit_type","piece"),
                "weight_unit": chosen.get("weight_unit"),
                "family_id": chosen.get("family_id"),
                "category": chosen.get("category","Other")
            }).execute()
            supabase.table("buy_list").delete().eq("id", chosen["id"]).execute()
            st.success(f"{chosen.get('name','Unknown')} moved to Stock List")
            st.rerun()

        if cols[2].button("Delete", key=f"delete_{chosen['id']}"):
            supabase.table("buy_list").delete().eq("id", chosen["id"]).execute()
            st.warning(f"{chosen.get('name','Unknown')} deleted from Buy List")
            st.rerun()
