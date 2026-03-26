import unittest
from datetime import datetime
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import only the Business class (no GUI needed)
from main import Business


class TestBusiness(unittest.TestCase):

    def setUp(self):
        self.business = Business("Test Cafe", 5000.0, "Monthly", "$")

    def test_business_creation(self):
        self.assertEqual(self.business.name, "Test Cafe")
        self.assertEqual(self.business.budget, 5000.0)
        self.assertEqual(self.business.period, "Monthly")
        self.assertEqual(self.business.currency, "$")

    def test_add_income(self):
        self.business.add_income(1000.0)
        self.assertEqual(len(self.business.incomes), 1)
        self.assertEqual(self.business.total_income(), 1000.0)

    def test_add_multiple_incomes(self):
        self.business.add_income(500.0)
        self.business.add_income(750.0)
        self.assertEqual(self.business.total_income(), 1250.0)

    def test_add_expense(self):
        self.business.add_expense(200.0, "Rent", "BILL-001")
        self.assertEqual(len(self.business.expenses), 1)
        self.assertEqual(self.business.total_expense(), 200.0)

    def test_net_profit_positive(self):
        self.business.add_income(3000.0)
        self.business.add_expense(1000.0, "Rent")
        self.assertEqual(self.business.net_profit(), 2000.0)

    def test_net_profit_negative(self):
        self.business.add_income(500.0)
        self.business.add_expense(1000.0, "Rent")
        self.assertEqual(self.business.net_profit(), -500.0)

    def test_alert_budget_exceeded(self):
        self.business.add_expense(6000.0, "Rent")
        alerts = self.business.alerts()
        self.assertIn("⚠ Budget exceeded!", alerts)

    def test_alert_running_at_loss(self):
        self.business.add_income(100.0)
        self.business.add_expense(500.0, "Salaries")
        alerts = self.business.alerts()
        self.assertIn("⚠ Business running at loss!", alerts)

    def test_no_alerts_when_healthy(self):
        self.business.add_income(5000.0)
        self.business.add_expense(1000.0, "Supplies")
        alerts = self.business.alerts()
        self.assertEqual(len(alerts), 0)

    def test_expense_by_category(self):
        self.business.add_expense(300.0, "Rent")
        self.business.add_expense(500.0, "Salaries")
        by_cat = self.business.expense_by_category()
        self.assertEqual(by_cat[0], 300.0)   # Rent
        self.assertEqual(by_cat[1], 500.0)   # Salaries

    def test_to_dict_and_from_dict(self):
        self.business.add_income(1000.0, datetime(2024, 1, 15))
        self.business.add_expense(300.0, "Rent", "B001", datetime(2024, 1, 20))
        data = self.business.to_dict()
        restored = Business.from_dict(data)
        self.assertEqual(restored.name, self.business.name)
        self.assertEqual(restored.total_income(), 1000.0)
        self.assertEqual(restored.total_expense(), 300.0)

    def test_empty_business_totals(self):
        self.assertEqual(self.business.total_income(), 0.0)
        self.assertEqual(self.business.total_expense(), 0.0)
        self.assertEqual(self.business.net_profit(), 0.0)

    def test_income_with_custom_date(self):
        custom_date = datetime(2024, 6, 1, 10, 30, 0)
        self.business.add_income(200.0, custom_date)
        self.assertEqual(self.business.incomes[0]["date"], custom_date)

    def test_categories_list(self):
        expected = ["Rent", "Salaries", "Supplies", "Marketing",
                    "Utilities", "Transport", "Maintenance", "Other"]
        self.assertEqual(self.business.categories, expected)


if __name__ == "__main__":
    unittest.main()
