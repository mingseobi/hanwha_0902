import numpy as np

# 0부터 8까지의 연속된 숫자로 3x3 행렬 생성
matrix = np.arange(9).reshape(3, 3)

# 2차원 슬라이싱: 1~2행, 1~2열 추출
print("부분 행렬:\n", matrix[1:, 1:])

# Boolean Indexing: 5보다 큰 요소만 추출
mask = matrix > 5
print("조건 마스크:\n", mask)
print("5보다 큰 값들:", matrix[mask])

# 부분 행렬:
#  [[4 5]
#  [7 8]]
# 조건 마스크:
#  [[False False False]
#  [False False False]
#  [ True  True  True]]
# 5보다 큰 값들: [6 7 8]