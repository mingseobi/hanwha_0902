requests = ["첫 번째 질문", "두 번째 질문"]

response = {
    "status": "success",
    "count": len(requests),
    "items": requests,
}

print(response["count"], end="개")

# 2개