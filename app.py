import re
import streamlit as st
import pandas as pd

from hello import Bank


# ---------------- PAGE CONFIGURATION ----------------

st.set_page_config(
    page_title="NextGen Bank",
    page_icon="🏦",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ---------------- CUSTOM CSS ----------------

st.markdown("""
<style>
    .main {
        background-color: #f5f7fb;
    }

    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }

    [data-testid="stMetric"] {
        background-color: white;
        padding: 20px;
        border-radius: 12px;
        border: 1px solid #e5e7eb;
    }

    div.stButton > button {
        width: 100%;
        border-radius: 8px;
        height: 45px;
        font-weight: 600;
    }

    div[data-testid="stForm"] {
        background-color: white;
        padding: 20px;
        border-radius: 12px;
        border: 1px solid #e5e7eb;
    }
</style>
""", unsafe_allow_html=True)


# ---------------- VALIDATION FUNCTIONS ----------------

def valid_pin(pin):
    return (
        isinstance(pin, str)
        and len(pin) == 4
        and pin.isdigit()
    )


def valid_email(email):
    return bool(
        re.fullmatch(
            r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}",
            email.strip()
        )
    )


def show_result(result, message):

    if result:
        st.success(message)
    else:
        st.error(message)


# ---------------- SIDEBAR ----------------

st.sidebar.title("🏦 NextGen Bank")

st.sidebar.caption("Banking made simple and secure")

menu = st.sidebar.radio(
    "Navigation",
    [
        "Home",
        "Create Account",
        "Deposit",
        "Withdraw",
        "Show Details",
        "Transaction History",
        "Update Info",
        "Delete Account"
    ]
)

st.sidebar.divider()

st.sidebar.info(
    "Your banking information is stored in the JSON database."
)


# ---------------- HOME ----------------

if menu == "Home":

    st.title("Welcome to NextGen Bank 👋")

    st.write(
        "Manage your bank account easily through our "
        "simple and secure banking application."
    )

    st.divider()

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Banking", "24/7")

    with col2:
        st.metric("Account Creation", "Easy")

    with col3:
        st.metric("Transactions", "Simple")

    st.subheader("Available Services")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("""
        ### 💳 Account Management

        - Create a new account
        - View account information
        - Update personal details
        - Delete an account
        """)

    with col2:
        st.markdown("""
        ### 💰 Banking Services

        - Deposit money
        - Withdraw money
        - Check account balance
        - View transaction history
        """)

    st.divider()

    st.info("Select a service from the sidebar to get started.")


# ---------------- CREATE ACCOUNT ----------------

elif menu == "Create Account":

    st.title("📝 Create Your Account")

    st.write("Fill in the details below to open a new account.")

    with st.form("create_account_form"):

        name = st.text_input("Full Name")

        age = st.number_input(
            "Age",
            min_value=18,
            max_value=120,
            value=18,
            step=1
        )

        email = st.text_input("Email Address")

        pin = st.text_input(
            "Create 4-digit PIN",
            type="password",
            max_chars=4
        )

        confirm_pin = st.text_input(
            "Confirm PIN",
            type="password",
            max_chars=4
        )

        submitted = st.form_submit_button(
            "Create Account",
            type="primary"
        )

        if submitted:

            if not name.strip():
                st.error("Please enter your name.")

            elif not valid_email(email):
                st.error("Please enter a valid email address.")

            elif not valid_pin(pin):
                st.error("PIN must contain exactly 4 digits.")

            elif pin != confirm_pin:
                st.error("PINs do not match.")

            else:

                try:
                    user, msg = Bank.create_account(
                        name.strip(),
                        int(age),
                        email.strip(),
                        pin
                    )

                    if user:

                        st.success(msg)

                        st.balloons()

                        st.subheader("Your Account Details")

                        st.info(
                            f"Your account number is: "
                            f"{user['accountNo.']}"
                        )

                        st.warning(
                            "Please save your account number "
                            "safely. You will need it to access "
                            "your account."
                        )

                    else:
                        st.error(msg)

                except Exception as error:
                    st.error(f"Something went wrong: {error}")


# ---------------- DEPOSIT ----------------

elif menu == "Deposit":

    st.title("💰 Deposit Money")

    with st.form("deposit_form"):

        acc_no = st.text_input("Account Number")

        pin = st.text_input(
            "Account PIN",
            type="password",
            max_chars=4
        )

        amount = st.number_input(
            "Deposit Amount",
            min_value=1,
            max_value=10000,
            value=100,
            step=1
        )

        submitted = st.form_submit_button(
            "Deposit Money",
            type="primary"
        )

        if submitted:

            if not acc_no.strip():
                st.error("Enter your account number.")

            elif not valid_pin(pin):
                st.error("Enter a valid 4-digit PIN.")

            else:

                try:
                    success, msg = Bank.deposit(
                        acc_no.strip(),
                        pin,
                        int(amount)
                    )

                    show_result(success, msg)

                except Exception as error:
                    st.error(f"Transaction failed: {error}")


# ---------------- WITHDRAW ----------------

