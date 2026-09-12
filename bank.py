import streamlit as st
import json
import os
import random
from datetime import datetime

# --- PAGE CONFIGURATION ---
st.set_page_config(page_title="Apex Virtual Bank", page_icon="🏦", layout="centered")

# --- DATABASE MANAGEMENT ---
DB_FILE = "bank_db.json"

def load_db():
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r") as f:
            return json.load(f)
    return {}

def save_db(data):
    with open(DB_FILE, "w") as f:
        json.dump(data, f, indent=4)

if 'db' not in st.session_state:
    st.session_state.db = load_db()
if 'logged_in_acc' not in st.session_state:
    st.session_state.logged_in_acc = None

def generate_account_number():
    while True:
        acc_num = '9' + ''.join([str(random.randint(0, 9)) for _ in range(9)])
        if acc_num not in st.session_state.db:
            return acc_num

def get_time():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

# ==========================================
# APP INTERFACE: NOT LOGGED IN (Welcome / Me / Auth)
# ==========================================
if st.session_state.logged_in_acc is None:
    st.title("The Smarter Way to Bank 🚀")
    st.caption("Free Transfers | Top Savings Rate | Reliable Service")
    
    # Bottom-style or main menu options like the reference image
    choice = st.radio("Select an Option:", ["Login", "Open an Account", "USSD Service", "Customer Service", "Security Center"])
    
    if choice == "Login":
        st.subheader("Customer Login")
        with st.container(border=True):
            login_acc = st.text_input("10-Digit Account Number:")
            login_pin = st.text_input("Enter 4-digit PIN:", type="password", max_chars=4)
            
            if st.button("Login to Dashboard", use_container_width=True):
                st.session_state.db = load_db()
                if login_acc in st.session_state.db:
                    if st.session_state.db[login_acc]["pin"] == login_pin:
                        st.session_state.logged_in_acc = login_acc
                        st.rerun()
                    else:
                        st.error("Incorrect PIN.")
                else:
                    st.error("Account Number not found.")

    elif choice == "Open an Account":
        st.subheader("Open a New Bank Account")
        with st.container(border=True):
            new_name = st.text_input("Enter Your Full Name:")
            new_pin = st.text_input("Choose a 4-digit PIN:", type="password", max_chars=4)
            
            if st.button("Create Account", use_container_width=True):
                if not new_name or not new_pin:
                    st.error("Please fill in all fields.")
                elif len(new_pin) != 4 or not new_pin.isdigit():
                    st.error("PIN must be exactly 4 digits.")
                else:
                    st.session_state.db = load_db()
                    acc_num = generate_account_number()
                    st.session_state.db[acc_num] = {
                        "name": new_name,
                        "pin": new_pin,
                        "balance": 0.0,
                        "history": [f"[{get_time()}] Account created successfully."]
                    }
                    save_db(st.session_state.db)
                    st.success("🎉 Account Created Successfully!")
                    st.info(f"**Your Account Number: {acc_num}**")

    elif choice == "USSD Service":
        st.subheader("📱 Quick USSD Banking")
        st.info("Dial `*999#` offline on any mobile network to check balances and perform quick transfers without internet data.")

    elif choice == "Customer Service":
        st.subheader("🎧 24/7 Support Center")
        st.write("Need help? Reach out to our virtual bank representatives.")
        st.text("Email: support@apexbank.com")
        st.text("Helpline: 0800-APEX-BANK")

    elif choice == "Security Center":
        st.subheader("🛡️ Security & Privacy Center")
        st.write("Your account is protected with advanced encryption and secure 4-digit PIN verification.")

# ==========================================
# APP INTERFACE: LOGGED IN DASHBOARD
# ==========================================
else:
    st.session_state.db = load_db()
    acc_num = st.session_state.logged_in_acc
    user_data = st.session_state.db[acc_num]
    
    # Fintech bottom-style navigation menu simulation using radio tabs
    nav = st.radio("Menu", ["🏠 Home", "💸 Transactions", "📊 Wealth / Savings", "🎁 Rewards", "⚙️ Me / Profile"], horizontal=True)
    
    st.divider()
    
    if nav == "🏠 Home":
        st.subheader(f"Welcome back, {user_data['name']} 👋")
        st.markdown(f"**Account Number:** `{acc_num}`")
        st.metric(label="Available Balance", value=f"₦{user_data['balance']:,.2f}")
        
        st.markdown("### Quick Actions")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Deposit Funds", use_container_width=True):
                st.session_state.quick_action = "Deposit"
        with col2:
            if st.button("Send Money", use_container_width=True):
                st.session_state.quick_action = "Transfer"
                
        # Handle quick action display if clicked
        action = st.session_state.get("quick_action", "Deposit")
        if action == "Deposit":
            st.write("---")
            st.write("#### Instant Deposit")
            dep_amount = st.number_input("Amount (₦):", min_value=0.0, step=500.0)
            if st.button("Confirm Deposit"):
                if dep_amount > 0:
                    user_data['balance'] += dep_amount
                    user_data['history'].append(f"[{get_time()}] Deposited: +₦{dep_amount:,.2f}")
                    save_db(st.session_state.db)
                    st.success("Deposit successful!")
                    st.rerun()
        else:
            st.write("---")
            st.write("#### Transfer Funds")
            rec_acc = st.text_input("Receiver's 10-Digit Account Number:")
            trans_amount = st.number_input("Amount to send (₦):", min_value=0.0, step=500.0)
            trans_pin = st.text_input("Confirm PIN:", type="password", max_chars=4)
            if st.button("Send Now"):
                if trans_pin != user_data['pin']:
                    st.error("Incorrect PIN.")
                elif rec_acc not in st.session_state.db:
                    st.error("Receiver not found.")
                elif trans_amount > user_data['balance']:
                    st.error("Insufficient funds.")
                else:
                    user_data['balance'] -= trans_amount
                    user_data['history'].append(f"[{get_time()}] Transfer to {rec_acc}: -₦{trans_amount:,.2f}")
                    st.session_state.db[rec_acc]['balance'] += trans_amount
                    st.session_state.db[rec_acc]['history'].append(f"[{get_time()}] Received from {acc_num}: +₦{trans_amount:,.2f}")
                    save_db(st.session_state.db)
                    st.success("Transfer successful!")
                    st.rerun()

    elif nav == "💸 Transactions":
        st.subheader("📜 Transaction History")
        with st.container(border=True):
            for record in reversed(user_data['history']):
                st.text(record)

    elif nav == "📊 Wealth / Savings":
        st.subheader("💰 Apex Target Savings")
        st.write("Lock funds to earn up to 15% interest per annum.")
        st.info("No active savings plans yet. Create one to start growing your wealth!")

    elif nav == "🎁 Rewards":
        st.subheader("🎉 Cashback & Rewards")
        st.write("Earn points on every transfer and deposit you make.")
        st.metric("Reward Points", "1,250 pts")

    elif nav == "⚙️ Me / Profile":
        st.subheader("User Profile & Settings")
        st.write(f"**Name:** {user_data['name']}")
        st.write(f"**Account Number:** {acc_num}")
        
        if st.button("Log Out", type="primary", use_container_width=True):
            st.session_state.logged_in_acc = None
            st.rerun()
