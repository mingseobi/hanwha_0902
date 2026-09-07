import numpy as np

# 1차원 및 2차원 배열 생성
arr = np.array([[1, 2, 3], [4, 5, 6]])

# 전체 요소에 10 더하기 및 2 곱하기 (Broadcasting)
print("10 더하기:\n", arr + 10)
print("2 곱하기:\n", arr * 2)

# 행렬의 주요 통계값 계산
print("전체 합계:", arr.sum())
print("열별 평균(axis=0):", arr.mean(axis=0))
print("행별 최댓값(axis=1):", arr.max(axis=1))

# 10 더하기:
#  [[11 12 13]
#  [14 15 16]]
# 2 곱하기:
#  [[ 2  4  6]
#  [ 8 10 12]]
# 전체 합계: 21
# 열별 평균(axis=0): [2.5 3.5 4.5]
# 행별 최댓값(axis=1): [3 6]