# 01. Python 기초 문법

AI 서비스 백엔드에서 반복적으로 등장하는 입력 처리 패턴을 Python 기본 문법으로 구현하는 단계입니다.

| 항목        | 내용                                          |
| ----------- | --------------------------------------------- |
| 과목        | AI 서비스 백엔드 프로그래밍 실무              |
| 실습일      | Day 1–2 (9/2 수, 9/3 목)                      |
| 키워드      | 타입 힌트, 조건문, list/dict, 함수, 예외 처리 |
| 필요 패키지 | 없음 (표준 라이브러리만 사용)                 |

## 파일 구성

| 파일                                       | 주제                       | 핵심 문법                                     |
| ------------------------------------------ | -------------------------- | --------------------------------------------- |
| [`day1_value_type.py`](day1_value_type.py) | 변수와 타입 힌트           | `변수: 타입 = 값`, `type()`                   |
| [`day1_condition.py`](day1_condition.py)   | 반복문과 조건으로 걸러내기 | `for`, `strip()`, `continue`, `append()`      |
| [`day1_list_dict.py`](day1_list_dict.py)   | list와 dict로 응답 구성    | `list`, `dict`, `len()`, `print(end=)`        |
| [`day2_func_try.py`](day2_func_try.py)     | 함수화와 예외 처리         | `def`, 기본값 인자, `raise`, `try/except`     |
| [`day2_list.py`](day2_list.py)             | 여러 건 일괄 처리          | `enumerate()`, 중첩 타입 힌트, 부분 실패 처리 |

## day1_value_type.py — 변수와 타입 힌트

```python
service_name: str = "summary-api"
max_length: int = 100
temperature: float = 0.2
is_enabled: bool = True

print(type(service_name), type(max_length))
```

실행 결과

```text
<class 'str'> <class 'int'>
```

### 선언 형식

```text
service_name : str = "summary-api"
     │         │          │
   변수명    타입 힌트    값
```

| 타입    | 의미    | 예시            | 백엔드에서의 용도                |
| ------- | ------- | --------------- | -------------------------------- |
| `str`   | 문자열  | `"summary-api"` | 서비스명, 사용자 질문, 모델 이름 |
| `int`   | 정수    | `100`           | 최대 길이, 토큰 수, 재시도 횟수  |
| `float` | 실수    | `0.2`           | LLM temperature, 유사도 점수     |
| `bool`  | 참/거짓 | `True`, `False` | 기능 활성화 플래그               |

### ⚠️ 타입 힌트는 강제되지 않는다

```python
max_length: int = "백"   # 오류 없이 실행됨
print(type(max_length))  # <class 'str'>
```

Python의 타입 힌트는 사람과 개발 도구를 위한 표시입니다.

실행 시점에 값을 검사하지 않으므로, 선언과 다른 타입을 넣어도 그대로 통과합니다.

💡 이 한계가 [04_pydantic](../04_pydantic/README.md)이 필요한 이유입니다. Pydantic은 동일한 형태의 타입 힌트를 실제 검증 규칙으로 동작하게 만듭니다.

### type()과 isinstance()

```python
type(max_length)             # <class 'int'>  타입을 확인할 때
isinstance(max_length, int)  # True           조건문에서 판단할 때
```

조건문에서는 상속 관계까지 고려하는 `isinstance()`를 사용하는 편이 안전합니다.

## day1_condition.py — 반복문으로 걸러내기

```python
questions = ["asyncio란?", "", "FastAPI란?"]
valid_questions: list[str] = []

for question in questions:
    cleaned = question.strip()
    if not cleaned:
        continue

    valid_questions.append(cleaned)

print(valid_questions)
```

실행 결과

```text
['asyncio란?', 'FastAPI란?']
```

### 동작 흐름

| 회차 | `question`     | `cleaned`      | `not cleaned` | 처리                |
| ---- | -------------- | -------------- | ------------- | ------------------- |
| 1    | `"asyncio란?"` | `"asyncio란?"` | `False`       | 목록에 추가         |
| 2    | `""`           | `""`           | `True`        | `continue`로 건너뜀 |
| 3    | `"FastAPI란?"` | `"FastAPI란?"` | `False`       | 목록에 추가         |

### strip() — 양쪽 공백 제거

문자열 양쪽 끝의 공백, 탭, 줄바꿈을 제거합니다. 가운데 공백은 유지됩니다.

```python
"  안녕  ".strip()   # '안녕'
"\n하이\t".strip()   # '하이'
"안 녕".strip()      # '안 녕'
```

| 메서드             | 동작                           |
| ------------------ | ------------------------------ |
| `strip()`          | 양쪽 끝 제거                   |
| `lstrip()`         | 왼쪽 끝만 제거                 |
| `rstrip()`         | 오른쪽 끝만 제거               |
| `replace(" ", "")` | 가운데를 포함한 모든 공백 제거 |

