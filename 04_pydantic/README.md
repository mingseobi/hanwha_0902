# 04. Pydantic

타입 힌트를 실제 검증 규칙으로 동작하게 만드는 라이브러리를 다루는 단계입니다.

| 항목        | 내용                                                                         |
| ----------- | ---------------------------------------------------------------------------- |
| 과목        | AI 서비스 백엔드 프로그래밍 실무                                             |
| 실습일      | Day 4 (9/7 월)                                                               |
| 키워드      | `BaseModel`, 자동 타입 변환, `Field`, Optional, 중첩 모델, `ValidationError` |
| 필요 패키지 | `pydantic` (v2 기준)                                                         |

Python의 타입 힌트는 실행 시점에 검사되지 않습니다.

```python
age: int = "25"   # 오류 없이 통과
```

그래서 앞선 폴더에서는 `if not cleaned: raise ValueError(...)` 형태로 검증을 직접 작성했습니다.

💡 Pydantic은 이 검증을 타입 힌트 선언만으로 대체합니다.

## 파일 구성

| 파일                                       | 단계 | 주제                                              |
| ------------------------------------------ | ---- | ------------------------------------------------- |
| [`day4_pydantic01.py`](day4_pydantic01.py) | 1    | `BaseModel` — 타입 검증과 자동 변환               |
| [`day4_pydantic02.py`](day4_pydantic02.py) | 2    | `Field`, Optional, 중첩 모델 — 복잡한 데이터 검증 |
| [`day4_pydantic03.py`](day4_pydantic03.py) | 3    | API 요청 모델링 — 검증과 변환의 실무 적용         |
| [`pydantic_note.md`](pydantic_note.md)     | —    | 수업 중 작성한 요약 메모                          |

## 사전 준비

```bash
pip install pydantic
```

```python
import pydantic
print(pydantic.VERSION)   # 2.x
```

이 문서는 Pydantic v2를 기준으로 작성되었습니다.

⚠️ v1과 문법 차이가 크므로 외부 자료를 참고할 때는 버전 확인이 필요합니다.

