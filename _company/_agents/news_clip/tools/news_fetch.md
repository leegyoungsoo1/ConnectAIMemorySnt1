# 📰 IT 뉴스 RSS 클리핑

국내외 IT RSS 피드에서 최신 뉴스를 수집하고, goal.md 양식에 맞는 데일리 보고서 초안을 생성합니다.

**API 키 불필요** — Python 표준 라이브러리만 사용합니다.

## 수집 소스 (기본값)

| 구분 | 피드 |
|------|------|
| 국내 | ZDNet Korea, IT조선, 전자신문 |
| 해외 | TechCrunch, The Verge, Wired, Ars Technica, Hacker News |

## 실행 방법

```bash
python news_fetch.py
python news_fetch.py --count 15 --output my_report.md
```

## 출력 파일

- `news_latest.md` — goal.md 양식의 보고서 초안 (에이전트가 요약 보완)
- `news_latest.json` — 원본 데이터 (제목·출처·링크·점수)

## 설정 (news_fetch.json)

- `count` — 보고서에 포함할 뉴스 개수 (기본 10)
- `feeds` — RSS 피드 목록 추가/제거 가능 (`name`, `url`, `lang` 필드)

## 스코어링 기준

AI·보안·반도체·빅테크 등 핫 키워드 + 발행 시간 신선도로 자동 순위 산정합니다.
