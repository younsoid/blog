---
date : 2026-10-06
tags: ['2026-10']
categories: ['pretrained-model', 'feature-extraction']
bookHidden: true
title: "사전 훈련 모델과 특성 추출"
bookComments: true
index: 3
---

# 사전 훈련 모델과 특성 추출

#2026-10-06

---

### 1. 사전 훈련 모델

이미지 데이터셋은 대개 데이터셋이 모델 크기에 비해 좀 작다. 그래서 대량의 데이터셋에서 사전 훈련된 모델을 많이 쓴다. 이 모델이 학습한 특성의 계층 구조를 실제 세상에 대한 일반적인 특성으로 보는 것이다.

사전 훈련에 사용할수있는 데이터셋으로는  1400만개의 레이블된 이미지와 12000개 클래스로 구성된 ImageNet-21K 데이터셋이 있는데, 보통 훈련에는 128만개 이미지와 1000개 클래스로 구성된 ImageNet-1K 데이터셋을 사용한다고 한다. 유명한 컨브넷 모델로는 VGG, ResNet, Inception, Xception등이 있다. 

요즘은 컨브넷 외에도 비전 트랜스포머(ViT)나 이를 반영한 ConvNeXt 같은 사전 훈련 모델을 많이 쓴다고 한다. 학습 방식도 레이블 없이 스스로 학습하는 자기지도 학습(DINOv2)이나 이미지와 텍스트 쌍으로 학습하는 방식(CLIP)이 생기면서 레이블 없는 이미지도 훈련에 사용해서, ImageNet보다 더 큰 데이터셋으로 사전 훈련된 모델들이 많다.

### 2. 특성 추출

사전 훈련된 모델은 2가지 방법으로 사용할수있다. 첫번째는 '이미지'에 대한 이해가 있는 그 모델을 사용해서 내 이미지들의 특성을 추출하는것이고 두번째는 그 모델을 내 이미지에 맞게 미세조정하는것이다. 

컴퓨터 비전 모델을 사용해서 내 이미지에서 특성을 추출하면, '이미지'는 못 받지만 '특성'은 입력으로 받을 수 있는 다른 모델을 사용해서 새로운 분류 또는 예측 모델을 훈련시킬수 있다.

컴퓨터 비전 모델 중 컨브넷을 사용한다고 하면, 사전 훈련된 컨브넷에서 특성 추출하고 새로운 분류기를 학습하는 것은 어떻게 구현될까? 

컨브넷이 "연속 합성곱과 풀링 층 -> 밀집 연결 분류기" 구성인데 "연속 합성곱과 풀링 층"은 유지하고 밀집 연결 분류기만 갈아 끼우면 된다. 분류기만 새롭게 훈련시키면 기존 모델로 특성 추출하고 새롭게 분류기를 훈련시키는 것을 구현하는것이 된다.

연속 합성곱과 풀링 층은 "이미지에 대한 이해"여서 남기는 것이고 밀집 연결 분류기는 상대적으로 그 모델이 학습한 데이터 집합에 특화된 경향이 있어서 합성곱 층만 재사용하고 밀집 연결 분류기는 재사용을 권장하지 않는다.

### 3. 추출한 표현의 일반성

연속 합성곱과 풀링 층에서, 특정 합성곱 층에서 끊고 특성을 추출할 수도 있다.

추출한 특성의 일반성 즉 재사용성 수준은 그 특성을 추출한 층의 깊이와 관련있다. 모델의 하위 층은 일반적인 특성맵을 추출하고(테두리, 색깔 등) 상위 층은 데이터 집합의 추상적인 개념을 담는다(강아지 눈, 고양이 귀 등). 

그래서 모델이 훈련할때 쓴 데이터셋과 내 데이터셋이 많이 다르다면 모델의 하위 층 몇개만 특성 추출에 사용하는것이 좋다.

