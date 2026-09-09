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
| `05_fastapi`     | AI 서비스 백엔드 프로그래밍 실무 (후반) |
| `06_test`        | AI-Native 아키텍처 및 테스트 공학       |
| `07_langchain`   | LLM 오케스트레이션 및 파이프라인 구축   |
| `08_rag`         | 실무형 RAG 시스템 구축 및 최적화        |
| `09_agent`       | AI 에이전트 기획 및 툴 연동 실무        |
| `10_multi-agent` | 멀티 에이전트 제어 및 파이프라인 자동화 |
| `11_deploy`      | 엔터프라이즈 AI 에이전트 배포 및 상용화 |
| `12_capstone`    | 한화시스템 인프라-AI 융합 캡스톤        |

## 가상환경 준비

macOS / Linux

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install numpy pydantic
```

Windows (PowerShell)

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install --upgrade pip
pip install numpy pydantic
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

```bash
python 01_python-basic/day1_value_type.py
python 03_numpy/day3_numpy03.py
python 04_pydantic/day4_pydantic03.py
```

```bash
python -c "import numpy, pydantic; print(numpy.__version__, pydantic.VERSION)"
```
