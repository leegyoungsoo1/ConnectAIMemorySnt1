# write_file.py — 코드 파일 생성/수정 (개발 에이전트용)
# 사용법 A (멀티라인, 권장):
#   $code = @'...코드...'@; $code | python write_file.py --path "src/App.jsx"
# 사용법 B (단순):
#   python write_file.py --path "src/App.jsx" --content "짧은내용"
import sys, os, json, argparse
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
sys.stderr.reconfigure(encoding='utf-8', errors='replace')

CONFIG_FILE  = os.path.join(os.path.dirname(__file__), 'write_file.json')
PROJECT_CONFIG = os.path.normpath(os.path.join(os.path.dirname(__file__), '..', '..', '..', '_shared', 'project_config.json'))

def get_project_path():
    try:
        with open(PROJECT_CONFIG, encoding='utf-8') as f:
            return json.load(f).get('projectPath', '').strip()
    except: return ''

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--path',    default='')
    parser.add_argument('--content', default='')
    args = parser.parse_args()

    cfg = {}
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, encoding='utf-8') as f: cfg = json.load(f)
        except: pass

    file_path = args.path or cfg.get('path', '')

    # 내용 우선순위: --content 인자 > 파이프(stdin) > config 기본값
    if args.content:
        content = args.content
    elif not sys.stdin.isatty():
        content = sys.stdin.read()
    else:
        content = cfg.get('content', '')

    if not file_path:
        print('❌ 파일 경로가 없습니다.')
        print('   사용법: $code = @\'...\'@; $code | python write_file.py --path "src/파일.jsx"')
        sys.exit(1)

    if not os.path.isabs(file_path):
        base = get_project_path()
        if base:
            file_path = os.path.join(base, file_path)
        else:
            print('⚠️  프로젝트 폴더 미설정 — 회사 설정에서 경로를 지정하세요')

    os.makedirs(os.path.dirname(os.path.abspath(file_path)), exist_ok=True)
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    size  = len(content.encode('utf-8'))
    lines = content.count('\n') + (1 if content else 0)
    print(f'✅ 파일 저장 완료: {file_path}')
    print(f'   {lines}줄 · {size:,} bytes')

if __name__ == '__main__': main()
