"""상품 관리 화면 - FastAPI 백엔드와 연동되는 Streamlit 관리자 UI.

실행:
    streamlit run day7_streamlit.py

백엔드가 먼저 떠 있어야 한다:
    uvicorn day7_fastapi:app --reload
"""

import pandas as pd
import requests
import streamlit as st

API_URL = "http://127.0.0.1:8000"
TIMEOUT = 5

st.set_page_config(page_title="상품 관리", page_icon="📦", layout="wide")


# =========================
# API 호출
# =========================


def format_error(body: object, status_code: int) -> str:
    """FastAPI의 오류 응답을 화면에 보여줄 문장으로 바꾼다."""
    if not isinstance(body, dict) or "detail" not in body:
        return f"요청이 실패했습니다 (HTTP {status_code})"

    detail = body["detail"]

    # HTTPException은 문자열, Pydantic 검증 실패(422)는 목록으로 온다
    if isinstance(detail, str):
        return detail

    if isinstance(detail, list):
        lines = []
        for error in detail:
            field = " → ".join(str(part) for part in error.get("loc", [])[1:])
            lines.append(
                f"{field or '입력값'}: {error.get('msg', '올바르지 않습니다')}"
            )
        return "\n\n".join(lines)

    return f"요청이 실패했습니다 (HTTP {status_code})"


def call_api(method: str, path: str, **kwargs) -> tuple[object | None, str | None]:
    """(응답 데이터, 오류 메시지)를 돌려준다. 성공하면 오류가 None."""
    try:
        response = requests.request(
            method, f"{API_URL}{path}", timeout=TIMEOUT, **kwargs
        )
    except requests.exceptions.ConnectionError:
        return None, "서버에 연결할 수 없습니다. FastAPI 서버가 실행 중인지 확인하세요."
    except requests.exceptions.Timeout:
        return None, f"서버 응답이 {TIMEOUT}초 안에 오지 않았습니다."

    # 204 No Content는 본문이 없다
    if response.status_code == 204:
        return {}, None

    try:
        body = response.json()
    except ValueError:
        return None, f"응답을 해석할 수 없습니다 (HTTP {response.status_code})"

    if response.ok:
        return body, None

    return None, format_error(body, response.status_code)


def flash(kind: str, message: str) -> None:
    """다시 그려진 뒤에 표시할 메시지를 남긴다."""
    st.session_state.flash = (kind, message)


def show_flash() -> None:
    kind, message = st.session_state.pop("flash", (None, None))
    if kind == "success":
        st.success(message)
    elif kind == "error":
        st.error(message)


# =========================
# 사이드바
# =========================

st.session_state.setdefault("page", 0)

SORT_FIELDS = {"등록순": "id", "상품명": "name", "가격": "price", "재고": "stock"}

with st.sidebar:
    st.subheader("서버 상태")

    health, health_error = call_api("GET", "/health")

    if health_error:
        st.error("연결 끊김")
        st.caption(health_error)
    else:
        st.success("정상 연결")
        st.caption(f"{API_URL} · 상품 {health['count']}건")

    st.divider()
    st.subheader("검색과 정렬")

    keyword = st.text_input("상품명", placeholder="예: 노트북", key="f_keyword")

    sort_label = st.selectbox("정렬 기준", list(SORT_FIELDS), key="f_sort")
    sort_by = SORT_FIELDS[sort_label]

    direction = st.radio("정렬 방향", ["오름차순", "내림차순"], key="f_order")
    order = "asc" if direction == "오름차순" else "desc"

    limit = st.select_slider(
        "페이지당 개수", options=[5, 10, 20, 50], value=10, key="f_limit"
    )

    st.divider()

    if st.button("새로고침", width="stretch", key="btn_refresh"):
        st.rerun()


# =========================
# 상단 지표
# =========================

st.title("📦 상품 관리")
st.caption("FastAPI 백엔드와 연동된 관리 화면입니다.")

