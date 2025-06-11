import unittest
import requests

BASE_URL = 'http://127.0.0.1:5000'


class TestBackendAPI(unittest.TestCase):

    def test_products_endpoint(self):
        resp = requests.get(f'{BASE_URL}/products')
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertTrue(isinstance(data, list))
        self.assertTrue('product_id' in data[0])

    def test_adjust_prices_endpoint(self):
        resp = requests.get(f'{BASE_URL}/adjust-prices')
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertTrue('adjusted_price' in data[0])
        self.assertTrue('predicted_price' in data[0])

        for item in data:
            base_price = item['base_price']
            adjusted_price = item['adjusted_price']
            # test proce不低于 base_price * 1.10（MIN_MARGIN）
            self.assertTrue(adjusted_price >= base_price * 1.10 - 1e-6)
            # test price不高于 base_price * 1.50（MAX_INCREASE）
            self.assertLessEqual(adjusted_price, base_price * 1.50)


if __name__ == '__main__':
    unittest.main()
