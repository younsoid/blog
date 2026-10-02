---
date : 2025-09-15
tags: ['2025-09']
categories: ['스터디', 'Ray']
bookHidden: true
title: "Ray #1 Batch Prediction with Ray Core"
---

# Ray #1 Batch Prediction with Ray Core

#2025-09-15

---

스터디때 준비해갔던 Ray Core를 사용해서 batch prediction 수행하는 예제!!

- batch prediction이 batch를 예측하는건줄알았는데(..) batch로 prediction하는것이었다. 
- 순서는 1. Task 기반 batch prediction 2. Actor 기반 batch prediction 3. GPU 기반 수행 코드
- 출처는 Ray Document의 [Batch Prediction with Ray Core](https://docs.ray.io/en/latest/ray-core/examples/batch_prediction.html)이다. 

###

### 0. 개요

- 목적
  - Parquet 형식의 대규모 데이터셋을 Ray를 이용해 분산 처리하며, 더미 모델을 로딩하여 배치 예측(batch prediction) 을 수행한다.
  - Task와 Actor 두 가지 실행 방식을 비교하고, CPU/GPU 자원 활용 차이를 이해한다.
- 설계
  - 데이터셋 분할: S3에 저장된 Parquet 파일(12 shards)을 불러와 분산 태스크 단위로 처리
  - 모델 로딩: 더미 모델(load_model)을 정의하고 ray.put()을 통해 오브젝트 스토어에 1회 저장
  - 배치 예측(Task 기반): @ray.remote 태스크로 각 shard를 병렬 예측, 결과 크기 반환
  - 배치 예측(Actor 기반): BatchPredictor 클래스를 Ray Actor로 등록하고, ActorPool을 이용해 shard 분산 예측
  - 자원 활용(CPU/GPU): CPU 환경에서는 기본 Task 실행, GPU 환경에서는 @ray.remote(num_gpus=1)를 사용해 GPU에서 모델을 실행하도록 구성
  - 결과 확인: 각 shard에 대해 예측된 결과 크기를 출력하여 병렬 처리 동작을 검증

###

### 1. 코드

```python
# 0. 환경 준비
!pip -q install ray pandas pyarrow s3fs torch

# 1. Ray 초기화
import ray
ray.init()
```

```python
# 2. 더미 모델 정의
import pandas as pd
import numpy as np

def load_model():
    # A dummy model
    def model(batch: pd.DataFrame) -> pd.DataFrame:
        model.payload = np.zeros(100_000_000)
        return pd.DataFrame({"score": batch["passenger_count"] % 2 == 0})
    return model
```

- 실습에서는 분산 처리 흐름을 보는 것이 핵심이기 때문에 실제 모델이 갖는 특성을 갖는 더미 모델을 생성해준다.
  - 실제 모델이 갖는 특성 = 정확히는 실제 모델이 갖는 특성 중 분산 처리에 관여하는 특성.
- 실제 모델이 갖는 특성 2가지? 
  1. 큰 메모리 용량. 실제 머신러닝 모델, 특히 딥러닝 모델은 수백 MB에서 수 GB에 달하는 가중치 파라미터를 담고 있다 예를 들어 BERT나 GPT 같은 모델은 엄청난 수의 파라미터를 갖기 때문에, 한 노드에서 다른 노드로 옮길 때 그 자체로 데이터 전송 비용이 크므로 이를 구현해준다.
  2. 입력 데이터를 받아서 변환된 출력을 만듭니다. 실제 모델은 어떤 입력(이미지, 텍스트, 테이블 데이터 등)을 받아서 예측값을 내놓으므로, 이를 구현해줍니다.
- 구현 방법? 
  1. model.payload = np.zeros(100_000_000)
   - 큰 메모리의 가중치 파라미터를 담고 있음을 모방하는 코드. 모델이 내부적으로 “큰 덩어리” 데이터를 가진 객체처럼 보이며 이를 통해 Ray가 이 모델을 여러 노드에 배포할 때 진짜처럼 부담을 준다. 
  2. {"score": batch["passenger_count"] % 2 == 0}
   - 입력값을 받아서 예측값을 내놓음을 모방하는 코드. 모델은 dataframe을 input으로 받아 승객 수가 짝수냐 홀수냐를 판별한다 즉 “입력 데이터를 보고 뭔가 계산해서 새로운 결과를 만든다”라는 모델의 핵심 행위만 구현한다. 

###

<mark>1. Task 기반 batch prediction</mark>

```python
# 3. 기본 Task 기반 배치 예측
import pyarrow.parquet as pq

@ray.remote
def make_prediction(model, shard_path):
    df = pq.read_table(shard_path).to_pandas()
    result = model(df)
    return len(result)

# 12개의 S3 parquet 파일
input_files = [
    f"s3://anonymous@air-example-data/ursa-labs-taxi-data/downsampled_2009_full_year_data.parquet"
    f"/fe41422b01c04169af2a65a83b753e0f_{i:06d}.parquet"
    for i in range(12)
]

model = load_model()
model_ref = ray.put(model)
```

- Ray에서 Task 기반 분산처리란? 
  - 데이터 파일을 통째로 처리하지 않고 여러 조각(Task)으로 잘라 각 조각을 서로 다른 Worker에게 맡기기.
- 코드 설명
  - input_files
    - 2009년 뉴욕시 택시 데이터. parquet 포맷이며 12개 데이터로 구성
  - function make_prediction(model, shard_path)
    - shard 파일 경로를 받아서 pyarrow.parquet.read_table(shard_path)로 데이터를 불러고 df로 변환해서 더미 모델 model에 입력
      - 앞서 더미 모델인 model은 passenger_count 값이 짝수인지 여부를 판단해서 불리언 값으로 반환하는 모델이었다!
  - ray.put(model)
    - 모델이 큰 메모리 객체를 내부적으로 가지고 있고(payload=1억) 따라서 매번 모델을 직접 태스크로 전달하면 드라이버의 오브젝트 스토어가 과부하될 수 있다. 
    - 그래서 ray.put(model)을 사용해서 모델을 오브젝트 스토어에 단 한 번만 저장하고 이후 태스크에는 그 참조값 model_ref 만 넘긴다.
    - 이렇게 해야 각 태스크가 동일한 모델을 공유하되 불필요한 데이터 복제가 발생하지 않는다.

###

<mark>cf1</mark>

- 의문점1
  - ray.put(model)을 해야 각 태스크가 동일한 모델을 공유하되 불필요한 데이터 복제가 발생하지 않는다고 했는데 
    - 모델을 ray.put()으로 한 번만 넣었을 때와, 매번 remote 호출마다 모델을 넘겼을 때 오브젝트 스토어 메모리 사용량 차이는 얼마일까?
- 확인1
  - Ray에서 메모리 현황을 ray memory 명령어를 통해 확인할 수 있음
  - 위의 두 Case 에서 ray memory를 호출하여 메모리 사용량과 참조 개수를 확인해보면 Ray 오브젝트 스토어에 몇 개의 모델 사본이 올라갔는지, 그리고 참조 개수가 어떻게 달라졌는지를 확인해서 메모리 사용량 차이 확인이 가능!

```python
# cf) 모델을 ray.put()으로 한 번만 넣었을 때와, 매번 remote 호출마다 모델을 넘겼을 때 오브젝트 스토어 메모리 사용량 차이
# 샘플 파일 하나만 사용
sample_file = "s3://anonymous@air-example-data/ursa-labs-taxi-data/downsampled_2009_full_year_data.parquet/fe41422b01c04169af2a65a83b753e0f_000000.parquet"

# 1. 올바른 방식 (ray.put(model) → 참조 전달)
print("=== Good Case: ray.put(model) 사용 ===")
model = load_model()
model_ref = ray.put(model)

# 같은 참조값만 여러 태스크에 전달
good_refs = [make_prediction.remote(model_ref, sample_file) for _ in range(3)]
ray.get(good_refs)

# 메모리 상황 확인
!ray memory | head -20

# 2. 잘못된 방식 (매번 모델 직접 전달)
print("=== Bad Case: 모델 직접 전달 ===")
model = load_model()

# 모델 자체를 매번 넘기면, 태스크마다 ray.put이 내부적으로 발생 → 중복 저장
bad_refs = [make_prediction.remote(model, sample_file) for _ in range(3)]
ray.get(bad_refs)

# 메모리 상황 확인
!ray memory | head -20
```
```plain text
=== Good Case: ray.put(model) 사용 ===
2025-09-12 21:10:44,955 - INFO - NumExpr defaulting to 2 threads.
======== Object references status: 2025-09-12 21:10:45.563194 ========
Grouping by node address...        Sorting by object size...        Display allentries per group...


--- Summary for node address: 172.28.0.12 ---
Mem Used by Objects  Local References  Pinned        Used by task   Captured in Objects  Actor Handles
950.0 B              4, (950.0 B)      0, (0.0 B)    0, (0.0 B)     0, (0.0 B)           0, (0.0 B)   

--- Object references for node address: 172.28.0.12 ---
IP Address    | PID      | Type    | Call Site | Status    | Attampt  | Size     | Reference Type | Object Ref

172.28.0.12   | 1502     | Driver  | disabled  | FINISHED  | 1        | 19.0 B   | LOCAL_REFERENCE | 16310a0f0a45af5cffffffffffffffffffffffff0100000001000000


172.28.0.12   | 1502     | Driver  | disabled  | FINISHED  | 1        | 19.0 B   | LOCAL_REFERENCE | c8ef45ccd0112571ffffffffffffffffffffffff0100000001000000


172.28.0.12   | 1502     | Driver  | disabled  | FINISHED  | 1        | 19.0 B   | LOCAL_REFERENCE | c2668a65bda616c1ffffffffffffffffffffffff0100000001000000


=== Bad Case: 모델 직접 전달 ===
2025-09-12 21:10:53,384 - INFO - NumExpr defaulting to 2 threads.
======== Object references status: 2025-09-12 21:10:53.860894 ========
Grouping by node address...        Sorting by object size...        Display allentries per group...


--- Summary for node address: 172.28.0.12 ---
Mem Used by Objects  Local References  Pinned        Used by task   Captured in Objects  Actor Handles
1007.0 B             7, (1007.0 B)     0, (0.0 B)    0, (0.0 B)     0, (0.0 B)           0, (0.0 B)   

--- Object references for node address: 172.28.0.12 ---
IP Address    | PID      | Type    | Call Site | Status    | Attampt  | Size     | Reference Type | Object Ref

172.28.0.12   | 1502     | Driver  | disabled  | FINISHED  | 1        | 19.0 B   | LOCAL_REFERENCE | 16310a0f0a45af5cffffffffffffffffffffffff0100000001000000


172.28.0.12   | 1502     | Driver  | disabled  | FINISHED  | 1        | 19.0 B   | LOCAL_REFERENCE | c8ef45ccd0112571ffffffffffffffffffffffff0100000001000000


172.28.0.12   | 1502     | Driver  | disabled  | FINISHED  | 1        | 19.0 B   | LOCAL_REFERENCE | 32d950ec0ccf9d2affffffffffffffffffffffff0100000001000000
```

- 결과
  - Mem Used by Objects 비교
    - Good Case - 1178.0 B
    - Bad Case - 1235.0 B
    - 비슷한이유는뭘까? 더미 데이터에서 파라미터 부하를 모방한다고 작성한 np.zeros(100_000_000)은 실제로는 800MB짜리 배열이어야 하지만 Ray와 NumPy 내부에서 메모리 최적화 (zero-copy, lazy allocation) 때문에 실제 크기가 반영되지 않았고 ray memory 출력에서도 몇 백 byte 수준으로 나왔다.
  - Mem Used by Objects 비교 - 실제 숫자를 넣어줫다면?
    - model.payload = np.random.rand(100_000_000)처럼 랜덤 값을 채우면 실제 메모리가 할당되었을것이고(float64 → 약 800MB)
    - 이경우 Good Case (ray.put(model) 한 번)는 Mem Used by Objects ≈ 800MB, Bad Case (태스크 3개에 직접 모델 전달) Mem Used by Objects ≈ 2400MB (800MB × 3) 가 출력되었을것이다. 즉, 모델 크기 × 태스크 수 만큼 차이가 벌어지는 게 일반적인 결과!
  - Local References 비교
    - Good Case - 16
    - Bad Case - 19
    - 결과설명? ray.put(model)을 호출 후 생성된 ObjectRef는 오브젝트 스토어에 저장된 모델을 가리키는 “포인터” 같은 역할을 한다. 
      - Good Case에서는 드라이버 프로세스(파이썬에서 코드를 실행하는 쪽)와 태스크 실행 시 필요한 내부 참조들이 모두 합쳐져서 16개 참조가 생겼다 즉 모델 사본은 1개지만 그 사본을 가리키는 참조가 16개 있다.
      - Bad Case와 같이 모델을 직접 태스크 인자로 넘기면 태스크가 실행될 때마다 Ray 내부적으로 새로운 ray.put(model) 이 실행되고 따라서 태스크 3개를 실행하면 모델 사본이 3개 만들어지고, 각각의 사본에 대해 참조가 따로 생기고 Good Case에서 16이었던 값이 3 증가해서 19가된다 즉 여기서 +3은 곧 태스크 개수만큼 늘어난 중복 ref 숫자.
    - 메모리 사본이 중복 생성되면(중복 참조되면) 왜 안되는가?
        - 모델이 태스크 개수만큼 복제돼서 올라가서, 만약 모델이 800MB라면 태스크가 3개면 2.4GB, 10개면 8GB까지 차지하게 되니까 메모리 낭비가 발생하고 큰 모델을 쓰면 금방 object store OOM(Out Of Memory) 에러가 난다
        - 작은 더미 모델일 땐 차이가 안 드러나지만, 실제 대형 모델(PyTorch, TensorFlow 등)을 쓰면 시스템이 바로 느려지고 OOM으로 죽을 수 있다.

###

```python
result_refs = [make_prediction.remote(model_ref, f) for f in input_files]
results = ray.get(result_refs)

for r in results:
    print("Prediction output size:", r)
```

- make_prediction
  - 각 parquet 파일을 읽어 데이터프레임으로 만든 뒤, 더미 모델을 적용했다. 더미 모델은 `passenger_count`가 짝수인지 여부를 판별해서 불리언(`True`/`False`) 값을 반환하구
  - 12개 파일에 대해 잘 수행되었다!!

###

<mark>2. Actor 기반 batch prediction</mark>

```python
# 4. Actor 기반 배치 예측
@ray.remote
class BatchPredictor:
    def __init__(self, model):
        self.model = model

    def predict(self, shard_path):
        df = pq.read_table(shard_path).to_pandas()
        result = self.model(df)
        return len(result)
```

- Ray의 Actor 기반 분산처리?
  - 모델을 Actor 안에 올려 상태를 유지하고, 여러 Actor를 풀로 관리해 병렬성을 확보.
- @ray.remote class BatchPredictor
  - 함수 대신 클래스가 원격 실행 단위로 선언되어 있음.
  - 참고로 Task에서는 다음과 같이 선언돼있었는데

```python
@ray.remote
def make_prediction(model, shard_path):
    df = pq.read_table(shard_path).to_pandas()
    result = model(df)
    return len(result)
```
- 보면 self.model 같은 멤버 변수가 없고, 그냥 model이라는 인자를 받는다. 
- result = model(df)처럼 함수의 인자로 모델을 받아 쓰고 함수가 끝나면 모델은 사라지고, 다음 작업에서는 또 다시 같은 model_ref를 넘긴다. 

###

```python
@ray.remote
class BatchPredictor:
    def __init__(self, model):
        self.model = model

    def predict(self, shard_path):
        df = pq.read_table(shard_path).to_pandas()
        result = self.model(df)
        return len(result)

from ray.util.actor_pool import ActorPool

model = load_model()
model_ref = ray.put(model)

# Actor 4개 생성
actors = [BatchPredictor.remote(model_ref) for _ in range(4)]
pool = ActorPool(actors)

for file in input_files:
    pool.submit(lambda a, v: a.predict.remote(v), file)
```

- 원래 코드로 돌아와서 보면,,
- `__init__` 안에서 self.model = model을 저장하면 모델은 Actor의 상태로 남는다. 따라서 한 번 생성된 Actor는 이후 여러 shard 데이터를 받아도 같은 모델을 반복해서 활용한다.
  - 이게 Actor의 가장 중요한 특징인데 단순 태스크에서는 매번 model_ref를 전달하고 실행이 끝나면 상태가 사라지지만, Actor에서는 이 모델이 메모리에 계속 붙어있다.
- actors = [BatchPredictor.remote(model_ref) for _ in range(4)]
  - 네 개의 Actor 인스턴스를 생성. 각각은 독립된 워커 프로세스로 Ray 클러스터 안에 배치된다 즉, 네 개의 예측기가 동시에 shard 파일을 읽고 결과를 계산할 수 있다.
- ActorPool
  - Actor를 관리하는 유틸리티. 여러 Actor를 모아두고, 사용할 수 있는 Actor가 생기면 작업을 하나씩 할당한다.
- for file in input_files: pool.submit(lambda a, v: a.predict.remote(v), file)
  - a는 Actor 하나, v는 shard 파일 경로.
  - 제출된 작업은 내부적으로 큐에 쌓이고 Actor가 놀고 있으면 즉시 할당되기 때문에, 사용자가 Actor 스케줄링을 직접 신경 쓰지 않고도 여러 데이터를 효율적으로 분배할 수 있다.

```python
while pool.has_next():
    print("Prediction output size:", pool.get_next())
```

- 결과 수집 루프 (while pool.has_next())
  - 결과 수집 루프 돌렸고 12개 파일에 대해 정상적으로 수행!!

###

<mark>cf2</mark>

- 의문점2
  - Actor 기반 방법은 모델을 Actor 안에 올려 상태를 유지하고, 여러 Actor를 풀로 관리해 병렬성을 확보한다구했다. 
  - 궁극적으로 Task 기반과의 성능 차이?
- 확인2
  - Task 기반과 Actor 기반 실행에서 시작 시간과 종료 시간을 time으로 측정하면 실행 시간을 확인해볼수 있다.

```python
# cf) Task 기반과의 차이?
# 데코레이터 정의
def benchmark(title):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            print(f"=== {title} ===")
            times = func(*args, **kwargs)
            print("개별 shard 실행 시간:", times)
            print("총합:", sum(times), "초\n")
            return times
        return wrapper
    return decorator

# 실행 함수
@benchmark("Task 기반 실행 (매번 모델 로딩)")
def run_task(input_files):
    refs = [make_prediction_task.remote(f) for f in input_files]
    return ray.get(refs)

@benchmark("Actor 기반 실행 (한 번만 로딩)")
def run_actor(input_files):
    model = load_model()
    model_ref = ray.put(model)
    actor = BatchPredictor.remote(model_ref)
    refs = [actor.predict.remote(f) for f in input_files]
    return ray.get(refs)

# 실행
input_files = [
    f"s3://anonymous@air-example-data/ursa-labs-taxi-data/downsampled_2009_full_year_data.parquet"
    f"/fe41422b01c04169af2a65a83b753e0f_{i:06d}.parquet"
    for i in range(12)
]

task_times = run_task(input_files)
actor_times = run_actor(input_files)
```
```plain text
2025-09-12 21:11:27,088	INFO worker.py:1789 -- Calling ray.init() again after it has already been called.
=== Task 기반 실행 (매번 모델 로딩) ===
개별 shard 실행 시간: [2.5572421550750732, 2.420006036758423, 2.561861991882324, 2.557760238647461, 2.540508508682251, 2.517340660095215, 2.5709900856018066, 2.5400502681732178, 2.5643177032470703, 2.8599958419799805, 3.399395704269409, 2.549189567565918]
총합: 31.63865876197815 초

=== Actor 기반 실행 (한 번만 로딩) ===
개별 shard 실행 시간: [2.7201454639434814, 2.5550737380981445, 2.527881383895874, 2.5825955867767334, 2.5718047618865967, 2.3835108280181885, 2.997328519821167, 2.4681167602539062, 2.5404725074768066, 2.573448419570923, 2.5259084701538086, 2.53125]
총합: 30.97753643989563 초
```

- 결과
  - 실행 시간 비교
    - Task 기반: 대부분 2.5초대, 몇몇 shard는 2.8~3.3초 소요 / 총합 31.63초
    - Actor 기반: 대부분 2.4~2.7초에 안정적으로 분포 / 총합 30.97초
  - 실행 시간에 영향을 주는 요소 중 Task와 Actor의 방식 차이와 직접적으로 연관된 요소는?
    - 모델 로딩 비용: 로딩 비용을 매번 치르느냐, 한 번만 치르느냐.
    - 모델 로딩 비용은 load_model() 안에서 np.zeros(100_000_000)을 만들면서 메모리 초기화할때 발생하는데, 한 번 할 때마다 0.5~1초 가까운 오버헤드가 발생할 수 있고 이게 Task 기반에서는 shard마다 반복되고, Actor 기반에서는 딱 한 번만 발생한다.
  - 일반적인 결과 차이
    - 모델이 커지거나 연산량이 많아지면, Task 기반 방식은 shard 수가 많아질수록 모델을 계속 새로 불러야 하니 실행 시간이 선형적으로 증가하고 Actor 기반 방식은 초기 한 번만 로딩, 이후에는 오로지 데이터 I/O + 추론만 걸리므로 평균 실행 시간이 안정적이고 훨씬 짧다. 즉, 일반적으로는 Actor 기반이 훨씬 빠르고 안정적이다.
  - 이번 결과에서 두 방식의 총합이 31.6초 vs 31.0초로 거의 비슷했던 이유?
    - 데이터 I/O가 지배적이었기 때문 즉 12개의 parquet 파일을 병렬로 읽는 데 걸리는 시간이 모델 로딩 비용보다 더 크게 작용했기 때문에 비슷하게 나왔다.
    - 모델 로딩이 실제로는 몇백 MB 정도라 현대 CPU/메모리 환경에서는 빠르게 끝났고 따라서 “모델 로딩 절약 효과”가 “I/O 지연 변동”에 묻힌듯하다 데이터가 단순해서 모델 로딩 오버헤드가 확인이잘안됐다.

###

<mark>3. GPU에서 실행</mark>

- 을 설명하기 앞서 현재까지 진행된 내용을 정리하면? 
  - 기본 Task 기반 배치 예측
    - @ray.remote 태스크로 파일 단위(shard) 배치를 실행
    - Ray에서 여러 파일을 나눠 태스크로 돌리면 이렇게 분산 병렬 예측을 할 수 있다.
  - Actor 기반 배치 예측
    - BatchPredictor라는 클래스를 @ray.remote로 선언해서, 한 번 생성된 Actor 내부에 모델을 올려두었고 모델을 계속 재사용하는 장기 실행 프로세스를 사용
    - 계속 모델을 다시 올리지 않고, 같은 Actor 안에서 여러 shard를 처리할 수 있다.
  - GPU Task 기반 배치 예측 
    - 다음 코드에서는 GPU 자원을 요구하는 태스크를 실행
    - 앞선 2개 코드에서는 CPU 배치 예측을 수행했는데, Ray Core로 GPU 자원 스케줄링도 가능하며 @ray.remote(num_gpus=1)로 GPU 할당, model.to("cuda")로 GPU 메모리를 이동하여 수행할거고
    - GPU 리소스도 Ray가 알아서 분산 배치할 수 있고, 모델은 GPU 메모리에 옮겨야 함을 확인할예정.

###

```python
# 5. GPU Task 예시 (PyTorch)
import ray
print(ray.cluster_resources())
```
```plain text
{'node:__internal_head__': 1.0, 'CPU': 2.0, 'object_store_memory': 3977052979.0, 'node:172.28.0.12': 1.0, 'memory': 9279790285.0, 'GPU': 1.0, 'accelerator_type:T4': 1.0}
```

- ray.cluster_resources
  - 현재 Ray 클러스터에 등록된 전체 자원(capacity)을 확인해본결과 다음과 같다.
- CPU: 2.0
  - Ray가 인식한 논리 CPU 코어 수는 2개
  - 현재 클러스터 전체에서 2개의 CPU 코어를 태스크 실행에 사용할 수 있으며 Ray 태스크를 실행할 때 @ray.remote(num_cpus=1) 같은 식으로 요청하면 여기서 소모됨.
- GPU: 1.0
  - Ray가 인식한 논리 GPU 코어 수는 1개
  - 현재 클러스터 전체에서 1개의 GPU 코어를 태스크 실행에 사용할 수 있으며 Ray 태스크를 실행할 때 @ray.remote(num_gpus=1)로 요청할 수있다,

###

```python
import torch
@ray.remote(num_gpus=1)
def make_torch_prediction(model: torch.nn.Module, shard_path):
    model.to(torch.device("cuda"))
    inputs = pq.read_table(shard_path).to_pandas().to_numpy()
    results = []
    return len(results)
```

- @ray.remote(num_gpus=1)
  - 이 부분이 없었을때는 Ray는 태스크를 CPU 자원만 필요로 하는 일반 작업으로 인식해서 아무 노드에나 배치했었음.
  - 참고로 Task에선 다음과 같이 적어줬엇다

```python
@ray.remote
def make_prediction(model, shard_path):
    df = pq.read_table(shard_path).to_pandas()
    result = model(df)
    return len(result)
```

###

```python
import torch
@ray.remote(num_gpus=1)
def make_torch_prediction(model: torch.nn.Module, shard_path):
    model.to(torch.device("cuda"))
    inputs = pq.read_table(shard_path).to_pandas().to_numpy()
    results = []
    return len(results)

torch_model = torch.nn.Linear(10, 1)  # 예시 torch 모델
torch_model_ref = ray.put(torch_model)

# GPU 태스크 실행
for file in input_files:
    make_torch_prediction.remote(torch_model_ref, file)
```

- 원래 코드로 돌아와서보면
- Task때와 반대로 이 속성을 지정하면 스케줄러는 반드시 GPU가 하나 이상 있는 노드에서만 해당 태스크를 실행시킨다.
- model.to(torch.device("cuda")
  - 일반적으로 PyTorch 모델은 처음 생성하면 CPU 메모리에 적재되므로 GPU에서 연산을 시도하려고 하는 GPU 태스크에서는 모델을 반드시 CUDA 디바이스로 옮겨주어야 한다.
- torch_model = torch.nn.Linear(10, 1), torch_model_ref = ray.put(torch_model)
  - 여기서는 여기서는 예시로 간단한 torch.nn.Linear(10, 1) 모델을 만들고 모델을 ray.put으로 객체 저장소에 올린 뒤 make_torch_prediction.remote 호출 시 참조(torch_model_ref)를 전달하여 최종 학습을 수행.

###

<mark>cf3</mark>

- 의문점3
  - Ray에서 CPU와 GPU를 활용했을 때 시스템 메모리 사용량 변화를 가시화해보면??
- 확인3
  - 간단한 torch.nn.Linear(10, 1) 모델에서 “실행전 → CPU 태스크 후 → GPU 태스크 후” 동안 RAM 사용량을 확인해보기.

```python
@ray.remote
def cpu_task():
    model = torch.nn.Linear(10000, 10000)  # CPU 모델
    x = torch.randn(10000, 10000)
    y = model(x)
    return y.sum().item()

@ray.remote(num_gpus=1)
def gpu_task():
    model = torch.nn.Linear(10000, 10000).cuda()  # GPU 모델
    x = torch.randn(10000, 10000, device="cuda")
    y = model(x)
    return y.sum().item()

print_mem_usage("실행 전")
ray.get(cpu_task.remote())
print_mem_usage("CPU 태스크 실행 후")
ray.get(gpu_task.remote())
print_mem_usage("GPU 태스크 실행 후")

# GPU 시스템 상태도 확인
print_nvidia_smi()
```
```plain text
2025-09-12 21:45:21,108	INFO worker.py:1789 -- Calling ray.init() again after it has already been called.
[실행 전]
CPU 전체: 13.61 GB | 사용 중: 3.49 GB | 사용률: 28.1%
GPU VRAM 사용 중: 0.00 GB | 예약됨: 0.00 GB

[CPU 태스크 실행 후]
CPU 전체: 13.61 GB | 사용 중: 3.50 GB | 사용률: 28.2%
GPU VRAM 사용 중: 0.00 GB | 예약됨: 0.00 GB

[GPU 태스크 실행 후]
CPU 전체: 13.61 GB | 사용 중: 3.89 GB | 사용률: 31.1%
GPU VRAM 사용 중: 0.00 GB | 예약됨: 0.00 GB

[nvidia-smi]
Fri Sep 12 21:45:45 2025       
+-----------------------------------------------------------------------------------------+
| NVIDIA-SMI 550.54.15              Driver Version: 550.54.15      CUDA Version: 12.4     |
|-----------------------------------------+------------------------+----------------------+
| GPU  Name                 Persistence-M | Bus-Id          Disp.A | Volatile Uncorr. ECC |
| Fan  Temp   Perf          Pwr:Usage/Cap |           Memory-Usage | GPU-Util  Compute M. |
|                                         |                        |               MIG M. |
|=========================================+========================+======================|
|   0  Tesla T4                       Off |   00000000:00:04.0 Off |                    0 |
| N/A   45C    P0             30W /   70W |    1296MiB /  15360MiB |    100%      Default |
|                                         |                        |                  N/A |
+-----------------------------------------+------------------------+----------------------+
                                                                                         
+-----------------------------------------------------------------------------------------+
| Processes:                                                                              |
|  GPU   GI   CI        PID   Type   Process name                              GPU Memory |
|        ID   ID                                                               Usage      |
|=========================================================================================|
+-----------------------------------------------------------------------------------------+
```

- 실행 전
  - CPU RAM - 3.49 GB 사용 중
  - GPU VRAM - 0.00 GB 사용 중
- CPU 태스크 실행 후
  - CPU RAM - 3.50 GB 사용 중: CPU에서 모델+데이터를 생성해서 RAM이 0.01 GB 증가
  - GPU VRAM - 변화 없음
- GPU 태스크 실행 후
  - CPU RAM - 3.89 GB 사용 중: GPU를 쓸 때도 CPU에서 메타데이터, 버퍼, 연산 준비용 객체를 유지하기 때문에 0.39 GB가 증가
  - GPU VRAM - 1296 MiB (약 1.3 GB) 사용 중
    - [GPU 태스크 실행 후] 출력에는 torch.cuda.memory_allocated() 값을 사용했는데, Ray 워커 프로세스에서 GPU를 사용했기 때문에 VRAM 점유량을 잡아내지 못해서 0.0 GB 사용중으로 나온다. 
    - nvidia-smi 확인 결과 GPU 태스크가 모델과 입력 데이터를 GPU에 올려서 약 1.3 GB를 사용한 것이 확인된다.
  - GPU Utilization (GPU-Util) 100%
    - 태스크 실행 시 GPU 연산이 꽉 차서 돌았음을 확인 가능.
- 결론
  - “실행전 → CPU 태스크 후 → GPU 태스크 후” 동안 RAM 사용량이 CPU: 3.49 GB(27%) → 3.50 GB (28%) → 3.89 GB (31%)으로 변화하였고 GPU: 0GB → 0GB → ≈1.3 GB으로 변화했다.

#

#출처

Ray Document - Batch Prediction with Ray Core https://docs.ray.io/en/latest/ray-core/examples/batch_prediction.html

전체 코드 - google colab https://colab.research.google.com/drive/1Kp1zMDVJB2ZgIb0JwPqHD2Wpbumm0XUi?usp=sharing#scrollTo=PbEbMk4x3ozC

#

