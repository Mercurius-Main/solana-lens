# -*- coding: utf-8 -*-
"""Minimal dependency-free Solana JSON-RPC client (stdlib only)."""
import json
import urllib.request

DEFAULT_RPC = "https://api.mainnet-beta.solana.com"
LAMPORTS_PER_SOL = 1_000_000_000


class SolanaRPCError(Exception):
    """Raised when the RPC node returns a JSON-RPC error."""


class SolanaRPC:
    """Thin, dependency-free wrapper around a Solana JSON-RPC endpoint."""

    def __init__(self, url=DEFAULT_RPC, timeout=30):
        self.url = url
        self.timeout = timeout

    def _call(self, method, params):
        payload = json.dumps({
            "jsonrpc": "2.0", "id": 1, "method": method, "params": params,
        }).encode("utf-8")
        req = urllib.request.Request(
            self.url, data=payload, headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=self.timeout) as resp:
            data = json.loads(resp.read().decode("utf-8"))
        if "error" in data:
            raise SolanaRPCError(data["error"])
        return data.get("result")

    def get_balance_lamports(self, address):
        result = self._call("getBalance", [address])
        return result["value"]

    def get_signatures(self, address, limit=10, before=None):
        opts = {"limit": limit}
        if before:
            opts["before"] = before
        return self._call("getSignaturesForAddress", [address, opts])

    def get_transaction(self, signature):
        return self._call("getTransaction", [signature, {"encoding": "jsonParsed", "maxSupportedTransactionVersion": 0}])

    def get_version(self):
        return self._call("getVersion", [])
