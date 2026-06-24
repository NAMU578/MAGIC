# -*- coding: utf-8 -*-
"""
Fusion 360 파라메트릭 생성 스크립트
점자 인식 웨어러블 기기 ("손끝에서 귀로") — 하드웨어 하우징

생성 부품:
  1) 손끝 센서 캡 (thimble) — 검지에 끼우는 골무형, 바닥에 센서 윈도우
  2) 메인 보드 인클로저 하부 — ESP32 + 배터리 + PCB 수납 박스
  3) 메인 보드 인클로저 상부 뚜껑

사용법:
  Fusion 360 → Utilities → ADD-INS → Scripts and Add-Ins
  → "+" 로 이 .py 파일을 추가 → Run
  치수를 바꾸려면 아래 PARAMS 딕셔너리 값만 수정하세요.
  (모든 단위: cm — Fusion 360 API 내부 길이 단위는 cm 입니다. 1mm = 0.1cm)

작성: 의공학마법사 팀 하드웨어 설계 참고용
"""

import adsk.core
import adsk.fusion
import traceback

# ─────────────────────────────────────────────────────────────
# 파라미터 (단위: mm 로 적고 내부에서 cm 로 변환)
# 점자/부품 근거값은 동봉 설계 문서 참고
# ─────────────────────────────────────────────────────────────
P = {
    # 손끝 캡
    "finger_dia":      17.0,   # 검지 직경 (성인 약 16~18mm)
    "cap_wall":         1.8,   # 캡 벽 두께
    "cap_len":         22.0,   # 캡 길이(손끝에서 첫마디까지)
    "sensor_win_dia":  13.0,   # 센서 윈도우 직경 (FSR402 활성면 12.7mm 이상)

    # 메인 박스 (손등/손목)
    "box_inner_w":     30.0,   # 내부 폭  (PCB 25 + 여유)
    "box_inner_l":     40.0,   # 내부 길이(PCB 35 + 여유)
    "box_inner_h":     12.0,   # 내부 높이(PCB + 배터리 적층)
    "box_wall":         2.0,   # 박스 벽 두께
    "lid_h":            3.0,   # 뚜껑 높이
    "post_dia":         4.0,   # PCB 나사 보스 외경
    "post_hole_dia":    1.8,   # M2 나사 하공 직경
    "cable_hole_dia":   3.0,   # 캡-박스 연결 케이블 구멍

    # 배치 간격 (부품들이 겹치지 않게 X축으로 분리)
    "gap":             20.0,
}


def mm(v):
    """mm → cm (Fusion 360 내부 단위)"""
    return v / 10.0


def run(context):
    ui = None
    try:
        app = adsk.core.Application.get()
        ui = app.userInterface
        design = app.activeProduct
        if not isinstance(design, adsk.fusion.Design):
            ui.messageBox("활성 디자인이 없습니다. 새 디자인을 연 뒤 실행하세요.")
            return
        root = design.rootComponent

        # 부품별로 위치를 분리하기 위한 X 오프셋
        x_cursor = 0.0

        # 1) 손끝 센서 캡
        cap_w = P["finger_dia"] + 2 * P["cap_wall"]
        _create_finger_cap(root, x_cursor)
        x_cursor += cap_w + P["gap"]

        # 2) 메인 박스 하부
        box_w = P["box_inner_w"] + 2 * P["box_wall"]
        _create_main_box(root, x_cursor)
        x_cursor += box_w + P["gap"]

        # 3) 메인 박스 상부 뚜껑
        _create_lid(root, x_cursor)

        ui.messageBox(
            "생성 완료!\n\n"
            "· 손끝 센서 캡\n"
            "· 메인 박스 하부\n"
            "· 메인 박스 상부 뚜껑\n\n"
            "치수를 바꾸려면 스크립트 상단 P 딕셔너리를 수정 후 재실행하세요.\n"
            "STL 내보내기: 우클릭 Body → Save As Mesh."
        )

    except:
        if ui:
            ui.messageBox("실패:\n{}".format(traceback.format_exc()))


