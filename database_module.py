import streamlit as st
from supabase_client import supabase
from helpers import get_family_id
import pandas as pd

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
        st.rerun()

    # Show items
    data = supabase.table("database_items").select("*").eq("family_id", family_id).execute()
    items = data.data

    if not items:
        st.info("No items in Database")
        return

    # Display aligned table
    st.write("### Current Database Items")
    df = pd.DataFrame([{
        "Item": i["name"],
        "Unit Type": i["default_unit"],
        "Weight Unit": i["default_weight_unit"] or ""
    } for i in items])
    st.dataframe(df, use_container_width=True)

    # Selection dropdown
    selected_item = st.selectbox(
        "Select an item to modify/delete",
        options=[f"{i['name']} ({i['default_unit']} {i['default_weight_unit'] or ''})" for i in items],
        index=None,
        placeholder="Choose an item..."
    )

    if selected_item:
        chosen = next(i for i in items if selected_item.startswith(i["name"]))

        st.markdown(f"---\n### Manage: **{chosen['name']}**")
        new_name = st.text_input("Edit Name", value=chosen["name"], key=f"name_{chosen['id']}")
        new_unit = st.selectbox("Edit Unit Type", ["piece","weight"],
                                index=["piece","weight"].index(chosen["default_unit"]),
                                key=f"unit_{chosen['id']}")
        new_weight_unit = st.selectbox("Edit Weight Unit",
                                       ["","kg","gram","liter","ml","ounce","pound"],
                                       index=(["","kg","gram","liter","ml","ounce","pound"].index(chosen["default_weight_unit"])
                                              if chosen["default_weight_unit"] else 0),
                                       key=f"wunit_{chosen['id']}")

        cols = st.columns([1,1])
        if cols[0].button("Update", key=f"update_{chosen['id']}"):
            supabase.table("database_items").update({
                "name": new_name,
                "default_unit": new_unit,
                "default_weight_unit": new_weight_unit if new_weight_unit else None
            }).eq("id", chosen["id"]).execute()
            st.success(f"{chosen['name']} updated")
            st.rerun()

        if cols[1].button("Delete", key=f"delete_{chosen['id']}"):
            supabase.table("database_items").delete().eq("id", chosen["id"]).execute()
            st.warning(f"{chosen['name']} deleted from Database")
            st.rerun()