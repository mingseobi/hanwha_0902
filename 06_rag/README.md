# 06. LangChain 개념 정리

LLM 호출을 **조립 가능한 부품**으로 다루는 방법에 대한 정리입니다.

| 항목        | 내용                                                            |
| ----------- | --------------------------------------------------------------- |
| 과목        | 실무형 RAG 시스템 구축 및 최적화                                |
| 키워드      | Runnable, LCEL, `PromptTemplate`, 출력 파서, `RunnableParallel` |
| 필요 패키지 | `langchain`, `langchain-openai`, `python-dotenv`                |

## 1. Runnable — 모든 것의 공통 규격

LangChain을 이해하는 출발점입니다. 이걸 알면 나머지가 전부 따라옵니다.

### 무엇인가

`Runnable`은 **"입력을 받아 출력을 내놓는 것"** 에 대한 공통 규격(인터페이스)입니다.

프롬프트도, 모델도, 출력 파서도, 심지어 이들을 이어 붙인 체인 전체도 모두 Runnable입니다. 하는 일은 전혀 다르지만 **부르는 방법이 같습니다.**

```python
prompt.invoke({"topic": "..."})    # 프롬프트 완성
model.invoke(프롬프트)              # 모델 호출
parser.invoke(응답)                 # 결과 정리
chain.invoke({"topic": "..."})     # 위 셋을 한 번에
```

모든 Runnable이 다음 여섯 가지를 보장합니다.

| 메서드                           | 하는 일                      |
| -------------------------------- | ---------------------------- |
| `invoke`                         | 한 건 처리                   |
| `stream`                         | 한 건을 조각으로 나눠 내보냄 |
| `batch`                          | 여러 건 처리                 |
| `ainvoke` / `astream` / `abatch` | 위 셋의 비동기 버전          |

### 왜 이렇게 만들었나

**규격이 같으면 부품을 바꿔 끼울 수 있기 때문**입니다.

전기 콘센트 규격이 통일되어 있어서 어떤 가전이든 꽂을 수 있는 것과 같습니다. 모델을 OpenAI에서 다른 회사 것으로 바꿔도, 출력 파서를 문자열에서 구조화 객체로 바꿔도, **연결 방식은 그대로**입니다.

여기서 나오는 이점이 하나 더 있습니다.

```python
chain = prompt | model | parser
chain.stream(input)    # 체인 전체가 스트리밍을 지원한다
chain.batch(inputs)    # 체인 전체가 배치를 지원한다
```

스트리밍이나 배치를 직접 구현한 적이 없는데도 동작합니다. **각 부품이 규격을 지키므로 조합한 결과물도 자동으로 규격을 갖추기** 때문입니다.

### 체인도 Runnable이다

```python
chain = prompt | model | parser
isinstance(chain, Runnable)    # True
```

이 사실이 실무에서 중요합니다. 완성된 체인을 **다른 체인의 부품으로 다시 쓸 수 있다**는 뜻이기 때문입니다.

```python
bigger_chain = chain | 다음_단계
```

RAG 파이프라인이 이렇게 만들어집니다. 검색 체인과 생성 체인을 각각 완성한 뒤 이어 붙이면 전체가 됩니다.

---

## 2. LCEL — 파이프 연산자

```python
chain = prompt | model | output_parser
```

LangChain에서는 이 표기법을 LCEL(LangChain Expression Language)이라고 부릅니다.

### `|`가 실제로 하는 일

파이썬의 `|`는 원래 비트 OR 연산자입니다. LangChain은 Runnable에 `__or__` 메서드를 정의해 이 기호의 의미를 **"연결"** 로 바꿨습니다.

```python
prompt | model
# 내부적으로 prompt.__or__(model) 이 호출되어 RunnableSequence를 만든다
```

```python
type(prompt | model)          # RunnableSequence
(prompt | model).steps        # [PromptTemplate, ChatOpenAI]
```

`RunnableSequence`는 단계 목록을 들고 있다가, `invoke`가 불리면 **앞에서부터 차례로 실행하며 결과를 다음 단계에 넘깁니다.**