가상환경 구성은 [저장소 루트의 가상환경 준비 항목](../README.md#가상환경-준비)을 참고합니다.

## day4_pydantic01.py — BaseModel과 자동 타입 변환

```python
from pydantic import BaseModel

# 1. 기본: 데이터 검증과 타입 변환

class User(BaseModel):
    name: str
    age: int
    email: str


user = User(
    name="Alice",
    age="25",
    email="alice@example.com",
)

print(user)
print(user.age)
print(type(user.age))
```

실행 결과

```text
name='Alice' age=25 email='alice@example.com'
25
<class 'int'>
```

### 자동 타입 변환

문자열 `"25"`를 전달했지만 `user.age`는 정수 `25`입니다.

Pydantic이 타입 힌트를 기준으로 검사와 변환(coercion)을 함께 수행한 결과입니다.

```text
입력 "25"   → int 힌트 확인 → 변환 가능    → 25로 저장
입력 "abc"  → int 힌트 확인 → 변환 불가능  → ValidationError
```

### 일반 클래스와의 차이

```python
# ❌ 일반 클래스 — 아무 검사도 하지 않음
class User:
    def __init__(self, name: str, age: int):
        self.name = name
        self.age = age

u = User(name="Alice", age="스물다섯")
print(u.age)   # '스물다섯' — 그대로 저장됨
```

```python
# ✅ Pydantic 모델 — 잘못된 값을 즉시 차단
class User(BaseModel):
    name: str
    age: int

u = User(name="Alice", age="스물다섯")   # ValidationError 발생
```

| 항목              | 일반 클래스 | `BaseModel`          |
| ----------------- | ----------- | -------------------- |
| `__init__`        | 직접 작성   | 자동 생성            |
| `self.x = x` 반복 | 필요        | 불필요               |
| 타입 검사         | 없음        | 있음                 |
| 타입 변환         | 없음        | 있음 (`"25"` → `25`) |
| 잘못된 값         | 그대로 통과 | `ValidationError`    |
| JSON 변환         | 직접 구현   | `model_dump_json()`  |

`class User(BaseModel):`의 괄호는 상속 문법입니다.

[02_class](../02_class/README.md)에서 다룬 클래스 개념이 그대로 적용됩니다.

### 변환 규칙

Pydantic v2의 기본 동작은 lax 모드로, 합리적으로 변환 가능한 값만 변환합니다.

| 입력     | 힌트   | 결과                                                |
| -------- | ------ | --------------------------------------------------- |
| `"25"`   | `int`  | `25`                                                |
| `25.0`   | `int`  | `25`                                                |
| `"25.7"` | `int`  | `ValidationError` (소수점 손실)                     |
| `"abc"`  | `int`  | `ValidationError`                                   |
| `"true"` | `bool` | `True`                                              |
| `25`     | `str`  | `ValidationError` (숫자에서 문자로는 변환하지 않음) |

변환 자체를 허용하지 않으려면 `model_config = ConfigDict(strict=True)`로 strict 모드를 사용합니다.

### ValidationError

```python
from pydantic import ValidationError

try:
    User(name="Alice", age="스물다섯", email="a@b.com")
except ValidationError as e:
    print(e)
```

```text
1 validation error for User
age
  Input should be a valid integer, unable to parse string as an integer
    [type=int_parsing, input_value='스물다섯', input_type=str]
```

어떤 필드에서, 어떤 이유로, 어떤 입력값 때문에 실패했는지가 모두 포함됩니다.

FastAPI는 이 정보를 HTTP 422 응답으로 그대로 전달합니다.

## day4_pydantic02.py — Field, Optional, 중첩 모델

```python
# 2. 실전: 기본값, Optional, 중첩 모델

from pydantic import BaseModel, Field

class Address(BaseModel):
    city: str
    zip_code: str

class User(BaseModel):
    name: str
    age: int = Field(ge=0, le=150)
    email: str
    address: Address
    nickname: str | None = None

user = User(
    name="Alice",
    age=25,
    email="alice@example.com",
    address={
        "city": "Daejeon",
        "zip_code": "34100",
    },
)

print(user)
print(user.address.city)
print(user.nickname)
```

실행 결과

```text
name='Alice' age=25 email='alice@example.com' address=Address(city='Daejeon', zip_code='34100') nickname=None
Daejeon
None
```

### Field — 타입만으로 표현할 수 없는 제약

`int`는 정수라는 사실만 보장합니다.

0 이상 150 이하와 같은 범위 조건은 `Field`로 지정합니다.

```python
age: int = Field(ge=0, le=150)
#                 │      └ less than or equal    → age <= 150
#                 └ greater than or equal        → age >= 0
```

| 옵션                       | 의미                  | 적용 대상      |
| -------------------------- | --------------------- | -------------- |
| `gt`, `ge`                 | 초과, 이상            | 숫자           |
| `lt`, `le`                 | 미만, 이하            | 숫자           |
| `min_length`, `max_length` | 최소 길이, 최대 길이  | 문자열, 리스트 |
| `pattern`                  | 정규식 일치           | 문자열         |
| `default`                  | 기본값                | 전체           |
| `description`              | 설명, API 문서에 노출 | 전체           |

```python
User(name="Bob", age=200, ...)
# ValidationError: Input should be less than or equal to 150
```

이 선언이 없다면 `if not (0 <= age <= 150): raise ValueError(...)`를 직접 작성해야 합니다.

### `str | None` — 선택 필드

```python
nickname: str | None = None
#            │         └ 기본값
#            └ 타입: 문자열 또는 None
```

타입과 기본값은 서로 다른 역할을 하며, 둘 다 있어야 완전한 선택 필드가 됩니다.

| 선언                           | 값을 생략하면       | `None`을 전달하면 |
| ------------------------------ | ------------------- | ----------------- |
| `nickname: str`                | 필수 필드 누락 오류 | 타입 오류         |
| `nickname: str = "익명"`       | `"익명"`            | 타입 오류         |
| `nickname: str \| None`        | 필수 필드 누락 오류 | `None`            |
| `nickname: str \| None = None` | `None`              | `None`            |

⚠️ 세 번째 행이 자주 오해되는 지점입니다. `| None`은 생략 가능이라는 뜻이 아니라 None도 허용되는 타입이라는 의미입니다.

생략까지 허용하려면 `= None` 기본값이 필요합니다.

`str | None`은 이전 문법인 `Optional[str]`과 같습니다. Python 3.10 이상에서는 `| None` 표기가 권장됩니다.

### 중첩 모델

```python
address: Address   # 타입 자리에 다른 Pydantic 모델을 지정
```

dict를 전달하면 해당 모델 객체로 변환되며, 내부 필드도 함께 검증됩니다.

```python
address={"city": "Daejeon", "zip_code": "34100"}   # 입력은 dict
user.address        # Address(city='Daejeon', zip_code='34100')
user.address.city   # 'Daejeon'
```

변환 이후에는 dict가 아니므로 점 표기로 접근합니다.

```python
user.address["city"]   # ❌ TypeError
user.address.city      # ✅ 정상
```

중첩된 필드가 누락되면 경로와 함께 오류가 보고됩니다.

```python
User(..., address={"city": "Daejeon"})
# ValidationError: address.zip_code — Field required
```

실제 API가 주고받는 JSON은 대부분 중첩 구조입니다.

```json
{
  "name": "Alice",
  "age": 25,
  "address": { "city": "Daejeon", "zip_code": "34100" },
  "orders": [
    { "id": 1, "amount": 15000 },
    { "id": 2, "amount": 8900 }
  ]
}
```

```python
class Order(BaseModel):
    id: int
    amount: int

class User(BaseModel):
    name: str
    age: int
    address: Address
    orders: list[Order] = []
```

이 구조를 직접 검증하려면 상당한 분량의 조건문이 필요하지만, Pydantic에서는 모델 정의만으로 처리됩니다.

## day4_pydantic03.py — API 요청 모델링

```python
# 3. API 요청 → 검증 → 데이터 변환

from pydantic import BaseModel, Field


class SignupRequest(BaseModel):
    username: str = Field(min_length=3, max_length=20)
    password: str = Field(min_length=8)
    age: int = Field(ge=14)


def signup(data: SignupRequest):
    print("회원가입 처리")
    print(f"username: {data.username}")
    print(f"age: {data.age}")


request = SignupRequest(
    username="alice",
    password="12345678",
    age=25,
)

signup(request)
```

실행 결과

```text
회원가입 처리
username: alice
age: 25
```

### 검증과 비즈니스 로직의 분리

```text
외부 입력(JSON)  →  SignupRequest  →  signup()
신뢰할 수 없음      검증 관문           비즈니스 로직
                   통과하지 못하면      값이 유효하다는
                   여기서 차단          전제로 시작
```

💡 `signup()` 함수 안에는 검증 코드가 없습니다.

`data: SignupRequest`라는 타입 선언 자체가, 전달된 데이터가 이미 검증을 통과했음을 보장하기 때문입니다.

Pydantic을 쓰지 않았다면 다음과 같은 형태가 됩니다.

```python
def signup(username, password, age):
    if not isinstance(username, str):
        raise TypeError("username은 문자열이어야 합니다")
    if len(username) < 3 or len(username) > 20:
        raise ValueError("username은 3~20자여야 합니다")
    if not isinstance(password, str) or len(password) < 8:
        raise ValueError("password는 8자 이상이어야 합니다")
    if not isinstance(age, int) or age < 14:
        raise ValueError("만 14세 이상만 가입 가능합니다")

    print("회원가입 처리")
```

12줄의 검증 코드가 3줄의 모델 정의로 대체되고, 함수는 본래의 역할만 수행합니다.

### 검증 규칙의 근거

| 필드       | 제약     | 근거                                                    |
| ---------- | -------- | ------------------------------------------------------- |
| `username` | 3~20자   | 너무 짧으면 식별이 어렵고, 너무 길면 UI와 저장소에 부담 |
| `password` | 8자 이상 | 보안 정책 최소 기준                                     |
| `age`      | 14 이상  | 국내 온라인 서비스 가입 연령 기준                       |

### model_dump와 model_dump_json

검증을 마친 모델은 dict나 JSON 문자열로 변환할 수 있습니다.

```python
request.model_dump()
# {'username': 'alice', 'password': '12345678', 'age': 25}

request.model_dump_json()
# '{"username":"alice","password":"12345678","age":25}'
```

| 메서드                             | 반환   | 용도                          |
| ---------------------------------- | ------ | ----------------------------- |
| `model_dump()`                     | `dict` | 저장소 기록, 다른 함수로 전달 |
| `model_dump_json()`                | `str`  | HTTP 응답, 파일 저장, 로그    |
| `model_dump(exclude={"password"})` | `dict` | 민감 정보를 제외하고 내보내기 |
| `Model.model_validate(dict)`       | 모델   | dict를 모델로 변환            |
| `Model.model_validate_json(str)`   | 모델   | JSON 문자열을 모델로 변환     |

```python
request.model_dump(exclude={"password"})
# {'username': 'alice', 'age': 25}
```

⚠️ v1의 `.dict()`와 `.json()`은 v2에서 `model_dump()`와 `model_dump_json()`으로 변경되었습니다.

## 전체 정리

| 단계 | 파일                 | 학습 내용                    | 핵심                   |
| ---- | -------------------- | ---------------------------- | ---------------------- |
| 1    | `day4_pydantic01.py` | `BaseModel`                  | 타입 검증과 자동 변환  |
| 2    | `day4_pydantic02.py` | `Field`, Optional, 중첩 모델 | 복잡한 데이터 검증     |
| 3    | `day4_pydantic03.py` | API 데이터 모델링            | 실무에서의 검증과 변환 |

앞선 폴더와의 연결은 다음과 같습니다.

```text
01  name: str = "..."       타입 힌트 — 검사되지 않음
    if not x: raise ...     검증을 직접 작성

02  class TextService:      클래스로 상태와 동작을 묶음
                                 │ 상속
04  class User(BaseModel): ──────┘
      name: str             동일한 타입 힌트가 검증 규칙으로 동작
```

## 이후 과목에서의 활용

FastAPI에서는 Pydantic 모델이 곧 요청과 응답 스키마입니다.

```python
@app.post("/signup")
def signup(request: SignupRequest):
    return {"username": request.username}
```

- 요청 JSON이 자동으로 모델로 변환되고 검증됩니다.
- 검증에 실패하면 HTTP 422와 상세 오류가 자동으로 응답됩니다.
- `/docs` 경로에 API 문서가 자동 생성됩니다.

LangChain과 LLM 에이전트에서는 모델 출력을 정해진 구조로 강제하는 데 사용됩니다.

```python
class Answer(BaseModel):
    summary: str
    confidence: float = Field(ge=0, le=1)
    sources: list[str]
```

에이전트의 Tool 입력 스키마도 Pydantic 모델로 정의됩니다.

따라서 이 폴더의 내용은 3주차 LLM 오케스트레이션과 5주차 AI 에이전트 과목의 전제 지식에 해당합니다.

## 자주 발생하는 오류

| 원인                            | 증상                         | 해결                                        |
| ------------------------------- | ---------------------------- | ------------------------------------------- |
| `nickname: str \| None`만 선언  | 값을 생략하면 Field required | `= None` 기본값 추가                        |
| `user.address["city"]` 접근     | `TypeError`                  | `user.address.city`                         |
| v1 문법 `.dict()` 사용          | `AttributeError`             | `model_dump()`                              |
| `Field` import 누락             | `NameError`                  | `from pydantic import BaseModel, Field`     |
| 필수 필드를 선택 필드 뒤에 선언 | 가독성 저하                  | 필수 필드를 앞쪽에 배치                     |
| 형식 검증을 보안 처리로 오인    | —                            | Pydantic은 형식 검증이며 인증과 권한은 별도 |

## 점검 항목

- [ ] `age: int`에 `"25"`를 전달했을 때의 결과 — `25`로 변환
- [ ] `age: int`에 `"abc"`를 전달했을 때의 결과 — `ValidationError`
- [ ] `nickname: str | None`만 선언하고 값을 생략했을 때의 결과
- [ ] `Field(ge=0, le=150)`이 의미하는 범위
- [ ] `address: Address`에 dict를 전달했을 때의 동작
- [ ] `model_dump()`와 `model_dump_json()`의 차이
- [ ] `signup()` 함수 안에 검증 코드가 없는 이유

## 다음 단계

- Pydantic 모델을 API 엔드포인트에 연결 (AI 서비스 백엔드 프로그래밍 실무 후반, FastAPI)
- [01_python-basic](../01_python-basic/README.md)의 `day2_list.py`를 Pydantic 모델로 다시 작성해 보면 수동 검증과 선언적 검증의 차이가 분명해집니다.
