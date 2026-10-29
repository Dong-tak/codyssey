import subprocess


def run_git(args):
    result = subprocess.run(
        ["git"]+args,
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode!=0:
        raise RuntimeError(f"실패 : ㅡㅡ{result.stderr}")
    
    return result.stdout


def is_git_repo():
    """git 저장소 안이면 True, 아니면 False"""
    try: 
        run_git(["rev-parse", "--is-inside-work-tree"])
        return True
    except RuntimeError:
        return False
    raise NotImplementedError


def get_status():
    """git status --porcelain 결과를 '줄 목록'으로 반환 (변경 없으면 [])"""
    # TODO
    # 1. out = run_git(["status", "--porcelain"])
    # 2. out.splitlines() 반환
    # 주의: out.strip() 쓰지 말 것. 첫 줄이 " M file"처럼 공백으로 시작하는데 strip이 그 공백을 지움
    raise NotImplementedError


def get_diff():
    """스테이징 전 diff + 스테이징 후 diff를 합친 문자열 (없으면 '')"""
    # TODO
    # 1. unstaged = run_git(["diff"])
    # 2. staged   = run_git(["diff", "--cached"])
    # 3. 둘을 이어 붙여 반환 (사이에 "\n" 하나)
    # 알아둘 것: untracked(새 파일)는 diff에 안 나옴 -> status 쪽에서만 보임. 지금은 그대로 둬도 됨
    raise NotImplementedError


def get_branch():
    """현재 브랜치 이름 (detached HEAD면 '')"""
    # TODO
    # 1. out = run_git(["branch", "--show-current"])
    # 2. 끝의 줄바꿈 제거해서 반환 (여기선 strip 써도 됨)
    raise NotImplementedError


def summarize_changes(status, diff):
    """로컬 계산 요약 dict (API 호출 아님). main이 돌아간 뒤에 구현"""
    # TODO
    # 반환 예: {"files": 3, "modified": 2, "added": 1, "deleted": 0, "plus": 128, "minus": 34}
    # - 파일 수 = len(status)
    # - status 각 줄의 앞 2글자로 수정(M) / 추가(??, A) / 삭제(D) 개수 세기
    # - diff.splitlines() 중 "+"로 시작(단 "+++" 제외) = 추가 줄, "-"로 시작(단 "---" 제외) = 삭제 줄
    raise NotImplementedError
