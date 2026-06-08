# service_vuln_check.py — v1.0 — AI 보안팀 영호 담당
# 2단계: 열린 포트별 서비스 취약점 점검
# scan_results.json(1단계 출력)을 읽어 각 서비스를 분석합니다.
# ⚠️ 반드시 승인된 대상에만 사용할 것
import sys, os, json, socket, http.client, datetime, argparse
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
sys.stderr.reconfigure(encoding='utf-8', errors='replace')

CONFIG_FILE   = os.path.join(os.path.dirname(__file__), 'service_vuln_check.json')
SCAN_RESULTS  = os.path.join(os.path.dirname(__file__), 'scan_results.json')
VULN_RESULTS  = os.path.join(os.path.dirname(__file__), 'vuln_results.json')

RISK_HIGH   = '🔴 HIGH'
RISK_MEDIUM = '⚠️  MED'
RISK_LOW    = 'ℹ️  LOW'
RISK_OK     = '✅  OK '

def check_http(host, port, timeout=4):
    findings = []
    try:
        conn = http.client.HTTPConnection(host, port, timeout=timeout)
        conn.request('GET', '/')
        resp = conn.getresponse()
        resp.read()

        server    = resp.getheader('Server', '')
        x_powered = resp.getheader('X-Powered-By', '')
        csp       = resp.getheader('Content-Security-Policy', '')
        xframe    = resp.getheader('X-Frame-Options', '')
        hsts      = resp.getheader('Strict-Transport-Security', '')
        xcontent  = resp.getheader('X-Content-Type-Options', '')
        conn.close()

        if server:    findings.append((RISK_MEDIUM, f'서버 정보 노출 — Server: {server}'))
        if x_powered: findings.append((RISK_MEDIUM, f'기술 스택 노출 — X-Powered-By: {x_powered}'))
        if not csp:   findings.append((RISK_MEDIUM, 'Content-Security-Policy 헤더 없음 (XSS 위험)'))
        if not xframe:findings.append((RISK_MEDIUM, 'X-Frame-Options 헤더 없음 (Clickjacking 위험)'))
        if not hsts:  findings.append((RISK_LOW,    'HSTS 미설정 — HTTPS 미사용 또는 미강제'))
        if not xcontent: findings.append((RISK_LOW, 'X-Content-Type-Options 헤더 없음'))

        # 위험 메서드 확인
        conn2 = http.client.HTTPConnection(host, port, timeout=timeout)
        conn2.request('OPTIONS', '/')
        resp2 = conn2.getresponse()
        allow = resp2.getheader('Allow', '')
        resp2.read(); conn2.close()
        if allow:
            dangerous = [m for m in ['PUT','DELETE','TRACE','CONNECT'] if m in allow]
            if dangerous:
                findings.append((RISK_HIGH, f'위험 HTTP 메서드 허용: {", ".join(dangerous)}'))
            else:
                findings.append((RISK_OK, f'허용 메서드 정상: {allow}'))

        # 관리자·민감 경로 확인
        sensitive = ['/admin','/administrator','/manager','/console','/login',
                     '/.git','/.env','/backup','/phpmyadmin','/wp-admin','/api']
        conn3 = http.client.HTTPConnection(host, port, timeout=timeout)
        for path in sensitive:
            try:
                conn3.request('GET', path)
                r3 = conn3.getresponse(); r3.read()
                if r3.status in (200, 301, 302, 403):
                    risk = RISK_HIGH if r3.status == 200 else RISK_MEDIUM
                    findings.append((risk, f'경로 응답 HTTP {r3.status}: {path}'))
            except: pass
        conn3.close()

    except Exception as e:
        findings.append((RISK_LOW, f'HTTP 연결 실패: {e}'))
    return findings

def check_smb(host, timeout=4):
    findings = []
    try:
        with socket.create_connection((host, 445), timeout=timeout) as s:
            # SMBv1 Negotiate 패킷 전송
            smb1 = bytes.fromhex(
                '000000850000000000000000000000000000000000000000'
                'fffffffffffffe0000000000620002'
                '50432044455441434845442d4e455420574f524b53544154494f4e'
                '00024c414e4d414e312e3000024c4d312e325830303200'
                '024e54204c4d20302e313200025a6200'
            )
            try: s.send(smb1)
            except: pass
            try:
                resp = s.recv(256)
                if b'\xffSMB' in resp or b'\xfeSMB' in resp:
                    if b'\xffSMB' in resp:
                        findings.append((RISK_HIGH, 'SMBv1 활성화 — EternalBlue(MS17-010) 취약점 노출 가능'))
                    else:
                        findings.append((RISK_OK, 'SMBv1 비활성화 (SMB2/3 응답)'))
                else:
                    findings.append((RISK_LOW, 'SMB 응답 불명확 — 수동 확인 필요'))
            except:
                findings.append((RISK_LOW, 'SMB 응답 없음 — 방화벽 차단 가능성'))
    except Exception as e:
        findings.append((RISK_LOW, f'SMB 연결 실패: {e}'))
    return findings

