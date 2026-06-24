# 점자 인식 웨어러블 하드웨어 설계 패키지
## "손끝에서 귀로" — 한글 점자 번역 웨어러블 기기

> **작성 목적**: 의공학마법사 팀(경북과학고등학교)의 KOSOMBE 창의경진대회 제안 기기 중 **하드웨어 및 회로기판(PCB)** 설계 담당(조영진)을 위한 종합 설계 가이드입니다.
> **포함 범위**: ① 시스템 아키텍처 ② 센서 프론트엔드 회로 2종(광섬유/압력) ③ 전체 스케매틱 + BOM ④ PCB 레이아웃 가이드 ⑤ Fusion 360 3D 설계 가이드 ⑥ 펌웨어/신호처리 개요
> **검증 기준**: 모든 부품 사양과 설계값은 공식 데이터시트·표준 문서를 근거로 합니다(각 항목에 출처 표기).

---

## 0. 설계 철학 및 두 가지 센서 방식 비교

제안서에서 광섬유(메인)와 압력센서(대안) 두 방식을 모두 언급하셨으므로, **두 버전을 모두 설계**하여 프로토타입 단계에서 직접 비교·선택할 수 있도록 했습니다. 두 방식은 손끝 패드와 센서 프론트엔드 회로만 다르고, **MCU·전원·배터리·블루투스 부분(메인 보드)은 100% 동일**하게 설계합니다. 이렇게 하면 메인 보드를 한 번만 만들고 센서 모듈만 교체하며 비교할 수 있습니다.

| 항목 | 방식 A: 광섬유(POF) 굽힘 센서 | 방식 B: 압력(FSR) 센서 |
|---|---|---|
| 감지 원리 | 점자 돌기가 광섬유를 누르면 굽힘 손실 발생 → 투과 광량 감소 | 점자 돌기 압력으로 저항 감소 → 분압 전압 변화 |
| 핵심 부품 | POF + LED + 포토다이오드(또는 OPT101) | FSR 402 + 기준저항 + (옵션) 멀티플렉서 |
| 회로 난이도 | **높음** (TIA·광 정렬·노이즈) | **낮음** (단순 분압) |
| 디버깅 난이도 | 높음 (광량을 눈으로 못 봄) | 낮음 (멀티미터로 바로 측정) |
| 제안서 부합도 | 메인 아이디어, 차별성 강조 | 대안, 빠른 검증에 유리 |
| 권장 용도 | **최종 시연/제안 핵심** | **초기 개념 검증(PoC)·백업** |

> **조영진 학생에게 드리는 실전 조언**: 시간이 빠듯하다면 **방식 B(FSR)로 먼저 점자 셀 인식 로직과 펌웨어를 완성**한 뒤, 그 위에서 방식 A(광섬유)로 차별성을 입증하는 전략을 추천합니다. 펌웨어·메인 보드를 공유하므로 센서만 갈아끼우면 됩니다.

---

## 1. 시스템 아키텍처 (전체 블록 다이어그램)

```
┌─────────────────────────────────────────────────────────────┐
│  손끝 센서 패드 (착용부)                                       │
│  ┌──────────────────────┐   또는   ┌──────────────────────┐  │
│  │ 방식 A: POF 6~10채널  │          │ 방식 B: FSR 6채널 어레이│  │
│  │ LED → POF → 포토다이오드│          │ FSR + 분압저항         │  │
│  └──────────┬───────────┘          └──────────┬───────────┘  │
│             │ 아날로그 전압 (0~3.3V)            │             │
└─────────────┼───────────────────────────────────┼────────────┘
              │                                   │
        ┌─────▼───────────────────────────────────▼─────┐
        │  신호 프론트엔드                                │
        │  · 방식A: TIA(OPT101 내장) → RC 필터           │
        │  · 방식B: 분압 → (옵션) 버퍼 → RC 필터          │
        │  · 채널 > ADC핀 수 → 아날로그 MUX(CD74HC4067)   │
        └───────────────────────┬───────────────────────┘
                                │ ADC 입력 (다채널)
        ┌───────────────────────▼───────────────────────┐
        │  MCU: ESP32-S3-MINI-1                           │
        │  · 12bit ADC 다채널 샘플링                       │
        │  · 점자 셀 패턴 디코딩(임계값 분류)               │
        │  · BLE로 디코딩 결과 전송                         │
        └───────┬────────────────────────────┬───────────┘
                │ BLE                         │
        ┌───────▼────────┐          ┌─────────▼──────────┐
        │ 스마트폰 앱     │          │ 전원 서브시스템     │
        │ · LLM 교정      │          │ · LiPo 셀          │
        │ · TTS 출력      │          │ · MCP73831 충전 IC  │
        │ (소프트웨어 팀) │          │ · USB-C 입력        │
        └────────────────┘          │ · 3.3V LDO/벅       │
                                    │ · 배터리 보호(DW01) │
                                    └────────────────────┘
```

