---
title: 회의록
body_class: report-wide
# ───────────────────────────────────────────────
# 회의록은 "하나의 구글 독스 문서" 안에 탭(1차·2차·3차…)을 만들어 작성합니다.
# 1) gdoc_url  : 그 구글 독스를 "웹에 게시"한 링크 (File → Share → 웹에 게시)
# 2) tabs      : 문서 안의 각 탭. id 는 구글 독스에서 탭을 클릭했을 때
#                주소창 끝에 보이는 tab=t.XXXX 의 "t.XXXX" 부분입니다.
#                (탭 옵션 → 링크 복사 로도 확인할 수 있습니다)
# ───────────────────────────────────────────────
gdoc_url: ""
tabs:
  - label: "1차 회의"
    id: "t.0"
  - label: "2차 회의"
    id: ""
  - label: "3차 회의"
    id: ""
---

팀 회의록을 **하나의 구글 독스 문서**에 차수별 탭(1차·2차·3차…)으로 작성합니다. 아래 버튼으로 보고 싶은 회의 차수를 골라 보세요. 구글 독스에서 내용을 수정하면 이 페이지에도 자동으로 반영됩니다.

{% assign _has_doc = false %}
{% if page.gdoc_url and page.gdoc_url != "" %}{% assign _has_doc = true %}{% endif %}

{% if _has_doc %}
<div class="doc-tabs" id="meetingTabs">
  {% for t in page.tabs %}
    {% if t.id and t.id != "" %}
    <button type="button"
            class="doc-tab-btn{% if forloop.first %} active{% endif %}"
            data-tab="{{ t.id }}">{{ t.label }}</button>
    {% endif %}
  {% endfor %}
</div>

<div class="gdoc-card">
  <div class="gdoc-bar">
    <span class="gdoc-label">📋 <span id="meetingTitle">회의록</span></span>
    <a class="gdoc-open" id="meetingOpen" href="{{ page.gdoc_url }}" target="_blank" rel="noopener">전체 화면으로 보기 ↗</a>
  </div>
  <div class="gdoc-frame-wrap">
    <iframe class="gdoc-frame" id="meetingFrame" src="" loading="lazy" title="회의록"></iframe>
  </div>
</div>

<script>
(function () {
  var baseUrl = {{ page.gdoc_url | jsonify }};
  var tabsBox = document.getElementById('meetingTabs');
  var frame   = document.getElementById('meetingFrame');
  var openLnk = document.getElementById('meetingOpen');
  var titleEl = document.getElementById('meetingTitle');
  if (!frame) return;

  function buildSrc(tabId) {
    var url = baseUrl;
    if (tabId) { url += (url.indexOf('?') > -1 ? '&' : '?') + 'tab=' + encodeURIComponent(tabId); }
    url += (url.indexOf('?') > -1 ? '&' : '?') + 'embedded=true';
    return url;
  }
  function buildOpen(tabId) {
    var url = baseUrl;
    if (tabId) { url += (url.indexOf('?') > -1 ? '&' : '?') + 'tab=' + encodeURIComponent(tabId); }
    return url;
  }
  function activate(btn) {
    var buttons = tabsBox ? tabsBox.querySelectorAll('.doc-tab-btn') : [];
    for (var i = 0; i < buttons.length; i++) buttons[i].classList.remove('active');
    btn.classList.add('active');
    var tabId = btn.getAttribute('data-tab');
    frame.src = buildSrc(tabId);
    openLnk.href = buildOpen(tabId);
    if (titleEl) titleEl.textContent = btn.textContent.trim();
  }

  if (tabsBox) {
    tabsBox.addEventListener('click', function (e) {
      var btn = e.target.closest('.doc-tab-btn');
      if (btn) activate(btn);
    });
  }

  // 첫 번째(활성) 탭으로 초기화
  var first = tabsBox ? tabsBox.querySelector('.doc-tab-btn.active') : null;
  if (first) { activate(first); }
  else { frame.src = buildSrc(''); }
})();
</script>
{% else %}
<div class="gdoc-empty">
  <p>📋 아직 연결된 회의록 문서가 없습니다.</p>
  <p class="muted">구글 독스로 회의록 문서를 만들고 <strong>탭(1차·2차·3차)</strong>을 추가한 뒤, <strong>파일 → 공유 → 웹에 게시</strong>해서 나온 링크를 이 페이지 파일(<code>meetings.md</code>) 맨 위 <code>gdoc_url:</code> 에 붙여넣으세요. 각 탭의 <code>id</code>도 함께 채우면 버튼으로 차수를 골라 볼 수 있습니다. (<a href="{{ '/CONTRIBUTING' | relative_url }}">자세한 방법</a>)</p>
</div>
{% endif %}

## 회의록 작성 방법 (이대로 따라 하세요)

1. 구글 독스에서 **회의록 문서 하나**를 만듭니다.
2. 왼쪽 위 **탭 표시 및 개요** 아이콘을 눌러 **탭을 추가**하고, 이름을 `1차 회의`, `2차 회의`, `3차 회의` … 로 짓습니다.
3. 각 탭에 아래 양식대로 회의 내용을 적습니다.
4. **파일 → 공유 → 웹에 게시** → 게시 링크를 복사해 `meetings.md` 의 `gdoc_url:` 에 붙여넣습니다.
5. 각 탭을 클릭하면 주소창 끝에 `tab=t.XXXX` 가 보입니다. 그 `t.XXXX` 를 `tabs:` 목록의 해당 차수 `id:` 에 넣습니다.

> **탭 id 찾는 또 다른 방법** — 탭 위에서 **탭 옵션(⋮) → 링크 복사**를 누르면 그 탭으로 바로 가는 링크가 복사됩니다. 링크 끝의 `tab=t.XXXX` 부분을 사용하세요.

## 회의록 양식 (각 탭에 이대로 작성)

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

## 작성 팁

- **한 문서 + 탭 구조**라 차수가 늘어도 링크 하나로 관리됩니다.
- **결정 사항과 To-Do**를 꼭 남겨야 다음 회의에서 이어가기 쉽습니다.
- 새 차수를 추가하면 `meetings.md` 의 `tabs:` 목록에 `label`·`id` 한 줄만 더 넣으면 버튼이 자동으로 생깁니다.