elif menu == "Withdraw":

    st.title("💸 Withdraw Money")

    with st.form("withdraw_form"):

        acc_no = st.text_input("Account Number")

        pin = st.text_input(
            "Account PIN",
            type="password",
            max_chars=4
        )

        amount = st.number_input(
            "Withdrawal Amount",
            min_value=1,
            value=100,
            step=1
        )

        submitted = st.form_submit_button(
            "Withdraw Money",
            type="primary"
        )

        if submitted:

            if not acc_no.strip():
                st.error("Enter your account number.")

            elif not valid_pin(pin):
                st.error("Enter a valid 4-digit PIN.")

            else:

                try:
                    success, msg = Bank.withdraw(
                        acc_no.strip(),
                        pin,
                        int(amount)
                    )

                    show_result(success, msg)

                except Exception as error:
                    st.error(f"Transaction failed: {error}")


# ---------------- SHOW DETAILS ----------------

elif menu == "Show Details":

    st.title("👤 Account Details")

    with st.form("details_form"):

        acc_no = st.text_input("Account Number")

        pin = st.text_input(
            "Account PIN",
            type="password",
            max_chars=4
        )

        submitted = st.form_submit_button(
            "View Account",
            type="primary"
        )

        if submitted:

            if not acc_no.strip():
                st.error("Enter your account number.")

            elif not valid_pin(pin):
                st.error("Enter a valid 4-digit PIN.")

            else:

                try:
                    user = Bank.find_user(
                        acc_no.strip(),
                        pin
                    )

                    if user:

                        st.success("Account verified!")

                        st.subheader(
                            f"Welcome, {user['name']}!"
                        )

                        col1, col2 = st.columns(2)

                        with col1:
                            st.metric(
                                "Available Balance",
                                f"₹{user['balance']:,}"
                            )

                        with col2:
                            st.metric(
                                "Account Age",
                                f"{user['age']} years"
                            )

                        st.divider()

                        st.write("### Personal Information")

                        st.write(
                            f"**Name:** {user['name']}"
                        )

                        st.write(
                            f"**Email:** {user['email']}"
                        )

                        st.write(
                            f"**Account Number:** "
                            f"{user['accountNo.']}"
                        )

                    else:
                        st.error("Invalid account number or PIN.")

                except Exception as error:
                    st.error(f"Unable to retrieve details: {error}")


# ---------------- TRANSACTION HISTORY ----------------

elif menu == "Transaction History":

    st.title("📊 Transaction History")

    with st.form("history_form"):

        acc_no = st.text_input("Account Number")

        pin = st.text_input(
            "Account PIN",
            type="password",
            max_chars=4
        )

        submitted = st.form_submit_button(
            "View Transactions",
            type="primary"
        )

        if submitted:

            if not acc_no.strip():
                st.error("Enter your account number.")

            elif not valid_pin(pin):
                st.error("Enter a valid 4-digit PIN.")

            else:

                try:
                    transactions, msg = Bank.transaction_history(
                        acc_no.strip(),
                        pin
                    )

                    if transactions is None:
                        st.error(msg)

                    elif not transactions:
                        st.info("No transactions found.")

                    else:

                        st.success(msg)

                        df = pd.DataFrame(transactions)

                        df.index = range(1, len(df) + 1)

                        df.index.name = "Transaction No."

                        st.dataframe(
                            df,
                            use_container_width=True
                        )

                except Exception as error:
                    st.error(f"Unable to retrieve history: {error}")


# ---------------- UPDATE INFO ----------------

elif menu == "Update Info":

    st.title("⚙️ Update Account Information")

    with st.form("update_form"):

        acc_no = st.text_input("Account Number")

        pin = st.text_input(
            "Current PIN",
            type="password",
            max_chars=4
        )

        st.write("### New Information")

        name = st.text_input("New Name (Optional)")

        email = st.text_input("New Email (Optional)")

        new_pin = st.text_input(
            "New PIN (Optional)",
            type="password",
            max_chars=4
        )

        submitted = st.form_submit_button(
            "Update Information",
            type="primary"
        )

        if submitted:

            if not acc_no.strip():
                st.error("Enter your account number.")

            elif not valid_pin(pin):
                st.error("Current PIN must contain 4 digits.")

            elif email and not valid_email(email):
                st.error("Enter a valid email address.")

            elif new_pin and not valid_pin(new_pin):
                st.error("New PIN must contain exactly 4 digits.")

            else:

                try:
                    success, msg = Bank.update_user(
                        acc_no.strip(),
                        pin,
                        name=name.strip() or None,
                        email=email.strip() or None,
                        new_pin=new_pin or None
                    )

                    show_result(success, msg)

                except Exception as error:
                    st.error(f"Unable to update account: {error}")


# ---------------- DELETE ACCOUNT ----------------

elif menu == "Delete Account":

    st.title("🗑️ Delete Account")

    st.warning(
        "Deleting your account is permanent. "
        "Your account information and transaction history "
        "will be removed."
    )

    with st.form("delete_form"):

        acc_no = st.text_input("Account Number")

        pin = st.text_input(
            "Account PIN",
            type="password",
            max_chars=4
        )

        confirm = st.checkbox(
            "I understand that this action cannot be undone."
        )

        submitted = st.form_submit_button(
            "Delete Account",
            type="primary"
        )

        if submitted:

            if not acc_no.strip():
                st.error("Enter your account number.")

            elif not valid_pin(pin):
                st.error("Enter a valid 4-digit PIN.")

            elif not confirm:
                st.error("Please confirm account deletion.")

            else:

                try:
                    success, msg = Bank.delete_user(
                        acc_no.strip(),
                        pin
                    )

                    show_result(success, msg)

                except Exception as error:
                    st.error(f"Unable to delete account: {error}")
