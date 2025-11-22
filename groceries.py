import streamlit as st
from components import render_item_row
from supabase_client import supabase
from helpers import get_app_user

def grocery_module():
    st.subheader("Grocery Stock Management")

    name = st.text_input("Item name")
    quantity = st.number_input("Quantity", min_value=0.0, step=1.0)
    unit_type = st.selectbox("Unit type", ["piece", "weight"])
    weight_unit = st.selectbox("Select unit (optional)", ["", "kg","gram","liter","ml","ounce","pound"])
    must_buy_next = st.checkbox("Must buy next visit")

    app_user = get_app_user()
    family_id = app_user["family_id"] if app_user else None
    app_user_id = app_user["id"] if app_user else None

    if st.button("Add Grocery"):
        if family_id and app_user_id:
            existing = supabase.table("groceries").select("*").eq("family_id", family_id).eq("name", name).execute()
            if existing.data:
                current = existing.data[0]
                new_quantity = current["quantity"] + quantity
                supabase.table("groceries").update({"quantity": new_quantity}).eq("id", current["id"]).execute()
                st.success(f"Updated {name} quantity to {new_quantity}")
            else:
                supabase.table("groceries").insert({
                    "name": name,
                    "quantity": quantity,
                    "unit_type": unit_type,
                    "weight_unit": weight_unit if weight_unit else None,
                    "must_buy_next": must_buy_next,
                    "family_id": family_id,
                    "added_by": app_user_id
                }).execute()
                st.success("Item added!")
        else:
            st.error("No family linked to your account.")

    st.write("Current Grocery List:")
    if family_id:
        data = supabase.table("groceries").select("*").eq("family_id", family_id).execute()
        groceries = data.data
        for g in groceries:
            user_lookup = supabase.table("app_users").select("name").eq("id", g["added_by"]).execute()
            g["added_by_name"] = user_lookup.data[0]["name"] if user_lookup.data else "Unknown"

        header = st.columns([2,2,2,2,2,2,2])
        header[0].markdown("**Item**")
        header[1].markdown("**Quantity**")
        header[2].markdown("**Unit**")
        header[3].markdown("**Added By**")
        header[4].markdown("**Modify Qty**")
        header[5].markdown("**Update**")
        header[6].markdown("**Action**")

        for g in groceries:
            render_item_row(g, mode="grocery")