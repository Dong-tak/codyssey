import os
from dataclasses import dataclass

import requests

# 제공자 미결 (PLAN 3.3). 정해지면 아래 둘 중 하나만 남기기
URL = "TODO: https://api.anthropic.com/v1/messages  또는  https://copa.codyssey.kr/v1/chat/completions"
ENV_KEY = "AI_API_KEY"
TIMEOUT = 60


class AiError(Exception):
    """사용자에게 그대로 보여줄 한 줄 메시지를 담는다"""


@dataclass
class AiResult:
    text: str
    input_tokens: int
    output_tokens: int
    stop_reason: str


def get_api_key():
    """환경변수에서 키를 읽어 반환. 없으면 AiError"""
    # TODO
    # 1. key = os.environ.get(ENV_KEY)
    # 2. key가 None 또는 빈 문자열이면 AiError("[ERROR] AI_API_KEY 환경변수가 설정되지 않았습니다.\n  export AI_API_KEY=\"YOUR_KEY\"")
    # 3. return key   (키 값은 절대 print / 로그에 찍지 말 것)
    raise NotImplementedError


def call_ai(system, user, model, temperature, max_tokens):
    """AI 1회 호출 -> AiResult. 실패는 전부 AiError로 바꿔서 던진다 (PLAN 4.6)"""
    # TODO
    # 1. key = get_api_key()
    # 2. headers / body 만들기
    #      Anthropic: headers x-api-key, anthropic-version: 2023-06-01
    #                 body {model, max_tokens, temperature, system(최상위), messages:[{role:"user", content:user}]}
    #      Codyssey : headers Authorization: Bearer <key>
    #                 body {model, max_tokens, temperature, messages:[{system},{user}]}
    # 3. try: r = requests.post(URL, headers=..., json=..., timeout=TIMEOUT)
    #    except requests.Timeout        -> AiError("[ERROR] 요청 시간 초과(60초).")
    #    except requests.ConnectionError -> AiError("[ERROR] 네트워크에 연결할 수 없습니다.")
    # 4. r.status_code 별 메시지 (표는 PLAN 4.6): 401 / 404 / 400(서버 error.message 덧붙임) / 429 / 500·529
    # 5. 성공(200)이면 JSON에서 텍스트와 usage, stop_reason 꺼내 AiResult 반환
    raise NotImplementedError
