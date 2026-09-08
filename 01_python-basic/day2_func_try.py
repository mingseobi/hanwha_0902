def normalize_question(question: str, max_length: int = 100) -> str:

    # 입력받은 문자열의 앞뒤 공백(띄어쓰기, 줄바꿈 등)을 제거
    cleaned = question.strip()

    # 공백을 제거한 결과가 빈 문자열("")인 경우
    if not cleaned:
        raise ValueError("질문을 입력하세요.")  # 의도적으로 에러를 발생

    # 정상적으로 입력시, 최대 max_length(기본값 100자)만큼만 자르고 반환함.
    return cleaned[:max_length]


try:
    result = normalize_question("  Python이란?  ")
    print(result)
except ValueError as error:
    print("입력 오류:", error)

# Python이란?
