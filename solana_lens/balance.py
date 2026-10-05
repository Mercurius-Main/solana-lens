# -*- coding: utf-8 -*-
"""Balance formatting helpers."""
from .rpc import LAMPORTS_PER_SOL


def lamports_to_sol(lamports):
    return lamports / LAMPORTS_PER_SOL


def format_sol(lamports):
    """Format lamports as a trimmed, human-readable SOL amount."""
    sol = lamports_to_sol(lamports)
    return f"{sol:.9f}".rstrip("0").rstrip(".")


# Well-known SPL token mints -> human-readable symbol.
TOKEN_NAMES = {
    "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v": "USDC",
    "Es9vMFrzaCERmJfrF4H2FYD4KCoNkY11McCe8BenwNYB": "USDT",
    "So11111111111111111111111111111111111111112": "wSOL",
    "JUPyiwrYJFskUPiHa7hkeR8VUtAeFoSYbKedZNsDvCN": "JUP",
    "DezXAZ8z7PnrnRJjz3wXBoRgixCa6xjnB7bBpESmr": "BONK",
    "HZ1JovNiVvGrGNiiYvEozEVgZ58xaU3RKwX8eACQBCt3": "PYTH",
    "2b1kV6DkPAnxd5ixfnxCpjxmKwqjjaYmCZfHsFu24GXo": "WIF",
    "6p6xgHyF7AeE6TZkSmFsko444wqoP15icUSqi2jfGiPN": "WEN",
}


def token_name(mint):
    """Return a friendly symbol for a known mint, else the mint address."""
    return TOKEN_NAMES.get(mint, mint)


def parse_token_balances(token_accounts):
    """Extract mint + amount from jsonParsed getTokenAccountsByOwner output."""
    balances = []
    for ta in token_accounts:
        info = ta.get("account", {}).get("data", {}).get("parsed", {}).get("info", {})
        mint = info.get("mint")
        token_amount = info.get("tokenAmount") or {}
        ui_amount = token_amount.get("uiAmountString")
        if mint and ui_amount is not None:
            try:
                if float(ui_amount) <= 0:
                    continue
            except (TypeError, ValueError):
                pass
            balances.append({
                "mint": mint,
                "amount": ui_amount,
                "decimals": token_amount.get("decimals"),
            })
    return balances
