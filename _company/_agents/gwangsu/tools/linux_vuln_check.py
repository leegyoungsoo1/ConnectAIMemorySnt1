# linux_vuln_check.py — v1.0 — AI 보안팀 광수 담당
# Linux 서버 취약점 점검 스크립트
# 사용: python linux_vuln_check.py [--checks all|suid|cron|ssh|users|ports]
import sys, os, json, subprocess, datetime, argparse
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
sys.stderr.reconfigure(encoding='utf-8', errors='replace')

CONFIG_FILE = os.path.join(os.path.dirname(__file__), 'linux_vuln_check.json')

def run_cmd(cmd, timeout=15):
    try:
        r = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=timeout)
        return r.stdout.strip() or r.stderr.strip()
    except Exception as e:
        return f"오류: {e}"

def check_suid():
    out = run_cmd("find / -perm -4000 -type f 2>/dev/null | head -30")
    return {'check': 'SUID 파일', 'output': out or '없음', 'status': 'collected'}

def check_cron():
    out = run_cmd("crontab -l 2>/dev/null; ls /etc/cron* /var/spool/cron 2>/dev/null")
    return {'check': 'Cron 작업', 'output': out or '없음', 'status': 'collected'}

def check_ssh_config():
    out = run_cmd("grep -E 'PermitRootLogin|PasswordAuthentication|Port|AllowUsers' /etc/ssh/sshd_config 2>/dev/null")
    return {'check': 'SSH 설정', 'output': out or '파일 없음', 'status': 'collected'}

def check_users():
    out = run_cmd("awk -F: '$3==0{print $1}' /etc/passwd")
    out2 = run_cmd("cat /etc/passwd | awk -F: '$7~/sh$/{print $1": "$7}'")
    return {'check': 'UID=0 계정 + 쉘 계정', 'output': f"UID0: {out}\n쉘 계정:\n{out2}", 'status': 'collected'}

def check_ports():
    out = run_cmd("ss -tlnp 2>/dev/null || netstat -tlnp 2>/dev/null")
    return {'check': '열린 포트 (LISTEN)', 'output': out, 'status': 'collected'}

def check_world_writable():
    out = run_cmd("find /etc /usr /bin -perm -0002 -type f 2>/dev/null | head -20")
    return {'check': 'World-Writable 파일', 'output': out or '없음', 'status': 'collected'}

def main():
    parser = argparse.ArgumentParser(description='Linux 서버 취약점 점검')
    parser.add_argument('--checks', default='all')
    args = parser.parse_args()

    cfg = {}
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, encoding='utf-8') as f: cfg = json.load(f)

    print(f"=== Linux 취약점 점검 | {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')} ===")
    checks = args.checks.lower()
    results = []
    if checks in ('all', 'suid'):  results.append(check_suid())
    if checks in ('all', 'cron'):  results.append(check_cron())
    if checks in ('all', 'ssh'):   results.append(check_ssh_config())
    if checks in ('all', 'users'): results.append(check_users())
    if checks in ('all', 'ports'): results.append(check_ports())
    if checks in ('all', 'writable'): results.append(check_world_writable())

    for r in results:
        print(f"\n[✅ {r['check']}]\n{r['output']}")

    print("\n=== 점검 완료. 결과를 영철에게 전달해 체크리스트 작성 요청 ===")

if __name__ == '__main__':
    main()
