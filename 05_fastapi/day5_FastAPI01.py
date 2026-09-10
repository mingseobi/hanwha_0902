from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI()


# 데이터 형식
class User(BaseModel):
    name: str
    email: str
    desc: str | None = None


class Product(BaseModel):
    name: str
    price: int


# 임시 데이터
users = [
    {"id": 1, "name": "철수", "email": "chulsoo@example.com", "desc": "첫 번째 사용자"},
    {
        "id": 2,
        "name": "영희",
        "email": "younghee@example.com",
        "desc": "두 번째 사용자",
    },
]

products = [
    {"id": 1, "name": "노트북", "price": 1000000},
    {"id": 2, "name": "마우스", "price": 30000},
]

# ID 카운터 - 현재 데이터의 최댓값 다음부터 시작해 삭제와 무관하게 증가한다
user_id_counter = max((user["id"] for user in users), default=0) + 1
product_id_counter = max((product["id"] for product in products), default=0) + 1


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

    raise HTTPException(
        status_code=404, detail=f"{user_id}번 사용자를 찾을 수 없습니다."
    )


@app.get("/products")
async def get_products():
    return {"products": products}


@app.get("/products/{product_id}")
async def get_product(product_id: int):

    for product in products:
        if product["id"] == product_id:
            return product

    raise HTTPException(
        status_code=404, detail=f"{product_id}번 상품을 찾을 수 없습니다."
    )


# =========================
# POST - 생성
# =========================


@app.post("/users", status_code=201)
async def create_user(user: User):
    global user_id_counter

    new_user = {
        "id": user_id_counter,
        "name": user.name,
        "email": user.email,
        "desc": user.desc,
    }

    users.append(new_user)
    user_id_counter += 1

    return {"message": "사용자가 생성되었습니다.", "user": new_user}


@app.post("/products", status_code=201)
async def create_product(product: Product):
    global product_id_counter

    new_product = {
        "id": product_id_counter,
        "name": product.name,
        "price": product.price,
    }

    products.append(new_product)
    product_id_counter += 1

    return {"message": "상품이 생성되었습니다.", "product": new_product}


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
                "email": user.email,
                "desc": user.desc,
            }

            return {"message": "사용자 정보가 수정되었습니다.", "user": users[i]}

    raise HTTPException(
        status_code=404, detail=f"{user_id}번 사용자를 찾을 수 없습니다."
    )


@app.put("/products/{product_id}")
async def update_product(product_id: int, product: Product):

    for i in range(len(products)):

        if products[i]["id"] == product_id:

            products[i] = {
                "id": product_id,
                "name": product.name,
                "price": product.price,
            }

            return {"message": "상품 정보가 수정되었습니다.", "product": products[i]}

    raise HTTPException(
        status_code=404, detail=f"{product_id}번 상품을 찾을 수 없습니다."
    )


# =========================
# DELETE - 삭제
# =========================


@app.delete("/users/{user_id}")
async def delete_user(user_id: int):

    for i in range(len(users)):

        if users[i]["id"] == user_id:

            deleted_user = users.pop(i)

            return {"message": "사용자가 삭제되었습니다.", "user": deleted_user}

    raise HTTPException(
        status_code=404, detail=f"{user_id}번 사용자를 찾을 수 없습니다."
    )


@app.delete("/products/{product_id}")
async def delete_product(product_id: int):

    for i in range(len(products)):

        if products[i]["id"] == product_id:

            deleted_product = products.pop(i)

            return {"message": "상품이 삭제되었습니다.", "product": deleted_product}

    raise HTTPException(
        status_code=404, detail=f"{product_id}번 상품을 찾을 수 없습니다."
    )
