#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""solana-lens command-line interface."""
import argparse
import sys

from .rpc import SolanaRPC, DEFAULT_RPC
from .balance import format_sol, parse_token_balances
from .history import history_rows, to_markdown

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
            print(f"  {t['amount']} (mint {t['mint']})")
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

    return p


def main(argv=None):
    parser = build_parser()
    args = parser.parse_args(argv)
    args.func(args)
    return 0


if __name__ == "__main__":
    sys.exit(main())
