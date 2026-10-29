import argparse
import sys

from git_utils import is_git_repo, get_status, get_diff, get_branch, summarize_changes
from sanitizer import mask, limit_diff
from prompts import COMMIT_SYSTEM, PR_SYSTEM, build_user_prompt
from ai_client import call_ai, get_api_key, AiError
from validators import validate_commit, validate_pr, split_pr


def parse_args():
    """argparse 서브커맨드 (PLAN 4.4)"""
    # TODO
    # parser = argparse.ArgumentParser(...)
    # sub = parser.add_subparsers(dest="command", required=True)
    # commit, pr 두 서브커맨드를 만들고, 둘 다 같은 옵션을 가진다:
    #   "-model", "--model"           str    기본 claude-haiku-4-5
    #   "-temperature", "--temperature" float 기본 0.3
    #   "-max-tokens", "--max-tokens"  int   기본 1024   (args.max_tokens 로 읽힘)
    #   "--safe-mode"                 store_true
    # return parser.parse_args()
    raise NotImplementedError


def generate(system, user, args, validate):
    """AI 호출 + 검증 + 필요 시 재생성 1회. (결과 텍스트, 호출 횟수) 반환 (PLAN 6.2)"""
    # TODO
    # 1. print("[INFO] AI API 요청 중... (model=..., temperature=..., max_tokens=...)")
    # 2. result = call_ai(...)    호출 1회차, 토큰 수 로그 출력
    # 3. stop_reason == "max_tokens" 이면 "[WARN] 응답이 max_tokens에서 잘렸습니다..." 출력
    # 4. problems = validate(result.text)
    # 5. problems가 있으면: 위반 목록을 user 프롬프트 끝에 덧붙여 call_ai 한 번 더 (2회차, 딱 1번)
    # 6. 2회차도 problems가 있으면 포기하고 그대로 쓰되 "[WARN] ..." 로 위반 항목 출력
    # 7. return (text, 호출 횟수)
    raise NotImplementedError


def print_block(title, body):
    """--- title --- / 본문 / ---------- 구획 출력 (PLAN 4.5)"""
    # TODO
    raise NotImplementedError


def main():
    """종료 코드를 반환한다 (0 정상, 1 오류). PLAN 4.3 데이터 흐름 그대로"""
    # TODO
    # 1. args = parse_args()
    # 2. if not is_git_repo():  "[ERROR] Git 저장소가 아닙니다. 프로젝트 루트에서 실행하세요." -> return 1
    # 3. status = get_status(), diff = get_diff(), branch = get_branch()
    # 4. status도 diff도 비었으면 "[INFO] 변경 사항이 없습니다. ... 종료합니다." -> return 0  (API 호출 0회)
    # 5. "[INFO] Git status 수집 완료: N개 파일 변경 감지" / "[INFO] Git diff 수집 완료: M줄"
    # 6. summary = summarize_changes(status, diff)  -> Change Summary 구획 출력
    # 7. args.safe_mode 이면: diff = mask(diff), diff, cut = limit_diff(diff, 10, 200), 잘렸으면 note 만들기
    # 8. user = build_user_prompt(...)
    # 9. try: get_api_key()  except AiError as e: print(e), return 1   (키 없으면 호출 전에 종료)
    # 10. args.command 가 "commit" 이면 COMMIT_SYSTEM + validate_commit, "pr" 이면 PR_SYSTEM + validate_pr(split_pr 사용)
    # 11. try: generate(...)  except AiError as e: print(e), return 1
    # 12. 결과를 print_block 으로 출력, "[DONE] ..." , "※ AI가 만든 초안입니다. 검토 후 적용하세요."
    # 13. "[INFO] API 호출 N회" 로그, return 0
    raise NotImplementedError


if __name__ == "__main__":
    sys.exit(main())
