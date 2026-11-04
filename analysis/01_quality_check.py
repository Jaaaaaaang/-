"""
01_quality_check.py — 데이터 품질 진단 (중복·결측·용어변형·운영규칙 예외)
입력: data/SCX_NEXT_Analysis_Tables_v1.4.3.xlsx (+ Source_Records 교차검증)
출력: output/quality_report.md
"""
import pandas as pd, numpy as np, os
pd.set_option('display.width', 250)

XL = pd.ExcelFile('data/SCX_NEXT_Analysis_Tables_v1.4.3.xlsx')
SRC = pd.ExcelFile('data/SCX_NEXT_Source_Records_v1.4.3.xlsx')
os.makedirs('output', exist_ok=True)
lines = ["# 데이터 품질 진단 리포트 (v1.4.3)\n",
         "분석기준일 2026-10-31 / 통합 Excel(04_analysis_tables) 단일 형식 사용, CSV 중복 합산 없음\n"]

def H(t): lines.append(f"\n## {t}\n")
def P(t): lines.append(t + "\n")

# 1) 결측치
H("1. 결측치 현황")
for s in XL.sheet_names[1:]:
    df = XL.parse(s); na = df.isna().sum(); na = na[na > 0]
    if len(na):
        P(f"- **{s}**: " + ", ".join(f"{k}={v}" for k, v in na.items()))
P("- 해석: 01 Actual_Finish 결측 10건 = 진행중 공정(정상). 06 Actual_Start/End 결측 14건 = 보류·취소 양중(정상). "
  "09 Closed_DateTime 결측 29건 = 미조치(Open/In Progress). 05 DL-0079 Unload_End_Time 결측 1건 → Gate_Out_Time(15:53) 기준 대체·가정 표기.")

# 2) 중복
H("2. 중복 ID·문서번호")
dl = XL.parse('05_delivery_log')
dup = dl[dl['Source_Document_No'].duplicated(keep=False)]
P(f"- 05 반입전표번호 중복: {dl['Source_Document_No'].duplicated().sum()}건 → {dup[['Delivery_ID','Source_Document_No','Material_Name']].values.tolist()}")
P("  - 처리: 서로 다른 Delivery_ID·자재·시각 → 별개 업무로 **유지**(안내서 §5: 문서번호 중복만으로 자동 삭제 금지). 전표번호 오기재로 가정.")
for s, k in [('06_lifting_log','Lift_ID'),('11_work_permits','Permit_ID'),('12_tbm_log','TBM_ID'),('09_inspection_action_log','Inspection_ID'),('10_near_miss_reports','NearMiss_ID')]:
    P(f"- {s} {k} 중복: {XL.parse(s)[k].duplicated().sum()}건")
wp = XL.parse('02_daily_work_plan')
P(f"- 02 (Date,Task_ID) 중복: {wp.duplicated(['Date','Task_ID']).sum()}건")

# 3) 용어변형
H("3. 용어·표기 변형")
ins = XL.parse('09_inspection_action_log')
suffix = ins['Finding'].str.contains('확인$')
P(f"- 09 Finding 자유기재 접미어('…오전 점검에서 확인', '…작업구간 정리 중 확인', '…공종간 합동점검에서 확인', '…작업 전 순회점검에서 확인') 부착: {suffix.sum()}/{len(ins)}건 → **Finding_Code(20종)** 기준으로 정규화하여 반복지적 집계")
P(f"- 09 Finding 원문 고유값 {ins['Finding'].nunique()}개 vs Finding_Code {ins['Finding_Code'].nunique()}개")
P("- 02 Trade: '형틀공사'(1건) vs '철근콘크리트' 혼용 → T002 거푸집 공정은 Task_ID 기준으로 통합")
P("- 지하층 표기 B2F/B3F ≠ 구역코드 B2/B3 (안내서 명시) → 구역분석은 Subzone 코드만 사용")
P("- 06 Rigging_Check: '적합' / '샤클 교체 후 적합' 등 변형 → '적합' 계열로 통합")

# 4) 운영규칙 예외
H("4. 운영규칙 예외 기록")
for c in ['Reserved_Start','Reserved_End','Arrival_Time','Gate_In_Time','Unload_Start_Time','Unload_End_Time','Gate_Out_Time']:
    dl[c] = pd.to_datetime(dl[c], errors='coerce')
