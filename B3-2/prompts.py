# system = 매번 같은 규칙 / user = 매번 다른 데이터  (PLAN 5.1)

COMMIT_SYSTEM = """\
TODO: 커밋 메시지 규칙을 숫자로 못 박아 쓰기 (PLAN 5.3)
 - 역할 한 줄
 - 제목 1줄 `type: 설명`, type 목록, 50자 이내(최대 72자), 마침표 금지, 명령형 한국어
 - 제목 다음 빈 줄, 본문은 `- ` 불릿 1~2개 또는 파일 1~3개 언급
 - 금지: 코드 블록(백틱 3개), 인사말, 설명 문장, 추측으로 사실 지어내기
 - 예시 1개 (형식만 참고, 내용 베끼지 말라고 명시)
"""

PR_SYSTEM = """\
TODO: PR 규칙 (PLAN 5.4)
 - 첫 줄 제목 (80자 이내, 1줄), 빈 줄 후 본문
 - 헤더는 정확히 `## Why` / `## What` / `## How to Test`
 - 섹션마다 `- ` 불릿 1개 이상, How to Test는 실행 가능한 명령
 - 금지사항 + 예시 1개
"""


def build_user_prompt(status, diff, branch, truncated_note=""):
    """AI에게 보낼 user 메시지(문자열) 조립"""
    # TODO
    # 1. 브랜치명 (branch가 빈 문자열이면 "알 수 없음")
    # 2. status 줄 목록을 줄바꿈으로 이어서 넣기
    #    ?? 로 시작하는 줄 = 새 파일 -> "새 파일(내용 미포함)" 로 따로 표시 (PLAN 5.5)
    # 3. diff 넣기
    # 4. truncated_note 가 있으면 끝에 덧붙이기 (예: "※ 총 N줄 중 200줄만 전송됨")
    # 5. 위 4가지를 구획 제목("## Branch", "## Status", "## Diff")으로 나눠 하나의 문자열로 반환
    raise NotImplementedError
