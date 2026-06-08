# generate_report.py — v1.0 — AI 보안팀 영호 담당
# 4단계: 모의해킹 최종 보고서 생성
# 1~3단계 JSON 결과를 종합해 마크다운 보고서를 작성하고 영철에게 전달합니다.
import sys, os, json, datetime, argparse
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
sys.stderr.reconfigure(encoding='utf-8', errors='replace')

TOOLS_DIR       = os.path.dirname(__file__)
CONFIG_FILE     = os.path.join(TOOLS_DIR, 'generate_report.json')
SCAN_RESULTS    = os.path.join(TOOLS_DIR, 'scan_results.json')
VULN_RESULTS    = os.path.join(TOOLS_DIR, 'vuln_results.json')
EXPLOIT_RESULTS = os.path.join(TOOLS_DIR, 'exploit_results.json')
REPORTS_DIR     = os.path.join(os.path.dirname(TOOLS_DIR), 'reports')

CVSS_MAP = {
    '🔴 VULNERABLE': ('Critical/High', '즉시 조치 필요'),
    '⚠️  LIKELY   ':  ('Medium',        '조속한 조치 권고'),
    '🔴 HIGH':        ('High',           '즉시 조치 필요'),
    '⚠️  MED':        ('Medium',         '조속한 조치 권고'),
    'ℹ️  LOW':         ('Low',            '일정 내 조치'),
    '✅ SAFE     ':   ('None',           '정상'),
    '✅  OK ':         ('None',           '정상'),
    'ℹ️  MANUAL   ':  ('Info',           '수동 확인 권고'),
}

def load_json(path):
    if os.path.exists(path):
        with open(path, encoding='utf-8') as f:
            return json.load(f)
    return {}

def severity_order(risk_str):
    order = {'Critical/High': 0, 'High': 1, 'Medium': 2, 'Low': 3, 'Info': 4, 'None': 5}
    for k in CVSS_MAP:
        if k in risk_str:
            return order.get(CVSS_MAP[k][0], 9)
    return 9

