"""
04_sensitivity.py — 구역 종합 위험지수 가중치 민감도 분석
[외부참고: BuildSmart supplier_recommendation의 '가중치 조정 → 순위 재계산' 패턴을 자체 구현]
목적: 팀이 가정한 가중치(.25/.15/.15/.15/.10/.10/.10)가 바뀌어도 우선순위(B2·D2 상위)가 유지되는지 검증
출력: output/sensitivity_result.json, output/fig10_sensitivity.png
"""
import pandas as pd, numpy as np, json
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
fm.fontManager.addfont('/usr/share/fonts/truetype/nanum/NanumGothic.ttf'); plt.rcParams['font.family'] = 'NanumGothic'; plt.rcParams['axes.unicode_minus'] = False

zone = pd.read_csv('output/zone_risk_profile.csv', index_col=0)
IND = ['near_miss', 'prox_alert', 'mix_slots', 'insp_open', 'insp_recur', 'risk_max', 'high_days']
BASE = np.array([.25, .15, .15, .15, .10, .10, .10])
norm = lambda s: (s - s.min()) / (s.max() - s.min()) if s.max() > s.min() else s * 0
N = zone[IND].apply(norm)

def rank(w):
    return (N.values @ w).argsort()[::-1]

rng = np.random.default_rng(42); K = 5000
top1 = {z: 0 for z in zone.index}; top2 = {z: 0 for z in zone.index}; top3 = {z: 0 for z in zone.index}
ranks = {z: [] for z in zone.index}
for _ in range(K):
    w = rng.dirichlet(np.ones(7))                    # 가중치 전체를 무작위(합=1)로 교란 — 가장 보수적인 검정
    r = rank(w); order = zone.index[r]
    top1[order[0]] += 1
    for z in order[:2]: top2[z] += 1
    for z in order[:3]: top3[z] += 1
    for i, z in enumerate(order): ranks[z].append(i + 1)
res = pd.DataFrame({'top1_pct': pd.Series(top1) / K * 100, 'top2_pct': pd.Series(top2) / K * 100, 'top3_pct': pd.Series(top3) / K * 100,
                    'rank_mean': {z: np.mean(v) for z, v in ranks.items()}, 'rank_p90': {z: np.percentile(v, 90) for z, v in ranks.items()}}).round(1)
res['base_rank'] = pd.Series({zone.index[r]: i + 1 for i, r in enumerate(rank(BASE))})
res = res.sort_values('base_rank')
# 단일 지표 제거(leave-one-out) 시 순위
loo = {}
for i, k in enumerate(IND):
    w = BASE.copy(); w[i] = 0; w = w / w.sum()
    loo[k] = list(zone.index[rank(w)][:3])
out = {'K': K, 'method': 'Dirichlet(1,...,1) 무작위 가중치 — 모든 가중치 조합을 균등 탐색', 'table': res.to_dict(orient='index'), 'leave_one_out_top3': loo}
json.dump(out, open('output/sensitivity_result.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print(res); print(loo)

fig, axs = plt.subplots(1, 2, figsize=(14, 5.2))
r2 = res.sort_values('top3_pct', ascending=False)
axs[0].barh(r2.index[::-1], r2.top3_pct[::-1], color=['#C0392B' if v >= 50 else '#7F8C8D' for v in r2.top3_pct[::-1]])
axs[0].set_xlabel('상위 3위 안에 든 비율 (%)'); axs[0].set_title(f'가중치 무작위 교란 {K:,}회 — 구역별 Top-3 진입률', weight='bold')
for i, v in enumerate(r2.top3_pct[::-1]): axs[0].text(v + 1, i, f'{v:.0f}%', va='center', fontsize=9)
bp = axs[1].boxplot([ranks[z] for z in res.index], tick_labels=res.index, vert=True, patch_artist=True, showfliers=False)
for p, z in zip(bp['boxes'], res.index): p.set_facecolor('#F5B7B1' if z in ('B2', 'D2') else '#D6DBDF')
axs[1].invert_yaxis(); axs[1].set_ylabel('순위 (1=최고위험)'); axs[1].set_title('가중치 교란 시 순위 분포 (기준 가중치 순 정렬)', weight='bold'); axs[1].axhline(3.5, color='#C0392B', ls='--', lw=.8)
fig.text(.01, .01, '자료: output/zone_risk_profile.csv (7개 지표 min-max 정규화). 기준 가중치는 팀 가정. [외부참고: BuildSmart 가중치 조정 패턴을 민감도 검정으로 전용]', fontsize=8, color='#7F8C8D')
plt.tight_layout(); plt.savefig('output/fig10_sensitivity.png', dpi=150); plt.close()
