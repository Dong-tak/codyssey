import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from sanitizer import mask, limit_diff


def test_mask():
    # TODO: assert 로 확인
    #  - "sk-ant-" 키가 [MASKED_API_KEY] 로 바뀐다
    #  - 이메일 / 전화번호 / API_KEY=값 이 가려진다
    #  - 평범한 문장은 그대로다
    pass


def test_limit_diff():
    # TODO: 파일 12개짜리 가짜 diff 로 max_files=10 -> (잘린 diff, True)
    #       짧은 diff -> (원본, False)
    pass


if __name__ == "__main__":
    test_mask()
    test_limit_diff()
    print("sanitizer OK")
