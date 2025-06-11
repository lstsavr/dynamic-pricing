import unittest
import pandas as pd
from pricing_engine import apply_business_rules, predict_and_adjust
from config import (
    MIN_MARGIN,
    MAX_INCREASE,
    LOW_INVENTORY_THRESHOLD,
    MAX_STOCK_ADJUSTMENT,
    MAX_DISCOUNT_IF_UNDERCUT)


class TestPricingEngine(unittest.TestCase):

    def test_low_inventory_increase(self):
        price = apply_business_rules(
            base_price=100.0,
            pred_price=140.0,
            competitor_price=120.0,
            inventory=2
        )
        self.assertEqual(price, 130.0)  # base * (1 + MAX_STOCK_ADJUSTMENT)

    def test_competitor_undercut_discount(self):
        base_price = 200.0
        pred_price = 180.0
        competitor_price = 100.0  # 远低于 base_price
        inventory = 50

        price = apply_business_rules(
            base_price=base_price,
            pred_price=pred_price,
            competitor_price=competitor_price,
            inventory=inventory
        )

        lower_bound = base_price * (1 + MIN_MARGIN)
        upper_bound1 = base_price * (1 + MAX_INCREASE)
        upper_bound2 = base_price * (1 - MAX_DISCOUNT_IF_UNDERCUT)
        expected_upper_bound = min(upper_bound1, upper_bound2)

        if lower_bound > expected_upper_bound:
            self.assertAlmostEqual(price, lower_bound, delta=1e-6)
        else:
            self.assertLessEqual(price, expected_upper_bound)
            self.assertGreaterEqual(price, lower_bound)

    def test_price_bounds(self):
        price = apply_business_rules(
            base_price=100.0,
            pred_price=500.0,
            competitor_price=400.0,
            inventory=100
        )
        self.assertLessEqual(price, 150.0)  # MAX_INCREASE = 0.5
        self.assertGreaterEqual(price, 110.0)  # MIN_MARGIN = 0.1

    def test_predict_and_adjust_integration(self):
        df_products = pd.DataFrame([{
            "product_id": "P001",
            "base_price": 100.0,
            "inventory": 8,
            "sales_last_30_days": 20,
            "average_rating": 4.3,
            "avg_units_sold": 5,
            "category": "Electronics"
        }])

        df_competitor = pd.DataFrame([{
            "product_id": "P001",
            "competitor_price": 70.0
        }])

        df_out = predict_and_adjust(df_products, df_competitor)

        self.assertIn("predicted_price", df_out.columns)
        self.assertIn("adjusted_price", df_out.columns)
        self.assertGreaterEqual(df_out['adjusted_price'].iloc[0], 110.0)
        self.assertLessEqual(df_out['adjusted_price'].iloc[0], 150.0)

    def test_zero_inventory_handling(self):
        price = apply_business_rules(
            base_price=100.0,
            pred_price=120.0,
            competitor_price=100.0,
            inventory=0  # 极端低库存
        )
        self.assertLessEqual(price, 130.0)  # base * (1 + MAX_STOCK_ADJUSTMENT)

    def test_missing_competitor_price_fallback(self):
        df_products = pd.DataFrame([{
            "product_id": "P001",
            "base_price": 100.0,
            "inventory": 15,
            "sales_last_30_days": 30,
            "average_rating": 4.5,
            "avg_units_sold": 6,
            "category": "Electronics"
        }])

        df_competitor = pd.DataFrame(columns=["product_id", "competitor_price"])

        df_out = predict_and_adjust(df_products, df_competitor)
        self.assertIn("adjusted_price", df_out.columns)
        self.assertGreaterEqual(df_out['adjusted_price'].iloc[0], 110.0)

    def test_predicted_price_too_low(self):
        price = apply_business_rules(
            base_price=100.0,
            pred_price=50.0,  # 模型预测超低
            competitor_price=60.0,
            inventory=100
        )
        self.assertGreaterEqual(price, 110.0)  # base * (1 + MIN_MARGIN)


if __name__ == '__main__':
    unittest.main()
