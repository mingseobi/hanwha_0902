# 01. Python 기초 문법

> **과목** AI 서비스 백엔드 프로그래밍 실무 · **실습일** Day1~2 (9/2 수 ~ 9/3 목)
> **키워드** 타입 힌트 · 조건문 · list/dict · 함수 · 예외 처리

---

## 이 폴더에서 배우는 것

AI 서비스 백엔드가 하는 일을 아주 단순하게 줄이면 이렇습니다.

```
사용자 질문(문자열)  →  다듬기  →  유효한지 판단  →  응답 형태로 포장  →  반환
```

이 폴더의 5개 파일은 정확히 그 4단계를 하나씩 쪼개서 연습합니다.
그래서 예제 소재가 전부 "질문(question)"과 "응답(response)"입니다 — 나중에 FastAPI에서 다룰 요청/응답과 같은 소재입니다.

| 파일 | 한 줄 요약 | 핵심 문법 |
|---|---|---|
| [`day1_value_type.py`](day1_value_type.py) | 변수와 타입 힌트 | `변수: 타입 = 값`, `type()` |
| [`day1_condition.py`](day1_condition.py) | 반복문 + 조건으로 걸러내기 | `for`, `strip()`, `continue`, `append()` |
| [`day1_list_dict.py`](day1_list_dict.py) | list와 dict로 응답 만들기 | `list`, `dict`, `len()`, `print(end=)` |
| [`day2_func_try.py`](day2_func_try.py) | 함수로 묶고 예외로 방어하기 | `def`, 기본값 인자, `raise`, `try/except` |
| [`day2_list.py`](day2_list.py) | 여러 건을 일괄 처리하기 | `enumerate()`, 중첩 타입 힌트, 부분 실패 처리 |

---

## 1. `day1_value_type.py` — 변수와 타입 힌트

```python
service_name: str = "summary-api"
max_length: int = 100
temperature: float = 0.2
is_enabled: bool = True

print(type(service_name), type(max_length))
```

**실행 결과**
```
<class 'str'> <class 'int'>
```

### 문법 정리

```
service_name : str = "summary-api"
     │         │          │
   변수명    타입 힌트    실제 값
```

| 타입 | 의미 | 예시 | 백엔드에서 쓰이는 곳 |
|---|---|---|---|
| `str` | 문자열 | `"summary-api"` | 서비스명, 사용자 질문, 모델 이름 |
| `int` | 정수 | `100` | 최대 길이, 토큰 수, 재시도 횟수 |
| `float` | 실수 | `0.2` | LLM temperature, 유사도 점수 |
| `bool` | 참/거짓 | `True` / `False` | 기능 on/off 플래그 |

### ⚠️ 가장 중요한 포인트 — 타입 힌트는 강제되지 않는다

```python
max_length: int = "백"   # 에러가 안 남! 그냥 실행됨
print(type(max_length))  # <class 'str'>
```

파이썬의 타입 힌트는 **사람과 도구(IDE, 린터)를 위한 표시**일 뿐, 실행 시점에 값을 검사하지 않습니다.

> 💡 이게 바로 [`04_pydantic`](../04_pydantic/README.md)이 존재하는 이유입니다.
> Pydantic은 **똑같이 생긴 타입 힌트를 실제 검증 규칙으로 바꿔 주는** 라이브러리입니다.
> 그래서 이 파일 → Pydantic 파일 순서로 보면 "왜 필요한지"가 바로 이해됩니다.

### `type()` vs `isinstance()`

```python
type(max_length)                  # <class 'int'>   ← 타입을 "확인"할 때
isinstance(max_length, int)       # True            ← 조건문에서 "판단"할 때 (권장)
```

---

## 2. `day1_condition.py` — 반복문으로 걸러내기

```python
questions = ["asyncio란?", "", "FastAPI란?"]
valid_questions: list[str] = []

for question in questions:
    cleaned = question.strip()
    if not cleaned:
        continue            # 빈 문자열이면 건너뛰기

    valid_questions.append(cleaned)

print(valid_questions)
```