### 왜 파이프로 쓰는가

파이프가 없다면 이렇게 됩니다.

```python
# 중첩 호출 — 데이터는 안쪽에서 바깥쪽으로 흐르는데, 읽기는 바깥쪽부터 하게 된다
result = output_parser.invoke(model.invoke(prompt.invoke(input)))
```

```python
# 파이프 — 데이터가 흐르는 순서와 읽는 순서가 일치한다
result = (prompt | model | output_parser).invoke(input)
```

단계가 셋일 때는 큰 차이가 없어 보이지만, RAG처럼 예닐곱 단계가 되면 중첩 호출은 사실상 읽을 수 없습니다.

### 단계 사이를 흐르는 데이터

각 단계가 무엇을 받아 무엇을 내놓는지 알아야 체인을 조립할 수 있습니다.

```text
{"topic": "..."}          dict                   내가 넣는 값
      ↓  prompt
StringPromptValue         프롬프트 문자열 래퍼      변수가 채워진 상태
      ↓  model
AIMessage                 content + 메타데이터     토큰 수, 종료 이유 등 포함
      ↓  output_parser
str                       순수 문자열              바로 쓸 수 있는 형태
```

⚠️ **연결 규칙은 하나뿐입니다.** 앞 단계의 출력 타입이 뒤 단계가 받을 수 있는 타입이어야 합니다. 체인이 깨질 때는 대부분 이 지점입니다.

### 자동 변환 — dict와 함수도 넣을 수 있다

파이프에는 Runnable이 아닌 것도 넣을 수 있습니다. LangChain이 알아서 Runnable로 감싸 줍니다.

| 넣은 것 | 변환되는 것        | 의미                                |
| ------- | ------------------ | ----------------------------------- |
| 함수    | `RunnableLambda`   | 그 함수를 한 단계로 실행            |
| dict    | `RunnableParallel` | 각 값을 병렬 실행하고 결과를 dict로 |

```python
model | (lambda msg: msg.content.upper())
# 두 번째 단계가 RunnableLambda로 감싸짐
```

```python
{"a": chain1, "b": chain2} | 다음_단계
# dict가 RunnableParallel로 감싸짐
```

💡 **아래 RAG 표준 형태가 이 자동 변환 덕분에 성립합니다.**

```python
{"context": retriever, "question": RunnablePassthrough()} | prompt | model | parser
```

dict를 쓴 것처럼 보이지만 실제로는 `RunnableParallel`이 만들어지고, 그 결과 dict가 `prompt`의 입력 변수로 들어갑니다.

---

## 3. PromptTemplate — 프롬프트를 함수처럼

```python
prompt = PromptTemplate.from_template("{topic} 에 대해 쉽게 설명해주세요.")
```

중괄호 자리가 **입력 변수**가 되고, 호출할 때 dict로 채웁니다.

```python
prompt.input_variables         # ['topic']
prompt.invoke({"topic": "X"})  # StringPromptValue(text='X 에 대해 쉽게 설명해주세요.')
```

### f-string으로 하면 안 되는가

동작 자체는 합니다. 그런데도 `PromptTemplate`을 쓰는 이유가 있습니다.

```python
text = f"{topic} 에 대해 쉽게 설명해주세요."   # 문자열이 만들어지는 순간 값이 확정된다
```

| 항목                 | f-string                       | `PromptTemplate`             |
| -------------------- | ------------------------------ | ---------------------------- |
| 체인 연결            | 불가 — 그냥 문자열             | `\|`로 연결 가능             |
| 어떤 변수가 필요한지 | 알 방법 없음                   | `input_variables`로 확인     |
| 변수 누락            | `NameError` 또는 조용한 오동작 | 실행 시점에 명확한 오류      |
| 일부만 미리 채우기   | 불가                           | `partial()`                  |
| 재사용               | 매번 문자열을 새로 만듦        | 객체 하나를 여러 입력에 사용 |

핵심은 **템플릿과 값의 분리**입니다.

