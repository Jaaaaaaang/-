"""
02_core_analysis.py — 안전·공정 핵심 분석 + KPI 산출 + 적용 전·후 시뮬레이션
출력: output/analysis_results.json, output/kpi_table.csv, output/*.csv (중간 집계)
"""
import pandas as pd, numpy as np, json, os
pd.set_option('display.width', 250)
XL = pd.ExcelFile('data/SCX_NEXT_Analysis_Tables_v1.4.3.xlsx')
os.makedirs('output', exist_ok=True)
R = {}  # 결과 저장
REF = pd.Timestamp('2026-10-31 17:00')
WORKDAYS = 23

# ---------- 로드 ----------
ms = XL.parse('01_master_schedule')
wp = XL.parse('02_daily_work_plan'); wp['Date'] = pd.to_datetime(wp.Date)
cam = XL.parse('04_camera_object_log'); cam['Date'] = pd.to_datetime(cam.Date); cam['hour'] = pd.to_datetime(cam.Slot_Start).dt.hour
dl = XL.parse('05_delivery_log'); dl['Date'] = pd.to_datetime(dl.Date)
for c in ['Reserved_Start','Reserved_End','Arrival_Time','Gate_In_Time','Unload_Start_Time','Unload_End_Time','Gate_Out_Time']:
    dl[c] = pd.to_datetime(dl[c], errors='coerce')
dl['hour'] = dl.Gate_In_Time.dt.hour
lf = XL.parse('06_lifting_log'); lf['Date'] = pd.to_datetime(lf.Date)
for c in ['Planned_Start','Planned_End','Actual_Start','Actual_End']: lf[c] = pd.to_datetime(lf[c])
eq = XL.parse('07_equipment_log')
ra = XL.parse('08_risk_assessment')
ins = XL.parse('09_inspection_action_log')
for c in ['Issue_DateTime','Due_DateTime','Closed_DateTime']: ins[c] = pd.to_datetime(ins[c])
nm = XL.parse('10_near_miss_reports'); nm['dt'] = pd.to_datetime(nm.Occurrence_DateTime); nm['hour'] = nm.dt.dt.hour
pm = XL.parse('11_work_permits')
tbm = XL.parse('12_tbm_log')
wx = XL.parse('13_weather_hourly')

# ---------- A. 구역별 위험 프로파일 (위험·간섭 지도 데이터) ----------
zone = pd.DataFrame(index=['A1','A2','A3','A4','B1','B2','B3','C1','C2','C3','D1','D2','D3'])
zone['near_miss'] = nm.groupby('Subzone').size()
zone['prox_alert'] = cam.groupby('Subzone').Proximity_Alert_Count.sum()
cam['eqp'] = cam.Forklift_Count + cam.Truck_Count + cam.Excavator_Count
cam['mix'] = (cam.People_Count >= 5) & (cam.eqp >= 1)          # 사람·장비 혼재 슬롯 (가정: 5명 이상 + 장비 1대 이상)
zone['mix_slots'] = cam.groupby('Subzone').mix.sum()
zone['people_avg'] = cam[cam.hour != 12].groupby('Subzone').People_Count.mean().round(1)
zone['crane_slots'] = cam.groupby('Subzone').Crane_Active.sum()
zone['insp_open'] = ins[ins.Status != 'Closed'].groupby('Subzone').size()
zone['insp_recur'] = ins[ins.Recurrence_Flag == 'Y'].groupby('Subzone').size()
zone['risk_max'] = ra.groupby('Subzone').Initial_Risk_Score.max()
zone['high_days'] = wp[wp.Risk_Level == 'High'].groupby('Subzone').size()
zone = zone.fillna(0)
# 종합 위험지수 (팀 정의): 각 지표를 0~1 정규화 후 가중합 — 가정 가중치
w = {'near_miss': .25, 'prox_alert': .15, 'mix_slots': .15, 'insp_open': .15, 'insp_recur': .10, 'risk_max': .10, 'high_days': .10}
norm = lambda s: (s - s.min()) / (s.max() - s.min()) if s.max() > s.min() else s * 0
zone['risk_index'] = sum(norm(zone[k]) * v for k, v in w.items()).round(3) * 100
zone = zone.sort_values('risk_index', ascending=False)
zone.to_csv('output/zone_risk_profile.csv', encoding='utf-8-sig')
R['zone_risk_profile'] = zone.round(1).to_dict(orient='index')
R['risk_index_weights'] = w
print(zone)

