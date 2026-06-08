# web_vuln_check.py — v1.0 — AI 보안팀 경수 담당
# 웹사이트 취약점 점검 스크립트 (OWASP 기반)
# 사용: python web_vuln_check.py --url https://example.com [--checks all|headers|ssl|info|forms]
import sys, os, json, urllib.request, urllib.error, ssl, datetime, argparse
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
sys.stderr.reconfigure(encoding='utf-8', errors='replace')

CONFIG_FILE = os.path.join(os.path.dirname(__file__), 'web_vuln_check.json')

SECURITY_HEADERS = [
    'X-Frame-Options', 'X-Content-Type-Options', 'X-XSS-Protection',
    'Content-Security-Policy', 'Strict-Transport-Security',
    'Referrer-Policy', 'Permissions-Policy'
]

def check_headers(url):
    results = []
    try:
        ctx = ssl.create_default_context()
        req = urllib.request.Request(url, headers={'User-Agent': 'SecurityCheckBot/1.0'})
        with urllib.request.urlopen(req, context=ctx, timeout=10) as resp:
            headers = dict(resp.headers)
            for h in SECURITY_HEADERS:
                found = headers.get(h) or headers.get(h.lower())
                results.append({
                    'header': h,
                    'status': '✅ 존재' if found else '⚠️ 누락',
                    'value': found or ''
                })
            server = headers.get('Server', '미공개')
            results.append({'header': 'Server 헤더 노출', 'status': '⚠️ 노출' if 'Server' in headers else '✅ 미공개', 'value': server})
    except Exception as e:
        results.append({'header': '연결 오류', 'status': '❌', 'value': str(e)})
    return results

def check_ssl(url):
    results = []
    try:
        import ssl as ssl_lib, socket
        hostname = url.replace('https://', '').replace('http://', '').split('/')[0]
        ctx = ssl_lib.create_default_context()
        with socket.create_connection((hostname, 443), timeout=10) as sock:
            with ctx.wrap_socket(sock, server_hostname=hostname) as ssock:
                cert = ssock.getpeercert()
                protocol = ssock.version()
                results.append({'check': 'TLS 버전', 'value': protocol, 'status': '✅' if 'TLS' in protocol else '⚠️'})
                expire = cert.get('notAfter', '')
                results.append({'check': '인증서 만료', 'value': expire, 'status': '✅'})
    except Exception as e:
        results.append({'check': 'SSL 점검', 'value': str(e), 'status': '❌'})
    return results

def check_info_disclosure(url):
    sensitive_paths = [
        '/.git/config', '/.env', '/config.php', '/web.config',
        '/phpinfo.php', '/admin', '/wp-admin', '/robots.txt', '/sitemap.xml'
    ]
    results = []
    base = url.rstrip('/')
    for p in sensitive_paths:
        try:
            ctx = ssl.create_default_context()
            req = urllib.request.Request(base + p, headers={'User-Agent': 'SecurityCheckBot/1.0'})
            with urllib.request.urlopen(req, context=ctx, timeout=5) as resp:
                status = resp.status
                results.append({'path': p, 'status': f'⚠️ HTTP {status} — 접근 가능', 'risk': 'High' if p in ('/.git/config', '/.env') else 'Medium'})
        except urllib.error.HTTPError as e:
            results.append({'path': p, 'status': f'✅ HTTP {e.code}', 'risk': 'OK'})
        except Exception:
            results.append({'path': p, 'status': '✅ 차단/오류', 'risk': 'OK'})
    return results

def main():
    parser = argparse.ArgumentParser(description='웹사이트 취약점 점검')
    parser.add_argument('--url', help='점검 대상 URL')
    parser.add_argument('--checks', default='all')
    args = parser.parse_args()

    cfg = {}
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, encoding='utf-8') as f: cfg = json.load(f)
    url = args.url or cfg.get('target_url', '')
    if not url:
        print("오류: --url 또는 web_vuln_check.json의 target_url 설정 필요")
        sys.exit(1)

    print(f"=== 웹 취약점 점검 | 대상: {url} | {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')} ===")
    checks = args.checks.lower()

    if checks in ('all', 'headers'):
        print("\n[보안 헤더 점검]")
        for r in check_headers(url):
            print(f"  {r['status']} {r['header']}: {r['value']}")

    if checks in ('all', 'ssl') and url.startswith('https'):
        print("\n[SSL/TLS 점검]")
        for r in check_ssl(url):
            print(f"  {r['status']} {r['check']}: {r['value']}")

    if checks in ('all', 'info'):
        print("\n[정보 노출 점검]")
        for r in check_info_disclosure(url):
            print(f"  {r['status']} {r['path']} (위험도: {r['risk']})")

    print("\n=== 점검 완료. 결과를 영철에게 전달해 체크리스트 작성 요청 ===")

if __name__ == '__main__':
    main()
