---
title: 홈
---

## 프로젝트 개요

**MAGIC(의공학마법사)** 팀은 시각장애인을 위한 **점자 인식 웨어러블 기기**를 연구합니다. 손가락에 착용하는 작은 기기가 광섬유 또는 압력 센서로 점자를 읽어내고, 블루투스로 스마트폰에 전송하면 AI가 해당 점자를 글자로 해석해 음성으로 들려줍니다.

이 사이트는 팀의 연구 기록과 설계 자료를 정리한 공식 홈페이지입니다. 팀원 누구나 GitHub에서 Markdown 파일을 수정해 내용을 추가·갱신할 수 있습니다.

<div class="card-grid">
  <a class="card" href="introduction">
    <div class="card-icon">📖</div>
    <h3>프로젝트 소개</h3>
    <p>연구 배경, 목표, 동작 원리</p>
  </a>
  <a class="card" href="hardware">
    <div class="card-icon">🔧</div>
    <h3>하드웨어 설계</h3>
    <p>센서 회로, PCB, 3D 하우징 설계 패키지</p>
  </a>
  <a class="card" href="report">
    <div class="card-icon">📝</div>
    <h3>보고서</h3>
    <p>구글독스 제안서·최종보고서 연동</p>
  </a>
  <a class="card" href="meetings">
    <div class="card-icon">📋</div>
    <h3>회의록</h3>
    <p>팀 회의 기록 모음</p>
  </a>
  <a class="card" href="timeline">
    <div class="card-icon">📅</div>
    <h3>연구 일정</h3>
    <p>개발 단계별 추진 일정</p>
  </a>
  <a class="card" href="members">
    <div class="card-icon">👥</div>
    <h3>팀 소개</h3>
    <p>팀원과 역할 분담</p>
  </a>
  <a class="card" href="downloads">
    <div class="card-icon">📦</div>
    <h3>자료실</h3>
    <p>설계 파일, 다이어그램, 스크립트</p>
  </a>
  <a class="card" href="CONTRIBUTING">
    <div class="card-icon">✏️</div>
    <h3>홈페이지 수정 방법</h3>
    <p>팀원을 위한 편집 가이드</p>
  </a>
</div>

---

## 핵심 아이디어

<div class="table-wrap" markdown="1">

| 단계 | 내용 |
|---|---|
| ① 입력 | 손끝 센서(광섬유/압력)가 점자 돌기를 감지 |
| ② 전송 | ESP32 마이크로컨트롤러가 신호를 디코딩해 블루투스로 전송 |
| ③ 해석 | 스마트폰 앱에서 AI가 점자 패턴을 글자로 변환 |
| ④ 출력 | 음성(TTS)으로 사용자에게 읽어줌 |

</div>

> 본 홈페이지의 하드웨어 설계 자료는 공식 데이터시트와 표준 문서를 근거로 작성되었습니다. 자세한 출처는 각 문서에 표기되어 있습니다.