# ---------- B. 시간대별 위험도 (구역×시간) ----------
ht = cam[cam.hour != 12].pivot_table(index='hour', columns='Subzone', values='Proximity_Alert_Count', aggfunc='sum').fillna(0)
ht.to_csv('output/heat_hour_zone_alerts.csv')
hm = cam.pivot_table(index='hour', columns='Subzone', values='mix', aggfunc='sum').fillna(0)
hm.to_csv('output/heat_hour_zone_mix.csv')
hour_sum = pd.DataFrame({
    'prox_alert': cam.groupby('hour').Proximity_Alert_Count.sum(),
    'mix_slots': cam.groupby('hour').mix.sum(),
    'near_miss': nm.groupby('hour').size(),
    'deliveries': dl.groupby('hour').size(),
    'lifts': lf[lf.Status == '완료'].groupby(lf.Actual_Start.dt.hour).size(),
}).fillna(0).astype(int)
hour_sum.to_csv('output/hour_summary.csv')
R['hour_summary'] = hour_sum.to_dict(orient='index')
print(hour_sum)
# 요일
nm['dow'] = nm.dt.dt.dayofweek; cam['dow'] = cam.Date.dt.dayofweek
R['dow_alerts'] = cam.groupby('dow').Proximity_Alert_Count.sum().to_dict()
R['dow_nearmiss'] = nm.groupby('dow').size().to_dict()

# ---------- C. B구역 하역장 혼잡 — 반입 집중과 근접경보 연관 ----------
big = dl[dl.Delivery_Size_Class == '대형'].copy()
dd = big.groupby(['Date', 'hour']).size().rename('deliv').reset_index()
b2 = cam[cam.Subzone == 'B2'].merge(dd, on=['Date', 'hour'], how='left').fillna({'deliv': 0})
b2['busy'] = (b2.Forklift_Count + b2.Truck_Count) >= 2
R['B2_alert_by_deliv'] = b2.groupby('deliv').Proximity_Alert_Count.mean().round(2).to_dict()
R['B2_alert_busy_vs_not'] = b2.groupby('busy').Proximity_Alert_Count.agg(['size', 'sum', 'mean']).round(2).to_dict(orient='index')
# 반입 슬롯 동시성: 같은 시간대에 2대 이상 입문한 슬롯 수
slot = big.groupby(['Date', 'hour']).size()
R['delivery_slots_total'] = int(len(slot)); R['delivery_slots_multi'] = int((slot >= 2).sum()); R['delivery_slots_3plus'] = int((slot >= 3).sum())
big['wait_min'] = (big.Gate_In_Time - big.Arrival_Time).dt.total_seconds() / 60
big['unload_min'] = (big.Unload_End_Time - big.Unload_Start_Time).dt.total_seconds() / 60
big['dwell_min'] = (big.Gate_Out_Time - big.Gate_In_Time).dt.total_seconds() / 60
big['early_min'] = ((big.Reserved_Start - big.Arrival_Time).dt.total_seconds() / 60).clip(lower=0)
R['delivery_stats'] = {
    'n_big': int(len(big)), 'wait_mean': round(big.wait_min.mean(), 1), 'wait_max': int(big.wait_min.max()),
    'wait_total_min': int(big.wait_min.sum()), 'unload_mean': round(big.unload_min.mean(), 1), 'dwell_mean': round(big.dwell_min.mean(), 1),
    'early_arrivals_30min_plus': int((big.early_min >= 30).sum()), 'early_mean_min': round(big.early_min.mean(), 1),
    'gate_in_by_hour': big.groupby('hour').size().to_dict(),
    'window_violation_reserved': int(((~(((big.Reserved_Start.dt.hour >= 9) & (big.Reserved_Start.dt.hour < 11)) | ((big.Reserved_Start.dt.hour >= 14) & (big.Reserved_Start.dt.hour < 16))))).sum()),
}
# 하역장비별 하역 시간 & 하역장 점유 (동시 체류)
R['unload_by_equipment'] = big.groupby('Unloading_Equipment_ID').unload_min.agg(['count', 'mean']).round(1).to_dict(orient='index')
R['staging_subzone'] = big.Related_Staging_Subzone.value_counts().to_dict()
R['final_target'] = big.Final_Target_Subzone.value_counts().to_dict()

