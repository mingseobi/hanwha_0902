import numpy as np

# 12개의 원소를 가진 1차원 배열
vec = np.arange(12)

# 3행 4열 2차원 배열로 형태 변환
matrix_3x4 = vec.reshape(3, 4)
print("3x4 행렬:\n", matrix_3x4)

# 전치 행렬 (행과 열을 맞바꿈 -> 4x3 행렬)
transposed = matrix_3x4.T
print("전치(Transpose) 결과:\n", transposed)

# 3x4 행렬:
#  [[ 0  1  2  3]
#  [ 4  5  6  7]
#  [ 8  9 10 11]]
# 전치(Transpose) 결과:
#  [[ 0  4  8]
#  [ 1  5  9]
#  [ 2  6 10]
#  [ 3  7 11]]