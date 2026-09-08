# 04. Pydantic

> **과목** AI 서비스 백엔드 프로그래밍 실무 · **실습일** Day4 (9/7 월)
> **키워드** `BaseModel` · 자동 타입 변환 · `Field` · Optional · 중첩 모델 · `ValidationError`
>
> 📌 **이 문서가 04_pydantic의 메인 정리본입니다.**
> [`pydantic_note.md`](pydantic_note.md) 는 수업 중 직접 작성한 원본 메모로, 기록 보존용으로만 남겨두었습니다.
> (원래 파일명 `pydantic.md` → `pydantic_note.md` 로 변경)

---

## 이 폴더에서 배우는 것

**타입 힌트를 진짜 검증 규칙으로 만드는 라이브러리**입니다.

[`01_python-basic`](../01_python-basic/README.md)에서 확인한 문제로 돌아가 봅시다.

```python
age: int = "25"       # 파이썬: 아무 말 없이 통과 😐
```

타입 힌트는 검사되지 않으므로, 지금까지는 검증을 **손으로** 짰습니다.

```python
if not cleaned:
    raise ValueError("질문을 입력하세요.")
```

필드가 10개면 이런 `if`문이 10개, 20개가 됩니다. **Pydantic은 이 전부를 타입 힌트 한 줄로 대체합니다.**

| 파일 | 단계 | 배우는 것 |
|---|---|---|
| [`day4_pydantic01.py`](day4_pydantic01.py) | 1단계 | `BaseModel` — 타입 검증과 자동 변환 |
| [`day4_pydantic02.py`](day4_pydantic02.py) | 2단계 | `Field`, `\| None`, 중첩 모델 — 복잡한 데이터 검증 |
| [`day4_pydantic03.py`](day4_pydantic03.py) | 3단계 | API 요청 모델링 — 실무 검증 + 변환 |
| [`pydantic_note.md`](pydantic_note.md) | — | 수업 중 작성한 원본 메모 (참고용) |

---

## 사전 준비

```bash
pip install pydantic
```

