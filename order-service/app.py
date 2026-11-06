import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import httpx

app = FastAPI(title="Order Service", version="1.0.0")

PRODUCT_SERVICE_URL = os.getenv("PRODUCT_SERVICE_URL", "http://localhost:8001")

orders = []


class OrderRequest(BaseModel):
    product_id: int
    quantity: int


@app.get("/health")
def health():
    return {"status": "ok", "service": "order-service"}


@app.get("/orders")
def list_orders():
    return orders


@app.post("/orders")
async def create_order(order: OrderRequest):
    async with httpx.AsyncClient(timeout=3.0) as client:
        response = await client.get(f"{PRODUCT_SERVICE_URL}/products/{order.product_id}")

    if response.status_code == 404:
        raise HTTPException(status_code=404, detail="Product not found")
    response.raise_for_status()

    product = response.json()
    new_order = {
        "id": len(orders) + 1,
        "product_id": product["id"],
        "product_name": product["name"],
        "quantity": order.quantity,
        "total": round(product["price"] * order.quantity, 2),
    }
    orders.append(new_order)
    return new_order