사용자 입력에는 공백이 섞여 들어오는 경우가 많습니다.

검증 전 `strip()` 처리는 사실상 기본 절차입니다.

### not cleaned — 빈 값 판단

Python은 비어 있는 값을 모두 거짓으로 취급합니다.

| Falsy (거짓 취급)      | Truthy (참 취급)         |
| ---------------------- | ------------------------ |
| `""`, `[]`, `{}`, `()` | `"a"`, `[0]`, `{"k": 1}` |
| `0`, `0.0`             | `1`, `-1`, `0.1`         |
| `None`, `False`        | `True`                   |

⚠️ 공백만 있는 문자열 `"   "`은 Truthy입니다. `strip()`을 먼저 적용해야 걸러집니다.

```python
if not "   ":            # ❌ False — 걸러지지 않음
if not "   ".strip():    # ✅ True  — 걸러짐
```

### continue와 break

| 키워드     | 동작                                       |
| ---------- | ------------------------------------------ |
| `continue` | 현재 회차만 건너뛰고 다음 회차를 계속 진행 |
| `break`    | 반복문 자체를 즉시 종료                    |

빈 질문 하나 때문에 뒤따르는 항목까지 버려서는 안 되므로, 이 코드에서는 `continue`가 적절합니다.

## day1_list_dict.py — 응답 데이터 구성

```python
requests = ["첫 번째 질문", "두 번째 질문"]

response = {
    "status": "success",
    "count": len(requests),
    "items": requests,
}

print(response["count"], end="개")
```

실행 결과

```text
2개
```

### list와 dict

| 구분 | list                         | dict                           |
| ---- | ---------------------------- | ------------------------------ |
| 표기 | `[a, b, c]`                  | `{"키": 값}`                   |
| 접근 | 순서(인덱스) — `requests[0]` | 이름(키) — `response["count"]` |
| 용도 | 여러 개를 담을 때            | 구조를 표현할 때               |

### dict와 JSON의 대응

```python
response = {"status": "success", "count": 2, "items": [...]}
```

```json
{ "status": "success", "count": 2, "items": ["첫 번째 질문", "두 번째 질문"] }
```

API 응답은 결국 이 형태입니다.

따라서 dict를 설계하는 일은 백엔드 응답을 설계하는 일과 거의 같습니다.

`status`, `count`, `items` 조합은 실무 응답 스키마에서 자주 쓰이는 패턴입니다.

### 관련 문법

```python
len(requests)              # 2 — 요소 개수
response["count"]          # 2 — 없는 키를 조회하면 KeyError
response.get("count", 0)   # 2 — 없는 키면 기본값 반환

print("2", end="개")       # 줄바꿈 대신 "개"를 출력 → 2개
print("2")                 # end 기본값은 "\n"
```

## day2_func_try.py — 함수와 예외 처리

```python
def normalize_question(question: str, max_length: int = 100) -> str:
    cleaned = question.strip()

    if not cleaned:
        raise ValueError("질문을 입력하세요.")

    return cleaned[:max_length]


try:
    result = normalize_question("  Python이란?  ")
    print(result)
except ValueError as error:
    print("입력 오류:", error)
```

실행 결과

```text
Python이란?
```

### 함수 시그니처

```text
def normalize_question(question: str, max_length: int = 100) -> str:
    │        │              │     │        │        │    │      │
   정의    함수명        매개변수  타입   매개변수  타입 기본값  반환 타입
```

- `question` — 필수 인자. 전달하지 않으면 `TypeError`가 발생합니다.
- `max_length: int = 100` — 선택 인자. 전달하지 않으면 `100`이 사용됩니다.
- `-> str` — 문자열을 반환한다는 표시이며, 타입 힌트이므로 강제되지는 않습니다.

```python
normalize_question("안녕")                 # max_length = 100
normalize_question("안녕", 20)             # 위치 인자로 전달
normalize_question("안녕", max_length=20)  # ✅ 키워드 인자로 전달
```

키워드 인자는 호출부만 봐도 값의 의미가 드러나므로 가독성 면에서 유리합니다.

### raise — 의도적인 예외 발생

`raise`는 현재 함수가 처리할 수 없는 상황임을 호출자에게 알리는 신호입니다.

```python
# ❌ 실패를 호출자가 알 수 없음
if not cleaned:
    return ""

# ✅ 실패를 명확하게 전달
if not cleaned:
    raise ValueError("질문을 입력하세요.")
```

| 예외         | 사용 상황                                             |
| ------------ | ----------------------------------------------------- |
| `ValueError` | 타입은 맞지만 값이 잘못된 경우 (빈 문자열, 음수 나이) |
| `TypeError`  | 타입 자체가 잘못된 경우                               |
| `KeyError`   | dict에 없는 키를 조회한 경우                          |
| `IndexError` | list 범위를 벗어난 인덱스를 조회한 경우               |

