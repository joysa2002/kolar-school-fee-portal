import streamlit as st
import pandas as pd
import gspread
from datetime import date
from google.oauth2.service_account import Credentials

# --- PAGE CONFIG ---
st.set_page_config(
    page_title="School Fee Portal",
    page_icon="🏫",
    layout="wide"
)

CLASS_TABS = ["LKG", "UKG", "1st", "2nd", "3rd", "4th", "5th", "6th", "7th"]
EXPECTED_COLS = ["Student_ID", "Student_Name", "Total_Fee", "Amount_Paid", "Balance"]

# --- CUSTOM AESTHETIC THEME (Honeydew, Mint, Seafoam, Paris Green, White, Black) ---
st.markdown("""
<style>
    :root {
        --honeydew: #F0FFF0;
        --mint-green: #B8F2D0;
        --seafoam: #71EEB8;
        --paris-green: #2E8B57;
        --paris-bright: #50C878;
        --pure-white: #FFFFFF;
        --ink-black: #111814;
    }

    .stApp {
        background-color: var(--honeydew);
        color: var(--ink-black);
    }

    /* Force dark, crisp text on all form labels & captions */
    [data-testid="stWidgetLabel"],
    [data-testid="stWidgetLabel"] p,
    [data-testid="stWidgetLabel"] label,
    .stMarkdown p {
        color: var(--ink-black) !important;
        font-weight: 600 !important;
    }

    /* Sidebar Styling */
    [data-testid="stSidebar"] {
        background-color: var(--ink-black);
        border-right: 3px solid var(--paris-bright);
    }
    [data-testid="stSidebar"] * {
        color: var(--honeydew) !important;
    }
    [data-testid="stSidebar"] .stRadio label:hover {
        color: var(--seafoam) !important;
    }

    h1, h2, h3 {
        color: var(--ink-black) !important;
        font-weight: 700 !important;
        letter-spacing: -0.02em;
    }

    /* Metric Cards */
    [data-testid="stMetric"] {
        background-color: var(--pure-white);
        border: 1.5px solid var(--mint-green);
        border-left: 6px solid var(--paris-bright);
        padding: 16px 20px;
        border-radius: 12px;
        box-shadow: 0 4px 12px rgba(17, 24, 20, 0.05);
    }
    [data-testid="stMetricLabel"], [data-testid="stMetricLabel"] p {
        color: #2D4A3E !important;
        font-weight: 600 !important;
        font-size: 0.9rem !important;
    }
    [data-testid="stMetricValue"] {
        color: var(--ink-black) !important;
        font-weight: 800 !important;
    }

    /* Forms & Containers */
    [data-testid="stForm"] {
        background-color: var(--pure-white);
        border: 1.5px solid var(--mint-green);
        border-radius: 14px;
        padding: 24px;
        box-shadow: 0 6px 18px rgba(17, 24, 20, 0.04);
    }

    /* Primary & Form Submit Buttons */
    .stButton > button, [data-testid="stFormSubmitButton"] > button {
        background: linear-gradient(135deg, var(--paris-bright), var(--paris-green)) !important;
        color: var(--pure-white) !important;
        border: none !important;
        border-radius: 10px !important;
        padding: 0.55rem 1.4rem !important;
        font-weight: 600 !important;
        transition: all 0.2s ease !important;
        box-shadow: 0 3px 8px rgba(46, 139, 87, 0.25) !important;
    }
    .stButton > button p, [data-testid="stFormSubmitButton"] > button p {
        color: var(--pure-white) !important;
    }
    .stButton > button:hover, [data-testid="stFormSubmitButton"] > button:hover {
        background: var(--ink-black) !important;
        color: var(--seafoam) !important;
        transform: translateY(-1px);
    }

    /* Download Button */
    [data-testid="stDownloadButton"] > button {
        background-color: var(--pure-white) !important;
        color: var(--paris-green) !important;
        border: 2px solid var(--paris-bright) !important;
        border-radius: 10px !important;
        font-weight: 600 !important;
    }
    [data-testid="stDownloadButton"] > button p {
        color: var(--paris-green) !important;
    }

    /* Inputs, Date Pickers & Placeholders */
    .stSelectbox div[data-baseweb="select"] > div,
    .stTextInput input,
    .stNumberInput input,
    .stDateInput input,
    div[data-baseweb="input"] {
        background-color: var(--pure-white) !important;
        color: var(--ink-black) !important;
        border: 1.5px solid var(--mint-green) !important;
        border-radius: 8px !important;
    }
    input::placeholder {
        color: #5C7568 !important;
        opacity: 1 !important;
    }

    /* Header Banner */
    .school-banner {
        background: linear-gradient(120deg, var(--ink-black) 0%, #1B3B2B 60%, var(--paris-green) 100%);
        color: var(--pure-white);
        padding: 20px 26px;
        border-radius: 14px;
        margin-bottom: 20px;
        border-bottom: 4px solid var(--seafoam);
    }
    .school-banner h2 {
        color: var(--pure-white) !important;
        margin: 0;
        font-size: 1.55rem;
    }
    .school-banner p {
        color: var(--mint-green) !important;
        margin: 4px 0 0 0;
        font-size: 0.95rem;
    }

    .history-header {
        background-color: var(--mint-green);
        color: var(--ink-black);
        padding: 10px 16px;
        border-radius: 8px;
        font-weight: 700;
        margin-top: 10px;
        margin-bottom: 10px;
        border-left: 5px solid var(--paris-green);
    }
</style>
""", unsafe_allow_html=True)

