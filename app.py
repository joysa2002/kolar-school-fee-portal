import streamlit as st
import pandas as pd
import gspread
from datetime import date
from google.oauth2.service_account import Credentials

# --- PAGE CONFIG ---
st.set_page_config(
    page_title="School Fee & Student Portal",
    page_icon="🏫",
    layout="wide"
)

CLASS_TABS = ["LKG", "UKG", "1st", "2nd", "3rd", "4th", "5th", "6th", "7th"]
EXPECTED_COLS = [
    "Student_ID", "Student_Name", "Primary_Mobile", "Alternate_Mobile",
    "Prev_Balance", "Current_Fee", "Amount_Paid", "Balance", "Status"
]
STATUS_OPTIONS = ["Active", "Hold - Fee Due", "Hold - Academic"]

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

    [data-testid="stWidgetLabel"],
    [data-testid="stWidgetLabel"] p,
    [data-testid="stWidgetLabel"] label,
    .stMarkdown p {
        color: var(--ink-black) !important;
        font-weight: 600 !important;
    }

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

    [data-testid="stForm"] {
        background-color: var(--pure-white);
        border: 1.5px solid var(--mint-green);
        border-radius: 14px;
        padding: 24px;
        box-shadow: 0 6px 18px rgba(17, 24, 20, 0.04);
    }

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
                <h2>🏫 School Fee & Student Portal</h2>
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

# --- GOOGLE SHEETS CONNECTION & HELPERS ---
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
    cleaned = (
        series.astype(str)
        .str.replace("₹", "", regex=False)
        .str.replace(",", "", regex=False)
        .str.strip()
    )
    return pd.to_numeric(cleaned, errors="coerce").fillna(0).astype(int)

def load_class_data(class_name, include_unassigned=False):
    """Reads columns A:I safely and tracks exact Google Sheet row index."""
    worksheet = spreadsheet.worksheet(class_name)
    all_values = worksheet.get_all_values()
    cols_with_row = EXPECTED_COLS + ["Sheet_Row"]
    
    if len(all_values) <= 1:
        return pd.DataFrame(columns=cols_with_row), worksheet
    
    rows = []
    for sheet_row_idx, r in enumerate(all_values[1:], start=2):
        padded = (r + [""] * 9)[:9]
        s_id = padded[0].strip()
        s_name = padded[1].strip()
        
        if include_unassigned:
            if s_id != "" or s_name != "":
                rows.append(padded + [sheet_row_idx])
        else:
            if s_name != "":
                rows.append(padded + [sheet_row_idx])
                
    if not rows:
        return pd.DataFrame(columns=cols_with_row), worksheet
        
    df = pd.DataFrame(rows, columns=cols_with_row)
    df["Student_ID"] = df["Student_ID"].astype(str).str.strip()
    df["Student_Name"] = df["Student_Name"].astype(str).str.strip()
    df["Primary_Mobile"] = df["Primary_Mobile"].astype(str).str.strip()
    df["Alternate_Mobile"] = df["Alternate_Mobile"].astype(str).str.strip()
    df["Prev_Balance"] = clean_int_series(df["Prev_Balance"])
    df["Current_Fee"] = clean_int_series(df["Current_Fee"])
    df["Amount_Paid"] = clean_int_series(df["Amount_Paid"])
    df["Balance"] = df["Prev_Balance"] + df["Current_Fee"] - df["Amount_Paid"]
    df["Status"] = df["Status"].replace("", "Active").fillna("Active")
    return df, worksheet

def load_payment_history():
    hist_cols = ["Date", "Class", "Student_ID", "Student_Name", "Amount_Paid", "Note"]
    try:
        hist_ws = spreadsheet.worksheet("Payment_History")
        all_values = hist_ws.get_all_values()
        if len(all_values) <= 1:
            return pd.DataFrame(columns=hist_cols), hist_ws
        rows = [(r + [""] * 6)[:6] for r in all_values[1:] if any(c.strip() for c in r)]
        df = pd.DataFrame(rows, columns=hist_cols)
        df["Amount_Paid"] = clean_int_series(df["Amount_Paid"])
        return df, hist_ws
    except Exception:
        return pd.DataFrame(columns=hist_cols), None

