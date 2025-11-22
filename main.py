import streamlit as st
from supabase_client import supabase

# --- Session State for Auth ---
if "user" not in st.session_state:
    st.session_state["user"] = None

# --- Login / Register ---
def login():
    st.subheader("Login")
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        try:
            user = supabase.auth.sign_in_with_password({"email": email, "password": password})
            if user.user:  # ensure login succeeded
                st.session_state["user"] = user.user
                st.success("Logged in successfully!")
                st.experimental_rerun()  # force app to reload into main menu
            else:
                st.error("Login failed: No user returned")
        except Exception as e:
            st.error(f"Login failed: {e}")


def register():
    st.subheader("Register")
    email = st.text_input("Email (register)")
    password = st.text_input("Password (register)", type="password")
    if st.button("Register"):
        try:
            user = supabase.auth.sign_up({"email": email, "password": password})
            if user.user:
                supabase.table("app_users").insert({
                    "auth_id": user.user.id,
                    "name": email.split("@")[0],
                    "role": "member",
                    "family_id": None
                }).execute()
                st.success("Registered successfully! Please login.")
            else:
                st.error("Registration failed: No user returned")
        except Exception as e:
            st.error(f"Registration failed: {e}")


# --- Grocery Management ---
def grocery_module():
    st.subheader("Grocery Stock Management")
    name = st.text_input("Item name")
    quantity = st.number_input("Quantity", min_value=0.0, step=1.0)
    unit_type = st.selectbox("Unit type", ["piece", "weight"])
    must_buy_next = st.checkbox("Must buy next visit")

    if st.button("Add Grocery"):
        supabase.table("groceries").insert({
            "name": name,
            "quantity": quantity,
            "unit_type": unit_type,
            "must_buy_next": must_buy_next,
            "family_id": 1,  # placeholder family id
            "added_by": st.session_state["user"].user.id
        }).execute()
        st.success("Item added!")

    st.write("Current Grocery List:")
    data = supabase.table("groceries").select("*").execute()
    st.table(data.data)

# --- Task Management ---
def task_module():
    st.subheader("Task Management")
    title = st.text_input("Task title")
    description = st.text_area("Description")
    due_date = st.date_input("Due date")
    assigned_to = st.text_input("Assign to (user id)")
    status = st.selectbox("Status", ["pending", "completed"])

    if st.button("Add Task"):
        supabase.table("tasks").insert({
            "title": title,
            "description": description,
            "due_date": str(due_date),
            "assigned_to": assigned_to,
            "family_id": 1,  # placeholder family id
            "status": status
        }).execute()
        st.success("Task added!")

    st.write("My Tasks:")
    data = supabase.table("tasks").select("*").execute()
    st.table(data.data)

# --- Main App ---
def main():
    st.title("🏠 Family Productivity Hub")

    if st.session_state["user"] is None:
        choice = st.radio("Choose action", ["Login", "Register"])
        if choice == "Login":
            login()
        else:
            register()
    else:
        menu = st.sidebar.radio("Menu", ["Groceries", "Tasks", "Logout"])
        if menu == "Groceries":
            grocery_module()
        elif menu == "Tasks":
            task_module()
        elif menu == "Logout":
            st.session_state["user"] = None
            st.success("Logged out!")
            st.experimental_rerun()


if __name__ == "__main__":
    main()