# --- AUTHENTICATION ---
def check_login():
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False

    if not st.session_state.authenticated:
        col_l, col_c, col_r = st.columns([1, 1.3, 1])
        with col_c:
            st.markdown("""
            <div class="school-banner" style="text-align:center;">
                <h2>🏫 School Fee Management</h2>
                <p>Authorized Staff & Headmaster Login</p>
            </div>
            """, unsafe_allow_html=True)
            with st.form("login_form"):
                username = st.text_input("Username")
                password = st.text_input("Password", type="password")
                submit = st.form_submit_button("Sign In to Portal", use_container_width=True)
                
                if submit:
                    if (username == st.secrets["admin"]["username"] and 
                        password == st.secrets["admin"]["password"]):
                        st.session_state.authenticated = True
                        st.rerun()
                    else:
                        st.error("Invalid username or password.")
        st.stop()

check_login()

# --- GOOGLE SHEETS CONNECTION & SAFE PARSERS ---
@st.cache_resource
def get_spreadsheet():
    scopes = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive"
    ]
    creds_dict = dict(st.secrets["gcp_service_account"])
    creds_dict["private_key"] = creds_dict["private_key"].replace("\\n", "\n")
    creds = Credentials.from_service_account_info(creds_dict, scopes=scopes)
    client = gspread.authorize(creds)
    return client.open("School_Fee_Database")

spreadsheet = get_spreadsheet()

def clean_int_series(series):
    """Safely converts strings, commas, currency symbols, or blanks into clean integers."""
    cleaned = (
        series.astype(str)
        .str.replace("₹", "", regex=False)
        .str.replace(",", "", regex=False)
        .str.strip()
    )
    return pd.to_numeric(cleaned, errors="coerce").fillna(0).astype(int)

def load_class_data(class_name):
    """Reads columns A:E safely without failing on duplicate/blank headers or blank cells."""
    worksheet = spreadsheet.worksheet(class_name)
    all_values = worksheet.get_all_values()
    
    if len(all_values) <= 1:
        return pd.DataFrame(columns=EXPECTED_COLS), worksheet
    
    rows = []
    for r in all_values[1:]:
        # Pad row to at least 5 columns
        padded = (r + ["", "", "", "", ""])[:5]
        # Skip completely empty rows
        if any(cell.strip() != "" for cell in padded[:2]):
            rows.append(padded)
            
    if not rows:
        return pd.DataFrame(columns=EXPECTED_COLS), worksheet
        
    df = pd.DataFrame(rows, columns=EXPECTED_COLS)
    df["Student_ID"] = df["Student_ID"].astype(str).str.strip()
    df["Student_Name"] = df["Student_Name"].astype(str).str.strip()
    df["Total_Fee"] = clean_int_series(df["Total_Fee"])
    df["Amount_Paid"] = clean_int_series(df["Amount_Paid"])
    df["Balance"] = df["Total_Fee"] - df["Amount_Paid"]
    return df, worksheet