다만 하위층 특성은 일반적인 대신 그 자체로는 판별력이 약해서, 그 위에 붙이는 모델이 더 많은 걸 스스로 학습해야 하고 그러려면 내 데이터가 어느 정도 있어야 한다.

또 하위 층 출력은 공간 해상도가 커서 특성의 크기가 훨씬 크고 그만큼 계산과 저장 부담도 커서, 실무에서는 하위 층만 고르는 것보다 전체를 쓰되 상위 몇 개 층을 미세 조정하거나, 여러 층의 특성을 함께 이어 붙여(concatenate) 쓰는 방식을 많이 쓴다고 한다.

그리고 "상위 층은 원래 과제에 특화된다"는 경향은 지도 학습 모델에서 강한 편이고, DINOv2나 DINOv3 같은 자기지도 학습 모델은 특정 클래스 맞히기가 목표가 아니었기 때문에 마지막 층 특성도 꽤 범용적이라서 백본 전체를 고정해 그대로 쓰는 경우도 많다.

### 4. 실습

이미지 분류기를 사전 학습 모델로 사용해서 강아지 vs 고양이 분류기를 만들려고 한다. 

ImageNet 데이터셋으로 훈련한 VGG16 네트워크의 합성곱 층을 사용해서 강아지와 고양이 이미지의 특성을 추출하고, 추출한 특성으로 강아지, 고양이 분류기를 훈련시킨다.

```python
conv_base = keras.applications.vgg16.VGG16(
  weights="imagenet",
  include_top=False,
  input_shape=(180, 180, 3))
```

먼저 합성곱 층을 만들면, input은 (180, 180, 3) 크기의 텐서이다. output인 최종 특성맵은 (5, 5, 512) 텐서이고, 추출한 특성 위에 밀집 연결 층을 놓을 것이다. 여기서 두가지 방식이 가능하다.

첫번째는 추출한 특성 맵을 저장해두고, 내가 사용하고싶은 다른 밀집 연결 분류기에 입력으로 사용한다. 특성맵을 input으로 받을수있는 모델이라면 (flatten으로 펴거나 pooling을 거쳐서) 무엇이든 밀집연결 분류기로 사용할 수 있다. 

이렇게 하면 내가 가진 이미지 데이터들은 합성곱 층을 1번 지나고 나서는 지나지 않기 때문에 연산 비용이 적고 빠르다.

두번째는 기존 모델 conv_base 위에 Dense 층을 쌓아서 확장하고, 입력 데이터 (아까 (180, 180, 3) 크기였던 그 부분) 부터 엔드투 엔드로 기존 모델의 전체 파이프라인을 돌린다.

이렇게 하면 내 이미지 데이터들이 합성곱 층을 지나기 때문에 데이터 증식을 사용할 수 있다. 

```python
def get_features_and_labels(dataset):
  ...
  return np.concatenate(all_features), np.concatenate(all_labels)

train_features, train_labels = get_features_and_labels(train_dataset)
val_features, val_labels = get_features_and_labels(validation_dataset)
test_features, test_labels = get_features_and_labels(test_dataset)

train_features.shape # (2000, 5, 5, 512)
```

먼저 첫번째 방법인 빠른 특성 추출을 해보면, VGG16 모델인 conv_base의 predict()를 사용해서 array 형태의 특성인 train_features, val_features, test_features를 추출할 수 있다. 특성 맵의 크기는 (samples, 5, 5, 512)이다.

```python
inputs = keras.Input(shape=(5, 5, 512))
x = layers.Flatten()(inputs) # Dense 층에 특성을 주입하기 전에 Flatten 층을 사용
x = layers.Dense(256, activation="relu")(x)
x = layers.Dropout(0.5)(x)
outputs = layers.Dense(1, activation="sigmoid")(x)
model = keras.Model(inputs, outputs)
model.compile(loss="binary_crossentropy",
              optimizer="rmsprop",
              metrics=["accuracy"])
callbacks = [
  keras.callbacks.ModelCheckpoint(
      filepath="feature_extractions.h5",
      save_best_only=True,
      monitor="val_loss")
]
history = model.fit(
  train_features, train_labels,
  epochs=20,
  validation_data=(val_features, val_labels),
  callbacks=callbacks)
```

