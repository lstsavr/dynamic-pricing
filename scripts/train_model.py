import os
import logging

import pandas as pd
import joblib

from sklearn.compose import ColumnTransformer
from sklearn.dummy import DummyRegressor
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

from config import PRODUCT_CATALOG, SALES_HISTORY, MODEL_PATH, RESULTS_DIR

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

def load_and_preprocess():
    #加载，聚合，合并

    catalog = pd.read_csv(PRODUCT_CATALOG)
    sales   = pd.read_csv(SALES_HISTORY)

    # 把聚合平均销量和成交价作为预测目标
    sales_agg = (
        sales.groupby('product_id')
             .agg(
                 avg_units_sold=('units_sold', 'mean'),
                 avg_price      =('price',      'mean')
             )
             .reset_index()
    )

    # 合并特征数据与目标变量
    df = catalog.merge(sales_agg, on='product_id', how='inner')

    # 简单填充
    df['sales_last_30_days'] = df['sales_last_30_days'].fillna(0)
    df['inventory']          = df['inventory'].fillna(0)
    df['average_rating']     = df['average_rating'].fillna(df['average_rating'].mean())

    return df


def build_pipeline(numeric_features, categorical_features, model):
    """
    开始构建Pipeline
    """
    preprocessor = ColumnTransformer([
        ('num', StandardScaler(), numeric_features),
        ('cat', OneHotEncoder(handle_unknown='ignore'), categorical_features)
    ])

    pipeline = Pipeline([
        ('pre', preprocessor),
        ('model', model)
    ])
    return pipeline


def evaluate(name, y_true, y_pred):

    # RMSE、MAE、R²

    mse  = mean_squared_error(y_true, y_pred)
    rmse = mse ** 0.5
    mae  = mean_absolute_error(y_true, y_pred)
    r2   = r2_score(y_true, y_pred)
    logger.info(f"{name} → RMSE: {rmse:.3f}, MAE: {mae:.3f}, R²: {r2:.3f}")


def train_and_evaluate(df):

    #模型训练主函数

    # 特征与目标
    numeric_feats     = ['base_price', 'inventory', 'sales_last_30_days',
                         'average_rating', 'avg_units_sold']
    categorical_feats = ['category']
    label             = 'avg_price'  # 目标是预测商品平均成交价（业务目标：价格预测）

    X = df[numeric_feats + categorical_feats]
    y = df[label]

    # 拆分训练/测试集
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    n_samples = X_train.shape[0]
    logger.info(f"训练集样本数: {n_samples}")

    # fallback 小样本处理
    if n_samples < 2:
        logger.warning("样本量过少，使用 DummyRegressor(strategy='mean') 降级回归")
        model    = DummyRegressor(strategy='mean')
        pipeline = build_pipeline(numeric_feats, categorical_feats, model)
        pipeline.fit(X_train, y_train)
    else:
        # 使用交叉验证 + 网格搜索
        cv_folds = min(3, n_samples)
        logger.info(f"使用 {cv_folds} 折交叉验证进行超参数搜索")

        rf = RandomForestRegressor(random_state=42)
        param_grid = {
            'model__n_estimators' : [100, 200],
            'model__max_depth'    : [None, 10, 20],
            'model__max_features' : ['sqrt', 'log2']
        }
        pipeline = build_pipeline(numeric_feats, categorical_feats, rf)
        grid     = GridSearchCV(
            pipeline,
            param_grid,
            cv=cv_folds,
            scoring='neg_root_mean_squared_error',
            n_jobs=-1,
            verbose=1
        )
        grid.fit(X_train, y_train)
        pipeline = grid.best_estimator_
        logger.info(f"最佳参数: {grid.best_params_}")

    # 模型评估
    y_train_pred = pipeline.predict(X_train)
    y_test_pred  = pipeline.predict(X_test)
    evaluate("Train", y_train, y_train_pred)
    evaluate("Test",  y_test,  y_test_pred)

    # 输出特征重要性
    model_step = pipeline.named_steps['model']
    if hasattr(model_step, 'feature_importances_'):
        ohe           = pipeline.named_steps['pre'].named_transformers_['cat']
        cat_names     = list(ohe.get_feature_names_out(categorical_feats))
        feature_names = numeric_feats + cat_names

        fi = pd.Series(model_step.feature_importances_, index=feature_names)
        os.makedirs(RESULTS_DIR, exist_ok=True)
        fi.sort_values(ascending=False).to_csv(
            os.path.join(RESULTS_DIR, 'feature_importances.csv'),
            header=['importance']
        )
        logger.info(f"特征重要性已保存到 {RESULTS_DIR}/feature_importances.csv")

    return pipeline


def save_pipeline(pipeline):
    #把完整的 Pipeline 保存到模型文件里面去

    os.makedirs(os.path.dirname(MODEL_PATH), exist_ok=True)
    joblib.dump(pipeline, MODEL_PATH)
    logger.info(f"Pipeline 已保存到 {MODEL_PATH}")


def main():
    df       = load_and_preprocess()
    pipeline = train_and_evaluate(df)
    save_pipeline(pipeline)


if __name__ == '__main__':
    main()
