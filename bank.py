import streamlit as st
import json
import os
import random
from datetime import datetime

# --- PAGE CONFIGURATION ---
st.set_page_config(page_title="Apex Virtual Bank Pro", page_icon="🏦", layout="centered")

# --- DATABASE MANAGEMENT ---
DB_FILE = "bank_db.json"
ADMIN_SECRET = "ApexFounder2026"  # Your hardcoded admin password

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
if 'is_admin' not in st.session_state:
    st.session_state.is_admin = False

def generate_account_number():
    while True:
        acc_num = '9' + ''.join([str(random.randint(0, 9)) for _ in range(9)])
        if acc_num not in st.session_state.db:
            return acc_num

def get_time():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

# --- REFERENCE DATA ---
NIGERIAN_STATES = [
    "Abia", "Adamawa", "Akwa Ibom", "Anambra", "Bauchi", "Bayelsa", "Benue", "Borno", 
    "Cross River", "Delta", "Ebonyi", "Edo", "Ekiti", "Enugu", "Gombe", "Imo", 
    "Jigawa", "Kaduna", "Kano", "Katsina", "Kebbi", "Kogi", "Kwara", "Lagos", 
    "Nasarawa", "Niger", "Ogun", "Ondo", "Osun", "Oyo", "Plateau", "Rivers", 
    "Sokoto", "Taraba", "Yobe", "Zamfara", "Federal Capital Territory (FCT)"
]

OCCUPATIONS = [
    "Student", "Software Developer", "Medical Doctor", "Trader / Merchant", 
    "Civil Servant", "Engineer", "Entrepreneur / Business Owner", "Banker / FinTech", 
    "Lawyer", "Accountant", "Designer", "Teacher / Lecturer", "Artisan / Craftsman", "Other"
]

