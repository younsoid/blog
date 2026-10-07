---
date : 2026-10-07
tags: ['2026-10']
categories: ['pretrained-model', 'fine-tuning']
bookHidden: true
title: "사전 훈련 모델의 파인 튜닝"
bookComments: true
index: 2
---

# 사전 훈련 모델의 파인 튜닝

#2026-10-07

---

사전 학습 모델을 사용하는 첫번째 방법은 특성 추출이었고 두번째 방법은 파인 튜닝이다. 

파인 튜닝은 앞서 동결했던 합성곱 기반 층을 (상위 층) 필요에 따라 일부 동결 해제하고 모델에 새로 추가한 층과 함께 훈련하는 것이다. 사전 학습 모델의 "이미지에 대한 이해"를 내 이미지 데이터에 조금더 밀접하게 이해하도록 조정하는 것이다. 즉 모델의 표현을 주어진 데이터셋에 좀더 밀접한 표현으로 만드는 것이다.

파인 튜닝 구현 순서는 다음과 같다

1. 사전 학습된 기반 네트워크 위에 새로운 네트워크를 추가한다.
2. 기반 네트워크를 동결한다.
3. 새로운 네트워크를 훈련한다.
4. 기반 네트워크의 일부 층을 동결 해제한다. (batch normalization 층 제외)
5. 동결 해제한 층과 새로운 네트워크를 같이 훈련한다.

```python
# 기존 모델
conv_base = keras.applications.vgg16.VGG16(
  weights="imagenet",
  include_top=False)

conv_base.trainable = False

# 마지막 ~ 4번째 층만 동결
conv_base.trainable = True

for layer in conv_base.layers[:-4]:
  layer.trainable = False
```

합성곱 층 conv_base input은 (180, 180, 3) 크기의 텐서이고 output인 최종 특성맵은 (5, 5, 512) 텐서였다. 기존에는 conv_base.trainable = False로 전체 동결했었던걸, 최상위 3개 층을 제외하고 동결하는 방법으로 수정한다.

```python
model.compile(loss="binary_crossentropy",
              optimizer=keras.optimizers.RMSprop(learning_rate=1e-5), # 특성 추출때는 "rmsprop"
              metrics=["accuracy"])

callbacks = [
  keras.callbacks.ModelCheckpoint(
      filepath="fine_tuning.h5",
      save_best_only=True,
      monitor="val_loss")
]
history = model.fit(
  train_dataset,
  epochs=30,
  validation_data=validation_dataset,
  callbacks=callbacks)
```

다음으로 파인튜닝을 해준다. optimizer로 학습률을 낮춘 RMSprop를 사용하는데, 미세 조정하는 3개의 층에서 표현을 조금씩만 수정하기 위해서이다. 

테스트 데이터에서 평가 결과, 98.5% 정확도가 나온다고 한다. 

###

#출처

책 케라스 창시자에게 배우는 딥러닝