f-string은 "만드는 순간" 완성된 문자열이 되어 버려서, 그 뒤로는 손댈 수 없는 죽은 데이터입니다. `PromptTemplate`은 **아직 값이 채워지지 않은 틀**로 남아 있어서, 체인의 한 단계로 꽂아 두고 값만 바꿔 가며 반복 호출할 수 있습니다.

이 차이가 뒤에서 결정적입니다. `batch`로 여러 입력을 한꺼번에 처리하거나, 검색 결과를 `context` 자리에 밀어 넣는 일은 **틀이 살아 있어야** 가능합니다.

### partial() — 미리 채워 두기

```python
prompt = prompt.partial(format=parser.get_format_instructions())
```

```text
partial 전  input_variables: ['format', 'question']
partial 후  input_variables: ['question']          ← format이 목록에서 빠짐
```

출력 형식 지침처럼 **매번 똑같은 값**은 미리 박아 둡니다. 그러면 호출부에서는 실제로 달라지는 값만 넘기면 됩니다.

```python
chain.invoke({"question": "..."})   # format을 매번 넘길 필요가 없다
```

단순히 타이핑을 줄이는 게 아닙니다. 형식 지침은 **체인을 만드는 사람**이 정하는 것이고 질문은 **체인을 쓰는 사람**이 넣는 것인데, `partial`이 그 경계를 코드로 표현해 줍니다.

---

## 4. 출력 파서 — 모델의 답을 쓸 수 있는 형태로

### 파서란 무엇인가

출력 파서도 Runnable입니다. **모델의 출력을 받아 다른 형태로 바꿔 내놓는 단계**일 뿐입니다.

특별한 개념이 아니라, 체인의 마지막에 놓이는 변환기라고 보면 됩니다.

### StrOutputParser — 가장 단순한 파서

모델은 문자열이 아니라 `AIMessage` 객체를 돌려줍니다.

```python
chain = prompt | model
chain.invoke(input)
# AIMessage(content='...', additional_kwargs={}, response_metadata={...}, tool_calls=[], ...)
```

`AIMessage`에는 본문 말고도 토큰 사용량, 종료 이유, 도구 호출 정보가 함께 들어 있습니다. 필요한 정보지만, 답변 텍스트만 쓰려면 매번 `.content`를 꺼내야 합니다.

```python
chain = prompt | model | StrOutputParser()
chain.invoke(input)
# '...'   순수 문자열
```

| 파서 없음                      | 파서 있음                   |
| ------------------------------ | --------------------------- |
| `AIMessage` 반환               | `str` 반환                  |
| `.content`를 직접 꺼내야 함    | 바로 사용 가능              |
| 추출 코드가 체인 **밖에** 남음 | 추출이 체인 **안에서** 끝남 |

마지막 행이 핵심입니다. `.content`를 체인 밖에서 꺼내면, 그 체인은 "쓰기 전에 손질이 필요한 반제품"이 됩니다. 파서를 넣으면 **체인 하나가 완결된 부품**이 되어 다른 곳에 그대로 꽂을 수 있습니다.

### 왜 구조화 출력이 필요한가

요약문 한 덩어리가 아니라 **필드별로 나뉜 값**이 필요할 때가 있습니다. 보낸 사람, 날짜, 제목을 각각 꺼내 데이터베이스에 넣거나 화면 항목에 뿌려야 하는 경우입니다.

문자열로 받으면 직접 파싱해야 하는데, 모델이 형식을 조금만 바꿔도 깨집니다. 줄바꿈 하나, 콜론 하나 차이로 코드가 실패합니다.

이 문제를 푸는 방식이 두 가지 있고, **작동 원리가 근본적으로 다릅니다.**

---

### 4-1. PydanticOutputParser — 프롬프트에 형식을 적어 주는 방식

```python
class EmailSummary(BaseModel):
    person: str = Field(description="메일을 보낸 사람")
    date: str = Field(description="미팅 날짜와 시간")

parser = PydanticOutputParser(pydantic_object=EmailSummary)
```

#### 전체 흐름