MARITAL_STATUSES = ["Single", "Married", "Divorced", "Widowed", "Prefer not to say"]
# ==========================================
# 1. ADMIN LOGIN VIEW
# ==========================================
if st.session_state.is_admin:
    st.title("👑 Apex Bank - Founder / Admin Portal")
    st.markdown("Full systemic control, liquidity management, and customer support resolution.")
    
    admin_tab1, admin_tab2, admin_tab3 = st.tabs(["📊 Client Accounts & Funding", "🛡️ Fraud & Freeze Control", "💬 Support Tickets"])

    # --- CLIENT ACCOUNTS & FUNDING ---
    with admin_tab1:
        st.subheader("Registered Client Directory & Transaction Inspector")
        st.session_state.db = load_db()
        
        if not st.session_state.db:
            st.info("No accounts created yet.")
        else:
            acc_list = list(st.session_state.db.keys())
            selected_acc = st.selectbox("Select Account Number to Manage:", acc_list)
            
            if selected_acc:
                client = st.session_state.db[selected_acc]
                with st.container(border=True):
                    surname = client.get('surname', client.get('name', 'Unknown'))
                    mid_name = client.get('middle_name', '')
                    last_name = client.get('last_name', '')
                    
                    st.write(f"**Name:** {surname} {mid_name} {last_name}")
                    st.write(f"**Account Status:** {'🟢 Active' if client.get('status', 'active') == 'active' else '🔴 Frozen'}")
                    st.write(f"**Balance:** ₦{client.get('balance', 0.0):,.2f}")
                    st.write(f"**Max Single Incoming Limit:** ₦{client.get('expected_limit', 0):,.2f}")
                    st.write(f"**Occupation:** {client.get('occupation', 'N/A')} | **State:** {client.get('state_of_origin', 'N/A')}")
                    
                    st.divider()
                    st.write("📜 **User Transaction History / Statement:**")
                    history_list = client.get('history', [])
                    if history_list:
                        for h in reversed(history_list):
                            st.text(h)
                    else:
                        st.info("No transactions recorded yet.")
                    
                    st.divider()
                    st.write("#### Fund / Credit Account")
                    fund_amount = st.number_input("Amount to inject (₦):", min_value=0.0, step=1000.0, key=f"fund_{selected_acc}")
                    if st.button("Authorize Founder Credit"):
                        client['balance'] = client.get('balance', 0.0) + fund_amount
                        if 'history' not in client:
                            client['history'] = []
                        client['history'].append(f"[{get_time()}] Founder Credited: +₦{fund_amount:,.2f}")
                        save_db(st.session_state.db)
                        st.success(f"Successfully credited ₦{fund_amount:,.2f} to {selected_acc}!")
                        st.rerun()

    
    # --- FRAUD & FREEZE CONTROL ---
    with admin_tab2:
        st.subheader("Account Freeze & Security Control")
        st.write("Freeze suspicious accounts or unfreeze accounts flagged for exceeding expected daily limits.")
        
        st.session_state.db = load_db()
        if st.session_state.db:
            for acc, data in st.session_state.db.items():
                col1, col2, col3 = st.columns([2, 2, 1])
                with col1:
                    s_name = data.get('surname', data.get('name', 'User'))
                    st.text(f"{acc} - {s_name}")
                with col2:
                    status = data.get('status', 'active')
                    st.text(f"Status: {status.upper()}")
                with col3:
                    if status == 'active':
                        if st.button("Freeze", key=f"freeze_{acc}"):
                            data['status'] = 'frozen'
                            if 'history' not in data:
                                data['history'] = []
                            data['history'].append(f"[{get_time()}] Account frozen by Admin.")
                            save_db(st.session_state.db)
                            st.rerun()
                    else:
                        if st.button("Unfreeze", key=f"unfreeze_{acc}"):
                            data['status'] = 'active'
                            if 'history' not in data:
                                data['history'] = []
                            data['history'].append(f"[{get_time()}] Account unfrozen by Admin.")
                            save_db(st.session_state.db)
                            st.rerun()

    # --- SUPPORT TICKETS ---
    with admin_tab3:
        st.subheader("Customer Support Inbox")
        st.session_state.db = load_db()
        ticket_found = False
        
        for acc, data in st.session_state.db.items():
            if "tickets" in data and data["tickets"]:
                for idx, ticket in enumerate(data["tickets"]):
                    ticket_found = True
                    with st.container(border=True):
                        s_name = data.get('surname', data.get('name', 'User'))
                        st.markdown(f"**From Account:** `{acc}` ({s_name})")
                        st.markdown(f"**Issue:** {ticket['message']}")
                        st.markdown(f"**Status:** `{ticket['status']}`")
                        
                        admin_reply = st.text_input("Reply to User / Provide Solution:", key=f"reply_{acc}_{idx}")
                        if st.button("Send Reply & Resolve", key=f"send_reply_{acc}_{idx}"):
                            ticket['admin_response'] = admin_reply
                            ticket['status'] = 'Resolved'
                            save_db(st.session_state.db)
                            st.success("Response sent to user!")
                            st.rerun()
        if not ticket_found:
            st.info("No pending support tickets.")

    st.divider()
    if st.button("Exit Admin Portal"):
        st.session_state.is_admin = False
        st.rerun()


        

