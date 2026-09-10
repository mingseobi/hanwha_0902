# FastAPI CRUD — day5, day6

라우팅과 CRUD의 기본기를 익히고(day5), 검색·부분 수정·응답 스키마 같은 실무 패턴을 더합니다(day6).

실행 방법과 패키지 준비는 [05_fastapi 개요](README.md)를 참고합니다.

## day5_FastAPI01.py — CRUD 기본

사용자와 상품 두 리소스에 대해 조회, 생성, 수정, 삭제를 구현한 파일입니다.

### 앱과 모델 정의

```python
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
```

`app = FastAPI()`가 애플리케이션 본체이고, 이후 모든 경로가 여기에 등록됩니다.

두 모델은 요청 본문의 형식을 정의하며, 검증 규칙 역할도 겸합니다.

### 데코레이터로 경로 등록

```python
@app.get("/")
async def root():
    return {"message": "안녕!"}
```

```text
@app.get("/")
  │   │    └ 경로(path)
  │   └ HTTP 메서드
  └ 등록 대상 앱
```

| 데코레이터      | HTTP 메서드 | 역할      |
| --------------- | ----------- | --------- |
| `@app.get()`    | GET         | 조회      |
| `@app.post()`   | POST        | 생성      |
| `@app.put()`    | PUT         | 전체 수정 |
| `@app.delete()` | DELETE      | 삭제      |

반환한 `dict`는 FastAPI가 자동으로 JSON으로 변환합니다. `json.dumps()`를 호출할 필요가 없습니다.

### 경로 파라미터

URL의 일부를 변수로 받는 방식입니다.

```python
@app.get("/users/{user_id}")
async def get_user(user_id: int):

    for user in users:
        if user["id"] == user_id:
            return user

    raise HTTPException(status_code=404, detail=f"{user_id}번 사용자를 찾을 수 없습니다.")
```

중괄호 안의 이름과 함수 매개변수 이름이 같아야 값이 전달됩니다.

`user_id: int` 타입 힌트가 검증까지 담당합니다.

```text
GET /users/1     → user_id = 1 (int로 변환)
GET /users/abc   → HTTP 422, int_parsing 오류 (함수는 실행되지 않음)
```

### HTTPException — 실패를 상태 코드로 전달

찾지 못했을 때 메시지만 반환하면 상태 코드가 200이 되어, 호출한 쪽에서 실패를 알아채지 못합니다.

```python
# 상태 코드가 200 OK — 실패가 전달되지 않는다
return {"message": "사용자를 찾을 수 없습니다."}

# 상태 코드가 404 Not Found
raise HTTPException(status_code=404, detail=f"{user_id}번 사용자를 찾을 수 없습니다.")
```

`return`이 아니라 `raise`라는 점이 핵심입니다.

```text
GET /users/999  →  HTTP 404 Not Found
                   {"detail": "999번 사용자를 찾을 수 없습니다."}
```

`detail`은 FastAPI가 오류 응답에 사용하는 표준 키입니다. Pydantic 검증 실패(422)도 같은 키를 쓰므로, 클라이언트는 오류 처리를 하나로 통일할 수 있습니다.

| 상황                  | 상태 코드                |
| --------------------- | ------------------------ |
| 조회 성공             | 200 OK                   |
| 생성 성공             | 201 Created              |
| 삭제 성공 (본문 없음) | 204 No Content           |
| 잘못된 요청           | 400 Bad Request          |
| 리소스 없음           | 404 Not Found            |
| 입력 형식 오류        | 422 Unprocessable Entity |

### 요청 본문과 생성

매개변수 타입을 Pydantic 모델로 지정하면, 요청 본문 JSON이 그 모델로 변환됩니다.

```python
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
```

FastAPI는 매개변수 타입만 보고 값을 어디서 가져올지 판단합니다.

| 매개변수 선언                            | 값을 읽는 위치      |
| ---------------------------------------- | ------------------- |
| `user_id: int` (경로에 `{user_id}` 있음) | 경로 파라미터       |
| `user: User` (Pydantic 모델)             | 요청 본문 JSON      |
| `q: str = None` (경로에 없는 일반 타입)  | 쿼리 스트링 `?q=값` |

본문 검증에 실패하면 함수는 실행되지 않고 HTTP 422와 상세 오류가 자동 응답됩니다.

```json
{ "detail": [{ "type": "missing", "loc": ["body", "email"], "msg": "Field required" }] }
```

