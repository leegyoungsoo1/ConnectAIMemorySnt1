# news_fetch.py — v1.0 — 데일리 IT 핫이슈 뉴스 클리핑
# RSS 피드에서 국내외 IT 뉴스를 수집하여 보고서 형식으로 저장
# API 키 불필요 — Python 표준 라이브러리만 사용
# 사용: python news_fetch.py [--count 10] [--output report.md]
import sys, os, json, datetime, argparse, html, re, ssl
import urllib.request, urllib.error
import xml.etree.ElementTree as ET

# Windows Python 환경에서 기업 CA/루트 인증서 문제 우회
_SSL_CTX = ssl.create_default_context()
_SSL_CTX.check_hostname = False
_SSL_CTX.verify_mode = ssl.CERT_NONE
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
sys.stderr.reconfigure(encoding='utf-8', errors='replace')

CONFIG_FILE = os.path.join(os.path.dirname(__file__), 'news_fetch.json')

DEFAULT_FEEDS = [
    # 국내 IT
    {"name": "ZDNet Korea",      "url": "https://www.zdnet.co.kr/rss/news/",             "lang": "ko"},
    {"name": "Bloter",           "url": "https://www.bloter.net/feed",                    "lang": "ko"},
    {"name": "전자신문",          "url": "https://www.etnews.com/rss/",                    "lang": "ko"},
    # 해외 IT
    {"name": "TechCrunch",       "url": "https://techcrunch.com/feed/",                   "lang": "en"},
    {"name": "The Verge",        "url": "https://www.theverge.com/rss/index.xml",         "lang": "en"},
    {"name": "Wired",            "url": "https://www.wired.com/feed/rss",                 "lang": "en"},
    {"name": "Ars Technica",     "url": "https://feeds.arstechnica.com/arstechnica/index", "lang": "en"},
    {"name": "Hacker News (Top)","url": "https://hnrss.org/frontpage?count=20",           "lang": "en"},
]

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (compatible; NewsBot/1.0)',
    'Accept': 'application/rss+xml, application/xml, text/xml, */*',
}

