# 데이터 품질 진단 리포트 (v1.4.3)

분석기준일 2026-10-31 / 통합 Excel(04_analysis_tables) 단일 형식 사용, CSV 중복 합산 없음


## 1. 결측치 현황

- **01_master_schedule**: Predecessor=12, Actual_Finish=10, Predecessor_Relation=12, Work_Package_Note=12

- **05_delivery_log**: Unload_End_Time=1

- **06_lifting_log**: Actual_Start=14, Actual_End=14, Related_Delivery_ID=9

- **09_inspection_action_log**: Closed_DateTime=29, After_Photo_ID=29

- **10_near_miss_reports**: Equipment_ID=3, Related_Event_ID=12

- **11_work_permits**: Equipment_ID=32, Gas_O2_Pct=62, Gas_LEL_Pct=62

- 해석: 01 Actual_Finish 결측 10건 = 진행중 공정(정상). 06 Actual_Start/End 결측 14건 = 보류·취소 양중(정상). 09 Closed_DateTime 결측 29건 = 미조치(Open/In Progress). 05 DL-0079 Unload_End_Time 결측 1건 → Gate_Out_Time(15:53) 기준 대체·가정 표기.


## 2. 중복 ID·문서번호

- 05 반입전표번호 중복: 1건 → [['DL-0077', 'SRC-D-0077', '덕트·배관 지지대'], ['DL-0080', 'SRC-D-0077', '커튼월 패널']]

  - 처리: 서로 다른 Delivery_ID·자재·시각 → 별개 업무로 **유지**(안내서 §5: 문서번호 중복만으로 자동 삭제 금지). 전표번호 오기재로 가정.

- 06_lifting_log Lift_ID 중복: 0건

- 11_work_permits Permit_ID 중복: 0건

- 12_tbm_log TBM_ID 중복: 0건

- 09_inspection_action_log Inspection_ID 중복: 0건

- 10_near_miss_reports NearMiss_ID 중복: 0건

- 02 (Date,Task_ID) 중복: 0건


## 3. 용어·표기 변형

- 09 Finding 자유기재 접미어('…오전 점검에서 확인', '…작업구간 정리 중 확인', '…공종간 합동점검에서 확인', '…작업 전 순회점검에서 확인') 부착: 41/52건 → **Finding_Code(20종)** 기준으로 정규화하여 반복지적 집계

- 09 Finding 원문 고유값 39개 vs Finding_Code 23개

- 02 Trade: '형틀공사'(1건) vs '철근콘크리트' 혼용 → T002 거푸집 공정은 Task_ID 기준으로 통합

- 지하층 표기 B2F/B3F ≠ 구역코드 B2/B3 (안내서 명시) → 구역분석은 Subzone 코드만 사용

- 06 Rigging_Check: '적합' / '샤클 교체 후 적합' 등 변형 → '적합' 계열로 통합


## 4. 운영규칙 예외 기록

- C01 대형자재 예약시작 창 외 예약: 4/80건 (DL-0001, DL-0003, DL-0004, DL-0002) — 모두 10/05~06 초기

- 예약시작 전 조기 입문: 3건 / 예약종료 후 지연 입문: 1건 (ENV-001·009 조기도착 민원과 대응)

- 17:00 이후 하역 완료: 0건 (C03 준수)

- 작업허가 미발행(작업일보 작업일 vs 허가일):

  - T016 고소작업: 작업일 17 / 허가일 0 / **미발행 17일**

  - T010 고소작업: 작업일 15 / 허가일 10 / **미발행 5일**

  - T014 굴착·토공: 작업일 14 / 허가일 8 / **미발행 6일**

  - T013 굴착·토공: 작업일 6 / 허가일 3 / **미발행 3일**

  - 가정: 고소작업대(SL-03) 사용 T016은 고소작업 허가 대상으로 간주(T010 사례와 동일 기준). 중량물 양중은 Permit_ID 연결 100%, 허가시간 외 양중 0건.

- TBM 미참석: 164명·일 / 미참석 발생 TBM 110/282회 (참석>실투입 이상치 0건)

- 안전점검 기한 내 미조치(완료지연+기한경과 미완료): 34/52건, 미완료 29건, 재발 플래그 Y 15건


## 5. 원천기록 ↔ 분석표 교차검증

- 작업일보 원천 282행 = 02_daily_work_plan 282행 (행수·공종코드 일치)

- 자재반입대장 116행 = 05_delivery_log 116행

- 양중작업일지 113행 = 06_lifting_log 113행

- 아차사고대장 25행 = 10_near_miss_reports 25행

- 작업허가대장 73행 = 11_work_permits 73행

- TBM일지 282행 = 12_tbm_log 282행

- 안전점검조치대장 52행 = 09_inspection_action_log 52행

- 결론: 원천(국문 헤더)과 분석표(영문 헤더)는 동일 데이터의 형식 차이 → 분석표만 사용, 합산 없음


## 6. 적용한 정제·가정·제외 기준

- 분석기간 2026-10-05~10-31, 일요일·10/09 제외 → 작업일 23일 (CCTV 23일과 일치)

- 양중 실적 = Status '완료' 99건만. 보류 13·취소 1건은 실적 제외하되 '풍속 보류' 손실시간 산정에 사용

- 레미콘 36대(3일×12대)는 C01 반입창 예외 → 대형자재 KPI에서 제외, 레미콘 간격 KPI 별도

- CCTV People/Equipment_Count는 슬롯 내 최대 동시값 → 밀집지표는 '평균 최대 동시값'으로 표기, Proximity_Alert는 참고지표(정답값 아님)

- 거리·면적은 산정하지 않음(배치도 무축척). 반경 중첩은 C04·C10 텍스트 기준 B3·C1을 중첩구역으로 가정

- 공정편차 기준선 = 01 Planned_Finish, 기준일 10/31. Forecast_Variance_Days 사용(작업일 기준)

- TBM 미참석 = max(실투입-참석, 0). 참석>실투입은 0건이라 보정 불필요

- DL-0079 Unload_End 결측 → 하역시간 통계에서 제외(79건으로 집계)
