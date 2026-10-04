# -*- coding: utf-8 -*-
import json
import unittest
from unittest import mock

from solana_lens.rpc import SolanaRPC, SolanaRPCError, LAMPORTS_PER_SOL


class _FakeResponse:
    """Minimal file-like object supporting the context-manager protocol."""

    def __init__(self, body):
        self._body = body

    def read(self):
        return self._body

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False


class TestRPC(unittest.TestCase):
    def test_get_balance_lamports(self):
        rpc = SolanaRPC("https://example.test")
        with mock.patch("urllib.request.urlopen") as uo:
            uo.return_value = _FakeResponse(json.dumps(
                {"jsonrpc": "2.0", "id": 1, "result": {"context": {"slot": 1}, "value": 12345}}).encode())
            result = rpc.get_balance_lamports("Addr")
        self.assertEqual(result, 12345)

    def test_rpc_error_raises(self):
        rpc = SolanaRPC("https://example.test")
        with mock.patch("urllib.request.urlopen") as uo:
            uo.return_value = _FakeResponse(json.dumps(
                {"jsonrpc": "2.0", "id": 1, "error": {"code": -32602, "message": "invalid"}}).encode())
            with self.assertRaises(SolanaRPCError):
                rpc.get_balance_lamports("Addr")

    def test_get_signatures_passes_limit(self):
        rpc = SolanaRPC("https://example.test")
        captured = {}
        with mock.patch("urllib.request.urlopen") as uo:
            def fake(req, timeout):
                captured["data"] = json.loads(req.data.decode())
                return _FakeResponse(json.dumps({"jsonrpc": "2.0", "id": 1, "result": []}).encode())
            uo.side_effect = fake
            rpc.get_signatures("Addr", limit=5)
        self.assertEqual(captured["data"]["params"], ["Addr", {"limit": 5}])

    def test_lamports_constant(self):
        self.assertEqual(LAMPORTS_PER_SOL, 1_000_000_000)


if __name__ == "__main__":
    unittest.main()