def check_rpc(host, timeout=4):
    findings = []
    try:
        with socket.create_connection((host, 135), timeout=timeout):
            findings.append((RISK_MEDIUM, 'RPC Endpoint Mapper 노출 — 내부 서비스 열거 가능'))
            findings.append((RISK_LOW,    '권고: 외부망에서 135/tcp 방화벽 차단'))
    except Exception as e:
        findings.append((RISK_OK, f'RPC 접근 차단됨: {e}'))
    return findings

SERVICE_CHECKS = {
    80:   ('HTTP',      lambda h,_: check_http(h, 80)),
    8080: ('HTTP-Alt',  lambda h,_: check_http(h, 8080)),
    8443: ('HTTPS-Alt', lambda h,_: check_http(h, 8443)),
    8000: ('HTTP-Dev',  lambda h,_: check_http(h, 8000)),
    443:  ('HTTPS',     lambda h,_: [(RISK_LOW, 'HTTPS — 인증서 만료일·암호화 강도 수동 확인 권장')]),
    445:  ('SMB',       lambda h,_: check_smb(h)),
    135:  ('RPC',       lambda h,_: check_rpc(h)),
    22:   ('SSH',       lambda h,_: [(RISK_MEDIUM, 'SSH 노출 — 키 인증 강제, fail2ban 설정 권장')]),
    3389: ('RDP',       lambda h,_: [(RISK_HIGH,   'RDP 직접 노출 — BlueKeep(CVE-2019-0708) 패치·NLA 강제 필수')]),
    21:   ('FTP',       lambda h,_: [(RISK_HIGH,   'FTP 노출 — 평문 전송, 익명 로그인 허용 여부 즉시 확인')]),
    23:   ('Telnet',    lambda h,_: [(RISK_HIGH,   'Telnet 노출 — 평문 전송, 즉시 비활성화 권고')]),
    5900: ('VNC',       lambda h,_: [(RISK_HIGH,   'VNC 노출 — 비밀번호 없는 접근 허용 여부 확인')]),
    3306: ('MySQL',     lambda h,_: [(RISK_HIGH,   'MySQL 직접 노출 — 외부 접근 차단 및 원격 root 로그인 비활성화')]),
    1433: ('MSSQL',     lambda h,_: [(RISK_HIGH,   'MSSQL 직접 노출 — sa 계정 비활성화, 방화벽 차단 확인')]),
}

def main():
    parser = argparse.ArgumentParser(description='서비스 취약점 점검 (2단계)')
    parser.add_argument('--target', help='대상 호스트')
    parser.add_argument('--ports',  help='콤마 구분 포트 (예: 80,445,135)')
    parser.add_argument('--input',  default=SCAN_RESULTS, help='1단계 결과 JSON')
    parser.add_argument('--output', default=VULN_RESULTS,  help='결과 저장 JSON')
    args = parser.parse_args()

    cfg = {}
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, encoding='utf-8') as f: cfg = json.load(f)

    target     = args.target or cfg.get('target_host', '')
    open_ports = []
    scan_meta  = {}

    if not args.ports and os.path.exists(args.input):
        with open(args.input, encoding='utf-8') as f: scan_meta = json.load(f)
        target     = target or scan_meta.get('target', '')
        open_ports = [p['port'] for p in scan_meta.get('open_ports', [])]
        print(f"ℹ️  1단계 결과 로드: {args.input} ({len(open_ports)}개 포트 감지)")
    elif args.ports:
        open_ports = [int(p.strip()) for p in args.ports.split(',')]

    if not target:
        print("오류: --target 필요"); sys.exit(1)
    if not open_ports:
        print("오류: 포트 목록 없음 — 1단계를 먼저 실행하거나 --ports 지정"); sys.exit(1)

    print(f"\n=== 서비스 취약점 점검 (2단계) | 대상: {target} | {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')} ===")
    print("⚠️  이 점검은 반드시 서면 승인된 범위 내에서만 실행해야 합니다\n")

    all_findings = {}
    for port in sorted(open_ports):
        checker = SERVICE_CHECKS.get(port)
        service = checker[0] if checker else 'Unknown'
        print(f"[Port {port}/{service}]")
        if checker:
            findings = checker[1](target, port)
        else:
            findings = [(RISK_LOW, '자동 점검 미지원 서비스 — 수동 확인 권장')]
        all_findings[str(port)] = {'service': service, 'findings': [{'risk': r, 'desc': d} for r, d in findings]}
        for risk, desc in findings:
            print(f"  {risk} | {desc}")
        print()

    # 요약
    highs = sum(1 for p in all_findings.values() for f in p['findings'] if 'HIGH' in f['risk'])
    meds  = sum(1 for p in all_findings.values() for f in p['findings'] if 'MED'  in f['risk'])
    print(f"=== 점검 완료 | 🔴 HIGH: {highs}건  ⚠️ MED: {meds}건 ===")

    result = {
        'target': target, 'timestamp': datetime.datetime.now().isoformat(),
        'scope': scan_meta.get('scope', cfg.get('scope', '')),
        'approved_by': scan_meta.get('approved_by', cfg.get('approved_by', '')),
        'findings': all_findings,
        'summary': {'high': highs, 'medium': meds}
    }
    with open(args.output, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    print(f"\n✅ 결과 저장 완료: {args.output}")
    print("→ 3단계: exploit_test.py 실행하여 취약점 침투 테스트")

if __name__ == '__main__':
    main()
