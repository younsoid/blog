---
date : 2025-07-23
tags: ['2025-07']
categories: ['SKALA', 'javascript']
bookHidden: true
title: "JavaScript #1 쇼핑몰 주문 처리"
---

# JavaScript #1 쇼핑몰 주문 처리

#2025-07-23

---

### 1. 문제

당신은 온라인 쇼핑몰의 개발자로, 고객 주문을 처리하는 프로그램을 작성하고 있습니다. 주문 처리 과정에서는 여러 조건을 고려해야 합니다. 예를 들어, 상품의 재고 여부, 고객의 회원 등급, 주문 금액, 배송 옵션 등을 확인하여 적절한 메시지와 할인율을 적용해야 합니다. 아래의 세부 조건에 맞도록 JavaScript 함수를 구현하고, 최종 결과를 console.log 또는 alert로 출력해보세요.

#세부 조건

상품 재고 확인
- 재고가 1개 이상일 경우: 주문을 진행한다.
- 재고가 0개일 경우: 품절 메시지를 출력한다.

회원 등급에 따른 할인율 적용
- VIP 회원: 10% 할인
- Gold 회원: 5% 할인
- 그 외 회원: 할인 없음

주문 금액에 따른 추가 할인 (기본 할인 적용 이후 기준)
- 100,000원 이상: 5,000원 추가 할인
- 200,000원 이상: 15,000원 추가 할인

배송 옵션에 따른 배송비 처리
- 배송 옵션이 "fast"인 경우: 배송비 3,000원 추가
- 배송 옵션이 "standard" 또는 미선택인 경우: 배송비 없음

최종 출력 메시지
- 주문이 정상적으로 처리된 경우: "주문이 정상적으로 완료되었습니다." 메시지와 함께 최종 결제 금액 출력
- 재고가 없는 경우: "죄송합니다. 해당 상품은 품절입니다." 메시지 출력

HTML 인터페이스 구현 조건
- 상품 재고와 주문 금액은 숫자만 입력 가능하도록 설정할 것 (type="number" 사용)
- 회원 등급과 배송 옵션은 Drop-down List 형태로 구현할 것 (`<select>` 태그 사용)
- 버튼 클릭 시 모든 입력값의 유효성을 검사한 후 함수가 호출되도록 할 것
- 함수 실행 결과는 alert()을 사용해 사용자에게 보여줄 것

CSS를 이용하여 페이지의 스타일을 간단히 꾸밀 것 (예: 선택자 `button`, 속성 `background-color`, 값 `green` 등 사용).

###

### 2. 구현 코드

<mark>#구조</mark>

```plain text
/JS
├── order.html
├── style.css
└── script.js
```

<mark>#코드</mark>

```html
<!-- order.html -->

<!DOCTYPE html>
<html lang="ko">
<head>
  <meta charset="UTF-8" />
  <title>주문 시스템</title>
  <link rel="stylesheet" href="style.css" />
</head>
<body>
  <div class="container">
    <h1>주문 시스템</h1>
    <div class="order-card">
      <label for="stock">📦 상품 재고 (숫자):</label>
      <input type="number" id="stock" min="0" placeholder="예: 5" required />

      <label for="membership">👤 회원 등급:</label>
      <select id="membership">
        <option value="Basic">Basic</option>
        <option value="Gold">Gold</option>
        <option value="VIP">VIP</option>
      </select>

      <label for="amount">💰 주문 금액 (숫자):</label>
      <input type="number" id="amount" min="0" placeholder="예: 100000" required />

      <label for="shipping">🚚 배송 옵션:</label>
      <select id="shipping">
        <option value="standard">일반 배송</option>
        <option value="fast">빠른 배송</option>
      </select>

      <button onclick="handleOrder()">📝 주문하기</button>
    </div>
  </div>

  <script src="script.js"></script>
</body>
</html>
```

```css
/* style.css */

body {
    margin: 0;
    padding: 0;
    font-family: 'Segoe UI', sans-serif;
    background: linear-gradient(145deg, #fdfdfd, #eaeaea);
    display: flex;
    justify-content: center;
    align-items: center;
    min-height: 100vh;
  }
  
  .container {
    text-align: center;
  }
  
  h1 {
    margin-bottom: 20px;
    color: #2c3e50;
    font-size: 28px;
  }
  
  .order-card {
    background-color: white;
    padding: 30px;
    border-radius: 16px;
    box-shadow: 0 4px 20px rgba(0,0,0,0.1);
    width: 320px;
    display: flex;
    flex-direction: column;
    align-items: stretch;
  }
  
  label {
    text-align: left;
    margin: 12px 0 5px;
    font-weight: 600;
    color: #333;
  }
  
  input, select {
    padding: 10px;
    border: 1px solid #ccc;
    border-radius: 8px;
    margin-bottom: 10px;
    font-size: 14px;
  }
  
  button {
    background-color: #27ae60;
    color: white;
    font-weight: bold;
    padding: 12px;
    border: none;
    border-radius: 8px;
    font-size: 16px;
    cursor: pointer;
    transition: background-color 0.3s;
  }
  
  button:hover {
    background-color: #219150;
  }
  
  input::placeholder {
    color: #aaa;
  }
```
```js
// script.js

function processOrder(itemStock, membership, orderAmount, shippingOption) {
    if (itemStock < 1) {
      alert("❌ 죄송합니다. 해당 상품은 품절입니다.");
      return;
    }
  
    let discountRate = 0;
    if (membership === "VIP") discountRate = 0.10;
    else if (membership === "Gold") discountRate = 0.05;
  
    let discountedAmount = orderAmount * (1 - discountRate);
  
    if (discountedAmount >= 200000) discountedAmount -= 15000;
    else if (discountedAmount >= 100000) discountedAmount -= 5000;
  
    let shippingFee = shippingOption === "fast" ? 3000 : 0;
  
    const finalAmount = discountedAmount + shippingFee;
  
    alert(`✅ 주문이 정상적으로 완료되었습니다.\n💳 최종 결제 금액: ${finalAmount.toLocaleString("ko-KR")}원`);
  }
  
  function handleOrder() {
    const stock = document.getElementById("stock").value;
    const amount = document.getElementById("amount").value;
    const membership = document.getElementById("membership").value;
    const shipping = document.getElementById("shipping").value;
  
    if (stock === "" || amount === "") {
      alert("📌 상품 재고와 주문 금액을 모두 입력해주세요.");
      return;
    }
  
    const stockNum = parseInt(stock);
    const amountNum = parseInt(amount);
  
    if (isNaN(stockNum) || isNaN(amountNum) || stockNum < 0 || amountNum < 0) {
      alert("⚠️ 재고와 주문 금액은 0 이상의 숫자로 입력되어야 합니다.");
      return;
    }
  
    processOrder(stockNum, membership, amountNum, shipping);
  }
```

###

### 3. 결과

![image](https://github.com/user-attachments/assets/145ea5af-1ae6-4cc6-b8bf-3415d9d3fb06)
![image](https://github.com/user-attachments/assets/f2087716-da4d-4af9-b44d-8699d056b21d)
![image](https://github.com/user-attachments/assets/1bd26353-8111-445f-92bd-467e8a236d2a)
![image](https://github.com/user-attachments/assets/1e061c66-52f2-4b0b-a4e1-0d310944c85d)

#
