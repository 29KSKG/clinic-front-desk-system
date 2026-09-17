# 🩺 CareSync — Front Desk Operations & Appointment System

CareSync is an enterprise-grade front-desk appointment management system built with **FastAPI** (Backend) and **Streamlit** (Frontend). It features conflict-free appointment scheduling, late cancellation enforcement, microsecond search capabilities, pre-seeded admin credentials, and a polished glassmorphic UI.

---

## 🌟 Key Features

* **Pre-configured Admin Access:** Default credentials (`ADMIN` / `ADMIN`) available out of the box for instant evaluation.
* **Conflict-Free Booking:** Algorithmic overlapping slot prevention using interval-intersection logic (`start < existing_end AND end > existing_start`).
* **Fair Cancellation Policy:** Automatic detection of cancellation windows. Notice given $\ge 24\text{ hours}$ incurs **$\$0.00$** fee; late notice ($< 24\text{ hours}$) incurs a **$\$25.00$** penalty.
* **Fast Search & Filters:** Microsecond search latency with substring matching, doctor-wise schedule filtering, multi-column sorting, and server-side pagination.
* **Strict Form Validations:** Real-time checking for patient name presence and exact **10-digit mobile number** formatting before payload transmission.
* **Glassmorphic UI:** Modern Streamlit frontend styled with Tailwind CSS, active tab highlights, hover states, and dynamic status badges.

---

## 🛠️ Tech Stack

* **Frontend:** Streamlit, Tailwind CSS, FontAwesome Icons
* **Backend:** FastAPI, Python 3.10+
* **Database / Storage:** In-Memory / SQLite (Expandable to PostgreSQL)
* **Data Validation:** Pydantic, Regular Expressions

---

## 🔑 Default Login Credentials

To quickly test and evaluate the system, use the pre-configured admin account:

* **Username:** `ADMIN`
* **Password:** `ADMIN`

*(You can also register new staff accounts using the Login / Register tab in the top navigation bar).*

---

## 🚀 How to Start & Run the Project

### Step 1: Install Dependencies
Ensure Python 3.10+ is installed on your system. Run:

`pip install fastapi uvicorn streamlit requests`

### Step 2: Launch the FastAPI Backend
Start the backend service on port 8000:

`uvicorn main:app --reload --port 8000`

* **Backend API Base URL:** `http://127.0.0.1:8000`
* **Interactive Swagger Documentation:** `http://127.0.0.1:8000/docs`

### Step 3: Launch the Streamlit Frontend
Open a new terminal window or tab and run:

`streamlit run app.py`

* **Frontend Application Interface:** `http://localhost:8501`

---

## 📁 Project File Structure

* `main.py` — FastAPI Backend (REST Endpoints, Business Logic, ADMIN Auth)
* `app.py` — Streamlit Frontend (Glassmorphic Navigation Bar & UI)
* `README.md` — Setup, Credentials & Execution Instructions
* `Reasoning.md` — Engineering Trade-offs, Architectural Choices & Specs

---

## 🧪 API Endpoints Summary

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `POST` | `/api/auth/login` | Authenticate staff (Supports `ADMIN`/`ADMIN`) |
| `POST` | `/api/auth/register` | Register new staff credentials |
| `GET` | `/api/doctors` | Retrieve list of active doctors |
| `POST` | `/api/appointments` | Book new conflict-checked appointment |
| `GET` | `/api/appointments/search` | Search/Filter appointments with pagination |
| `PUT` | `/api/appointments/{id}/cancel` | Cancel appointment & apply fee logic |
