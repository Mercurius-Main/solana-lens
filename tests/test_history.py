# -*- coding: utf-8 -*-
import unittest

from solana_lens.history import format_timestamp, short_signature, history_rows, to_markdown


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


if __name__ == "__main__":
    unittest.main()
