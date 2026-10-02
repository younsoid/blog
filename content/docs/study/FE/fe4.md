---
date : 2024-12-31
tags: ['2024-12']
categories: ['hugo']
bookHidden: true
title: "Hugo #1 사이트 생성, 깃허브 배포"
bookComments: true
---

# Hugo #1 사이트 생성, 깃허브 배포

#2024-12-31

---

### 1. Hugo 설치

```
$ brew install hugo

$ hugo version
hugo v0.131.0+extended darwin/arm64 BuildDate=2024-08-02T09:03:48Z VendorInfo=brew
```
Hugo v0.112.0 이상인지 확인하면 된다.

### 2. Hugo 사이트 생성

작업하고 싶은 위치에 Hugo 디렉토리를 만들어준다.

```
$ mkdir Hugo
$ cd Hugo
```

Hugo로 들어가서 hugo 사이트 틀을 생성해준다. 나는 blog라는 이름으로 생성하였다.

```
$ pwd
/Users/yshmbid/Hugo

$ hugo new site blog
```

blog 디렉토리에 빈 Git 저장소를 초기화한다.

```
$ cd blog
$ pwd
/Users/yshmbid/Hugo/blog

$ git init
hint: Using 'master' as the name for the initial branch. This default branch name
hint: is subject to change. To configure the initial branch name to use in all
hint: of your new repositories, which will suppress this warning, call:
hint:
hint: 	git config --global init.defaultBranch <name>
hint:
hint: Names commonly chosen instead of 'master' are 'main', 'trunk' and
hint: 'development'. The just-created branch can be renamed via this command:
hint:
hint: 	git branch -m <name>
/Users/yshmbid/Hugo/blog/.git/ 안의 빈 깃 저장소를 다시 초기화했습니다
```

위에서 Using 'master' as the name for the initial branch. 언급이 나온다. 여기서 확인해줘야 할 부분이 있다.