가상환경 세팅은 [루트 README의 «실행 환경»](../README.md#6-실행-환경) 을 참고하세요.

이 문서는 **Pydantic v2** 기준입니다. v1과 문법이 꽤 다르니 구글 검색 시 버전을 꼭 확인하세요.

```python
import pydantic; print(pydantic.VERSION)   # 2.x 이면 OK
```

---

## 1. `day4_pydantic01.py` — BaseModel과 자동 타입 변환

```python
from pydantic import BaseModel

class User(BaseModel):
    name: str
    age: int
    email: str


user = User(
    name="Alice",
    age="25",              # ← 문자열로 넣었는데?
    email="alice@example.com",
)

print(user)
print(user.age)
print(type(user.age))
```

**실행 결과**
```
name='Alice' age=25 email='alice@example.com'
25
<class 'int'>
```

### 핵심 — `"25"`가 `25`로 바뀌었다

문자열 `"25"`를 넣었는데 `user.age`는 **정수 `25`** 입니다.
Pydantic이 타입 힌트를 보고 **검사 + 변환(coercion)** 을 자동으로 수행한 결과입니다.

```
입력 "25"  →  [Pydantic]  int 힌트 확인  →  변환 가능? → 예  →  25 저장
입력 "abc" →  [Pydantic]  int 힌트 확인  →  변환 가능? → 아니오 → ValidationError 💥
```

### 일반 클래스와의 결정적 차이

```python
# 일반 클래스 (02_class에서 배운 것)
class User:
    def __init__(self, name: str, age: int):
        self.name = name
        self.age = age          # 아무 검사도 안 함

u = User(name="Alice", age="스물다섯")
print(u.age)                     # '스물다섯' — 그대로 들어감 😱
```

```python
# Pydantic 모델
class User(BaseModel):
    name: str
    age: int

u = User(name="Alice", age="스물다섯")   # 💥 ValidationError 즉시 발생
```

| | 일반 클래스 | Pydantic `BaseModel` |
|---|---|---|
| `__init__` | 직접 작성 | **자동 생성** |
| `self.x = x` 반복 | 필요 | 불필요 |
| 타입 검사 | 안 함 | **함** |
| 타입 변환 | 안 함 | **함** (`"25"` → `25`) |
| 잘못된 값 | 조용히 통과 | `ValidationError` |
| JSON 변환 | 직접 구현 | `model_dump_json()` |

> `class User(BaseModel):` 의 괄호는 **상속** 문법입니다. [`02_class`](../02_class/README.md)에서 배운 클래스를,
> Pydantic이 만들어 둔 `BaseModel`로부터 기능을 물려받아 정의하는 것입니다.

### 변환 규칙 — 되는 것과 안 되는 것

Pydantic v2의 기본 모드는 **lax(느슨) 모드**로, "합리적으로 변환 가능하면 변환"합니다.

| 입력 | 힌트 | 결과 |
|---|---|---|
| `"25"` | `int` | ✅ `25` |
| `25.0` | `int` | ✅ `25` |
| `"25.7"` | `int` | ❌ `ValidationError` (소수점 손실) |
| `"abc"` | `int` | ❌ `ValidationError` |
| `"true"` | `bool` | ✅ `True` |
| `25` | `str` | ❌ `ValidationError` (숫자→문자는 안 해줌) |

> 변환을 아예 원하지 않으면 `model_config = ConfigDict(strict=True)` 로 **strict 모드**를 켤 수 있습니다.

### ValidationError 읽는 법

```python
from pydantic import ValidationError

try:
    User(name="Alice", age="스물다섯", email="a@b.com")
except ValidationError as e:
    print(e)
```
```
1 validation error for User
age
  Input should be a valid integer, unable to parse string as an integer
    [type=int_parsing, input_value='스물다섯', input_type=str]
```

에러 메시지가 **어느 필드(`age`)가 / 왜(`int_parsing`) / 무슨 값(`'스물다섯'`)때문에** 실패했는지 전부 알려줍니다.
직접 짠 `raise ValueError("질문을 입력하세요.")` 보다 훨씬 친절합니다. FastAPI는 이 정보를 그대로 HTTP 422 응답으로 내보냅니다.

---

## 2. `day4_pydantic02.py` — Field, Optional, 중첩 모델

```python
from pydantic import BaseModel, Field

class Address(BaseModel):
    city: str
    zip_code: str

class User(BaseModel):
    name: str
    age: int = Field(ge=0, le=150)      # 범위 제약
    email: str
    address: Address                     # 중첩 모델
    nickname: str | None = None          # 선택 필드

user = User(
    name="Alice",
    age=25,
    email="alice@example.com",
    address={                            # dict를 넣었는데?
        "city": "Daejeon",
        "zip_code": "34100",
    },
)

print(user)
print(user.address.city)
print(user.nickname)
```

**실행 결과**
```
name='Alice' age=25 email='alice@example.com' address=Address(city='Daejeon', zip_code='34100') nickname=None
Daejeon
None
```

### ① `Field()` — 타입만으로 부족할 때

`int`는 "정수"라는 것만 보장합니다. **"0 이상 150 이하인 정수"** 같은 조건은 `Field`로 붙입니다.

```python
age: int = Field(ge=0, le=150)
#                 │      └── less than or equal    → age <= 150
#                 └───────── greater than or equal → age >= 0
```

| 옵션 | 의미 | 적용 타입 |
|---|---|---|
| `gt` / `ge` | 초과 / 이상 | 숫자 |
| `lt` / `le` | 미만 / 이하 | 숫자 |
| `min_length` / `max_length` | 최소/최대 길이 | 문자열, 리스트 |
| `pattern` | 정규식 일치 | 문자열 |
| `default` | 기본값 | 전부 |
| `description` | 설명 (API 문서에 노출) | 전부 |

```python
User(name="Bob", age=200, ...)
# 💥 ValidationError: Input should be less than or equal to 150
```

> 이 한 줄이 없었다면 `if not (0 <= age <= 150): raise ValueError(...)` 를 직접 써야 했습니다.

### ② `str | None` — 있어도 되고 없어도 되는 필드

```python
nickname: str | None = None
#            │         └── 기본값 (안 넘기면 None)
#            └── 타입: 문자열이거나 None
```

**두 부분은 서로 다른 이야기**이고, 둘 다 있어야 "완전한 선택 필드"가 됩니다.

| 선언 | 넘기지 않으면 | `None`을 넘기면 |
|---|---|---|
| `nickname: str` | 💥 필수 필드 누락 에러 | 💥 타입 에러 |
| `nickname: str = "익명"` | `"익명"` | 💥 타입 에러 |
| `nickname: str \| None` | 💥 **필수 필드 누락 에러** ⚠️ | `None` |
| `nickname: str \| None = None` | `None` ✅ | `None` ✅ |

⚠️ 셋째 줄이 함정입니다. **`| None`은 "생략 가능"이 아니라 "None도 허용되는 타입"** 이라는 뜻입니다.
생략까지 허용하려면 반드시 `= None` 기본값을 함께 적어야 합니다.

> `str | None`은 예전 문법 `Optional[str]`과 같습니다. Python 3.10+ 에서는 `| None` 표기를 권장합니다.

### ③ 중첩 모델 (Nested Model)

```python
address: Address        # 타입 자리에 다른 Pydantic 모델
```

여기서 진짜 마법이 일어납니다. **`dict`를 넣었는데 `Address` 객체가 나옵니다.**

```python
address={"city": "Daejeon", "zip_code": "34100"}     # 입력: dict
             ↓ Pydantic이 자동 변환 + 내부 필드까지 검증
user.address                    # Address(city='Daejeon', zip_code='34100')
user.address.city               # 'Daejeon'  ← 점(.)으로 접근
```

```python
user.address["city"]     # ❌ TypeError — 더 이상 dict가 아님
user.address.city        # ✅
```

중첩 모델의 내부도 **똑같이 검증**됩니다.

```python
User(..., address={"city": "Daejeon"})     # zip_code 누락
# 💥 ValidationError: address.zip_code — Field required
#                     └── 어느 중첩 필드인지 경로로 알려줌
```

### 왜 중첩이 중요한가 — 실제 API JSON은 항상 중첩

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
    orders: list[Order] = []      # 모델의 리스트도 가능
```

이 정도 구조를 직접 검증하려면 `if`문이 수십 줄 필요합니다. Pydantic은 **모델 정의만으로 끝**입니다.

---

## 3. `day4_pydantic03.py` — API 요청 모델링

```python
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

**실행 결과**
```
회원가입 처리
username: alice
age: 25
```

### 이 코드가 보여주는 것 — 검증과 비즈니스 로직의 분리

```
┌────────────────────┐    ┌───────────────────┐    ┌─────────────────────┐
│  외부 입력 (JSON)   │ →  │  SignupRequest    │ →  │  signup()           │
│  신뢰할 수 없음     │    │  = 검증 관문       │    │  = 비즈니스 로직     │
│                    │    │  통과 못하면 여기서 │    │  "값은 이미 옳다"고  │
│                    │    │  즉시 차단 💥      │    │  믿고 시작 ✅        │
└────────────────────┘    └───────────────────┘    └─────────────────────┘
```

> **Pydantic의 역할은 비즈니스 로직에 들어가기 전에 데이터가 올바른지 검사하는 것** — [`pydantic_note.md`](pydantic_note.md)

`signup()` 함수 안에 검증 코드가 **한 줄도 없다**는 점을 보세요.
`data: SignupRequest` 라는 타입 힌트 하나가 "여기 들어온 데이터는 이미 검증을 통과했다"를 보장합니다.

**Pydantic이 없었다면 `signup()` 은 이랬을 겁니다.**

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

    # ← 진짜 하고 싶은 일은 여기서부터 시작 😩
    print("회원가입 처리")
```

검증 12줄이 **모델 정의 3줄**로 줄었고, 비즈니스 로직은 온전히 자기 일만 합니다.

### 실무 검증 규칙 매핑

| 필드 | 제약 | 현실적 이유 |
|---|---|---|
| `username` | 3~20자 | 너무 짧으면 식별 불가, 너무 길면 UI/DB 문제 |
| `password` | 8자 이상 | 보안 정책 최소 기준 |
| `age` | 14 이상 | 국내 온라인 서비스 가입 연령 기준 |

### `model_dump()` / `model_dump_json()` — 밖으로 내보내기

검증이 끝난 모델은 다시 dict나 JSON으로 꺼낼 수 있습니다.

```python
request.model_dump()
# {'username': 'alice', 'password': '12345678', 'age': 25}      ← Python dict

request.model_dump_json()
# '{"username":"alice","password":"12345678","age":25}'         ← JSON 문자열
```

| 메서드 | 반환 | 언제 쓰나 |
|---|---|---|
| `model_dump()` | `dict` | DB 저장, 다른 함수로 전달 |
| `model_dump_json()` | `str` | HTTP 응답, 파일 저장, 로그 |
| `model_dump(exclude={"password"})` | `dict` | **민감 정보 제외**하고 내보내기 |
| `Model.model_validate(dict)` | 모델 | dict → 모델 (역방향) |
| `Model.model_validate_json(str)` | 모델 | JSON 문자열 → 모델 |

```python
# 응답에 비밀번호를 실어 보내면 안 되므로
request.model_dump(exclude={"password"})
# {'username': 'alice', 'age': 25}
```

> ⚠️ v1의 `.dict()` / `.json()` 은 v2에서 `model_dump()` / `model_dump_json()` 으로 이름이 바뀌었습니다.

---

## 4. 전체 정리

### 3단계 학습 흐름

| 단계 | 파일 | 배운 것 | 핵심 |
|---|---|---|---|
| 1 | `day4_pydantic01.py` | `BaseModel` | 타입 검증 + 자동 변환 |
| 2 | `day4_pydantic02.py` | `Field`, `\| None`, 중첩 모델 | 복잡한 데이터 검증 |
| 3 | `day4_pydantic03.py` | API 데이터 모델링 | 실무에서 검증 + 변환 |

### 지금까지 배운 것과의 연결

```
[01] name: str = "..."      타입 힌트 — 검사 안 됨
     if not x: raise ...    검증을 손으로

[02] class TextService:     클래스로 상태 + 동작 묶기
                                 │  상속
[04] class User(BaseModel): ─────┘
       name: str            같은 타입 힌트가 이제 진짜 검증 규칙으로 작동
```

### 다음 과목에서 이렇게 쓰입니다

**FastAPI** — Pydantic 모델을 그대로 요청/응답 스키마로 사용합니다.

```python
@app.post("/signup")
def signup(request: SignupRequest):     # ← 오늘 만든 모델 그대로
    return {"username": request.username}
```

- 요청 JSON을 자동으로 `SignupRequest`로 변환 + 검증
- 검증 실패 시 **HTTP 422**와 상세 에러를 자동 응답
- `/docs` 에 API 문서를 **자동 생성**

**LangChain / LLM 에이전트** — LLM의 출력을 정해진 구조로 강제할 때 씁니다.

```python
class Answer(BaseModel):
    summary: str
    confidence: float = Field(ge=0, le=1)
    sources: list[str]

# LLM이 뱉은 JSON을 이 모델로 검증 → 형식이 깨지면 즉시 감지
```

에이전트의 **Tool 입력 스키마**도 전부 Pydantic 모델입니다.
즉 이 폴더의 내용은 3주차 LLM 오케스트레이션, 5주차 AI 에이전트 과목의 **전제 지식**입니다.

---

## 자주 하는 실수

| 실수 | 증상 | 해결 |
|---|---|---|
| `nickname: str \| None` 만 씀 | 생략하면 "Field required" | `= None` 기본값 추가 |
| `user.address["city"]` | `TypeError` | `user.address.city` |
| v1 문법 `.dict()` 사용 | `AttributeError` | `model_dump()` |
| `Field` import 누락 | `NameError` | `from pydantic import BaseModel, Field` |
| 필수 필드를 선택 필드 뒤에 선언 | 혼란스러운 코드 | 필수 → 선택 순서로 정렬 |
| 검증을 통과했다고 **보안**까지 된 줄 앎 | — | Pydantic은 **형식** 검증. 인증/권한은 별개 |

---

## 체크리스트

- [ ] `age: int` 에 `"25"`를 넣으면? → **`25`로 자동 변환**
- [ ] `age: int` 에 `"abc"`를 넣으면? → **`ValidationError`**
- [ ] `nickname: str | None` 만 쓰고 값을 생략하면? → **에러 (`= None` 필요)**
- [ ] `Field(ge=0, le=150)` 을 말로 풀면? → **0 이상 150 이하**
- [ ] `address: Address` 에 dict를 넣으면 어떻게 되는가?
- [ ] `model_dump()` 와 `model_dump_json()` 의 차이는?
- [ ] `signup()` 함수 안에 검증 코드가 없는 이유는?

---

## 다음 단계

- [**FastAPI**] Pydantic 모델을 API 엔드포인트에 연결 (`AI 서비스 백엔드 프로그래밍 실무` 후반)
- 처음으로 돌아가 [`01_python-basic`](../01_python-basic/README.md)의 `day2_list.py`를 Pydantic 모델로 바꿔 보면
  "수동 검증 → 선언적 검증"의 차이가 몸으로 느껴집니다.
