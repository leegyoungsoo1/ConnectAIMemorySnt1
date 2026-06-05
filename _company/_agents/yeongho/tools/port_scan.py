# port_scan.py — v1.0 — AI 보안팀 영호 담당
# 포트 스캔 및 서비스 배너 수집 (모의해킹 사전 정찰)
# ⚠️ 반드시 승인된 대상에만 사용할 것
# 사용: python port_scan.py --target 192.168.1.100 [--ports 1-1024] [--timeout 1]
import sys, os, json, socket, datetime, argparse, concurrent.futures
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
sys.stderr.reconfigure(encoding='utf-8', errors='replace')

CONFIG_FILE = os.path.join(os.path.dirname(__file__), 'port_scan.json')

COMMON_PORTS = {
    21: 'FTP', 22: 'SSH', 23: 'Telnet', 25: 'SMTP', 53: 'DNS',
    80: 'HTTP', 110: 'POP3', 143: 'IMAP', 443: 'HTTPS', 445: 'SMB',
    1433: 'MSSQL', 1521: 'Oracle', 3306: 'MySQL', 3389: 'RDP',
    5432: 'PostgreSQL', 5900: 'VNC', 6379: 'Redis', 8080: 'HTTP-Alt',
    8443: 'HTTPS-Alt', 27017: 'MongoDB'
}

def grab_banner(host, port, timeout):
    try:
        with socket.create_connection((host, port), timeout=timeout) as s:
            s.settimeout(timeout)
            try: banner = s.recv(1024).decode('utf-8', errors='ignore').strip()[:100]
            except: banner = ''
            return banner
    except: return ''

def scan_port(host, port, timeout):
    try:
        with socket.create_connection((host, port), timeout=timeout):
            banner = grab_banner(host, port, timeout)
            service = COMMON_PORTS.get(port, 'Unknown')
            return {'port': port, 'state': 'open', 'service': service, 'banner': banner}
    except: return None

def parse_ports(port_str):
    ports = []
    for part in port_str.split(','):
        if '-' in part:
            s, e = part.split('-')
            ports.extend(range(int(s), int(e)+1))
        else:
            ports.append(int(part))
    return ports

def main():
    parser = argparse.ArgumentParser(description='포트 스캔 (모의해킹 사전 정찰)')
    parser.add_argument('--target', help='스캔 대상 IP/호스트')
    parser.add_argument('--ports', default='1-1024', help='포트 범위 (예: 1-1024, 22,80,443)')
    parser.add_argument('--timeout', type=float, default=1.0)
    parser.add_argument('--threads', type=int, default=100)
    args = parser.parse_args()

    cfg = {}
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE) as f: cfg = json.load(f)
    target = args.target or cfg.get('target_host', '')
    if not target:
        print("오류: --target 또는 port_scan.json의 target_host 설정 필요")
        print("⚠️ 반드시 승인된 대상에만 사용하세요")
        sys.exit(1)

    print(f"=== 포트 스캔 (모의해킹 정찰) | 대상: {target} | {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')} ===")
    print("⚠️ 이 스캔은 반드시 서면 승인된 범위 내에서만 실행해야 합니다\n")

    ports = parse_ports(args.ports)
    open_ports = []

    with concurrent.futures.ThreadPoolExecutor(max_workers=args.threads) as executor:
        futures = {executor.submit(scan_port, target, p, args.timeout): p for p in ports}
        for future in concurrent.futures.as_completed(futures):
            result = future.result()
            if result:
                open_ports.append(result)
                print(f"  🔴 {result['port']}/tcp OPEN — {result['service']} {result['banner']}")

    print(f"\n=== 스캔 완료 | 열린 포트: {len(open_ports)}개 ===")
    if open_ports:
        print("\n[위험 평가]")
        risky = [p for p in open_ports if p['port'] in (23, 21, 445, 3389, 5900)]
        for r in risky:
            print(f"  ⚠️ {r['port']} ({r['service']}) — 보안 검토 필요")
    print("\n결과를 영철에게 전달해 체크리스트 작성 요청")

if __name__ == '__main__':
    main()