```text
① Pydantic 모델로 원하는 구조를 선언
        ↓
② parser.get_format_instructions() 가 지시문을 자동 생성
        ↓
③ 그 지시문을 프롬프트에 끼워 넣음 (partial)
        ↓
④ 모델이 지시대로 JSON 문자열을 생성
        ↓
⑤ parser.parse() 가 JSON을 Pydantic 객체로 변환
        ↓
⑥ obj.person 처럼 속성으로 접근
```

#### ② 지시문은 스키마에서 자동으로 만들어진다

```python
print(parser.get_format_instructions())
```

```text
The output should be formatted as a JSON instance that conforms to the JSON schema below.
...
Here is the output schema:
{"properties": {"person": {"description": "메일을 보낸 사람", "type": "string"},
                "date": {"description": "미팅 날짜와 시간", "type": "string"}},
 "required": ["person", "date"]}
```

💡 `Field(description=...)`에 적은 설명이 **그대로 모델에게 전달되는 지시**가 됩니다.

이게 `description`을 성의 있게 적어야 하는 이유입니다. 사람이 읽는 주석이 아니라 **모델이 읽는 명세**이기 때문입니다. "날짜"라고만 적는 것과 "미팅 날짜와 시간"이라고 적는 것은 결과가 달라집니다.

#### ③ partial로 지시문을 프롬프트에 고정

```python
prompt = PromptTemplate.from_template("...\nFORMAT:\n{format}")
prompt = prompt.partial(format=parser.get_format_instructions())
```

형식 지침은 호출할 때마다 바뀌지 않으므로 미리 채워 둡니다.

#### ⑤ parse가 하는 일

```python
obj = parser.parse('{"person": "...", "date": "..."}')
obj.person    # 속성으로 접근
```

JSON **문자열**을 받아 Pydantic **객체**로 바꿉니다. 이때 Pydantic의 검증이 함께 걸리므로, 필드가 빠지거나 타입이 맞지 않으면 여기서 오류가 납니다.

#### 체인에 넣으면 한 번에

```python
chain = prompt | llm | parser
response = chain.invoke({...})    # 결과가 바로 EmailSummary 객체
```

파서도 Runnable이므로 그냥 이어 붙이면 됩니다. ④⑤가 자동으로 처리됩니다.

#### ⚠️ 이 방식의 한계

**모델이 지시를 따른다는 전제에 의존합니다.**

지시문은 프롬프트 본문에 들어간 그냥 텍스트입니다. 모델이 앞뒤에 설명을 덧붙이거나, 코드 블록으로 감싸거나, 필드 이름을 살짝 바꾸면 `parse()`가 실패합니다.

작은 모델일수록, 프롬프트가 길수록 실패 확률이 올라갑니다. 지시문 자체도 토큰을 차지해 비용과 지연이 늘어납니다.

---

### 4-2. with_structured_output — 모델에 형식을 강제하는 방식

```python
llm_structured = ChatOpenAI(...).with_structured_output(EmailSummary)
answer = llm_structured.invoke(email_conversation)
```

프롬프트에 지시문을 **넣지 않습니다.** 대신 모델 API가 제공하는 구조화 출력 기능에 스키마를 직접 전달합니다.

모델이 "이 형식으로 답해 주세요"라는 부탁을 받는 게 아니라, **API 수준에서 그 형식 외에는 생성할 수 없게** 됩니다.

|                | `PydanticOutputParser` | `with_structured_output` |
| -------------- | ---------------------- | ------------------------ |
| 형식 전달 경로 | 프롬프트 본문에 글로   | 모델 API 파라미터로      |
| 프롬프트 길이  | 지시문만큼 길어짐      | 그대로                   |
| 형식 준수      | 모델의 성실성에 의존   | API 수준에서 보장        |
| 실패 지점      | `parse()` 에서 터짐    | 거의 없음                |
| 모델 호환성    | 대부분의 모델          | 지원하는 모델만          |

💡 **같은 목적에 두 가지 길이 있고, 모델이 지원하면 후자가 안전합니다.** 지원하지 않는 모델을 쓸 때 전자가 대안이 됩니다.

