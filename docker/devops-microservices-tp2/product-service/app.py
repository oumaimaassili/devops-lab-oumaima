from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI(title="Product Service", version="1.0.0")

products = [
    {"id": 1, "name": "Laptop", "price": 1200.0},
    {"id": 2, "name": "Keyboard", "price": 80.0},
    {"id": 3, "name": "Mouse", "price": 40.0},
]


class Product(BaseModel):
    id: int
    name: str
    price: float


@app.get("/health")
def health():
    return {"status": "ok", "service": "product-service"}


@app.get("/products", response_model=list[Product])
def list_products():
    return products


@app.get("/products/{product_id}", response_model=Product)
def get_product(product_id: int):
    for product in products:
        if product["id"] == product_id:
            return product
    raise HTTPException(status_code=404, detail="Product not found")
