from fastapi import FastAPI, Query, Path
from pydantic import BaseModel, Field
from typing import List, Optional

app = FastAPI()

# --- MOCK DATA ---
products = [
    {"id": 1, "name": "Wireless Mouse", "price": 899, "category": "Electronics", "in_stock": True},
    {"id": 2, "name": "Notebook", "price": 149, "category": "Stationery", "in_stock": True},
    {"id": 3, "name": "Gel Pen", "price": 49, "category": "Stationery", "in_stock": True},
    {"id": 4, "name": "Gaming Headset", "price": 3499, "category": "Electronics", "in_stock": False},
    {"id": 5, "name": "Laptop Stand", "price": 1299, "category": "Electronics", "in_stock": True},
]

orders = [
    {"order_id": 101, "customer": "Ashlesha", "status": "pending", "amount": 1798}
]
feedback = []

# Q1: Filter Products by Minimum Price
@app.get("/products/filter")
def filter_products(
    category: Optional[str] = None, 
    max_price: Optional[int] = None,
    min_price: int = Query(None, description="Minimum price")
):
    result = products
    if category:
        result = [p for p in result if p["category"].lower() == category.lower()]
    if max_price:
        result = [p for p in result if p["price"] <= max_price]
    if min_price:
        result = [p for p in result if p["price"] >= min_price]
    return result

# Q2: Get Only Price of a Product
@app.get("/products/{product_id}/price")
def get_product_price(product_id: int = Path(..., gt=0)):
    for product in products:
        if product["id"] == product_id:
            return {"name": product["name"], "price": product["price"]}
    return {"error": "Product not found"}

# Q3: Customer Feedback
class CustomerFeedback(BaseModel):
    customer_name: str = Field(..., min_length=2, max_length=100)
    product_id: int = Field(..., gt=0)
    rating: int = Field(..., ge=1, le=5)
    comment: Optional[str] = Field(None, max_length=300)

@app.post("/feedback")
def submit_feedback(data: CustomerFeedback):
    feedback.append(data.dict())
    return {
        "message": "Feedback submitted successfully",
        "feedback": data.dict(),
        "total_feedback": len(feedback)
    }

# Q4: Product Summary Dashboard
@app.get("/products/summary")
def product_summary():
    in_stock = [p for p in products if p["in_stock"]]
    out_stock = [p for p in products if not p["in_stock"]]
    expensive = max(products, key=lambda p: p["price"])
    cheapest = min(products, key=lambda p: p["price"])
    categories = list(set(p["category"] for p in products))
    
    return {
        "total_products": len(products),
        "in_stock_count": len(in_stock),
        "out_of_stock_count": len(out_stock),
        "most_expensive": {"name": expensive["name"], "price": expensive["price"]},
        "cheapest": {"name": cheapest["name"], "price": cheapest["price"]},
        "categories": categories
    }

# Q5: Bulk Order Validation
class OrderItem(BaseModel):
    product_id: int = Field(..., gt=0)
    quantity: int = Field(..., ge=1, le=50)

class BulkOrder(BaseModel):
    company_name: str = Field(..., min_length=2)
    contact_email: str = Field(..., min_length=5)
    items: List[OrderItem] = Field(..., min_items=1)

@app.post("/orders/bulk")
def place_bulk_order(order: BulkOrder):
    confirmed, failed, grand_total = [], [], 0
    for item in order.items:
        product = next((p for p in products if p["id"] == item.product_id), None)
        if not product:
            failed.append({"product_id": item.product_id, "reason": "Product not found"})
        elif not product["in_stock"]:
            failed.append({"product_id": item.product_id, "reason": f"{product['name']} is out of stock"})
        else:
            subtotal = product["price"] * item.quantity
            grand_total += subtotal
            confirmed.append({"product": product["name"], "qty": item.quantity, "subtotal": subtotal})
            
    return {
        "company": order.company_name,
        "confirmed": confirmed,
        "failed": failed,
        "grand_total": grand_total
    }

# BONUS: Order Status Tracker
@app.patch("/orders/{order_id}/confirm")
def confirm_order(order_id: int):
    # Search for the order in the orders list
    for order in orders:
        if order.get("order_id") == order_id:
            order["status"] = "confirmed"
            return {"message": "Order status updated successfully", "updated_order": order}
    
    return {"error": f"Order ID {order_id} not found"}