두 방식을 모두 배우는 이유가 여기 있습니다. 어느 하나가 항상 옳은 게 아니라, **쓰는 모델에 따라 선택**하는 것입니다.

---

### 4-3. 그 밖의 파서

| 파서                             | 반환   | 특징                                  |
| -------------------------------- | ------ | ------------------------------------- |
| `CommaSeparatedListOutputParser` | `list` | 쉼표로 나눠 리스트로                  |
| `StructuredOutputParser`         | `dict` | `ResponseSchema` 목록으로 스키마 정의 |
| `JsonOutputParser`               | `dict` | JSON을 dict로                         |

```python
parser = CommaSeparatedListOutputParser()
parser.get_format_instructions()
# 'Your response should be a list of comma separated values, eg: `foo, bar, baz`'
parser.parse("a, b, c")   # ['a', 'b', 'c']
```

⚠️ 모든 파서가 `get_format_instructions()`와 `parse()`를 가진다는 점에 주목할 만합니다. **파서마다 형식은 달라도 사용 방법은 동일**합니다. Runnable이 그랬듯 여기서도 같은 설계 원칙이 반복됩니다.

`StructuredOutputParser`는 Pydantic 클래스 대신 필드 설명 목록으로 스키마를 정의합니다.

```python
response_schemas = [
    ResponseSchema(name="answer", description="사용자의 질문에 대한 답변"),
    ResponseSchema(name="source", description="답변에 사용된 출처"),
]
```

답변과 근거를 분리해 받는 이 형태는 RAG 응답의 전형입니다. 검색으로 답한 이상 **어느 문서에서 나왔는지** 함께 돌려주어야 사용자가 신뢰할 수 있기 때문입니다.

---

## 5. 실행 방식 — invoke, stream, batch, async

같은 체인을 어떻게 호출하느냐에 따라 동작이 달라집니다.

| 메서드            | 입력    | 반환        | 쓰는 상황                 |
| ----------------- | ------- | ----------- | ------------------------- |
| `invoke(x)`       | 한 건   | 완성된 결과 | 결과 전체가 필요할 때     |
| `stream(x)`       | 한 건   | 조각들      | 사용자에게 즉시 보여줄 때 |
| `batch([x1, x2])` | 여러 건 | 결과 리스트 | 여러 건을 한꺼번에        |
| `ainvoke(x)`      | 한 건   | 코루틴      | 다른 작업과 병행할 때     |

### stream을 쓰는 이유

`invoke`는 모델이 답변을 **끝까지 만들 때까지** 아무것도 돌려주지 않습니다. 긴 답변이면 사용자는 몇 초간 빈 화면을 보게 됩니다.

`stream`은 토큰이 생성되는 대로 내보냅니다. **전체 소요 시간은 같지만** 첫 글자가 훨씬 빨리 보이므로 체감 반응 속도가 완전히 달라집니다.

```python
for token in chain.stream(input):
    print(token, end="", flush=True)
```

| 옵션         | 없으면                                                 |
| ------------ | ------------------------------------------------------ |
| `end=""`     | 토큰마다 줄바꿈되어 세로로 출력됨                      |
| `flush=True` | 버퍼에 쌓였다가 한꺼번에 나와 스트리밍처럼 보이지 않음 |

⚠️ 두 옵션이 빠지면 스트리밍을 써도 효과가 드러나지 않습니다.

### batch와 동시 실행 수 제한

```python
chain.batch(inputs, config={"max_concurrency": 3})
```

`batch`는 여러 입력을 동시에 처리합니다. 순차 호출보다 훨씬 빠릅니다.

`max_concurrency`는 **한 번에 몇 건까지 동시에 보낼지**를 제한합니다. 제한이 필요한 이유는 API에 분당 요청 수 제한이 있기 때문입니다. 100건을 한꺼번에 던지면 상당수가 거부되고, 재시도 로직이 없으면 그대로 실패합니다.

### 비동기가 필요한 순간

```python
async for token in chain.astream({"topic": "..."}):
    print(token, end="", flush=True)
```

