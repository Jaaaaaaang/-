"""
03_visuals.py — 과제안내서 필수 시각자료 6종 생성
 1 현장 위험·간섭 지도            output/fig1_risk_map.png
 2 시간대별 위험도·밀집도 차트     output/fig2_hourly_risk.png
 3 원인·결과 구조도               output/fig3_cause_effect.png
 4 해결안 시스템 구성도           output/fig4_system_architecture.png
 5 적용 전·후 비교표              output/fig5_before_after.png
 6 90일 실행 로드맵               output/fig6_roadmap_90d.png
 + 보조: 공정편차·대기 원인, 반입 슬롯 집중, 점검 조치 현황
"""
import pandas as pd, numpy as np, json, os
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Rectangle, Circle
import matplotlib.font_manager as fm

FONT = '/usr/share/fonts/truetype/nanum/NanumGothic.ttf'
fm.fontManager.addfont(FONT); fm.fontManager.addfont('/usr/share/fonts/truetype/nanum/NanumGothicBold.ttf')
plt.rcParams['font.family'] = 'NanumGothic'; plt.rcParams['axes.unicode_minus'] = False
os.makedirs('output', exist_ok=True)
R = json.load(open('output/analysis_results.json', encoding='utf-8'))
zone = pd.read_csv('output/zone_risk_profile.csv', index_col=0)
XL = pd.ExcelFile('data/SCX_NEXT_Analysis_Tables_v1.4.3.xlsx')
NAVY, RED, ORG, YEL, GRN, BLU, GRY = '#1F3A5F', '#C0392B', '#E67E22', '#F1C40F', '#27AE60', '#2E86C1', '#7F8C8D'

# ============ FIG 1. 현장 위험·간섭 지도 (배치도 개념 + 위험지수 히트) ============
fig, ax = plt.subplots(figsize=(14, 9.5)); ax.set_xlim(0, 100); ax.set_ylim(-2.5, 72); ax.axis('off')
layout = {  # (x, y, w, h) 개념 배치 (무축척)
    'A3': (6, 44, 16, 10), 'A4': (24, 44, 18, 10), 'B2': (44, 44, 16, 10), 'B3': (62, 44, 18, 10),
    'A1': (6, 20, 16, 22), 'A2': (24, 20, 18, 22), 'C1': (44, 20, 16, 22), 'C2': (62, 20, 18, 22), 'C3': (84, 20, 12, 22),
    'D1': (44, 4, 13, 10), 'D2': (59, 4, 13, 10), 'D3': (74, 4, 13, 10), 'B1': (44, 58, 16, 7)}
names = {'A1': '1동 코어·벽체', 'A2': '슬래브·타설 작업면', 'A3': '양중·호이스트', 'A4': '펌프카·레미콘', 'B1': '메인게이트', 'B2': '일반자재 하역장',
         'B3': '자재 적치장', 'C1': '포디움 외장', 'C2': '커튼월·TC-02', 'C3': '이동식크레인', 'D1': '지하램프', 'D2': 'B2F 설비', 'D3': 'B3F 토목·방수'}
cmap = plt.cm.YlOrRd; vmax = zone.risk_index.max()
for z, (x, y, w, h) in layout.items():
    ri = zone.loc[z, 'risk_index']; col = cmap(0.15 + 0.85 * ri / vmax)
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle='round,pad=0.3', fc=col, ec=NAVY, lw=1.5))
    ax.text(x + w / 2, y + h - 2.2, f'{z}  {names[z]}', ha='center', va='top', fontsize=10, weight='bold', color=NAVY)
    ax.text(x + w / 2, y + h / 2 - 1, f'위험지수 {ri:.0f}', ha='center', fontsize=11, weight='bold', color='#222')
    sub = f"아차 {int(zone.loc[z,'near_miss'])} · 경보 {int(zone.loc[z,'prox_alert'])}\n혼재슬롯 {int(zone.loc[z,'mix_slots'])} · 미조치 {int(zone.loc[z,'insp_open'])}"
    ax.text(x + w / 2, y + 1.2, sub, ha='center', va='bottom', fontsize=8, color='#333')
# 외부 보행통로 & 도로
ax.add_patch(Rectangle((2, 66.5), 96, 4, fc='#D5F5E3', ec=GRN)); ax.text(50, 68.5, '북측 도시도로 / 외부 보호보행통로 (상시 개방, C05 · TC 선회 금지 C04)', ha='center', va='center', fontsize=9, color='#145A32')
# TC 반경 (개념)
ax.add_patch(Circle((33, 42), 28, fill=False, ec=RED, lw=2, ls='--')); ax.text(33, 42 + 28 + 1, 'TC-01 반경(개념, C04)', color=RED, fontsize=9, ha='center')
ax.add_patch(Circle((70, 31), 20, fill=False, ec='#8E44AD', lw=2, ls='--')); ax.text(91, 44, 'TC-02 반경\n(개념, C10)', color='#8E44AD', fontsize=9, ha='center', va='center', bbox=dict(fc='white', ec='none', alpha=.9))
ax.text(53, 36, '중첩\nB3·C1\n(C10)', ha='center', fontsize=9, color='#8E44AD', weight='bold', bbox=dict(fc='white', ec='#8E44AD', alpha=.9))
# 동선 화살표
def arr(p, q, c, lbl=None, ls='-', off=(0, 0.8), ha='center'):
    ax.add_patch(FancyArrowPatch(p, q, arrowstyle='-|>', mutation_scale=18, color=c, lw=2.2, ls=ls))
    if lbl: ax.text((p[0] + q[0]) / 2 + off[0], (p[1] + q[1]) / 2 + off[1], lbl, fontsize=8, color=c, ha=ha, weight='bold', bbox=dict(fc='white', ec='none', alpha=.85, pad=1))
