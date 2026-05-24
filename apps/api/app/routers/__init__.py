# apps/api/app/routers/__init__.py
"""API route handlers"""

from . import (
    auth,
    dashboard,
    hospitals,
    pricing,
    bookings,
    recovery,
    patients,
    financing,
    health,
)

__all__ = [
    "auth",
    "dashboard",
    "hospitals",
    "pricing",
    "bookings",
    "recovery",
    "patients",
    "financing",
    "health",
]
