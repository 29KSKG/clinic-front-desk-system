"""Launch the Streamlit front desk UI against the FastAPI API."""
import os
from datetime import date, datetime, time
import requests
import streamlit as st

API = os.getenv("API_BASE_URL", "http://127.0.0.1:8000/api")
st.set_page_config(page_title="CareSync Front Desk", page_icon="🩺", layout="wide")


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


if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.username = ""

st.title("🩺 CareSync")
st.caption("Conflict-free front-desk appointment management")

if st.session_state.logged_in:
    st.sidebar.success(f"Signed in as {st.session_state.username}")
    if st.sidebar.button("Log out"):
        st.session_state.logged_in = False
        st.rerun()

page = st.sidebar.radio("Navigate", ["Home", "Login / Register", "Book appointment", "Schedule", "Appointment search"])

if page == "Home":
    st.header("Front desk operations, without double-booking")
    st.markdown("""CareSync checks overlapping appointments before saving, applies the 24-hour cancellation policy automatically, and provides searchable, paginated schedules.""")
    c1, c2, c3 = st.columns(3)
    c1.metric("Conflict protection", "Enabled")
    c2.metric("Free cancellation notice", "24 hours")
    c3.metric("Late cancellation fee", "$25")
    st.info("Demo login: admin / admin123")

elif page == "Login / Register":
    login, register = st.tabs(["Sign in", "Create account"])
    with login:
        with st.form("login"):
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            if st.form_submit_button("Sign in"):
                r, data = request("POST", "/auth/login", json={"username": username, "password": password})
                if r is not None and r.ok:
                    st.session_state.logged_in = True
                    st.session_state.username = data["username"]
                    st.success("Signed in")
                    st.rerun()
                else:
                    st.error(data.get("detail", "Invalid credentials"))
    with register:
        with st.form("register"):
            full_name = st.text_input("Full name")
            username = st.text_input("New username")
            password = st.text_input("New password", type="password")
            if st.form_submit_button("Create account"):
                r, data = request("POST", "/auth/register", json={"username": username, "password": password, "full_name": full_name})
                st.success(data.get("message", "Account created")) if r is not None and r.ok else st.error(data.get("detail", "Registration failed"))

elif page == "Book appointment":
    if not st.session_state.logged_in:
        st.warning("Sign in first.")
    else:
        r, doctors = request("GET", "/doctors")
        doctors = doctors if r is not None and r.ok else []
        if not doctors:
            st.info("No active doctors found.")
        else:
            with st.form("booking"):
                patient_name = st.text_input("Patient name")
                patient_phone = st.text_input("Patient phone")
                selected = st.selectbox("Doctor", doctors, format_func=lambda d: f"{d['name']} — {d['specialty']}")
                appointment_date = st.date_input("Date", min_value=date.today())
                appointment_time = st.time_input("Start time", value=time(9, 0))
                duration = st.selectbox("Duration", [15, 30, 45, 60], index=1)
                if st.form_submit_button("Confirm booking"):
                    payload = {"patient_name": patient_name, "patient_phone": patient_phone, "doctor_id": selected["id"], "start_time": datetime.combine(appointment_date, appointment_time).isoformat(), "duration_minutes": duration}
                    r, data = request("POST", "/appointments", json=payload)
                    st.success(f"Booked appointment #{data['id']}") if r is not None and r.ok else st.error(data.get("detail", "Booking failed"))

elif page in ("Schedule", "Appointment search"):
    if not st.session_state.logged_in:
        st.warning("Sign in first.")
    else:
        query = st.text_input("Search patient")
        selected_date = st.date_input("Date", value=date.today())
        r, data = request("GET", "/appointments", params={"search": query or None, "date_str": selected_date.isoformat(), "page_size": 50})
        if r is not None and r.ok:
            st.caption(f"{data['total']} appointment(s)")
            for item in data["items"]:
                st.write(f"**{item['patient_name']}** · {item['patient_phone']} · {item['doctor_name']} · {item['start_time']} · `{item['status']}`")
                if item["status"] == "CONFIRMED" and st.button(f"Cancel #{item['id']}", key=f"cancel-{item['id']}"):
                    cr, cancellation = request("PUT", f"/appointments/{item['id']}/cancel")
                    if cr is not None and cr.ok:
                        st.success(f"Cancelled; fee ${cancellation['cancellation_fee']:.2f}")
                        st.rerun()
                    else:
                        st.error(cancellation.get("detail", "Cancellation failed"))
        else:
            st.error(data.get("detail", "Could not load appointments"))
