---
date : 2025-04-09
tags: ['2025-04']
categories: ['github']
bookHidden: true
title: "Github #2 Ubuntu 20.04 brownout 오류"
bookComments: true
---

# Github #2 Ubuntu 20.04 brownout 오류

#2025-04-09

---

![image](https://github.com/user-attachments/assets/43de5741-43f6-41ec-a76b-8a79fd8fba51)

블로그 수정하는데 갑자기 처음보는 오류가 발생,,

찾아보니 ubuntu-20.04 GitHub Actions runner가 2025년 4월 15일에 지원 종료함에 따라 workflow에서 runs-on: ubuntu-20.04를 사용중이라면 runs-on: ubuntu-22.04로 수정하라는 내용이었다.

```yml
jobs:
  deploy:
    runs-on: ubuntu-22.04
```

`gh-pages.yml`에 들어가서 runs-on: ubuntu-20.04를 runs-on: ubuntu-22.04로 바꿔주니까 다시 돌아간다!

#
