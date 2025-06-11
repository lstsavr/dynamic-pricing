from config import (
    MIN_MARGIN,
    MAX_INCREASE,
    LOW_INVENTORY_THRESHOLD,
    MAX_STOCK_ADJUSTMENT,
    MAX_DISCOUNT_IF_UNDERCUT
)
import joblib
import pandas as pd
import os

# 导入模型
MODEL_PATH = os.path.join(os.path.dirname(__file__), "models", "pricing_pipeline.pkl")
model_pipeline = joblib.load(MODEL_PATH)


def apply_business_rules(base_price: float, pred_price: float,
                         competitor_price: float, inventory: int) -> float:
    from config import MAX_DISCOUNT_IF_UNDERCUT

    print(f"[DEBUG] >>> apply_business_rules() 被调用: base={base_price}, pred={pred_price}, comp={competitor_price}, inv={inventory}")

    price = pred_price

    # 初始化边界
    lower_bound = base_price * (1 + MIN_MARGIN)
    upper_bound = base_price * (1 + MAX_INCREASE)

    # 被压价限制最高降价
    if competitor_price < base_price * (1 - MAX_DISCOUNT_IF_UNDERCUT):
        competitor_limit = base_price * (1 - MAX_DISCOUNT_IF_UNDERCUT)
        upper_bound = min(upper_bound, competitor_limit)

    # 库存紧张限制最高涨价
    if inventory < LOW_INVENTORY_THRESHOLD:
        stock_limit = base_price * (1 + MAX_STOCK_ADJUSTMENT)
        upper_bound = min(upper_bound, stock_limit)

    price = max(lower_bound, min(price, upper_bound))
    return round(price, 2)



def predict_and_adjust(df_products: pd.DataFrame, df_competitor: pd.DataFrame) -> pd.DataFrame:
    df = df_products.copy()

    # 合并竞争者价格
    df = df.merge(df_competitor, on='product_id', how='left')
    df['competitor_price'] = df['competitor_price'].fillna(df['base_price'])

    # 模型预测
    df['predicted_price'] = model_pipeline.predict(df)

    # 我要崩溃了
    df['adjusted_price'] = df.apply(
        lambda row: apply_business_rules(
            base_price=row['base_price'],
            pred_price=row['predicted_price'],
            competitor_price=row['competitor_price'],
            inventory=row['inventory']
        ),
        axis=1
    )

    return df
