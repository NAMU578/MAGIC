---
title: 회의록
# 회의록을 추가하려면 아래 meetings 목록에 항목을 넣으세요.
# 각 항목: date(날짜), title(제목), url(구글독스 게시 링크)
meetings:
  # - date: "2026-06-24"
  #   title: "1차 회의 — 역할 분담"
  #   url: "여기에_구글독스_게시_링크"
---

팀 회의록을 구글독스로 작성하고 이곳에 연동합니다. 각 회의 문서를 구글독스에서 "웹에 게시"한 뒤 링크를 등록하면 목록에 나타납니다.

{% if page.meetings and page.meetings.size > 0 %}
<div class="doc-list">
  {% for m in page.meetings %}
  <a class="doc-item" href="{{ m.url }}" target="_blank" rel="noopener">
    <span class="doc-item-title">{{ m.title }}</span>
    <span class="doc-item-date">{{ m.date }} ↗</span>
  </a>
  {% endfor %}
</div>
{% else %}
<div class="gdoc-empty">
  <p>📋 아직 등록된 회의록이 없습니다.</p>
  <p class="muted">구글독스로 회의록을 작성하고 <strong>웹에 게시</strong>한 뒤, 이 페이지 파일(<code>meetings.md</code>) 맨 위의 <code>meetings:</code> 목록에 날짜·제목·링크를 추가하세요. (<a href="{{ '/CONTRIBUTING' | relative_url }}">자세한 방법</a>)</p>
</div>
{% endif %}

## 회의록 양식 (이대로 작성하세요)

회의마다 아래 양식을 **구글독스에 새 문서로 복사**해서 작성한 뒤, 웹에 게시해서 위 목록에 등록하세요.

<div class="table-wrap" markdown="1">

**■ 회의 개요**

| 항목 | 내용 |
|---|---|
| 회의 차수 | 제 N 차 회의 |
| 일시 | 2026. __. __. (요일) __:__ ~ __:__ |
| 장소 | 학교 OO실 / 온라인 |
| 참석자 | 유동형, 정영현, 조영진, 최준우 (불참: ___) |
| 작성자 | ___ |

</div>

- **회의 목표** — 이번 회의의 핵심 안건 1~3줄
- **진행 상황 보고** — 지난 회의 이후 팀원별 진행 내용
- **논의 내용** — 안건별 논의·근거
- **결정 사항** — 무엇을, 왜 결정했는지
- **다음 할 일(To-Do)** — 담당자 / 할 일 / 기한 표
- **다음 회의** — 일시·주요 안건

## 회의록 작성 팁

- 회의마다 새 구글독스 문서를 만들면 관리가 편합니다.
- **결정 사항과 To-Do**를 꾭 남겨야 다음 회의에서 이어가기 쉽습니다.
- 날짜는 `2026-06-24` 형식으로 통일하면 정렬이 깔끔합니다.
