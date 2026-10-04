# -*- coding: utf-8 -*-
"""Balance formatting helpers."""
from .rpc import LAMPORTS_PER_SOL


def lamports_to_sol(lamports):
    return lamports / LAMPORTS_PER_SOL


def format_sol(lamports):
    """Format lamports as a trimmed, human-readable SOL amount."""
    sol = lamports_to_sol(lamports)
    return f"{sol:.9f}".rstrip("0").rstrip(".")
