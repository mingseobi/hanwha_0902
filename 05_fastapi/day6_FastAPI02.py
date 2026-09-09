from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI()


class ItemsSchema(BaseModel):
    name: str
    price: float
    desc: str | None = None


items_db: dict[int, dict] = {}
id_counter = 1


# =========================
# POST - 상품 생성
# =========================

@app.post("/items/", status_code=201)
async def create_item(item: ItemsSchema):
    global id_counter

    item_id = id_counter

    items_db[item_id] = {
        "id": item_id,
        "name": item.name,
        "price": item.price,
        "desc": item.desc
    }

    id_counter += 1

    return {
        "message": "상품이 생성되었습니다.",
        "item": items_db[item_id]
    }


# =========================
# GET - 상품 전체 조회
# =========================

@app.get("/items/")
async def get_items():

    if not items_db:
        raise HTTPException(
            status_code=404,
            detail="등록된 상품이 없습니다."
        )

    return {
        "items": items_db
    }


# =========================
# GET - 상품 단일 조회
# =========================

@app.get("/items/{item_id}")
async def get_item(item_id: int):

    if item_id not in items_db:
        raise HTTPException(
            status_code=404,
            detail=f"{item_id}번 상품을 찾을 수 없습니다."
        )

    return {
        "item": items_db[item_id]
    }


# =========================
# PUT - 상품 수정
# =========================

@app.put("/items/{item_id}")
async def update_item(item_id: int, item: ItemsSchema):

    if item_id not in items_db:
        raise HTTPException(
            status_code=404,
            detail=f"{item_id}번 상품을 찾을 수 없습니다."
        )

    items_db[item_id] = {
        "id": item_id,
        "name": item.name,
        "price": item.price,
        "desc": item.desc
    }

    return {
        "message": "상품이 수정되었습니다.",
        "item": items_db[item_id]
    }


# =========================
# DELETE - 상품 삭제
# =========================

@app.delete("/items/{item_id}")
async def delete_item(item_id: int):

    if item_id not in items_db:
        raise HTTPException(
            status_code=404,
            detail=f"{item_id}번 상품을 찾을 수 없습니다."
        )

    deleted_item = items_db.pop(item_id)

    return {
        "message": "상품이 삭제되었습니다.",
        "item": deleted_item
    }
