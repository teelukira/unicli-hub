---
name: email-html-report
description: >-
  조사 결론·작업 결과·비용 요약을 Microsoft Outlook 및 일반 이메일 본문에
  복사-붙여넣기해도 서식이 깨지지 않는 인라인 CSS HTML 문서를 생성한다.
  사용자가 "메일용 html 만들어줘", "아웃룩 메일 본문 생성", "이메일 보고서 작성",
  "메일로 보낼 수 있게 html로 변환"을 요청할 때 트리거.
---

# email-html-report

이메일 클라이언트는 외부 CSS 와 `<style>` 일부 속성을 버린다.
모든 스타일을 태그 `style="..."` 인라인으로 넣어 단일 HTML 파일로 끝낸다.

브라우저 HTML 대시보드·자체 완결 리포트는 `html-report` 스킬을 쓴다.
이 스킬은 **Outlook 붙여넣기** 가 목적인 경우에만 쓴다.

---

## 작성 원칙

1. 문체: 공학적 건조체 (`~함`, `~이다`, `~로 구성됨`). 구어체 배제.
   상단 작성자/날짜 헤더를 넣지 않는다. 본문은 결론 또는 개요 표로 시작한다.
   볼드 남발 금지. 표·수치·박스로 구조화한다.
2. Outlook 호환:
   - 스타일은 전부 인라인 `style`
   - 폰트: `font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif, 'Malgun Gothic', '맑은 고딕';`
   - 표: `border-collapse: collapse; width: 100%;` 헤더 배경 `#f1f5f9`, 테두리 `#cbd5e1`
   - 요약 박스: `background-color: #f8fafc; border-left: 4px solid #2563eb; padding: 12px 16px; margin: 16px 0;`
   - `<style>` 블록, flex/grid, position, 외부 이미지 URL 에 의존하지 않는다
3. 팔레트:
   - 제목 `#1e293b` / 섹션 `#1e3a8a` / 표 헤더 `#f1f5f9` / 테두리 `#e2e8f0`
   - 성공 `#15803d` / 경고 `#b45309`

---

## 워크플로

1. 보고 데이터를 취합한다.
2. Top-down 으로 짠다: 결론 → 전/후 비교 → 검증 → 후속 조치.
3. 작업 산출물 디렉터리에 `.html` 로 쓴다.
4. 브라우저에서 열어 `Ctrl+A` → `Ctrl+C` 후 Outlook 본문에 `Ctrl+V` 했을 때
   표·박스·색이 유지되는지 확인한다.

---

## 최소 골격

```html
<!DOCTYPE html>
<html lang="ko">
<body style="margin:0;padding:16px;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,'Helvetica Neue',Arial,sans-serif,'Malgun Gothic','맑은 고딕';color:#1e293b;font-size:14px;line-height:1.5;">
  <div style="background-color:#f8fafc;border-left:4px solid #2563eb;padding:12px 16px;margin:16px 0;">결론 한 줄</div>
  <table style="border-collapse:collapse;width:100%;">
    <tr>
      <th style="background-color:#f1f5f9;border:1px solid #cbd5e1;padding:8px 10px;text-align:left;">항목</th>
      <th style="background-color:#f1f5f9;border:1px solid #cbd5e1;padding:8px 10px;text-align:left;">값</th>
    </tr>
  </table>
</body>
</html>
```