# ==========================================
# 2. STANDARD USER / PUBLIC VIEW
# ==========================================
elif st.session_state.logged_in_acc is None:
    st.title("🏦 Apex Virtual Bank Pro")
    st.caption("The Smarter, Fully Digitized Way to Bank | Secure Core Infrastructure")
    
    choice = st.sidebar.radio("Navigation", ["Login", "Open an Account", "Admin Portal Login", "Help / Support Desk"])
    
    # --- LOGIN ---
    if choice == "Login":
        st.subheader("Customer Portal Login")
        with st.container(border=True):
            login_acc = st.text_input("10-Digit Account Number:")
            login_pin = st.text_input("Enter 4-digit PIN:", type="password", max_chars=4)
            
            if st.button("Secure Login", use_container_width=True):
                st.session_state.db = load_db()
                if login_acc in st.session_state.db:
                    user = st.session_state.db[login_acc]
                    if user["pin"] == login_pin:
                        st.session_state.logged_in_acc = login_acc
                        st.rerun()
                    else:
                        st.error("Incorrect PIN.")
                else:
                    st.error("Account Number not found.")

    # --- OPEN AN ACCOUNT (DETAILED FORM & CONFIRMATION) ---
    elif choice == "Open an Account":
        st.subheader("Open a New Verified Bank Account")
        
        # Initialize form stage tracking
        if 'form_stage' not in st.session_state:
            st.session_state.form_stage = "input"
            
        if st.session_state.form_stage == "input":
            with st.form("account_form"):
                st.markdown("### Personal Information")
                col1, col2 = st.columns(2)
                with col1:
                    surname = st.text_input("Surname *")
                    first_name = st.text_input("First Name *")
                with col2:
                    middle_name = st.text_input("Middle Name")
                    nationality = st.text_input("Nationality *", value="Nigerian")
                
                state_of_origin = st.selectbox("State of Origin *", NIGERIAN_STATES)
                marital_status = st.selectbox("Marital Status *", MARITAL_STATUSES)
                occupation = st.selectbox("Occupation *", OCCUPATIONS)
                
                st.markdown("### Financial Profile")
                expected_limit = st.number_input("Expected Daily Incoming Transfer (₦) *", min_value=1000.0, step=10000.0, value=50000.0)
                pin = st.text_input("Create 4-digit PIN *", type="password", max_chars=4)
                
                submitted = st.form_submit_button("Preview Details")
                if submitted:
                    if not surname or not first_name or not pin or len(pin) != 4 or not pin.isdigit():
                        st.error("Please fill all required fields correctly and ensure your PIN is exactly 4 digits.")
                    else:
                        st.session_state.temp_user = {
                            "surname": surname,
                            "middle_name": middle_name,
                            "last_name": first_name,
                            "nationality": nationality,
                            "state_of_origin": state_of_origin,
                            "marital_status": marital_status,
                            "occupation": occupation,
                            "expected_limit": expected_limit,
                            "pin": pin
                        }
                        st.session_state.form_stage = "confirm"
                        st.rerun()
                        
        elif st.session_state.form_stage == "confirm":
            st.markdown("### 🔍 Confirm Your Details")
            st.info("Please review your information carefully before final submission.")
            
            u = st.session_state.temp_user
            with st.container(border=True):
                st.write(f"**Full Name:** {u['surname']} {u['middle_name']} {u['last_name']}")
                st.write(f"**Nationality:** {u['nationality']} | **State:** {u['state_of_origin']}")
                st.write(f"**Marital Status:** {u['marital_status']} | **Occupation:** {u['occupation']}")
                st.write(f"**Expected Daily Limit:** ₦{u['expected_limit']:,.2f}")
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("Confirm & Submit Account", use_container_width=True):
                    st.session_state.db = load_db()
                    acc_num = generate_account_number()
                    
                    st.session_state.db[acc_num] = {
                        "surname": u['surname'],
                        "middle_name": u['middle_name'],
                        "last_name": u['last_name'],
                        "nationality": u['nationality'],
                        "state_of_origin": u['state_of_origin'],
                        "marital_status": u['marital_status'],
                        "occupation": u['occupation'],
                        "expected_limit": u['expected_limit'],
                        "pin": u['pin'],
                        "balance": 0.0,
                        "status": "active",
                        "history": [f"[{get_time()}]: Account successfully opened and verified."],
                        "tickets": []
                    }
                    save_db(st.session_state.db)
                    st.session_state.created_acc = acc_num
                    st.session_state.form_stage = "success"
                    st.rerun()
            with col2:
                if st.button("Go Back & Edit", use_container_width=True):
                    st.session_state.form_stage = "input"
                    st.rerun()
                    
        elif st.session_state.form_stage == "success":
            st.success("🎉 Account Created Successfully!")
            st.balloons()
            with st.container(border=True):
                st.markdown(f"### Your 10-Digit Account Number: `{st.session_state.created_acc}`")
                st.warning("⚠️ Please copy your account number and keep your 4-digit PIN safe. Founder startup funding will be required before transacting.")
            if st.button("Proceed to Login"):
                st.session_state.form_stage = "input"
                st.rerun()

    # --- ADMIN PORTAL LOGIN TAB ---
    elif choice == "Admin Portal Login":
        st.subheader("Founder / Admin Access")
        with st.container(border=True):
            entered_secret = st.text_input("Enter Admin Master Password:", type="password")
            if st.button("Unlock Admin Panel"):
                if entered_secret == ADMIN_SECRET:
                    st.session_state.is_admin = True
                    st.rerun()
                else:
                    st.error("Invalid Admin Passcode.")

    # --- HELP / SUPPORT DESK ---
    elif choice == "Help / Support Desk":
        st.subheader("Customer Support & Inquiry Center")
        st.write("Submit an issue, dispute, or password reset request to the bank administration.")
        
        with st.container(border=True):
            lookup_acc = st.text_input("Your 10-Digit Account Number:")
            user_msg = st.text_area("Describe your issue or request (e.g., Forgot PIN, transaction issue):")
            
            if st.button("Submit Support Ticket"):
                if not lookup_acc or not user_msg:
                    st.error("Please enter your account number and message.")
                else:
                    st.session_state.db = load_db()
                    if lookup_acc in st.session_state.db:
                        if "tickets" not in st.session_state.db[lookup_acc]:
                            st.session_state.db[lookup_acc]["tickets"] = []
                        st.session_state.db[lookup_acc]["tickets"].append({
                            "message": user_msg,
                            "status": "Pending",
                            "admin_response": "Pending review by founder."
                        })
                        save_db(st.session_state.db)
                        st.success("Ticket submitted successfully! Check back later for founder resolution.")
                    else:
                        st.error("Account number not found in database.")

