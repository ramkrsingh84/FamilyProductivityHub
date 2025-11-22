from components import render_item_row

def grocery_module():
    st.subheader("Grocery Stock Management")
    # [input form remains unchanged...]

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