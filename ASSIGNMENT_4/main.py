from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional

app = FastAPI()

# 1. Data Models
class Product(BaseModel):
    id: int
    name: str
    price: int
    in_stock: bool

class CartItem(BaseModel):
    product_id: int
    product_name: str
    quantity: int
    unit_price: int
    subtotal: int

class CheckoutRequest(BaseModel):
    customer_name: str
    delivery_address: str

# 2. In-memory Database
products = [
    {"id": 1, "name": "Wireless Mouse", "price": 499, "in_stock": True},
    {"id": 2, "name": "Notebook", "price": 99, "in_stock": True},
    {"id": 3, "name": "USB Hub", "price": 899, "in_stock": False}, # Out of stock for Q3
    {"id": 4, "name": "Pen Set", "price": 49, "in_stock": True},
]

cart = []
orders = []
order_id_counter = 1

# 3. Helper Functions
def find_product(product_id: int):
    return next((p for p in products if p["id"] == product_id), None)

# 4. Endpoints

@app.post("/cart/add")
def add_to_cart(product_id: int, quantity: int = 1):
    product = find_product(product_id)
    
    # Q3: Handle Not Found
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    # Q3: Handle Out of Stock
    if not product["in_stock"]:
        raise HTTPException(status_code=400, detail=f"{product['name']} is out of stock")
    
    # Q4: Check for duplicates and update quantity
    for item in cart:
        if item["product_id"] == product_id:
            item["quantity"] += quantity
            item["subtotal"] = item["quantity"] * item["unit_price"]
            return {"message": "Cart updated", "cart_item": item}
    
    # Q1: Add new item
    new_item = {
        "product_id": product["id"],
        "product_name": product["name"],
        "quantity": quantity,
        "unit_price": product["price"],
        "subtotal": quantity * product["price"]
    }
    cart.append(new_item)
    return {"message": "Added to cart", "cart_item": new_item}

@app.get("/cart")
def view_cart():
    # Bonus Task & Q5 empty state
    if not cart:
        return {"message": "Cart is empty", "items": [], "grand_total": 0}
        
    grand_total = sum(item["subtotal"] for item in cart)
    return {
        "items": cart,
        "item_count": len(cart),
        "grand_total": grand_total
    }

@app.delete("/cart/{product_id}")
def remove_from_cart(product_id: int):
    # Q5: Remove item logic
    global cart
    initial_len = len(cart)
    cart = [item for item in cart if item["product_id"] != product_id]
    
    if len(cart) == initial_len:
        raise HTTPException(status_code=404, detail="Item not in cart")
    return {"message": "Item removed from cart"}

@app.post("/cart/checkout")
def checkout(request: CheckoutRequest):
    global order_id_counter
    
    # Bonus Task: Check if cart is empty before checkout
    if not cart:
        raise HTTPException(status_code=400, detail="Cart is empty — add items first")
    
    new_orders = []
    # Q6: Create an order for each item in the cart
    for item in cart:
        order = {
            "order_id": order_id_counter,
            "customer_name": request.customer_name,
            "product": item["product_name"],
            "quantity": item["quantity"],
            "total_price": item["subtotal"]
        }
        orders.append(order)
        new_orders.append(order)
        order_id_counter += 1
    
    # Q5: Clear cart after checkout
    cart.clear()
    
    return {
        "message": "Order placed successfully",
        "orders_placed": new_orders
    }

@app.get("/orders")
def get_orders():
    return {"orders": orders, "total_orders": len(orders)}