show_flash()

if health_error:
    st.warning("백엔드에 연결되지 않아 데이터를 표시할 수 없습니다.")
    st.code("uvicorn day7_fastapi:app --reload", language="bash")
    st.stop()

summary, summary_error = call_api("GET", "/items/summary")

if summary_error:
    st.error(summary_error)
    st.stop()

col1, col2, col3, col4 = st.columns(4)
col1.metric("등록 상품", f"{summary['count']}건")
col2.metric("총 재고", f"{summary['total_stock']}개")
col3.metric("재고 자산", f"{summary['total_value']:,}원")
col4.metric("품절 상품", f"{summary['out_of_stock']}건")

st.divider()


# =========================
# 목록 조회
# =========================

# 검색 조건이 바뀌면 첫 페이지로 되돌린다
condition = (keyword, sort_by, order, limit)
if st.session_state.get("condition") != condition:
    st.session_state.condition = condition
    st.session_state.page = 0

params = {
    "sort_by": sort_by,
    "order": order,
    "skip": st.session_state.page * limit,
    "limit": limit,
}
if keyword:
    params["keyword"] = keyword

page_data, page_error = call_api("GET", "/items", params=params)

if page_error:
    st.error(page_error)
    st.stop()

items = page_data["items"]
total = page_data["total"]
last_page = max((total - 1) // limit, 0)

# 삭제 등으로 현재 페이지가 비면 마지막 페이지로 돌아간다
if not items and st.session_state.page > 0:
    st.session_state.page = last_page
    st.rerun()


# =========================
# 탭
# =========================

tab_list, tab_create, tab_edit = st.tabs(["목록", "등록", "수정 · 삭제"])


with tab_list:
    if not items:
        message = (
            f"'{keyword}'에 해당하는 상품이 없습니다."
            if keyword
            else "등록된 상품이 없습니다."
        )
        st.info(message)
    else:
        table = pd.DataFrame(items)[["id", "name", "price", "stock", "desc"]]

        # 설명이 없는 항목이 표에 None으로 보이지 않게 한다
        table["desc"] = table["desc"].fillna("")

        st.dataframe(
            table,
            hide_index=True,
            width="stretch",
            column_config={
                "id": st.column_config.NumberColumn("번호", width="small"),
                "name": st.column_config.TextColumn("상품명", width="medium"),
                # localized를 쓰면 1,450,000처럼 천 단위 구분이 붙는다
                "price": st.column_config.NumberColumn("가격(원)", format="localized"),
                "stock": st.column_config.NumberColumn("재고(개)", format="localized"),
                "desc": st.column_config.TextColumn("설명", width="large"),
            },
        )

        first = st.session_state.page * limit + 1
        last = first + len(items) - 1

        nav_prev, nav_info, nav_next = st.columns([1, 3, 1])

        with nav_prev:
            if st.button(
                "이전",
                width="stretch",
                disabled=st.session_state.page == 0,
                key="btn_prev",
            ):
                st.session_state.page -= 1
                st.rerun()

        position = (
            f"전체 {total}건 중 {first}–{last} · "
            f"{st.session_state.page + 1} / {last_page + 1} 페이지"
        )
        nav_info.markdown(
            f"<div style='text-align:center; padding-top:0.4rem; color:#6b7280;'>"
            f"{position}</div>",
            unsafe_allow_html=True,
        )

        with nav_next:
            if st.button(
                "다음",
                width="stretch",
                disabled=st.session_state.page >= last_page,
                key="btn_next",
            ):
                st.session_state.page += 1
                st.rerun()


with tab_create:
    st.subheader("새 상품 등록")

    with st.form("create_form", clear_on_submit=True):
        left, right = st.columns(2)

        new_name = left.text_input(
            "상품명", placeholder="예: 무선 이어폰", key="c_name"
        )
        new_price = right.number_input(
            "가격(원)", min_value=1, value=10_000, step=1_000, key="c_price"
        )
        new_stock = left.number_input(
            "재고 수량", min_value=0, value=0, step=1, key="c_stock"
        )
        new_desc = right.text_input("설명", placeholder="선택 입력", key="c_desc")

        if st.form_submit_button("등록", type="primary", width="stretch"):
            payload = {
                "name": new_name.strip(),
                "price": int(new_price),
                "stock": int(new_stock),
                "desc": new_desc.strip() or None,
            }

            created, error = call_api("POST", "/items", json=payload)

            if error:
                flash("error", error)
            else:
                flash("success", f"'{created['name']}' 상품을 등록했습니다.")

            st.rerun()


with tab_edit:
    all_data, all_error = call_api("GET", "/items", params={"limit": 100})

    if all_error:
        st.error(all_error)
    elif not all_data["items"]:
        st.info("수정할 상품이 없습니다.")
    else:
        options = {f"{item['id']}. {item['name']}": item for item in all_data["items"]}
        selected_label = st.selectbox("대상 상품", list(options), key="e_target")
        target = options[selected_label]

        # key에 상품 번호를 넣어야 다른 상품을 고를 때 입력값이 새로 채워진다.
        # 고정 key를 쓰면 이전 상품의 값이 그대로 남는다.
        item_id = target["id"]

        st.divider()
        edit_col, action_col = st.columns([2, 1])

        with edit_col:
            st.markdown("**전체 수정** · 모든 필드를 함께 보냅니다 (PUT)")

            with st.form(f"edit_form_{item_id}"):
                edit_name = st.text_input(
                    "상품명", value=target["name"], key=f"e_name_{item_id}"
                )
                edit_price = st.number_input(
                    "가격(원)",
                    min_value=1,
                    value=target["price"],
                    step=1_000,
                    key=f"e_price_{item_id}",
                )
                edit_stock = st.number_input(
                    "재고 수량",
                    min_value=0,
                    value=target["stock"],
                    step=1,
                    key=f"e_stock_{item_id}",
                )
                edit_desc = st.text_input(
                    "설명", value=target["desc"] or "", key=f"e_desc_{item_id}"
                )

                if st.form_submit_button("수정", type="primary", width="stretch"):
                    payload = {
                        "name": edit_name.strip(),
                        "price": int(edit_price),
                        "stock": int(edit_stock),
                        "desc": edit_desc.strip() or None,
                    }

                    _, error = call_api("PUT", f"/items/{item_id}", json=payload)

                    if error:
                        flash("error", error)
                    else:
                        flash("success", f"{item_id}번 상품을 수정했습니다.")

                    st.rerun()

        with action_col:
            st.markdown("**재고만 변경** · 보낸 필드만 반영합니다 (PATCH)")

            quick_stock = st.number_input(
                "재고 수량",
                min_value=0,
                value=target["stock"],
                step=1,
                key=f"e_quick_{item_id}",
            )

            if st.button("재고 반영", width="stretch", key=f"btn_patch_{item_id}"):
                _, error = call_api(
                    "PATCH", f"/items/{item_id}", json={"stock": int(quick_stock)}
                )

                if error:
                    flash("error", error)
                else:
                    flash("success", f"재고를 {quick_stock}개로 변경했습니다.")

                st.rerun()

            st.divider()
            st.markdown("**삭제**")

            confirmed = st.checkbox(
                f"'{target['name']}' 삭제에 동의합니다", key=f"e_confirm_{item_id}"
            )

            if st.button(
                "삭제",
                width="stretch",
                disabled=not confirmed,
                key=f"btn_delete_{item_id}",
            ):
                _, error = call_api("DELETE", f"/items/{item_id}")

                if error:
                    flash("error", error)
                else:
                    flash("success", f"'{target['name']}' 상품을 삭제했습니다.")

                st.rerun()
