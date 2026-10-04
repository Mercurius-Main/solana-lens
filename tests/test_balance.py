# -*- coding: utf-8 -*-
import unittest

from solana_lens.balance import lamports_to_sol, format_sol


class TestBalance(unittest.TestCase):
    def test_lamports_to_sol(self):
        self.assertEqual(lamports_to_sol(1_000_000_000), 1.0)
        self.assertEqual(lamports_to_sol(500_000_000), 0.5)

    def test_format_sol_trims_trailing_zeros(self):
        self.assertEqual(format_sol(1_000_000_000), "1")
        self.assertEqual(format_sol(500_000_000), "0.5")
        self.assertEqual(format_sol(1_234_567_890), "1.23456789")

    def test_format_sol_zero(self):
        self.assertEqual(format_sol(0), "0")


if __name__ == "__main__":
    unittest.main()
