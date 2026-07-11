"""Unit tests — accounts/service.py and auth/service.py (no real DB)."""

from __future__ import annotations

import os
import sys
import unittest
from unittest.mock import MagicMock, patch

# Make BACKEND importable
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))


# ---------------------------------------------------------------------------
# Auth service — verify_credentials()
# ---------------------------------------------------------------------------

class TestVerifyCredentials(unittest.TestCase):
    """Tests for auth.service.verify_credentials — no real database calls."""

    def _make_customer(self, hashed_pw: str) -> MagicMock:
        customer = MagicMock()
        customer.__getitem__ = lambda self, key: hashed_pw if key == "password" else None
        return customer

    @patch("auth.service.find_by_username")
    @patch("auth.service.check_password_hash")
    def test_valid_credentials_returns_customer(self, mock_check, mock_find):
        mock_customer = MagicMock()
        mock_find.return_value = mock_customer
        mock_check.return_value = True

        from auth.service import verify_credentials
        result = verify_credentials("john", "password123")

        self.assertIs(result, mock_customer)
        mock_find.assert_called_once_with("john")

    @patch("auth.service.find_by_username")
    @patch("auth.service.check_password_hash")
    def test_wrong_password_returns_none(self, mock_check, mock_find):
        mock_find.return_value = MagicMock()
        mock_check.return_value = False

        from auth.service import verify_credentials
        result = verify_credentials("john", "wrongpass")

        self.assertIsNone(result)

    @patch("auth.service.find_by_username")
    def test_unknown_username_returns_none(self, mock_find):
        mock_find.return_value = None

        from auth.service import verify_credentials
        result = verify_credentials("nobody", "anything")

        self.assertIsNone(result)


# ---------------------------------------------------------------------------
# Accounts service — deposit()
# ---------------------------------------------------------------------------

class TestDeposit(unittest.TestCase):
    """Tests for accounts.service.deposit — model layer is mocked."""

    def setUp(self):
        self.patches = {
            "get_balance": patch("accounts.service.get_balance"),
            "update_balance": patch("accounts.service.update_balance"),
            "record_transaction": patch("accounts.service.record_transaction"),
        }
        self.mocks = {k: p.start() for k, p in self.patches.items()}
        self.mocks["get_balance"].return_value = 500.0

    def tearDown(self):
        for p in self.patches.values():
            p.stop()

    def test_positive_amount_succeeds(self):
        from accounts.service import deposit
        success, msg = deposit(1, "100.00")
        self.assertTrue(success)
        self.mocks["update_balance"].assert_called_once_with(1, 600.0)
        self.mocks["record_transaction"].assert_called_once_with(1, "deposit", 100.0)

    def test_zero_amount_fails(self):
        from accounts.service import deposit
        success, msg = deposit(1, "0")
        self.assertFalse(success)
        self.assertIn("greater than zero", msg)

    def test_negative_amount_fails(self):
        from accounts.service import deposit
        success, msg = deposit(1, "-50")
        self.assertFalse(success)

    def test_non_numeric_fails(self):
        from accounts.service import deposit
        success, msg = deposit(1, "abc")
        self.assertFalse(success)
        self.assertIn("valid number", msg)

    def test_empty_amount_fails(self):
        from accounts.service import deposit
        success, msg = deposit(1, "  ")
        self.assertFalse(success)
        self.assertIn("Please enter", msg)


# ---------------------------------------------------------------------------
# Accounts service — withdraw()
# ---------------------------------------------------------------------------

class TestWithdraw(unittest.TestCase):
    """Tests for accounts.service.withdraw — model layer is mocked."""

    def setUp(self):
        self.patches = {
            "get_balance": patch("accounts.service.get_balance"),
            "update_balance": patch("accounts.service.update_balance"),
            "record_transaction": patch("accounts.service.record_transaction"),
        }
        self.mocks = {k: p.start() for k, p in self.patches.items()}
        self.mocks["get_balance"].return_value = 500.0

    def tearDown(self):
        for p in self.patches.values():
            p.stop()

    def test_valid_withdrawal_below_balance_succeeds(self):
        from accounts.service import withdraw
        success, msg = withdraw(1, "200.00")
        self.assertTrue(success)
        self.mocks["update_balance"].assert_called_once_with(1, 300.0)

    def test_withdrawal_exactly_equal_to_balance_succeeds(self):
        from accounts.service import withdraw
        success, msg = withdraw(1, "500.00")
        self.assertTrue(success)
        self.mocks["update_balance"].assert_called_once_with(1, 0.0)

    def test_withdrawal_above_balance_fails(self):
        from accounts.service import withdraw
        success, msg = withdraw(1, "600.00")
        self.assertFalse(success)
        self.assertIn("Insufficient", msg)
        self.assertIn("500.00", msg)

    def test_zero_amount_fails(self):
        from accounts.service import withdraw
        success, msg = withdraw(1, "0")
        self.assertFalse(success)

    def test_negative_amount_fails(self):
        from accounts.service import withdraw
        success, msg = withdraw(1, "-10")
        self.assertFalse(success)

    def test_non_numeric_fails(self):
        from accounts.service import withdraw
        success, msg = withdraw(1, "xyz")
        self.assertFalse(success)


if __name__ == "__main__":
    unittest.main()
