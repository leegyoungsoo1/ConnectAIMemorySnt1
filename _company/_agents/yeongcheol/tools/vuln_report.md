# 🛡️ 보안 취약점 점검 결과 보고서

**점검 일시**: 2026-06-11 15:36
**대상 시스템**: web-server-01, linux-server-01, win-server-01
**작성자**: 영철 (AI 보안팀)

---

## 📊 요약

| 심각도 | 건수 |
|--------|------|
| 🔴 Critical | 0 |
| 🟠 High | 2 |
| 🟡 Medium | 1 |
| 🟢 Low | 0 |
| ℹ️ Info | 0 |
| **합계** | **3** |

---

## 📋 취약점 목록 (심각도 순)

### 🟠 [V-001] SQL Injection 취약점 (High)
- **대상**: web-server-01
- **유형**: 웹 취약점
- **설명**: 로그인 폼에서 SQL Injection 가능
- **조치방법**: PreparedStatement 사용, 입력값 검증

### 🟠 [V-003] SSH 루트 로그인 허용 (High)
- **대상**: linux-server-01
- **유형**: 리눅스 취약점
- **설명**: PermitRootLogin yes 설정
- **조치방법**: sshd_config: PermitRootLogin no 설정 후 재시작

### 🟡 [V-002] RDP 포트 외부 노출 (Medium)
- **대상**: win-server-01
- **유형**: 윈도우 취약점
- **설명**: 3389 포트가 외부에서 접근 가능
- **조치방법**: 방화벽 정책으로 내부망 접근만 허용


---

## ✅ 조치 체크리스트

- [ ] 🟠 [V-001] web-server-01 — SQL Injection 취약점 (High)
- [ ] 🟠 [V-003] linux-server-01 — SSH 루트 로그인 허용 (High)
- [ ] 🟡 [V-002] win-server-01 — RDP 포트 외부 노출 (Medium)

---

## 📝 경영진 요약

본 점검 결과 총 3건의 취약점이 발견되었으며,
즉시 조치가 필요한 Critical/High 취약점은 2건입니다.

---
*이 보고서는 AI 보안팀 자동 생성 시스템으로 작성되었습니다.*
