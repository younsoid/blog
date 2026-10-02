---
date : 2025-07-21
tags: ['2025-07']
categories: ['env']
bookHidden: true
title: "개발환경 설정 (GIT, Docker, VScode, RDE 컨테이너)"
---

# env #2 개발환경 설정 (GIT, Docker, VScode, RDE 컨테이너)

#2025-07-21

---

### 1. GIT 사용자 정보 설정

```bash
[Git 설치 확인]
git --version

[사용자 이름 설정]
git config --global user.name "윤소현"

[이메일 주소 설정] GitHub에 등록된 이메일 주소와 일치하는지 확인 필요
git config --global user.email "yshggid@gmail.com"

[설정 확인]
git config --global --list
```

### 2. 로컬 GIT Repository 생성

vscode에서 좌측 SOURCE CONTRIL 아이콘 > Initialize Repository > 로컬 폴더를 git repository로 생성

-> 터미널을 통해 ".git" 폴더와 ".gitignore" 파일 생성

```bash
(skala) yshmbid:github yshmbid$ ls -al
total 0
drwxr-xr-x   4 yshmbid  staff  128 Jul 21 19:36 .
drwxr-xr-x   7 yshmbid  staff  224 Jul 21 19:36 ..
drwxr-xr-x@ 14 yshmbid  staff  448 Jul 21 16:17 .git
-rw-r--r--   1 yshmbid  staff    0 Jul 21 15:48 .gitignore
```


### 3. 확인

https://github.com/settings/applications 확인해보면

![image](https://github.com/user-attachments/assets/3c87c158-a933-4841-9807-d30381e4c364)

잘 들어갔다!

### 4. Docker 연결 

#1 Docker desktop 설치하기

https://www.docker.com/products/docker-desktop

#2 RdE container 다운로드

```bash
docker pull amdp-registry.skala-ai.com/mydev-ywyi/devplace-vscode-server.local-python:4.96.4.lite.SKALA.RELEASE.arm64
```

다운로드 확인

![image](https://github.com/user-attachments/assets/95edc6ed-fa9f-4a3a-9483-4217db55bb46)

#3 Local RDE 설치 (강의 제공 링크에서)

#4 Remote SSH  Extension 설치

![image](https://github.com/user-attachments/assets/4a47aa95-7a97-403b-b41f-4a249d6b4f19)

설치 후?

![image](https://github.com/user-attachments/assets/84e9de3c-1403-4200-b310-f996938660b0)

`창+` 아이콘 클릭해서 접속

![image](https://github.com/user-attachments/assets/c0a320d8-c4f2-4aa2-9839-dc381d343a79)

원격접속을 `/config`로 설정해서 열기.

#cf 현재 수행중인 도커 확인

```bash
$ docker ps
CONTAINER ID   IMAGE                                                                                                       COMMAND                  CREATED          STATUS          PORTS                                                                                                                                                      NAMES
a0a3f97456b9   amdp-registry.skala-ai.com/mydev-ywyi/devplace-vscode-server.local-python:4.96.4.lite.SKALA.RELEASE.arm64   "/bin/bash -c 'ls -l…"   43 minutes ago   Up 42 minutes   0.0.0.0:2222->2222/tcp, 0.0.0.0:5173->5173/tcp, 0.0.0.0:5500->5500/tcp, 0.0.0.0:8080-8081->8080-8081/tcp, 0.0.0.0:8443->8443/tcp, 0.0.0.0:9931->9931/tcp   local-rde
(skala) yshmbid:github yshmbid$ docker exec -it a0a3f97456b9 bash
[oh-my-zsh] Insecure completion-dependent directories detected:
drwxr-xr-x 1 skala skala  4096 Jul 17 23:29 /initial-config/.oh-my-zsh
drwxr-xr-x 1 skala skala  4096 Jul 21 16:23 /initial-config/.oh-my-zsh/cache
drwxr-xr-x 1 skala skala  4096 Jul 17 23:29 /initial-config/.oh-my-zsh/custom
...
```

