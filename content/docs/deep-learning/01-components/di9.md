---
date : 2026-08-04
tags: ['2026-08']
categories: ['backpropagation']
bookHidden: true
title: "역전파"
bookComments: true
index: 1
---

# 역전파

#2026-08-04

---

### 1. 개념

모델을 학습시키려면 손실 함수의 그레이디언트가 필요하고, 함수가 미분 가능하니까 그레이디언트를 계산할 수 있었다.

신경망의 손실 함수는 합성함수이다. 합성함수에서 특정 가중치 하나에 대한 변화율(그레이디언트)를 어떻게 계산할까? 이 계산 방법이 역전파 알고리즘(backpropagation)이다.

덧셈, 렐루(relu), 텐서 곱셈(dot), 소프트맥스(softmax) 등 신경망을 이루는 개별 연산은  각각의 도함수가 이미 알려져 있다. 이 연산들이 연결된 합성 연산의 도함수는 각 연산의 도함수를 조합해서 구할수있다. (역전파)

```plain text
loss_value = loss(y_true, softmax(dot(relu(dot(inputs, W1) + b1), W2) + b2))
```

예를들어 2개의 Dense 층으로 된 모델의 손실은 위와 같은 구성으로, dot, +, relu, dot, +, softmax, loss가 겹쳐 있다.

이들 각각은 미분 가능하고 미적분의 연쇄 법칙(chain rule)으로 도함수들을 연결할수 있다.

```python
def fg(x):
    x1 = g(x)
    y = f(x1)
    return y
```

위처럼 f와 g 함수가 있고 f와 g를 연결한 합성 함수 fg가 있다.

fg(x)는 g(x)를 먼저 계산한 다음 그 결과를 f에 넣는 것 즉 f(g(x))다. 코드로 쓰면 중간 결과 x1 = g(x)를 만들고, y = f(x1)를 만든다.

이때 x가 y에 미치는 영향 grad(y, x)는 연쇄 법칙에 의해 grad(y, x1) * grad(x1, x)가 된다.

즉 x가 조금 바뀌면 그것이 x1을 얼마나 바꾸는지(grad(x1, x))와, x1이 바뀌면 그것이 다시 y를 얼마나 바꾸는지(grad(y, x1))를 곱한 것이 된다. 이렇게 각 단계의 "민감도"를 곱해서 이어붙이는것이 연쇄 법칙이다.

신경망에선 x에서 y까지 가는 경로마다 도함수를 하나씩 구하고, 그것들을 전부 곱하면 맨 끝 x가 맨 끝 y에 미치는 전체 영향이 나온다. 이렇게 연쇄법칙으로 신경망의 그레이디언트를 구하는것이 역전파이다.

###

### 2. 계산 그래프

<img width="600" alt="image" src="https://github.com/user-attachments/assets/474ffe22-7791-4112-9dc9-8bbbd4ea2218" />

간단한 계산그래프로 역전파를 돌려보면 이렇다. 

이 계산그래프는 선형 층 1개로 되어있고 스칼라 변수 w와 b, 입력 x가 있다. 계산은 먼저 x1 = x * w를 계산하고 그다음 x2 = x1 + b를 계산하고, 마지막으로 절댓값 오차 손실 loss_val = abs(y_true - x2)를 계산한다.

목표는 이 loss_val을 줄이기 위해 w와 b를 어떻게 조정할지 아는 것, 즉 grad(loss_val, w)와 grad(loss_val, b)를 구하는 것이다.

<img width="600" alt="image" src="https://github.com/user-attachments/assets/3a6c04af-4780-4dbb-9802-9933fe2e7167" />

먼저 정방향 패스를 실행한다. 입력 노드로 x=2, w=3, b=1, y_true=4를 넣으면

```plain text
x1 = x * w = 2 * 3 = 6
x2 = x1 + b = 6 + 1 = 7
loss_val = abs(4 - 7) = 3
```

로 중간 노드 x1, x2를 구한다.

<img width="600" alt="image" src="https://github.com/user-attachments/assets/8efcb6de-a712-4671-acde-711135ba4f5a" />

다음으로 역방향 패스를 실행한다. 그래프의 화살표를 반대로 실행하는데, 원래 A에서 B로 가던 에지마다 B에서 A로 가는 반대 에지를 만들고, 그 반대 에지 위에 "A가 조금 변하면 B가 얼마나 변하는가", 즉 grad(B, A) 값을 구한다.

먼저 loss_val = abs(4 - x2)인데 지금 x2=7이라 4-x2가 음수 구간이고, 여기서 x2가 epsilon만큼 늘면 loss_val도 그만큼 늘어난다. grad(loss_val, x2)는 1이다. 

다음으로 x2 = x1 + b이므로 x1이 epsilon 변하면 x2도 딱 그만큼 변한다. grad(x2, x1)은 1이다. 덧셈의 도함수는 1이라는 뜻이다.

grad(x2, b)도 b가 epsilon 변하면 x2 = x1 + b도 그만큼 변하므로 1이다.

마지막으로  x1 = x * w = 2 * w이므로, w가 epsilon 변하면 x1은 2 * epsilon만큼 변한다. 그래서 grad(x1, w)는 2이다. 곱셈에서 w에 대한 도함수는 곱해지는 상대편 값, 즉 x=2가 되는 것이다. 이렇게 에지마다 국소 도함수를 구한다.

이제 연쇄 법칙을 적용하면, 관심 있는 두 노드를 잇는 경로를 따라가며 그 위에 적힌 에지 도함수들을 전부 곱하면 한 노드가 다른 노드에 미치는 전체 도함수가 나온다.

<img width="1280" height="1012" alt="image" src="https://github.com/user-attachments/assets/ae496acf-ec30-4190-a019-2843cb72fdeb" />

loss_val에서 w까지 가는 경로는 loss_val → x2 → x1 → w이므로 이 경로 위의 값을 곱하면 된다.

```plain text
grad(loss_val, w) = grad(loss_val, x2) * grad(x2, x1) * grad(x1, w)
                  = 1 * 1 * 2 = 2
grad(loss_val, b) = grad(loss_val, x2) * grad(x2, b)
                  = 1 * 1 = 1
```plain text

만약 두 노드를 잇는 경로가 여러 갈래라면, 각 경로마다 이렇게 곱해서 얻은 값을 전부 더해야 grad(a, b)가 된다. 

역전파는 맨 끝에서 나온 최종 손실 값에서 출발해 그래프를 거꾸로 거슬러 올라가면서 각 파라미터가 그 손실에 얼마나 기여했는지를 계산한다. 손실에 대한 기여도가 뒤에서 앞으로 거꾸로 전파되기 때문에 역전파라고 한다. 각 노드에 대해 최종 손실을 얼마나 좌우하는지 값을 뒤에서부터 흘려보내는것이다.

###

#출처

책 케라스 창시자에게 배우는 딥러닝