arr((46, 58), (34, 54.5), RED, '① 레미콘 B1→A4 (12대×3일, C09)', off=(-4, 1.2))
arr((54, 58), (54, 54.5), BLU, '② 일반자재→B2', off=(5.5, 0))
arr((44, 49), (22, 49), BLU, '③ 하역 후 A3 양중거점', '--')
arr((60, 61), (82, 61), GRN); arr((82, 61), (82, 55), GRN); arr((82, 44), (82, 15), GRN); arr((82, 2.5), (57, 2.5), GRN, '④ 장비·설비자재 B3 동측→D1 (10/13~, C07)', off=(0, -0.3))
ax.add_patch(FancyArrowPatch((82, 15), (82, 2.5), arrowstyle='-', color=GRN, lw=2.2))
# 핫스팟 마커
for z, lbl in [('B2', '★ 하역장 혼재·경보 최다'), ('D2', '★ 미조치·재발·TBM누락 최다'), ('A2', '★ High작업·양중하부'), ('A4', '★ 타설일 교행 3건'), ('C1', '★ TC 중첩·시야제한')]:
    x, y, w, h = layout[z]; ax.text(x + w / 2, y + h + 0.5, lbl, ha='center', va='bottom', fontsize=7.5, color=RED, weight='bold', bbox=dict(fc='white', ec=RED, lw=.8, alpha=.95))
sm = plt.cm.ScalarMappable(cmap=cmap, norm=plt.Normalize(0, vmax)); cb = plt.colorbar(sm, ax=ax, fraction=0.025, pad=0.01); cb.set_label('구역 종합 위험지수(팀 정의, 0~100)', fontsize=9)
ax.set_title('현장 위험·간섭 지도 — 13개 세부구역 종합 위험지수 (2026.10.05~10.31, 23작업일)', fontsize=14, weight='bold', color=NAVY, pad=12)
ax.text(2, -0.5, '※ 배치도는 무축척 개념도. 위험지수 = 아차사고25%·근접경보15%·사람장비 혼재슬롯15%·미조치지적15%·재발지적10%·위험성평가 최대점10%·High작업일10% (정규화 가중합, 팀 가정)\n'
        '   자료: 04_camera_object_log, 10_near_miss_reports, 09_inspection_action_log, 08_risk_assessment, 02_daily_work_plan, 15_site_constraints', fontsize=8, color=GRY)
plt.tight_layout(); plt.savefig('output/fig1_risk_map.png', dpi=160); plt.close()

