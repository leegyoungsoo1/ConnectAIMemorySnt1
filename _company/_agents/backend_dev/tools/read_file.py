# read_file.py — 프로젝트 파일 읽기 (개발 에이전트용)
# 사용법: python read_file.py --path "src/components/App.jsx"
import sys, os, json, argparse
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

CONFIG_FILE   = os.path.join(os.path.dirname(__file__), 'read_file.json')
PROJECT_CONFIG = os.path.normpath(os.path.join(os.path.dirname(__file__), '..', '..', '..', '_shared', 'project_config.json'))

def get_project_path():
    try:
        with open(PROJECT_CONFIG, encoding='utf-8') as f:
            return json.load(f).get('projectPath', '').strip()
    except: return ''

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--path',  default='')
    parser.add_argument('--lines', type=int, default=300)
    args = parser.parse_args()

    cfg = {}
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, encoding='utf-8') as f: cfg = json.load(f)
        except: pass

    file_path = args.path or cfg.get('path', '')
    max_lines = cfg.get('lines', args.lines)

    if not file_path:
        print('❌ 파일 경로가 없습니다.')
        print('   사용법: python read_file.py --path "src/App.jsx"')
        sys.exit(1)

    if not os.path.isabs(file_path):
        base = get_project_path()
        if base: file_path = os.path.join(base, file_path)

    if not os.path.exists(file_path):
        print(f'❌ 파일 없음: {file_path}')
        sys.exit(1)

    try:
        with open(file_path, encoding='utf-8', errors='replace') as f:
            all_lines = f.readlines()
        total = len(all_lines)
        shown = all_lines[:max_lines]
        print(f'📄 {file_path}  ({total}줄)\n' + '─' * 60)
        for i, line in enumerate(shown, 1):
            print(f'{i:4d} │ {line}', end='')
        if not shown[-1].endswith('\n'):
            print()
        if total > max_lines:
            print(f'\n... ({total - max_lines}줄 더 있음 — --lines {total} 로 전체 보기)')
    except Exception as e:
        print(f'❌ 읽기 실패: {e}')
        sys.exit(1)

if __name__ == '__main__': main()
