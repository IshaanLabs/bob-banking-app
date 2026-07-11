"""Shared utilities — session guard decorator."""

from __future__ import annotations

from functools import wraps
from typing import Callable

from flask import redirect, session, url_for


def login_required(view: Callable) -> Callable:
    """Decorator that redirects unauthenticated users to the login page.

    Usage::

        @login_required
        def my_protected_route():
            ...
    """

    @wraps(view)
    def wrapped(*args, **kwargs):
        if "customer_id" not in session:
            return redirect(url_for("auth.login"))
        return view(*args, **kwargs)

    return wrapped