# ============ FIG 2. 시간대별 위험도·밀집도 ============
hs = pd.DataFrame(R['hour_summary']).T; hs.index = hs.index.astype(float).astype(int)
ht = pd.read_csv('output/heat_hour_zone_alerts.csv', index_col=0); hm = pd.read_csv('output/heat_hour_zone_mix.csv', index_col=0)
fig = plt.figure(figsize=(15, 9)); gs = fig.add_gridspec(2, 2, height_ratios=[1, 1.1])
ax1 = fig.add_subplot(gs[0, :]); x = np.arange(len(hs)); wdt = .18
ax1.bar(x - 1.5 * wdt, hs.prox_alert, wdt, label='근접경보(CCTV, 참고)', color=RED)
ax1.bar(x - .5 * wdt, hs.mix_slots, wdt, label='사람·장비 혼재 슬롯', color=ORG)
ax1.bar(x + .5 * wdt, hs.deliveries, wdt, label='차량 입문(대)', color=BLU)
ax1.bar(x + 1.5 * wdt, hs.lifts, wdt, label='양중 실적(건)', color=GRN)
ax1b = ax1.twinx(); ax1b.plot(x, hs.near_miss, 'o-', color=NAVY, lw=2, label='아차사고(건)'); ax1b.set_ylim(0, 8); ax1b.set_ylabel('아차사고 건수')
ax1.set_xticks(x); ax1.set_xticklabels([f'{h:02d}:00' for h in hs.index]); ax1.set_ylabel('건·슬롯·대'); ax1.set_title('시간대별 위험·밀집 프로파일 (23작업일 합계)', weight='bold', color=NAVY)
ax1.set_ylim(0, 92)
bb = dict(fc='white', ec='none', alpha=.85, pad=1.5)
ax1.axvspan(1.5, 3.5, color=YEL, alpha=.15); ax1.text(2.5, 84, '피크① 09~11시\n반입창+양중+TBM 직후', ha='center', fontsize=9, color='#7D6608', bbox=bb)
ax1.axvspan(6.5, 8.5, color=YEL, alpha=.15); ax1.text(7.5, 84, '피크② 14~16시\n오후 반입창+양중 재개', ha='center', fontsize=9, color='#7D6608', bbox=bb)
ax1.axvspan(5.5, 6.5, color=GRN, alpha=.12); ax1.text(5.7, 62, '13시 양중 집중\n(38건, 점심 직후)', ha='center', fontsize=9, color='#145A32', bbox=bb)
ax1.text(5.0, 84, '12시 점심\n양중 미실시', ha='center', fontsize=8.5, color=GRY, bbox=bb)
h1, l1 = ax1.get_legend_handles_labels(); h2, l2 = ax1b.get_legend_handles_labels(); ax1.legend(h1 + h2, l1 + l2, loc='upper left', fontsize=8, ncol=1, framealpha=.95)
ax2 = fig.add_subplot(gs[1, 0]); im = ax2.imshow(ht.T.values, cmap='Reds', aspect='auto'); ax2.set_xticks(range(len(ht.index))); ax2.set_xticklabels([f'{int(h)}' for h in ht.index]); ax2.set_yticks(range(len(ht.columns))); ax2.set_yticklabels(ht.columns)
ax2.set_title('구역×시간 근접경보 합계', weight='bold'); ax2.set_xlabel('시각(시)')
for i in range(ht.shape[0]):
    for j in range(ht.shape[1]):
        v = int(ht.iloc[i, j]);
        if v: ax2.text(i, j, v, ha='center', va='center', fontsize=7, color='white' if v > 10 else 'black')
ax3 = fig.add_subplot(gs[1, 1]); im2 = ax3.imshow(hm.T.values, cmap='Oranges', aspect='auto'); ax3.set_xticks(range(len(hm.index))); ax3.set_xticklabels([f'{int(h)}' for h in hm.index]); ax3.set_yticks(range(len(hm.columns))); ax3.set_yticklabels(hm.columns)
ax3.set_title('구역×시간 사람·장비 혼재 슬롯 수 (People≥5 & 장비≥1)', weight='bold'); ax3.set_xlabel('시각(시)')
for i in range(hm.shape[0]):
    for j in range(hm.shape[1]):
        v = int(hm.iloc[i, j]);
        if v: ax3.text(i, j, v, ha='center', va='center', fontsize=7, color='white' if v > 14 else 'black')
fig.text(.01, .005, '자료: 04_camera_object_log(슬롯 최대 동시값), 05_delivery_log(Gate_In_Time), 06_lifting_log(Actual_Start, 완료 99건), 10_near_miss_reports. Proximity_Alert는 교육용 참고지표.', fontsize=8, color=GRY)
plt.tight_layout(); plt.savefig('output/fig2_hourly_risk.png', dpi=160); plt.close()

# ============ FIG 3. 원인·결과 구조도 ============
fig, ax = plt.subplots(figsize=(16, 9.5)); ax.set_xlim(0, 100); ax.set_ylim(0, 100); ax.axis('off')
def box(x, y, w, h, t, fc, ec=NAVY, fs=9, tc='#111', bold=False):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle='round,pad=0.4', fc=fc, ec=ec, lw=1.4)); ax.text(x + w / 2, y + h / 2, t, ha='center', va='center', fontsize=fs, color=tc, weight='bold' if bold else 'normal', linespacing=1.4)
def link(p, q, c=GRY, lw=1.5, style='-|>'):
    ax.add_patch(FancyArrowPatch(p, q, arrowstyle=style, mutation_scale=14, color=c, lw=lw, connectionstyle='arc3,rad=0.0'))
ax.text(50, 97, '원인·결과 구조도 — 구조적 제약 → 운영 메커니즘 → 안전 사건 ↔ 공정 손실 (데이터 근거 병기)', ha='center', fontsize=14, weight='bold', color=NAVY)
ax.text(8, 91, '근본원인(구조적 제약)', fontsize=11, weight='bold', color=GRY); ax.text(36, 91, '운영 메커니즘(중간원인)', fontsize=11, weight='bold', color=GRY); ax.text(66, 91, '안전 결과', fontsize=11, weight='bold', color=GRY); ax.text(86, 91, '공정 결과', fontsize=11, weight='bold', color=GRY)
root = [('단일 메인게이트\n차량·보행 공유 (C02·C05)', 80), ('반입창 2회/일 집중\n09-11·14-16 (C01)', 64), ('TC-01·TC-02 반경 중첩\nB3·C1 (C04·C10)', 48), ('지하램프 공용·적치금지\n(C07) + 협소 적치 (C08)', 32), ('안전정보 분산\n(허가·TBM·점검·일보 별도 관리)', 16)]
for t, y in root: box(2, y - 5, 20, 10, t, '#EAF2F8')
mid = [('동일 슬롯 복수 입문 %d/%d슬롯\n조기도착(≥30분) %d대 → B1 전면 정차' % (R['delivery_slots_multi'], R['delivery_slots_total'], R['delivery_stats']['early_arrivals_30min_plus']), 78),
       ('B2 장비 2대 이상 슬롯에서\n근접경보 100% 발생 (83/83건)', 64),
       ('TC-01·TC-02 양중 시간중첩 %d쌍 %d분\n+ 신호수 시야제한(적치물) 4회 반복' % (R['tc_overlap']['pairs'], R['tc_overlap']['total_min']), 50),
       ('D2 통로 자재 임시적치 반복\n(설비통로 지적 7건, 재발 4건)', 36),
       ('허가 미발행 %d작업일 · TBM 미참석 %d명·일\n기한 내 미조치 %d/52건' % (R['permit_missing_total'], R['tbm']['absent_mandays'], R['inspection']['overdue']), 20)]
