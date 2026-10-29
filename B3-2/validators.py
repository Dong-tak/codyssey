# 모든 validate_* 는 "위반 목록(list[str])"을 반환. 빈 리스트 = 통과  (PLAN 6.1)


def validate_commit(text):
    """커밋 메시지 검사"""
    # TODO
    # problems = []
    # 1. 제목 = 첫 줄. 비어 있으면 "제목이 없음"
    # 2. len(제목) > 72 -> 오류,  > 50 -> 경고 문구 (경고는 목록에 넣을지 말지 직접 결정)
    # 3. 제목이 "." 으로 끝나면 경고
    # 4. 본문이 있다면: "- " 로 시작하는 줄이 1개 이상, 또는 파일 언급이 있어야 함
    # 5. text 안에 백틱 3개가 있으면 오류
    # return problems
    raise NotImplementedError


def split_pr(text):
    """AI 출력을 (제목, 본문)으로 분리. 첫 줄 = 제목, 나머지 = 본문"""
    # TODO
    # 힌트: text.strip().split("\n", 1) , 줄이 하나뿐인 경우 처리
    raise NotImplementedError


def validate_pr(title, body):
    """PR 제목/본문 검사"""
    # TODO
    # 1. 제목: 비어 있지 않음, 80자 이하
    # 2. 본문에 "## Why", "## What", "## How to Test" 3개 모두 있는지
    # 3. 각 섹션 아래에 "- " 불릿이 1개 이상 있는지
    #      힌트: body를 "## " 기준으로 쪼개서 섹션별로 검사
    # 4. 백틱 3개 금지
    raise NotImplementedError