### try / except — 예외 처리

```python
try:
    result = normalize_question("  Python이란?  ")
    print(result)
except ValueError as error:
    print("입력 오류:", error)
```

예외를 처리하지 않으면 프로그램이 그 지점에서 종료됩니다.

서버는 요청 하나의 실패로 전체가 중단되어서는 안 되므로, 예외 처리는 백엔드 코드의 기본 요건입니다.

| 블록      | 실행 시점                             |
| --------- | ------------------------------------- |
| `try`     | 항상 먼저 실행                        |
| `except`  | `try` 안에서 해당 예외가 발생했을 때  |
| `else`    | 예외가 발생하지 않았을 때 (선택)      |
| `finally` | 예외 발생 여부와 무관하게 항상 (선택) |

⚠️ `except:` 또는 `except Exception:`처럼 모든 예외를 한꺼번에 잡으면 실제 버그가 드러나지 않습니다. 처리할 예외를 명시하는 편이 좋습니다.

### 슬라이싱

```python
"안녕하세요"[:3]   # '안녕하'
"안녕"[:100]      # '안녕' — 범위를 넘겨도 오류 없이 전체 반환
```

범위를 초과해도 예외가 발생하지 않는 점이 슬라이싱의 장점입니다.

## day2_list.py — 여러 건 일괄 처리

앞선 파일이 한 건을 처리했다면, 이 파일은 여러 건을 처리하면서 일부만 실패하는 상황을 다룹니다.

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

실행 결과

```text
{'id': '1', 'question': 'Pydantic이란?', 'status': 'ready'}
{'id': '2', 'question': '',             'status': 'invalid'}
{'id': '3', 'question': 'FastAPI란?',   'status': 'ready'}
```

### 부분 실패 처리

입력 세 건 중 두 번째만 실패했습니다. 이때 선택할 수 있는 전략은 두 가지입니다.

| 전략                                         | 결과                         | 채택 |
| -------------------------------------------- | ---------------------------- | ---- |
| 하나라도 실패하면 전체 중단                  | 정상 처리된 두 건까지 버려짐 | ❌   |
| 실패한 항목만 `invalid`로 표시하고 계속 진행 | 세 건 모두 결과가 생성됨     | ✅   |

💡 핵심은 `try/except`를 for 루프 **안**에 둔 것입니다.

```python
# ✅ 루프 안 — 한 건이 실패해도 나머지를 계속 처리
for q in questions:
    try: ...
    except ValueError: ...

# ❌ 루프 밖 — 한 건이 실패하면 전체 반복이 중단
try:
    for q in questions: ...
except ValueError: ...
```

### enumerate() — 인덱스와 값을 함께 순회

```python
for index, question in enumerate(questions, start=1):
    #  1        "Pydantic이란?"
    #  2        " "
    #  3        "FastAPI란?"
```

| 표기                            | 시작 번호                   |
| ------------------------------- | --------------------------- |
| `enumerate(questions)`          | `0` (기본값)                |
| `enumerate(questions, start=1)` | `1` — 사람이 읽는 ID에 적합 |

카운터 변수를 직접 선언하고 증가시킬 필요가 없습니다.

### 중첩 타입 힌트

```python
def build_responses(questions: list[str]) -> list[dict[str, str]]:
```

| 표기                   | 의미                             |
| ---------------------- | -------------------------------- |
| `list[str]`            | 문자열을 담은 리스트             |
| `dict[str, str]`       | 키와 값이 모두 문자열인 딕셔너리 |
| `list[dict[str, str]]` | 그런 딕셔너리를 담은 리스트      |

반환값의 형태는 다음과 같습니다.

```python
[{"id": "1", ...}, {"id": "2", ...}, {"id": "3", ...}]
```

`"id": str(index)`처럼 숫자를 문자열로 변환한 것은 `dict[str, str]` 타입 힌트를 맞추기 위해서입니다.

실무에서는 `id`를 정수로 두고 `dict[str, str | int]`를 쓰거나, Pydantic 모델로 정의하는 방식을 사용합니다.

## 점검 항목

- [ ] `max_length: int = 100`에 문자열을 넣으면 오류가 발생하는가 — 발생하지 않음
- [ ] `"   "`을 `if not question:`으로 걸러낼 수 있는가 — 불가능. `strip()`이 선행되어야 함
- [ ] `continue`와 `break`의 차이
- [ ] `raise`가 `return ""`보다 나은 이유
- [ ] `try/except`를 for 루프 안에 두는 것과 밖에 두는 것의 차이
- [ ] `list[dict[str, str]]`이 나타내는 자료 구조

## 다음 단계

- 흩어진 함수와 반복되는 설정값을 하나로 묶기 → [02_class](../02_class/README.md)
- 직접 작성하던 검증 로직을 선언적으로 대체하기 → [04_pydantic](../04_pydantic/README.md)