# 레미콘 연속타설 간격
rm = dl[dl.Material_Category == '레미콘'].sort_values('Gate_In_Time')
rmi = {}
for d, g in rm.groupby(rm.Date.dt.date):
    iv = g.Gate_In_Time.diff().dt.total_seconds().div(60).dropna()
    rmi[str(d)] = {'n': int(len(g)), 'interval_mean': round(iv.mean(), 1), 'min': int(iv.min()), 'max': int(iv.max()),
                   'out_of_12_15': int(((iv < 12) | (iv > 15)).sum()), 'b1_wait_mean': round((g.Gate_In_Time - g.Arrival_Time).dt.total_seconds().div(60).mean(), 1),
                   'first_in': g.Gate_In_Time.min().strftime('%H:%M'), 'last_in': g.Gate_In_Time.max().strftime('%H:%M')}
R['remicon'] = rmi
# 타설일 B1: 레미콘 + 일반자재 동시 입문 (ENV-005)
for d in rm.Date.unique():
    same = big[(big.Date == d)]
    R.setdefault('pour_day_general_deliveries', {})[str(pd.Timestamp(d).date())] = same.Gate_In_Time.dt.strftime('%H:%M').tolist()

# ---------- D. 양중 간섭 (TC-01 ↔ TC-02, C10) ----------
done = lf[lf.Status == '완료'].copy()
ov = []
for d, g in done.groupby('Date'):
    t1 = g[g.Equipment_ID == 'TC-01']; t2 = g[g.Equipment_ID == 'TC-02']
    for _, a in t1.iterrows():
        for _, b in t2.iterrows():
            s = max(a.Actual_Start, b.Actual_Start); e = min(a.Actual_End, b.Actual_End)
            if s < e: ov.append({'Date': str(d.date()), 'TC01': a.Lift_ID, 'TC02': b.Lift_ID, 'overlap_min': (e - s).total_seconds() / 60, 'start': s.strftime('%H:%M')})
ov = pd.DataFrame(ov); ov.to_csv('output/tc_overlap_pairs.csv', index=False)
R['tc_overlap'] = {'pairs': int(len(ov)), 'total_min': int(ov.overlap_min.sum()), 'days': int(ov.Date.nunique()), 'detail': ov.to_dict(orient='records')}
# 같은 날 TC-01·TC-02 모두 가동한 날 수
both_days = set(done[done.Equipment_ID == 'TC-01'].Date) & set(done[done.Equipment_ID == 'TC-02'].Date)
R['tc_both_active_days'] = len(both_days)
# 풍속 보류 손실
hold = lf[lf.Status != '완료']
hold_min = (hold.Planned_End - hold.Planned_Start).dt.total_seconds().div(60)
R['lift_hold'] = {'n_wind': int((hold.Hold_Reason == '풍속 기준 초과').sum()), 'n_delivery': int((hold.Hold_Reason == '연계 반입 하역 미완료').sum()),
                  'planned_min_lost': int(hold_min.sum()), 'days': sorted(hold.Date.dt.strftime('%Y-%m-%d').unique().tolist())}
# 양중 신호수 시야 아차사고 ↔ 점검 SIGNAL_VIEW 반복
R['signal_view_recurrence'] = int((ins.Finding_Code == 'SIGNAL_VIEW').sum())
# 장비 가동률
eqs = eq.groupby('Equipment_ID').agg(days=('Date', 'nunique'), op=('Operation_Minutes', 'sum'), wait=('Waiting_Minutes', 'sum'), mnt=('Maintenance_Minutes', 'sum'))
eqs['util_pct'] = (eqs.op / (eqs.op + eqs.wait + eqs.mnt) * 100).round(1)
eqs['wait_per_day'] = (eqs.wait / eqs.days).round(0)
R['equipment'] = eqs.to_dict(orient='index')
R['equipment_notes'] = eq.Notes.value_counts().to_dict()
eqs.to_csv('output/equipment_util.csv')

