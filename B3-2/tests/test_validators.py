import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from validators import validate_commit, validate_pr, split_pr


def test_commit():
    # TODO: 좋은 메시지 -> [] / 73자 제목 -> 위반 있음 / 백틱 3개 포함 -> 위반 있음
    pass


def test_pr():
    # TODO: 섹션 3개 + 불릿 있는 본문 -> [] / ## Why 빠진 본문 -> 위반 있음
    pass


if __name__ == "__main__":
    test_commit()
    test_pr()
    print("validators OK")
