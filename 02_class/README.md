# 02. 클래스

데이터(상태)와 동작(함수)을 하나의 단위로 묶는 방법을 다루는 단계입니다.

| 항목        | 내용                                                |
| ----------- | --------------------------------------------------- |
| 과목        | AI 서비스 백엔드 프로그래밍 실무                    |
| 실습일      | Day 3 (9/4 금)                                      |
| 키워드      | `class`, `__init__`, `self`, 인스턴스, 메서드, 상태 |
| 필요 패키지 | 없음 (표준 라이브러리만 사용)                       |

## 파일 구성

| 파일                             | 주제                               |
| -------------------------------- | ---------------------------------- |
| [`day3_class.py`](day3_class.py) | 텍스트 요약 서비스를 클래스로 구현 |

## day3_class.py — TextService

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

실행 결과

```text
클래스는 데이터와 동작을 함께 관리합
```

원문은 마침표를 포함해 23자이고 `max_length`가 20이므로 앞에서 20자만 남습니다.

Python 문자열 슬라이싱은 유니코드 문자 단위로 동작하므로, 한글도 한 글자가 1로 계산됩니다.

## 함수 방식과의 비교

동일한 로직을 두 방식으로 작성해 나란히 놓으면 클래스를 쓰는 이유가 드러납니다.

함수 방식 — [`day2_func_try.py`](../01_python-basic/day2_func_try.py)

```python
def normalize_question(question: str, max_length: int = 100) -> str:
    cleaned = question.strip()
    if not cleaned:
        raise ValueError("질문을 입력하세요.")
    return cleaned[:max_length]

normalize_question("첫 번째", 20)
normalize_question("두 번째", 20)   # 설정값을 매번 반복 전달
normalize_question("세 번째", 20)   # ⚠️ 누락하면 기본값 100이 조용히 적용됨
```

클래스 방식 — `day3_class.py`

```python
service = TextService(max_length=20)   # 설정은 생성 시 한 번

service.summarize("첫 번째")
service.summarize("두 번째")           # 설정값은 객체가 보관
service.summarize("세 번째")
```

| 비교 항목                  | 함수                    | 클래스                  |
| -------------------------- | ----------------------- | ----------------------- |
| 설정값 전달                | 호출할 때마다           | 생성 시 한 번           |
| 설정 누락 위험             | 있음                    | 구조적으로 방지         |
| 설정이 여러 개일 때        | 인자 목록이 계속 늘어남 | 속성으로 정리됨         |
| 서로 다른 설정의 동시 운용 | 어려움                  | 인스턴스를 여러 개 생성 |

```python
short_service = TextService(max_length=20)    # 요약용
long_service = TextService(max_length=500)    # 원문 보존용
```

두 객체는 각자의 `max_length`를 독립적으로 유지합니다.

💡 정리하면 함수는 동작을 담고, 클래스는 동작과 그 동작이 기억해야 할 값을 함께 담습니다.

## 문법 구조

```text
class TextService:                                     ① 클래스 정의
    def __init__(self, max_length: int = 100) -> None: ② 생성자
        self.max_length = max_length                   ③ 인스턴스 속성 저장

    def summarize(self, text: str) -> str:             ④ 메서드
        ...
        return cleaned[: self.max_length]              ⑤ 저장된 값 사용


service = TextService(max_length=20)                   ⑥ 인스턴스 생성
print(service.summarize("..."))                        ⑦ 메서드 호출
```

### class — 설계도 정의

`class TextService:`는 설계도이며 실제 객체가 아닙니다.

붕어빵 틀이 클래스라면, 구워져 나온 붕어빵이 인스턴스에 해당합니다.

| 용어     | 의미                   | 이 코드에서       |
| -------- | ---------------------- | ----------------- |
| 클래스   | 설계도                 | `TextService`     |
| 인스턴스 | 설계도로 만든 객체     | `service`         |
| 속성     | 인스턴스가 가진 데이터 | `self.max_length` |
| 메서드   | 인스턴스가 가진 동작   | `summarize()`     |

클래스명은 관례적으로 PascalCase(`TextService`), 함수와 변수는 snake_case(`max_length`)를 사용합니다.

### `__init__` — 생성자

`TextService(max_length=20)`을 실행하는 시점에 자동으로 호출됩니다. 직접 호출하지 않습니다.

```python
service = TextService(max_length=20)
#         __init__(self, max_length=20)이 자동 실행됨
```

- 이름 앞뒤의 밑줄 두 개는 Python이 특별하게 취급하는 이름이라는 표시입니다.
- 역할은 인스턴스의 초기 상태를 설정하는 것입니다.
- 값을 반환하지 않으므로 반환 타입은 `None`입니다.

