---
date : 2025-04-13
tags: ['2025-04']
categories: ['hugo']
bookHidden: true
title: "Hugo #3 블로그 scss 커스텀하기 (visited 링크 글자색 수정)"
bookComments: true
---

# Hugo #3 Hugo 블로그 scss 커스텀하기 (visited 링크 글자색 수정)

#2025-04-13

---

![image](https://github.com/user-attachments/assets/9da1fb5b-77a7-4367-838f-640f4567b07b)

기존 화면에서 방문하지않은 하이퍼링크는 파란색, 방문한 링크는 보라색으로 표시됐는데, 뭔가 링크를 누르는 느낌보다는 글을 누르는 느낌이 났으면 좋겠어서 + 근데 링크인건 인지돼야해서 적절한 색깔로 바꿔주고 싶었다.

![image](https://github.com/user-attachments/assets/488cc4e5-44a4-46d9-9674-2cbec8e46711)

[Hugo Book Theme 깃히브](https://github.com/alex-shpak/hugo-book/tree/master)를 확인해보면 assets 디렉토리에 _variables.scss 파일을 생성해주면 되는듯해서 아래와 같이 넣어줬다.

```
// Themes
@mixin theme-light {
  --gray-100: #f8f9fa;
  --gray-200: #e9ecef;
  --gray-500: #adb5bd;

  --color-link: #0f5294;//#2619c1;//#0055bb;
  --color-visited-link: #0f5294;//#2619c1;//#0055bb;//#8440f1;

  --body-background: white;
  --body-font-color: black;

  --icon-filter: none;

  --hint-color-info: #6bf;
  --hint-color-warning: #fd6;
  --hint-color-danger: #f66;
}
```

여러 색깔을 시도한 흔적.. ㅋㅋ

![image](https://github.com/user-attachments/assets/ac22310f-7214-426c-85ef-9ef055f3ee58)

최종적으로 진한 남색으로 선택해줬다! 진한 회색이 자연스럽긴한데 링크 느낌이 안나서 남색으로 설정해줬다

![image](https://github.com/user-attachments/assets/dfe33a92-502e-471b-a5c9-bedc6fd6f0f2)

요건 색깔만 봤을땐 이뻐보였는데 적용하니깐 별로였다.

cf) _custom.scss랑 _variables.scss랑 뭐가 다른지 모르겠는데 ㅠ custom은 안먹고 variables만 먹음.

