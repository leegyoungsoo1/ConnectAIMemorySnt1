# 🪟 Windows 취약점 점검 도구 (영수 담당)

Windows 서버 보안 상태를 점검합니다.

## 실행 방법
```bash
python windows_vuln_check.py --checks all
```

## 점검 항목
- **accounts**: 로컬 계정 정책 (패스워드 복잡도, 잠금 정책)
- **patches**: 최근 윈도우 패치 현황
- **services**: 실행 중인 서비스 목록
- **ports**: LISTENING 상태 포트

## 설정 (windows_vuln_check.json)
```json
{ "target_host": "192.168.1.100" }
```