다음으로 밀집 연결 분류기를 위 feature, label을 사용해서 훈련한다. 2개의 Dense 층만 처리하면 돼서 훈련이 매우 빠르다.

훈련과 검증 데이터의 결과를 가지고 훈련 과정에서의 손실과 정확도를 그래프로 확인해보면, 약 97%의 정확도에 도달한다고 한다. 정확도가 높은 이유는 사전 학습 모델 conv_base가 학습한 데이터셋인 ImageNet에 개, 고양이 샘플이 많았기 때문이고 대부분의 경우 사전 훈련된 특성이 내가 분류하고자하는 라벨에 대해서 이정도의 이해도를 가지고 있지 않다.

그리고 드롭아웃을 사용했음에도 훈련을 시작하면서 거의 바로 과대적합 되고있는데, 이미지 데이터처럼 작은 데이터셋에서는 과대적합을 막기 위해 데이터 증식은 거의 필수이기 때문이다.

```python
conv_base = keras.applications.vgg16.VGG16(
  weights="imagenet",
  include_top=False)

conv_base.trainable = False
```

두번째로 데이터 증식을 사용한 특성 추출을 수행한다. 다른건 똑같고 conv_base.trainable = False를 해주면 되는데, 앞의 방법에서는 conv_base가 predict()로써만 사용되어서 가중치 변동이 없었는데 이번에는 conv_base의 fit()도 사용되어서 가중치가 업데이트되게된다. 이때 합성곱 층을 동결하지 않으면 합성곱 층의 가중치가 수정되는데, 새로 붙이는 Dense 층은 무작위로 초기화되어 있어서 처음에 아주 큰 오차 신호를 보내기 때문에 동결하지 않으면 사전 학습된 표현이 크게 훼손된다.

```python
data_augmentation = keras.Sequential(
  [
    layers.RandomFlip("horizontal"),
    layers.RandomRotation(0.1),
    layers.RandomZoom(0.2),
  ]
)

inputs = keras.Input(shape=(180, 180, 3)) # 아까는 특성맵의 크기인 (5, 5, 512)였다
x = data_augmentation(inputs)
x = keras.applications.vgg16.preprocess_input(x)
x = conv_base(x)
x = layers.Flatten()(x) # 아까는 input 다음에 바로 Flatten 층, layers.Flatten()(inputs)였다.
x = layers.Dense(256)(x) # 아까와 동일
x = layers.Dropout(0.5)(x) # 아까와 동일

outputs = layers.Dense(1, activation="sigmoid")(x)
model = keras.Model(inputs, outputs)
model.compile(loss="binary_crossentropy",
              optimizer="rmsprop",
              metrics=["accuracy"])
```

다음으로 "데이터 증식 - (동결된) 합성곱 층 - 밀집 분류기"로 구성된 새로운 모델을 만든다. 이렇게 하면 conv_base는 건드리지 않고 추가한 Dense층 2개만 훈련한다. 층마다 2개씩(가중치 행렬과 편향 벡터) 총 4개의 텐서가 훈련된다.

```python
callbacks = [
  keras.callbacks.ModelCheckpoint(
      filepath="feature_extractions.h5",
      save_best_only=True,
      monitor="val_loss")
]
history = model.fit(
  train_dataset,# 아까는 train_features, train_labels
  epochs=50, # 아까는 20
  validation_data=validation_dataset, # 아까는 (val_features, val_labels)
  callbacks=callbacks)
```

훈련을 해주고 정확도를 확인하면 97.5%가 나온다.

###

#출처

책 케라스 창시자에게 배우는 딥러닝