### ID는 별도 카운터로 관리한다

⚠️ ID를 `len(users) + 1`로 계산하면 삭제가 일어난 뒤 값이 중복됩니다.

```text
초기 상태          id = [1, 2]
POST            → len+1 = 3,  id = [1, 2, 3]
DELETE /users/1 →             id = [2, 3]
POST            → len+1 = 3,  id = [2, 3, 3]
                                     └───┴ 중복
```

ID가 중복되면 `/users/3`은 앞의 것만 반환하고, 뒤의 데이터는 조회도 수정도 삭제도 되지 않습니다.

💡 개수(`len`)와 식별자(`id`)는 별개입니다. ID는 삭제와 무관하게 계속 증가하는 카운터로 관리해야 합니다.

```python
# 현재 데이터의 최댓값 다음부터 시작한다
user_id_counter = max((user["id"] for user in users), default=0) + 1


@app.post("/users", status_code=201)
async def create_user(user: User):
    global user_id_counter
    ...
    user_id_counter += 1
```

시작값을 `3`처럼 직접 적으면, 초기 데이터를 늘렸을 때 카운터를 함께 고치지 않는 순간 같은 문제가 다시 생깁니다. 데이터에서 계산하면 그런 실수가 생기지 않습니다.

`default=0`은 목록이 비어 있을 때를 위한 값입니다. 이것이 없으면 `max()`가 빈 시퀀스에서 `ValueError`를 냅니다.

`global`은 함수 밖의 변수를 수정하겠다는 선언입니다. 이 선언이 없으면 대입하는 순간 지역 변수로 취급되어 `UnboundLocalError`가 발생합니다.

카운터를 쓰면 삭제 후에도 ID가 겹치지 않습니다.

```text
DELETE /users/1  →  id = [2, 3]
POST             →  id = [2, 3, 4]   중복 없음
```

## day6_FastAPI02.py — 실무 패턴

단일 리소스에 집중하면서, 실제 API에 필요한 기능을 더한 파일입니다.

### 용도별 스키마 분리

day5는 하나의 모델을 생성과 수정에 함께 썼지만, 요청의 성격에 따라 필요한 필드가 다릅니다.

```python
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
```

| 스키마         | 용도           | 필드      |
| -------------- | -------------- | --------- |
| `ItemCreate`   | POST, PUT 요청 | 필수      |
| `ItemUpdate`   | PATCH 요청     | 전부 선택 |
| `ItemResponse` | 모든 응답      | `id` 포함 |

`ItemResponse`에만 `id`가 있는 이유는, 서버가 부여하는 값이라 요청에 포함되어서는 안 되기 때문입니다.

### response_model — 응답 형태 고정

```python
@app.post("/items/", response_model=ItemResponse, status_code=status.HTTP_201_CREATED)
async def create_item(item: ItemCreate):
    ...
    return items_db[item_id]
```

`response_model`을 지정하면 반환값이 그 모델을 거쳐 나갑니다.

```json
{ "id": 5, "name": "모니터", "price": 400000.0, "desc": "27인치" }
```

| 효과           | 설명                                              |
| -------------- | ------------------------------------------------- |
| 형태 보장      | 모델에 없는 필드는 응답에서 제거됨                |
| 정보 노출 차단 | 비밀번호처럼 내부에만 필요한 값이 빠져나가지 않음 |
| 문서 반영      | `/docs`의 응답 예시가 이 모델로 표시됨            |

목록 응답에는 `list[ItemResponse]`를 지정합니다.

### status 상수

```python
from fastapi import status

status_code=status.HTTP_201_CREATED     # 201
status_code=status.HTTP_404_NOT_FOUND   # 404
status_code=status.HTTP_204_NO_CONTENT  # 204
```

숫자를 직접 쓰는 것과 동작은 같지만, 이름으로 의도가 드러나고 오타를 줄일 수 있습니다.

### 쿼리 파라미터 — 검색과 페이징

경로에 없는 매개변수는 쿼리 스트링에서 값을 읽습니다.

```python
@app.get("/items/", response_model=list[ItemResponse])
async def get_items(
    keyword: str | None = Query(default=None, description="상품명 부분 일치 검색"),
    skip: int = Query(default=0, ge=0, description="건너뛸 개수"),
    limit: int = Query(default=10, ge=1, le=100, description="가져올 개수"),
):
    results = list(items_db.values())

    if keyword:
        results = [item for item in results if keyword.lower() in item["name"].lower()]

    return results[skip : skip + limit]
```