### self — 인스턴스 자신

메서드 호출은 내부적으로 다음과 같이 변환됩니다.

```python
service.summarize("텍스트")
# 실제 실행 형태
TextService.summarize(service, "텍스트")
#                     └ self에 해당
```

| 상황               | 규칙                                        |
| ------------------ | ------------------------------------------- |
| 메서드를 정의할 때 | 첫 번째 매개변수로 `self`를 명시            |
| 메서드를 호출할 때 | `self`는 전달하지 않음 (Python이 자동 전달) |
| 이름               | 관례상 `self`를 사용                        |

`self.`를 붙이는지 여부에 따라 값의 수명이 달라집니다.

```python
def __init__(self, max_length: int = 100) -> None:
    self.max_length = max_length
    #      │              └ 지역 변수 — 함수 종료와 함께 사라짐
    #      └ 인스턴스 속성 — 객체에 저장되어 다른 메서드에서도 접근 가능
```

⚠️ `self.`를 누락하면 값이 저장되지 않아, `summarize()` 호출 시 `AttributeError`가 발생합니다.

### 메서드

메서드는 클래스 안에 정의된 함수입니다.

`self`를 통해 객체의 상태에 접근할 수 있다는 점이 일반 함수와 다릅니다.

```python
def summarize(self, text: str) -> str:
    cleaned = text.strip()
    if not cleaned:
        raise ValueError("본문을 입력하세요.")
    return cleaned[: self.max_length]
```

내부 로직은 `day2_func_try.py`와 동일합니다.

`max_length`를 인자에서 가져오는지 인스턴스 속성에서 가져오는지만 다릅니다.

## 백엔드에서 클래스를 사용하는 이유

실제 AI 서비스에서는 설정 항목이 여러 개로 늘어납니다.

```python
# ❌ 함수 방식 — 인자 목록이 계속 길어짐
def summarize(text, max_length, model, api_key, temperature, timeout, retry): ...

# ✅ 클래스 방식 — 설정은 생성 시 한 번, 호출부는 간결하게 유지
class SummaryService:
    def __init__(self, api_key: str, model: str = "claude-sonnet-5",
                 max_length: int = 100, temperature: float = 0.2) -> None:
        self.api_key = api_key
        self.model = model
        self.max_length = max_length
        self.temperature = temperature

    def summarize(self, text: str) -> str: ...
    def translate(self, text: str) -> str: ...

service = SummaryService(api_key="sk-...")
service.summarize("...")
service.translate("...")
```

이 구조는 이후 과정에서 반복적으로 등장합니다.

- **FastAPI** — 라우터와 의존성 주입에서 서비스 객체를 주입해 사용합니다.
- **Pydantic** — `BaseModel`을 상속한 클래스로 데이터 스키마를 정의합니다.
- **LangChain 및 에이전트** — Chain, Tool, Agent가 모두 클래스로 구성됩니다.

## 자주 발생하는 오류

| 원인                             | 증상                                                                  | 해결                              |
| -------------------------------- | --------------------------------------------------------------------- | --------------------------------- |
| `self.` 누락                     | `AttributeError: 'TextService' object has no attribute 'max_length'`  | `self.max_length = max_length`    |
| 메서드에 `self` 미선언           | `TypeError: summarize() takes 1 positional argument but 2 were given` | `def summarize(self, text)`       |
| `__init__` 철자 오류 (`__int__`) | 생성자가 실행되지 않음                                                | `init`은 initialize의 약자        |
| 인스턴스 없이 호출               | `TextService.summarize("...")` 실패                                   | `service = TextService()` 후 호출 |
| 클래스 속성에 가변 기본값        | 모든 인스턴스가 같은 객체를 공유                                      | `__init__` 안에서 초기화          |

```python
# ❌ 모든 인스턴스가 같은 리스트를 공유
class Bad:
    items = []

# ✅ 인스턴스마다 별도의 리스트 생성
class Good:
    def __init__(self):
        self.items = []
```

## 점검 항목

- [ ] 클래스와 인스턴스의 차이
- [ ] `__init__`이 호출되는 시점 — 인스턴스를 생성하는 순간 자동 호출
- [ ] `self.max_length`와 `max_length`의 차이
- [ ] `service.summarize("텍스트")`에서 `self`가 가리키는 대상 — `service` 객체
- [ ] 같은 로직에서 함수 대신 클래스를 선택했을 때 얻는 이점

## 다음 단계

- 배열 데이터를 대량으로 계산하기 → [03_numpy](../03_numpy/README.md)
- 클래스를 상속해 데이터 검증 모델 정의하기 → [04_pydantic](../04_pydantic/README.md)

`class User(BaseModel):`이 여기서 다룬 클래스 문법입니다.
