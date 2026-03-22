# Grocery Delivery App - FastAPI Backend

A real-world grocery delivery backend system built using FastAPI as part of the Innomatics Research Labs internship.

## 🚀 Features
- **CRUD Operations**: Manage grocery items (Create, Read, Update, Delete).
- **Pydantic Validation**: Strict data validation for orders and items.
- **Workflow**: Integrated Cart to Checkout system.
- **Advanced Search**: Keyword-based search, sorting, and pagination.
- **API Documentation**: Fully interactive Swagger UI.

## 🛠️ Tech Stack
- Python
- FastAPI
- Pydantic
- Uvicorn

## 📂 Project Structure
- `main.py`: Main application code with all 20 endpoints.
- `requirements.txt`: Python dependencies.
- `screenshots/`: API testing evidence from Swagger UI.

## 🏁 How to Run
1. Clone the repository.
2. Install dependencies: `pip install -r requirements.txt`
3. Start the server: `uvicorn main:app --reload`
4. Access documentation at: `http://127.0.0.1:8000/docs`