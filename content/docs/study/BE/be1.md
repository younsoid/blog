---
date : 2025-07-22
tags: ['2025-07']
categories: ['Linux']
bookHidden: true
title: "Linux #1 NPM 과 PIP 명령어 목록"
---

# Linux #1 NPM 과 PIP 명령어 목록

#2025-07-22

---

### 1. NPM (Node Package Manager)

패키지 설치

```bash
npm install <패키지명> - 패키지 설치
npm install -g <패키지명> - 전역 설치
npm install --save-dev <패키지명> - 개발 의존성으로 설치
npm install - package.json의 모든 의존성 설치
```

패키지 관리

```bash
npm uninstall <패키지명> - 패키지 제거
npm update <패키지명> - 패키지 업데이트
npm list - 설치된 패키지 목록 보기
npm list -g - 전역 설치된 패키지 목록
```

프로젝트 관리

```bash
npm init - package.json 생성
npm start - 프로젝트 시작
npm run <스크립트명> - package.json의 스크립트 실행
npm version <버전> - 버전 업데이트
```

기타

```bash
npm search <검색어> - 패키지 검색
npm info <패키지명> - 패키지 정보 보기
npm cache clean --force - 캐시 정리
```

### 2. PIP (Python Package Installer)

패키지 설치

```bash
pip install <패키지명> - 패키지 설치
pip install <패키지명>==<버전> - 특정 버전 설치
pip install -r requirements.txt - requirements 파일로 설치
pip install --user <패키지명> - 사용자 디렉토리에 설치
```

패키지 관리

```bash
pip uninstall <패키지명> - 패키지 제거
pip install --upgrade <패키지명> - 패키지 업그레이드
pip list - 설치된 패키지 목록
pip show <패키지명> - 패키지 정보 보기
```

의존성 관리

```bash
pip freeze - 설치된 패키지와 버전 출력
pip freeze > requirements.txt - requirements 파일 생성
pip check - 의존성 충돌 확인
```

기타

```bash
pip search <검색어> - 패키지 검색 (일부 환경에서 비활성화)
pip cache purge - 캐시 정리
pip config list - 설정 보기
```

