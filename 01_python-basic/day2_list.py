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

# {'id': '1', 'question': 'Pydantic이란?', 'status': 'ready'}
# {'id': '2', 'question': '', 'status': 'invalid'}
# {'id': '3', 'question': 'FastAPI란?', 'status': 'ready'}