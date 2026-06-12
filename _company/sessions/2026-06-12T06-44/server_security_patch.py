from flask import Flask, request, jsonify, render_template
from werkzeug.security import check_password_hash, generate_password_hash
import re
import html

app = Flask(__name__)

# [보안 설정] 실제 환경에서는 DB에서 조회하지만, 테스트를 위해 메모리 저장소 사용
USER_DB = {
    "admin": generate_password_hash("p@ssword123!")
}

def validate_input(text):
    """
    [OWASP A03:2021] 입력값 검증 및 XSS 방지 필터링
    - 특수문자 제거 및 HTML 엔티티 인코딩
    """
    if not text:
        return None
    # 1. 입력값 길이 제한 (DoS 방지)
    if len(text) > 50:
        return None
    # 2. HTML 인코딩 처리 (XSS 방지)
    return html.escape(text)

@app.route('/login', methods=['POST'])
def login():
    # 1. 클라이언트 전송 데이터 수신
    user_id = request.form.get('userId')
    password = request.form.get('password')

    # 2. [서버 측 검증] 지현님의 JS 검증 우회 대응
    sanitized_id = validate_input(user_id)
    if not sanitized_id or not password:
        return jsonify({"status": "error", "message": "유효하지 않은 입력값입니다."}), 400

    # 3. [인증 보안] SQL Injection 방지 및 안전한 비밀번호 비교
    # 실제 DB 사용 시: SELECT password_hash FROM users WHERE user_id = %s (Parameterized Query 사용)
    stored_hash = USER_DB.get(sanitized_id)
    
    if stored_hash and check_password_hash(stored_hash, password):
        # 로그인 성공
        return jsonify({"status": "success", "message": f"Welcome {sanitized_id}님"}), 200
    else:
        # [보안 팁] 아이디가 틀렸는지 비밀번호가 틀렸는지 구체적으로 알려주지 않음 (계정 열거 공격 방지)
        return jsonify({"status": "error", "message": "아이디 또는 비밀번호가 일치하지 않습니다."}), 401

if __name__ == "__main__":
    app.run(debug=False) # Production 환경에서는 debug=False 필수