# ---------- E. 공정 편차 & 대기 ----------
ms_s = ms[['Task_ID', 'Subzone', 'Task_Name', 'Planned_Finish', 'Forecast_Finish', 'Forecast_Variance_Days', 'Delay_Reason_Code', 'Status_AsOf_2026_10_31', 'Progress_Pct']]
R['schedule'] = ms_s.astype(str).to_dict(orient='records')
R['schedule_variance_inprogress'] = int(ms[ms.Status_AsOf_2026_10_31 == 'In Progress'].Forecast_Variance_Days.sum())
R['schedule_variance_all'] = int(ms.Forecast_Variance_Days.sum())
R['delay_reason_counts'] = ms.Delay_Reason_Code.value_counts().to_dict()
R['delay_days_by_reason'] = ms.groupby('Delay_Reason_Code').Forecast_Variance_Days.sum().to_dict()
cw = wp[wp.Crew_Waiting_Minutes > 0]
R['crew_wait'] = {'total_min': int(wp.Crew_Waiting_Minutes.sum()), 'events': int(len(cw)),
                  'by_reason': cw.groupby('Daily_Remark').Crew_Waiting_Minutes.agg(['count', 'sum']).to_dict(orient='index'),
                  'by_subzone': cw.groupby('Subzone').Crew_Waiting_Minutes.sum().to_dict(),
                  'by_task': cw.groupby('Task_ID').Crew_Waiting_Minutes.sum().to_dict()}
# 인원·시간 환산 (가정: 대기 분 × 해당일 실투입 인원)
cw2 = cw.assign(mh=cw.Crew_Waiting_Minutes * cw.Actual_Workers / 60)
R['crew_wait_manhours'] = round(cw2.mh.sum(), 1)
R['crew_wait_manhours_by_reason'] = cw2.groupby('Daily_Remark').mh.sum().round(1).to_dict()

# ---------- F. 안전관리 프로세스 (허가·TBM·점검) ----------
pm['Date'] = pm.Date.astype(str); wpd = wp.assign(Date=wp.Date.dt.strftime('%Y-%m-%d'))
perm = {}
for t, pt in [('T016', '고소작업'), ('T010', '고소작업'), ('T014', '굴착·토공'), ('T013', '굴착·토공'), ('T018', '화기작업')]:
    days = set(wpd[wpd.Task_ID == t].Date); pdays = set(pm[(pm.Task_ID == t) & (pm.Permit_Type == pt)].Date)
    perm[f'{t}_{pt}'] = {'work_days': len(days), 'permit_days': len(pdays), 'missing': len(days - pdays)}
R['permit_gap'] = perm
R['permit_missing_total'] = sum(v['missing'] for v in perm.values())
tbm['Date'] = tbm.Date.astype(str)
m = tbm.merge(wpd[['Date', 'Task_ID', 'Actual_Workers']], on=['Date', 'Task_ID'])
m['gap'] = (m.Actual_Workers - m.Attendance_Count).clip(lower=0)
R['tbm'] = {'sessions': int(len(m)), 'sessions_with_absent': int((m.gap > 0).sum()), 'absent_mandays': int(m.gap.sum()),
            'by_subzone': m.groupby('Subzone').gap.sum().to_dict(), 'attend_rate_pct': round(m.Attendance_Count.sum() / m.Actual_Workers.sum() * 100, 1)}
ins['ttc_h'] = (ins.Closed_DateTime - ins.Issue_DateTime).dt.total_seconds() / 3600
ins['overdue'] = ((ins.Closed_DateTime.notna()) & (ins.Closed_DateTime > ins.Due_DateTime)) | ((ins.Closed_DateTime.isna()) & (ins.Due_DateTime < REF))
ins['age_h_open'] = np.where(ins.Closed_DateTime.isna(), (REF - ins.Issue_DateTime).dt.total_seconds() / 3600, np.nan)
R['inspection'] = {'n': int(len(ins)), 'closed': int((ins.Status == 'Closed').sum()), 'open': int((ins.Status != 'Closed').sum()),
                   'overdue': int(ins.overdue.sum()), 'recur': int((ins.Recurrence_Flag == 'Y').sum()),
                   'ttc_mean_h': round(ins.ttc_h.mean(), 1), 'ttc_median_h': round(ins.ttc_h.median(), 1),
                   'open_age_mean_h': round(np.nanmean(ins.age_h_open), 1),
                   'by_severity': ins.groupby('Severity').agg(n=('Inspection_ID', 'size'), closed=('Status', lambda s: int((s == 'Closed').sum())), overdue=('overdue', 'sum')).to_dict(orient='index'),
                   'top_codes': ins.Finding_Code.value_counts().head(8).to_dict(),
                   'by_subzone_open': ins[ins.Status != 'Closed'].groupby('Subzone').size().to_dict()}