# ─────────────────────────────────────────────────────────────
# 1) 손끝 센서 캡 (골무형)
# ─────────────────────────────────────────────────────────────
def _create_finger_cap(root, x0):
    extrudes = root.features.extrudeFeatures
    sketches = root.sketches
    xy = root.xYConstructionPlane

    outer_r = mm(P["finger_dia"] / 2 + P["cap_wall"])
    inner_r = mm(P["finger_dia"] / 2)
    length = mm(P["cap_len"])
    cx = mm(x0 + P["finger_dia"] / 2 + P["cap_wall"])

    # 바깥 원기둥
    sk = sketches.add(xy)
    sk.sketchCurves.sketchCircles.addByCenterRadius(
        adsk.core.Point3D.create(cx, 0, 0), outer_r)
    prof = sk.profiles.item(0)
    ext = extrudes.addSimple(
        prof, adsk.core.ValueInput.createByReal(length),
        adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
    cap_body = ext.bodies.item(0)
    cap_body.name = "FingerCap"

    # 내부 비우기 (윗면에서 손가락이 들어가도록 — 끝은 막힘)
    sk2 = sketches.add(xy)
    sk2.sketchCurves.sketchCircles.addByCenterRadius(
        adsk.core.Point3D.create(cx, 0, 0), inner_r)
    prof2 = sk2.profiles.item(0)
    # 손가락 삽입 깊이 = 전체 길이 - 바닥 두께(cap_wall)
    cut_depth = mm(P["cap_len"] - P["cap_wall"])
    cut_in = adsk.core.ValueInput.createByReal(cut_depth)
    cut_ext = extrudes.addSimple(
        prof2, cut_in, adsk.fusion.FeatureOperations.CutFeatureOperation)

    # 바닥(손끝 접촉면)에 센서 윈도우 컷 — 박스 끝면에 구멍
    # 끝면은 z=0 평면 근처(바닥). 여기서는 바닥에서 센서 윈도우를 관통.
    sk3 = sketches.add(xy)
    sk3.sketchCurves.sketchCircles.addByCenterRadius(
        adsk.core.Point3D.create(cx, 0, 0), mm(P["sensor_win_dia"] / 2))
    prof3 = sk3.profiles.item(0)
    win_cut = adsk.core.ValueInput.createByReal(mm(P["cap_wall"]))
    extrudes.addSimple(
        prof3, win_cut, adsk.fusion.FeatureOperations.CutFeatureOperation)


# ─────────────────────────────────────────────────────────────
# 2) 메인 박스 하부 (PCB+배터리 수납)
# ─────────────────────────────────────────────────────────────
def _create_main_box(root, x0):
    extrudes = root.features.extrudeFeatures
    sketches = root.sketches
    xy = root.xYConstructionPlane

    w = P["box_inner_w"] + 2 * P["box_wall"]
    l = P["box_inner_l"] + 2 * P["box_wall"]
    h = P["box_inner_h"] + P["box_wall"]   # 바닥 두께 포함

    x_min = x0
    y_min = -l / 2

    # 바깥 박스
    sk = sketches.add(xy)
    lines = sk.sketchCurves.sketchLines
    lines.addTwoPointRectangle(
        adsk.core.Point3D.create(mm(x_min), mm(y_min), 0),
        adsk.core.Point3D.create(mm(x_min + w), mm(y_min + l), 0))
    prof = sk.profiles.item(0)
    ext = extrudes.addSimple(
        prof, adsk.core.ValueInput.createByReal(mm(h)),
        adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
    box_body = ext.bodies.item(0)
    box_body.name = "MainBox_Bottom"

    # 내부 비우기 (윗면 개방)
    sk2 = sketches.add(xy)
    ix = x_min + P["box_wall"]
    iy = y_min + P["box_wall"]
    sk2.sketchCurves.sketchLines.addTwoPointRectangle(
        adsk.core.Point3D.create(mm(ix), mm(iy), 0),
        adsk.core.Point3D.create(mm(ix + P["box_inner_w"]), mm(iy + P["box_inner_l"]), 0))
    prof2 = sk2.profiles.item(0)
    cut_depth = mm(P["box_inner_h"])   # 바닥은 남기고 위만 파냄 (z=0에서 시작)
    # z=0 평면에서 양수 방향으로 파내면 바닥이 안 남으므로,
    # 바닥을 남기려면 z=box_wall 높이에서 파야 함 → offset plane 사용
    offset_plane = _offset_plane(root, mm(P["box_wall"]))
    sk2b = sketches.add(offset_plane)
    sk2b.sketchCurves.sketchLines.addTwoPointRectangle(
        adsk.core.Point3D.create(mm(ix), mm(iy), 0),
        adsk.core.Point3D.create(mm(ix + P["box_inner_w"]), mm(iy + P["box_inner_l"]), 0))
    prof2b = sk2b.profiles.item(0)
    extrudes.addSimple(
        prof2b, adsk.core.ValueInput.createByReal(mm(P["box_inner_h"])),
        adsk.fusion.FeatureOperations.CutFeatureOperation)

    # PCB 나사 보스 4개 (모서리)
    margin = 4.0
    posts = [
        (ix + margin,                    iy + margin),
        (ix + P["box_inner_w"] - margin, iy + margin),
        (ix + margin,                    iy + P["box_inner_l"] - margin),
        (ix + P["box_inner_w"] - margin, iy + P["box_inner_l"] - margin),
    ]
    base_plane = _offset_plane(root, mm(P["box_wall"]))
    for (px, py) in posts:
        skp = sketches.add(base_plane)
        skp.sketchCurves.sketchCircles.addByCenterRadius(
            adsk.core.Point3D.create(mm(px), mm(py), 0), mm(P["post_dia"] / 2))
        profp = skp.profiles.item(0)
        extrudes.addSimple(
            profp, adsk.core.ValueInput.createByReal(mm(P["box_inner_h"] - 2)),
            adsk.fusion.FeatureOperations.JoinFeatureOperation)

    # 케이블 구멍 (앞면, 센서 캡 방향)
    yz = root.yZConstructionPlane
    skc = sketches.add(yz)
    skc.sketchCurves.sketchCircles.addByCenterRadius(
        adsk.core.Point3D.create(0, mm(h / 2), mm(-(x_min + 1))),
        mm(P["cable_hole_dia"] / 2))
    # (케이블 구멍은 위치 보정이 필요할 수 있으므로 수동 조정 권장 주석)


def _create_lid(root, x0):
    extrudes = root.features.extrudeFeatures
    sketches = root.sketches
    xy = root.xYConstructionPlane

    w = P["box_inner_w"] + 2 * P["box_wall"]
    l = P["box_inner_l"] + 2 * P["box_wall"]
    x_min = x0
    y_min = -l / 2

    sk = sketches.add(xy)
    sk.sketchCurves.sketchLines.addTwoPointRectangle(
        adsk.core.Point3D.create(mm(x_min), mm(y_min), 0),
        adsk.core.Point3D.create(mm(x_min + w), mm(y_min + l), 0))
    prof = sk.profiles.item(0)
    ext = extrudes.addSimple(
        prof, adsk.core.ValueInput.createByReal(mm(P["lid_h"])),
        adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
    ext.bodies.item(0).name = "MainBox_Lid"


# ─────────────────────────────────────────────────────────────
# 유틸: z 방향 오프셋 평면 생성
# ─────────────────────────────────────────────────────────────
def _offset_plane(root, offset_cm):
    planes = root.constructionPlanes
    inp = planes.createInput()
    inp.setByOffset(
        root.xYConstructionPlane,
        adsk.core.ValueInput.createByReal(offset_cm))
    return planes.add(inp)
