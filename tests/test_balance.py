# -*- coding: utf-8 -*-
import unittest

from solana_lens.balance import lamports_to_sol, format_sol, parse_token_balances


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

    def test_parse_token_balances_extracts_mint_and_amount(self):
        accounts = [{
            "account": {"data": {"parsed": {"info": {
                "mint": "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v",
                "tokenAmount": {"uiAmountString": "12.5", "decimals": 6, "amount": "12500000"},
            }}}},
        }]
        result = parse_token_balances(accounts)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["mint"], "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v")
        self.assertEqual(result[0]["amount"], "12.5")

    def test_parse_token_balances_skips_zero_and_missing(self):
        accounts = [
            {"account": {"data": {"parsed": {"info": {
                "mint": "MintA", "tokenAmount": {"uiAmountString": "0", "decimals": 6},
            }}}}},
            {"account": {"data": {"parsed": {"info": {}}}}},
        ]
        self.assertEqual(parse_token_balances(accounts), [])


if __name__ == "__main__":
    unittest.main()
