"""05_winter_fig.py — 90일 기후 전망(18, 가상) × Look-ahead 계절위험(16) 그림 → output/fig11_winter.png"""
import pandas as pd, numpy as np
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt, matplotlib.font_manager as fm
fm.fontManager.addfont('/usr/share/fonts/truetype/nanum/NanumGothic.ttf'); plt.rcParams['font.family'] = 'NanumGothic'; plt.rcParams['axes.unicode_minus'] = False
XL = pd.ExcelFile('data/SCX_NEXT_Analysis_Tables_v1.4.3.xlsx'); cl = XL.parse('18_climate_reference_90d'); wx = XL.parse('13_weather_hourly')
NAVY, RED, BLU, GRY = '#1F3A5F', '#C0392B', '#2E86C1', '#7F8C8D'
fig, ax = plt.subplots(figsize=(14, 5)); x = np.arange(len(cl)); lbl = [w.replace('2026-', '').replace('2027-', "'27-") for w in cl.Week]
ax.bar(x - .2, cl.Freezing_Days, .4, color='#AED6F1', label='결빙일(일/주)'); ax.bar(x + .2, cl.Expected_Snow_Days, .4, color='#5D6D7E', label='적설일(일/주)')
ax.bar(x, cl.Expected_Strong_Wind_Days, .15, color=RED, alpha=.7, label='강풍일(일/주)'); ax.set_ylabel('일수/주'); ax.set_ylim(0, 8)
ax2 = ax.twinx(); ax2.plot(x, cl.Avg_Temp_C, 'o-', color=NAVY, lw=2, label='주 평균기온 °C'); ax2.plot(x, cl.Min_Temp_C, 's--', color=BLU, lw=1.8, label='주 최저기온 °C')
ax2.axhline(0, color=RED, lw=1, ls=':'); ax2.set_ylabel('기온 °C'); ax2.set_ylim(-9, 14)
ax2.axhline(wx.Temperature_C.min(), color=GRY, lw=1, ls='-.'); ax2.text(0, wx.Temperature_C.min() + .3, f'10월 분석기간 최저 {wx.Temperature_C.min():.0f}°C (영하 0시간)', fontsize=8.5, color=GRY)
first = int(np.argmax(cl.Min_Temp_C < 0)); ax.axvspan(first - .5, len(cl) - .5, color='#EBF5FB', zorder=0); ax.text(first - .4, 7.5, f'{lbl[first]}~ 7주 연속 영하 최저기온 · 결빙 {int(cl.Freezing_Days.sum())}/{int(cl.Planned_Work_Days.sum())}작업일', fontsize=9.5, color=NAVY, weight='bold')
ax.axvline(5 - .5, color=RED, lw=1.2, ls='--'); ax.text(4.6, 6.6, 'W50~ 한중콘크리트 보온양생\n(열풍기·갈탄 질식·화재)\n지하 난방기구·환기 부족', fontsize=8.5, color=RED, ha='right', va='top')
ax.set_xticks(x); ax.set_xticklabels([f'{l}\n{d[5:]}' for l, d in zip(lbl, cl.Week_Start)], fontsize=8)
for i, s in enumerate(cl.Sunset_Time): ax.text(i, -1.15, s, ha='center', fontsize=7.5, color=GRY, transform=ax.get_xaxis_transform(), clip_on=False)
ax.text(-.6, -1.15, '일몰', ha='right', fontsize=7.5, color=GRY, transform=ax.get_xaxis_transform(), clip_on=False)
h1, l1 = ax.get_legend_handles_labels(); h2, l2 = ax2.get_legend_handles_labels(); ax.legend(h1 + h2, l1 + l2, loc='upper left', fontsize=8, ncol=5, framealpha=.95)
ax.set_title('R8 동절기 전환 위험 — 90일 기후 전망(18, 교육용 가상값)과 Look-ahead 계절위험(16)', weight='bold', color=NAVY)
fig.text(.01, .005, '자료: 18_climate_reference_90d(가상 전망·실제 예보 아님), 16_lookahead_90d.Season_Risk, 13_weather_hourly. 위험성평가(08)에는 한랭·결빙·질식 항목 0건 → W50 전 갱신 필요.', fontsize=8, color=GRY)
plt.tight_layout(rect=(0, .04, 1, 1)); plt.savefig('output/fig11_winter.png', dpi=150); plt.close(); print('saved fig11')
