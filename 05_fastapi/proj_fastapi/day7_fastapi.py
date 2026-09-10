"""상품 관리 API - Streamlit 관리 화면의 백엔드.

실행:
    uvicorn day7_fastapi:app --reload
"""

from fastapi import FastAPI, HTTPException, Query, status
from pydantic import BaseModel, Field

app = FastAPI(title="상품 관리 API", version="1.0.0")


# =========================
# 스키마
# =========================


class ItemCreate(BaseModel):
    """생성과 전체 수정(PUT)에 사용한다. desc를 뺀 나머지는 필수."""

    name: str = Field(min_length=1, max_length=50, description="상품명")
    price: int = Field(gt=0, le=100_000_000, description="가격(원)")
    stock: int = Field(default=0, ge=0, description="재고 수량")
    desc: str | None = Field(default=None, max_length=200, description="상품 설명")


class ItemUpdate(BaseModel):
    """부분 수정(PATCH)에 사용한다. 모든 필드가 선택."""

    name: str | None = Field(default=None, min_length=1, max_length=50)
    price: int | None = Field(default=None, gt=0, le=100_000_000)
    stock: int | None = Field(default=None, ge=0)
    desc: str | None = Field(default=None, max_length=200)


class ItemResponse(BaseModel):
    """클라이언트에게 내보내는 형태."""

    id: int
    name: str
    price: int
    stock: int
    desc: str | None = None


class ItemPage(BaseModel):
    """목록 응답. 화면에서 페이지를 계산할 수 있도록 total을 함께 담는다."""

    total: int
    skip: int
    limit: int
    items: list[ItemResponse]


class Summary(BaseModel):
    """관리 화면 상단 지표."""

    count: int
    total_stock: int
    total_value: int
    out_of_stock: int


# =========================
# 저장소 (메모리)
# =========================

items_db: dict[int, dict] = {
    1: {"id": 1, "name": "노트북", "price": 1_450_000, "stock": 12, "desc": "16인치"},
    2: {"id": 2, "name": "무선 마우스", "price": 32_000, "stock": 0, "desc": None},
    3: {"id": 3, "name": "기계식 키보드", "price": 89_000, "stock": 7, "desc": "적축"},
    4: {"id": 4, "name": "27인치 모니터", "price": 410_000, "stock": 3, "desc": "QHD"},
    5: {"id": 5, "name": "USB-C 허브", "price": 45_000, "stock": 25, "desc": None},
}

# 현재 데이터의 최댓값 다음부터 시작해 삭제와 무관하게 증가한다
id_counter = max(items_db, default=0) + 1


# =========================
# 상태 확인
# =========================


@app.get("/health")
async def health():
    """관리 화면이 서버 연결 상태를 표시할 때 사용한다."""
    return {"status": "ok", "count": len(items_db)}


# =========================
# 목록과 요약
# =========================


@app.get("/items/summary", response_model=Summary)
async def get_summary():
    """상단 지표용 집계.

    주의: 이 경로는 /items/{item_id}보다 먼저 등록해야 한다.
    순서가 바뀌면 'summary'가 item_id로 해석되어 422가 발생한다.
    """
    values = items_db.values()

    return {
        "count": len(items_db),
        "total_stock": sum(item["stock"] for item in values),
        "total_value": sum(item["price"] * item["stock"] for item in values),
        "out_of_stock": sum(1 for item in values if item["stock"] == 0),
    }


@app.get("/items", response_model=ItemPage)
async def get_items(
    keyword: str | None = Query(default=None, description="상품명 부분 일치 검색"),
    sort_by: str = Query(default="id", pattern="^(id|name|price|stock)$"),
    order: str = Query(default="asc", pattern="^(asc|desc)$"),
    skip: int = Query(default=0, ge=0, description="건너뛸 개수"),
    limit: int = Query(default=10, ge=1, le=100, description="가져올 개수"),
):
    results = list(items_db.values())

    if keyword:
        results = [item for item in results if keyword.lower() in item["name"].lower()]

    results.sort(key=lambda item: item[sort_by], reverse=(order == "desc"))

    # 결과가 없어도 빈 목록을 정상 응답으로 반환한다
    return {
        "total": len(results),
        "skip": skip,
        "limit": limit,
        "items": results[skip : skip + limit],
    }


# =========================
# 단건 조회
# =========================


def find_item(item_id: int) -> dict:
    """없으면 404를 발생시키고, 있으면 해당 항목을 돌려준다."""
    if item_id not in items_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"{item_id}번 상품을 찾을 수 없습니다.",
        )

    return items_db[item_id]


@app.get("/items/{item_id}", response_model=ItemResponse)
async def get_item(item_id: int):
    return find_item(item_id)


# =========================
# 생성
# =========================


@app.post("/items", response_model=ItemResponse, status_code=status.HTTP_201_CREATED)
async def create_item(item: ItemCreate):
    global id_counter

    item_id = id_counter

    items_db[item_id] = {
        "id": item_id,
        "name": item.name,
        "price": item.price,
        "stock": item.stock,
        "desc": item.desc,
    }

    id_counter += 1

    return items_db[item_id]


# =========================
# 수정
# =========================


@app.put("/items/{item_id}", response_model=ItemResponse)
async def update_item(item_id: int, item: ItemCreate):
    """전체 교체. 보내지 않은 desc는 None이 된다."""
    find_item(item_id)

    items_db[item_id] = {
        "id": item_id,
        "name": item.name,
        "price": item.price,
        "stock": item.stock,
        "desc": item.desc,
    }

    return items_db[item_id]


@app.patch("/items/{item_id}", response_model=ItemResponse)
async def patch_item(item_id: int, item: ItemUpdate):
    """부분 수정. 보낸 필드만 반영한다."""
    stored = find_item(item_id)

    changes = item.model_dump(exclude_unset=True)

    if not changes:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="수정할 내용이 없습니다.",
        )

    stored.update(changes)

    return stored


# =========================
# 삭제
# =========================


@app.delete("/items/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_item(item_id: int):
    find_item(item_id)
    items_db.pop(item_id)

    # 204는 본문이 없다
    return None
