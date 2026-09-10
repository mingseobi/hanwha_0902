# 한화시스템 AI Agent 서비스 개발과정

한화시스템 AI Agent 서비스 개발과정(1회차 · 천안) 교육 중 작성한 실습 코드와 학습 정리를 보관하는 저장소입니다.

## 과정 정보

| 항목      | 내용                                |
| --------- | ----------------------------------- |
| 과정명    | 한화시스템 AI Agent 서비스 개발과정 |
| 교육 기간 | 2026.09.01 ~ 2026.11.13             |
| 교육 시간 | 총 50일 / 400시간 (1일 8시간)       |

9월 1일 OT 및 기업탐방을 거쳐 9월 2일부터 정규 강의가 시작됩니다.


## 폴더 확장 계획

| 폴더             | 대응 과목                               |
| ---------------- | --------------------------------------- |
| `06_test`        | AI-Native 아키텍처 및 테스트 공학       |
| `07_langchain`   | LLM 오케스트레이션 및 파이프라인 구축   |
| `08_rag`         | 실무형 RAG 시스템 구축 및 최적화        |
| `09_agent`       | AI 에이전트 기획 및 툴 연동 실무        |
| `10_multi-agent` | 멀티 에이전트 제어 및 파이프라인 자동화 |
| `11_deploy`      | 엔터프라이즈 AI 에이전트 배포 및 상용화 |
| `12_capstone`    | 한화시스템 인프라-AI 융합 캡스톤        |

## 가상환경 준비

필요한 패키지는 `requirements.txt`에 정리되어 있습니다.

macOS / Linux

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

Windows (PowerShell)

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install --upgrade pip
pip install -r requirements.txt
```

가상환경은 터미널 단위로 적용됩니다. 새 터미널을 열 때마다 `source .venv/bin/activate`(Windows는 `.venv\Scripts\Activate.ps1`)를 실행해야 합니다. 활성화되면 프롬프트 앞에 `(.venv)`가 표시되고, 종료는 `deactivate`입니다.

| 패키지                  | 사용 폴더                   |
| ----------------------- | --------------------------- |
| `numpy`                 | `03_numpy`                  |
| `pydantic`              | `04_pydantic`, `05_fastapi` |
| `fastapi`, `uvicorn`    | `05_fastapi`                |
| `streamlit`, `requests` | `05_fastapi/proj_streamlit` |

설치 상태는 다음 명령으로 확인할 수 있습니다.

```bash
python -c "import numpy, pydantic, fastapi, streamlit; print('ok')"
```

## 코드 포맷

코드 스타일은 [black](https://black.readthedocs.io)으로 통일합니다. 설정은 `pyproject.toml`에 있습니다.

```bash
pip install -r requirements-dev.txt

black .          # 전체 포맷 적용
black --check .  # 변경 없이 검사만
```

VS Code에서는 `.vscode/settings.json` 설정에 따라 저장할 때 자동으로 적용됩니다.
권장 확장(`ms-python.black-formatter`)은 처음 프로젝트를 열 때 설치 안내가 표시됩니다.

## 실행

가상환경을 활성화한 상태에서 저장소 루트를 기준으로 실행합니다.

```bash
python 01_python-basic/day1_value_type.py
python 03_numpy/day3_numpy03.py
python 04_pydantic/day4_pydantic03.py
```

### API 서버

`python 파일.py`로는 실행되지 않습니다. ASGI 서버인 uvicorn이 앱을 불러와 구동합니다.

```bash
cd 05_fastapi && uvicorn day6_FastAPI02:app --reload
```

`http://127.0.0.1:8000/docs`에서 API 문서를 확인할 수 있습니다.

### day7 프로젝트 (API + 화면)

백엔드와 화면을 함께 띄우므로 **터미널 두 개**가 필요합니다. 각 터미널에서 가상환경을 따로 활성화해야 합니다.

터미널 1 — 백엔드

```bash
cd ~/Desktop/hanwha_0902 && source .venv/bin/activate && cd 05_fastapi/proj_fastapi && uvicorn day7_fastapi:app --reload
```

터미널 2 — 화면

```bash
cd ~/Desktop/hanwha_0902 && source .venv/bin/activate && cd 05_fastapi/proj_streamlit && streamlit run day7_streamlit.py
```

| 주소                         | 화면           |
| ---------------------------- | -------------- |
| `http://127.0.0.1:8501`      | 상품 관리 화면 |
| `http://127.0.0.1:8000/docs` | API 문서       |

두 명령을 한 터미널에서 연달아 실행하면 두 번째 `cd`가 실패합니다. 첫 명령으로 이미 다른 폴더에 들어가 있기 때문입니다. 위 명령은 매번 홈 기준 경로에서 시작하므로 현재 위치와 무관하게 동작합니다.

종료는 각 터미널에서 `Ctrl + C`입니다.