**실행 결과**
```
['asyncio란?', 'FastAPI란?']
```

### 동작 흐름

| 회차 | `question` | `cleaned` | `not cleaned` | 결과 |
|---|---|---|---|---|
| 1 | `"asyncio란?"` | `"asyncio란?"` | `False` | ✅ 추가 |
| 2 | `""` | `""` | `True` | ⏭️ `continue` — 건너뜀 |
| 3 | `"FastAPI란?"` | `"FastAPI란?"` | `False` | ✅ 추가 |

### 핵심 문법 3가지

**① `strip()` — 양쪽 공백 제거**

문자열 **양쪽 끝**의 공백·탭·줄바꿈을 제거합니다. 가운데 공백은 건드리지 않습니다.

```python
"  안녕  ".strip()     # '안녕'
"\n하이\t".strip()     # '하이'
"안 녕".strip()        # '안 녕'  ← 가운데는 그대로
```

| 메서드 | 동작 |
|---|---|
| `strip()` | 양쪽 끝 제거 |
| `lstrip()` | 왼쪽만 제거 |
| `rstrip()` | 오른쪽만 제거 |
| `replace(" ", "")` | 모든 공백 제거 (가운데 포함) |

> 사용자 입력은 **거의 항상 공백이 섞여 들어옵니다.** 검증 전 `strip()`은 사실상 기본 절차입니다.

**② `not cleaned` — 빈 값 판단 (Falsy)**

파이썬은 "비어 있는 것"을 전부 `False`로 취급합니다.

```python
if not cleaned:   # cleaned가 "" 이면 True
```

| Falsy (거짓 취급) | Truthy (참 취급) |
|---|---|
| `""` `[]` `{}` `()` | `"a"` `[0]` `{"k":1}` |
| `0` `0.0` | `1` `-1` `0.1` |
| `None` `False` | `True` |

⚠️ `"   "` (공백만 있는 문자열)은 **Truthy**입니다. 그래서 `strip()`을 **먼저** 해야 걸러집니다.

```python
if not "   ":            # False → 안 걸러짐 ❌
if not "   ".strip():    # True  → 걸러짐   ✅
```

**③ `continue` vs `break`**

| 키워드 | 동작 |
|---|---|
| `continue` | 이번 회차만 건너뛰고 **다음 회차 계속** |
| `break` | 반복문 자체를 **즉시 종료** |

이 코드는 빈 질문 하나 때문에 뒤의 `"FastAPI란?"`까지 버리면 안 되므로 `continue`가 맞습니다.

---

## 3. `day1_list_dict.py` — 응답 데이터 만들기

```python
requests = ["첫 번째 질문", "두 번째 질문"]

response = {
    "status": "success",
    "count": len(requests),
    "items": requests,
}

print(response["count"], end="개")
```

**실행 결과**
```
2개
```

### list vs dict

| | list | dict |
|---|---|---|
| 표기 | `[a, b, c]` | `{"키": 값}` |
| 접근 | 순서(인덱스) — `requests[0]` | 이름(키) — `response["count"]` |
| 쓰임 | **여러 개**를 담을 때 | **구조**를 표현할 때 |

### 이 dict가 곧 JSON

```python
response = {"status": "success", "count": 2, "items": [...]}
```
```json
{ "status": "success", "count": 2, "items": ["첫 번째 질문", "두 번째 질문"] }
```

API 응답은 결국 이 형태입니다. **dict를 잘 만드는 게 백엔드 응답을 잘 만드는 것**과 거의 같습니다.
`status` / `count` / `items` 3종 세트는 실무 응답 스키마의 전형적인 패턴입니다.

### 알아둘 것

```python
len(requests)              # 2 — 요소 개수
response["count"]          # 2 — 없는 키면 KeyError 발생 💥
response.get("count", 0)   # 2 — 없는 키면 기본값 0 반환 (안전) ✅

print("2", end="개")       # 줄바꿈 대신 "개"를 붙임 → "2개"
print("2")                 # 기본값은 end="\n" (줄바꿈)
```

