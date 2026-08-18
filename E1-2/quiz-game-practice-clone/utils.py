"""공통 입력 처리 유틸리티.

이 모듈은 아무것도 import 하지 않는다. (의존 구조의 맨 아래층)
"""


def input_int(prompt, min_value, max_value):
    """min_value ~ max_value 범위의 정수를 입력받아 반환한다.

    공백 제거, 빈 입력, 숫자 변환 실패, 범위 밖 값을 모두 처리하고
    올바른 값이 들어올 때까지 다시 물어본다.
    """
    while True:
        raw = input(prompt).strip()

        if raw == "":
            print(f"경고: 입력이 비어 있습니다. {min_value}-{max_value} 사이의 숫자를 입력하세요.")
            continue

        try:
            value = int(raw)
        except ValueError:
            print(f"경고: 잘못된 입력입니다. {min_value}-{max_value} 사이의 숫자를 입력하세요.")
            continue

        if value < min_value or value > max_value:
            print(f"경고: {min_value}-{max_value} 범위를 벗어났습니다. 다시 입력하세요.")
            continue

        return value


def input_text(prompt):
    """비어 있지 않은 문자열을 입력받아 반환한다."""
    while True:
        raw = input(prompt).strip()
        if raw == "":
            print("경고: 내용을 입력해야 합니다.")
            continue
        return raw