def main():
    parser = argparse.ArgumentParser(description='모의해킹 보고서 생성 (4단계)')
    parser.add_argument('--target',  help='대상 호스트 (자동 감지 가능)')
    parser.add_argument('--tester',  help='테스터 이름', default='영호')
    parser.add_argument('--output',  help='보고서 저장 경로 (기본: reports/)')
    args = parser.parse_args()

    cfg = {}
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, encoding='utf-8') as f: cfg = json.load(f)

    scan    = load_json(SCAN_RESULTS)
    vuln    = load_json(VULN_RESULTS)
    exploit = load_json(EXPLOIT_RESULTS)

    target   = args.target or exploit.get('target') or vuln.get('target') or scan.get('target') or cfg.get('target_host', '알 수 없음')
    scope    = exploit.get('scope') or vuln.get('scope') or scan.get('scope') or cfg.get('scope', '')
    approved = exploit.get('approved_by') or cfg.get('approved_by', '')
    tester   = args.tester or cfg.get('tester', '영호')
    now      = datetime.datetime.now()

    os.makedirs(REPORTS_DIR, exist_ok=True)
    report_name = f"pentest_report_{now.strftime('%Y%m%d_%H%M')}.md"
    report_path = args.output or os.path.join(REPORTS_DIR, report_name)

    # ── 결과 수집 ──
    open_ports = scan.get('open_ports', [])
    vuln_findings = vuln.get('findings', {})
    exploit_results = exploit.get('exploit_results', {})

    all_issues = []  # (severity_rank, port, service, risk_label, description)
    for port_str, data in vuln_findings.items():
        svc = data.get('service', '')
        for f in data.get('findings', []):
            risk = f.get('risk', '')
            all_issues.append((severity_order(risk), port_str, svc, risk, f.get('desc', '')))
    for port_str, data in exploit_results.items():
        svc = data.get('service', '')
        for c in data.get('checks', []):
            risk = c.get('risk', '')
            if 'SAFE' not in risk and 'OK' not in risk:
                all_issues.append((severity_order(risk), port_str, svc, risk, f"[침투검증] {c.get('desc', '')}"))

    all_issues.sort(key=lambda x: x[0])

    critical = [i for i in all_issues if i[0] <= 1]
    medium   = [i for i in all_issues if i[0] == 2]
    low      = [i for i in all_issues if i[0] >= 3 and 'SAFE' not in i[3] and 'OK' not in i[3]]

    # ── 보고서 작성 ──
    lines = []
    lines.append(f"# 모의해킹(Pentest) 결과 보고서")
    lines.append(f"")
    lines.append(f"| 항목 | 내용 |")
    lines.append(f"|------|------|")
    lines.append(f"| 대상 | `{target}` |")
    lines.append(f"| 범위 | {scope} |")
    lines.append(f"| 테스터 | {tester} |")
    lines.append(f"| 승인자 | {approved} |")
    lines.append(f"| 점검일 | {now.strftime('%Y-%m-%d %H:%M')} |")
    lines.append(f"")
    lines.append(f"---")
    lines.append(f"")
    lines.append(f"## 요약 (Executive Summary)")
    lines.append(f"")
    lines.append(f"- 열린 포트: **{len(open_ports)}개**")
    lines.append(f"- 🔴 Critical/High 위험: **{len(critical)}건** — 즉시 조치 필요")
    lines.append(f"- ⚠️  Medium 위험: **{len(medium)}건** — 조속히 조치 권고")
    lines.append(f"- ℹ️  Low/Info: **{len(low)}건** — 일정 내 조치")
    lines.append(f"")

    if open_ports:
        lines.append(f"---")
        lines.append(f"")
        lines.append(f"## 1단계 — 정찰 (포트 스캔)")
        lines.append(f"")
        lines.append(f"| 포트 | 서비스 | 배너 |")
        lines.append(f"|------|--------|------|")
        for p in open_ports:
            lines.append(f"| {p['port']}/tcp | {p.get('service','?')} | {p.get('banner','')[:60]} |")
        lines.append(f"")

    if vuln_findings:
        lines.append(f"---")
        lines.append(f"")
        lines.append(f"## 2단계 — 서비스 취약점 점검")
        lines.append(f"")
        for port_str, data in sorted(vuln_findings.items(), key=lambda x: int(x[0])):
            lines.append(f"### Port {port_str} — {data.get('service','')}")
            lines.append(f"")
            for f in data.get('findings', []):
                lines.append(f"- {f.get('risk','')} | {f.get('desc','')}")
            lines.append(f"")

    if exploit_results:
        lines.append(f"---")
        lines.append(f"")
        lines.append(f"## 3단계 — 침투 검증")
        lines.append(f"")
        for port_str, data in sorted(exploit_results.items(), key=lambda x: int(x[0])):
            lines.append(f"### {data.get('service', f'Port {port_str}')}")
            lines.append(f"")
            for c in data.get('checks', []):
                lines.append(f"- {c.get('risk','')} | {c.get('desc','')}")
            lines.append(f"")

    lines.append(f"---")
    lines.append(f"")
    lines.append(f"## 조치 우선순위 (영철 체크리스트용)")
    lines.append(f"")
    if critical:
        lines.append(f"### 🔴 즉시 조치 (Critical/High)")
        lines.append(f"")
        for _, port, svc, risk, desc in critical:
            lines.append(f"- [ ] **[Port {port}/{svc}]** {desc}")
        lines.append(f"")
    if medium:
        lines.append(f"### ⚠️ 조속 조치 (Medium)")
        lines.append(f"")
        for _, port, svc, risk, desc in medium:
            lines.append(f"- [ ] [Port {port}/{svc}] {desc}")
        lines.append(f"")
    if low:
        lines.append(f"### ℹ️ 일정 내 조치 (Low/Info)")
        lines.append(f"")
        for _, port, svc, risk, desc in low:
            lines.append(f"- [ ] [Port {port}/{svc}] {desc}")
        lines.append(f"")

    lines.append(f"---")
    lines.append(f"")
    lines.append(f"_본 보고서는 서면 승인된 범위 내에서 수행된 모의해킹 결과입니다._")
    lines.append(f"_영호(모의해킹 담당) → 영철(취약점 취합 담당)에게 전달_")

    report_content = '\n'.join(lines)
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(report_content)

    print(f"=== 보고서 생성 완료 ===")
    print(f"")
    print(f"  대상: {target}")
    print(f"  🔴 Critical/High: {len(critical)}건")
    print(f"  ⚠️  Medium:        {len(medium)}건")
    print(f"  ℹ️  Low/Info:      {len(low)}건")
    print(f"")
    print(f"✅ 보고서 저장: {report_path}")
    print(f"→ 영철에게 전달: 위 보고서의 '조치 우선순위' 섹션을 체크리스트로 활용")

if __name__ == '__main__':
    main()
