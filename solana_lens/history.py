# -*- coding: utf-8 -*-
"""Transaction-history parsing and markdown formatting."""
from datetime import datetime, timezone

from .balance import lamports_to_sol


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


def parse_transfers(tx):
    """Extract SOL and SPL transfers from a jsonParsed getTransaction result."""
    transfers = []
    msg = (tx.get("transaction") or {}).get("message") or {}
    for inst in msg.get("instructions") or []:
        parsed = inst.get("parsed") or {}
        typ = parsed.get("type")
        info = parsed.get("info") or {}
        if typ == "transfer":
            transfers.append({
                "kind": "SOL",
                "source": info.get("source"),
                "destination": info.get("destination"),
                "amount": lamports_to_sol(info.get("lamports", 0)),
                "token": "SOL",
            })
        elif typ == "transferChecked":
            ta = info.get("tokenAmount") or {}
            transfers.append({
                "kind": "SPL",
                "source": info.get("source"),
                "destination": info.get("destination"),
                "amount": ta.get("uiAmountString"),
                "token": info.get("mint"),
            })
    return transfers
