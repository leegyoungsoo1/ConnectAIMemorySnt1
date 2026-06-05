# 🐧 Linux 취약점 점검 도구 (광수 담당)

Linux 서버 보안 상태를 점검합니다.

## 실행 방법
```bash
python linux_vuln_check.py --checks all
```

## 점검 항목
- **suid**: SUID 설정 파일 탐색
- **cron**: Cron 작업 목록
- **ssh**: SSH 보안 설정
- **users**: UID=0 계정 및 셸 접근 계정
- **ports**: 열린 포트 (LISTEN)
- **writable**: World-Writable 파일
