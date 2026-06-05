# 📋 취약점 보고서 생성 도구 (영철 담당)

각 담당자의 점검 결과를 취합해 체크리스트와 보고서를 자동 생성합니다.

## 실행 방법
```bash
# 샘플로 테스트
python vuln_report_gen.py

# 실제 결과 파일로 생성
python vuln_report_gen.py --input results.json --output 2024_report.md
```

## 입력 형식 (JSON)
```json
[
  {
    "id": "V-001",
    "target": "web-server-01",
    "type": "웹 취약점",
    "title": "SQL Injection",
    "severity": "High",
    "description": "로그인 폼 SQL Injection 가능",
    "remediation": "PreparedStatement 사용"
  }
]
```
