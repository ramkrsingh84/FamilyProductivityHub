import streamlit as st
from components import render_item_row
from supabase_client import supabase
from helpers import get_app_user

def grocery_module():
    st.subheader("Grocery Stock Management")

    # Input form
    name = st.text_input("Item name")
    quantity = st.number_input("Quantity", min_value=0.0, step=1.0)
    unit_type = st.selectbox("Unit type", ["piece", "weight"])
    weight_unit = st.selectbox("Select unit (optional)", ["", "kg", "gram", "liter", "ml", "ounce", "pound"])
    must_buy_next = st.checkbox("Must buy next visit")

    # ✅ Get current user and family context
    app_user = get_app_user()
    family_id = app_user["family_id"] if app_user else None
    app_user_id = app_user["id"] if app_user else None

    # Add grocery
    if st.button("Add Grocery"):
        if family_id and app_user_id:
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
            st.error("No family linked to your account. Please create or join a family first.")

    # Show grocery list
    st.write("Current Grocery List:")
    if family_id:
        data = supabase.table("groceries").select("*").eq("family_id", family_id).execute()
        groceries = data.data

        # Lookup added_by names
        for g in groceries:
            user_lookup = supabase.table("app_users").select("name").eq("id", g["added_by"]).execute()
            g["added_by_name"] = user_lookup.data[0]["name"] if user_lookup.data else "Unknown"

        # Table header
        header = st.columns([2, 2, 2, 2, 2, 2])
        header[0].markdown("**Item**")
        header[1].markdown("**Quantity**")
        header[2].markdown("**Unit**")
        header[3].markdown("**Added By**")
        header[4].markdown("**Status**")
        header[5].markdown("**Action**")

        for g in groceries:
            render_item_row(g, mode="grocery")