---

## 4. `day2_func_try.py` — 함수 + 예외 처리

```python
def normalize_question(question: str, max_length: int = 100) -> str:
    cleaned = question.strip()

    if not cleaned:
        raise ValueError("질문을 입력하세요.")   # 의도적으로 에러 발생

    return cleaned[:max_length]


try:
    result = normalize_question("  Python이란?  ")
    print(result)
except ValueError as error:
    print("입력 오류:", error)
```

**실행 결과**
```
Python이란?
```

### 함수 시그니처 뜯어보기

```
def normalize_question(question: str, max_length: int = 100) -> str:
    │        │              │    │        │        │    │       │
   정의    함수명        매개변수 타입   매개변수  타입  기본값  반환 타입
```

- `question` — **필수** 인자. 안 넘기면 `TypeError`
- `max_length: int = 100` — **선택** 인자. 안 넘기면 자동으로 `100`
- `-> str` — 이 함수는 문자열을 돌려준다는 표시 (역시 강제되지는 않음)

```python
normalize_question("안녕")                    # max_length = 100 (기본값)
normalize_question("안녕", 20)                # 위치로 전달
normalize_question("안녕", max_length=20)     # 이름으로 전달 (읽기 좋음, 권장)
```

### `raise` — 에러를 "일부러" 발생시키기

`raise`는 **"이건 내가 처리할 수 없는 상황이다"** 라고 호출한 쪽에 알리는 신호입니다.

```python
# ❌ 이러면 호출한 쪽이 실패를 알 수 없다
if not cleaned:
    return ""

# ✅ 실패를 명확하게 전달
if not cleaned:
    raise ValueError("질문을 입력하세요.")
```

| 예외 | 언제 쓰나 |
|---|---|
| `ValueError` | 타입은 맞는데 **값이 잘못됨** (빈 문자열, 음수 나이) |
| `TypeError` | **타입 자체**가 잘못됨 (str 자리에 int) |
| `KeyError` | dict에 **없는 키**를 조회 |
| `IndexError` | list 범위 밖 인덱스 |

### `try / except` — 에러를 "붙잡기"

```python
try:
    result = normalize_question("  Python이란?  ")   # 위험할 수 있는 코드
    print(result)
except ValueError as error:                          # ValueError가 나면 여기로
    print("입력 오류:", error)                        # error에 메시지가 담겨 있음
```

`try/except`가 없으면 프로그램이 그 자리에서 **죽습니다.**
서버는 요청 하나가 잘못됐다고 전체가 멈추면 안 되므로, 예외 처리는 백엔드의 필수 습관입니다.

| 블록 | 실행 시점 |
|---|---|
| `try` | 항상 먼저 실행 |
| `except` | `try` 안에서 해당 에러가 났을 때만 |
| `else` | 에러가 **안 났을** 때만 (선택) |
| `finally` | 에러 여부와 무관하게 **항상** (선택 — 파일 닫기, 연결 해제 등) |

⚠️ `except:` 또는 `except Exception:` 처럼 **모든 에러를 뭉뚱그려 잡는 건 피하세요.** 진짜 버그가 숨어버립니다.

### 슬라이싱 `[:max_length]`

```python
"안녕하세요"[:3]      # '안녕하'
"안녕"[:100]         # '안녕'  ← 길이를 넘겨도 에러 없이 전체 반환 (안전)
```

문자열/리스트를 자를 때 범위를 넘어도 에러가 나지 않는 것이 슬라이싱의 장점입니다.

---

## 5. `day2_list.py` — 여러 건 일괄 처리

`day2_func_try.py`가 **한 건**을 처리했다면, 이 파일은 **여러 건**을 처리하면서 **일부만 실패**하는 현실적인 상황을 다룹니다.