def load_payment_history():
    hist_cols = ["Date", "Class", "Student_ID", "Student_Name", "Amount_Paid", "Note"]
    try:
        hist_ws = spreadsheet.worksheet("Payment_History")
        all_values = hist_ws.get_all_values()
        if len(all_values) <= 1:
            return pd.DataFrame(columns=hist_cols), hist_ws
        rows = [(r + ["", "", "", "", "", ""])[:6] for r in all_values[1:] if any(c.strip() for c in r)]
        df = pd.DataFrame(rows, columns=hist_cols)
        df["Amount_Paid"] = clean_int_series(df["Amount_Paid"])
        return df, hist_ws
    except Exception:
        return pd.DataFrame(columns=hist_cols), None

def load_all_classes_data():
    all_dfs = []
    for cls in CLASS_TABS:
        try:
            temp_df, _ = load_class_data(cls)
            if not temp_df.empty:
                temp_df.insert(0, "Class", cls)
                all_dfs.append(temp_df)
        except Exception:
            pass
    if all_dfs:
        return pd.concat(all_dfs, ignore_index=True)
    return pd.DataFrame(columns=["Class"] + EXPECTED_COLS)

# --- SIDEBAR NAVIGATION ---
st.sidebar.markdown("## 🌿 Fee Portal Menu")
page = st.sidebar.radio(
    "Navigation",
    [
        "💳 Update Student Fee",
        "⚡ Bulk Fee Entry (25+)",
        "📋 Class Balance & Print",
        "➕ Add New Student"
    ],
    label_visibility="collapsed"
)
st.sidebar.divider()
if st.sidebar.button("🚪 Logout", use_container_width=True):
    st.session_state.authenticated = False
    st.rerun()

# ==========================================
# PAGE 1: UPDATE SINGLE STUDENT FEE + HISTORY
# ==========================================
if page == "💳 Update Student Fee":
    st.markdown("""
    <div class="school-banner">
        <h2>💳 Student Fee Update & Payment History</h2>
        <p>Select a class and student to view past receipts, edit balances, or record a new payment.</p>
    </div>
    """, unsafe_allow_html=True)
    
    c_sel1, c_sel2 = st.columns(2)
    with c_sel1:
        selected_class = st.selectbox("Select Class", CLASS_TABS)
    
    df, worksheet = load_class_data(selected_class)
    
    if df.empty:
        st.warning(f"No student records found in **{selected_class}**.")
    else:
        with c_sel2:
            student_names = df["Student_Name"].tolist()
            selected_student = st.selectbox("Select Student", student_names)
        
        student_row = df[df["Student_Name"] == selected_student].iloc[0]
        row_index = int(student_row.name) + 2
        student_id = str(student_row["Student_ID"])
        
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Roll / ID", student_id)
        m2.metric("Total Annual Fee", f"₹{int(student_row['Total_Fee']):,}")
        m3.metric("Total Paid", f"₹{int(student_row['Amount_Paid']):,}")
        m4.metric("Remaining Balance", f"₹{int(student_row['Balance']):,}")
        
        st.write("")
        left_col, right_col = st.columns([1.1, 1])
        
        with left_col:
            st.subheader("📝 Record / Edit Payment")
            with st.form("edit_fee_form"):
                pay_date = st.date_input("Payment Date", value=date.today())
                add_payment = st.number_input("New Fee Received Today (₹)", min_value=0, value=0, step=100)
                pay_note = st.text_input("Receipt / Note (Optional)", placeholder="e.g., Term 1 Cash / Receipt #42")
                
                with st.expander("Advanced: Edit Total Fee or Correct Past Paid Total"):
                    new_total = st.number_input("Total Annual Fee (₹)", value=int(student_row["Total_Fee"]), step=100)
                    new_paid = st.number_input("Previous Amount Paid (₹)", value=int(student_row["Amount_Paid"]), step=100)
                
                if st.form_submit_button("Save & Update Student Record", use_container_width=True):
                    final_paid = new_paid + add_payment
                    final_balance = new_total - final_paid
                    formula_str = f"=C{row_index}-D{row_index}"
                    
                    worksheet.update(
                        f"C{row_index}:E{row_index}",
                        [[new_total, final_paid, formula_str]],
                        value_input_option="USER_ENTERED"
                    )
                    
                    if add_payment > 0:
                        _, hist_ws = load_payment_history()
                        if hist_ws:
                            hist_ws.append_row([
                                str(pay_date),
                                selected_class,
                                student_id,
                                selected_student,
                                add_payment,
                                pay_note if pay_note else "Single Entry"
                            ], table_range="A1", value_input_option="USER_ENTERED")
                    
                    st.success(f"Updated **{selected_student}**! Remaining Balance: ₹{final_balance:,}")
                    st.rerun()
        
        with right_col:
            st.subheader("📜 Payment History")
            hist_df, _ = load_payment_history()
            
            if not hist_df.empty:
                student_hist = hist_df[
                    (hist_df["Class"].str.strip() == selected_class) &
                    (hist_df["Student_Name"].str.strip() == selected_student)
                ].copy()
            else:
                student_hist = pd.DataFrame()
            
            if student_hist.empty:
                st.info(f"No dated payment logs recorded yet for **{selected_student}**.")
            else:
                st.markdown(f'<div class="history-header">Total Transactions: {len(student_hist)}</div>', unsafe_allow_html=True)
                display_hist = student_hist[["Date", "Amount_Paid", "Note"]].sort_values(by="Date", ascending=False)
                st.dataframe(display_hist, use_container_width=True, hide_index=True)