def load_all_classes_data():
    all_dfs = []
    for cls in CLASS_TABS:
        try:
            temp_df, _ = load_class_data(cls, include_unassigned=False)
            if not temp_df.empty:
                temp_df.insert(0, "Class", cls)
                all_dfs.append(temp_df)
        except Exception:
            pass
    if all_dfs:
        return pd.concat(all_dfs, ignore_index=True)
    return pd.DataFrame(columns=["Class"] + EXPECTED_COLS + ["Sheet_Row"])

# --- SIDEBAR NAVIGATION ---
st.sidebar.markdown("## 🌿 Fee Portal Menu")
page = st.sidebar.radio(
    "Navigation",
    [
        "💳 Update Student Fee",
        "⚡ Bulk Fee Entry (25+)",
        "📞 Pending Balance & Contacts",
        "🎓 Class Promotion & Year-End",
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
        <p>View past payments, edit phone numbers/status, or record a new fee payment.</p>
    </div>
    """, unsafe_allow_html=True)
    
    c_sel1, c_sel2 = st.columns(2)
    with c_sel1:
        selected_class = st.selectbox("Select Class", CLASS_TABS)
    
    df, worksheet = load_class_data(selected_class)
    
    if df.empty:
        st.warning(f"No enrolled students found in **{selected_class}**.")
    else:
        with c_sel2:
            df["Selector_Label"] = df["Student_ID"] + " - " + df["Student_Name"]
            selected_label = st.selectbox("Select Student", df["Selector_Label"].tolist())
        
        student_row = df[df["Selector_Label"] == selected_label].iloc[0]
        row_index = int(student_row["Sheet_Row"])
        student_id = str(student_row["Student_ID"])
        selected_student = str(student_row["Student_Name"])
        
        m1, m2, m3, m4, m5 = st.columns(5)
        m1.metric("Prev Year Arrears", f"₹{int(student_row['Prev_Balance']):,}")
        m2.metric("Current Year Fee", f"₹{int(student_row['Current_Fee']):,}")
        m3.metric("Total Paid", f"₹{int(student_row['Amount_Paid']):,}")
        m4.metric("Net Balance", f"₹{int(student_row['Balance']):,}")
        m5.metric("Status", str(student_row["Status"]))
        
        mob1_disp = student_row["Primary_Mobile"] if student_row["Primary_Mobile"] else "Not Recorded"
        mob2_disp = student_row["Alternate_Mobile"] if student_row["Alternate_Mobile"] else "None"
        st.caption(f"📞 **Primary Mobile:** {mob1_disp}  |  **Alternate Mobile:** {mob2_disp}")
        st.write("")
        
        left_col, right_col = st.columns([1.15, 1])
        
        with left_col:
            st.subheader("📝 Record Payment / Edit Details")
            with st.form("edit_fee_form"):
                pay_date = st.date_input("Payment Date", value=date.today())
                add_payment = st.number_input("New Fee Received Today (₹)", min_value=0, value=0, step=100)
                pay_note = st.text_input("Receipt / Note (Optional)", placeholder="e.g., Term 1 Cash / Receipt #42")
                
                with st.expander("Edit Phone Numbers, Fee Structure, or Promotion Status"):
                    p_col1, p_col2 = st.columns(2)
                    with p_col1:
                        edit_mob1 = st.text_input("Primary Mobile Number", value=str(student_row["Primary_Mobile"]))
                    with p_col2:
                        edit_mob2 = st.text_input("Alternate Mobile Number", value=str(student_row["Alternate_Mobile"]))
                        
                    current_status = str(student_row["Status"])
                    status_idx = STATUS_OPTIONS.index(current_status) if current_status in STATUS_OPTIONS else 0
                    edit_status = st.selectbox("Student Status", STATUS_OPTIONS, index=status_idx)
                    new_prev = st.number_input("Previous Year Balance (₹)", value=int(student_row["Prev_Balance"]), step=100)
                    new_curr = st.number_input("Current Year Fee (₹)", value=int(student_row["Current_Fee"]), step=100)
                    new_paid = st.number_input("Previous Amount Paid (₹)", value=int(student_row["Amount_Paid"]), step=100)
                
                if st.form_submit_button("Save & Update Student Record", use_container_width=True):
                    final_paid = new_paid + add_payment
                    final_balance = new_prev + new_curr - final_paid
                    formula_str = f"=E{row_index}+F{row_index}-G{row_index}"
                    
                    # Update Columns C:I
                    worksheet.update(
                        f"C{row_index}:I{row_index}",
                        [[
                            edit_mob1.strip(), edit_mob2.strip(),
                            new_prev, new_curr, final_paid, formula_str, edit_status
                        ]],
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
                    
                    st.success(f"Updated **{selected_student}**! Net Balance: ₹{final_balance:,}")
                    st.rerun()
        
        with right_col:
            st.subheader("📜 Payment History")
            hist_df, _ = load_payment_history()
            
            if not hist_df.empty:
                student_hist = hist_df[
                    (hist_df["Student_ID"].str.strip() == student_id) &
                    (hist_df["Student_Name"].str.strip().str.lower() == selected_student.lower())
                ].copy()
            else:
                student_hist = pd.DataFrame()
            
            if student_hist.empty:
                st.info(f"No dated payment logs recorded yet for **{selected_student}**.")
            else:
                st.markdown(f'<div class="history-header">Total Transactions: {len(student_hist)}</div>', unsafe_allow_html=True)
                display_hist = student_hist[["Date", "Class", "Amount_Paid", "Note"]].sort_values(by="Date", ascending=False)
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
            st.warning(f"No enrolled students found in {batch_class}.")
        else:
            st.caption("👇 Enter amounts in **Amount Paid Today** (leave `0` for unpaid), then click **Save All Payments**.")
            
            editor_df = df_class[[
                "Student_ID", "Student_Name", "Prev_Balance", "Current_Fee", "Amount_Paid", "Balance", "Sheet_Row"
            ]].copy()
            editor_df["Amount_Paid_Today"] = 0
            
            edited_df = st.data_editor(
                editor_df,
                disabled=["Student_ID", "Student_Name", "Prev_Balance", "Current_Fee", "Amount_Paid", "Balance", "Sheet_Row"],
                column_config={
                    "Sheet_Row": None,
                    "Amount_Paid_Today": st.column_config.NumberColumn(
                        "Amount Paid Today (₹)", min_value=0, step=100, required=True
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
                    batch_cell_updates = []
                    history_rows = []
                    
                    for _, row in paying_students.iterrows():
                        sheet_row = int(row["Sheet_Row"])
                        paid_today = int(row["Amount_Paid_Today"])
                        new_total_paid = int(row["Amount_Paid"]) + paid_today
                        
                        batch_cell_updates.append({
                            "range": f"G{sheet_row}:H{sheet_row}",
                            "values": [[new_total_paid, f"=E{sheet_row}+F{sheet_row}-G{sheet_row}"]]
                        })
                        history_rows.append([
                            str(batch_date),
                            batch_class,
                            str(row["Student_ID"]),
                            str(row["Student_Name"]),
                            paid_today,
                            batch_note
                        ])
                    
                    worksheet.batch_update(batch_cell_updates, value_input_option="USER_ENTERED")
                    
                    _, hist_ws = load_payment_history()
                    if hist_ws and history_rows:
                        hist_ws.append_rows(history_rows, table_range="A1", value_input_option="USER_ENTERED")
                    
                    st.success(f"Saved payments for **{len(paying_students)} students** in **{batch_class}**!")
                    st.rerun()
    else:
        all_df = load_all_classes_data()
        if all_df.empty:
            st.warning("No student records found across any class.")
        else:
            c_num, c_date = st.columns(2)
            with c_num:
                num_rows = st.number_input("How many student entries?", min_value=1, max_value=100, value=10, step=1)
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
                        batch_updates = []
                        for s_id, s_name, amt in items:
                            mask = (cls_df["Student_ID"] == s_id) & (cls_df["Student_Name"] == s_name)
                            if mask.any():
                                r_idx = cls_df[mask].index[0]
                                cls_df.at[r_idx, "Amount_Paid"] = int(cls_df.at[r_idx, "Amount_Paid"]) + amt
                        
                        for _, r in cls_df.iterrows():
                            sheet_row = int(r["Sheet_Row"])
                            batch_updates.append({
                                "range": f"G{sheet_row}:H{sheet_row}",
                                "values": [[int(r["Amount_Paid"]), f"=E{sheet_row}+F{sheet_row}-G{sheet_row}"]]
                            })
                        ws.batch_update(batch_updates, value_input_option="USER_ENTERED")
                    
                    _, hist_ws = load_payment_history()
                    if hist_ws and history_rows:
                        hist_ws.append_rows(history_rows, table_range="A1", value_input_option="USER_ENTERED")
                    
                    st.success(f"Recorded **{len(valid_entries)} payments** across **{len(updates_by_class)} classes**!")
                    st.rerun()

# ==========================================
# PAGE 3: PENDING BALANCE & PARENT CONTACT LIST
# ==========================================
elif page == "📞 Pending Balance & Contacts":
    st.markdown("""
    <div class="school-banner">
        <h2>📞 Pending Balance & Parent Contact List</h2>
        <p>Filter students with unpaid fees across all classes and print a clean phone call sheet.</p>
    </div>
    """, unsafe_allow_html=True)
    
    all_df = load_all_classes_data()
    if all_df.empty:
        st.info("No student records found.")
    else:
        defaulters_df = all_df[all_df["Balance"] > 0].copy()
        
        f1, f2 = st.columns(2)
        with f1:
            class_choice = st.selectbox("Filter by Class", ["All Classes"] + CLASS_TABS)
        with f2:
            min_due = st.number_input("Minimum Pending Balance (₹)", min_value=0, value=1, step=500)
            
        if class_choice != "All Classes":
            defaulters_df = defaulters_df[defaulters_df["Class"] == class_choice]
        defaulters_df = defaulters_df[defaulters_df["Balance"] >= min_due]
        
        if defaulters_df.empty:
            st.success("🎉 Zero students with pending balance matching your filter!")
        else:
            m1, m2, m3 = st.columns(3)
            m1.metric("Students with Due Balance", len(defaulters_df))
            m2.metric("Total Previous Arrears", f"₹{int(defaulters_df['Prev_Balance'].sum()):,}")
            m3.metric("Total Pending Amount", f"₹{int(defaulters_df['Balance'].sum()):,}")
            
            display_cols = [
                "Class", "Student_ID", "Student_Name", "Primary_Mobile", "Alternate_Mobile",
                "Prev_Balance", "Current_Fee", "Amount_Paid", "Balance", "Status"
            ]
            
            st.dataframe(defaulters_df[display_cols], use_container_width=True, hide_index=True)
            
            export_df = defaulters_df[display_cols].copy()
            export_df["Call_Remarks_&_Promise_Date"] = ""
            
            csv = export_df.to_csv(index=False).encode("utf-8")
            st.download_button(
                label=f"🖨️ Download Printable Call List ({class_choice})",
                data=csv,
                file_name=f"Pending_Fee_Contacts_{class_choice}_{date.today()}.csv",
                mime="text/csv",
                use_container_width=True
            )

# ==========================================
# PAGE 4: CLASS PROMOTION & YEAR-END ROLLOVER
# ==========================================
elif page == "🎓 Class Promotion & Year-End":
    st.markdown("""
    <div class="school-banner">
        <h2>🎓 Class Promotion & Academic Year Rollover</h2>
        <p>Promote passed students to the next class (carrying forward any unpaid balance) or retain students in their current class.</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.info("💡 **Year-End Best Practice:** Promote from **7th Standard down to LKG** (highest class first) so promoted students never mix with the next class before they move up.")
    
    p1, p2, p3 = st.columns([1, 1, 1.2])
    with p1:
        source_class = st.selectbox("1. Select Current Class", CLASS_TABS)
    
    source_idx = CLASS_TABS.index(source_class)
    is_final_class = (source_class == "7th")
    target_class = "Passed_Out_Batch" if is_final_class else CLASS_TABS[source_idx + 1]
    
    with p2:
        st.text_input("2. Destination", value=f"🎓 {target_class}", disabled=True)
    with p3:
        if is_final_class:
            passing_year = st.text_input("3. Passing Batch Year", value=f"{date.today().year}-{str(date.today().year + 1)[-2:]}")
            next_year_fee = 0
        else:
            next_year_fee = st.number_input(f"3. New Annual Fee for {target_class} (₹)", min_value=0, value=5000, step=100)
            passing_year = ""
            
    src_df, src_ws = load_class_data(source_class)
    
    if src_df.empty:
        st.warning(f"No enrolled students found in **{source_class}**.")
    else:
        st.caption(f"Tick **Promote** for students moving to **{target_class}**. Unticked students stay in **{source_class}** with their chosen Status.")
        
        promo_df = src_df[[
            "Student_ID", "Student_Name", "Primary_Mobile", "Alternate_Mobile",
            "Prev_Balance", "Current_Fee", "Amount_Paid", "Balance", "Status", "Sheet_Row"
        ]].copy()
        promo_df["Promote"] = promo_df["Status"] == "Active"
        
        edited_promo = st.data_editor(
            promo_df,
            disabled=[
                "Student_ID", "Student_Name", "Primary_Mobile", "Alternate_Mobile",
                "Prev_Balance", "Current_Fee", "Amount_Paid", "Balance", "Sheet_Row"
            ],
            column_config={
                "Sheet_Row": None,
                "Promote": st.column_config.CheckboxColumn(f"Move to {target_class}?", default=True),
                "Status": st.column_config.SelectboxColumn("Status (If Retained)", options=STATUS_OPTIONS)
            },
            use_container_width=True,
            hide_index=True,
            height=480
        )
        
        to_promote = edited_promo[edited_promo["Promote"] == True]
        to_retain = edited_promo[edited_promo["Promote"] == False]
        
        c_p1, c_p2, c_p3 = st.columns(3)
        c_p1.metric(f"Promoting to {target_class}", len(to_promote))
        c_p2.metric(f"Staying in {source_class}", len(to_retain))
        c_p3.metric("Arrears Carrying Forward", f"₹{int(to_promote['Balance'].sum()):,}")
        
        if st.button(f"🚀 Confirm & Execute Promotion ({len(to_promote)} Students)", use_container_width=True):
            if not to_retain.empty:
                retain_updates = []
                for _, r in to_retain.iterrows():
                    s_row = int(r["Sheet_Row"])
                    retain_updates.append({
                        "range": f"I{s_row}",
                        "values": [[str(r["Status"])]]
                    })
                src_ws.batch_update(retain_updates, value_input_option="USER_ENTERED")
            
            if not to_promote.empty:
                if is_final_class:
                    grad_ws = spreadsheet.worksheet("Passed_Out_Batch")
                    grad_rows = []
                    for _, r in to_promote.iterrows():
                        grad_rows.append([
                            passing_year,
                            str(r["Student_ID"]),
                            str(r["Student_Name"]),
                            str(r["Primary_Mobile"]),
                            str(r["Alternate_Mobile"]),
                            int(r["Balance"]),
                            str(date.today())
                        ])
                    grad_ws.append_rows(grad_rows, table_range="A1", value_input_option="USER_ENTERED")
                else:
                    dst_df, dst_ws = load_class_data(target_class, include_unassigned=True)
                    next_dst_row = (int(dst_df["Sheet_Row"].max()) + 1) if not dst_df.empty else 2
                    
                    for _, r in to_promote.iterrows():
                        s_id = str(r["Student_ID"])
                        carried_balance = int(r["Balance"])
                        
                        matching_slot = dst_df[(dst_df["Student_ID"] == s_id) & (dst_df["Student_Name"] == "")]
                        if not matching_slot.empty:
                            write_row = int(matching_slot.iloc[0]["Sheet_Row"])
                        else:
                            write_row = next_dst_row
                            next_dst_row += 1
                            
                        dst_ws.update(
                            f"A{write_row}:I{write_row}",
                            [[
                                s_id,
                                str(r["Student_Name"]),
                                str(r["Primary_Mobile"]),
                                str(r["Alternate_Mobile"]),
                                carried_balance,
                                int(next_year_fee),
                                0,
                                f"=E{write_row}+F{write_row}-G{write_row}",
                                "Active"
                            ]],
                            value_input_option="USER_ENTERED"
                        )
                
                rows_to_delete = sorted(to_promote["Sheet_Row"].astype(int).tolist(), reverse=True)
                for del_row in rows_to_delete:
                    src_ws.delete_rows(del_row)
                    
            st.success(f"✅ Promoted **{len(to_promote)} students** to **{target_class}**! ({len(to_retain)} retained in {source_class})")
            st.rerun()

# ==========================================
# PAGE 5: CLASS BALANCE & PRINT VIEW
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
        st.info("No enrolled student records found for this selection.")
    else:
        if "Sheet_Row" in display_df.columns:
            display_df = display_df.drop(columns=["Sheet_Row"])
            
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Previous Arrears", f"₹{int(display_df['Prev_Balance'].sum()):,}")
        c2.metric("Current Year Fee", f"₹{int(display_df['Current_Fee'].sum()):,}")
        c3.metric("Total Collected", f"₹{int(display_df['Amount_Paid'].sum()):,}")
        c4.metric("Net Pending Balance", f"₹{int(display_df['Balance'].sum()):,}")
        
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
# PAGE 6: ADD NEW STUDENT
# ==========================================
elif page == "➕ Add New Student":
    st.markdown("""
    <div class="school-banner">
        <h2>➕ Enroll New Student</h2>
        <p>Add a new student with primary & alternate phone numbers, fee structure, and initial status.</p>
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
            s_mob1 = st.text_input("Primary Mobile Number")
            s_mob2 = st.text_input("Alternate Mobile Number (Optional)")
        with c2:
            s_prev = st.number_input("Previous Balance Carried Over (₹)", min_value=0, value=0, step=100)
            s_total = st.number_input("Current Annual Fee (₹)", min_value=0, value=5000, step=100)
            s_paid = st.number_input("Initial Fee Paid at Admission (₹)", min_value=0, value=0, step=100)
            s_status = st.selectbox("Initial Status", STATUS_OPTIONS)
            s_date = st.date_input("Admission / Payment Date", value=date.today())
        
        if st.form_submit_button("Enroll Student", use_container_width=True):
            clean_id = s_id.strip()
            clean_name = s_name.strip()
            
            if clean_id and clean_name:
                full_df, ws = load_class_data(s_class, include_unassigned=True)
                matching_id_rows = full_df[full_df["Student_ID"] == clean_id]
                
                if not matching_id_rows.empty:
                    existing_row = matching_id_rows.iloc[0]
                    if existing_row["Student_Name"] != "":
                        st.error(f"⚠️ Student ID **{clean_id}** in **{s_class}** is already assigned to **{existing_row['Student_Name']}**!")
                        st.stop()
                    else:
                        target_row = int(existing_row["Sheet_Row"])
                else:
                    target_row = (int(full_df["Sheet_Row"].max()) + 1) if not full_df.empty else 2
                
                balance = int(s_prev) + int(s_total) - int(s_paid)
                ws.update(
                    f"A{target_row}:I{target_row}",
                    [[
                        clean_id, clean_name, s_mob1.strip(), s_mob2.strip(),
                        int(s_prev), int(s_total), int(s_paid),
                        f"=E{target_row}+F{target_row}-G{target_row}",
                        s_status
                    ]],
                    value_input_option="USER_ENTERED"
                )
                
                if int(s_paid) > 0:
                    _, hist_ws = load_payment_history()
                    if hist_ws:
                        hist_ws.append_row(
                            [str(s_date), s_class, clean_id, clean_name, int(s_paid), "Initial Admission Fee"],
                            table_range="A1",
                            value_input_option="USER_ENTERED"
                        )
                
                st.session_state["enroll_msg"] = f"✅ Enrolled **{clean_name}** (ID: {clean_id}) into **{s_class}**! Net Balance: ₹{balance:,}"
                st.rerun()
            else:
                st.error("Please enter both Student ID and Student Full Name.")