for t, y in mid: box(28, y - 5.5, 28, 11, t, '#FEF9E7', ORG)
saf = [('B1 게이트 교행 아차 1건\nA4 타설일 교행 아차 3건', 80), ('B2 지게차 충돌위험 아차 2건\nB1·B2 근접경보 125건', 66), ('양중 배제구역 접근 3건·\n인양물 회전 1건·시야제한 3건', 52), ('D2 통로간섭 2건·화기 2건\nD3 굴착기 접근 2건', 38), ('동일 위험 재발 15건\n미조치 29건 누적', 22)]
for t, y in saf: box(60, y - 5, 20, 10, t, '#FADBD8', RED)
prj = [('T020 게이트 분리시설\n+2일 (DELIVERY_PRESSURE)', 80), ('T002·T003 LIFT_SLOT +4일\nT010 LIFT_CONFLICT +3일', 66), ('양중 대기 735분\n(강풍 550 + 순서조정 75 + 자재 140)', 52), ('T016 SPACE_CONFLICT +2일\nT014 MEP_CONFLICT +1일', 38), ('T012·T018 PERMIT_DELAY +3일\n진행중 공정 편차 합계 +9일', 22)]
for t, y in prj: box(84, y - 5, 15, 10, t, '#E8F8F5', GRN, fs=8.5)
for (a, b) in [(80, 78), (64, 64), (64, 78), (48, 50), (32, 36), (16, 20), (80, 20)]: link((22, a), (28, b))
for (a, b) in [(78, 80), (78, 66), (64, 66), (50, 52), (36, 38), (20, 22), (36, 22)]: link((56, a), (60, b), RED)
for (a, b) in [(80, 80), (66, 66), (52, 52), (38, 38), (22, 22), (50, 66)]: link((80, a), (84, b), GRN)
# 공정 → 안전 피드백 (공정압박)
ax.add_patch(FancyArrowPatch((91, 17), (42, 14), arrowstyle='-|>', mutation_scale=16, color='#8E44AD', lw=2, ls='--', connectionstyle='arc3,rad=-0.3'))
ax.text(66, 3.5, '피드백 루프: 공정 지연 → 공정압박 → 동일 슬롯 반입 몰아넣기·허가 생략·TBM 단축 → 안전사건 재발', ha='center', fontsize=9.5, color='#8E44AD', weight='bold')
ax.text(1, 1, '자료: 15_site_constraints, 05_delivery_log, 04_camera_object_log, 06_lifting_log, 09_inspection_action_log, 10_near_miss_reports, 11_work_permits, 12_tbm_log, 01_master_schedule, 02_daily_work_plan', fontsize=8, color=GRY)
plt.savefig('output/fig3_cause_effect.png', dpi=160, bbox_inches='tight'); plt.close()

