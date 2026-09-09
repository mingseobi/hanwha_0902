from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()


# 데이터 형식
class User(BaseModel):
    name: str
    price: float
    desc: str | None = None


class Product(BaseModel):
    name: str
    price: int


# 임시 데이터
users = [
    {
        "id": 1,
        "name": "철수",
        "price": 1000,
        "desc": "첫 번째 사용자"
    },
    {
        "id": 2,
        "name": "영희",
        "price": 2000,
        "desc": "두 번째 사용자"
    }
]

products = [
    {
        "id": 1,
        "name": "노트북",
        "price": 1000000
    },
    {
        "id": 2,
        "name": "마우스",
        "price": 30000
    }
]


# =========================
# GET - 조회
# =========================

@app.get("/")
async def root():
    return {"message": "안녕!"}


@app.get("/users")
async def get_users():
    return {"users": users}


@app.get("/users/{user_id}")
async def get_user(user_id: int):

    for user in users:
        if user["id"] == user_id:
            return user

    return {"message": "사용자를 찾을 수 없습니다."}


@app.get("/products")
async def get_products():
    return {"products": products}


@app.get("/products/{product_id}")
async def get_product(product_id: int):

    for product in products:
        if product["id"] == product_id:
            return product

    return {"message": "상품을 찾을 수 없습니다."}


# =========================
# POST - 생성
# =========================

@app.post("/users")
async def create_user(user: User):

    new_id = len(users) + 1

    new_user = {
        "id": new_id,
        "name": user.name,
        "price": user.price,
        "desc": user.desc
    }

    users.append(new_user)

    return {
        "message": "사용자가 생성되었습니다.",
        "user": new_user
    }


@app.post("/products")
async def create_product(product: Product):

    new_id = len(products) + 1

    new_product = {
        "id": new_id,
        "name": product.name,
        "price": product.price
    }

    products.append(new_product)

    return {
        "message": "상품이 생성되었습니다.",
        "product": new_product
    }


# =========================
# PUT - 수정
# =========================

@app.put("/users/{user_id}")
async def update_user(user_id: int, user: User):

    for i in range(len(users)):

        if users[i]["id"] == user_id:

            users[i] = {
                "id": user_id,
                "name": user.name,
                "price": user.price,
                "desc": user.desc
            }

            return {
                "message": "사용자 정보가 수정되었습니다.",
                "user": users[i]
            }

    return {"message": "사용자를 찾을 수 없습니다."}


@app.put("/products/{product_id}")
async def update_product(product_id: int, product: Product):

    for i in range(len(products)):

        if products[i]["id"] == product_id:

            products[i] = {
                "id": product_id,
                "name": product.name,
                "price": product.price
            }

            return {
                "message": "상품 정보가 수정되었습니다.",
                "product": products[i]
            }

    return {"message": "상품을 찾을 수 없습니다."}


# =========================
# DELETE - 삭제
# =========================

@app.delete("/users/{user_id}")
async def delete_user(user_id: int):

    for i in range(len(users)):

        if users[i]["id"] == user_id:

            deleted_user = users.pop(i)

            return {
                "message": "사용자가 삭제되었습니다.",
                "user": deleted_user
            }

    return {"message": "사용자를 찾을 수 없습니다."}


@app.delete("/products/{product_id}")
async def delete_product(product_id: int):

    for i in range(len(products)):

        if products[i]["id"] == product_id:

            deleted_product = products.pop(i)

            return {
                "message": "상품이 삭제되었습니다.",
                "product": deleted_product
            }

    return {"message": "상품을 찾을 수 없습니다."}
