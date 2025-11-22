import streamlit as st
from supabase_client import supabase
from helpers import get_family_id, format_timestamp

def stock_module():
    st.subheader("Stock List")
    family_id = get_family_id()
    if not family_id:
        st.error("No family linked to your account.")
        return

    data = supabase.table("stock_list").select("*, database_items(name)").eq("family_id", family_id).execute()
    stock_items = data.data

    for s in stock_items:
        col1, col2, col3, col4, col5 = st.columns([3,2,2,2,2])
        col1.write(f"{s['database_items']['name']} - {s['quantity']}")
        col2.write(format_timestamp(s.get("purchased_date")))
        new_status = col3.selectbox("Status", ["available","reducing","exhausted"],
                                    index=["available","reducing","exhausted"].index(s["status"]),
                                    key=f"status_{s['id']}")
        if new_status != s["status"]:
            supabase.table("stock_list").update({"status": new_status}).eq("id", s["id"]).execute()
        if col4.button("Update Qty", key=f"stockupdate_{s['id']}"):
            new_qty = st.number_input("Qty", value=float(s["quantity"]), step=1.0, key=f"qty_{s['id']}")
            supabase.table("stock_list").update({"quantity": new_qty}).eq("id", s["id"]).execute()
            st.success(f"{s['database_items']['name']} stock updated to {new_qty}")
        if new_status == "exhausted":
            if col5.button("Move Back to Database", key=f"moveback_{s['id']}"):
                supabase.table("stock_list").delete().eq("id", s["id"]).execute()
                st.warning(f"{s['database_items']['name']} moved back to Database")