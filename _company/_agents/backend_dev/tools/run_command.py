# run_command.py — 프로젝트 폴더에서 명령을 실행합니다
import sys, os, json, argparse, subprocess
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
sys.stderr.reconfigure(encoding='utf-8', errors='replace')

CONFIG_FILE = os.path.join(os.path.dirname(__file__), 'run_command.json')
PROJECT_CONFIG = os.path.join(os.path.dirname(__file__), '..', '..', '..', '_shared', 'project_config.json')

def get_project_path():
    try:
        with open(os.path.normpath(PROJECT_CONFIG), encoding='utf-8') as f:
            return json.load(f).get('projectPath', '').strip()
    except: return ''

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--cmd', default='')
    parser.add_argument('--cwd', default='')
    parser.add_argument('--timeout', type=int, default=60)
    args = parser.parse_args()

    cfg = {}
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, encoding='utf-8') as f: cfg = json.load(f)
        except: pass

    command = args.cmd or cfg.get('cmd', '')
    cwd     = args.cwd or cfg.get('cwd', '') or get_project_path()
    timeout = cfg.get('timeout', args.timeout)

    if not command:
        print('❌ 실행할 명령이 없습니다 (--cmd 또는 설정값 JSON의 cmd 필드)'); sys.exit(1)
    if not cwd or not os.path.exists(cwd):
        print(f'⚠️  실행 디렉토리 없음: {cwd}'); cwd = os.getcwd()

    print(f'▶ 실행: {command}\n   위치: {cwd}\n' + '─'*50)
    try:
        r = subprocess.run(command, shell=True, cwd=cwd, capture_output=True,
                           text=True, encoding='utf-8', errors='replace', timeout=timeout)
        if r.stdout: print(r.stdout)
        if r.stderr: print(f'[stderr]\n{r.stderr}')
        print(f'{"✅" if r.returncode==0 else "⚠️ "} 종료 코드: {r.returncode}')
        sys.exit(r.returncode)
    except subprocess.TimeoutExpired:
        print(f'❌ 타임아웃 ({timeout}초)'); sys.exit(1)
    except Exception as e:
        print(f'❌ 오류: {e}'); sys.exit(1)

if __name__ == '__main__': main()
