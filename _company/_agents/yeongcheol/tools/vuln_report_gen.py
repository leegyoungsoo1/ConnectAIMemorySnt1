# vuln_report_gen.py — v1.0 — AI 보안팀 영철 담당
# 취약점 점검 결과 취합 및 체크리스트/보고서 자동 생성
# 사용: python vuln_report_gen.py --input vuln_results.json [--output report.md]
import sys, os, json, datetime, argparse
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
sys.stderr.reconfigure(encoding='utf-8', errors='replace')

CONFIG_FILE = os.path.join(os.path.dirname(__file__), 'vuln_report_gen.json')

SEVERITY_ORDER = {'Critical': 0, 'High': 1, 'Medium': 2, 'Low': 3, 'Info': 4}

CHECKLIST_TEMPLATE = """# 🛡️ 보안 취약점 점검 결과 보고서

**점검 일시**: {date}
**대상 시스템**: {targets}
**작성자**: 영철 (AI 보안팀)

---

## 📊 요약

| 심각도 | 건수 |
|--------|------|
| 🔴 Critical | {cnt_critical} |
| 🟠 High | {cnt_high} |
| 🟡 Medium | {cnt_medium} |
| 🟢 Low | {cnt_low} |
| ℹ️ Info | {cnt_info} |
| **합계** | **{cnt_total}** |

---

## 📋 취약점 목록 (심각도 순)

{vuln_list}

---

## ✅ 조치 체크리스트

{checklist}

---

## 📝 경영진 요약

본 점검 결과 총 {cnt_total}건의 취약점이 발견되었으며,
즉시 조치가 필요한 Critical/High 취약점은 {cnt_urgent}건입니다.

---
*이 보고서는 AI 보안팀 자동 생성 시스템으로 작성되었습니다.*
"""

def load_sample_results():
    """입력 파일 없을 때 샘플 데이터"""
    return [
        {"id": "V-001", "target": "web-server-01", "type": "웹 취약점", "title": "SQL Injection 취약점", "severity": "High", "description": "로그인 폼에서 SQL Injection 가능", "remediation": "PreparedStatement 사용, 입력값 검증"},
        {"id": "V-002", "target": "win-server-01", "type": "윈도우 취약점", "title": "RDP 포트 외부 노출", "severity": "Medium", "description": "3389 포트가 외부에서 접근 가능", "remediation": "방화벽 정책으로 내부망 접근만 허용"},
        {"id": "V-003", "target": "linux-server-01", "type": "리눅스 취약점", "title": "SSH 루트 로그인 허용", "severity": "High", "description": "PermitRootLogin yes 설정", "remediation": "sshd_config: PermitRootLogin no 설정 후 재시작"},
    ]

def generate_report(vulns, output_path):
    by_severity = {}
    for v in vulns:
        s = v.get('severity', 'Info')
        if s not in by_severity: by_severity[s] = []
        by_severity[s].append(v)

    def count(s): return len(by_severity.get(s, []))

    vuln_lines = []
    for sev in ['Critical', 'High', 'Medium', 'Low', 'Info']:
        for v in by_severity.get(sev, []):
            icon = {'Critical':'🔴','High':'🟠','Medium':'🟡','Low':'🟢','Info':'ℹ️'}.get(sev,'⚪')
            vuln_lines.append(f"### {icon} [{v.get('id','')}] {v.get('title','')} ({sev})")
            vuln_lines.append(f"- **대상**: {v.get('target','')}")
            vuln_lines.append(f"- **유형**: {v.get('type','')}")
            vuln_lines.append(f"- **설명**: {v.get('description','')}")
            vuln_lines.append(f"- **조치방법**: {v.get('remediation','')}")
            vuln_lines.append("")

    checklist = []
    for i, v in enumerate(sorted(vulns, key=lambda x: SEVERITY_ORDER.get(x.get('severity','Info'),4)), 1):
        sev = v.get('severity','Info')
        icon = {'Critical':'🔴','High':'🟠','Medium':'🟡','Low':'🟢','Info':'ℹ️'}.get(sev,'⚪')
        checklist.append(f"- [ ] {icon} [{v.get('id','')}] {v.get('target','')} — {v.get('title','')} ({sev})")

    targets = list(set(v.get('target','') for v in vulns))
    report = CHECKLIST_TEMPLATE.format(
        date=datetime.datetime.now().strftime('%Y-%m-%d %H:%M'),
        targets=', '.join(targets),
        cnt_critical=count('Critical'), cnt_high=count('High'),
        cnt_medium=count('Medium'), cnt_low=count('Low'), cnt_info=count('Info'),
        cnt_total=len(vulns), cnt_urgent=count('Critical')+count('High'),
        vuln_list='\n'.join(vuln_lines),
        checklist='\n'.join(checklist)
    )
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(report)
    return report

def main():
    parser = argparse.ArgumentParser(description='취약점 보고서 생성')
    parser.add_argument('--input', help='취약점 결과 JSON 파일')
    parser.add_argument('--output', default='vuln_report.md', help='출력 보고서 파일명')
    args = parser.parse_args()

    if args.input and os.path.exists(args.input):
        with open(args.input, encoding='utf-8') as f:
            vulns = json.load(f)
    else:
        print("샘플 데이터로 보고서 생성 (--input으로 실제 결과 파일 지정 가능)")
        vulns = load_sample_results()

    out_path = args.output
    report = generate_report(vulns, out_path)
    print(f"=== 취약점 보고서 생성 완료: {out_path} ===")
    print(f"총 취약점: {len(vulns)}건")
    print("\n" + report[:500] + "...")

if __name__ == '__main__':
    main()
