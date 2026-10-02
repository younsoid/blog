---
date : 2025-07-24
tags: ['2025-07']
categories: ['hugo']
bookHidden: true
title: "Hugo #4 Markdown HTML 렌더링 문제"
---

# Hugo #4 Markdown HTML 렌더링 문제

#2025-07-24

---

### 1. 문제

```plain text
<details>
  <summary> 토글 </summary>
    토글 내용
</details>
```

Hugo book Theme는 [원래](https://github.com/alex-shpak/hugo-book/blob/master/exampleSite/content.en/docs/shortcodes/details.md) 위 코드를 작성하면 아래처럼 토글이 나온다.


<details>
  <summary> 토글 </summary>
    토글 내용
</details>

어느날부터 갑자기 토글이든 문단나누기든 다 안먹어서, 근데 원인을 몰라서 그냥 shortcode 기능 없는대로 쓰다가, 너무 불편해서 좀 찾아봤고 `hugo.toml`에 다음 내용 넣어준 뒤로는 잘 작동했다.

```toml
[markup]
  [markup.goldmark]
    [markup.goldmark.renderer]
      unsafe = true
```

근데 이후에 [html 관련 포스팅](https://yshghid.github.io/docs/study/sw/sw5/)을 작성했는데 넣어준 코드가 다 깨졌다. 

근데 심지어 html 코드 뿐만아니라 plain text 처리된 코드들도 다 깨졌다. (위에서 보다시피 이 글에선 잘 나오는데..)

![image](https://github.com/user-attachments/assets/74612054-0dc2-41f0-bfa4-c2a07747c60f)

실제 호스팅 화면은 이렇게 댓글창도 없어졌고

![image](https://github.com/user-attachments/assets/edbe7f19-7d7a-46c4-baaf-aa3f90a16823)

md 파일은 깨졌다.

###

### 2. 해결

md 파일을 봤을때 `<select>`가 들어가고부터 이상해진것같아서 코드로 감싸주니까 정상적으로 바꼈다.

![image](https://github.com/user-attachments/assets/eec683f3-d139-4f25-b55c-bf4abf9f80cf)

![image](https://github.com/user-attachments/assets/296429b7-da28-4f89-885e-67deebb1eb5b)

###

### 3. 원인

`<select>`가 왜 문제가 되는지 몰라서 찾아봤는데 일단

```toml
[markup]
  [markup.goldmark]
    [markup.goldmark.renderer]
      unsafe = true
```

이 설정에서 `markup.goldmark.renderer.unsafe = true`는 Markdown 안에 작성된 HTML 태그를 그대로 렌더링하도록 허용한다는 의미여서 

true 설정하면 ```로 감싸지 않은 HTML 태그가 글자 처리되는게 아니라 실제 요소로 렌더링되는바람에 오류가 난거였다.

###

### 4

챗지피티에 쳤을때

> 이 설정 때문에 발생할 수 있는 현상: Markdown 내부의 HTML 코드가 "코드 블록"이 아니라 "실제 HTML로 실행"되기 때문에, ```로 감싸지 않은 HTML 태그는 실제 요소로 렌더링됨 따라서 unsafe = true 상태에서 코드 블럭 없이 HTML 태그를 작성하면 코드 블럭처럼 보이지 않고 실제로 화면에 렌더링됨, 특히 `<script>` 태그는 실제로 실행될 수도 있음 (보안 주의)

라고까지 잘 알려줘놓고

> 해결 방법 1) HTML을 코드 블럭 안에 반드시 감싸야 함:
> 
> ```html
> <div>
>   <label>재고:</label>
>   <input type="number" />
> </div>
> ```
> 
> 해결 방법 2) HTML 태그를 쓰고 싶지만 코드로 보여주고 싶다면, unsafe = false로 바꾸고 `<`를 `&lt;`로 escape 처리하기. 

이런 이상한 해결 방법을 줬다(..)

#