# ============ FIG 4. 해결안 시스템 구성도 ============
fig, ax = plt.subplots(figsize=(16, 9.5)); ax.set_xlim(0, 100); ax.set_ylim(0, 100); ax.axis('off')
ax.text(50, 97, '해결안 시스템 구성도 — "작업·반입·양중 충돌 사전점검 게이트(Pre-Clash Gate)"  90일 파일럿', ha='center', fontsize=14, weight='bold', color=NAVY)
# 입력층
ax.text(10, 90, '① 입력 데이터 (기존 기록 그대로)', fontsize=10.5, weight='bold', color=GRY)
inputs = [('일일 작업계획·일보\n(02, Task·Zone·Risk)', 81), ('자재 반입 예약\n(05, Reserved/Arrival)', 70), ('일일 양중계획\n(06, 크레인·시간·구역)', 59), ('작업허가·TBM·점검\n(11·12·09)', 48), ('기상(13) + 90일 전망(18)\n풍속·결빙·일몰', 37), ('CCTV 슬롯 집계(04)\n출역(03)', 26)]
for t, y in inputs: box(1, y - 4, 19, 8, t, '#EAF2F8', fs=8.5)
# 엔진층
ax.text(36, 90, '② AI·규칙 엔진 (판단 지원, 결정 아님)', fontsize=10.5, weight='bold', color=GRY)
box(24, 70, 26, 15, 'F1  반입 슬롯 충돌 검사·재배정 제안\n• 슬롯당 1대/30분 규칙(C01)·레미콘일 예외(C09)\n• 조기도착 예측 → 장외대기 안내 문자\n• B2 하역장비(FL) 가용성 대조', '#FEF9E7', ORG, fs=8.5)
box(24, 52, 26, 15, 'F2  양중·동선 충돌 사전점검\n• TC-01×TC-02 시간중첩 자동 탐지(C10)\n• 양중 하부 High 작업 중첩 경고\n• 지브풍속 예측(×1.35/1.25/1.15) 보류 사전예고', '#FEF9E7', ORG, fs=8.5)
box(24, 34, 26, 15, 'F3  안전조치 추적·리마인더\n• 허가 필요작업 자동식별(고소·화기·굴착·양중)\n• TBM 참석 vs 출역 대조 → 미참석 보충\n• 지적 기한 D-1 알림·재발코드 에스컬레이션', '#FEF9E7', ORG, fs=8.5)
box(24, 18, 26, 12, 'LLM 보조 (Genspark 등)\n• 자유기재 지적내용 → Finding_Code 분류\n• TBM 위험요인 문구 → 당일 충돌경고 자동 삽입', '#F4ECF7', '#8E44AD', fs=8.5)
# 출력층
ax.text(63, 90, '③ 산출물 (매일 16:00 익일분)', fontsize=10.5, weight='bold', color=GRY)
box(54, 70, 22, 15, '익일 "충돌 체크리스트"\n(A4 1장 / 모바일)\n• 빨강: 반드시 조정\n• 노랑: 관리자 판단\n• 초록: 이상 없음', '#E8F8F5', GRN, fs=8.5)
box(54, 52, 22, 15, '반입 슬롯표·양중 순서표\n(협력사 F·G·A·B·J 공유)\n조기도착 안내문자', '#E8F8F5', GRN, fs=8.5)
box(54, 34, 22, 15, '안전 미결 보드\n허가 누락 / TBM 미참석 /\n기한임박 지적 / 재발 지적', '#E8F8F5', GRN, fs=8.5)
box(54, 18, 22, 12, '주간 KPI 리포트\n(10개 KPI, 전·후 비교)', '#E8F8F5', GRN, fs=8.5)
# 사람 결정층
ax.text(88, 90, '④ 사람의 최종 결정', fontsize=10.5, weight='bold', color=GRY)
box(80, 66, 19, 19, '공사·안전팀장\n익일 작업계획 승인\n(빨강 항목 미해결 시\n작업계획 확정 불가)', '#FADBD8', RED, fs=9, bold=True)
box(80, 46, 19, 15, '양중책임자\n일일 양중 우선순위\n·보류 결정 (C10)', '#FADBD8', RED, fs=9, bold=True)
box(80, 28, 19, 15, '물류반장·경비실\n슬롯 재배정 수용 여부\n게이트 통행 우선권', '#FADBD8', RED, fs=9, bold=True)
box(80, 12, 19, 12, '협력사 반장\nTBM 보충·허가 신청\n지적 조치 완료 보고', '#FADBD8', RED, fs=9, bold=True)
for y in [81, 70, 59, 48, 37, 26]: link((20, y), (24, min(max(y, 24), 77)))
for y in [77, 59, 41, 24]: link((50, y), (54, y), ORG)
for (a, b) in [(77, 75), (59, 53), (41, 35), (24, 18)]: link((76, a), (80, b), GRN)
ax.add_patch(FancyArrowPatch((89, 12), (37, 17), arrowstyle='-|>', mutation_scale=16, color=NAVY, lw=1.8, ls='--', connectionstyle='arc3,rad=-0.28'))
ax.text(63, 9, '피드백: 결정 결과(수용/거부/사유)를 기록 → 규칙 임계값·우선순위 보정 (사람이 승인한 기준만 반영)', ha='center', fontsize=9, color=NAVY, bbox=dict(fc='white', ec='none', alpha=.9))
ax.text(1, 0.5, '운영 원칙  • 자동 "중지"는 없음: 모든 알림은 제안이며 결정은 관리자   • 기존 양식(일보·허가서·TBM일지) 변경 없이 사본 입력만 추가   • 도구: 스프레드시트+스크립트+문자 API (외부비 5천만원 이내)   • 개인정보 미수집(인원수·차량ID만)', fontsize=8, color='#333', va='bottom', bbox=dict(fc='#F8F9F9', ec=GRY, lw=.8))
plt.savefig('output/fig4_system_architecture.png', dpi=160, bbox_inches='tight'); plt.close()

