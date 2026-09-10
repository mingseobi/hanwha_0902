# day7 프로젝트 — Streamlit 연동

FastAPI로 만든 API를 Streamlit 화면과 연결해 하나의 서비스로 만드는 단계입니다.

| 항목        | 내용                                                  |
| ----------- | ----------------------------------------------------- |
| 과목        | AI 서비스 백엔드 프로그래밍 실무                      |
| 실습일      | Day 7 (9/10 목)                                       |
| 키워드      | 서버 연동, `requests`, 세션 상태, 위젯 key, 오류 처리 |
| 필요 패키지 | `fastapi`, `uvicorn`, `streamlit`, `requests`         |

API를 화면과 연결해 하나의 서비스로 만드는 단계입니다.

| 폴더             | 파일                                                    | 역할                     |
| ---------------- | ------------------------------------------------------- | ------------------------ |
| `proj_fastapi`   | [`day7_fastapi.py`](proj_fastapi/day7_fastapi.py)       | 상품 CRUD API (백엔드)   |
| `proj_streamlit` | [`day7_streamlit.py`](proj_streamlit/day7_streamlit.py) | 관리자 화면 (프론트엔드) |

```text
브라우저 ── Streamlit(8501) ── requests ── FastAPI(8000) ── 메모리 저장소
             화면 렌더링          HTTP        비즈니스 로직
```

Streamlit은 브라우저가 아니라 **서버 쪽 Python에서** `requests`로 API를 호출합니다. 그래서 CORS 설정이 필요하지 않습니다.

## 실행

터미널 두 개가 필요합니다. 백엔드를 먼저 띄웁니다.

```bash
cd 05_fastapi/proj_fastapi
uvicorn day7_fastapi:app --reload
```

```bash
cd 05_fastapi/proj_streamlit
streamlit run day7_streamlit.py
```

| 주소                         | 화면           |
| ---------------------------- | -------------- |
| `http://127.0.0.1:8501`      | 상품 관리 화면 |
| `http://127.0.0.1:8000/docs` | API 문서       |

## 백엔드 구성

| 메서드 | 경로             | 응답            | 설명                         |
| ------ | ---------------- | --------------- | ---------------------------- |
| GET    | `/health`        | 200             | 화면의 연결 상태 표시에 사용 |
| GET    | `/items/summary` | 200             | 상단 지표 집계               |
| GET    | `/items`         | 200             | 검색·정렬·페이징 목록        |
| GET    | `/items/{id}`    | 200 / 404       | 단건 조회                    |
| POST   | `/items`         | 201             | 생성                         |
| PUT    | `/items/{id}`    | 200 / 404       | 전체 교체                    |
| PATCH  | `/items/{id}`    | 200 / 400 / 404 | 부분 수정                    |
| DELETE | `/items/{id}`    | 204 / 404       | 삭제                         |

⚠️ `/items/summary`는 `/items/{item_id}`보다 **먼저** 등록해야 합니다. 순서가 바뀌면 `summary`가 `item_id`로 해석되어 422가 발생합니다.

목록 응답에는 전체 개수를 함께 담습니다. 화면이 페이지 수를 계산하려면 현재 페이지의 항목만으로는 부족하기 때문입니다.

```json
{ "total": 5, "skip": 0, "limit": 10, "items": [ ... ] }
```

## 화면 구성

```text
사이드바              본문
├ 서버 상태          ├ 지표 4종 (등록 상품 · 총 재고 · 재고 자산 · 품절)
├ 상품명 검색        └ 탭
├ 정렬 기준·방향        ├ 목록      표 + 페이지 이동
└ 페이지당 개수         ├ 등록      입력 폼 (POST)
                       └ 수정·삭제  전체 수정(PUT) · 재고만(PATCH) · 삭제(DELETE)
```

## API 호출을 한 곳으로 모으기

모든 요청이 같은 함수를 거치게 하면 오류 처리를 한 번만 작성하면 됩니다.

