# 02. 클래스 (Class)

> **과목** AI 서비스 백엔드 프로그래밍 실무 · **실습일** Day3 (9/4 금)
> **키워드** `class` · `__init__` · `self` · 인스턴스 · 메서드 · 상태(state)

---

## 이 폴더에서 배우는 것

**"데이터(상태) + 동작(함수)"을 하나의 덩어리로 묶는 방법**입니다.

[`01_python-basic`](../01_python-basic/README.md)에서는 `normalize_question(question, max_length)` 처럼
**필요한 값을 매번 인자로 넘겼습니다.** 클래스는 그 값을 객체가 **기억하게** 만듭니다.

| 파일 | 한 줄 요약 |
|---|---|
| [`day3_class.py`](day3_class.py) | 텍스트 요약 서비스를 클래스로 구현 |

---

## `day3_class.py` — TextService

```python
class TextService:
    def __init__(self, max_length: int = 100) -> None:
        self.max_length = max_length

    def summarize(self, text: str) -> str:
        cleaned = text.strip()
        if not cleaned:
            raise ValueError("본문을 입력하세요.")
        return cleaned[: self.max_length]


service = TextService(max_length=20)
print(service.summarize("클래스는 데이터와 동작을 함께 관리합니다."))
```

**실행 결과**
```
클래스는 데이터와 동작을 함께 관리합
```

> 원문은 마침표 포함 23자입니다. `max_length=20`이므로 앞에서 20자만 잘려
> `"클래스는 데이터와 동작을 함께 관리합"` 까지 나옵니다. (파이썬 문자열 슬라이싱은 한글도 1글자 = 1)

---

## 1. 함수 버전과 무엇이 달라졌나

이게 이 파일의 전부입니다. **같은 로직을 두 방식으로 쓴 것**을 나란히 보면 클래스의 존재 이유가 보입니다.

**① 함수 버전 (`day2_func_try.py`)**
```python
def normalize_question(question: str, max_length: int = 100) -> str:
    cleaned = question.strip()
    if not cleaned:
        raise ValueError("질문을 입력하세요.")
    return cleaned[:max_length]

normalize_question("첫 번째", 20)
normalize_question("두 번째", 20)   # 20을 매번 반복해서 넘겨야 함
normalize_question("세 번째", 20)   # 하나라도 빠뜨리면 조용히 100이 됨 💥
```

**② 클래스 버전 (`day3_class.py`)**
```python
service = TextService(max_length=20)   # 설정을 딱 한 번만

service.summarize("첫 번째")
service.summarize("두 번째")           # max_length는 객체가 기억함
service.summarize("세 번째")
```

| 비교 항목 | 함수 | 클래스 |
|---|---|---|
| 설정값(`max_length`) | **호출할 때마다** 전달 | 생성 시 **한 번만** 전달, 이후 기억 |
| 설정 실수 | 빠뜨리기 쉬움 | 구조적으로 방지 |
| 설정이 여러 개일 때 | 인자가 계속 늘어남 | 속성으로 정리됨 |
| 여러 설정 동시 운용 | 어려움 | `short`, `long` 두 객체를 따로 만들면 끝 |

```python
short_service = TextService(max_length=20)   # 요약용
long_service  = TextService(max_length=500)  # 원문 보존용
# 두 객체가 각자의 max_length를 독립적으로 갖는다
```

> **한 줄 정리** — 함수는 "행동", 클래스는 "행동 + 그 행동이 기억해야 할 것".

---

## 2. 클래스 문법 뜯어보기

```
class TextService:                                    ← ① 설계도 정의
    def __init__(self, max_length: int = 100) -> None: ← ② 생성자
        self.max_length = max_length                   ← ③ 인스턴스 속성 저장

    def summarize(self, text: str) -> str:             ← ④ 메서드
        ...
        return cleaned[: self.max_length]              ← ⑤ 저장된 값 사용


service = TextService(max_length=20)                   ← ⑥ 인스턴스 생성
print(service.summarize("..."))                        ← ⑦ 메서드 호출
```

### ① `class` — 설계도

`class TextService:` 는 아직 **설계도**일 뿐, 실제 물건이 아닙니다.
붕어빵 **틀**이 클래스, 구워져 나온 **붕어빵**이 인스턴스입니다.

| 용어 | 의미 | 이 코드에서 |
|---|---|---|
| 클래스 (class) | 설계도 | `TextService` |
| 인스턴스 (instance) | 설계도로 만든 실체 | `service` |
| 속성 (attribute) | 인스턴스가 가진 **데이터** | `self.max_length` |
| 메서드 (method) | 인스턴스가 가진 **동작** | `summarize()` |

> 클래스명은 관례적으로 **PascalCase** (`TextService`), 함수·변수는 **snake_case** (`max_length`).

### ② `__init__` — 생성자

`TextService(max_length=20)` 이라고 쓰는 **순간 자동으로** 호출됩니다. 직접 부르지 않습니다.

```python
service = TextService(max_length=20)
#         └── 여기서 __init__(self, max_length=20)이 자동 실행
```

- 이름 앞뒤의 `__`(던더)는 **파이썬이 특별 취급하는 이름**이라는 표시입니다.
- 하는 일은 **초기 상태를 세팅**하는 것뿐입니다.
- `-> None` — 생성자는 값을 반환하지 않으므로 반환 타입이 `None`입니다.

