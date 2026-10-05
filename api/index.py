"""Vercel entrypoint for the FastAPI dashboard.

The canonical application remains in ref_sih_amr.dashboard.backend.main;
this thin adapter only gives Vercel an explicit ASGI entrypoint.
"""
from ref_sih_amr.dashboard.backend.main import app

__all__ = ["app"]
