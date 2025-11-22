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
        new_name = st.text_input("Edit Name", value