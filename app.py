from flask import Flask, jsonify, send_from_directory
from flask_cors import CORS
import os
import pandas as pd
import traceback
import json
import requests

from config import PRODUCT_CATALOG, SALES_HISTORY
from pricing_engine import predict_and_adjust

# 显式指定 statics 文件夹路径
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
app = Flask(__name__, static_folder=os.path.join(BASE_DIR, "static"))
CORS(app)

# fallback 竞争者价格
FALLBACK_COMPETITOR_DATA = [
    {"product_id": "P001", "competitor_price": 90.0},
    {"product_id": "P002", "competitor_price": 195.0},
    {"product_id": "P003", "competitor_price": 48.0}
]

# mock API
def get_competitor_prices():
    url = "https://mock-api.com/competitor-prices"
    try:
        resp = requests.get(url, timeout=3)
        resp.raise_for_status()
        print("成功从 mock API 获取竞争者价格")
        return resp.json()
    except Exception as e:
        print(f"获取失败，使用 fallback：{e}")
        return FALLBACK_COMPETITOR_DATA

# 获取产品信息
@app.route('/products', methods=['GET'])
def get_products():
    try:
        df = pd.read_csv(PRODUCT_CATALOG)
        return jsonify(df.to_dict(orient='records'))
    except Exception as e:
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

# 获取调整后价格
@app.route('/adjust-prices', methods=['GET'])
def adjust_prices():
    try:
        df_catalog = pd.read_csv(PRODUCT_CATALOG)
        df_sales = pd.read_csv(SALES_HISTORY)

        df_sales_agg = (
            df_sales
            .groupby('product_id')['units_sold']
            .mean()
            .reset_index(name='avg_units_sold')
        )

        df_products = (
            df_catalog
            .merge(df_sales_agg, on='product_id', how='left')
            .fillna({'avg_units_sold': 0})
        )

        comp_data = get_competitor_prices()
        df_comp = pd.DataFrame(comp_data)[["product_id", "competitor_price"]]
        df_out = predict_and_adjust(df_products, df_comp)

        return jsonify(df_out.to_dict(orient='records'))

    except Exception as e:
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

# 统一前端 React 页面路由
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve_react(path):
    if path != "" and os.path.exists(os.path.join(app.static_folder, path)):
        return send_from_directory(app.static_folder, path)
    else:
        return send_from_directory(app.static_folder, 'index.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)