R['near_miss_by_type'] = nm.Event_Type.value_counts().to_dict()
R['near_miss_by_status'] = nm.Action_Status.value_counts().to_dict()
R['near_miss_linked_delivery'] = int(nm.Related_Event_ID.astype(str).str.startswith('DL').sum())
R['near_miss_linked_lift'] = int(nm.Related_Event_ID.astype(str).str.startswith('LF').sum())

# ---------- G. 고위험 동시작업 (같은 날 같은 Zone 내 High 2건 이상 / 반경중첩구역) ----------
hi = wp[wp.Risk_Level == 'High']
co = hi.groupby(['Date', 'Zone']).size()
R['high_concurrent_zone_days'] = int((co >= 2).sum())
R['high_concurrent_by_zone'] = co[co >= 2].groupby(level=1).size().to_dict()
# 양중 + 하부작업: TC-01 양중일(A2 target) & A2 작업 High
lift_a2_days = set(done[(done.Equipment_ID == 'TC-01') & (done.Target_Subzone == 'A2')].Date.dt.strftime('%Y-%m-%d'))
a2_hi = set(hi[hi.Subzone == 'A2'].Date.dt.strftime('%Y-%m-%d'))
R['tc01_lift_over_A2_high_days'] = len(lift_a2_days & a2_hi)
# D1 램프: 10/13 이후 장비동선 전환 효과
d1 = cam[cam.Subzone == 'D1']
R['D1_alerts_before_1013'] = int(d1[d1.Date < '2026-10-13'].Proximity_Alert_Count.sum())
R['D1_alerts_after_1013'] = int(d1[d1.Date >= '2026-10-13'].Proximity_Alert_Count.sum())

# ---------- H. KPI 베이스라인 & 적용 후 시뮬레이션 ----------
# 시뮬레이션 가정(모두 '가정'으로 표기): 파일럿 3개 기능의 효과 계수
# F1 반입 슬롯 자동조정: 동일 슬롯 2대 이상 입문 → 1대로 분산(슬롯 용량 1대/30분), 조기도착 → 장외대기 안내
# F2 양중-동선 충돌 사전점검(TC 중첩 자동 탐지 + 일일양중계획 승인 게이트): 시간중첩 쌍 0, 풍속예보 기반 양중 재배치
# F3 안전조치 추적(허가·TBM·지적 자동알림): 허가 누락 0, 기한 내 조치율 향상
kpi = []
def K(name, base, after, unit, files, formula, assumption):
    kpi.append({'KPI': name, 'Before': base, 'After(가정)': after, 'Unit': unit, 'Files/Keys': files, 'Formula': formula, 'Assumption': assumption})

# KPI1 B구역 사람·장비 혼재 슬롯 (B1+B2)
mixB = int(cam[cam.Subzone.isin(['B1', 'B2'])].mix.sum())
# 가정: 복수 입문 슬롯(≥2대)을 분산하면 해당 슬롯의 혼재가 단일 입문 수준으로 → 혼재 슬롯 30% 감소 (슬롯 2대이상 비율 19/80 ≈ 24% + 조기도착 분산)
multi_share = R['delivery_slots_multi'] / R['delivery_slots_total']
K('B1·B2 사람·장비 혼재 슬롯 수', mixB, int(round(mixB * (1 - 0.30))), '슬롯(1h)/23일',
  '04_camera_object_log (Subzone, Slot_Start) ⟂ 05_delivery_log (Date, Gate_In_Time hour)',
  'People_Count≥5 & (Forklift+Truck+Excavator)≥1 인 슬롯 수', f'복수입문 슬롯 비율 {multi_share:.0%} → 슬롯 1대 제한 시 혼재 30% 감소(가정)')
# KPI2 근접경보 (B1+B2+A4+D1)
alertsB = int(cam[cam.Subzone.isin(['B1', 'B2'])].Proximity_Alert_Count.sum())
K('B1·B2 근접경보 건수(참고지표)', alertsB, int(round(alertsB * (1 - 0.40))), '건/23일',
  '04_camera_object_log.Proximity_Alert_Count', '합계', '경보 83건 중 100%가 장비≥2 슬롯에서 발생 → 장비 동시 2대 슬롯 40% 감소 가정')
