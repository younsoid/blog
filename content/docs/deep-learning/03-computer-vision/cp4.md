---
date : 2026-10-07
tags: ['2026-10']
categories: ['computer-vision']
bookHidden: true
title: "컴퓨터 비전 모델들"
bookComments: true
index: 1
---

# 컴퓨터 비전 모델들

#2026-10-07

---

모델을 정의할때는 구조랑 목적(학습방식) 측면에서 정의할수있다. 

컴퓨터 비전 모델들을 모델 구조 기준으로 6개로 나누고 각 모델들의 목적(학습방식)을 6가지 중 하나로 분류했다.

컴퓨터 비전 모델의 task
- 인식(판별) 모델: 이미지를 보고 "무엇이 어디에 있는지" 판단하는 모델. 분류, 객체 탐지, 시맨틱·인스턴스·파놉틱 분할 등이 여기에 속하고, 다른 과제의 기반이 되는 백본도 주로 이 범주에서 나온다.
- 표현 학습 모델: 레이블 없이(자기지도 학습) 이미지의 범용적인 특성을 배우는 모델. 그 자체로 특정 과제를 풀기보다는, 여러 과제에 재사용할 수 있는 좋은 특성 추출기(백본)를 만드는 게 목적.
- 생성 모델: 새로운 이미지나 영상을 만들어내는 모델. GAN, VAE, 확산 모델, 자기회귀 모델 같은 방식이 있으며, 텍스트-이미지 생성이나 이미지 변환·편집에 쓰인다.
- 멀티모달 모델: 이미지와 텍스트처럼 서로 다른 종류의 데이터를 함께 다루는 모델. 이미지-텍스트 정렬(CLIP 등), 이미지를 이해하고 대화하는 멀티모달 LLM, 글로 지정한 대상을 찾는 개방형 어휘 탐지 등이 있다.
- 3D 비전 모델: 2D 이미지에서 3D 구조를 복원하거나 3D 데이터를 직접 처리하는 모델. 3D 재구성, 깊이 추정, 새로운 시점 합성(뉴럴 렌더링), 포인트 클라우드 처리 등이 포함된다.
- 영상 모델: 이미지에 시간 축이 더해진 영상을 다루는 모델. 행동 인식, 영상 분할, 영상 예측, 영상 생성 등이 있으며, 다른 범주와 겹쳐서 "생성 모델 + 영상 모델"처럼 함께 표기되는 경우가 많다.

이중에 관심있는 task는? 인식, 표현 학습, 멀티모달 모델 정도가 되겠다.

###

1. CNN(합성곱 신경망)

* VGG - 인식(판별) 모델 (분류)
* ResNet - 인식(판별) 모델 (분류)
* Inception - 인식(판별) 모델 (분류)
* Xception - 인식(판별) 모델 (분류)
* DenseNet - 인식(판별) 모델 (분류)
* MobileNet - 인식(판별) 모델 (경량 분류)
* EfficientNet - 인식(판별) 모델 (분류)
* RegNet - 인식(판별) 모델 (분류)
* ConvNeXt V1·V2 - 인식(판별) 모델 (분류)
* ConvMixer - 인식(판별) 모델 (분류)
* MambaOut - 인식(판별) 모델 (분류)
* DINOv3 (ConvNeXt 버전) - 표현 학습 모델 (자기지도)
* Faster R-CNN - 인식(판별) 모델 (객체 탐지)
* RetinaNet - 인식(판별) 모델 (객체 탐지)
* YOLO 계열 - 인식(판별) 모델 (실시간 객체 탐지)
* FCN - 인식(판별) 모델 (시맨틱 분할)
* U-Net - 인식(판별) 모델 (시맨틱 분할, 의료 영상)
* DeepLab - 인식(판별) 모델 (시맨틱 분할)
* Mask R-CNN - 인식(판별) 모델 (인스턴스 분할)
* DCGAN - 생성 모델 (GAN)
* pix2pix - 생성 모델 (GAN, 이미지 변환)
* CycleGAN - 생성 모델 (GAN, 이미지 변환)
* ProGAN - 생성 모델 (GAN)
* StyleGAN 1·2·3 - 생성 모델 (GAN)
* BigGAN - 생성 모델 (GAN)
* VAE, VQ-VAE, VQ-VAE-2 - 생성 모델 (잠재 표현·토크나이저)


2. 트랜스포머

