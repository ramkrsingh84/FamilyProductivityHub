import streamlit as st
from supabase_client import supabase
from helpers import get_family_id

def database_module():
    st.subheader("Database of Items")
    family_id = get_family_id()
    if not family_id:
        st.error("No family linked to your account.")
        return

    # Add new item
    name = st.text_input("New Item Name")
    unit = st.selectbox("Default Unit Type", ["piece","weight"])
    weight_unit = st.selectbox("Weight Unit", ["","kg","gram","liter","ml","ounce","pound"])
    if st.button("Add to Database"):
        supabase.table("database_items").insert({
            "name": name,
            "default_unit": unit,
            "default_weight_unit": weight_unit if weight_unit else None,
            "family_id": family_id
        }).execute()
        st.success("Item added to database")

    # Show items
    data = supabase.table("database_items").select("*").eq("family_id", family_id).execute()
    items = data.data

    # Build labels with unit info
    options = {
        f"{i['name']} ({i['default_unit']}{' '+i['default_weight_unit'] if i['default_weight_unit'] else ''})": i
        for i in items
    }

    selected = st.multiselect("Select items to add to Buy List", list(options.keys()))

    if st.button("Add Selected to Buy List"):
        for label in selected:
            i = options[label]
            supabase.table("buy_list").insert({
                "item_id": i["id"],
                "quantity": 1,
                "unit_type": i["default_unit"],
                "weight_unit": i["default_weight_unit"],
                "family_id": family_id
            }).execute()
        st.success("Items added to Buy List")
