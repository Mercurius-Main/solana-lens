#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""solana-lens command-line interface."""
import argparse
import sys

from .rpc import SolanaRPC, DEFAULT_RPC
from .balance import format_sol, parse_token_balances, token_name
from .history import history_rows, to_markdown, parse_transfers

DONATE_ADDRESS = "HXq1DKLWi6QszNRK8BCLRVBaPK92QmcXSrJJ44ZfatCZ"


def cmd_balance(args):
    rpc = SolanaRPC(args.rpc)
    lamports = rpc.get_balance_lamports(args.address)
    print(f"Address: {args.address}")
    print(f"SOL balance: {format_sol(lamports)} SOL")
    token_accounts = rpc.get_token_accounts(args.address)
    tokens = parse_token_balances(token_accounts)
    if tokens:
        print("SPL tokens:")
        for t in tokens:
            print(f"  {t['amount']} {token_name(t['mint'])}")
    else:
        print("SPL tokens: none")


def cmd_history(args):
    rpc = SolanaRPC(args.rpc)
    sigs = rpc.get_signatures(args.address, limit=args.limit)
    rows = history_rows(sigs)
    if not rows:
        print("No transaction history found for this address.")
        return
    print(to_markdown(rows))


def cmd_donate(args):
    print("solana-lens is free and open source.")
    print(f"Support development by sending SOL/SPL USDC to:\n  {DONATE_ADDRESS}")


def cmd_transaction(args):
    rpc = SolanaRPC(args.rpc)
    tx = rpc.get_transaction(args.signature)
    if tx is None:
        print("Transaction not found.")
        return
    transfers = parse_transfers(tx)
    if not transfers:
        print("No SOL/SPL transfers found in this transaction.")
        return
    for t in transfers:
        src = (t["source"] or "")[:10]
        dst = (t["destination"] or "")[:10]
        if t["kind"] == "SOL":
            print(f"  {src} -> {dst}  {t['amount']} SOL")
        else:
            print(f"  {src} -> {dst}  {t['amount']} {token_name(t['token'])}")


def build_parser():
    p = argparse.ArgumentParser(prog="solana-lens", description="Tiny Solana chain-data CLI.")
    p.add_argument("--rpc", default=DEFAULT_RPC, help="Solana JSON-RPC endpoint")
    sub = p.add_subparsers(dest="command", required=True)

    b = sub.add_parser("balance", help="Query a wallet's SOL balance")
    b.add_argument("address")
    b.set_defaults(func=cmd_balance)

    h = sub.add_parser("history", help="List recent transactions as markdown")
    h.add_argument("address")
    h.add_argument("-n", "--limit", type=int, default=10)
    h.set_defaults(func=cmd_history)

    d = sub.add_parser("donate", help="Show the donation address")
    d.set_defaults(func=cmd_donate)

    t = sub.add_parser("transaction", help="Show transfers inside a transaction")
    t.add_argument("signature")
    t.set_defaults(func=cmd_transaction)

    return p


def main(argv=None):
    parser = build_parser()
    args = parser.parse_args(argv)
    args.func(args)
    return 0


if __name__ == "__main__":
    sys.exit(main())
