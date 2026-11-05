# SCX NEXT 2026 — 도심지 복합시설 건설현장 안전·공정 통합 최적화 분석

2026 SCX NEXT 청년 스마트건설 AI Lab 사전 온라인 프로젝트 (데이터 패키지 v1.4.3)

## 구조
```
data/        제공 데이터 패키지(가상·비식별) + PDF 텍스트 추출본
analysis/    재현 가능한 분석 스크립트
  01_quality_check.py    데이터 품질 진단 → output/quality_report.md
  02_core_analysis.py    위험·간섭·공정·KPI 분석 → output/analysis_results.json, kpi_table.csv
  03_visuals.py          필수 시각자료 6종 + 보조 3종 → output/fig*.png
  04_sensitivity.py      위험지수 가중치 민감도(우선순위 강건성) → output/fig10_sensitivity.png
output/
  findings.md            9장 목차 기준 분석결과·해결안 초안 (PDF 작성 원고)
  risk_factors.md        미션1 위험요인 7개 상세 설명
  quality_report.md      정제·가정·제외 기준 (AI활용·검증기록 별첨용)
  reference_buildsmart_review.md  외부 참고자료(BuildSmart) 검토 — 채택/배제/반면교사
  qna_compliance.md      운영사무국 Q&A 반영 체크리스트 + 가정↔제약 모순 점검
  예선결과물_SCX_NEXT.pdf  최종 제출용 PDF (표지 포함 15쪽)
report/      PDF 원고(part1~3.html) + style.css + build_pdf.py (WeasyPrint)
  fig1~6                 필수 시각자료 / fig7~9 보조
```

## 실행
```bash
python3 analysis/01_quality_check.py
python3 analysis/02_core_analysis.py
python3 analysis/03_visuals.py
```
의존성: pandas, openpyxl, matplotlib, NanumGothic 폰트

## 핵심 결과 요약
- **핫스팟**: B2 하역장(09~11·14~16시, 근접경보 83건·혼재슬롯 120), D2 지하설비(미조치 7·재발 4·TBM 미참석 36), A4 타설일 교행, B3·C1 TC 시간중첩 8쌍
- **근본원인**: 단일게이트+반입창 집중 → 동일 슬롯 복수입문 34% / 크레인별 양중계획 분리 / 허가·TBM·점검 기록 분산
- **해결안**: Pre-Clash Gate (F1 반입 슬롯 충돌검사, F2 양중·동선 충돌 사전점검, F3 안전조치 추적) — 모든 출력은 제안, 결정은 관리자
- **KPI 10종** 전·후 비교 (효과계수는 가정, 90일 파일럿 실측으로 대체)

※ 모든 데이터는 교육용 가상 데이터이며, 분석에 사용한 가정은 결과물에 [가정]으로 표기함.
