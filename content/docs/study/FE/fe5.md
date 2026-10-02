---
date : 2024-12-31
tags: ['2024-12']
categories: ['hugo']
bookHidden: true
title: "Hugo #2 Favicon 변경, Giscus 댓글창 추가"
bookComments: true
---

# Hugo #2 Favicon 변경, Giscus 댓글창 추가

#2024-12-31

---

### 1. Favicon 변경 

Hugo-book 테마의 github에서 README 파일을 읽어보면, logo와 favicon 이미지의 경로 정보를 찾을 수 있다.

(logo 정보)
![image](https://github.com/user-attachments/assets/c704ebb2-2531-49b6-ae79-21c1036c1dbb)

(favicon 정보)
![image](https://github.com/user-attachments/assets/a6e2a1c8-0386-40ac-ad19-d59806f5a6b2)

확인 결과 `static` 디렉토리에 각각 `logo.png`, `favicon.png`로 저장해두면 반영되는것 같다.

참고로 Hugo-book 테마의 오리지널 웹사이트는 아래와 같이 디자인되어있고

![image](https://github.com/user-attachments/assets/4116ae69-80e0-44a0-a177-152b32609da2)

최상단 탭에 들어가는 이미지가 `logo.png`, 블로그 이름 옆에 들어가는 이미지가 `favicon.png`이다.

먼저 `static` 디렉토리에 넣고 싶은 로고와 파비콘을 `logo.png`, `favicon.png` 로 저장해준다.

![image](https://github.com/user-attachments/assets/37f1cb77-6655-4e67-8efa-bfabf228e34b)

다음으로, hugo.toml 파일을 열어 아래 내용을 추가해준다.

```
# (Optional, default none) Set the path to a logo for the book. If the logo is
# /static/logo.png then the path would be 'logo.png'
BookLogo = 'logo.png'
```

블로그를 들어가보면 설정한 로고와 파비콘이 잘 들어간것을 확인할 수 있다!

![image](https://github.com/user-attachments/assets/cc3be435-b1fa-48b0-b9e5-1e9fdcad3950)

### 2. Giscus 댓글창 추가

Giscus 댓글 시스템을 Hugo 기반 블로그에 연동하기 위해서는 Giscus에 블로그 리포지토리를 연결한 후, js script를 작성하여 블로그 리포지토리의 layouts 디렉토리에 저장하면 된다고 한다.

이때 연결할 리포지토리는 다음 3가지 조건을 만족해야 한다.

1. Public이어야 함.
2. giscus 앱이 설치되어 있어야 함.
3. Discussions 기능이 해당 저장소에서 활성화되어 있어야 함.

### 2-1. 공개 저장소 확인

블로그 리포지토리의 Settings > General의 맨 하단을 보면 Danger Zone에서 public인지 private인지 확인이 가능하다.

![image](https://github.com/user-attachments/assets/41303089-405b-438c-bcdf-ec7973a6809a)

public이므로 다음으로 넘어간다.

### 2-2. Giscus 앱 설치

https://github.com/apps/giscus 에 접속하여 install, configure를 진행하면 쉽게 설치된다. 

![image](https://github.com/user-attachments/assets/600af8be-009e-4df5-aa5b-696b98cd9309)

Repository access는 All repositories 로 설정했다.

![image](https://github.com/user-attachments/assets/23ce8634-3363-429e-a874-c973db36a02c)

### 2-3. Discussion 기능 활성화

블로그 리포지토리의 Settings > General을 스크롤해보면 Discussions 체크박스가 생긴 것을 확인할 수 있다. 이를 체크해준다.

![image](https://github.com/user-attachments/assets/d6a1c179-968b-42bb-95e0-f46a0fd909ce)

위로 스크롤해보면 상단에 Discussions 탭이 생겼다.

![image](https://github.com/user-attachments/assets/70081470-23c7-47f2-8e59-9bb09b807279)

이제 블로그 리포지토리가 Giscus에 연결할 3가지 조건을 만족하였고 블로그를 Giscus로 연결해주면 된다. 연결해주려면 아래 형식의 js 스크립트를 작성하여 layouts/partials/comments.html에 추가해주면 된다.

js 스크립트는 https://giscus.app/ko에서 파라미터를 선택하면 적절하게 생성해준다! 

```
<script src="https://giscus.app/client.js"
        data-repo="yshghid/yshghid.github.io"
        data-repo-id="R_kgDONkMkNg"
        data-category-id="DIC_kwDONkMkNs4CloJh"
        data-mapping="pathname"
        data-strict="0"
        data-reactions-enabled="1"
        data-emit-metadata="0"
        data-input-position="bottom"
        data-theme="preferred_color_scheme"
        data-lang="ko"
        crossorigin="anonymous"
        async>
</script>
```

해당 내용을 복사해서 블로그 리포지토리의 layouts/partials/docs/comments.html로 생성해주었다.

![image](https://github.com/user-attachments/assets/4cd04a51-6f69-49c1-8f00-f86e84b6feb1)

성공적으로 댓글창이 추가되었다!!

### 3. 참고한 블로그

https://parker1609.github.io/post/creating-my-blog-with-hugo/
