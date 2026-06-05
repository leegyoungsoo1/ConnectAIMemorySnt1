# windows_vuln_check.py — v1.0 — AI 보안팀 영수 담당
# Windows 서버 취약점 점검 스크립트 (로컬 실행 또는 원격 WMI)
# 사용: python windows_vuln_check.py [--target 192.168.1.100] [--checks all|accounts|patches|services]
import sys, os, json, subprocess, datetime, argparse
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
sys.stderr.reconfigure(encoding='utf-8', errors='replace')

CONFIG_FILE = os.path.join(os.path.dirname(__file__), 'windows_vuln_check.json')

def load_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def check_accounts():
    """로컬 계정 정책 점검"""
    results = []
    try:
        r = subprocess.run(['net', 'accounts'], capture_output=True, text=True, timeout=10)
        results.append({'check': '계정 정책', 'output': r.stdout.strip(), 'status': 'collected'})
    except Exception as e:
        results.append({'check': '계정 정책', 'error': str(e), 'status': 'failed'})
    return results

def check_patches():
    """최근 패치 현황"""
    results = []
    try:
        r = subprocess.run(
            ['powershell', '-Command', 'Get-HotFix | Sort-Object InstalledOn -Descending | Select-Object -First 10 | Format-List'],
            capture_output=True, text=True, timeout=30
        )
        results.append({'check': '최근 패치', 'output': r.stdout.strip(), 'status': 'collected'})
    except Exception as e:
        results.append({'check': '최근 패치', 'error': str(e), 'status': 'failed'})
    return results

def check_open_services():
    """실행 중인 서비스 목록"""
    results = []
    try:
        r = subprocess.run(
            ['powershell', '-Command', 'Get-Service | Where-Object {$_.Status -eq "Running"} | Select-Object Name,DisplayName | Format-Table -AutoSize'],
            capture_output=True, text=True, timeout=30
        )
        results.append({'check': '실행 중 서비스', 'output': r.stdout.strip(), 'status': 'collected'})
    except Exception as e:
        results.append({'check': '실행 중 서비스', 'error': str(e), 'status': 'failed'})
    return results

def check_open_ports():
    """열린 포트 확인"""
    results = []
    try:
        r = subprocess.run(
            ['powershell', '-Command', 'netstat -ano | findstr LISTENING'],
            capture_output=True, text=True, timeout=15
        )
        results.append({'check': '열린 포트 (LISTENING)', 'output': r.stdout.strip(), 'status': 'collected'})
    except Exception as e:
        results.append({'check': '열린 포트', 'error': str(e), 'status': 'failed'})
    return results

def main():
    parser = argparse.ArgumentParser(description='Windows 서버 취약점 점검')
    parser.add_argument('--checks', default='all', help='all|accounts|patches|services|ports')
    args = parser.parse_args()

    cfg = load_config()
    target = cfg.get('target_host', 'localhost')
    print(f"=== Windows 취약점 점검 | 대상: {target} | {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')} ===")

    all_results = []
    checks = args.checks.lower()

    if checks in ('all', 'accounts'): all_results += check_accounts()
    if checks in ('all', 'patches'):  all_results += check_patches()
    if checks in ('all', 'services'): all_results += check_open_services()
    if checks in ('all', 'ports'):    all_results += check_open_ports()

    for r in all_results:
        status = '✅' if r.get('status') == 'collected' else '❌'
        print(f"\n[{status} {r['check']}]")
        if 'output' in r: print(r['output'])
        if 'error' in r:  print(f"오류: {r['error']}")

    print("\n=== 점검 완료. 위 결과를 영철에게 전달해 체크리스트 작성 요청 ===")

if __name__ == '__main__':
    main()
