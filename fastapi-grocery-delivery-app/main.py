from fastapi import FastAPI, HTTPException, Query, status
from pydantic import BaseModel, Field
from typing import Optional, List

app = FastAPI()

# --- 1. DATA STORE (Day 1) ---
grocery_items = [
    {"id": 1, "name": "Milk", "price": 50, "category": "Dairy", "is_in_stock": True},
    {"id": 2, "name": "Bread", "price": 35, "category": "Bakery", "is_in_stock": True},
    {"id": 3, "name": "Apples", "price": 120, "category": "Fruits", "is_in_stock": True},
    {"id": 4, "name": "Tomatoes", "price": 40, "category": "Vegetables", "is_in_stock": False},
    {"id": 5, "name": "Cheese", "price": 150, "category": "Dairy", "is_in_stock": True},
    {"id": 6, "name": "Eggs", "price": 70, "category": "Dairy", "is_in_stock": True},
]

orders = []
order_counter = 1
cart = []

# --- 2. MODELS (Day 2) ---
class OrderRequest(BaseModel):
    customer_name: str = Field(..., min_length=2)
    item_id: int = Field(..., gt=0)
    quantity: int = Field(..., gt=0, le=15)
    delivery_address: str = Field(..., min_length=10)
    is_express_delivery: bool = False

class NewItem(BaseModel):
    name: str
    price: float
    category: str
    is_in_stock: bool

# --- 3. HELPER FUNCTIONS (Day 3) ---
def find_item(item_id: int):
    return next((item for item in grocery_items if item["id"] == item_id), None)

def calculate_total(price: float, quantity: int, is_express: bool = False):
    total = price * quantity
    if is_express:
        total += 50
    return total

# --- 4. ENDPOINTS (ORDERED: FIXED BEFORE VARIABLE) ---

# Q1: Home Route
@app.get("/")
def home():
    return {"message": "Welcome to FreshMart Grocery Delivery"}

# Q5: Summary Endpoint (Fixed Route)
@app.get("/items/summary")
def get_items_summary():
    categories = list(set(i["category"] for i in grocery_items))
    in_stock = len([i for i in grocery_items if i["is_in_stock"]])
    return {
        "total_items": len(grocery_items),
        "in_stock": in_stock,
        "out_of_stock": len(grocery_items) - in_stock,
        "categories": categories
    }

# Q10 & Q20: Browsing & Filtering (Advanced)
@app.get("/items/browse")
def browse_items(
    search: Optional[str] = Query(None),
    category: Optional[str] = Query(None),
    sort_by: str = Query("name"),
    order: str = Query("asc"),
    page: int = Query(1, gt=0),
    limit: int = Query(5, gt=0)
):
    data = grocery_items
    # Filtering logic
    if search:
        data = [i for i in data if search.lower() in i["name"].lower()]
    if category:
        data = [i for i in data if i["category"].lower() == category.lower()]
    
    # Sorting logic
    reverse = True if order == "desc" else False
    data = sorted(data, key=lambda x: x.get(sort_by, "name"), reverse=reverse)
    
    # Pagination
    start = (page - 1) * limit
    end = start + limit
    return {"total": len(data), "page": page, "results": data[start:end]}

# Q2: List all items
@app.get("/items")
def get_all_items():
    return {"items": grocery_items, "total": len(grocery_items)}

# Q4: List all orders
@app.get("/orders")
def get_all_orders():
    return {"orders": orders, "total_orders": len(orders)}

# Q14: View Cart
@app.get("/cart")
def view_cart():
    total_price = sum(find_item(c["item_id"])["price"] * c["quantity"] for c in cart)
    return {"cart_items": cart, "total_cart_value": total_price}

# Q3: Get by ID (Variable Route)
@app.get("/items/{item_id}")
def get_item_by_id(item_id: int):
    item = find_item(item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    return item

# Q8: Create Order (Day 4)
@app.post("/orders", status_code=status.HTTP_201_CREATED)
def create_order(order: OrderRequest):
    global order_counter
    item = find_item(order.item_id)
    if not item or not item["is_in_stock"]:
        raise HTTPException(status_code=400, detail="Item unavailable")
    
    total_price = calculate_total(item["price"], order.quantity, order.is_express_delivery)
    new_order = {"order_id": order_counter, **order.dict(), "total_bill": total_price}
    orders.append(new_order)
    order_counter += 1
    return new_order

# Q11: Add New Item
@app.post("/items", status_code=status.HTTP_201_CREATED)
def add_item(item: NewItem):
    if any(i["name"].lower() == item.name.lower() for i in grocery_items):
        raise HTTPException(status_code=400, detail="Item already exists")
    new_id = grocery_items[-1]["id"] + 1 if grocery_items else 1
    item_dict = {"id": new_id, **item.dict()}
    grocery_items.append(item_dict)
    return item_dict

# Q14: Add to Cart
@app.post("/cart/add")
def add_to_cart(item_id: int, quantity: int):
    item = find_item(item_id)
    if not item: raise HTTPException(status_code=404, detail="Item not found")
    
    for c in cart:
        if c["item_id"] == item_id:
            c["quantity"] += quantity
            return {"message": "Updated quantity", "cart": cart}
    
    cart.append({"item_id": item_id, "name": item["name"], "quantity": quantity})
    return {"message": "Added to cart", "cart": cart}

# Q15: Checkout (Workflow)
@app.post("/cart/checkout", status_code=status.HTTP_201_CREATED)
def checkout(customer_name: str, address: str):
    if not cart: raise HTTPException(status_code=400, detail="Cart is empty")
    global order_counter
    
    processed_orders = []
    for entry in cart:
        item = find_item(entry["item_id"])
        order_data = {
            "order_id": order_counter,
            "customer": customer_name,
            "item": entry["name"],
            "bill": item["price"] * entry["quantity"]
        }
        orders.append(order_data)
        processed_orders.append(order_data)
        order_counter += 1
    
    cart.clear()
    return {"status": "Order Placed Successfully", "orders": processed_orders}

# Q12: Update Item
@app.put("/items/{item_id}")
def update_item(item_id: int, price: Optional[float] = None, in_stock: Optional[bool] = None):
    item = find_item(item_id)
    if not item: raise HTTPException(status_code=404, detail="Item not found")
    if price is not None: item["price"] = price
    if in_stock is not None: item["is_in_stock"] = in_stock
    return item

# Q13: Delete Item
@app.delete("/items/{item_id}")
def delete_item(item_id: int):
    item = find_item(item_id)
    if not item: raise HTTPException(status_code=404, detail="Item not found")
    grocery_items.remove(item)
    return {"message": f"Item {item_id} deleted"}