# ============ FIG 5. 적용 전·후 비교표 ============
import textwrap
kpi = pd.DataFrame(R['kpi'])
fig, ax = plt.subplots(figsize=(17, 9)); ax.axis('off')
cols = ['KPI', '적용 전\n(10월 실측)', '적용 후\n(90일 목표·가정)', '변화', '단위', '사용 파일·연결키 / 산식', '가정·제외기준']
fix = lambda s: str(s).replace('⟂', ' x ').replace('−', '-')
wrap = lambda s, w: '\n'.join(textwrap.wrap(fix(s), w)) if s else ''
rows = []
for _, r in kpi.iterrows():
    b, a = r['Before'], r['After(가정)']; ch = f'{(a - b) / b * 100:+.0f}%' if b else '-'
    rows.append([wrap(r['KPI'], 20), f'{b:,}', f'{a:,}', ch, wrap(r['Unit'], 12), wrap(r['Files/Keys'], 52) + '\n▸ ' + wrap(r['Formula'], 50), wrap(r['Assumption'], 40)])
tbl = ax.table(cellText=rows, colLabels=cols, loc='center', cellLoc='left', colWidths=[.15, .06, .07, .05, .08, .33, .26])
tbl.auto_set_font_size(False); tbl.set_fontsize(7.4); tbl.scale(1, 3.1)
for (i, j), c in tbl.get_celld().items():
    c.set_edgecolor('#BBB')
    if i == 0: c.set_facecolor(NAVY); c.set_text_props(color='white', weight='bold', ha='center'); c.set_height(c.get_height() * .6)
    elif j == 3: c.set_text_props(color=GRN if rows[i - 1][3].startswith('-') else RED, weight='bold')
    elif j in (1, 2): c.set_text_props(weight='bold')
    if i > 0 and i % 2 == 0 and j != 3: c.set_facecolor('#F4F6F7')
ax.set_title('적용 전·후 비교표 — 10개 정량 KPI (전: 2026.10.05~31 실측 / 후: 파일럿 종료 시 목표, 효과계수는 모두 가정)', fontsize=12.5, weight='bold', color=NAVY, pad=4)
fig.text(.01, .01, '※ "적용 후" 값은 제공 데이터에 효과계수(가정)를 곱한 목표값이며 실측이 아님. 모든 가정은 90일 파일럿 성과검증(W12~13)에서 실측치로 대체. 안전 관련 최종 결정권은 현장 관리자에게 있음.', fontsize=8, color=GRY)
plt.savefig('output/fig5_before_after.png', dpi=170, bbox_inches='tight'); plt.close()

# ============ FIG 6. 90일 실행 로드맵 ============
cl = XL.parse('18_climate_reference_90d'); la = XL.parse('16_lookahead_90d')
weeks = cl.Week.tolist(); n = len(weeks)
fig, ax = plt.subplots(figsize=(18, 10)); ax.set_xlim(-0.3, n + 3.2); ax.set_ylim(-2.2, 12.6); ax.axis('off')
ax.set_title('90일 실행 로드맵 (2026-11-02 ~ 2027-01-30, 13주 / 주 6일, 휴무 일요일·12/25·1/1, 12/31 축소운영)', fontsize=14, weight='bold', color=NAVY)
phases = [('① 도입준비', 0, 2, '#D6EAF8'), ('② 데이터 정비', 1, 3, '#D5F5E3'), ('③ 파일럿 적용 (B·C구역)', 3, 7, '#FCF3CF'), ('④ 현장 전면적용 (A·D 포함)', 7, 11, '#FADBD8'), ('⑤ 성과검증·확대판단', 11, 13, '#E8DAEF')]
for name, s, e, c in phases:
    ax.add_patch(Rectangle((s, 11.2), e - s, .9, fc=c, ec=NAVY, lw=1)); ax.text((s + e) / 2, 11.65, name, ha='center', va='center', fontsize=9.5, weight='bold', color=NAVY)
for i, w in enumerate(weeks):
    ax.text(i + .5, 10.75, w.replace('2026-', '').replace('2027-', "'27-"), ha='center', fontsize=8, color=GRY)
    ax.text(i + .5, 10.35, cl.Week_Start[i][5:], ha='center', fontsize=7.5, color=GRY)
    if cl.Planned_Work_Days[i] < 6: ax.text(i + .5, 9.95, f'작업 {cl.Planned_Work_Days[i]}일', ha='center', fontsize=7.5, color=RED, weight='bold')