동기 호출은 모델이 응답하는 동안 프로그램 전체가 멈춰 기다립니다. 노트북에서 혼자 실험할 때는 문제가 없습니다.

하지만 웹 서버에서는 다릅니다. 한 사용자의 요청을 기다리는 동안 다른 요청을 처리하지 못하면 서비스가 마비됩니다. 비동기 버전이 있는 이유입니다.

---

## 6. RunnableParallel — 갈래로 나누기

### 무엇인가

**같은 입력을 여러 갈래로 동시에 흘리고, 결과를 이름표가 붙은 dict로 모으는 것**입니다.

```python
combined = RunnableParallel(capital=chain1, area=chain2)
combined.invoke({"country": "..."})
```

```text
입력 하나
   ├──→ chain1 ──→ 결과1
   └──→ chain2 ──→ 결과2
          ↓
{"capital": 결과1, "area": 결과2}
```

반환 dict의 키는 `RunnableParallel`에 지정한 인자 이름 그대로입니다.

### 왜 필요한가 — 두 가지 이유

**① 속도**

두 체인이 순차 실행되면 시간이 두 배 걸립니다. `RunnableParallel`은 동시에 실행하므로 둘 중 느린 쪽 시간만 듭니다.

LLM 호출은 한 번에 수 초가 걸립니다. 세 개를 순차로 부르면 9초, 병렬로 부르면 3초입니다. 체감 차이가 큽니다.

**② 다음 단계가 요구하는 모양 만들기**

이쪽이 RAG에서 훨씬 중요합니다.

프롬프트가 두 개의 변수를 요구한다고 해 봅시다.

```python
prompt = PromptTemplate.from_template("문서: {context}\n질문: {question}")
```

이 프롬프트는 `{"context": ..., "question": ...}` 모양의 dict를 받아야 합니다. 그런데 사용자가 주는 것은 질문 문자열 하나뿐입니다.

**하나의 입력에서 두 개의 값을 만들어 내는 단계**가 필요하고, 그게 `RunnableParallel`입니다.

```python
{"context": retriever, "question": RunnablePassthrough()} | prompt | model | parser
```

```text
"질문 문자열"
   ├──→ retriever ────────────→ 검색된 문서   → context 자리로
   └──→ RunnablePassthrough ──→ 질문 그대로   → question 자리로
              ↓
{"context": 문서, "question": 질문}   ← prompt가 요구하는 모양
```

💡 **`RunnableParallel`은 단순한 성능 최적화 도구가 아니라, 데이터의 모양을 다음 단계에 맞추는 어댑터입니다.**

---

## 7. RunnablePassthrough — 그대로 통과시키기

```python
RunnablePassthrough().invoke({"num": 10})    # {"num": 10}
```

입력을 아무것도 하지 않고 그대로 내보냅니다.

### 왜 이런 게 필요한가

단독으로는 쓸모가 없어 보입니다. 아무 일도 하지 않으니까요.

의미는 **`RunnableParallel` 안에서** 생깁니다. 여러 갈래 중 한쪽만 가공하고 **다른 쪽은 원본을 유지해야** 할 때, 그 자리를 채울 무언가가 필요합니다.

```python
{"context": retriever, "question": RunnablePassthrough()}
#            └ 질문으로 문서를 검색       └ 질문 원본을 그대로 전달
```

`RunnableParallel`은 모든 갈래에 Runnable을 요구합니다. "여기는 아무것도 하지 마"를 표현하려면 **아무것도 하지 않는 Runnable**이 있어야 하고, 그게 `RunnablePassthrough`입니다.

### assign — 원본에 값을 덧붙이기

```python
RunnablePassthrough.assign(doubled=lambda d: d["num"] * 2).invoke({"num": 5})
# {"num": 5, "doubled": 10}
```

원본 dict를 유지한 채 **키를 추가**합니다. 기존 값을 잃지 않고 계산 결과를 얹을 때 씁니다.

---

## 8. FewShotPromptTemplate — 예시로 형식을 가르치기

