from fastapi import FastAPI, HTTPException, Query, status
from pydantic import BaseModel, Field

app = FastAPI(title="상품 관리 API")


# =========================
# 스키마 - 용도별로 분리
# =========================


# 생성 요청: 모든 필드 필수 (desc 제외)
class ItemCreate(BaseModel):
    name: str = Field(min_length=1, max_length=50)
    price: float = Field(gt=0)
    desc: str | None = None


# 부분 수정 요청: 모든 필드 선택
class ItemUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=50)
    price: float | None = Field(default=None, gt=0)
    desc: str | None = None


# 응답: 클라이언트에게 보낼 형태
class ItemResponse(BaseModel):
    id: int
    name: str
    price: float
    desc: str | None = None


items_db: dict[int, dict] = {}
id_counter = 1


# =========================
# POST - 상품 생성
# =========================


@app.post("/items/", response_model=ItemResponse, status_code=status.HTTP_201_CREATED)
async def create_item(item: ItemCreate):
    global id_counter

    item_id = id_counter

    items_db[item_id] = {
        "id": item_id,
        "name": item.name,
        "price": item.price,
        "desc": item.desc,
    }

    id_counter += 1

    return items_db[item_id]


# =========================
# GET - 검색과 페이징
# =========================


@app.get("/items/", response_model=list[ItemResponse])
async def get_items(
    keyword: str | None = Query(default=None, description="상품명 부분 일치 검색"),
    skip: int = Query(default=0, ge=0, description="건너뛸 개수"),
    limit: int = Query(default=10, ge=1, le=100, description="가져올 개수"),
):
    results = list(items_db.values())

    if keyword:
        results = [item for item in results if keyword.lower() in item["name"].lower()]

    # 결과가 없어도 빈 목록을 정상 응답으로 반환한다
    return results[skip : skip + limit]


# =========================
# GET - 상품 단일 조회
# =========================


@app.get("/items/{item_id}", response_model=ItemResponse)
async def get_item(item_id: int):

    if item_id not in items_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"{item_id}번 상품을 찾을 수 없습니다.",
        )

    return items_db[item_id]


# =========================
# PUT - 전체 수정
# =========================


@app.put("/items/{item_id}", response_model=ItemResponse)
async def update_item(item_id: int, item: ItemCreate):

    if item_id not in items_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"{item_id}번 상품을 찾을 수 없습니다.",
        )

    items_db[item_id] = {
        "id": item_id,
        "name": item.name,
        "price": item.price,
        "desc": item.desc,
    }

    return items_db[item_id]


# =========================
# PATCH - 부분 수정
# =========================


@app.patch("/items/{item_id}", response_model=ItemResponse)
async def patch_item(item_id: int, item: ItemUpdate):

    if item_id not in items_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"{item_id}번 상품을 찾을 수 없습니다.",
        )

    # 클라이언트가 실제로 보낸 필드만 추린다
    changes = item.model_dump(exclude_unset=True)

    if not changes:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="수정할 내용이 없습니다.",
        )

    items_db[item_id].update(changes)

    return items_db[item_id]


# =========================
# DELETE - 상품 삭제
# =========================


@app.delete("/items/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_item(item_id: int):

    if item_id not in items_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"{item_id}번 상품을 찾을 수 없습니다.",
        )

    items_db.pop(item_id)

    # 204는 본문이 없다
    return None