# ==========================================
# PAGE 2: BULK FEE ENTRY (25+ STUDENTS AT ONCE)
# ==========================================
elif page == "⚡ Bulk Fee Entry (25+)":
    st.markdown("""
    <div class="school-banner">
        <h2>⚡ Bulk Fee Entry (Batch Mode)</h2>
        <p>Enter fees for 25+ students at once from a teacher's collection sheet with a single save.</p>
    </div>
    """, unsafe_allow_html=True)
    
    entry_mode = st.radio(
        "Choose Entry Style:",
        [
            "📋 Class Sheet Mode (Fastest — Matches Teacher's Printed Class List)",
            "🔀 Multi-Class Custom Rows (Pick Any Class & Student per Row)"
        ],
        horizontal=True
    )
    
    st.divider()
    
    # --- MODE A: CLASS SHEET MODE ---
    if entry_mode.startswith("📋"):
        b1, b2, b3 = st.columns([1, 1, 1.2])
        with b1:
            batch_class = st.selectbox("1. Select Class", CLASS_TABS)
        with b2:
            batch_date = st.date_input("2. Collection Date", value=date.today())
        with b3:
            batch_note = st.text_input("3. Batch Note (Optional)", value=f"{batch_class} Class Collection")
            
        df_class, worksheet = load_class_data(batch_class)
        
        if df_class.empty:
            st.warning(f"No students found in {batch_class}.")
        else:
            st.caption("👇 Type the amount received in the **Amount Paid Today** column (leave `0` for students who didn't pay today), then click **Save All Payments**.")
            
            editor_df = df_class[["Student_ID", "Student_Name", "Total_Fee", "Amount_Paid", "Balance"]].copy()
            editor_df["Amount_Paid_Today"] = 0
            
            edited_df = st.data_editor(
                editor_df,
                disabled=["Student_ID", "Student_Name", "Total_Fee", "Amount_Paid", "Balance"],
                column_config={
                    "Amount_Paid_Today": st.column_config.NumberColumn(
                        "Amount Paid Today (₹)",
                        min_value=0,
                        step=100,
                        required=True
                    )
                },
                use_container_width=True,
                hide_index=True,
                height=500
            )
            
            edited_df["Amount_Paid_Today"] = clean_int_series(edited_df["Amount_Paid_Today"])
            paying_students = edited_df[edited_df["Amount_Paid_Today"] > 0]
            
            c_sum1, c_sum2 = st.columns(2)
            c_sum1.metric("Students Paying in This Batch", len(paying_students))
            c_sum2.metric("Total Batch Cash Collected", f"₹{int(paying_students['Amount_Paid_Today'].sum()):,}")
            
            if st.button("✅ Save All Payments to Sheet & History", use_container_width=True):
                if paying_students.empty:
                    st.warning("Enter an amount greater than 0 for at least one student before saving.")
                else:
                    updated_rows = []
                    history_rows = []
                    
                    for idx, row in edited_df.iterrows():
                        sheet_row = int(idx) + 2
                        paid_today = int(row["Amount_Paid_Today"])
                        new_total_paid = int(row["Amount_Paid"]) + paid_today
                        updated_rows.append([
                            int(row["Total_Fee"]),
                            new_total_paid,
                            f"=C{sheet_row}-D{sheet_row}"
                        ])
                        
                        if paid_today > 0:
                            history_rows.append([
                                str(batch_date),
                                batch_class,
                                str(row["Student_ID"]),
                                str(row["Student_Name"]),
                                paid_today,
                                batch_note
                            ])
                    
                    end_row = len(updated_rows) + 1
                    worksheet.update(
                        f"C2:E{end_row}",
                        updated_rows,
                        value_input_option="USER_ENTERED"
                    )
                    
                    _, hist_ws = load_payment_history()
                    if hist_ws and history_rows:
                        hist_ws.append_rows(history_rows, table_range="A1", value_input_option="USER_ENTERED")
                    
                    st.success(f"Saved payments for **{len(paying_students)} students** in **{batch_class}** (Total: ₹{int(paying_students['Amount_Paid_Today'].sum()):,})!")
                    st.rerun()

    # --- MODE B: MULTI-CLASS CUSTOM ROWS ---
    else:
        all_df = load_all_classes_data()
        if all_df.empty:
            st.warning("No student records found across any class.")
        else:
            c_num, c_date = st.columns(2)
            with c_num:
                num_rows = st.number_input("How many student entries do you want to add?", min_value=1, max_value=100, value=10, step=1)
            with c_date:
                default_batch_date = st.date_input("Default Payment Date", value=date.today())
            
            all_df["Display_Label"] = all_df["Class"] + " | " + all_df["Student_Name"] + " (ID: " + all_df["Student_ID"] + ")"
            student_options = all_df["Display_Label"].tolist()
            
            template_df = pd.DataFrame({
                "Student": [None] * int(num_rows),
                "Amount_Paid": [0] * int(num_rows),
                "Date": [default_batch_date] * int(num_rows),
                "Note": ["Batch Entry"] * int(num_rows)
            })
            
            st.caption("👇 Select the student from the dropdown in each row, type the amount, and click Save.")
            custom_edited = st.data_editor(
                template_df,
                column_config={
                    "Student": st.column_config.SelectboxColumn("Class & Student", options=student_options, width="large"),
                    "Amount_Paid": st.column_config.NumberColumn("Amount Paid (₹)", min_value=0, step=100),
                    "Date": st.column_config.DateColumn("Payment Date"),
                    "Note": st.column_config.TextColumn("Note")
                },
                use_container_width=True,
                hide_index=True
            )
            
            custom_edited["Amount_Paid"] = clean_int_series(custom_edited["Amount_Paid"])
            valid_entries = custom_edited.dropna(subset=["Student"])
            valid_entries = valid_entries[valid_entries["Amount_Paid"] > 0]
            
            if st.button("✅ Save Multi-Class Batch", use_container_width=True):
                if valid_entries.empty:
                    st.warning("Please select at least one student and enter an amount > 0.")
                else:
                    history_rows = []
                    updates_by_class = {}
                    
                    for _, entry in valid_entries.iterrows():
                        matched = all_df[all_df["Display_Label"] == entry["Student"]].iloc[0]
                        cls = matched["Class"]
                        s_id = str(matched["Student_ID"])
                        s_name = str(matched["Student_Name"])
                        amt = int(entry["Amount_Paid"])
                        
                        updates_by_class.setdefault(cls, []).append((s_id, s_name, amt))
                        history_rows.append([str(entry["Date"]), cls, s_id, s_name, amt, str(entry["Note"])])
                    
                    for cls, items in updates_by_class.items():
                        cls_df, ws = load_class_data(cls)
                        for s_id, s_name, amt in items:
                            mask = (cls_df["Student_ID"] == s_id) & (cls_df["Student_Name"] == s_name)
                            if mask.any():
                                r_idx = cls_df[mask].index[0]
                                cls_df.at[r_idx, "Amount_Paid"] = int(cls_df.at[r_idx, "Amount_Paid"]) + amt
                        
                        updated_cols = []
                        for idx, r in cls_df.iterrows():
                            sheet_row = int(idx) + 2
                            updated_cols.append([
                                int(r["Total_Fee"]),
                                int(r["Amount_Paid"]),
                                f"=C{sheet_row}-D{sheet_row}"
                            ])
                        ws.update(
                            f"C2:E{len(updated_cols) + 1}",
                            updated_cols,
                            value_input_option="USER_ENTERED"
                        )
                    
                    _, hist_ws = load_payment_history()
                    if hist_ws and history_rows:
                        hist_ws.append_rows(history_rows, table_range="A1", value_input_option="USER_ENTERED")
                    
                    st.success(f"Successfully recorded **{len(valid_entries)} payments** across **{len(updates_by_class)} classes**!")
                    st.rerun()