### ③ `self` — 자기 자신

가장 헷갈리는 부분이지만 규칙은 단순합니다.

```python
service.summarize("텍스트")
# ↓ 파이썬이 내부적으로 이렇게 바꿔서 실행
TextService.summarize(service, "텍스트")
#                     └─ 이게 self
```

| 규칙 | 내용 |
|---|---|
| 정의할 때 | 첫 번째 매개변수로 `self`를 **반드시 적는다** |
| 호출할 때 | `self`는 **적지 않는다** (파이썬이 자동으로 넣어줌) |
| 이름 | `self`는 관례일 뿐이지만 **바꾸지 마세요** |

**`self.` 를 붙이는 것과 안 붙이는 것의 차이**

```python
def __init__(self, max_length: int = 100) -> None:
    self.max_length = max_length
    #      │              └── 지역 변수 (이 함수 안에서만 살아있음, 곧 사라짐)
    #      └── 인스턴스 속성 (객체에 저장, 다른 메서드에서도 접근 가능)
```

`self.`를 빼먹으면 값이 저장되지 않아서 `summarize()`에서 `AttributeError`가 납니다. 초보자가 가장 자주 하는 실수입니다.

### ④ 메서드

메서드는 **클래스 안에 정의된 함수**입니다. 함수와 다른 점은 `self`를 통해 **객체의 상태에 접근할 수 있다**는 것뿐입니다.

```python
def summarize(self, text: str) -> str:
    cleaned = text.strip()
    if not cleaned:
        raise ValueError("본문을 입력하세요.")
    return cleaned[: self.max_length]   # ← self로 생성 시 저장한 값 사용
```

내부 로직(`strip` → 빈 값 검사 → `raise` → 슬라이싱)은 [`day2_func_try.py`](../01_python-basic/day2_func_try.py)와 **완전히 동일**합니다.
바뀐 것은 `max_length`를 **어디서 가져오는가** 하나뿐입니다.

---

## 3. 왜 백엔드에서 클래스를 쓰는가

실제 AI 서비스에서는 설정이 하나가 아니라 열 개씩 됩니다.

```python
# 함수로 하면… 인자가 끝없이 늘어난다 😵
def summarize(text, max_length, model, api_key, temperature, timeout, retry): ...

# 클래스로 하면 설정은 생성할 때 한 번, 호출은 간결하게 ✅
class SummaryService:
    def __init__(self, api_key: str, model: str = "claude-sonnet-5",
                 max_length: int = 100, temperature: float = 0.2) -> None:
        self.api_key = api_key
        self.model = model
        self.max_length = max_length
        self.temperature = temperature

    def summarize(self, text: str) -> str: ...
    def translate(self, text: str) -> str: ...   # 같은 설정을 공유하는 동작 추가

service = SummaryService(api_key="sk-...")
service.summarize("...")
service.translate("...")
```

이 구조가 앞으로 배울 내용의 뼈대가 됩니다.

- **FastAPI** — 라우터·의존성 주입에서 서비스 객체를 주입해서 씁니다
- **Pydantic** — `BaseModel`을 **상속**받은 클래스로 데이터 스키마를 정의합니다
- **LangChain / 에이전트** — Chain, Tool, Agent 전부 클래스입니다

---

## 4. 자주 하는 실수

| 실수 | 증상 | 해결 |
|---|---|---|
| `self.` 빼먹고 저장 | `AttributeError: 'TextService' object has no attribute 'max_length'` | `self.max_length = max_length` |
| 메서드에 `self` 안 씀 | `TypeError: summarize() takes 1 positional argument but 2 were given` | `def summarize(self, text)` |
| `__init__` 오타 (`__int__`) | 생성자가 아예 실행 안 됨 | 철자 확인 (`init` = initialize) |
| 인스턴스 없이 호출 | `TextService.summarize("...")` → 에러 | 먼저 `service = TextService()` |
| 클래스 속성에 리스트 기본값 | 모든 인스턴스가 리스트를 **공유**해버림 | `__init__` 안에서 `self.items = []` |

```python
# ❌ 위험 — 모든 인스턴스가 같은 리스트를 공유
class Bad:
    items = []

# ✅ 안전 — 인스턴스마다 새 리스트
class Good:
    def __init__(self):
        self.items = []
```

---

## 체크리스트

- [ ] 클래스와 인스턴스의 차이를 붕어빵으로 설명할 수 있는가?
- [ ] `__init__`은 언제 호출되는가? → **인스턴스를 만드는 순간, 자동으로**
- [ ] `self.max_length`와 `max_length`의 차이는?
- [ ] `service.summarize("텍스트")`에서 `self`는 무엇인가? → **`service` 객체 자신**
- [ ] 같은 로직인데 함수 대신 클래스를 쓰면 뭐가 좋아지는가?

---

## 다음 단계

- 배열 데이터를 빠르게 계산한다 → [**03_numpy**](../03_numpy/README.md)
- 클래스를 **상속**해서 데이터 검증 모델을 만든다 → [**04_pydantic**](../04_pydantic/README.md)
  (`class User(BaseModel):` ← 이 문법이 여기서 배운 클래스입니다)
