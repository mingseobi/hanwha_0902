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

# 클래스는 데이터와 동작을 함께 관리합