```python
def call_api(method: str, path: str, **kwargs) -> tuple[object | None, str | None]:
    """(응답 데이터, 오류 메시지)를 돌려준다. 성공하면 오류가 None."""
    try:
        response = requests.request(method, f"{API_URL}{path}", timeout=TIMEOUT, **kwargs)
    except requests.exceptions.ConnectionError:
        return None, "서버에 연결할 수 없습니다. FastAPI 서버가 실행 중인지 확인하세요."
    ...
```

호출부는 항상 같은 모양이 됩니다.

```python
created, error = call_api("POST", "/items", json=payload)

if error:
    flash("error", error)
else:
    flash("success", f"'{created['name']}' 상품을 등록했습니다.")
```

💡 서버가 꺼져 있어도 화면이 죽지 않고 안내를 표시합니다. `requests`는 연결 실패 시 예외를 던지므로, 잡지 않으면 Streamlit 화면 전체가 오류로 바뀝니다.

## 검증 오류를 사람이 읽을 수 있게

FastAPI의 오류 응답은 두 가지 형태로 옵니다.

| 상황                    | `detail`의 형태                                    |
| ----------------------- | -------------------------------------------------- |
| `HTTPException`         | 문자열 — `"3번 상품을 찾을 수 없습니다."`          |
| Pydantic 검증 실패(422) | 목록 — `[{"loc": ["body", "name"], "msg": "..."}]` |

두 형태를 모두 처리해야 화면에 일관된 메시지를 띄울 수 있습니다.

```python
if isinstance(detail, list):
    lines = []
    for error in detail:
        field = " → ".join(str(part) for part in error.get("loc", [])[1:])
        lines.append(f"{field}: {error.get('msg')}")
    return "\n\n".join(lines)
```

`loc`의 첫 항목은 `"body"`나 `"query"`처럼 위치 종류라서, `[1:]`로 잘라야 필드 이름만 남습니다.

## ⚠️ 위젯 key와 값 갱신

Streamlit에서 가장 빠지기 쉬운 함정입니다.

```python
# 다른 상품을 선택해도 이전 상품의 재고가 그대로 남는다
st.number_input("재고 수량", value=target["stock"], key="quick_stock")
```

`key`를 지정하면 그 값이 세션 상태에 보관되고, **다시 그릴 때 `value`보다 세션 상태가 우선**합니다. 1번 상품(재고 12)을 보다가 3번 상품(재고 7)으로 바꿔도 화면에는 12가 남고, 그대로 저장하면 잘못된 값이 기록됩니다.

`key`에 상품 번호를 넣으면 상품이 바뀔 때 다른 위젯으로 취급되어 값이 새로 채워집니다.

```python
st.number_input("재고 수량", value=target["stock"], key=f"e_quick_{item_id}")
```

삭제 동의 체크박스도 마찬가지입니다. 고정 `key`를 쓰면 A 상품에서 체크한 동의가 B 상품으로 넘어가, 확인 없이 삭제 버튼이 활성화됩니다.

## 처리 후 화면 갱신

생성·수정·삭제 뒤에는 `st.rerun()`으로 화면을 다시 그립니다. 이때 메시지를 그냥 출력하면 다시 그리는 과정에서 사라지므로, 세션 상태에 담아 두었다가 다음 렌더링에서 표시합니다.

```python
def flash(kind: str, message: str) -> None:
    st.session_state.flash = (kind, message)
```

## 점검 항목

- [ ] Streamlit에 CORS 설정이 필요 없는 이유
- [ ] 목록 응답에 `total`을 포함하는 이유
- [ ] `/items/summary`를 `/items/{item_id}`보다 먼저 등록해야 하는 이유
- [ ] 위젯에 고정 `key`를 쓰면 값이 갱신되지 않는 이유
- [ ] `st.rerun()` 직전에 출력한 메시지가 사라지는 이유
- [ ] `detail`이 문자열일 때와 목록일 때의 차이

## 다음 문서

- FastAPI 문법과 CRUD 기본기 → [FastAPI CRUD](fastapi_crud.md)