# ==========================================
# PAGE 3: CLASS BALANCE & PRINT VIEW
# ==========================================
elif page == "📋 Class Balance & Print":
    st.markdown("""
    <div class="school-banner">
        <h2>📋 Class-Wise Fee Balance & Print Sheet</h2>
        <p>Filter by class or export all classes with a blank column for teachers to note cash collections.</p>
    </div>
    """, unsafe_allow_html=True)
    
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
        c1, c2, c3 = st.columns(3)
        c1.metric("Total Expected Fee", f"₹{int(display_df['Total_Fee'].sum()):,}")
        c2.metric("Total Fee Collected", f"₹{int(display_df['Amount_Paid'].sum()):,}")
        c3.metric("Total Pending Balance", f"₹{int(display_df['Balance'].sum()):,}")
        
        print_df = display_df.copy()
        print_df["New_Fee_Collected_(Teacher_Note)"] = ""
        
        st.dataframe(print_df, use_container_width=True, hide_index=True)
        
        csv = print_df.to_csv(index=False).encode("utf-8")
        st.download_button(
            label=f"📥 Download {selected_filter} Printable Sheet (CSV)",
            data=csv,
            file_name=f"{selected_filter}_Fee_Sheet_{date.today()}.csv",
            mime="text/csv",
        )

