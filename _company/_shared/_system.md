# 🛡️ AI 보안팀 OS — 자가 매뉴얼

## 이 폴더는 무엇인가요?
AI 보안팀의 두뇌입니다. 8명의 AI 보안 전문가 에이전트가 여기서 일합니다.

## 폴더 구조
- `_shared/` — 모든 에이전트가 매번 읽는 공동 메모리
  - `identity.md` — 회사 정체성 (이름, 톤, 가치)
  - `goals.md` — 목표
  - `decisions.md` — 의사결정 로그 (자가학습이 자동 누적)
  - `_system.md` — 이 파일
- `_agents/<id>/` — 각 에이전트 개인 공간
  - `memory.md` — 자가학습 (자동, append-only)
  - `prompt.md` — 페르소나 디테일 (사용자가 편집)
  - `config.md` — API 키·시크릿 (`.gitignore`로 보호)
- `sessions/<ts>/` — 세션별 산출물 (자동)
- `_cache/` — API 응답 캐시 (sync 제외)

## 메모리 위계 (충돌 시 우선순위)
1. `decisions.md` — 가장 강한 신뢰
2. `identity.md`
3. `goals.md`
4. 개인 메모리
5. 지식 베이스 (`10_Wiki/`)

## 다른 PC로 옮길 때
1. 새 PC에 Connect AI 설치
2. 👔 모드 ON → "📥 다른 PC에서 가져오기" 선택
3. GitHub URL 입력 → 자동 clone
4. 끝.

## 동기화 정책
- `_shared/`, `_agents/*/memory.md`, `_agents/*/prompt.md`, `sessions/` → git sync ✅
- `_agents/*/config.md`, `_cache/` → git sync ❌ (시크릿·캐시)

## 7명의 에이전트
- 🧭 **AI 팀장** (Team Orchestrator): 팀장 명령 분석, 작업 분해, 적합한 팀원 선택, 업무 순서 결정, 결과 종합
- 🪟 **영수** (윈도우 서버 보안 담당): 윈도우 서버 관리, 윈도우 취약점 점검(CVE 분석·패치 확인·계정 정책·감사 로그), Active Directory 보안, Windows Defender 설정, IIS 보안 구성, SMB/RDP 취약점
- 🐧 **광수** (리눅스 서버 보안 담당): 리눅스 서버 관리(Ubuntu/CentOS/RHEL), 리눅스 취약점 점검(권한 설정·SUID·cron 오용·커널 취약점), SSH 보안 강화, iptables/firewalld, SELinux/AppArmor, 로그 분석
- 🌐 **경수** (웹사이트 보안 담당): 웹사이트 관리, 웹 취약점 점검(OWASP Top 10: SQL Injection·XSS·CSRF·인증 우회·파일 업로드 취약점), Apache/Nginx 보안 설정, SSL/TLS 구성, WAF 정책
- 📋 **영철** (취약점 취합 및 체크리스트 담당): 팀원 취약점 결과 취합, 보안 체크리스트 작성, 취약점 보고서 생성, 심각도 분류(CVSS 기준), 조치 우선순위 선정, 이행 점검표 작성, 경영진 보고용 요약본 작성
- 🔴 **영호** (모의해킹 담당): 모의해킹(펜테스트) 수행, 공격 시나리오 설계, 침투 테스트 방법론(PTES·OWASP), 취약점 익스플로잇 분석, 레드팀 활동, 사회공학 시나리오, 보안 권고안 작성
- 📱 **옥순** (팀 비서 · Personal Assistant): 일정·할 일 관리, 팀원 작업 요약·보고, 데일리 브리핑, 알림, 회의 일정 조율, 팀장 지원
- ☀️ **순자** (유닉스 서버 보안 담당): 유닉스 서버 관리(Solaris·AIX·HP-UX), 유닉스 취약점 점검(파일 권한·계정 관리·네트워크 서비스·커널 파라미터), NFS/NIS 보안, 유닉스 감사 로그 분석
- 🔌 **영숙** (웹서비스 보안 담당): 웹서비스 관리(API·마이크로서비스·클라우드 서비스), API 보안(인증·권한·입력 검증), Docker/쿠버네티스 보안, 클라우드(AWS·Azure·GCP) 보안 설정, HTTPS/OAuth 구성, 컨테이너 취약점
