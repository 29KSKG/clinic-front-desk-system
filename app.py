"""Bright, engaging Streamlit front desk UI for the CareSync API."""
import os
from datetime import date, datetime, time

import requests
import streamlit as st

API = os.getenv("API_BASE_URL", "http://127.0.0.1:8000/api")

st.set_page_config(
    page_title="CareSync | Front Desk",
    page_icon="🩺",
    layout="wide",
    initial_sidebar_state="expanded",
)

# -----------------------------------------------------------------------------
# Visual system
# -----------------------------------------------------------------------------
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700;800&family=Space+Grotesk:wght@500;600;700&display=swap');

    :root {
      --ink: #172554;
      --muted: #64748b;
      --purple: #7c3aed;
      --pink: #ec4899;
      --cyan: #06b6d4;
      --lime: #84cc16;
      --orange: #f97316;
      --surface: #ffffff;
      --soft: #f8f7ff;
    }

    html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; }
    .stApp { background: linear-gradient(135deg, #fff7ed 0%, #f5f3ff 45%, #ecfeff 100%); }
    .main .block-container { max-width: 1440px; padding: 2rem 3rem 4rem; }
    h1, h2, h3, h4 { font-family: 'Space Grotesk', sans-serif; color: var(--ink); }
    h1 { letter-spacing: -0.04em; }
    header[data-testid="stHeader"] { background: transparent; }
    section[data-testid="stSidebar"] { background: linear-gradient(180deg, #172554 0%, #312e81 55%, #7e22ce 100%); }
    section[data-testid="stSidebar"] * { color: #fff !important; }
    section[data-testid="stSidebar"] .stRadio label { padding: .65rem .8rem; border-radius: 12px; }
    section[data-testid="stSidebar"] .stRadio label:hover { background: rgba(255,255,255,.16); }
    section[data-testid="stSidebar"] .stButton button { background: rgba(255,255,255,.15); border: 1px solid rgba(255,255,255,.3); color: white; }

    .brand { display:flex; align-items:center; gap:14px; margin: 0 0 2rem; }
    .brand-icon { width:48px; height:48px; display:grid; place-items:center; border-radius:16px; background:linear-gradient(135deg,#22d3ee,#a855f7 55%,#ec4899); box-shadow:0 10px 25px rgba(236,72,153,.35); font-size:25px; }
    .brand-title { font: 700 25px 'Space Grotesk'; letter-spacing:-.04em; }
    .brand-sub { color:#c4b5fd !important; font-size:11px; letter-spacing:.12em; text-transform:uppercase; }

    .hero { position:relative; overflow:hidden; padding:2.6rem 3rem; border-radius:28px; color:white; background:linear-gradient(115deg,#312e81,#7c3aed 48%,#db2777); box-shadow:0 20px 45px rgba(109,40,217,.25); margin-bottom:1.6rem; }
    .hero:after { content:'✦'; position:absolute; right:8%; top:-30px; font-size:180px; color:rgba(255,255,255,.13); transform:rotate(18deg); }
    .hero h1, .hero p { color:white; position:relative; z-index:1; }
    .hero h1 { font-size:clamp(2rem,4vw,3.5rem); margin:0 0 .6rem; }
    .hero p { max-width:680px; font-size:1.08rem; opacity:.9; }
    .eyebrow { color:#fef08a !important; font-size:.76rem; font-weight:800; letter-spacing:.16em; text-transform:uppercase; }

    .metric { background:rgba(255,255,255,.88); border:1px solid rgba(124,58,237,.12); border-radius:20px; padding:1.15rem 1.3rem; box-shadow:0 10px 25px rgba(30,41,59,.06); min-height:115px; }
    .metric-label { color:var(--muted); font-size:.82rem; font-weight:700; }
    .metric-value { color:var(--ink); font:700 1.75rem 'Space Grotesk'; margin:.25rem 0; }
    .metric-note { font-size:.78rem; font-weight:700; }
    .green { color:#16a34a; } .purple { color:#7c3aed; } .orange { color:#ea580c; } .cyan { color:#0891b2; }

    .panel { background:rgba(255,255,255,.82); border:1px solid rgba(148,163,184,.2); border-radius:22px; padding:1.35rem; box-shadow:0 12px 30px rgba(30,41,59,.06); }
    .appt-card { background:white; border-left:6px solid #8b5cf6; border-radius:18px; padding:1rem 1.2rem; margin:.7rem 0; box-shadow:0 8px 22px rgba(30,41,59,.07); }
    .appt-card.cancelled { border-left-color:#fb7185; opacity:.78; }
    .appt-time { color:#7c3aed; font:700 1rem 'Space Grotesk'; }
    .appt-name { color:var(--ink); font-size:1.05rem; font-weight:800; }
    .pill { display:inline-block; padding:.25rem .65rem; border-radius:999px; font-size:.72rem; font-weight:800; }
    .pill-confirmed { color:#047857; background:#d1fae5; } .pill-cancelled { color:#be123c; background:#ffe4e6; }
    div.stButton > button { border:0; border-radius:12px; font-weight:800; background:linear-gradient(135deg,#7c3aed,#db2777); color:white; box-shadow:0 7px 15px rgba(124,58,237,.2); transition:.2s; }
    div.stButton > button:hover { transform:translateY(-2px); box-shadow:0 10px 22px rgba(124,58,237,.3); }
    div[data-testid="stForm"] { background:rgba(255,255,255,.82); border:1px solid rgba(124,58,237,.15); border-radius:22px; padding:1.25rem; }
    div[data-baseweb="input"] > div, div[data-baseweb="select"] > div { border-radius:12px; border-color:#ddd6fe; }
    .footer { text-align:center; color:#94a3b8; padding:2rem 0 0; font-size:.82rem; }
    </style>
    """,
    unsafe_allow_html=True,
)


def request(method, path, **kwargs):
    try:
        response = requests.request(method, f"{API}{path}", timeout=15, **kwargs)
        try:
            data = response.json()
        except ValueError:
            data = {"detail": response.text}
        return response, data
    except requests.RequestException as exc:
        return None, {"detail": f"API unavailable: {exc}"}


def require_login():
    if not st.session_state.logged_in:
        st.warning("🔐 Please sign in to access the front desk.")
        return False
    return True


def appointment_card(item):
    cancelled = item["status"] != "CONFIRMED"
    status_class = "pill-cancelled" if cancelled else "pill-confirmed"
    card_class = "appt-card cancelled" if cancelled else "appt-card"
    start = datetime.fromisoformat(item["start_time"]).strftime("%b %d · %I:%M %p")
    end = datetime.fromisoformat(item["end_time"]).strftime("%I:%M %p")
    st.markdown(
        f"""<div class="{card_class}">
        <div style="display:flex;justify-content:space-between;gap:1rem;align-items:center;flex-wrap:wrap">
          <div><div class="appt-time">{start} — {end}</div>
          <div class="appt-name">{item['patient_name']}</div>
          <div style="color:#64748b;font-size:.86rem">📞 {item['patient_phone']} &nbsp;•&nbsp; 🩺 {item['doctor_name']}</div></div>
          <span class="pill {status_class}">{item['status']}</span>
        </div></div>""",
        unsafe_allow_html=True,
    )


if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.username = ""

with st.sidebar:
    st.markdown('<div class="brand"><div class="brand-icon">🩺</div><div><div class="brand-title">CareSync</div><div class="brand-sub">Front Desk OS</div></div></div>', unsafe_allow_html=True)
    if st.session_state.logged_in:
        st.success(f"Online · {st.session_state.username}")
    page = st.radio("Workspace", ["✨ Overview", "🔐 Login / Register", "➕ Book appointment", "📅 Schedule", "🔎 Appointment search"], label_visibility="collapsed")
    st.divider()
    st.caption("A brighter way to care for every patient.")
    if st.session_state.logged_in and st.button("Sign out", use_container_width=True):
        st.session_state.logged_in = False
        st.session_state.username = ""
        st.rerun()

if page == "✨ Overview":
    st.markdown('<div class="hero"><div class="eyebrow">✨ Your clinic, beautifully organised</div><h1>Make every appointment feel effortless.</h1><p>CareSync keeps your front desk fast, friendly and completely conflict-free — from the first call to the final follow-up.</p></div>', unsafe_allow_html=True)
    m1, m2, m3, m4 = st.columns(4)
    for col, label, value, note, color in [(m1, "Booking protection", "100%", "No overlapping slots", "green"), (m2, "Cancellation window", "24 hrs", "Free notice period", "purple"), (m3, "Late cancellation", "$25", "Automatic fee rule", "orange"), (m4, "Team status", "Ready", "Front desk online", "cyan")]:
        col.markdown(f'<div class="metric"><div class="metric-label">{label}</div><div class="metric-value">{value}</div><div class="metric-note {color}">● {note}</div></div>', unsafe_allow_html=True)
    st.write("")
    left, right = st.columns([1.2, .8])
    with left:
        st.markdown('<div class="panel"><h2>Everything your desk needs</h2><p style="color:#64748b">Spend less time fixing calendar mistakes and more time welcoming patients.</p></div>', unsafe_allow_html=True)
        f1, f2, f3 = st.columns(3)
        f1.info("🛡️ **Conflict-free**\n\nOverlapping doctor bookings are blocked before they happen.")
        f2.success("⚡ **Fast search**\n\nFind a patient or appointment in seconds.")
        f3.warning("💛 **Fair policy**\n\nCancellation fees are applied consistently.")
    with right:
        st.markdown('<div class="panel"><h3>Quick start</h3><p style="color:#64748b">Use the menu to jump into your day.</p></div>', unsafe_allow_html=True)
        st.markdown("**1.** Sign in to your team account\n\n**2.** Choose a doctor and patient\n\n**3.** Confirm a free appointment slot")
        st.info("Demo account: **admin / admin123**")

elif page == "🔐 Login / Register":
    st.markdown('<div class="hero"><div class="eyebrow">🔐 Secure team access</div><h1>Welcome back.</h1><p>Sign in to keep the clinic moving.</p></div>', unsafe_allow_html=True)
    login, register = st.tabs(["🌈 Sign in", "✨ Create account"])
    with login:
        with st.form("login"):
            username = st.text_input("Username", placeholder="admin")
            password = st.text_input("Password", type="password", placeholder="••••••••")
            if st.form_submit_button("Sign in →", use_container_width=True):
                r, data = request("POST", "/auth/login", json={"username": username, "password": password})
                if r is not None and r.ok:
                    st.session_state.logged_in = True
                    st.session_state.username = data["username"]
                    st.success("You’re in! Loading your workspace…")
                    st.rerun()
                else:
                    st.error(data.get("detail", "Invalid credentials"))
    with register:
        with st.form("register"):
            full_name = st.text_input("Full name")
            username = st.text_input("New username")
            password = st.text_input("New password", type="password")
            if st.form_submit_button("Create my account →", use_container_width=True):
                r, data = request("POST", "/auth/register", json={"username": username, "password": password, "full_name": full_name})
                if r is not None and r.ok:
                    st.success(data.get("message", "Account created. You can now sign in."))
                else:
                    st.error(data.get("detail", "Registration failed"))

elif page == "➕ Book appointment":
    st.markdown('<div class="hero"><div class="eyebrow">➕ New appointment</div><h1>Book a moment of care.</h1><p>Choose the right doctor, time and patient details. We’ll protect the schedule for you.</p></div>', unsafe_allow_html=True)
    if require_login():
        r, doctors = request("GET", "/doctors")
        doctors = doctors if r is not None and r.ok else []
        if not doctors:
            st.info("No active doctors found. Add doctors in the API first.")
        else:
            with st.form("booking"):
                st.subheader("Patient details")
                c1, c2 = st.columns(2)
                patient_name = c1.text_input("Patient name", placeholder="e.g. Alex Morgan")
                patient_phone = c2.text_input("Phone number", placeholder="e.g. 555-0100")
                st.subheader("Appointment details")
                selected = st.selectbox("Doctor", doctors, format_func=lambda d: f"{d['name']}  ·  {d['specialty']}")
                c1, c2, c3 = st.columns(3)
                appointment_date = c1.date_input("Date", min_value=date.today())
                appointment_time = c2.time_input("Start time", value=time(9, 0))
                duration = c3.selectbox("Duration", [15, 30, 45, 60], index=1, format_func=lambda x: f"{x} minutes")
                if st.form_submit_button("💜 Confirm appointment", use_container_width=True):
                    payload = {"patient_name": patient_name, "patient_phone": patient_phone, "doctor_id": selected["id"], "start_time": datetime.combine(appointment_date, appointment_time).isoformat(), "duration_minutes": duration}
                    r, data = request("POST", "/appointments", json=payload)
                    if r is not None and r.ok:
                        st.balloons()
                        st.success(f"Appointment #{data['id']} booked for {patient_name}!")
                    else:
                        st.error(data.get("detail", "Booking failed"))

elif page in ("📅 Schedule", "🔎 Appointment search"):
    st.markdown('<div class="hero"><div class="eyebrow">📅 Your clinic rhythm</div><h1>See the day at a glance.</h1><p>Search, review and manage every appointment from one calm, colourful workspace.</p></div>', unsafe_allow_html=True)
    if require_login():
        c1, c2 = st.columns([1.5, 1])
        query = c1.text_input("🔎 Search by patient", placeholder="Type a patient name")
        selected_date = c2.date_input("📆 Filter by date", value=date.today())
        r, data = request("GET", "/appointments", params={"search": query or None, "date_str": selected_date.isoformat(), "page_size": 50})
        if r is not None and r.ok:
            st.markdown(f'<div class="metric"><span class="metric-label">Showing</span> <span class="metric-value" style="font-size:1.2rem">{data["total"]} appointment(s)</span></div>', unsafe_allow_html=True)
            if data["items"]:
                for item in data["items"]:
                    appointment_card(item)
                    if item["status"] == "CONFIRMED":
                        if st.button(f"Cancel appointment #{item['id']}", key=f"cancel-{item['id']}"):
                            cr, cancellation = request("PUT", f"/appointments/{item['id']}/cancel")
                            if cr is not None and cr.ok:
                                st.success(f"Cancelled successfully · fee ${cancellation['cancellation_fee']:.2f}")
                                st.rerun()
                            else:
                                st.error(cancellation.get("detail", "Cancellation failed"))
            else:
                st.info("🌼 No appointments found for this search. Try another date or patient name.")
        else:
            st.error(data.get("detail", "Could not load appointments"))

st.markdown('<div class="footer">CareSync · Making every clinic day brighter ✦</div>', unsafe_allow_html=True)
