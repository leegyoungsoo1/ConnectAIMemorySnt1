# 🔴 보고서 생성 (영호 담당 — 4단계)

1~3단계 결과를 종합해 모의해킹 최종 보고서를 생성하고, 영철에게 전달할 체크리스트를 작성합니다.

## 출력

- `reports/pentest_report_YYYYMMDD_HHmm.md` — 마크다운 보고서
- 영철 체크리스트용 조치 우선순위 포함

## 실행 방법
```bash
# 전체 단계 결과 자동 종합
python generate_report.py

# 테스터 이름 지정
python generate_report.py --tester 영호
```