```text
GET /items/?keyword=노트북      → ['노트북', '게이밍 노트북']
GET /items/?skip=1&limit=2      → ['게이밍 노트북', '마우스']
```

`Query()`는 기본값과 함께 제약을 지정합니다. `Field()`가 본문 필드에 하는 역할을 쿼리 파라미터에서 합니다.

```text
GET /items/?limit=999  →  HTTP 422, less_than_equal  (le=100 위반)
```

⚠️ `limit`에 상한을 두는 이유는, 데이터가 많아졌을 때 한 번의 요청이 전체를 끌어오는 상황을 막기 위해서입니다.

### 빈 목록은 오류가 아니다

```python
# 결과가 없어도 빈 목록을 정상 응답으로 반환한다
return results[skip : skip + limit]
```

```text
GET /items/                    (등록된 상품 없음)  →  HTTP 200  []
GET /items/?keyword=없는상품                       →  HTTP 200  []
```

특정 리소스를 지목한 `/items/999`는 404가 맞지만, 목록 조회에서 결과가 0건인 것은 "조건에 맞는 것이 없다"는 정상 응답입니다.

클라이언트도 빈 목록이면 화면에 "항목 없음"을 표시하면 되지만, 404를 받으면 오류 처리 분기를 타게 됩니다.

### PUT과 PATCH의 차이

가장 헷갈리기 쉬운 부분입니다. 같은 데이터에 두 방식을 적용한 결과를 비교하면 분명해집니다.

```text
원본             {"id": 1, "name": "노트북", "price": 1000000.0, "desc": "16인치 M4"}

PUT   {"name": "노트북", "price": 900000}
  →              {"id": 1, "name": "노트북", "price": 900000.0,  "desc": null}
                                                                  └ 보내지 않은 값이 사라짐

PATCH {"price": 900000}
  →              {"id": 1, "name": "노트북", "price": 900000.0,  "desc": "16인치 M4"}
                                                                  └ 유지됨
```

| 구분             | PUT                 | PATCH               |
| ---------------- | ------------------- | ------------------- |
| 의미             | 전체 교체           | 부분 수정           |
| 요청 스키마      | `ItemCreate` (필수) | `ItemUpdate` (선택) |
| 보내지 않은 필드 | 기본값으로 덮어씀   | 기존 값 유지        |
| `name` 생략 시   | HTTP 422            | HTTP 200            |

### exclude_unset — 보낸 필드만 추리기

PATCH의 핵심은 이 한 줄입니다.

```python
# 클라이언트가 실제로 보낸 필드만 추린다
changes = item.model_dump(exclude_unset=True)

if not changes:
    raise HTTPException(status_code=400, detail="수정할 내용이 없습니다.")

items_db[item_id].update(changes)
```

`ItemUpdate`의 모든 필드는 기본값이 `None`이라, 그냥 `model_dump()`를 쓰면 보내지 않은 필드까지 `None`으로 들어옵니다.

| 호출                             | 결과                                              |
| -------------------------------- | ------------------------------------------------- |
| `model_dump()`                   | `{"name": None, "price": 900000.0, "desc": None}` |
| `model_dump(exclude_unset=True)` | `{"price": 900000.0}`                             |

⚠️ `exclude_unset=True`가 없으면 PATCH가 PUT처럼 동작해, 보내지 않은 필드가 전부 `None`으로 덮어써집니다.

빈 본문에 대한 처리도 함께 두었습니다.

```text
PATCH /items/1  본문 {}  →  HTTP 400  {"detail": "수정할 내용이 없습니다."}
```

### 204 No Content — 본문 없는 삭제

```python
@app.delete("/items/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_item(item_id: int):

    if item_id not in items_db:
        raise HTTPException(status_code=404, detail=f"{item_id}번 상품을 찾을 수 없습니다.")

    items_db.pop(item_id)

    # 204는 본문이 없다
    return None
```

```text
DELETE /items/2  →  HTTP 204, 본문 0바이트
```

삭제는 성공했다는 사실 외에 돌려줄 내용이 없으므로, 본문 없이 상태 코드만 보내는 204가 적합합니다.

⚠️ 204를 지정하고 값을 반환하면 규격에 어긋납니다. 삭제한 내용을 돌려주고 싶다면 200을 쓰고 본문을 반환해야 합니다.

### 저장 구조 — list와 dict

