# -*- coding: utf-8 -*-
import unittest

from solana_lens.history import format_timestamp, short_signature, history_rows, to_markdown, parse_transfers, parse_program_activity, program_name


class TestHistory(unittest.TestCase):
    def test_format_timestamp_unknown(self):
        self.assertEqual(format_timestamp(None), "unknown")

    def test_format_timestamp_utc(self):
        # 2024-01-01 00:00:00 UTC
        self.assertEqual(format_timestamp(1704067200), "2024-01-01 00:00:00")

    def test_short_signature(self):
        self.assertEqual(short_signature("abcdefghijklmnop", 8), "abcdefgh...")
        self.assertEqual(short_signature("abc", 8), "abc")

    def test_history_rows_maps_status(self):
        sigs = [
            {"signature": "sig1", "blockTime": 1704067200, "err": None, "memo": "transfer"},
            {"signature": "sig2", "blockTime": None, "err": {"InstructionError": []}, "memo": ""},
        ]
        rows = history_rows(sigs)
        self.assertEqual(rows[0]["status"], "success")
        self.assertEqual(rows[1]["status"], "error")
        self.assertEqual(rows[0]["memo"], "transfer")

    def test_to_markdown_renders_table(self):
        rows = [{"signature": "abcdefghijklmnop", "block_time": 1704067200,
                 "status": "success", "memo": "hello"}]
        md = to_markdown(rows)
        self.assertIn("| Signature |", md)
        self.assertIn("abcdefgh...", md)
        self.assertIn("2024-01-01 00:00:00", md)
        self.assertIn("success", md)

    def test_to_markdown_escapes_pipe_in_memo(self):
        rows = [{"signature": "abc", "block_time": None, "status": "success", "memo": "a|b"}]
        md = to_markdown(rows)
        self.assertIn("a\\|b", md)

    def test_parse_transfers_sol_and_spl(self):
        tx = {"transaction": {"message": {"instructions": [
            {"parsed": {"type": "transfer", "info": {
                "source": "SrcAddr", "destination": "DstAddr", "lamports": 500_000_000}}},
            {"parsed": {"type": "transferChecked", "info": {
                "source": "SrcAddr", "destination": "DstAddr",
                "tokenAmount": {"uiAmountString": "12.5"},
                "mint": "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v"}}},
            {"parsed": {"type": "advanceNonce", "info": {}}},
        ]}}}
        transfers = parse_transfers(tx)
        self.assertEqual(len(transfers), 2)
        self.assertEqual(transfers[0]["kind"], "SOL")
        self.assertEqual(transfers[0]["amount"], 0.5)
        self.assertEqual(transfers[1]["kind"], "SPL")
        self.assertEqual(transfers[1]["amount"], "12.5")
        self.assertEqual(transfers[1]["token"], "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v")

    def test_parse_transfers_ignores_non_transfer(self):
        tx = {"transaction": {"message": {"instructions": [
            {"parsed": {"type": "setAuthority", "info": {}}},
        ]}}}
        self.assertEqual(parse_transfers(tx), [])

    def test_program_name_known_and_unknown(self):
        self.assertEqual(program_name("11111111111111111111111111111111"), "System (SOL transfer)")
        unknown = "UnknownProgramId123456789"
        self.assertEqual(program_name(unknown), unknown)

    def test_parse_program_activity_counts_and_dedupes(self):
        txs = [
            {"transaction": {"message": {"instructions": [
                {"programId": "11111111111111111111111111111111"},
                {"programId": "11111111111111111111111111111111"},  # dup in same tx
                {"programId": "675kPX9MHTjS2zt1qfr1NYHuzeLXfQM9H24wFSUt1Mp8"},
            ]}}},
            {"transaction": {"message": {"instructions": [
                {"programId": "11111111111111111111111111111111"},
            ]}}},
            {"transaction": {"message": {"instructions": []}}},
        ]
        activity = parse_program_activity(txs)
        self.assertEqual(activity[0], ("11111111111111111111111111111111", 2))
        self.assertEqual(activity[1], ("675kPX9MHTjS2zt1qfr1NYHuzeLXfQM9H24wFSUt1Mp8", 1))


if __name__ == "__main__":
    unittest.main()