```python
prompt = FewShotPromptTemplate(
    examples=examples,              # 예시 목록
    example_prompt=example_prompt,  # 예시 하나를 어떤 모양으로 넣을지
    suffix="Question:\n{question}\nAnswer:",
    input_variables=["question"],
)
```

### 무엇인가

지시문으로 "이렇게 답해라"라고 **설명하는** 대신, 모범 답안 몇 개를 **보여주고** 마지막에 실제 질문을 붙이는 방식입니다.

```text
[예시1 질문 → 예시1 답변]
[예시2 질문 → 예시2 답변]
[예시3 질문 → 예시3 답변]
[실제 질문 → ]                ← 모델이 이어서 채운다
```

| 구성 요소         | 역할                             |
| ----------------- | -------------------------------- |
| `examples`        | 예시 데이터 목록 (dict의 리스트) |
| `example_prompt`  | 예시 하나를 문자열로 만드는 틀   |
| `suffix`          | 예시들 뒤에 붙는 실제 질문 부분  |
| `input_variables` | 호출할 때 채울 변수              |

### 왜 효과가 있는가

언어 모델은 **주어진 맥락의 패턴을 이어가도록** 학습되어 있습니다. 앞에 같은 형식의 문답이 세 번 반복되면, 네 번째도 같은 형식으로 이어가는 것이 자연스러운 선택이 됩니다.

말로 설명하기 어려운 **답변의 구조와 길이와 톤**을 예시가 대신 전달합니다. 특히 "단계를 나눠 추론한 뒤 마지막에 결론을 내라" 같은 형식은, 글로 지시하는 것보다 예시 두세 개가 훨씬 정확하게 전달됩니다.

⚠️ 예시가 늘어날수록 프롬프트가 길어져 **비용과 지연이 함께 늘어납니다.** 모든 요청에 예시 전부가 따라붙기 때문입니다.

그래서 실무에서는 고정된 예시를 넣는 대신 **질문과 비슷한 예시만 골라 넣는** 방식을 씁니다. 그 선별에 쓰이는 것이 유사도 검색이고, RAG의 검색과 정확히 같은 원리입니다.

---

## 9. 환경 변수 — 왜 `.env`인가

```python
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
```

API 키를 코드에 직접 적으면 **파일 자체가 유출 경로**가 됩니다. Git에 커밋되고, 화면 공유에 찍히고, 노트북을 남에게 보낼 때 함께 넘어갑니다.

| 구분               | 역할                                          |
| ------------------ | --------------------------------------------- |
| `.env`             | 실제 키 값. `.gitignore`에 넣어 커밋에서 제외 |
| `load_dotenv()`    | `.env`를 읽어 `os.environ`에 올림             |
| `os.getenv("KEY")` | 올라온 값을 코드에서 읽음                     |

코드에는 **키 이름만** 남고 값은 남지 않습니다. 그래서 같은 코드를 다른 사람이 자기 키로 실행할 수 있습니다.

```python
print(api_key[:8])   # 앞 8글자만 출력
```

⚠️ 키 확인용 출력에서 **앞부분만 자르는 것**이 중요합니다. 노트북은 실행 결과가 파일에 그대로 저장되므로, 전체를 출력하면 `.ipynb` 안에 키가 박제됩니다.

> `load_dotenv()`는 기본적으로 시스템 환경변수를 덮어쓰지 않습니다. 이미 설정된 값이 있으면 그쪽이 우선합니다.

---

## 10. 관찰 — 트레이싱과 로깅

### 왜 필요한가

체인은 여러 단계를 거칩니다. 결과가 이상할 때 **어느 단계에서 틀어졌는지** 보이지 않으면 고칠 수가 없습니다.

특히 프롬프트는 템플릿과 값이 합쳐진 결과라, **모델에게 실제로 무엇이 전달됐는지** 코드만 봐서는 알 수 없습니다.

| 수단      | 보는 것                                               |
| --------- | ----------------------------------------------------- |
| LangSmith | 각 단계의 입출력, 완성된 프롬프트, 토큰 수, 소요 시간 |
| `logging` | 내 코드의 실행 흐름과 예외                            |