```python
def normalize_question(question: str, max_length: int = 100) -> str:
    cleaned = question.strip()
    if not cleaned:
        raise ValueError("질문을 입력하세요.")
    return cleaned[:max_length]


def build_responses(questions: list[str]) -> list[dict[str, str]]:
    responses = []
    for index, question in enumerate(questions, start=1):
        try:
            cleaned = normalize_question(question)
            responses.append({"id": str(index), "question": cleaned, "status": "ready"})
        except ValueError:
            responses.append({"id": str(index), "question": "", "status": "invalid"})
    return responses


items = build_responses(["Pydantic이란?", " ", "FastAPI란?"])
for item in items:
    print(item)
```

**실행 결과**
```
{'id': '1', 'question': 'Pydantic이란?', 'status': 'ready'}
{'id': '2', 'question': '',             'status': 'invalid'}
{'id': '3', 'question': 'FastAPI란?',   'status': 'ready'}
```

### 이 코드의 설계 포인트 — 부분 실패(partial failure)

입력 3건 중 2번째만 실패했습니다. 이때 선택지는 두 가지입니다.

| 전략 | 결과 | 이 코드의 선택 |
|---|---|---|
| 하나라도 실패하면 전체 중단 | 정상 2건도 버려짐 | ❌ |
| 실패한 것만 `invalid`로 표시하고 계속 | **3건 모두 결과가 나옴** | ✅ |

`try/except`를 **for 루프 안**에 둔 것이 핵심입니다. 밖에 두면 2번째에서 루프 전체가 끝나버립니다.

```python
# ✅ 루프 안 — 한 건 실패해도 나머지 계속
for q in questions:
    try: ...
    except ValueError: ...

# ❌ 루프 밖 — 한 건 실패하면 전체 중단
try:
    for q in questions: ...
except ValueError: ...
```

### `enumerate()` — 인덱스와 값을 함께 꺼내기

```python
for index, question in enumerate(questions, start=1):
    #  1        "Pydantic이란?"
    #  2        " "
    #  3        "FastAPI란?"
```

| 코드 | 시작 번호 |
|---|---|
| `enumerate(questions)` | `0` (기본값) |
| `enumerate(questions, start=1)` | `1` — 사람이 읽는 ID로 적합 |

번거롭게 `i = 0` / `i += 1`을 직접 관리하지 않아도 됩니다.

### 중첩 타입 힌트 읽는 법

```python
def build_responses(questions: list[str]) -> list[dict[str, str]]:
```

| 표기 | 의미 |
|---|---|
| `list[str]` | 문자열이 들어있는 리스트 |
| `dict[str, str]` | 키도 문자열, 값도 문자열인 딕셔너리 |
| `list[dict[str, str]]` | **그런 딕셔너리들이 들어있는 리스트** |

즉 반환값은 이런 모양입니다.
```python
[ {"id": "1", ...}, {"id": "2", ...}, {"id": "3", ...} ]
```

> 참고: `"id": str(index)` 처럼 숫자를 문자열로 바꾼 이유는 `dict[str, str]`이라는 타입 힌트를 지키기 위해서입니다.
> 실무에서는 보통 `id`를 정수로 두고 `dict[str, str | int]`로 쓰거나, **Pydantic 모델**로 만듭니다.

---

## 체크리스트

읽고 넘어가기 전에 스스로 답해 보세요.

- [ ] `max_length: int = 100`에 문자열을 넣으면 에러가 날까? → **안 남 (타입 힌트는 강제 X)**
- [ ] `"   "`을 `if not question:`으로 걸러낼 수 있을까? → **없음 (strip() 먼저 필요)**
- [ ] `continue`와 `break`의 차이는?
- [ ] `raise`는 왜 `return ""`보다 나은가?
- [ ] `try/except`를 for 루프 **안**에 넣는 것과 **밖**에 넣는 것의 차이는?
- [ ] `list[dict[str, str]]`을 말로 풀어 설명할 수 있는가?

---

## 다음 단계

- 흩어진 함수 + 반복되는 `max_length`를 하나로 묶는다 → [**02_class**](../02_class/README.md)
- 손으로 짜던 `if not cleaned: raise ...` 검증을 자동화한다 → [**04_pydantic**](../04_pydantic/README.md)