* ViT - 인식(판별) 모델 (분류 백본)
* DeiT - 인식(판별) 모델 (분류 백본)
* CaiT - 인식(판별) 모델 (분류 백본)
* Swin Transformer, Swin V2 - 인식(판별) 모델 (분류·탐지·분할 백본)
* PVT, PVTv2 - 인식(판별) 모델 (밀집 예측 백본)
* CSWin, Twins - 인식(판별) 모델 (백본)
* Hiera - 인식(판별) 모델 (백본)
* BEiT - 표현 학습 모델 (마스크드 이미지 모델링)
* MAE - 표현 학습 모델 (마스크드 이미지 모델링)
* DINO, DINOv2, DINOv3 (ViT 버전) - 표현 학습 모델 (자기지도)
* I-JEPA - 표현 학습 모델 (자기지도)
* V-JEPA, V-JEPA 2 - 표현 학습 모델 (자기지도, 영상)
* EVA, EVA-02 - 표현 학습 모델
* DETR - 인식(판별) 모델 (객체 탐지, 백본은 보통 CNN)
* Deformable DETR, DAB-DETR, DN-DETR, DINO(탐지용), Co-DETR - 인식(판별) 모델 (객체 탐지)
* SETR - 인식(판별) 모델 (시맨틱 분할)
* SegFormer - 인식(판별) 모델 (시맨틱 분할)
* MaskFormer, Mask2Former, OneFormer - 인식(판별) 모델 (시맨틱·인스턴스·파놉틱 통합 분할)
* SAM, SAM 3 - 인식(판별) 모델 (프롬프트 기반 분할)
* SAM 2 - 인식(판별) 모델 + 영상 모델 (이미지·영상 분할)
* CLIP - 멀티모달 모델 (이미지-텍스트 정렬)
* SigLIP, SigLIP 2, EVA-CLIP, OpenCLIP - 멀티모달 모델 (이미지-텍스트 정렬)
* BLIP, BLIP-2 - 멀티모달 모델 (캡셔닝·VQA)
* Flamingo - 멀티모달 모델 (멀티모달 LLM)
* LLaVA, Qwen-VL, InternVL, PaliGemma, Molmo - 멀티모달 모델 (멀티모달 LLM)
* OWL-ViT, OWLv2, GLIP, Grounding DINO - 멀티모달 모델 (개방형 어휘 탐지)
* DiT - 생성 모델 (확산)
* SD3, FLUX - 생성 모델 (확산, 텍스트-이미지)
* Sora, Wan, HunyuanVideo - 생성 모델 + 영상 모델 (확산, 텍스트-영상)
* DALL·E(1세대), Parti, LlamaGen, VAR - 생성 모델 (자기회귀)
* DUSt3R, MASt3R - 3D 비전 모델 (3D 재구성)
* VGGT, π³ - 3D 비전 모델 (피드포워드 3D 재구성)
* DPT, Depth Anything - 3D 비전 모델 (단안 깊이 추정)
* Point Transformer V1·V2·V3 - 3D 비전 모델 (포인트 클라우드)
* TimeSformer, ViViT, Video Swin - 영상 모델 (행동 인식)
* VideoMAE - 영상 모델 + 표현 학습 모델 (자기지도)


3. MLP 계열

* MLP-Mixer - 인식(판별) 모델 (분류)
* ResMLP - 인식(판별) 모델 (분류)
* gMLP - 인식(판별) 모델 (분류)
* CycleMLP - 인식(판별) 모델 (분류·밀집 예측)
* PointNet, PointNet++ - 3D 비전 모델 (포인트 클라우드)
* NeRF, Mip-NeRF, Zip-NeRF - 3D 비전 모델 (뉴럴 렌더링, 새로운 시점 합성)
* Instant-NGP - 3D 비전 모델 (뉴럴 렌더링, 해시 격자 + 작은 MLP)


4. SSM(상태 공간 모델) 계열

* Vision Mamba(Vim) - 인식(판별) 모델 (분류 백본)
* VMamba - 인식(판별) 모델 (분류·탐지·분할 백본)
* LocalMamba - 인식(판별) 모델 (백본)
* PlainMamba - 인식(판별) 모델 (백본)
* EfficientVMamba - 인식(판별) 모델 (경량 백본)


5. 하이브리드

* CvT - 인식(판별) 모델 (분류 백본, CNN+트랜스포머)
* CoAtNet - 인식(판별) 모델 (분류 백본, CNN+트랜스포머)
* MaxViT - 인식(판별) 모델 (분류 백본, CNN+트랜스포머)
* TransNeXt - 인식(판별) 모델 (백본, CNN+트랜스포머)
* MobileViT, EfficientViT, EdgeViT - 인식(판별) 모델 (경량 백본, CNN+트랜스포머)
* MambaVision - 인식(판별) 모델 (백본, SSM+트랜스포머)
* RT-DETR, RT-DETRv2, D-FINE - 인식(판별) 모델 (실시간 객체 탐지, CNN 백본+트랜스포머)
* ALIGN - 멀티모달 모델 (이미지-텍스트 정렬, EfficientNet+BERT)
* YOLO-World - 멀티모달 모델 (개방형 어휘 탐지, YOLO+CLIP 텍스트 인코더)
* DDPM - 생성 모델 (확산, 어텐션이 섞인 CNN U-Net)
* Stable Diffusion 1.x·2.x, SDXL - 생성 모델 (확산, 어텐션이 섞인 CNN U-Net)
* VQGAN - 생성 모델 (토크나이저, CNN+일부 어텐션)
* GigaGAN - 생성 모델 (GAN, CNN+어텐션)
* Marigold - 3D 비전 모델 (깊이 추정, Stable Diffusion 기반)


6. 기타 구조

* ST-GCN - 영상 모델 (골격 기반 행동 인식, 그래프 신경망)
* DGCNN - 3D 비전 모델 (포인트 클라우드, 그래프 신경망)
* ConvLSTM - 영상 모델 (영상 예측, 순환 신경망)
* CapsNet - 인식(판별) 모델 (분류, 캡슐 네트워크)
* 3D 가우시안 스플래팅(3DGS) - 3D 비전 모델 (뉴럴 렌더링, 신경망 대신 가우시안을 직접 최적화)