### LangSmith

```python
from langchain_teddynote import logging
logging.langsmith("프로젝트명", set_enable=True)
```

한 번 설정해 두면 이후 모든 체인 실행이 자동으로 기록됩니다.

가장 큰 가치는 **완성된 프롬프트를 눈으로 볼 수 있다**는 점입니다. 템플릿 변수가 잘못 채워졌거나, `partial`로 넣은 형식 지침이 빠졌거나, 검색된 문서가 엉뚱한 경우 — 코드만 봐서는 알기 어렵지만 트레이스에는 그대로 드러납니다.

### logging

```python
logging.basicConfig(
    filename="app.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    encoding="utf-8",
)
```

`print`와 달리 **파일에 남고**, 시간과 심각도가 함께 기록되며, 레벨로 걸러 볼 수 있습니다.

⚠️ `encoding="utf-8"`이 없으면 한글이 깨집니다.

```python
except Exception as e:
    logger.error(f"실행 중 에러 발생: {e}", exc_info=True)
```

`exc_info=True`는 **예외가 발생한 위치(스택 트레이스)까지** 함께 기록합니다. 이게 없으면 메시지만 남아 원인을 찾기 어렵습니다.

RAG는 단계가 더 늘어납니다. 답변이 엉뚱할 때 **검색이 잘못된 문서를 가져온 것인지, 프롬프트 조립이 틀린 것인지, 모델이 문서를 무시한 것인지** 구분해야 하는데, 관찰 수단 없이는 이 구분이 사실상 불가능합니다.

---

## 11. 멀티모달 입력

```python
message = HumanMessage(
    content=[
        {"type": "text", "text": prompt},
        {"type": "image_url", "image_url": {"url": IMAGE_URL}},
    ]
)
```

텍스트만 보낼 때는 `content`에 문자열을 넣지만, 이미지를 함께 보낼 때는 **타입이 표시된 조각들의 목록**으로 구성합니다.

| `type`        | 내용                      |
| ------------- | ------------------------- |
| `"text"`      | 문자열 프롬프트           |
| `"image_url"` | 이미지 주소 또는 data URL |

모델이 각 조각을 무엇으로 해석해야 하는지 알아야 하므로, 타입을 명시적으로 붙이는 구조입니다.

로컬 파일은 인터넷 주소가 없으므로 base64로 인코딩해 data URL로 만들어 넣습니다.

```python
encoded = base64.b64encode(image_path.read_bytes()).decode("utf-8")
return f"data:{mime_type};base64,{encoded}"
```

표나 도면이 들어간 문서를 다룰 때 이 기능이 의미를 갖습니다. 텍스트 추출만으로는 **표의 행과 열 관계나 그림의 내용이 소실**되는데, 페이지를 이미지로 넘기면 모델이 시각 정보를 그대로 해석할 수 있습니다.

---

## 전체 그림

```text
[환경]     load_dotenv()              키를 코드 밖으로 분리
              ↓
[입력]     PromptTemplate             템플릿과 값의 분리
              ↓  |  ← 모든 단계가 Runnable이므로 파이프로 연결된다
[생성]     ChatOpenAI                 AIMessage 반환
              ↓  |
[정형화]   OutputParser               문자열 또는 구조화 객체로
              ↓
[실행]     invoke / stream / batch    상황에 맞는 호출 방식
              ↓
[관찰]     LangSmith / logging        어느 단계가 틀어졌는지 확인
```

여기에 검색 단계가 붙으면 RAG가 됩니다.

```text
질문 ─┬─→ retriever ──────────→ 문서 ─┐
      │                                ├─→ prompt → model → parser → 답변
      └─→ RunnablePassthrough ─→ 질문 ─┘
           └────── RunnableParallel ──────┘
```

이 구조가 성립하는 이유를 되짚으면 결국 하나로 모입니다.

**모든 부품이 같은 규격(Runnable)을 따르기 때문에, 어떤 조합으로 이어 붙여도 다시 하나의 실행 가능한 부품이 된다.**
