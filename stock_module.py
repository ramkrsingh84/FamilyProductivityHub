import streamlit as st
import pandas as pd
from supabase_client import supabase
from helpers import get_family_id, format_timestamp

import streamlit as st
import pandas as pd
from supabase_client import supabase
from helpers import get_family_id, format_timestamp

def stock_module():
    st.subheader("Stock List")
    family_id = get_family_id()
    if not family_id:
        st.error("No family linked to your account.")
        return

    # Fetch stock items for this family
    data = supabase.table("stock_list").select("*").eq("family_id", family_id).execute()
    stock_items = data.data

    if stock_items:
        for s in stock_items:
            s["purchased_date"] = format_timestamp(s["purchased_date"]) if s.get("purchased_date") else "N/A"

            col1, col2, col3, col4 = st.columns([3,2,2,1])
            with col1:
                st.write(f"{s['name']} - {s['quantity']} {s.get('weight_unit') or ''}")
            with col2:
                st.write(f"Purchased {s['purchased_date']}")
            with col3:
                new_status = st.selectbox(
                    "Status",
                    ["available","reducing","exhausted"],
                    index=["available","reducing","exhausted"].index(s.get("status","available")),
                    key=f"status_{s['id']}"
                )
                if new_status != s.get("status"):
                    supabase.table("stock_list").update({"status": new_status}).eq("id", s["id"]).execute()
                    st.success(f"Status updated for {s['name']}")
            with col4:
                if st.button("Move Back", key=f"moveback_{s['id']}"):
                    supabase.table("groceries").insert({
                        "name": s["name"],
                        "quantity": s["quantity"],
                        "unit_type": s["unit_type"],
                        "weight_unit": s.get("weight_unit"),
                        "must_buy_next": True,
                        "family_id": s["family_id"],
                        "added_by": s["added_by"]
                    }).execute()
                    supabase.table("stock_list").delete().eq("id", s["id"]).execute()
                    st.warning(f"{s['name']} moved back to Buy List")