import streamlit as st
import requests
import re
from datetime import datetime, date, time, timedelta

API_BASE = "http://127.0.0.1:8000/api"

# Page configuration
st.set_page_config(
    page_title="CareSync | Front Desk Management",
    page_icon="🩺",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Inject Tailwind CSS, FontAwesome Icons, and High-End Custom CSS
st.markdown("""
<script src="https://cdn.tailwindcss.com"></script>
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&display=swap');
    
    * { font-family: 'Plus Jakarta Sans', sans-serif; }

    /* Hide default Streamlit header and sidebar */
    header[data-testid="stHeader"] { visibility: hidden; height: 0; }
    section[data-testid="stSidebar"] { display: none; }
    
    .main .block-container {
        padding-top: 1.25rem;
        padding-bottom: 3rem;
        max-width: 1200px;
    }

    /* Glassmorphism Navigation Bar Container */
    .navbar-container {
        background: rgba(15, 23, 42, 0.85);
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        border: 1px solid rgba(51, 65, 85, 0.7);
        border-radius: 16px;
        padding: 12px 24px;
        margin-bottom: 24px;
        box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.3);
    }
    
    /* Streamlit Radio Pill Styling Overrides for Navbar */
    div[data-testid="stRadio"] > div {
        background-color: rgba(30, 41, 59, 0.7);
        padding: 4px;
        border-radius: 12px;
        border: 1px solid rgba(51, 65, 85, 0.5);
        display: flex;
        gap: 6px;
    }
    
    div[data-testid="stRadio"] label {
        background: transparent !important;
        border-radius: 8px !important;
        padding: 8px 16px !important;
        color: #94a3b8 !important;
        font-weight: 600 !important;
        font-size: 0.88rem !important;
        transition: all 0.25s ease-in-out !important;
        border: 1px solid transparent !important;
        cursor: pointer !important;
    }

    div[data-testid="stRadio"] label:hover {
        color: #e2e8f0 !important;
        background: rgba(51, 65, 85, 0.4) !important;
    }

    /* Active Highlighted Tab styling */
    div[data-testid="stRadio"] label[aria-checked="true"] {
        background: linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%) !important;
        color: #ffffff !important;
        box-shadow: 0 4px 14px 0 rgba(59, 130, 246, 0.39) !important;
        border: 1px solid rgba(147, 197, 253, 0.3) !important;
    }

    div[data-testid="stRadio"] label[aria-checked="true"] p {
        color: #ffffff !important;
        font-weight: 700 !important;
    }

    /* Enhanced Card Styling */
    .metric-card {
        background: linear-gradient(145deg, #1e293b 0%, #0f172a 100%);
        border: 1px solid #334155;
        border-radius: 16px;
        padding: 22px;
        box-shadow: 0 8px 16px -4px rgba(0, 0, 0, 0.3);
        transition: transform 0.2s ease, border-color 0.2s ease;
    }

    .metric-card:hover {
        transform: translateY(-2px);
        border-color: #3b82f6;
    }
    
    /* Badges */
    .status-confirmed {
        background: rgba(16, 185, 129, 0.15);
        color: #34d399;
        border: 1px solid rgba(16, 185, 129, 0.4);
        padding: 4px 12px;
        border-radius: 9999px;
        font-weight: 700;
        font-size: 0.75rem;
        letter-spacing: 0.025em;
    }

    .status-cancelled {
        background: rgba(239, 68, 68, 0.15);
        color: #f87171;
        border: 1px solid rgba(239, 68, 68, 0.4);
        padding: 4px 12px;
        border-radius: 9999px;
        font-weight: 700;
        font-size: 0.75rem;
        letter-spacing: 0.025em;
    }
    
    .landing-hero {
        background: radial-gradient(circle at top right, #1e1b4b 0%, #0f172a 60%, #090d16 100%);
        border-radius: 20px;
        padding: 48px;
        margin-bottom: 28px;
        border: 1px solid rgba(99, 102, 241, 0.25);
        box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.4);
    }

    /* Input Field Highlights */
    .stTextInput input, .stSelectbox select, .stDateInput input, .stTimeInput input {
        border-radius: 10px !important;
        border: 1px solid #334155 !important;
        background-color: #0f172a !important;
    }

    .stTextInput input:focus, .stSelectbox select:focus {
        border-color: #3b82f6 !important;
        box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.2) !important;
    }
</style>
""", unsafe_allow_html=True)

# Session state initialization
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = ""
if "active_tab" not in st.session_state:
    st.session_state.active_tab = "Product Landing"

def fetch_doctors():
    try:
        r = requests.get(f"{API_BASE}/doctors")
        return r.json() if r.status_code == 200 else []
    except:
        return []

# ==========================================
# HIGH-END TOP NAVBAR HEADER
# ==========================================
if st.session_state.logged_in:
    nav_options = ["Product Landing", "Book Appointment", "Doctor Schedule", "Patient Lookup"]
else:
    nav_options = ["Product Landing", "Login / Register"]

if st.session_state.active_tab not in nav_options:
    st.session_state.active_tab = "Product Landing"

# Render Navbar Outer Frame
st.markdown('<div class="navbar-container">', unsafe_allow_html=True)

nav_col_logo, nav_col_menu, nav_col_user = st.columns([2.5, 5.5, 2])

with nav_col_logo:
    st.markdown("""
    <div class="flex items-center space-x-3">
        <div class="w-10 h-10 rounded-xl bg-gradient-to-tr from-blue-600 to-indigo-500 flex items-center justify-center text-white shadow-lg shadow-blue-500/30">
            <i class="fa-solid fa-hospital-user text-xl"></i>
        </div>
        <div>
            <h2 class="text-xl font-extrabold text-white tracking-tight leading-none">CareSync</h2>
            <p class="text-[11px] font-medium text-blue-400 mt-1">Front Desk Operations</p>
        </div>
    </div>
    """, unsafe_allow_html=True)

with nav_col_menu:
    selected_nav = st.radio(
        label="Navbar Options",
        options=nav_options,
        index=nav_options.index(st.session_state.active_tab),
        horizontal=True,
        label_visibility="collapsed"
    )
    st.session_state.active_tab = selected_nav

with nav_col_user:
    if st.session_state.logged_in:
        st.markdown(f"""
        <div class="flex items-center justify-end space-x-3 pt-1">
            <div class="text-right">
                <p class="text-xs text-slate-400 leading-none">Logged in as</p>
                <p class="text-sm font-bold text-blue-400 mt-1">{st.session_state.username}</p>
            </div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Logout", key="top_logout"):
            st.session_state.logged_in = False
            st.session_state.username = ""
            st.session_state.active_tab = "Product Landing"
            st.rerun()
    else:
        st.markdown("""
        <div class="flex items-center justify-end space-x-2 pt-2 text-slate-400 text-xs font-semibold">
            <span class="inline-block w-2 h-2 rounded-full bg-amber-400 animate-pulse"></span>
            <span>Guest Mode</span>
        </div>
        """, unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)

# ==========================================
# PAGE 1: PRODUCT LANDING PAGE
# ==========================================
if st.session_state.active_tab == "Product Landing":
    st.markdown("""
    <div class="landing-hero">
        <div class="max-w-3xl">
            <span class="bg-indigo-500/20 text-indigo-300 text-xs font-bold uppercase tracking-wider px-3.5 py-1.5 rounded-full border border-indigo-500/30">
                ✨ Enterprise Desk OS
            </span>
            <h1 class="text-4xl sm:text-5xl font-black mt-4 mb-3 text-white tracking-tight leading-tight">
                Conflict-Free Clinic Front Desk Operations
            </h1>
            <p class="text-slate-300 text-base leading-relaxed mb-6 font-normal">
                Eliminate double-booked doctors, automate late cancellation penalties, and search patient schedules instantly with microsecond precision.
            </p>
        </div>
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown("""
        <div class="metric-card">
            <div class="w-10 h-10 rounded-lg bg-blue-500/10 border border-blue-500/20 text-blue-400 flex items-center justify-center text-lg mb-3">
                <i class="fa-solid fa-calendar-check"></i>
            </div>
            <div class="text-slate-400 text-xs font-semibold uppercase tracking-wider">Booking Accuracy</div>
            <div class="text-3xl font-extrabold text-white mt-1">100%</div>
            <div class="text-emerald-400 text-xs font-medium mt-1">Zero Overlaps</div>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown("""
        <div class="metric-card">
            <div class="w-10 h-10 rounded-lg bg-amber-500/10 border border-amber-500/20 text-amber-400 flex items-center justify-center text-lg mb-3">
                <i class="fa-solid fa-clock-rotate-left"></i>
            </div>
            <div class="text-slate-400 text-xs font-semibold uppercase tracking-wider">Cancellation Window</div>
            <div class="text-3xl font-extrabold text-white mt-1">24 Hrs</div>
            <div class="text-amber-400 text-xs font-medium mt-1">Late Fee: $25.00</div>
        </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown("""
        <div class="metric-card">
            <div class="w-10 h-10 rounded-lg bg-indigo-500/10 border border-indigo-500/20 text-indigo-400 flex items-center justify-center text-lg mb-3">
                <i class="fa-solid fa-bolt"></i>
            </div>
            <div class="text-slate-400 text-xs font-semibold uppercase tracking-wider">Search Latency</div>
            <div class="text-3xl font-extrabold text-white mt-1">&lt; 50ms</div>
            <div class="text-indigo-300 text-xs font-medium mt-1">Paginated Query</div>
        </div>
        """, unsafe_allow_html=True)
    with col4:
        st.markdown("""
        <div class="metric-card">
            <div class="w-10 h-10 rounded-lg bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 flex items-center justify-center text-lg mb-3">
                <i class="fa-solid fa-user-doctor"></i>
            </div>
            <div class="text-slate-400 text-xs font-semibold uppercase tracking-wider">Active On-Call</div>
            <div class="text-3xl font-extrabold text-white mt-1">4 Doctors</div>
            <div class="text-emerald-400 text-xs font-medium mt-1">All Specialties</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    
    col_feat, col_road = st.columns(2)
    with col_feat:
        st.markdown("""
        <div class="bg-slate-900/60 border border-slate-800 rounded-2xl p-6">
            <h3 class="text-lg font-bold text-white mb-3 flex items-center space-x-2">
                <i class="fa-solid fa-shield-halved text-blue-400"></i>
                <span>Core System Features</span>
            </h3>
            <ul class="space-y-2.5 text-slate-300 text-sm">
                <li class="flex items-start"><i class="fa-solid fa-check text-emerald-400 mt-1 mr-2.5"></i><b>Algorithmic Overlap Prevention:</b> Uses atomic range validation (<code class="bg-slate-800 px-1.5 py-0.5 rounded text-blue-300 text-xs">start &lt; new_end AND end &gt; new_start</code>).</li>
                <li class="flex items-start"><i class="fa-solid fa-check text-emerald-400 mt-1 mr-2.5"></i><b>Fair Cancellation Policy:</b> Automatic notice detection. Late cancellations carry a $25.00 fee, while timely ones remain free.</li>
                <li class="flex items-start"><i class="fa-solid fa-check text-emerald-400 mt-1 mr-2.5"></i><b>Instant Search & Filters:</b> Fast substring matching on patient names, date filtering, and multi-column sorting.</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    with col_road:
        st.markdown("""
        <div class="bg-slate-900/60 border border-slate-800 rounded-2xl p-6">
            <h3 class="text-lg font-bold text-white mb-3 flex items-center space-x-2">
                <i class="fa-solid fa-rocket text-indigo-400"></i>
                <span>Roadmap (Next Releases)</span>
            </h3>
            <ul class="space-y-2.5 text-slate-300 text-sm">
                <li class="flex items-center"><span class="w-6 h-6 rounded-full bg-indigo-500/20 text-indigo-400 flex items-center justify-center text-xs font-bold mr-2.5">1</span> <b>Automated SMS Reminders:</b> Instant notification 24 hours prior.</li>
                <li class="flex items-center"><span class="w-6 h-6 rounded-full bg-indigo-500/20 text-indigo-400 flex items-center justify-center text-xs font-bold mr-2.5">2</span> <b>Patient Self-Service Portal:</b> Reschedule directly via magic links.</li>
                <li class="flex items-center"><span class="w-6 h-6 rounded-full bg-indigo-500/20 text-indigo-400 flex items-center justify-center text-xs font-bold mr-2.5">3</span> <b>Revenue Analytics:</b> Track slot utilization and cancellation loss analytics.</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

# ==========================================
# PAGE 2: AUTHENTICATION PORTAL
# ==========================================
elif st.session_state.active_tab == "Login / Register":
    st.markdown('<h2 class="text-2xl font-bold text-white mb-4"><i class="fa-solid fa-lock text-blue-400 mr-2"></i>Staff Portal Access</h2>', unsafe_allow_html=True)
    tab_login, tab_reg = st.tabs(["Sign In", "Create Staff Account"])

    with tab_login:
        with st.form("login_form"):
            u_name = st.text_input("Username")
            u_pass = st.text_input("Password", type="password")
            submit = st.form_submit_button("Log In")
            if submit:
                r = requests.post(f"{API_BASE}/auth/login", json={"username": u_name, "password": u_pass})
                if r.status_code == 200:
                    st.session_state.logged_in = True
                    st.session_state.username = r.json()["username"]
                    st.session_state.active_tab = "Book Appointment"
                    st.success("Successfully authenticated!")
                    st.rerun()
                else:
                    st.error("Invalid username or password.")

    with tab_reg:
        with st.form("register_form"):
            r_name = st.text_input("Full Name")
            r_user = st.text_input("Username")
            r_pass = st.text_input("Password", type="password")
            submit_reg = st.form_submit_button("Register Account")
            if submit_reg:
                r = requests.post(f"{API_BASE}/auth/register", json={"username": r_user, "password": r_pass, "full_name": r_name})
                if r.status_code == 200:
                    st.success("Account created successfully! Please log in using the Sign In tab.")
                else:
                    st.error(r.json().get("detail", "Registration failed"))

# ==========================================
# PAGE 3: BOOK APPOINTMENT
# ==========================================
elif st.session_state.active_tab == "Book Appointment":
    st.markdown('<h2 class="text-2xl font-bold text-white mb-2"><i class="fa-solid fa-calendar-plus text-blue-400 mr-2"></i>Conflict-Free Appointment Booking</h2>', unsafe_allow_html=True)
    doctors = fetch_doctors()
    doc_dict = {f"{d['name']} ({d['specialty']})": d['id'] for d in doctors}

    st.info("💡 **Validation Rules Active:** Patient Name is required and Mobile Number must contain exactly **10 digits**.")

    with st.form("booking_form"):
        c1, c2 = st.columns(2)
        with c1:
            patient_name = st.text_input("Patient Full Name", placeholder="e.g. John Doe").strip()
        with c2:
            patient_phone = st.text_input("Patient Mobile Number (10 Digits)", placeholder="e.g. 9876543210", max_chars=10).strip()

        selected_doc = st.selectbox("Assigned Doctor Specialist", list(doc_dict.keys()))
        
        col_date, col_time, col_dur = st.columns(3)
        with col_date:
            appt_date = st.date_input("Appointment Date", min_value=date.today())
        with col_time:
            appt_time = st.time_input("Start Time", value=time(9, 0))
        with col_dur:
            duration = st.selectbox("Slot Duration", [15, 30, 45, 60], index=1, format_func=lambda x: f"{x} Minutes")

        submit = st.form_submit_button("Submit & Confirm Slot")

        if submit:
            has_name = bool(patient_name)
            has_phone = bool(patient_phone)
            is_valid_phone = bool(re.match(r"^\d{10}$", patient_phone))

            if not has_name and not has_phone:
                st.error("❌ Booking Failed: Both Patient Name and Mobile Number are missing.")
            elif not has_name:
                st.error("❌ Booking Failed: Patient Name is missing.")
            elif not has_phone:
                st.error("❌ Booking Failed: Mobile Number is missing.")
            elif not is_valid_phone:
                st.error("❌ Booking Failed: Mobile Number must be exactly 10 numeric digits (e.g., 9876543210).")
            else:
                start_dt = datetime.combine(appt_date, appt_time)
                payload = {
                    "patient_name": patient_name,
                    "patient_phone": patient_phone,
                    "doctor_id": doc_dict[selected_doc],
                    "start_time": start_dt.isoformat(),
                    "duration_minutes": duration
                }
                r = requests.post(f"{API_BASE}/appointments", json=payload)
                if r.status_code == 200:
                    st.balloons()
                    st.success(f"✅ Slot successfully confirmed for {patient_name} with {selected_doc}!")
                elif r.status_code == 409:
                    st.error(f"🚫 Slot Conflict Blocked! {r.json()['detail']}")
                else:
                    st.error(f"Booking Error: {r.json().get('detail', 'Failed to schedule appointment')}")

# ==========================================
# PAGE 4: DOCTOR DAILY SCHEDULE
# ==========================================
elif st.session_state.active_tab == "Doctor Schedule":
    st.markdown('<h2 class="text-2xl font-bold text-white mb-4"><i class="fa-solid fa-user-doctor text-blue-400 mr-2"></i>Daily Schedule Matrix</h2>', unsafe_allow_html=True)
    doctors = fetch_doctors()
    doc_options = {"All Doctors View": None}
    doc_options.update({d['name']: d['id'] for d in doctors})

    col1, col2 = st.columns([2, 1])
    with col1:
        sel_doc_name = st.selectbox("Doctor Filter", list(doc_options.keys()))
    with col2:
        sel_date = st.date_input("Filter Date", value=date.today())

    params = {"date_str": sel_date.strftime("%Y-%m-%d"), "page_size": 50}
    if doc_options[sel_doc_name]:
        params["doctor_id"] = doc_options[sel_doc_name]

    r = requests.get(f"{API_BASE}/appointments/search", params=params)
    if r.status_code == 200:
        data = r.json()["items"]
        st.markdown(f"### Appointments on **{sel_date.strftime('%A, %B %d, %Y')}**")
        
        if not data:
            st.info("No appointments scheduled for this doctor/date.")
        else:
            for item in data:
                st_time = datetime.fromisoformat(item["start_time"]).strftime("%I:%M %p")
                en_time = datetime.fromisoformat(item["end_time"]).strftime("%I:%M %p")
                status = item["status"]
                
                badge_class = "status-confirmed" if status == "CONFIRMED" else "status-cancelled"
                fee_info = f" | Fee: ${item['cancellation_fee']:.2f}" if status == "CANCELLED" else ""

                st.markdown(f"""
                <div class="bg-slate-900/80 border border-slate-800 rounded-xl p-4 mb-3 flex items-center justify-between shadow-md">
                    <div>
                        <span class="{badge_class}">{status}{fee_info}</span>
                        <h4 class="text-lg font-bold text-white mt-2">{item['patient_name']}</h4>
                        <p class="text-xs text-slate-400 mt-1"><i class="fa-solid fa-user-doctor text-blue-400 mr-1"></i> Dr. {item['doctor_name']} &nbsp;|&nbsp; <i class="fa-solid fa-phone text-slate-400 mr-1"></i> {item['patient_phone']}</p>
                    </div>
                    <div class="text-right">
                        <div class="text-sm font-bold text-indigo-300 bg-slate-800/80 px-3 py-1.5 rounded-lg border border-slate-700/60"><i class="fa-regular fa-clock mr-1"></i> {st_time} - {en_time}</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

# ==========================================
# PAGE 5: PATIENT LOOKUP & SEARCH
# ==========================================
elif st.session_state.active_tab == "Patient Lookup":
    st.markdown('<h2 class="text-2xl font-bold text-white mb-4"><i class="fa-solid fa-magnifying-glass text-blue-400 mr-2"></i>Patient Lookup & Cancellation Engine</h2>', unsafe_allow_html=True)

    col_s, col_sort, col_order = st.columns([3, 1, 1])
    with col_s:
        query = st.text_input("Patient Search", placeholder="Type patient name to filter...")
    with col_sort:
        sort_by = st.selectbox("Sort Field", ["start_time", "patient_name", "created_at"])
    with col_order:
        sort_order = st.selectbox("Order", ["asc", "desc"])

    page = st.number_input("Page Number", min_value=1, value=1, step=1)

    params = {
        "search": query if query else None,
        "sort_by": sort_by,
        "sort_order": sort_order,
        "page": page,
        "page_size": 5
    }

    r = requests.get(f"{API_BASE}/appointments/search", params=params)
    if r.status_code == 200:
        res = r.json()
        st.caption(f"Showing page {res['page']} of {max(1, (res['total'] + 4)//5)} | Total Records: {res['total']}")
        
        for appt in res["items"]:
            st_time = datetime.fromisoformat(appt["start_time"]).strftime("%b %d, %Y at %I:%M %p")
            
            with st.container():
                c1, c2, c3, c4 = st.columns([3, 3, 2, 2])
                c1.markdown(f"**{appt['patient_name']}**\n\n📞 `{appt['patient_phone']}`")
                c2.markdown(f"**Dr. {appt['doctor_name']}**\n\n🗓️ {st_time}")
                
                if appt["status"] == "CONFIRMED":
                    c3.markdown('<span class="status-confirmed">CONFIRMED</span>', unsafe_allow_html=True)
                    if c4.button("Cancel Slot", key=f"btn_{appt['id']}"):
                        cancel_r = requests.put(f"{API_BASE}/appointments/{appt['id']}/cancel")
                        if cancel_r.status_code == 200:
                            res_data = cancel_r.json()
                            if res_data["is_late"]:
                                st.warning(f"Cancelled late (<24h). Late Fee Applied: ${res_data['cancellation_fee']:.2f}")
                            else:
                                st.success("Cancelled with >24h notice (No Fee).")
                            st.rerun()
                else:
                    c3.markdown('<span class="status-cancelled">CANCELLED</span>', unsafe_allow_html=True)
                    c4.markdown(f"Fee: **${appt['cancellation_fee']:.2f}**")
                
                st.markdown("<hr style='border-color: #1e293b; margin: 12px 0;'>", unsafe_allow_html=True)
