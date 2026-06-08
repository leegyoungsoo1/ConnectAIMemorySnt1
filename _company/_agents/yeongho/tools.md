# 🔴 영호 — 도구 매니페스트

_영호 에이전트가 어떤 도구를 어디까지 자율적으로 쓸 수 있는지 정의합니다._

---

## 자율도 레벨

AUTONOMY_LEVEL: 2

| 값 | 의미 |
|---|---|
| 0 | Off — 도구 전체 비활성 |
| 1 | Read-only — 읽기·분석·보고만 |
| 2 | Draft — 초안 작성 후 사용자 승인 게이트 통과해야 실행 ⭐ 권장 |
| 3 | Auto — 화이트리스트 안에서 자동 실행 |

---

## 4단계 모의해킹 워크플로우

```
1단계 [정찰]        port_scan.py          → scan_results.json
       ↓
2단계 [취약점 점검]  service_vuln_check.py → vuln_results.json
       ↓
3단계 [침투 검증]    exploit_test.py       → exploit_results.json
       ↓
4단계 [보고서]       generate_report.py    → reports/pentest_report_*.md
                                              ↓ 영철에게 전달
```

각 단계는 이전 단계의 JSON 출력을 자동으로 읽어 실행됩니다.

---

## 사용 가능한 도구

### 1단계 — `port_scan.py`
- **목적**: TCP 포트 스캔, 열린 서비스 식별
- **입력**: `port_scan.json` (target_host, scope, approved_by)
- **출력**: `scan_results.json`
- **핵심 옵션**: `--ports 1-9999`, `--threads 200`

### 2단계 — `service_vuln_check.py`
- **목적**: 서비스별 취약점 점검 (헤더, SMBv1, RPC, 위험 경로 등)
- **입력**: `scan_results.json` (자동) 또는 `--ports`
- **출력**: `vuln_results.json`
- **점검 항목**: HTTP 보안 헤더, 위험 메서드, 민감 경로, SMBv1, RPC, RDP, SSH

### 3단계 — `exploit_test.py`
- **목적**: 안전한 침투 검증 (파괴 없음)
- **입력**: `vuln_results.json` (자동)
- **출력**: `exploit_results.json`
- **테스트**: 기본 자격증명, SQL 인젝션 감지, 디렉터리 리스팅, 경로 탐색, SMB Null Session

### 4단계 — `generate_report.py`
- **목적**: 1~3단계 결과 종합 → 마크다운 보고서 + 영철 체크리스트
- **입력**: `scan/vuln/exploit_results.json` (자동)
- **출력**: `reports/pentest_report_YYYYMMDD_HHmm.md`

---

## 안전 규칙 (모든 레벨 공통, 절대 우회 X)

- **삭제·배포·발송** 류는 자율도와 무관하게 **항상 승인 게이트**
- 모든 도구는 `scope`에 명시된 승인 범위 내에서만 실행
- 외부 행동은 `_agents/yeongho/activity.log`에 기록
- 3단계 exploit_test는 읽기·탐지만 수행 — 변조·삭제 절대 금지
