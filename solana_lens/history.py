# -*- coding: utf-8 -*-
"""Transaction-history parsing and markdown formatting."""
from collections import Counter
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


PROGRAM_NAMES = {
    "11111111111111111111111111111111": "System (SOL transfer)",
    "TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA": "SPL Token",
    "ATokenGPvbdGVxr1b2hvZbsiqW5xWH25efTNsLJA8knL": "Associated Token",
    "ComputeBudget111111111111111111111111111111": "Compute Budget",
    "675kPX9MHTjS2zt1qfr1NYHuzeLXfQM9H24wFSUt1Mp8": "Raydium AMM",
    "JUP6LkbZbjS1jKKwapdHNy74zcZ3tLUZoi5QNyVTaV4": "Jupiter",
    "M2mx93ekt1fmXSVkTrUL9xVFHkmME8HTUi5Cyc5aF7K": "Magic Eden",
    "METAewfxy7bgHprWBokRxSaLz7zZxvXFVdNaX6pWjK5": "Metaplex",
    "cysPXAjehMpVXLapTavcH9WkUcs2uqDsdf6WjTYDNrZ": "Raydium CPMM",
    "CAMMCzo5YL8w4VFF8KVHrK22GGUsp5VTaW7grrKgrWqK": "Raydium CLMM",
    "whirLbMiicVdio4qvUfM5KAg6Ct8VwpYzGff3uctyCc": "Orca Whirlpool",
    "9W959DqEETiGZocYWCQPaJ6sBmUzgfxXfqGeTEdp3aQP": "Orca",
    "JUP2jxvXaqu7NQY1GmNF4m1vodw12LVXYxbFLiJvo1Em": "Jupiter DCA",
    "PhoeNiXZ8ByJGLkxNfZRnkUfjvmuYqLR89jjFHGqdXY": "Phoenix",
    "MemoSq4gqABAXKb96qnH8TysNcWxMyWCqXgDLGmfcHr": "Memo",
}


def program_name(program_id):
    """Return a friendly name for a known program id, else the raw id."""
    return PROGRAM_NAMES.get(program_id, program_id)


def parse_program_activity(txs):
    """Summarise which programs an address interacts with most.

    Expects a list of jsonParsed getTransaction results. Returns a list of
    (program_id, count) sorted by count desc.
    """
    counter = Counter()
    for tx in txs:
        msg = (tx.get("transaction") or {}).get("message") or {}
        seen = set()
        for inst in msg.get("instructions") or []:
            pid = inst.get("programId")
            if pid and pid not in seen:
                counter[pid] += 1
                seen.add(pid)
    return counter.most_common()
