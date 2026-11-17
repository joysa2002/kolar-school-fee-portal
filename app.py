import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials

# --- PAGE CONFIG ---
st.set_page_config(page_title="School Fee Management", layout="wide")

CLASS_TABS = ["LKG", "UKG", "1st", "2nd", "3rd", "4th", "5th", "6th", "7th"]

# --- AUTHENTICATION ---
def check_login():
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False

    if not st.session_state.authenticated:
        st.title("🏫 School Fee Portal - Login")
        with st.form("login_form"):
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            submit = st.form_submit_button("Login")
            
            if submit:
                if (username == st.secrets["admin"]["username"] and 
                    password == st.secrets["admin"]["password"]):
                    st.session_state.authenticated = True
                    st.rerun()
                else:
                    st.error("Invalid username or password")
        st.stop()

check_login()

# --- GOOGLE SHEETS CONNECTION ---
@st.cache_resource
def get_spreadsheet():
    scopes = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive"
    ]
    creds = Credentials.from_service_account_info(
        st.secrets["gcp_service_account"], scopes=scopes
    )
    client = gspread.authorize(creds)
    return client.open("School_Fee_Database")

spreadsheet = get_spreadsheet()

def load_class_data(class_name):
    worksheet = spreadsheet.worksheet(class_name)
    data = worksheet.get_all_records()
    return pd.DataFrame(data), worksheet

def load_all_classes_data():
    all_dfs = []
    for cls in CLASS_TABS:
        try:
            ws = spreadsheet.worksheet(cls)
            records = ws.get_all_records()
            if records:
                temp_df = pd.DataFrame(records)
                temp_df.insert(0, "Class", cls)
                all_dfs.append(temp_df)
        except Exception:
            pass
    if all_dfs:
        return pd.concat(all_dfs, ignore_index=True)
    return pd.DataFrame()

# --- SIDEBAR NAVIGATION ---
st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to:", ["Update Student Fee", "Class Balance & Print View", "Add New Student"])
if st.sidebar.button("Logout"):
    st.session_state.authenticated = False
    st.rerun()

# --- PAGE 1: UPDATE FEE ---
if page == "Update Student Fee":
    st.title("💳 Update Student Fee")
    
    selected_class = st.selectbox("Select Class", CLASS_TABS)
    df, worksheet = load_class_data(selected_class)
    
    if df.empty:
        st.warning(f"No student records found in {selected_class}. Go to 'Add New Student' or paste data into the '{selected_class}' sheet tab.")
    else:
        student_names = df["Student_Name"].astype(str).tolist()
        selected_student = st.selectbox("Select Student", student_names)
        
        # Fetch selected student's current row
        student_row = df[df["Student_Name"].astype(str) == selected_student].iloc[0]
        row_index = int(student_row.name) + 2  # +2 accounts for 0-index and Row 1 header
        
        st.divider()
        col1, col2, col3 = st.columns(3)
        col1.metric("Total Fee", f"₹{student_row['Total_Fee']}")
        col2.metric("Amount Paid", f"₹{student_row['Amount_Paid']}")
        col3.metric("Remaining Balance", f"₹{student_row['Balance']}")
        
        st.subheader(f"Edit Payment Details ({selected_student} - {selected_class})")
        with st.form("edit_fee_form"):
            new_total = st.number_input("Total Fee (₹)", value=int(student_row["Total_Fee"]), step=100)
            new_paid = st.number_input("Total Amount Paid So Far (₹)", value=int(student_row["Amount_Paid"]), step=100)
            add_payment = st.number_input("OR Add New Cash Received Today (₹)", value=0, step=100)
            
            if st.form_submit_button("Save & Update Record"):
                final_paid = new_paid + add_payment
                final_balance = new_total - final_paid
                
                # Columns C, D, E correspond to 3, 4, 5
                worksheet.update_cell(row_index, 3, new_total)
                worksheet.update_cell(row_index, 4, final_paid)
                worksheet.update_cell(row_index, 5, final_balance)
                
                st.success(f"Updated {selected_student}! New Balance: ₹{final_balance}")
                st.rerun()

# --- PAGE 2: CLASS BALANCE & PRINT VIEW ---
elif page == "Class Balance & Print View":
    st.title("📋 Class-Wise Fee Balance & Print Sheet")
    
    filter_options = ["All Classes"] + CLASS_TABS
    selected_filter = st.selectbox("Select Class to View / Print", filter_options)
    
    if selected_filter == "All Classes":
        display_df = load_all_classes_data()
    else:
        display_df, _ = load_class_data(selected_filter)
        if not display_df.empty:
            display_df.insert(0, "Class", selected_filter)
            
    if display_df.empty:
        st.info("No student records found for this selection.")
    else:
        # Summary Metrics
        c1, c2, c3 = st.columns(3)
        c1.metric("Total Expected", f"₹{display_df['Total_Fee'].sum()}")
        c2.metric("Total Collected", f"₹{display_df['Amount_Paid'].sum()}")
        c3.metric("Total Pending Balance", f"₹{display_df['Balance'].sum()}")
        
        # Add blank column for teachers to write down new fee collections on paper
        print_df = display_df.copy()
        print_df["New_Fee_Collected_(Teacher_Entry)"] = ""
        
        st.dataframe(print_df, use_container_width=True, hide_index=True)
        
        st.info("💡 **Printing Tip:** Open the Google Sheet directly to print individual class tabs with gridlines, or download the CSV below.")
        
        csv = print_df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label=f"📥 Download {selected_filter} Sheet (CSV)",
            data=csv,
            file_name=f"{selected_filter}_Fee_Sheet.csv",
            mime="text/csv",
        )

# --- PAGE 3: ADD NEW STUDENT ---
elif page == "Add New Student":
    st.title("➕ Enroll New Student")
    with st.form("add_student_form"):
        s_class = st.selectbox("Class", CLASS_TABS)
        s_id = st.text_input("Student ID / Roll No")
        s_name = st.text_input("Student Full Name")
        s_total = st.number_input("Total Annual Fee (₹)", min_value=0, value=5000, step=100)
        s_paid = st.number_input("Initial Fee Paid (₹)", min_value=0, value=0, step=100)
        
        if st.form_submit_button("Add Student"):
            if s_id and s_name:
                balance = s_total - s_paid
                ws = spreadsheet.worksheet(s_class)
                ws.append_row([s_id, s_name, s_total, s_paid, balance])
                st.success(f"{s_name} added to {s_class}!")
                st.rerun()
            else:
                st.error("Please enter both Student ID and Name.")