tasks = [
 ('킥오프·역할지정(TF 5명)·KPI 베이스라인 확정', 0, 1, NAVY, '공사·안전팀장'),
 ('반입예약·양중계획·허가·TBM 입력 사본 양식 통일', 0, 2, NAVY, '물류F·양중팀'),
 ('10월 데이터 정제 규칙 코드화(Finding_Code, 허가대상 매핑)', 1, 3, GRN, 'TF 데이터담당'),
 ('F1 반입 슬롯 검사 스크립트·문자 안내 테스트', 1, 3, GRN, 'TF + 경비실'),
 ('F2 양중 중첩·풍속 예측 규칙 구축(지브보정 1.35/1.25/1.15)', 2, 4, GRN, 'TF + 양중책임자'),
 ('F1 운영: B1·B2 슬롯 1대/30분, 조기도착 장외대기', 3, 13, ORG, '물류F·경비실'),
 ('F2 운영: 일일 양중계획 충돌검사 → 양중책임자 승인', 3, 13, ORG, '양중책임자'),
 ('F3 운영: 허가·TBM·지적 미결 보드 (D2·D3 우선)', 4, 13, ORG, '안전팀·협력사J'),
 ('동절기 전환: 한중콘크리트 보온양생 화기·질식 체크 추가(W50~)', 7, 13, RED, '안전팀·협력사D'),
 ('일몰 17:15 대응: 16시 이후 양중·하역 슬롯 축소 규칙', 7, 13, RED, '양중팀·물류F'),
 ('결빙·강풍일 양중 사전보류 예고(전망 18 연동)', 5, 13, RED, 'TF'),
 ('주간 KPI 리포트·관리자 피드백 반영', 3, 13, BLU, 'TF'),
 ('중간점검(W49) → 임계값 조정', 6, 7, '#8E44AD', '공사·안전팀장'),
 ('성과검증(10개 KPI 실측) · 확대/중단 판단 보고', 11, 13, '#8E44AD', '현장소장'),
]
for k, (t, s, e, c, who) in enumerate(tasks):
    y = 9.3 - k * .66
    ax.add_patch(FancyBboxPatch((s + .05, y - .22), e - s - .1, .44, boxstyle='round,pad=0.02', fc=c, ec='none', alpha=.85))
    inside = (e - s) >= 4
    if inside: ax.text(s + .15, y, t, va='center', fontsize=8, color='white', weight='bold')
    else: ax.text(e + .1, y, t, va='center', fontsize=8, color=c, weight='bold')
    ax.text(n + .2, y, who, va='center', fontsize=8, color=GRY)
ax.text(n + .2, 9.95, '담당', fontsize=8.5, weight='bold', color=GRY)
# 기상 리스크 띠
for i in range(n):
    sev = cl.Freezing_Days[i] + cl.Expected_Snow_Days[i] + cl.Expected_Strong_Wind_Days[i]
    ax.add_patch(Rectangle((i, -0.75), 1, .55, fc=plt.cm.Blues(0.15 + min(sev, 8) / 10), ec='white'))
    ax.text(i + .5, -0.47, f'결빙{cl.Freezing_Days[i]}·설{cl.Expected_Snow_Days[i]}·풍{cl.Expected_Strong_Wind_Days[i]}', ha='center', va='center', fontsize=6.8, color='#111')
ax.text(-0.25, -0.47, '기상(18)', ha='right', fontsize=8, color=GRY, weight='bold')
ax.text(-0.25, -1.05, '전망공정(16)', ha='right', fontsize=8, color=GRY, weight='bold')
ax.text(n / 2, -1.05, 'A1/A2 상층부 골조 반복(TC-01·PC-01 양중·타설 중첩) ∥ C1/C2 커튼월(풍속) ∥ D2/D3 설비·토목 병행(지하통로 혼잡·난방화기) — W53 축소운영', ha='center', fontsize=8, color='#333')
for xx in [2, 3, 7, 11]: ax.axvline(xx, color=NAVY, lw=.8, ls=':')
ax.text(0, -1.75, '예산(외부 직접비, VAT포함) ≤ 5천만원 (만원, 가정): 분석·개발 인력(파트타임 2인×3개월) 2,400 / 문자·클라우드·시트 라이선스 300 / 풍속계 2대·태블릿 5대 임대 600 / 교육·운영비 700 / 예비 1,000  = 합계 5,000', fontsize=8, color='#333', va='top', bbox=dict(fc='#F8F9F9', ec=GRY, lw=.6))
plt.savefig('output/fig6_roadmap_90d.png', dpi=160, bbox_inches='tight'); plt.close()

# ============ 보조 그림 ============
# 7 공정 편차 & 지연사유
ms = XL.parse('01_master_schedule')
fig, axs = plt.subplots(1, 2, figsize=(15, 5.5))
m2 = ms.sort_values('Forecast_Variance_Days'); colors = [RED if s == 'In Progress' else GRY for s in m2.Status_AsOf_2026_10_31]
axs[0].barh(m2.Task_ID + ' ' + m2.Task_Name.str[:12], m2.Forecast_Variance_Days, color=colors); axs[0].axvline(0, color='k', lw=.8); axs[0].set_title('공정별 예측편차(작업일) — 빨강=진행중(4주 목표 직접영향)', weight='bold'); axs[0].set_xlabel('Forecast_Finish − Planned_Finish (일)')
for i, (v, rc) in enumerate(zip(m2.Forecast_Variance_Days, m2.Delay_Reason_Code)): axs[0].text(v + .05 if v >= 0 else v - .05, i, rc, va='center', ha='left' if v >= 0 else 'right', fontsize=7.5)
cw = pd.Series(R['crew_wait']['by_reason']).apply(lambda d: d['sum']).sort_values()
axs[1].barh(cw.index, cw.values, color=[RED if '강풍' in k else ORG for k in cw.index]); axs[1].set_title(f"작업대기 사유별 합계 (총 {R['crew_wait']['total_min']}분 ≈ {R['crew_wait_manhours']:.0f} 인·시)", weight='bold'); axs[1].set_xlabel('분')
for i, v in enumerate(cw.values): axs[1].text(v + 3, i, f'{v}', va='center', fontsize=8)
fig.text(.01, .01, '자료: 01_master_schedule(Forecast_Variance_Days, Delay_Reason_Code), 02_daily_work_plan(Crew_Waiting_Minutes × Actual_Workers)', fontsize=8, color=GRY)
plt.tight_layout(); plt.savefig('output/fig7_schedule_variance.png', dpi=150); plt.close()

