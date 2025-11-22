import streamlit as st
from datetime import datetime
from supabase_client import supabase
from helpers import get_app_user, format_timestamp

# --- Grocery Management ---
def grocery_module():
    st.subheader("Grocery Stock Management")
    name = st.text_input("Item name")
    quantity = st.number_input("Quantity", min_value=0.0, step=1.0)

    # First dropdown: piece or weight
    unit_type = st.selectbox("Unit type", ["piece", "weight"])

    # Second dropdown: always visible, optional
    weight_unit = st.selectbox(
        "Select unit (optional)",
        ["", "kg", "gram", "liter", "ml", "ounce", "pound"]
    )

    must_buy_next = st.checkbox("Must buy next visit")

    app_user = get_app_user()
    if app_user:
        family_id = app_user["family_id"]
        app_user_id = app_user["id"]
    else:
        family_id = None
        app_user_id = None

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

    st.write("Current Grocery List:")
    if family_id:
        data = supabase.table("groceries").select("*").eq("family_id", family_id).execute()
        groceries = data.data

        for g in groceries:
            # Lookup added_by user name but keep UUID intact
            user_lookup = supabase.table("app_users").select("name").eq("id", g["added_by"]).execute()
            g["added_by_name"] = user_lookup.data[0]["name"] if user_lookup.data else "Unknown"
            g["created_at"] = format_timestamp(g["created_at"])

            # Display unit nicely
            if g["unit_type"] == "piece":
                g["unit_display"] = f"{g['quantity']} pieces"
            elif g["unit_type"] == "weight":
                if g.get("weight_unit"):
                    g["unit_display"] = f"{g['quantity']} {g['weight_unit']}"
                else:
                    g["unit_display"] = f"{g['quantity']} (weight)"
            else:
                g["unit_display"] = str(g["quantity"])

            # Show item + Mark Purchased button
            col1, col2 = st.columns([3,1])
            with col1:
                st.write(f"{g['name']} - {g['unit_display']} (Added by {g['added_by_name']})")
            with col2:
                if st.button("Mark Purchased", key=f"purchase_{g['id']}"):
                    supabase.table("stock_list").insert({
                        "grocery_id": g["id"],
                        "name": g["name"],
                        "quantity": g["quantity"],
                        "unit_type": g["unit_type"],
                        "weight_unit": g.get("weight_unit"),
                        "family_id": g["family_id"],
                        "added_by": g["added_by"]   # ✅ still UUID
                    }).execute()
                    supabase.table("groceries").delete().eq("id", g["id"]).execute()
                    st.success(f"{g['name']} moved to Stock List")

        import pandas as pd
        df = pd.DataFrame(groceries)
        # Drop raw UUIDs and internal columns
        df = df.drop(columns=["id", "family_id", "unit_type", "weight_unit", "added_by"], errors="ignore")
        # Keep added_by_name for display
        st.dataframe(df)
           