# Dynamic Pricing System



## 1. System Architecture & Design Choices

### 1.1 Frontend (Client Interface)

- Framework: React.js  
- Deployment: Built into static files (index.html, JS, CSS) and served via Flask  
- Functionality:
  - Visualizes product information and predicted prices  
  - Allows users to trigger price adjustment requests via API calls  

### 1.2 Backend (API Server)

- Framework: Flask (Python), with flask_cors for cross-origin support  
- Responsibilities:
  - Serve static frontend assets  
  - Expose RESTful API endpoints (/products, /adjust-prices)  
  - Integrate machine learning prediction and business rule post-processing  

### 1.3 Machine Learning Pipeline

- Model: RandomForestRegressor (via scikit-learn pipeline)  
- Input Features: inventory level, product rating, average sales  
- Output: Raw predicted price  
- Post-processing business rules:
  - Apply surge pricing if inventory is critically low  
  - Apply discounting if undercut by competitors  
  - Enforce bounds: price ≥ cost × 1.1 and ≤ base price + 50  

### 1.4 Data Sources

- product_catalog.csv: Product attributes (e.g., rating, cost, inventory)  
- sales_history.csv: Historical sales data for demand estimation  
- External competitor prices: Fetched via mock API, fallback to local data  

### 1.5 Design Rationale

- Separation of concerns: Frontend and backend are decoupled and integrated via REST APIs  
- Extensibility: ML model can be retrained or replaced without frontend change  
- Fallback resilience: Uses fallback data if external API fails  
- Portability: Docker-compatible setup for consistent deployment  

## 2. Setup & Run Instructions

### Requirements

- Python 3.9+  
- Node.js & npm  
- Docker (optional, but recommended)  

### Option 1: Local Setup (for development)

```bash
# 1. Clone the repository
git clone https://github.com/Istsavr/dynamic-pricing.git
cd dynamic-pricing

# 2. Backend setup
pip install -r requirements.txt

# 3. Build frontend
cd pricing-dashboard
npm install
npm run build

# 4. Move frontend build to backend
cp -r build/* ../static/
cd ..

# 5. Start Flask server
python app.py
````

Visit: [http://localhost:5000](http://localhost:5000)

### Option 2: Run with Docker (recommended)

```bash
# 1. Clone the repository
git clone https://github.com/Istsavr/dynamic-pricing.git
cd dynamic-pricing

# 2. Build Docker image
docker build -t dynamic-pricing-app .

# 3. Run the container
docker run -p 5000:5000 dynamic-pricing-app
```

Visit: [http://localhost:5000](http://localhost:5000)

## 3. API Documentation

### GET /products

Returns all product information.

Example response:

```json
[
  {
    "product_id": "P001",
    "name": "Product A",
    "price": 120,
    "inventory": 25,
    "rating": 4.3
  }
]
```

### GET /adjust-prices

Returns dynamically adjusted prices based on model prediction and business logic.

Logic:

1. Load product and sales data
2. Estimate demand (average units sold)
3. Fetch competitor prices
4. Apply trained Random Forest model
5. Apply business rules for adjustment

Example response:

```json
[
  {
    "product_id": "P001",
    "original_price": 120,
    "predicted_price": 128.53,
    "adjusted_price": 134.00
  }
]
```

## 4. Machine Learning Pipeline Details

* Model: RandomForestRegressor (from scikit-learn)
* Trained model stored at: models/pipeline.pkl
* Preprocessing: StandardScaler
* Input features:

  * inventory
  * rating
  * avg\_units\_sold
* Post-processing business rules:

  * Adds markup if inventory is low
  * Adjusts price down if competitor price is much lower
  * Enforces minimum price: cost × 1.1
  * Caps maximum price: base price + 50

