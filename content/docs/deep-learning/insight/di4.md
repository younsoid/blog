---
date : 2026-07-30
tags: ['2026-07']
categories: ['tensor']
bookHidden: true
title: "텐서 연산"
bookComments: true
index: 4
---

# 텐서 연산

#2026-07-30

---

### 1. 신경망 만들기

신경망에서 층은 데이터로부터 '주어진 문제에 더 의미있는 표현'을 추출한다.  

```python
from tensorflow import keras
from tensorlfow.keras import layers

model = keras.Sequential([
    layers.Dense(512, activation="relu"),
    layers.Dense(10, activation="softmax")
])
```

위 신경망은 fully connected된 신경망 층인 Dense 층 2개가 연결되어 구성되어 있다.

두번째 층은 10개의 확률 점수가 들어있는 배열을 반환하는 소프트맥스 분류층이다. (10개를 더하면 1)

```python
model.compile(optimizer="rmsprop",
    loss="sparse_categorial_crossentropy",
    metrics=["accuracy"])
```

신경망이 훈련하기 위해서는 옵티마이저, 손실함수, 훈련과 테스트를 평가할 지표가 필요하다.

옵티마이저는 모델을 업데이트하는 메커니즘, 손실함수는 성능 측정 방법이다.

```python
train_images = train_images.reshape((60000, 28 * 28))
train_images = train_images.astype("float32") / 255
```

그리고 데이터를 모델에 맞는 크기로 바꾸고 0과 1 사이 스케일로 조정해야 한다.

원래 훈련 이미지는 [0, 255] 내의 값인 uint8 타입의 (60000, 28, 28) 크기 배열인데 이를 0과 1 사이 값을 갖는 float32 타입의 (60000, 28*28) 크기 배열로 바꾼다.

###

### 2. 텐서 연산

신경망의 데이터 변환은 텐서 연산으로 나타낼수있다. 

```python
keras.layers.Dense(512, activation="relu")
```

이 층은 행렬을 받고 새로운 표현으로 바꿔서 또다른 행렬을 반환하는 함수로 보면 다음과 같다.

```python
output = relu(dot(W, input) + b)
```

이 함수에는 3개의 텐서연산이 있다. 입력텐서와 텐서W사이의 점곱(dot), 점곱으로 만든 행렬과 벡터b 사이의 덧셈(+), relu연산이다. (relu 연산은 relu(x) = max(x,0)이다)

이중 relu 함수와 덧셈은 원소별 연산이다. 텐서에 있는 각 원소에 독립적으로 적용되므로 고도의 병렬 구현이 가능한 연산이다.

numpy 배열을 다루는 경우라면 최적화된 numpy 내장 함수로 이 연산들을 처리할수있다. 비슷하게 텐서플로 코드를 GPU에서 실행하면 고도로 병렬화된 GPU 칩 구조를 최대로 활용할수있는 완전히 벡터화된 CUDA 구현을 통해 원소별 연산이 실행된다고 한다.

그리고 점곱, 즉 텐서 곱셈은 x.shape[1] == y.shape[0]일때 행렬 x와 y 사이의 점곱 dot(x,y)이 성립된다. 결과 행렬의 크기는 (x.shape[0], y.shape[1])이 된다.

```python
train_images = train_images.reshape((60000, 28 * 28))
```

텐서 연산으로는 텐서 크기 변환(reshaping)도 있다. 신경망의 Dense 층에서는 안나오지만 데이터 전처리에 사용했었다.

텐서 크기 변환은 열과 행을 재배열하는것이다. 원소 개수는 원래 텐서와 동일하다.

<img width="600" alt="image" src="https://github.com/user-attachments/assets/c2edf1c3-5a25-4acd-9558-652bb46e8dc4" />

텐서는 공간 좌표로도 볼수있어서 모든 텐서 연산은 기하학적 해석이 가능하다. 예를 들어 벡터(포인트) 덧셈을 한다고 하자. 데이터 포인트 A = [0.5, 1]에 B = [1, 0.25]를 더한다.

기하학적으로는 벡터화살표를 연결해서 계산하는게 된다. 텐서 덧셈은 객체(여기서는 포인트 A = [0.5, 1])를 특정 방향으로 특정 양(여기서는 벡터 B = [1, 0.25])만큼 이동하는 행동을 나타낸다.

<img width="1280" height="653" alt="image" src="https://github.com/user-attachments/assets/8b4bfa3d-6396-47d1-b1a9-39565c12587b" />
<img width="1280" height="649" alt="image" src="https://github.com/user-attachments/assets/e96c5e60-bf00-48d4-9d52-a3d18f0ee16a" />

이동 외에도 회전, 크기 변경, 기울이기 같은 기본적인 기하학적 연산은 텐서 연산으로 표현할 수 있다.

먼저 점(2D 객체) 집합에 벡터를 더하면 고정된 방향으로 점 집합을 이동한다. 2D 벡터에 2x2 행렬 R=[cos(theta), -sin(theta)], [sin(theta), cos(theta)]와 점곱하면 theta만큼 회전할수있다. 

<img width="1280" height="698" alt="image" src="https://github.com/user-attachments/assets/07695115-b2c1-44ce-bf59-6104e2e258b8" />

이미지에 2x2 행렬 S = [[horizontal_factor, 0], [0, vertical_factor]]을 점곱하면 수직 수평으로 크기 변경할 수 있다. S를 대각행렬이라고 한다. (대각선 방향 성분만 0이 아닌 행렬)

<img width="1280" height="615" alt="image" src="https://github.com/user-attachments/assets/af3b3365-c21c-4f83-93d2-90853de6800b" />

그림 2-10, 11처럼 행렬과 점곱하면 선형 변환이다. (크기 변경, 회전)

행렬과 점곱하는 선형 변환과 벡터를 더하는 이동을 조합한 변환이 아핀 변환이다. Dense 층에서 y=W*x+b를 수행했는데 이게 아핀변환인것이다. 고로 (활성화 함수를 사용하지 않는) Dense층은 일종의 아핀변환 층이다.

<img width="1280" height="631" alt="image" src="https://github.com/user-attachments/assets/04081d2e-d4fc-4bea-a857-454db6a2bc3b" />

```plain text
affine2(affine1(x)) = W2 * (W1*x+b1) + b2 = (W2*W1) * x + (W2*b1+b2)
```

아핀변환의 특징은 여러 아핀변환을 반복해서 적용해도 결국 하나의 아핀변환이 된다는 것이다. 

위 아핀 변환은 2개의 아핀변환이지만 변형하면 선형변환이 `W2*W1`이고 이동이 `W2*(b1+b2)`인 하나의 아핀변환이 된다. 즉 활성화함수 없이 Dense 층으로만 구성된 다층신경망은 그냥 하나의 Dense층 즉 하나의 선형모델인 셈이다.

그래서 relu 같은 활성화 함수가 있어야 Dense 층을 중첩해서 복잡하고 비선형적인 기하학적 변형을 구현해서 심층신경망에 풍부한 가설공간을 제공할수가 있는 것이다.


###

#출처

책 케라스 창시자에게 배우는 딥러닝