![image](https://github.com/user-attachments/assets/a483f192-c2a4-4235-b23f-97126b895eaa)

레포지토리 생성 페이지에서 Add a README file.을 체크하면 This will set main as the default branch.라는 안내가 뜬다. 이를 통해 default가 main임을 확인할수있다.

따라서 위의 경우에는 master가 아닌 main으로 바꿔줘야 한다.

```
$ pwd
/Users/yshmbid/Hugo/blog

$ git config --global init.defaultBranch main
$ git branch -m main
```

다음으로 선택한 테마를 Git 서브모듈로 프로젝트에 추가한다. 나는 hugo-book이라는 테마를 사용했다.

```
$ pwd
/Users/yshmbid/Hugo/blog

$ git submodule add https://github.com/alex-shpak/hugo-book themes/hugo-book
```

다음으로, 블로그의 기본 설정들을 세팅해준다. blog 디렉토리 내 파일들은 대략적으로 아래와 같이 구성되어 있다.

```
$ ls
archetypes	data		i18n		resources
assets		hugo.toml	layouts		static
content		public		themes
```

이 중에서 content와 hugo.toml만 수정할것이다. content에는 작성한 게시물이 들어가고, hugo.toml에는 기본 세팅을 위한 config 변수들이 들어간다.

![image](https://github.com/user-attachments/assets/0243e743-af0a-4c9c-9632-59a2277fb2f5)

hugo-book 테마의 경우에는 content에 대해 이와 같이 언급하고 있다. 해당 테마는 국가별로 여러 content 디렉토리가 존재해서, 그 중 main이 되는 content.en의 내용만을 시키는대로 복사해준다.

```
$ cp -R themes/hugo-book/exampleSite/content.en/* ./content
```

다음으로 hugo.toml에 선택한 테마를 설정해주고 열어서 확인해본다.

```
$ echo "theme = 'hugo-book'" >> hugo.toml
$ view hugo.toml
  1 baseURL = 'https://example.org/'
  2 languageCode = 'en-us'
  3 title = 'My New Hugo Site'
  4 theme = 'hugo-book'
```

여기서 base가 되는 내용만 수정해줬다.

```
  1 baseURL = 'https://yshghid.github.io/'
  2 languageCode = 'en-us'
  3 title = 'Lifelog 2025'
  4 theme = 'hugo-book'
  # i를 누르면 편집모드로 전환된다.
  # 편집이 끝났으면 esc를 누르고 :wq!를 입력하면 완료된다.
```

기본적인 설정이 끝났으므로 로컬에서 실행시켜보자! http://localhost:1313에 접속하면 local 환경에서 어떻게 실행 중인지 확인할수있다.

```
$ hugo server
```

![image](https://github.com/user-attachments/assets/db51ffd4-686b-47e4-bfdd-c1e7f03ece21)

이쁘게 잘 나온다 ㅎㅎ

변경 사항을 픽스하려면 `hugo`를 수행해서 `public` 디렉토리에 static site 코드를 생성해준다.

```
$ pwd
/Users/yshmbid/Hugo/blog

$ hugo
Start building sites …
hugo v0.131.0+extended darwin/arm64 BuildDate=2024-08-02T09:03:48Z VendorInfo=brew

WARN  Expand shortcode is deprecated. Use 'details' instead.

                   | EN
-------------------+-----
  Pages            | 58
  Paginator pages  |  0
  Non-page files   |  0
  Static files     | 78
  Processed images |  0
  Aliases          | 11
  Cleaned          |  0

Total in 66 ms
```

### 3. Hugo 사이트 배포

hugo로 만든 static site를 github page를 활용해서 배포할것이다. 이를 위해서 `<user-id>.github.io` 리포지토리를 생성해준다.

이때 Add a README file 을 선택할 경우 push 할때 오류가 날 수 있으므로 체크 해제해서 생성해주는게 좋다.

![image](https://github.com/user-attachments/assets/82ece276-c744-4ea0-8d95-221934d347ba)

다음으로, .github/workflows 경로에 gh-pages.yml 파일을 만들어준다. gh-pages.yml은 GitHub Actions 워크플로우를 정의하여 코드가 커밋되거나 푸시될 때 자동으로 Hugo 사이트를 빌드하고 GitHub Pages에 배포할 수 있도록 하는 파일이다.

```
$ pwd
/Users/yshmbid/Hugo/blog

$ mkdir -p .github/workflows
$ cd .github/workflows
$ touch gh-pages.yml
```

아래 내용은 [HUGO 공식 문서](https://gohugo.io/hosting-and-deployment/hosting-on-github/)에서 제공한 워크플로우인데, 나의 경우에는 오류가 났다.

```
# Sample workflow for building and deploying a Hugo site to GitHub Pages
name: Deploy Hugo site to Pages

on:
  # Runs on pushes targeting the default branch
  push:
    branches:
      - main

  # Allows you to run this workflow manually from the Actions tab
  workflow_dispatch:

# Sets permissions of the GITHUB_TOKEN to allow deployment to GitHub Pages
permissions:
  contents: read
  pages: write
  id-token: write

# Allow only one concurrent deployment, skipping runs queued between the run in-progress and latest queued.
# However, do NOT cancel in-progress runs as we want to allow these production deployments to complete.
concurrency:
  group: "pages"
  cancel-in-progress: false

# Default to bash
defaults:
  run:
    shell: bash

jobs:
  # Build job
  build:
    runs-on: ubuntu-latest
    env:
      HUGO_VERSION: 0.128.0
    steps:
      - name: Install Hugo CLI
        run: |
          wget -O ${{ runner.temp }}/hugo.deb https://github.com/gohugoio/hugo/releases/download/v${HUGO_VERSION}/hugo_extended_${HUGO_VERSION}_linux-amd64.deb \
          && sudo dpkg -i ${{ runner.temp }}/hugo.deb
      - name: Install Dart Sass
        run: sudo snap install dart-sass
      - name: Checkout
        uses: actions/checkout@v4
        with:
          submodules: recursive
          fetch-depth: 0
      - name: Setup Pages
        id: pages
        uses: actions/configure-pages@v5
      - name: Install Node.js dependencies
        run: "[[ -f package-lock.json || -f npm-shrinkwrap.json ]] && npm ci || true"
      - name: Build with Hugo
        env:
          HUGO_CACHEDIR: ${{ runner.temp }}/hugo_cache
          HUGO_ENVIRONMENT: production
          TZ: America/Los_Angeles
        run: |
          hugo \
            --gc \
            --minify \
            --baseURL "${{ steps.pages.outputs.base_url }}/"
      - name: Upload artifact
        uses: actions/upload-pages-artifact@v3
        with:
          path: ./public

  # Deployment job
  deploy:
    environment:
      name: github-pages
      url: ${{ steps.deployment.outputs.page_url }}
    runs-on: ubuntu-latest
    needs: build
    steps:
      - name: Deploy to GitHub Pages
        id: deployment
        uses: actions/deploy-pages@v4
```

위의 워크플로우를 사용한다면 line 8의 main를 확인해주자면 default가 master라면 master로 바꿔줘야 한다.

나의 경우는 위 워크플로우로는 오류가 났어서 아래의 수정된 내용을 넣어줬다.

```
name: github pages

on:
  push:
    branches:
      - main  # Set a branch to deploy
  pull_request:

jobs:
  deploy:
    runs-on: ubuntu-20.04
    steps:
      - uses: actions/checkout@v3
        with:
          submodules: true  # Fetch Hugo themes (true OR recursive)
          fetch-depth: 0    # Fetch all history for .GitInfo and .Lastmod

      - name: Create .nojekyll
        run: echo '' > .nojekyll

      - name: Setup Hugo
        uses: peaceiris/actions-hugo@v3
        with:
          hugo-version: 'latest'
          # extended: true

      - name: Build
        run: hugo --minify

      - name: Deploy
        uses: peaceiris/actions-gh-pages@v4
        if: github.ref == 'refs/heads/main'
        with:
          github_token: ${{ secrets.GH_TOKEN }}
          publish_dir: ./public
```

이어서 GH_TOKEN를 정의해줘야 하는데

![image](https://github.com/user-attachments/assets/e623f313-7263-4c12-8e7b-487b497fad01)

리포지토리의 Settings -> Secretes and Variables -> Actions 에서 Repository secretes와 Repository variables를 생성해준다.

![image](https://github.com/user-attachments/assets/376e400a-4403-41e8-a1fe-c6ba512d1dd4)

Secret 자리에 토큰을 입력해주면 된다.

작성이 완료되었다면, 생성한 `<user-id>.github.io` 리포지토리에 연결한 후 커밋, 푸시해준다.

```
$ pwd
/Users/yshmbid/Hugo/blog

$ git remote add origin https://github.com/yshghid/yshghid.github.io.git
$ git add .
$ git commit -m "first commit"
$ git push origin main
```

### 4. 마무리

이로써 블로그 생성과 배포는 끝이지만!! 추가로 확인하면 좋은 부분이 있다.

1. Actions

![image](https://github.com/user-attachments/assets/4e0d8af9-13ad-46d1-8fb3-ce3179e01145)

Actions에서 초록색 체크박스가 뜨는지 확인하기. 오류가 난다면 해당 오류의 로그를 읽어보고 그에 맞게 수정해주면 된다.

2. Sources, Branch

![image](https://github.com/user-attachments/assets/718443b2-67d5-4bb8-a838-17393a3cf0ab)

공식 문서에서는 Deploy from a branch에서 Github Actions로 바꿔주라고 나온다. 바꿔도 상관없으나 나는 그냥 뒀다.

브랜치는 보통은 gh-pages 브랜치가 기본 Github Pages 브랜치로 설정되어 있지만 혹시 안되어 있다면 gh-pages로 바꿔주면 된다.

3. 구조

```
/Users/yshmbid/Hugo/blog
├── hugo.toml
├── content/
├── layouts/
├── static/
└── .github/
    └── workflows/
        └── gh-pages.yml
```

blog 디렉토리가 이와 같은 구조를 띤다면 제대로 작성된 것이다.


### 5. 참고한 블로그 및 문서 

1. HUGO 공식 문서 - https://gohugo.io/getting-started/quick-start/
2. HUGO 공식 문서2 - https://gohugo.io/hosting-and-deployment/hosting-on-github/
3. hugo-book github - https://github.com/alex-shpak/hugo-book.git
4. https://c11oud.tistory.com/entry/GitHub-깃허브-블로그-만들기1
5. https://github.com/Integerous/Integerous.github.io
6. https://kzeoh.github.io/posts/make-blog/
