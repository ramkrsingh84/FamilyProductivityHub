import streamlit as st
from supabase_client import supabase

# --- Session State for Auth ---
if "user" not in st.session_state:
    st.session_state["user"] = None

st.set_page_config(
    page_title="Family Productivity Hub",
    page_icon="🛒"
)


st.markdown(
    """
    <link rel="manifest" href="manifest.json">
    """,
    unsafe_allow_html=True
)


# --- Helper: Get family_id for current user ---
def get_family_id():
    result = supabase.table("app_users").select("family_id").eq("auth_id", st.session_state["user"].id).execute()
    if result.data and result.data[0]["family_id"]:
        return result.data[0]["family_id"]
    return None

def get_app_user():
    result = supabase.table("app_users").select("id, family_id").eq("auth_id", st.session_state["user"].id).execute()
    if result.data:
        return result.data[0]
    return None


# --- Login ---
def login():
    st.subheader("Login")
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        try:
            user = supabase.auth.sign_in_with_password({"email": email, "password": password})
            if user.user:
                st.session_state["user"] = user.user
                st.success("Logged in successfully!")
                st.rerun()
            else:
                st.error("Login failed: No user returned")
        except Exception as e:
            st.error(f"Login failed: {e}")

# --- Register ---
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

# --- Family Management ---
def family_module():
    st.subheader("Family Management")

    # Create Family
    fam_name = st.text_input("Family Name")
    if st.button("Create Family"):
        family = supabase.table("families").insert({
            "name": fam_name,
            "created_by": st.session_state["user"].id
        }).execute()
        if family.data:
            fam_id = family.data[0]["id"]
            supabase.table("app_users").update({
                "family_id": fam_id,
                "role": "admin"
            }).eq("auth_id", st.session_state["user"].id).execute()
            st.success(f"Family '{fam_name}' created! Share ID: {fam_id}")

    # Join Family
    fam_id = st.text_input("Enter Family ID to join")
    if st.button("Join Family"):
        supabase.table("app_users").update({
            "family_id": fam_id,
            "role": "member"
        }).eq("auth_id", st.session_state["user"].id).execute()
        st.success("Joined family successfully!")

# --- Grocery Management ---
def grocery_module():
    st.subheader("Grocery Stock Management")
    name = st.text_input("Item name")
    quantity = st.number_input("Quantity", min_value=0.0, step=1.0)
    unit_type = st.selectbox("Unit type", ["piece", "weight"])
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
                "must_buy_next": must_buy_next,
                "family_id": family_id,
                "added_by": app_user_id   # ✅ use app_users.id
            }).execute()
            st.success("Item added!")
        else:
            st.error("No family linked to your account. Please create or join a family first.")

    st.write("Current Grocery List:")
    if family_id:
        data = supabase.table("groceries").select("*").eq("family_id", family_id).execute()
        st.table(data.data)

# --- Task Management ---
def task_module():
    st.subheader("Task Management")
    title = st.text_input("Task title")
    description = st.text_area("Description")
    due_date = st.date_input("Due date")
    assigned_to = st.text_input("Assign to (user id)")
    status = st.selectbox("Status", ["pending", "completed"])

    family_id = get_family_id()

    if st.button("Add Task"):
        if family_id:
            supabase.table("tasks").insert({
                "title": title,
                "description": description,
                "due_date": str(due_date),
                "assigned_to": assigned_to,
                "family_id": family_id,
                "status": status
            }).execute()
            st.success("Task added!")
        else:
            st.error("No family linked to your account. Please create or join a family first.")

    st.write("My Tasks:")
    if family_id:
        data = supabase.table("tasks").select("*").eq("family_id", family_id).execute()
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
        st.write(f"👋 Welcome, **{st.session_state['user'].email}**")
        menu = st.sidebar.radio("Menu", ["Family", "Groceries", "Tasks", "Logout"])
        if menu == "Family":
            family_module()
        elif menu == "Groceries":
            grocery_module()
        elif menu == "Tasks":
            task_module()
        elif menu == "Logout":
            st.session_state["user"] = None
            st.success("Logged out!")
            st.rerun()

if __name__ == "__main__":
    main()