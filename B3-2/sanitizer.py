import re  # 마스킹에 사용


def mask(text):
    """민감정보를 치환한 문자열 반환 (PLAN 7.1). 원칙: 오탐 허용, 누락 불허"""
    # TODO
    # 치환 규칙 (re.sub, 위에서부터 순서대로. 긴/구체적인 것 먼저)
    #   sk-ant-[A-Za-z0-9_-]{20,}           -> [MASKED_API_KEY]
    #   sk-[A-Za-z0-9]{20,}                 -> [MASKED_API_KEY]
    #   이메일 (글자@글자.글자)              -> [MASKED_EMAIL]
    #   01X-XXXX-XXXX (하이픈 선택)          -> [MASKED_PHONE]
    #   (API_KEY|SECRET|TOKEN|PASSWORD)\s*[=:]\s*\S+  -> 키 이름은 남기고 값만 [MASKED]
    #       힌트: 그룹 ( ) 으로 앞부분을 잡고 치환 문자열에서 \1 로 되살리기
    raise NotImplementedError


def limit_diff(diff, max_files, max_lines):
    """(잘린 diff, 잘렸는지 True/False) 반환 (PLAN 7.2)"""
    # TODO
    # 1. 파일 단위로 나누기: diff를 "diff --git" 로 시작하는 줄 기준으로 쪼갬
    # 2. 앞에서 max_files개만 남기기
    # 3. 이어 붙인 뒤 splitlines() 로 max_lines줄까지만 남기기
    # 4. 하나라도 잘렸으면 (잘린 diff, True), 아니면 (원본, False)
    raise NotImplementedError
