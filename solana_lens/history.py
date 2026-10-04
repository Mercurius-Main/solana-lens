# -*- coding: utf-8 -*-
"""Transaction-history parsing and markdown formatting."""
from datetime import datetime, timezone


def format_timestamp(block_time):
    """Render a Solana blockTime (unix seconds) as UTC, or 'unknown'."""
    if block_time is None:
        return "unknown"
    return datetime.fromtimestamp(block_time, tz=timezone.utc).strftime("%Y-%m-%d %H:%M:%S")


def short_signature(signature, length=8):
    if not signature:
        return ""
    return signature[:length] + "..." if len(signature) > length else signature


def history_rows(signatures):
    """Convert getSignaturesForAddress output into a list of dicts."""
    rows = []
    for s in signatures:
        rows.append({
            "signature": s.get("signature", ""),
            "block_time": s.get("blockTime"),
            "status": "success" if s.get("err") is None else "error",
            "memo": (s.get("memo") or "").strip(),
        })
    return rows


def to_markdown(rows):
    """Render history rows as a GitHub-flavoured markdown table."""
    lines = ["| Signature | Time (UTC) | Status | Memo |", "|---|---|---|---|"]
    for r in rows:
        memo = (r["memo"] or "").replace("|", "\\|")[:40]
        lines.append(
            f"| `{short_signature(r['signature'])}` | {format_timestamp(r['block_time'])} "
            f"| {r['status']} | {memo} |")
    return "\n".join(lines)
