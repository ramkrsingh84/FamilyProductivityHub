import streamlit as st
import pandas as pd
from supabase_client import supabase
from helpers import get_family_id

CATEGORIES = [
    "Vegetables","Fruits","Bakery","Meat & Seafood","Dairy & Eggs",
    "Frozen Food","Pantry/Staples","Snacks","Beverages","Condiments & Sauces",
    "Household","Personal Care","Baby Products","Pet Supplies",
    "Breakfast & Grains","Other"
]


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
    category = st.selectbox("Category", CATEGORIES)
    if st.button("Add to Database"):
        supabase.table("groceries").insert({
            "name": name,
            "quantity": 1,
            "unit_type": unit,
            "weight_unit": weight_unit if weight_unit else None,
            "family_id": family_id,
            "category": category
        }).execute()
        st.success("Item added to database")
        st.rerun()

    # Show items
    data = supabase.table("groceries").select("*").eq("family_id", family_id).execute()
    items = data.data
    if not items:
        st.info("No items in Database")
        return
    
    # 🔎 Category filter
    filter_cat = st.selectbox("Filter by Category", ["All"] + CATEGORIES)
    if filter_cat != "All":
        items = [i for i in items if i.get("category") == filter_cat]

    df = pd.DataFrame([{
        "Item": i["name"],
        "Category": i.get("category","Other"),
        "Unit Type": i["unit_type"],
        "Weight Unit": i["weight_unit"] or "",
        "Quantity": i["quantity"]
    } for i in items])
    st.dataframe(df, width="stretch")

    # Selection dropdown
    selected_item = st.selectbox(
        "Select an item to manage",
        options=[f"{i['name']} ({i.get('category','Other')})" for i in items],
        index=None,
        placeholder="Choose an item..."
    )

    if selected_item:
        chosen = next(i for i in items if selected_item.startswith(i["name"]))
        st.markdown(f"---\n### Manage: **{chosen['name']}**")

        new_name = st.text_input("Edit Name", value=chosen["name"], key=f"name_{chosen['id']}")
        new_unit = st.selectbox("Edit Unit Type", ["piece","weight"],
                                index=["piece","weight"].index(chosen["unit_type"]),
                                key=f"unit_{chosen['id']}")
        new_weight_unit = st.selectbox("Edit Weight Unit",
                                       ["","kg","gram","liter","ml","ounce","pound"],
                                       index=(["","kg","gram","liter","ml","ounce","pound"].index(chosen["weight_unit"])
                                              if chosen["weight_unit"] else 0),
                                       key=f"wunit_{chosen['id']}")
        new_category = st.selectbox("Edit Category", CATEGORIES,
                                    index=CATEGORIES.index(chosen.get("category","Other")),
                                    key=f"cat_{chosen['id']}")

        cols = st.columns([1,1,1])
        if cols[0].button("Update", key=f"update_{chosen['id']}"):
            supabase.table("groceries").update({
                "name": new_name,
                "unit_type": new_unit,
                "weight_unit": new_weight_unit if new_weight_unit else None,
                "category": new_category
            }).eq("id", chosen["id"]).execute()
            st.success(f"{chosen['name']} updated")
            st.rerun()

        if cols[1].button("Delete", key=f"delete_{chosen['id']}"):
            supabase.table("groceries").delete().eq("id", chosen["id"]).execute()
            st.warning(f"{chosen['name']} deleted from Database")
            st.rerun()

        if cols[2].button("Copy to Buy List", key=f"copy_{chosen['id']}"):
            supabase.table("buy_list").insert({
                "item_id": chosen["id"],
                "name": chosen["name"],
                "quantity": 1,
                "unit_type": chosen["unit_type"],
                "weight_unit": chosen["weight_unit"],
                "family_id": family_id,
                "category": chosen.get("category","Other")
            }).execute()
            st.success(f"{chosen['name']} copied to Buy List")
