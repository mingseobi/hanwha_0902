from pydantic import BaseModel

# 1. 기본: 데이터 검증과 타입 변환

class User(BaseModel):
    name: str
    age: int
    email: str


user = User(
    name="Alice",
    age="25",
    email="alice@example.com",
)

print(user)
print(user.age)
print(type(user.age))

# ----------
# name='Alice' age=25 email='alice@example.com'
# 25
# <class 'int'>
# ----------