# ==========================================
# PAGE 4: ADD NEW STUDENT
# ==========================================
elif page == "➕ Add New Student":
    st.markdown("""
    <div class="school-banner">
        <h2>➕ Enroll New Student</h2>
        <p>Add a student to any class from LKG to 7th Standard.</p>
    </div>
    """, unsafe_allow_html=True)
    
    if "enroll_msg" in st.session_state:
        st.success(st.session_state.pop("enroll_msg"))
    
    with st.form("add_student_form", clear_on_submit=True):
        c1, c2 = st.columns(2)
        with c1:
            s_class = st.selectbox("Class", CLASS_TABS)
            s_id = st.text_input("Student ID / Roll No")
            s_name = st.text_input("Student Full Name")
        with c2:
            s_total = st.number_input("Total Annual Fee (₹)", min_value=0, value=5000, step=100)
            s_paid = st.number_input("Initial Fee Paid at Admission (₹)", min_value=0, value=0, step=100)
            s_date = st.date_input("Admission / Payment Date", value=date.today())
        
        if st.form_submit_button("Enroll Student", use_container_width=True):
            if s_id.strip() and s_name.strip():
                existing_df, ws = load_class_data(s_class)
                next_row = len(existing_df) + 2  # Exact next row right below existing students
                balance = int(s_total) - int(s_paid)
                
                ws.update(
                    f"A{next_row}:E{next_row}",
                    [[s_id.strip(), s_name.strip(), int(s_total), int(s_paid), f"=C{next_row}-D{next_row}"]],
                    value_input_option="USER_ENTERED"
                )
                
                if int(s_paid) > 0:
                    _, hist_ws = load_payment_history()
                    if hist_ws:
                        hist_ws.append_row(
                            [str(s_date), s_class, s_id.strip(), s_name.strip(), int(s_paid), "Initial Admission Fee"],
                            table_range="A1",
                            value_input_option="USER_ENTERED"
                        )
                
                st.session_state["enroll_msg"] = f"✅ Enrolled **{s_name.strip()}** into **{s_class}** (Row {next_row})! Remaining Balance: ₹{balance:,}"
                st.rerun()
            else:
                st.error("Please enter both Student ID and Student Full Name.")