def _strip_html(text: str) -> str:
    text = html.unescape(text or '')
    text = re.sub(r'<[^>]+>', '', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text[:300]

def _fetch_feed(feed: dict, timeout: int = 10) -> list:
    items = []
    try:
        req = urllib.request.Request(feed['url'], headers=HEADERS)
        with urllib.request.urlopen(req, timeout=timeout, context=_SSL_CTX) as resp:
            raw = resp.read()
        root = ET.fromstring(raw)
        # RSS 2.0
        for item in root.findall('.//item')[:15]:
            title = _strip_html(item.findtext('title', ''))
            desc  = _strip_html(item.findtext('description', '') or item.findtext('summary', ''))
            link  = (item.findtext('link', '') or '').strip()
            pub   = item.findtext('pubDate', '') or item.findtext('published', '')
            if title:
                items.append({'source': feed['name'], 'lang': feed['lang'],
                              'title': title, 'desc': desc, 'link': link, 'pub': pub})
        # Atom
        ns = {'atom': 'http://www.w3.org/2005/Atom'}
        for entry in root.findall('atom:entry', ns)[:15]:
            title = _strip_html(entry.findtext('atom:title', '', ns))
            summary = _strip_html(entry.findtext('atom:summary', '', ns) or entry.findtext('atom:content', '', ns))
            link_el = entry.find('atom:link', ns)
            link = link_el.get('href', '') if link_el is not None else ''
            pub = entry.findtext('atom:published', '', ns) or entry.findtext('atom:updated', '', ns)
            if title:
                items.append({'source': feed['name'], 'lang': feed['lang'],
                              'title': title, 'desc': summary, 'link': link, 'pub': pub})
    except Exception as e:
        print(f"  ⚠️  {feed['name']} 피드 실패: {e}")
    return items

def _score_item(item: dict) -> int:
    """IT 관련도 점수 — 키워드 가중치 기반."""
    HOT_KW = ['AI', '인공지능', 'GPT', 'LLM', '클라우드', '보안', '해킹', '반도체', '애플', '구글',
              '마이크로소프트', '삼성', '오픈AI', '테슬라', '로봇', '양자컴퓨터', '메타버스',
              'chatgpt', 'openai', 'nvidia', 'apple', 'google', 'microsoft', 'cybersecurity',
              'breach', 'exploit', 'semiconductor', 'quantum', 'robot', 'autonomous', 'cloud']
    text = (item['title'] + ' ' + item['desc']).lower()
    score = 0
    for kw in HOT_KW:
        if kw.lower() in text:
            score += 2
    # 최신 뉴스 보너스
    if item.get('pub'):
        try:
            from email.utils import parsedate_to_datetime
            pub_dt = parsedate_to_datetime(item['pub'])
            age_h = (datetime.datetime.now(pub_dt.tzinfo) - pub_dt).total_seconds() / 3600
            if age_h < 6:   score += 5
            elif age_h < 24: score += 3
            elif age_h < 48: score += 1
        except Exception:
            pass
    return score

def build_report(items: list, count: int, date_str: str) -> str:
    lines = [
        f"# 📅 데일리 IT 핫이슈 뉴스 클리핑 보고서",
        f"*{date_str} — 가장 뜨거운 IT 뉴스 {count}가지를 요약하여 보고합니다.*",
        "",
        "---",
        "",
    ]
    for i, item in enumerate(items[:count], 1):
        title = item['title']
        desc  = item['desc'] or "(본문 미제공)"
        src   = item['source']
        link  = item['link']
        lines.append(f"## {i}. {title}")
        lines.append(f"- **출처:** {src}")
        lines.append(f"- **핵심 요약:** {desc}")
        if link:
            lines.append(f"- **링크:** {link}")
        lines.append(f"- **주요 포인트:**")
        lines.append(f"  - *(이 항목은 에이전트가 요약합니다)*")
        lines.append("")
    lines += [
        "---",
        f"*오늘의 IT 뉴스 보고를 마칩니다.*",
    ]
    return '\n'.join(lines)

def main():
    parser = argparse.ArgumentParser(description='IT 뉴스 RSS 클리핑')
    parser.add_argument('--count', type=int, default=10, help='수집할 뉴스 개수')
    parser.add_argument('--output', default=os.path.join(os.path.dirname(__file__), 'news_latest.md'),
                        help='결과 저장 마크다운')
    parser.add_argument('--timeout', type=int, default=10, help='피드 요청 타임아웃(초)')
    args = parser.parse_args()

    cfg = {}
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, encoding='utf-8') as f: cfg = json.load(f)
        except Exception: pass

    feeds = cfg.get('feeds') or DEFAULT_FEEDS
    count = cfg.get('count') or args.count
    date_str = datetime.datetime.now().strftime('%Y년 %m월 %d일')

    print(f"=== IT 뉴스 클리핑 | {date_str} ===\n")
    all_items = []
    for feed in feeds:
        print(f"  📡 {feed['name']} 수집 중...")
        items = _fetch_feed(feed, timeout=args.timeout)
        print(f"     → {len(items)}건")
        all_items.extend(items)

    # 중복 제목 제거
    seen = set()
    unique = []
    for it in all_items:
        key = it['title'][:60].lower()
        if key not in seen:
            seen.add(key)
            unique.append(it)

    # 점수 정렬
    unique.sort(key=_score_item, reverse=True)

    print(f"\n📊 총 {len(unique)}건 수집 → 상위 {count}건 선정")
    report = build_report(unique, count, date_str)

    with open(args.output, 'w', encoding='utf-8') as f:
        f.write(report)
    print(f"✅ 보고서 저장: {args.output}")

    # JSON 결과도 저장 (에이전트가 읽어서 요약 가능)
    json_out = args.output.replace('.md', '.json')
    with open(json_out, 'w', encoding='utf-8') as f:
        json.dump({
            'date': date_str,
            'generated_at': datetime.datetime.now().isoformat(),
            'total_fetched': len(unique),
            'top_items': unique[:count]
        }, f, ensure_ascii=False, indent=2)
    print(f"✅ JSON 결과: {json_out}")
    print(f"\n→ 다음 단계: 에이전트가 news_latest.json을 읽고 goal.md 양식으로 최종 보고서 작성")

if __name__ == '__main__':
    main()