```python
items_db: dict[int, dict] = {}
```

| 구분        | day5 (`list`)          | day6 (`dict`)             |
| ----------- | ---------------------- | ------------------------- |
| 조회        | 전체 순회 후 `id` 비교 | 키로 즉시 접근            |
| 시간 복잡도 | O(n)                   | O(1)                      |
| 존재 확인   | for 루프               | `item_id not in items_db` |
| 코드 길이   | 반복문 필요            | 조건문 한 줄              |

## 알아둘 동작

### 타입 변환은 API에서도 동작한다

```text
POST /items/  본문 {"name": "책", "price": "12000"}
           →  HTTP 201, 저장된 값 12000.0 (float)
```

문자열 `"12000"`이 `price: float` 선언에 따라 변환되어 저장됩니다.

### async def에 await가 없어도 되는 이유

이 파일들의 함수는 모두 `async def`지만 `await`가 없습니다. 문법 오류는 아니며 정상 동작합니다.

| 선언        | FastAPI의 처리            |
| ----------- | ------------------------- |
| `async def` | 이벤트 루프에서 직접 실행 |
| `def`       | 별도 스레드 풀에서 실행   |

⚠️ 메모리 데이터만 다루는 지금은 문제가 없지만, `async def` 안에서 오래 걸리는 동기 작업(파일 읽기, `requests` 호출, `time.sleep`)을 하면 이벤트 루프 전체가 멈춥니다.

그런 작업은 `def`로 선언하거나, `await`가 가능한 비동기 라이브러리를 사용해야 합니다.

## 정리 — day5에서 day6로

| 항목      | day5             | day6                      |
| --------- | ---------------- | ------------------------- |
| 리소스    | 사용자, 상품 2종 | 상품 1종                  |
| 저장 구조 | `list`           | `dict`                    |
| 스키마    | 요청용 1개       | 생성·수정·응답 3개로 분리 |
| 응답 형태 | `dict` 그대로    | `response_model`로 고정   |
| 목록 조회 | 전체 반환        | 검색과 페이징             |
| 수정      | PUT (전체 교체)  | PUT + PATCH (부분 수정)   |
| 삭제 응답 | 200 + 본문       | 204 (본문 없음)           |
| 상태 코드 | 숫자 직접 지정   | `status` 상수             |

## 자주 발생하는 오류

| 원인                               | 증상                              | 해결                              |
| ---------------------------------- | --------------------------------- | --------------------------------- |
| `python 파일.py`로 실행            | 아무 일도 일어나지 않음           | `uvicorn 파일명:app --reload`     |
| uvicorn 인자에 `.py` 포함          | `ModuleNotFoundError`             | 확장자 없이 `day5_FastAPI01:app`  |
| `global` 선언 누락                 | `UnboundLocalError`               | 함수 첫 줄에 `global id_counter`  |
| 오류를 `return HTTPException(...)` | 상태 코드가 200으로 응답          | `raise`로 발생시켜야 함           |
| PATCH에 `exclude_unset` 누락       | 보내지 않은 필드가 `None`이 됨    | `model_dump(exclude_unset=True)`  |
| 204인데 본문 반환                  | 규격 위반                         | `return None` 또는 200으로 변경   |
| 경로 등록 순서                     | `/items/new`가 `{item_id}`에 잡힘 | 구체적인 경로를 먼저 등록         |
| 포트 사용 중                       | `Address already in use`          | `--port 8001` 또는 기존 서버 종료 |

## 점검 항목

- [ ] `@app.get("/users/{user_id}")`의 중괄호가 의미하는 것
- [ ] `user: User` 매개변수의 값이 어디서 오는가 — 요청 본문 JSON
- [ ] `HTTPException`을 `return`이 아니라 `raise`로 쓰는 이유
- [ ] `len(users) + 1`로 ID를 만들면 언제 문제가 생기는가 — 삭제 이후
- [ ] `global` 선언이 필요한 이유
- [ ] 목록 조회가 0건일 때 404가 적절하지 않은 이유
- [ ] PUT과 PATCH에서 보내지 않은 필드가 각각 어떻게 되는가
- [ ] `exclude_unset=True`를 빼면 PATCH가 어떻게 동작하는가
- [ ] `response_model`을 지정했을 때 얻는 것
- [ ] 204 응답에 본문을 넣으면 안 되는 이유

## 다음 문서

- API를 화면과 연결하기 → [day7 프로젝트](day7_project.md)
