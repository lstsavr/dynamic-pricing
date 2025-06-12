1. System Architecture & Design Choices

1. Frontend (Client Interface)
	•	Framework:react JS
	•	Deployment: Built into static files (index.html, JS, CSS) and served via Flask.
	•	Functionality:
	•	Visualizes product information and predicted prices.
	•	Allows users to trigger price adjustment requests through API calls.

2. Backend (API Server)
	•	Framework: Flask (Python) with flask_cors for cross-origin support.
	•	Key Responsibilities:
	•	Serve static frontend assets.
	•	Expose RESTful API endpoints (/products, /adjust-prices).
	•	Integrate machine learning prediction and post-processing logic.

3. Machine Learning Pipeline
	•	Model: Random Forest Regressor (via scikit-learn pipeline)
	•	Input Features: Inventory level, product rating, average sales.
	•	Output: Raw predicted price.
	•	Enhancement Logic (based on business rules):
	•	Apply surge pricing if inventory is critically low.
	•	Apply competitive discounting if undercut by a competitor.
	•	Enforce profit margin bounds (price ≥ cost × 1.1 and ≤ base price + 50).

4. Data Sources
	•	product_catalog.csv: Product attributes (e.g., rating, cost, inventory).
	•	sales_history.csv: Historical sales data used for demand estimation.
	•	External competitor prices (via mock API or fallback data).

5. Design Rationale
	•	Separation of concerns: Frontend and backend are decoupled but integrated via REST APIs.
	•	Extensibility: ML model can be retrained or swapped without changing frontend.
	•	Fallback resilience: Competitor prices are retrieved via a mock API, with a fallback to local data if the request fails.
	•	Portability: Docker-compatible setup ensures consistent deployment across environments.



2. Setup & Run Instructions
 Requirements
	•	Python 3.9+
	•	Node.js & npm
	•	Docker (optional but recommended)

Local Setup

Step 1: Clone the repo
git clone https://github.com/Istsavr/dynamic-pricing.git
cd dynamic-pricing

Step 2: Backend setup
pip install -r requirements.txt

Step 3: Frontend build
cd pricing-dashboard
npm install
npm run build

Step 4: Move frontend build to backend
This creates: static/index.html + static/statics/js/...
cp -r build/* ../static/

Step 5: Run Flask
cd ..
python app.py

Visit: http://localhost:5000

Docker Run

docker build -t dynamic-pricing-app .
docker run -p 5000:5000 dynamic-pricing-app


⸻

3.API Documentation

GET /products
	•	Description: Returns all product info.
	•	Response Example:

[
  {
    "product_id": "P001",
    "name": "Product A",
    "price": 120,
    "inventory": 25,
    "rating": 4.3
  }
]


⸻

GET /adjust-prices
	•	Description: Returns dynamically adjusted prices.
	•	Logic:
	1.	Loads product and sales data
	2.	Aggregates average units sold
	3.	Fetches competitor prices
	4.	Applies Random Forest model for prediction
	5.	Applies business rules for final pricing
	•	Response Example:

[
  {
    "product_id": "P001",
    "original_price": 120,
    "predicted_price": 128.53,
    "adjusted_price": 134.00
  }
]




4. ML Pipeline
	•	Input Features:
	•	inventory
	•	rating
	•	avg_units_sold
	•	Model:
	•	RandomForestRegressor from sklearn
	•	Trained using pipeline.pkl stored in models/
	•	Preprocessing handled via StandardScaler
•	Post-processing (Rules):
	•	Adds markup if inventory is low
	•	Adjusts downwards if competitor price is much lower
	•	Ensures price is not below cost_price × 1.1
