"""Pure scheduling and cancellation rules."""
from datetime import datetime, timedelta


def overlaps(a_start, a_end, b_start, b_end):
    return a_start < b_end and a_end > b_start


def cancellation_fee(start_at, now, free_hours, late_fee):
    return 0.0 if (start_at - now).total_seconds() / 3600 >= free_hours else late_fee


def free_slots(day, work_start="09:00", work_end="17:00", slot_minutes=30, busy=(), now=None, duration_minutes=None):
    start = datetime.combine(day, datetime.strptime(work_start, "%H:%M").time())
    end = datetime.combine(day, datetime.strptime(work_end, "%H:%M").time())
    duration = duration_minutes or slot_minutes
    result = []
    while start + timedelta(minutes=duration) <= end:
        slot_end = start + timedelta(minutes=duration)
        if (now is None or start >= now) and not any(overlaps(start, slot_end, a, b) for a, b in busy):
            result.append(start)
        start += timedelta(minutes=slot_minutes)
    return result
