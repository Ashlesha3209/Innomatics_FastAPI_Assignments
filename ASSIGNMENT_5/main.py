from fastapi import FastAPI, Query, HTTPException
from typing import Optional

app = FastAPI()

# --- DATABASE / DATA ---
# Product data as per Day 6 Assignment
products = [
    {"id": 1, "name": "Wireless Mouse", "price": 499, "category": "Electronics"},
    {"id": 2, "name": "Notebook", "price": 99, "category": "Stationery"},
    {"id": 3, "name": "USB Hub", "price": 799, "category": "Electronics"},
    {"id": 4, "name": "Pen Set", "price": 49, "category": "Stationery"},
]

# Order data (populated via POST /orders)
orders = []

# --- PRODUCT ENDPOINTS (Q1, Q2, Q3) ---

@app.get("/products/search")
def search_products(keyword: str):
    # Case-insensitive search logic
    results = [p for p in products if keyword.lower() in p['name'].lower()]
    if not results:
        return {"message": f"No products found for: {keyword}"}
    return {"keyword": keyword, "total_found": len(results), "products": results}

@app.get("/products/sort")
def sort_products(sort_by: str = "price", order: str = "asc"):
    # Reject invalid sort fields
    if sort_by not in ["price", "name"]:
        return {"error": "sort_by must be 'price' or 'name'"}
    
    is_reverse = (order == "desc")
    sorted_data = sorted(products, key=lambda p: p[sort_by], reverse=is_reverse)
    return {"sort_by": sort_by, "order": order, "products": sorted_data}

@app.get("/products/page")
def paginate_products(page: int = 1, limit: int = 2):
    # Pagination formula: start = (page-1) * limit
    start = (page - 1) * limit
    end = start + limit
    paged_data = products[start:end]
    
    total_pages = -(-len(products) // limit) # Ceiling division
    return {
        "page": page,
        "limit": limit,
        "total_pages": total_pages,
        "products": paged_data
    }

# --- NEW ASSIGNMENT ENDPOINTS (Q4, Q5, Q6) ---

@app.get("/orders/search")
def search_orders(customer_name: str = Query(...)):
    # Q4: Search orders by customer name (case-insensitive)
    results = [
        o for o in orders 
        if customer_name.lower() in o['customer_name'].lower()
    ]
    if not results:
        return {"message": f"No orders found for: {customer_name}"}
    return {"customer_name": customer_name, "total_found": len(results), "orders": results}

@app.get("/products/sort-by-category")
def sort_by_category():
    # Q5: Sort by Category (A-Z) then Price (cheapest first)
    result = sorted(products, key=lambda p: (p['category'], p['price']))
    return {"products": result, "total": len(result)}

@app.get("/products/browse")
def browse_products(
    keyword: Optional[str] = Query(None),
    sort_by: str = Query("price"),
    order: str = Query("asc"),
    page: int = Query(1, ge=1),
    limit: int = Query(4, ge=1, le=20)
):
    # Q6: Search + Sort + Paginate combined
    # 1. Filter
    result = products
    if keyword:
        result = [p for p in result if keyword.lower() in p['name'].lower()]
    
    # 2. Sort
    if sort_by in ['price', 'name']:
        result = sorted(result, key=lambda p: p[sort_by], reverse=(order == "desc"))
    
    # 3. Paginate
    total = len(result)
    start = (page - 1) * limit
    paged_data = result[start : start + limit]
    
    return {
        "keyword": keyword,
        "sort_by": sort_by,
        "order": order,
        "page": page,
        "limit": limit,
        "total_found": total,
        "total_pages": -(-total // limit),
        "products": paged_data
    }

# --- POST ENDPOINT FOR TESTING ---
@app.post("/orders")
def create_order(customer_name: str, amount: float):
    new_order = {
        "order_id": len(orders) + 1,
        "customer_name": customer_name,
        "amount": amount
    }
    orders.append(new_order)
    return new_order

# --- GET BY ID (Requirement: Add new code ABOVE this) ---
@app.get("/products/{product_id}")
def get_product(product_id: int):
    for product in products:
        if product['id'] == product_id:
            return product
    raise HTTPException(status_code=404, detail="Product not found")