**하드웨어 담당 범위(조영진)**: 위 그림의 점선 박스(센서 패드) + 신호 프론트엔드 + ESP32 메인 보드 + 전원 서브시스템 = **PCB 전체와 3D 하우징**. LLM/TTS 앱은 정보 담당(최준우)이 처리합니다.

---

## 2. 핵심 설계 사양 (검증된 근거값)

### 2.1 한글 점자 물리 규격 (설계 입력값)
센서 패드의 치수를 결정하는 가장 중요한 기준입니다. 문화체육관광부 「한국 점자 규정」(2024 개정) 및 국립국어원 해설서 기준:

| 파라미터 | 규격 값 | 설계 시사점 |
|---|---|---|
| 점 높이 | 0.6 ~ 0.9 mm (2024 개정 시 0.4mm까지 허용 논의) | 센서가 감지해야 할 최소 변형량 |
| 점 지름 | 1.5 ~ 1.6 mm | 센서 감지면 분해능 기준 |
| 점간 거리 | 2.3 ~ 2.5 mm | **센서 채널 피치(간격)의 기준** |
| 자간 거리 | 5.5 ~ 6.9 mm (종이) | 셀 단위 인식 시 셀 폭 |
| 셀 구성 | 2열 × 3행 = 6점 | 6채널 센서 기본 구성 |

