import streamlit as st
from auth import login, register
from family import family_module
from groceries import grocery_module
from tasks import task_module
from helpers import get_user_name
from stock_module import stock_module

if "user" not in st.session_state:
    st.session_state["user"] = None

st.set_page_config(page_title="Family Productivity Hub", page_icon="🛒")

def main():
    st.title("🏠 Family Productivity Hub")

    if st.session_state["user"] is None:
        choice = st.radio("Choose action", ["Login", "Register"])
        if choice == "Login":
            login()
        else:
            register()
    else:
        user_name = get_user_name()
        st.write(f"👋 Welcome, **{user_name}**")
        menu = st.sidebar.radio("Menu", ["Family", "Groceries", "Stock List", "Tasks", "Logout"])
        if menu == "Family":
            family_module()
        elif menu == "Groceries":
            grocery_module()
        elif menu == "Stock List":
            stock_module()
        elif menu == "Tasks":
            task_module()
        elif menu == "Logout":
            st.session_state["user"] = None
            st.success("Logged out!")
            st.rerun()

if __name__ == "__main__":
    main()