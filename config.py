import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

PRODUCT_CATALOG = os.path.join(BASE_DIR, 'data', 'product_catalog.csv')
SALES_HISTORY   = os.path.join(BASE_DIR, 'data', 'sales_history.csv')
COMPETITOR_PRICES = os.path.join(BASE_DIR, 'data', 'competitor_prices.json')

MODEL_PATH  = os.path.join(BASE_DIR, 'models', 'pricing_pipeline.pkl')
RESULTS_DIR = os.path.join(BASE_DIR, 'results')


# 最低利润规则
MIN_MARGIN = 0.10

# 最高加价规则
MAX_INCREASE = 0.50

# 库存临界点规则
LOW_INVENTORY_THRESHOLD = 10

# 库存紧张时规则
MAX_STOCK_ADJUSTMENT = 0.30

# 被竞争者压价时规则
MAX_DISCOUNT_IF_UNDERCUT = 0.20
