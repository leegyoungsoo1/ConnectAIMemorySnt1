# 🌐 웹 취약점 점검 도구 (경수 담당)

웹사이트 보안 취약점을 점검합니다 (OWASP 기반).

## 실행 방법
```bash
python web_vuln_check.py --url https://example.com --checks all
```

## 점검 항목
- **headers**: 보안 헤더 누락 여부 (CSP, HSTS, X-Frame-Options 등)
- **ssl**: TLS 버전, 인증서 만료일
- **info**: 민감 경로 노출 (.env, .git/config, phpinfo.php 등)

## 설정 (web_vuln_check.json)
```json
{ "target_url": "https://example.com" }
```
