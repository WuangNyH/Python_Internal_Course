from fastapi import FastAPI, HTTPException
from pydantic import BaseModel


app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "Hello World from FastAPI!"}


@app.get("/hello/{name}")
def say_hello(name: str) -> dict[str, str]:
    return {"message": f"Hello {name}!"}


class ErrorResponse(BaseModel):
    detail: str


# Thêm mã lỗi 400 trên Swagger UI
@app.get("/calculate/sum",
         responses={
             400: {"model": ErrorResponse, "description": "Business validation error"}
         })
def calculate_sum(a: int, b: int) -> dict[str, int]:
    if a < 0 or b < 0:
        raise HTTPException(
            status_code=400,
            detail="Negative numbers are not allowed")

    return {
        "a": a,
        "b": b,
        "sum": a + b
    }


# ===== Path Parameters =====
@app.get("/items/{item_id}")
def get_item(item_id: int) -> dict[str, int]:
    return {"item_id": item_id}


# Nhiều tham số
@app.get("/users/{user_id}/orders/{order_id}")
def get_order(user_id: int, order_id: str) -> dict[str, int | str]:
    return {"user": user_id, "order": order_id}


# ===== Query Parameters =====

# Giá trị mặc định
@app.get("/search")
def search(keyword: str, limit: int = 10):
    return {
        "keyword": keyword,
        "limit": limit
    }


# Optional query param
@app.get("/filter")
def filter_items(
        category: str | None = None,
        active: bool | None = None
) -> dict[str, str | bool | None]:
    return {
        "category": category,
        "active": active
    }


# Kết hợp Path + Query Parameters
@app.get("/products/{product_id}")
def get_product(
        product_id: int,
        price_filter: float | None = None,
        detailed: bool = False
) -> dict[str, int | float | bool | None]:
    return {
        "id": product_id,
        "price": price_filter,
        "detailed": detailed
    }

