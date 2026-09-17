# CareSync — Front Desk Operations & Appointment System

CareSync is a FastAPI and Streamlit clinic front-desk system. It prevents overlapping bookings for a doctor, supports safe cancellation fees, provides doctor and patient search, and includes pagination and sorting for appointment lists.

## Features

- Demo staff account: `admin` / `admin123`
- Doctor directory and active-doctor filtering
- Conflict-free half-open interval booking (`start < existing_end` and `end > existing_start`)
- Past-booking validation
- 24-hour free cancellation policy and configurable late fee
- Appointment search by patient, doctor, and date
- Pagination and whitelisted sorting
- Streamlit front desk UI
- SQLite by default, configurable through environment variables

## Setup

```bash
python -m venv .venv
source .venv/bin/activate       # Windows: .venv\\Scripts\\activate
pip install -r requirements.txt
python seed.py
```

## Run

Start the API:

```bash
uvicorn main:app --reload --port 8000
```

In another terminal start the UI:

```bash
streamlit run app.py
```

- UI: http://localhost:8501
- API docs: http://localhost:8000/docs
- Health check: http://localhost:8000/api/health

Set `API_BASE_URL` when the API is hosted elsewhere. The value should include `/api`, for example `https://example.com/api`.

## Configuration

| Variable | Default | Purpose |
|---|---|---|
| `DATABASE_URL` | `sqlite:///./clinic.db` | SQLAlchemy database URL |
| `SECRET_KEY` | `dev-secret-change-me` | Reserved application secret |
| `FREE_CANCEL_HOURS` | `24` | Notice required for free cancellation |
| `LATE_CANCEL_FEE` | `25` | Late cancellation charge |
| `CURRENCY` | `USD` | Display currency |
| `API_BASE_URL` | `http://127.0.0.1:8000/api` | Streamlit API URL |

## API endpoints

- `POST /api/auth/register`
- `POST /api/auth/login`
- `GET /api/doctors`
- `POST /api/appointments`
- `GET /api/appointments` and `GET /api/appointments/search`
- `PUT /api/appointments/{id}/cancel`
- `GET /api/health`

## Tests

```bash
pytest -q
```

## Project structure

```text
main.py          FastAPI routes and validation
app.py           Streamlit front desk UI
config.py        Environment configuration
database.py      SQLAlchemy engine and sessions
models.py        Database models
schemas.py       Pydantic API schemas
security.py      Password hashing
scheduling.py    Pure overlap, slot, and fee rules
seed.py          Demo data loader
```