# 8 반입 슬롯 집중 & B2 경보
dl = XL.parse('05_delivery_log'); dl['Gate_In_Time'] = pd.to_datetime(dl.Gate_In_Time); dl['Date'] = pd.to_datetime(dl.Date)
big = dl[dl.Delivery_Size_Class == '대형']; piv = big.groupby([big.Date.dt.strftime('%m/%d'), big.Gate_In_Time.dt.hour]).size().unstack(fill_value=0)
fig, axs = plt.subplots(1, 2, figsize=(15, 5.5), gridspec_kw={'width_ratios': [1.6, 1]})
im = axs[0].imshow(piv.values, cmap='Blues', aspect='auto'); axs[0].set_xticks(range(len(piv.columns))); axs[0].set_xticklabels([f'{h}시' for h in piv.columns]); axs[0].set_yticks(range(len(piv.index))); axs[0].set_yticklabels(piv.index, fontsize=8)
for i in range(piv.shape[0]):
    for j in range(piv.shape[1]):
        v = piv.iloc[i, j]
        if v: axs[0].text(j, i, v, ha='center', va='center', fontsize=8, color='white' if v >= 2 else 'black', weight='bold' if v >= 2 else 'normal')
axs[0].set_title(f"대형자재 입문 슬롯(일×시) — 복수입문 {R['delivery_slots_multi']}/{R['delivery_slots_total']}슬롯, 3대 이상 {R['delivery_slots_3plus']}슬롯", weight='bold')
bd = pd.Series(R['B2_alert_by_deliv']); bd.index = bd.index.astype(float).astype(int)
axs[1].bar(bd.index.astype(str), bd.values, color=[GRY, ORG, RED, RED]); axs[1].set_title('B2 슬롯당 평균 근접경보 vs 동일시간 입문 대수', weight='bold'); axs[1].set_xlabel('해당 시간대 입문 대수'); axs[1].set_ylabel('평균 경보(건/슬롯)')
for i, v in enumerate(bd.values): axs[1].text(i, v + .02, f'{v:.2f}', ha='center', fontsize=9)
fig.text(.01, .01, '자료: 05_delivery_log(Gate_In_Time, 대형 80건) ⟂ 04_camera_object_log(CAM-B2, Date+hour). 경보는 참고지표.', fontsize=8, color=GRY)
plt.tight_layout(); plt.savefig('output/fig8_delivery_slots.png', dpi=150); plt.close()

# 9 안전관리 프로세스 현황
ins = XL.parse('09_inspection_action_log')
fig, axs = plt.subplots(1, 3, figsize=(16, 5))
st = ins.groupby(['Subzone', 'Status']).size().unstack(fill_value=0).reindex(columns=['Closed', 'In Progress', 'Open']).fillna(0).sort_values('Open', ascending=False)
st.plot(kind='barh', stacked=True, ax=axs[0], color=[GRN, ORG, RED]); axs[0].set_title('구역별 안전지적 조치상태 (52건)', weight='bold'); axs[0].invert_yaxis()
tc = pd.Series(R['inspection']['top_codes']); axs[1].barh(tc.index[::-1], tc.values[::-1], color=NAVY); axs[1].set_title('반복 지적 코드 Top 8 (Finding_Code 정규화)', weight='bold')
pg = pd.DataFrame(R['permit_gap']).T; pg.index = [i.replace('_', '\n') for i in pg.index]
pg[['permit_days', 'missing']].plot(kind='bar', stacked=True, ax=axs[2], color=[GRN, RED], rot=0); axs[2].set_title(f"작업허가 발행/미발행 작업일 (미발행 {R['permit_missing_total']}일)", weight='bold'); axs[2].legend(['허가 발행일', '미발행 작업일'], fontsize=8)
fig.text(.01, .01, '자료: 09_inspection_action_log, 11_work_permits ⟂ 02_daily_work_plan (Date, Task_ID). T016 고소작업 대상은 가정.', fontsize=8, color=GRY)
plt.tight_layout(); plt.savefig('output/fig9_safety_process.png', dpi=150); plt.close()
print('figures saved:', sorted(f for f in os.listdir('output') if f.endswith('.png')))
