import streamlit as st
from supabase_client import supabase
from helpers import get_family_id

def buylist_module():
    st.subheader("Buy List")
    family_id = get_family_id()
    if not family_id:
        st.error("No family linked to your account.")
        return

    data = supabase.table("buy_list").select("*, database_items(name)").eq("family_id", family_id).execute()
    buy_items = data.data

    for b in buy_items:
        col1, col2, col3 = st.columns([3,2,2])
        col1.write(b["database_items"]["name"])
        new_qty = col2.number_input("Qty", value=float(b["quantity"]), step=1.0, key=f"qty_{b['id']}")
        if col2.button("Update", key=f"update_{b['id']}"):
            supabase.table("buy_list").update({"quantity": new_qty}).eq("id", b["id"]).execute()
        if col3.button("Mark Purchased", key=f"purchase_{b['id']}"):
            supabase.table("stock_list").insert({
                "item_id": b["item_id"],
                "name": b["database_items"]["name"],   # if you kept name
                "quantity": b["quantity"],
                "unit_type": b.get("unit_type", "piece"),   # ✅ include unit_type
                "weight_unit": b.get("weight_unit"),        # optional
                "family_id": b["family_id"]
            }).execute()
            supabase.table("buy_list").delete().eq("id", b["id"]).execute()
            st.success(f"{b['database_items']['name']} moved to Stock List")