# KPI3 반입차량 게이트 대기
K('대형자재 게이트 대기시간 합계', R['delivery_stats']['wait_total_min'], int(round(R['delivery_stats']['wait_total_min'] * 0.6)), '분/80대',
  '05_delivery_log: Gate_In_Time − Arrival_Time', 'Σ(Gate_In − Arrival), 대형 80건', '조기도착(≥30분) 차량 장외대기 안내 + 슬롯 재배정 → 대기 40% 감소 가정')
# KPI4 TC 반경중첩 동시선회
K('TC-01·TC-02 양중 시간중첩(C10 위반 후보)', R['tc_overlap']['pairs'], 0, '쌍(총 %d분)' % R['tc_overlap']['total_min'],
  '06_lifting_log: Equipment_ID, Actual_Start/End (같은 Date)', '시간구간 교집합>0인 TC-01×TC-02 쌍', '일일양중계획 자동 충돌검사 → 승인 전 시간 분리(0건 목표)')
# KPI5 고위험 동시작업
K('동일 대구역 High 작업 동시일(Zone-일)', R['high_concurrent_zone_days'], int(round(R['high_concurrent_zone_days'] * 0.7)), 'Zone·일',
  '02_daily_work_plan: Date, Zone, Risk_Level', '같은 Date·Zone에 Risk_Level=High ≥2건', '주간 Look-ahead 충돌검토로 30% 시차 분산 가정')
# KPI6 허가 미발행
K('작업허가 미발행 작업일', R['permit_missing_total'], 0, '일', '11_work_permits ⟂ 02_daily_work_plan (Date, Task_ID, Permit_Type)',
  '작업일 − 동일 Task·유형 허가일', 'T016 고소작업 대상 가정. TBM 입력 시 허가 자동 체크로 0건')
# KPI7 기한 내 미조치
K('안전점검 기한 내 미조치 건수', R['inspection']['overdue'], int(round(R['inspection']['overdue'] * 0.5)), '건/52',
  '09_inspection_action_log: Due_DateTime, Closed_DateTime', '(Closed>Due) or (미완료 & Due<10/31 17:00)', '기한 24h 전 자동알림 + 재발코드 에스컬레이션 → 50% 감소 가정')
# KPI8 TBM 미참석
K('TBM 미참석 인원(명·일)', R['tbm']['absent_mandays'], int(round(R['tbm']['absent_mandays'] * 0.5)), '명·일/23일',
  '12_tbm_log ⟂ 02_daily_work_plan (Date, Task_ID)', 'Σ max(Actual_Workers − Attendance_Count, 0)', '출역(03) 연동 미참석 자동식별 + 보충TBM → 50% 감소 가정')
# KPI9 작업대기
K('공종 작업대기 합계', R['crew_wait']['total_min'], int(round(R['crew_wait']['total_min'] * 0.65)), '분(%.0f 인·시)' % R['crew_wait_manhours'],
  '02_daily_work_plan.Crew_Waiting_Minutes', 'Σ Crew_Waiting_Minutes', '양중순서·자재반입 확인 대기(215분) 제거, 강풍 대기는 예보기반 재배치로 50% → 전체 35% 감소 가정')
# KPI10 공정편차
K('진행중 공정 예측편차 합계', R['schedule_variance_inprogress'], max(R['schedule_variance_inprogress'] - 3, 0), '작업일',
  '01_master_schedule: Forecast_Finish − Planned_Finish', 'Σ Forecast_Variance_Days (In Progress)', 'LIFT_SLOT·MAT_DELAY·SPACE_CONFLICT 연계 3일 회복 가정(추가 지연 0 목표)')
kpi_df = pd.DataFrame(kpi); kpi_df.to_csv('output/kpi_table.csv', index=False, encoding='utf-8-sig')
R['kpi'] = kpi
print(kpi_df[['KPI', 'Before', 'After(가정)', 'Unit']])

def conv(o):
    if isinstance(o, (np.integer,)): return int(o)
    if isinstance(o, (np.floating,)): return float(o)
    if isinstance(o, (pd.Timestamp,)): return str(o)
    if isinstance(o, dict): return {str(k): conv(v) for k, v in o.items()}
    if isinstance(o, (list, tuple)): return [conv(v) for v in o]
    return o
json.dump(conv(R), open('output/analysis_results.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('saved output/analysis_results.json')