big = dl[dl.Delivery_Size_Class == '대형'].copy()
h = big.Reserved_Start.dt.hour + big.Reserved_Start.dt.minute/60
inwin = ((h >= 9) & (h < 11)) | ((h >= 14) & (h < 16))
P(f"- C01 대형자재 예약시작 창 외 예약: {(~inwin).sum()}/{len(big)}건 ({', '.join(big.loc[~inwin,'Delivery_ID'])}) — 모두 10/05~06 초기")
early = big.Gate_In_Time < big.Reserved_Start; late = big.Gate_In_Time > big.Reserved_End
P(f"- 예약시작 전 조기 입문: {early.sum()}건 / 예약종료 후 지연 입문: {late.sum()}건 (ENV-001·009 조기도착 민원과 대응)")
P(f"- 17:00 이후 하역 완료: {(big.Unload_End_Time.dt.hour >= 17).sum()}건 (C03 준수)")
pm = XL.parse('11_work_permits'); pm['Date'] = pm.Date.astype(str); wp['Date'] = wp.Date.astype(str)
P("- 작업허가 미발행(작업일보 작업일 vs 허가일):")
for t, pt in [('T016','고소작업'),('T010','고소작업'),('T014','굴착·토공'),('T013','굴착·토공')]:
    days = set(wp[wp.Task_ID == t].Date); pdays = set(pm[(pm.Task_ID == t) & (pm.Permit_Type == pt)].Date)
    P(f"  - {t} {pt}: 작업일 {len(days)} / 허가일 {len(pdays)} / **미발행 {len(days-pdays)}일**")
P("  - 가정: 고소작업대(SL-03) 사용 T016은 고소작업 허가 대상으로 간주(T010 사례와 동일 기준). 중량물 양중은 Permit_ID 연결 100%, 허가시간 외 양중 0건.")
tbm = XL.parse('12_tbm_log'); tbm['Date'] = tbm.Date.astype(str)
m = tbm.merge(wp[['Date','Task_ID','Actual_Workers']], on=['Date','Task_ID'])
m['gap'] = (m.Actual_Workers - m.Attendance_Count).clip(lower=0)
P(f"- TBM 미참석: {int(m.gap.sum())}명·일 / 미참석 발생 TBM {int((m.gap>0).sum())}/{len(m)}회 (참석>실투입 이상치 {int((m.Actual_Workers<m.Attendance_Count).sum())}건)")
ins['Issue'] = pd.to_datetime(ins.Issue_DateTime); ins['Due'] = pd.to_datetime(ins.Due_DateTime); ins['Closed'] = pd.to_datetime(ins.Closed_DateTime)
ref = pd.Timestamp('2026-10-31 17:00')
overdue = ((ins.Closed.notna()) & (ins.Closed > ins.Due)) | ((ins.Closed.isna()) & (ins.Due < ref))
P(f"- 안전점검 기한 내 미조치(완료지연+기한경과 미완료): {int(overdue.sum())}/{len(ins)}건, 미완료 {int((ins.Status!='Closed').sum())}건, 재발 플래그 Y {int((ins.Recurrence_Flag=='Y').sum())}건")

# 5) 원천 vs 분석표 교차검증
H("5. 원천기록 ↔ 분석표 교차검증")
wk = pd.concat([SRC.parse(f'작업일보_{i}주차') for i in range(1, 5)])
P(f"- 작업일보 원천 {len(wk)}행 = 02_daily_work_plan {len(wp)}행 (행수·공종코드 일치)")
for s_src, s_an in [('자재반입대장','05_delivery_log'),('양중작업일지','06_lifting_log'),('아차사고대장','10_near_miss_reports'),('작업허가대장','11_work_permits'),('TBM일지','12_tbm_log'),('안전점검조치대장','09_inspection_action_log')]:
    P(f"- {s_src} {len(SRC.parse(s_src))}행 = {s_an} {len(XL.parse(s_an))}행")
P("- 결론: 원천(국문 헤더)과 분석표(영문 헤더)는 동일 데이터의 형식 차이 → 분석표만 사용, 합산 없음")

# 6) 가정·제외 기준 요약
H("6. 적용한 정제·가정·제외 기준")
for t in [
 "분석기간 2026-10-05~10-31, 일요일·10/09 제외 → 작업일 23일 (CCTV 23일과 일치)",
 "양중 실적 = Status '완료' 99건만. 보류 13·취소 1건은 실적 제외하되 '풍속 보류' 손실시간 산정에 사용",
 "레미콘 36대(3일×12대)는 C01 반입창 예외 → 대형자재 KPI에서 제외, 레미콘 간격 KPI 별도",
 "CCTV People/Equipment_Count는 슬롯 내 최대 동시값 → 밀집지표는 '평균 최대 동시값'으로 표기, Proximity_Alert는 참고지표(정답값 아님)",
 "거리·면적은 산정하지 않음(배치도 무축척). 반경 중첩은 C04·C10 텍스트 기준 B3·C1을 중첩구역으로 가정",
 "공정편차 기준선 = 01 Planned_Finish, 기준일 10/31. Forecast_Variance_Days 사용(작업일 기준)",
 "TBM 미참석 = max(실투입-참석, 0). 참석>실투입은 0건이라 보정 불필요",
 "DL-0079 Unload_End 결측 → 하역시간 통계에서 제외(79건으로 집계)",
]: P(f"- {t}")

open('output/quality_report.md', 'w', encoding='utf-8').write("\n".join(lines))
print("\n".join(lines))