# ==========================================
# 3. LOGGED IN USER DASHBOARD
# ==========================================
else:
    st.session_state.db = load_db()
    acc_num = st.session_state.logged_in_acc
    
    if acc_num not in st.session_state.db:
        st.session_state.logged_in_acc = None
        st.rerun()
        
    user_data = st.session_state.db[acc_num]
    
    # Check if frozen
    if user_data.get('status', 'active') == 'frozen':
        st.error("🔴 **Account Frozen:** Your account has been temporarily restricted or frozen by administration (likely due to a security flag or limit review). Please visit the Support tab or contact the administrator.")
        if st.button("Log Out"):
            st.session_state.logged_in_acc = None
            st.rerun()
        st.stop()
        
    # Fintech App Navigation Bar
    nav = st.radio("Menu", ["🏠 Home", "💸 Transactions", "💬 Support & Feedback", "⚙️ Profile"], horizontal=True)
    st.divider()
    
    # --- HOME TAB ---
    if nav == "🏠 Home":
        st.subheader(f"Welcome, {user_data['surname']} 👋")
        st.markdown(f"**Account Number:** `{acc_num}`")
        st.metric(label="Available Balance", value=f"₦{user_data['balance']:,.2f}")
        
        st.markdown("### 📥 Deposit Funds Instructions")
        with st.container(border=True):
            st.write("To fund your Apex Virtual Bank account, share your 10-digit account number below with another user or fund via your founder admin panel:")
            st.info(f"**Bank Name:** Apex Virtual Bank\n**Account Number:** `{acc_num}`\n**Account Name:** {user_data['surname']} {user_data['last_name']}")
            
        st.markdown("### ⚡ Quick Transfer")
        with st.container(border=True):
            rec_acc = st.text_input("Receiver's 10-Digit Account Number:")
            trans_amount = st.number_input("Amount to send (₦):", min_value=0.0, step=500.0)
            trans_pin = st.text_input("Confirm PIN:", type="password", max_chars=4)
            
            if st.button("Send Transfer"):
                st.session_state.db = load_db()
                sender = st.session_state.db[acc_num]
                
                if trans_pin != sender['pin']:
                    st.error("Incorrect PIN.")
                elif rec_acc not in st.session_state.db:
                    st.error("Receiver account number not found.")
                elif rec_acc == acc_num:
                    st.error("You cannot transfer to yourself.")
                elif trans_amount > sender['balance']:
                    st.error("Insufficient funds.")
                elif trans_amount > 0
                    # Deduct sender
                    sender['balance'] -= trans_amount
                    sender['history'].append(f"[{get_time()}] Transfer to {rec_acc}: -₦{trans_amount:,.2f}")
                    
                    # Add receiver
                    receiver = st.session_state.db[rec_acc]
                    receiver['balance'] += trans_amount
                    receiver['history'].append(f"[{get_time()}] Received from {acc_num}: +₦{trans_amount:,.2f}")
                    
                    # FRAUD / SINGLE-TRANSFER LIMIT CHECK
                    # Freezes if this ONE individual transfer exceeds their max single incoming limit
                    single_limit = receiver.get('expected_limit', 50000.0)
                    if trans_amount > single_limit:
                        receiver['status'] = 'frozen'
                        receiver['history'].append(f"[{get_time()}] ACCOUNT AUTO-FROZEN: Single incoming transfer (₦{trans_amount:,.2f}) exceeded max single limit (₦{single_limit:,.2f}).")
                        st.warning(f"⚠️ Transfer completed, but recipient account was flagged and frozen because the single transfer of ₦{trans_amount:,.2f} exceeded their max limit of ₦{single_limit:,.2f}.")
                    
                    save_db(st.session_state.db)
                    st.success(f"Successfully transferred ₦{trans_amount:,.2f}!")
                    st.rerun()

                    
    # --- SUPPORT & FEEDBACK TAB ---
    elif nav == "💬 Support & Feedback":
        st.subheader("Help Desk & Founder Responses")
        
        with st.form("user_ticket_form"):
            new_issue = st.text_area("Send a message, request a PIN reset, or report an issue:")
            ticket_submitted = st.form_submit_button("Send to Admin")
            if ticket_submitted and new_issue:
                if "tickets" not in user_data:
                    user_data["tickets"] = []
                user_data["tickets"].append({
                    "message": new_issue,
                    "status": "Pending",
                    "admin_response": "Pending review by founder."
                })
                save_db(st.session_state.db)
                st.success("Ticket sent to admin!")
                st.rerun()
                
        st.markdown("#### Your Ticket History & Resolutions")
        if "tickets" in user_data and user_data["tickets"]:
            for t in reversed(user_data["tickets"]):
                with st.container(border=True):
                    st.write(f"**Your Request:** {t['message']}")
                    st.write(f"**Status:** {t['status']}")
                    st.info(f"**Founder Response / Solution:** {t['admin_response']}")
        else:
            st.info("No active support inquiries.")

    # --- PROFILE TAB ---
    elif nav == "⚙️ Profile":
        st.subheader("User Account Profile")
        with st.container(border=True):
            st.write(f"**Name:** {user_data['surname']} {user_data['middle_name']} {user_data['last_name']}")
            st.write(f"**Account Number:** `{acc_num}`")
            st.write(f"**State of Origin:** {user_data['state_of_origin']}")
            st.write(f"**Occupation:** {user_data['occupation']}")
            st.write(f"**Daily Limit:** ₦{user_data.get('expected_limit', 0):,.2f}")
            
        st.divider()
        if st.button("Log Out", type="primary", use_container_width=True):
            st.session_state.logged_in_acc = None
            st.rerun()