출처: [한국 점자 규정 해설, 국립국어원](https://www.korean.go.kr); [점자 세부규격, 한국지능정보사회진흥원 키오스크UI](https://www.kioskui.or.kr/index.do?menu_id=00001049); 국제 표준 [ISO 17049:2013](https://cdn.standards.iteh.ai/samples/58086/fb6f17bed4ff425fa03583afabdafb97/ISO-17049-2013.pdf) (점간 a 2.2~2.8mm, b 2.0~2.8mm).

> **핵심 설계값**: 점간 거리 **2.5mm**를 센서 채널 피치의 기준으로 삼습니다. 단, 미세 센서를 0.5mm 간격으로 6개 배열하는 것은 매우 어렵습니다(아래 6.3 "스캐닝 방식" 참고).

### 2.2 검증된 전자 부품 사양

| 부품 | 핵심 사양 | 출처 |
|---|---|---|
| **ESP32-S3** | 12bit SAR ADC, 다채널, 입력 0~3.3V, BLE 5.0 내장 | [Espressif ESP32-S3 ADC](https://docs.espressif.com/projects/esp-idf/en/stable/esp32s3/api-reference/peripherals/adc/index.html) |
| **FSR 402** | 활성면 ⌀12.7mm, 두께 0.46mm, 작동력 ~0.1N부터, 무압 >1MΩ ~ 최대압 ~200Ω | [Interlink FSR 400 Datasheet](https://cdn2.hubspot.net/hubfs/3899023/Interlinkelectronics%20November2017/Docs/Datasheet_FSR.pdf); [Adafruit FSR Guide](https://cdn-learn.adafruit.com/assets/assets/000/010/126/original/fsrguide.pdf) |
| **OPT101** | 포토다이오드+TIA 통합, 2.7~36V, 정지전류 120µA, 내장 1MΩ 피드백 | [TI OPT101 Datasheet](https://www.ti.com/lit/ds/symlink/opt101.pdf) |
| **MCP73831** | 단일셀 LiPo 충전, 4.2V CC/CV, 전류 = 1000/R_PROG(mA), SOT-23-5 | [Microchip MCP73831](https://www.ultralibrarian.com/2021/11/04/mcp73831-datasheet-a-linear-charge-management-controller-ulc/) |
| **CD74HC4067** | 16:1 아날로그 멀티플렉서 (다채널 → 1 ADC) | TI 표준 부품 |

---

## 3. 센서 프론트엔드 회로 — 방식 A: 광섬유(POF)

### 3.1 동작 원리
플라스틱 광섬유(POF)의 한쪽 끝에 LED 광원을 넣고 반대쪽 끝을 포토다이오드로 받습니다. 점자 돌기가 광섬유를 국부적으로 누르면 **매크로벤딩(macrobending) 손실**이 발생해 투과 광량이 감소하고, 포토다이오드 전류가 줄어듭니다. 이 전류를 TIA(트랜스임피던스 증폭기)로 전압으로 바꿔 ADC가 읽습니다.

광섬유 굽힘 손실의 물리적 근거: 굽힘 반경이 작을수록(눌릴수록) 광 손실이 증가하며, 이는 강도측정(intensiometric) 방식 센서의 표준 원리입니다 ([Macrobending POF sensor, ITS journal](https://iptek.its.ac.id/index.php/jfa/article/download/20(2)06/pdf_99)).

### 3.2 회로 구성 (채널 1개 기준)

```
   3.3V
    │
   [R_LED 100~330Ω]      ← LED 전류 제한 (I = (3.3 - Vf)/R)
    │
  [LED]  ──광──> POF(0.5mm, U자 삽입) ──광──> [포토다이오드]
                                                  │
                                          ┌───────┴────────┐
                                          │  TIA (OPT101    │
                                          │  내장형 권장)    │
                                          │  Vout = I × Rf  │
                                          └───────┬────────┘
                                                  │
                                          [RC 저역통과필터]  ← R 10kΩ + C 100nF
                                                  │
                                              ADC 핀 (ESP32)
```

### 3.3 권장 설계 (초보자 친화)
- **OPT101 사용 강력 권장**: 포토다이오드 + TIA가 한 칩에 통합되어 있어, 직접 op-amp로 TIA를 설계할 때 흔히 겪는 발진·노이즈 문제를 크게 줄여줍니다. 내장 1MΩ 피드백 저항으로 0.45A/W(650nm) 응답성을 제공합니다 ([TI OPT101](https://www.ti.com/lit/ds/symlink/opt101.pdf)).
- **LED 선택**: 가시광 적색 LED(파장 ~650nm)가 OPT101 응답성과 잘 맞습니다. POF는 650nm에서 손실이 낮습니다.
- **단일 전원 동작 보정**: 직접 op-amp(예: MCP6022, TL082)로 TIA를 만들 경우, 비반전 입력에 ~0.2V 바이어스를 걸어 0V 레일 포화를 방지합니다 ([TI TIPD176](https://www.ti.com/tool/TIPD176); devttys0 TIA 설계).

### 3.4 직접 TIA 설계 시 (OPT101 대신 op-amp 사용)

```
                    Rf (1MΩ)
              ┌──────WWW──────┐
              │      Cf(10pF) │   ← 안정화용 피드백 커패시터
              │  ┌────││────┐ │
포토다이오드 ──┴──┤-          ├─┴──> Vout → ADC
        (역바이어스) │  op-amp   │
              ┌──┤+          │
   바이어스 ───┘  └───────────┘
   (~0.2V, 분압)
```
- 피드백 저항 R_f가 클수록 이득 증가(V_out = I_photo × R_f). 1MΩ이면 1µA → 1V.
- C_f는 발진 방지 필수. 대역폭 = 1/(2π·R_f·C_f) ([Transimpedance amplifier, Wikipedia](https://en.wikipedia.org/wiki/Current-to-voltage_converter); [RP Photonics](https://www.rp-photonics.com/photodiode_amplifiers.html)).
- op-amp는 **FET 입력·저 바이어스 전류** 제품 선택(입력 전류가 신호 손실).

### 3.5 다채널 처리
6~10채널이 필요하므로:
1. **OPT101 6~10개 + 아날로그 MUX(CD74HC4067)** → ESP32 ADC 1핀으로 순차 읽기, 또는
2. **ESP32-S3의 다중 ADC 핀 직접 사용**(ADC1: GPIO1~10 중 다수 사용 가능). ADC2는 Wi-Fi/BLE 사용 시 충돌 가능하므로 **ADC1 핀만 사용** 권장.

---

## 4. 센서 프론트엔드 회로 — 방식 B: 압력(FSR)

### 4.1 동작 원리
FSR(Force Sensitive Resistor)은 누르는 힘이 커질수록 저항이 감소합니다(무압 >1MΩ → 강압 ~200Ω). 기준저항과 직렬로 연결한 **분압 회로**로 전압을 만들어 ADC로 읽습니다 ([Adafruit FSR Guide](https://cdn-learn.adafruit.com/assets/assets/000/010/126/original/fsrguide.pdf)).

### 4.2 분압 회로 (채널 1개 기준)

```
   3.3V
    │
  [FSR 402]      ← 점자 돌기 압력 감지
    │
    ├──────────> ADC 핀 (ESP32)
    │
  [R_M 10kΩ]     ← 기준(풀다운) 저항
    │
   GND

   Vout = 3.3V × R_M / (R_M + R_FSR)
   힘↑ → R_FSR↓ → Vout↑
```

- **기준저항 R_M 선택**: 가벼운 터치(점자 돌기는 약한 압력) 감지가 목적이므로 **47kΩ**이 미세 압력에 유리. 넓은 범위면 **10kΩ** ([FSR 센서 인터페이스, Wasil Zafar](https://www.wasilzafar.com/pages/series/sensors-actuators/sensors-actuators-sensor-fsr.html)).
- ESP32는 3.3V 시스템이므로 분압 상단을 **3.3V**로 연결(5V 금지, ADC 최대 3.3V).
- **노이즈 저감**: 각 ADC 입력에 0.1µF 커패시터를 GND로 추가하면 안정적 ([Adafruit FSR Guide](https://cdn-learn.adafruit.com/downloads/pdf/force-sensitive-resistor-fsr.pdf)).

### 4.3 6채널 어레이 + 버퍼(옵션)
- FSR 6개(점자 6점 대응)를 각각 분압 → 6개 ADC 핀 직접 입력.
- FSR은 part-to-part 편차 ±20~30%로 크므로, **채널별 개별 캘리브레이션 필수**(펌웨어에서 임계값 보정).
- 분압 출력 임피던스가 높아 ADC 정확도가 떨어지면, 채널마다 op-amp 버퍼(전압 팔로워, 예: LM358/MCP6002) 추가.

### 4.4 FSR의 한계와 보완 (제안서 "실패 가능성" 대응)
- 점자 돌기 높이는 0.6~0.9mm로 매우 작아 FSR의 작동력(~0.1N) 근처에서 동작 → 감도 부족 가능.
- **보완**: 손끝 패드에 미세 돌기·필름을 덧대 압력을 집중시키거나, FSR 위 실리콘 패드로 점자 패턴을 전사받는 구조 설계(아래 7장 3D 하우징 참고).

---

## 5. 전체 회로 스케매틱 (메인 보드 — 두 방식 공통)

### 5.1 블록별 스케매틱 텍스트 표현

```
[USB-C 커넥터]
  VBUS(5V) ──┬──> [MCP73831 충전 IC] ──> [LiPo 셀 3.7V]
             │      PROG: R=2kΩ → 500mA 충전 (I=1000/R_kΩ)
             │      STAT → LED(충전표시)
             │      VIN, VBAT에 각 4.7µF 세라믹
             │
  D+/D- ─────┴──> ESP32-S3 USB (펌웨어 업로드/디버그)

[LiPo 3.7V] ──> [배터리 보호 DW01+FS8205] ──> [전원 스위치]
                                                  │
                                          ┌───────┴────────┐
                                          │ 3.3V LDO        │  (예: AP2112K-3.3,
                                          │ 또는 벅 컨버터   │   600mA, 저드롭아웃)
                                          └───────┬────────┘
                                                  │ 3.3V 시스템 레일
        ┌─────────────────────────────────────────┼──────────────────┐
        │                                          │                  │
  [ESP32-S3-MINI-1]                          [센서 프론트엔드]    [부트/리셋 회로]
   · 3V3, GND, EN(10kΩ풀업+버튼)               방식A 또는 B        · EN: 10kΩ+0.1µF
   · IO0 (부트, 버튼)                                              · IO0: 버튼
   · ADC1 핀들 → 센서 입력                                         
   · 디커플링: 10µF + 0.1µF (전원핀 근처)
```

### 5.2 ESP32-S3 핀 할당 예시

| 기능 | GPIO | 비고 |
|---|---|---|
| ADC 채널 0~5 (센서 6점) | GPIO1~6 (ADC1) | Wi-Fi/BLE와 충돌 없는 ADC1 사용 |
| MUX 선택선 S0~S3 (방식A 다채널 시) | GPIO7~10 | CD74HC4067 제어 |
| 충전 STAT 입력 | GPIO11 | 충전 상태 모니터 |
| 상태 LED | GPIO12 | 동작 표시 |
| 부트 버튼 | GPIO0 | 펌웨어 모드 |
| 리셋(EN) | EN 핀 | 풀업+버튼 |
| USB D+/D- | GPIO19/20 | 네이티브 USB |

출처: ESP32-S3 ADC2는 무선 사용 시 사용 불가 → ADC1 채널만 할당 ([Espressif ADC docs](https://docs.espressif.com/projects/esp-idf/en/stable/esp32s3/api-reference/peripherals/adc/index.html)).

### 5.3 BOM (부품 명세서)

#### 공통 메인 보드
| # | 부품 | 권장 부품번호 | 수량 | 비고 |
|---|---|---|---|---|
| 1 | MCU 모듈 | ESP32-S3-MINI-1 | 1 | BLE 내장, 작은 풋프린트 |
| 2 | LiPo 충전 IC | MCP73831T-2ACI/OT (SOT-23-5) | 1 | 500mA, 4.2V |
| 3 | 3.3V LDO | AP2112K-3.3TRG1 | 1 | 600mA |
| 4 | 배터리 보호 IC | DW01A + FS8205A | 1조 | 과충/과방전 보호 |
| 5 | LiPo 배터리 | 3.7V 250~500mAh (보호회로 내장형 권장) | 1 | 웨어러블 크기 고려 |
| 6 | USB-C 리셉터클 | USB4085 등 16핀 | 1 | 전원+데이터 |
| 7 | PROG 저항 | 2kΩ 1% | 1 | 충전전류 500mA |
| 8 | 디커플링 커패시터 | 10µF / 0.1µF (0603) | 각 다수 | 전원핀 근처 |
| 9 | 충전 입출력 커패시터 | 4.7µF (0603) | 2 | VIN/VBAT |
| 10 | 상태/충전 LED | 0603 LED + 1kΩ | 2 | |
| 11 | 택트 스위치 | 부트/리셋/전원 | 3 | |

#### 방식 A: 광섬유 센서 모듈
| # | 부품 | 권장 부품번호 | 수량 | 비고 |
|---|---|---|---|---|
| A1 | 플라스틱 광섬유(POF) | ⌀0.5mm 또는 ⌀0.75mm | 6~10가닥 | 점자 점 대응 |
| A2 | LED 광원 | 적색 650nm (0805 또는 3mm) | 6~10 | POF 입사용 |
| A3 | 광검출 TIA | OPT101P | 6~10 | 통합 포토다이오드+TIA |
| A4 | 아날로그 MUX | CD74HC4067 | 1 | 채널>ADC핀 시 |
| A5 | LED 전류제한 저항 | 100~330Ω | 6~10 | |
| A6 | RC 필터 | 10kΩ + 100nF | 채널당 1조 | |

#### 방식 B: 압력 센서 모듈
| # | 부품 | 권장 부품번호 | 수량 | 비고 |
|---|---|---|---|---|
| B1 | 압력 센서 | Interlink FSR 402 (Short Tail) | 6 | 점자 6점 |
| B2 | 기준저항 | 10kΩ 또는 47kΩ 1% | 6 | 분압용 |
| B3 | 버퍼 op-amp(옵션) | MCP6002 (2채널) | 3 | 임피던스 정합 |
| B4 | 노이즈 커패시터 | 0.1µF | 6 | ADC 입력 |

---

## 6. PCB 레이아웃 가이드

### 6.1 보드 분할 전략 (권장: 2-보드 구조)
웨어러블 특성상 **유연성과 착용성**이 중요하므로 보드를 둘로 나눕니다:

1. **센서 보드 (손끝)**: 매우 작게(약 15×20mm). 방식 A는 OPT101+LED, 방식 B는 FSR 패드. FPC(연성 PCB) 또는 얇은 리지드 보드.
2. **메인 보드 (손등/손목)**: ESP32-S3 + 전원 + 충전(약 25×35mm). 둘은 가는 FFC 케이블 또는 실리콘 피복 와이어로 연결.

### 6.2 레이아웃 핵심 규칙
- **2층 PCB로 충분**. 한 면 전체를 GND 그라운드 플레인으로.
- **ESP32 안테나 영역**: 모듈 안테나 아래·주변에는 구리/부품 금지(keep-out). 보드 가장자리로 안테나가 튀어나오게 배치.
- **전원부 디커플링**: 10µF + 0.1µF를 ESP32 전원핀에서 2~3mm 이내 배치.
- **방식 A(TIA) 특별 주의**: 포토다이오드/TIA 반전입력 노드 주변은 스트레이 커패시턴스 최소화. 입력 노드 아래 그라운드 플레인 컷아웃, 피드백 R/C를 op-amp 핀에 최대한 근접 배치, 가드링 적용 ([TIA PCB 레이아웃, PCBGOGO](https://www.pcbgogo.com/Article/how-to-design-a-photodiode-transimpedance-amplifier.html)).
- **아날로그/디지털 분리**: 센서 아날로그 신호 트레이스를 ESP32 고속 디지털·USB 트레이스에서 멀리.
- **충전 IC 열**: MCP73831은 충전 중 발열 → 방열 구리 패드 확보.

### 6.3 ★중요: 6점 동시 vs 스캐닝(1점) 방식 결정
점간 거리 2.5mm 안에 센서 6개를 모두 넣는 것은 물리적으로 매우 어렵습니다. 두 가지 현실적 접근:

- **(권장 초기) 단일 센서 스캐닝**: 센서 1개를 손끝에 두고 점자를 **쓸어가며(슬라이딩)** 읽음. 시간축으로 6점 패턴을 재구성. 하드웨어가 단순해져 프로토타입에 최적.
- **(고급) 6점 정밀 어레이**: 미세 FSR 또는 POF 6가닥을 2×3로 정밀 배열. 제조 난이도 높음. 제안서의 "다중 감지 레이어" 전략과 연결.

> 시연 일정(센서 제작 6/26~7/26)을 고려하면 **단일 센서 스캐닝으로 시작 → 정확도 평가 후 어레이로 확장**을 권장합니다.

### 6.4 추천 EDA 도구
- **KiCad** (무료, 오픈소스): 학생 프로젝트 표준. ESP32-S3-MINI-1, MCP73831 등 라이브러리 풍부.
- 발주: JLCPCB/PCBWay (소량·저가, 학생 예산 30만원 내 적합).

---

## 7. Fusion 360 3D 설계 가이드 (하우징/웨어러블 구조)

> 아래 7.1~7.4는 **수동 모델링 단계별 가이드**, 별도 파일 `fusion360_braille_wearable.py`는 **자동 생성 스크립트**입니다.

### 7.1 설계할 3D 부품 목록
1. **손끝 센서 캡(thimble)**: 검지에 끼우는 골무형. 센서 패드 수납.
2. **메인 보드 인클로저(손등/손목)**: ESP32+배터리+PCB 수납 박스(상·하 2피스).
3. **연결 구조**: 캡과 박스를 잇는 플렉시블 밴드 또는 케이블 가이드.

### 7.2 핵심 치수 설계값
| 부품 | 치수 | 근거 |
|---|---|---|
| 손끝 캡 내경 | 성인 검지 ⌀ ~16~18mm (조절 가능 슬릿) | 인체공학 |
| 센서 개구부 | ⌀13mm 이상 (FSR 402 활성면 ⌀12.7mm) | [FSR 402 datasheet](https://cdn2.hubspot.net/hubfs/3899023/Interlinkelectronics%20November2017/Docs/Datasheet_FSR.pdf) |
| 점자 접촉 윈도우 | 셀 폭 ~6mm × 높이 ~10mm | 점자 1셀 + 여유 |
| 메인 박스 내부 | PCB 25×35mm + 배터리 + 여유 → 약 30×40×12mm | BOM 기준 |
| 벽 두께 | 1.5~2.0mm (FDM 3D프린트 기준) | 강성 |
| 배터리 칸 | 250~500mAh LiPo (예: 30×20×5mm) | 부품 실측 |

### 7.3 Fusion 360 수동 모델링 순서
1. **새 디자인 → 파라미터 설정**(Modify > Change Parameters): `finger_dia`, `wall`, `pcb_w`, `pcb_l`, `batt_h` 등 변수로 등록 → 나중에 한 번에 수정.
2. **손끝 캡**: 스케치로 ⌀(finger_dia+2·wall) 원 → Extrude → Shell(wall 두께) → 바닥에 센서 윈도우 컷.
3. **메인 박스 하부**: 박스 스케치 → Extrude → Shell(상단 개방) → PCB 보스(나사 기둥) 추가.
4. **메인 박스 상부 뚜껑**: 하부에 스냅핏 또는 M2 나사 체결부.
5. **케이블 채널**: 캡-박스 사이 와이어 통로(⌀2~3mm).
6. **출력**: STL 내보내기 → 3D 프린터(FDM, TPU 밴드는 유연 필라멘트).

### 7.4 파라메트릭 스크립트 자동 생성
첨부한 `fusion360_braille_wearable.py`를 Fusion 360의 **Utilities > Add-Ins > Scripts and Add-Ins**에서 실행하면 위 부품의 기본 형상이 자동 생성됩니다. 치수는 스크립트 상단 변수로 즉시 조절 가능합니다.

---

## 8. 펌웨어 / 신호처리 개요 (ESP32, 하드웨어 검증용)

> 이 코드는 **하드웨어가 제대로 동작하는지 검증**하기 위한 골격입니다. LLM/TTS 연동은 앱(최준우) 담당이며, 여기서는 ① ADC 읽기 ② 점자 셀 디코딩 ③ BLE 전송까지 다룹니다.

### 8.1 신호처리 흐름
```
ADC 다채널 샘플링 (수십~수백 Hz)
   → 이동평균/중앙값 필터 (노이즈 제거)
   → 채널별 임계값 비교 (점 ON/OFF 판정)
   → 6비트 셀 패턴 구성 (점1~점6)
   → 한글 점자 매핑 테이블 → 글자 후보
   → BLE Notify로 앱에 전송
```

### 8.2 ESP32 펌웨어 골격 (Arduino 프레임워크, 예시)

```cpp
#include <Arduino.h>
#include <NimBLEDevice.h>   // 경량 BLE 라이브러리

// ── 핀 설정 (방식 B: FSR 6채널 직접 ADC) ──
const int SENSOR_PINS[6] = {1, 2, 3, 4, 5, 6};  // ADC1 채널
int threshold[6];                                // 채널별 임계값(캘리브레이션)

// ── 이동평균 필터 ──
const int N = 8;
int buf[6][N]; int idx = 0;

int readFiltered(int ch) {
  buf[ch][idx % N] = analogRead(SENSOR_PINS[ch]);
  long sum = 0;
  for (int i = 0; i < N; i++) sum += buf[ch][i];
  return sum / N;
}

// ── 캘리브레이션: 무압 상태 기준 + 마진 ──
void calibrate() {
  for (int ch = 0; ch < 6; ch++) {
    long base = 0;
    for (int i = 0; i < 50; i++) base += analogRead(SENSOR_PINS[ch]);
    base /= 50;
    threshold[ch] = base + 200;   // 마진(실험으로 조정)
  }
}

// ── 6점 → 셀 패턴(비트) ──
uint8_t readCell() {
  uint8_t cell = 0;
  for (int ch = 0; ch < 6; ch++) {
    if (readFiltered(ch) > threshold[ch]) cell |= (1 << ch);
  }
  return cell;   // bit0=점1 ... bit5=점6
}

// ── BLE 설정 ──
NimBLECharacteristic* pChar;
void setupBLE() {
  NimBLEDevice::init("BrailleReader");
  NimBLEServer* s = NimBLEDevice::createServer();
  NimBLEService* svc = s->createService("180D");
  pChar = svc->createCharacteristic("2A37", NIMBLE_PROPERTY::NOTIFY);
  svc->start();
  NimBLEDevice::getAdvertising()->start();
}

void setup() {
  Serial.begin(115200);
  analogReadResolution(12);              // 12bit ADC
  analogSetAttenuation(ADC_11db);        // 0~3.3V 입력 범위
  for (int ch = 0; ch < 6; ch++) pinMode(SENSOR_PINS[ch], INPUT);
  setupBLE();
  delay(500);
  calibrate();
}

void loop() {
  static uint8_t lastCell = 0xFF;
  uint8_t cell = readCell();
  if (cell != lastCell && cell != 0) {     // 변화 + 비어있지 않을 때만
    pChar->setValue(&cell, 1);
    pChar->notify();                        // 앱으로 셀 비트 전송
    Serial.printf("Cell: %06b\n", cell);
    lastCell = cell;
    delay(120);                             // 디바운스
  }
  idx++;
  delay(5);
}
```
- ADC 설정 근거: ESP32 12bit, 11dB 감쇠 시 0~3.3V 측정 ([ESP32 ADC, DeepBlue](https://deepbluembedded.com/esp32-adc-tutorial-read-analog-voltage-arduino/)).
- 방식 A(광섬유)는 임계값 방향이 반대(눌리면 광량↓=전압↓)이므로 `<` 비교로 수정.

### 8.3 한글 점자 매핑은 앱에서
6비트 셀 → 한글 점자(초성/중성/종성, 약자 660종) 매핑과 LLM 교정은 **앱(소프트웨어 팀)**이 담당. 하드웨어는 6비트 패턴만 정확히 보내면 됩니다.

---

## 9. 다음 단계 체크리스트 (조영진용)

- [ ] 방식 결정: B(FSR)로 PoC 먼저 → A(광섬유)로 차별성 (권장)
- [ ] 단일 센서 스캐닝 vs 6점 어레이 결정 (초기엔 스캐닝 권장)
- [ ] KiCad에서 메인 보드 스케매틱 작성 → ERC 검사
- [ ] PCB 레이아웃 → DRC 검사 → JLCPCB 발주
- [ ] Fusion 360 스크립트 실행 → 치수 조정 → STL → 3D 프린트
- [ ] ESP32 펌웨어로 ADC·BLE 동작 검증 (점자 카드로 테스트)
- [ ] 캘리브레이션·임계값 튜닝 → 셀 인식 정확도 80% 목표 측정

---

## 부록: 참고 출처 정리
- 한국 점자 규정·세부규격: [국립국어원 점자 종합정보](https://korean.go.kr/braille/search/search.do), [한국 점자 규정 해설(국립국어원)](https://www.korean.go.kr), [키오스크UI 점자 규격](https://www.kioskui.or.kr/index.do?menu_id=00001049)
- 국제 점자 표준: [ISO 17049:2013](https://cdn.standards.iteh.ai/samples/58086/fb6f17bed4ff425fa03583afabdafb97/ISO-17049-2013.pdf)
- FSR 압력센서: [Interlink FSR 400 Datasheet](https://cdn2.hubspot.net/hubfs/3899023/Interlinkelectronics%20November2017/Docs/Datasheet_FSR.pdf), [Adafruit FSR Integration Guide](https://cdn-learn.adafruit.com/assets/assets/000/010/126/original/fsrguide.pdf)
- 광섬유 굽힘 센서: [Macrobending POF sensor (ITS)](https://iptek.its.ac.id/index.php/jfa/article/download/20(2)06/pdf_99)
- TIA/포토다이오드: [TI OPT101 Datasheet](https://www.ti.com/lit/ds/symlink/opt101.pdf), [TI TIPD176](https://www.ti.com/tool/TIPD176), [RP Photonics 광다이오드 증폭기](https://www.rp-photonics.com/photodiode_amplifiers.html)
- TIA PCB 레이아웃: [PCBGOGO TIA 가이드](https://www.pcbgogo.com/Article/how-to-design-a-photodiode-transimpedance-amplifier.html)
- ESP32 ADC: [Espressif ESP32-S3 ADC docs](https://docs.espressif.com/projects/esp-idf/en/stable/esp32s3/api-reference/peripherals/adc/index.html), [DeepBlue ESP32 ADC](https://deepbluembedded.com/esp32-adc-tutorial-read-analog-voltage-arduino/)
- LiPo 충전: [Microchip MCP73831](https://www.ultralibrarian.com/2021/11/04/mcp73831-datasheet-a-linear-charge-management-controller-ulc/)

*본 문서는 설계 가이드이며, 실제 제작 전 각 부품의 최신 데이터시트를 다시 확인하시기 바랍니다. 리튬 배터리 취급 시 보호회로·발열·과충전에 각별히 유의하세요.*
