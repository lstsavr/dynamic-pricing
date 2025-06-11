import pandas as pd
import matplotlib.pyplot as plt
import os
#数据也太少了，有数据集就好了
df = pd.DataFrame([
    {"product_id": "P001", "base_price": 100.0, "predicted_price": 121.84, "adjusted_price": 121.84, "competitor_price": 90.0},
    {"product_id": "P002", "base_price": 200.0, "predicted_price": 158.76, "adjusted_price": 220.0, "competitor_price": 195.0},
    {"product_id": "P003", "base_price": 50.0,  "predicted_price": 84.92,  "adjusted_price": 65.0,   "competitor_price": 48.0}
])

# 画图咯！
plt.figure(figsize=(10, 6))
x = df["product_id"]
plt.plot(x, df["base_price"], label="Base Price", marker='o')
plt.plot(x, df["predicted_price"], label="Predicted Price", marker='o')
plt.plot(x, df["adjusted_price"], label="Adjusted Price", marker='o')
plt.plot(x, df["competitor_price"], label="Competitor Price", marker='o')
plt.xlabel("Product ID")
plt.ylabel("Price")
plt.title("Dynamic Pricing Comparison")
plt.legend()
plt.grid(True)

# 保存图像到 statics/
static_dir = os.path.join(os.path.dirname(__file__), "statics")
os.makedirs(static_dir, exist_ok=True)
output_path = os.path.join(static_dir, "price_comparison_chart.png")
plt.savefig(output_path)
print(f"✅ 图表已保存到：{output_path}")
