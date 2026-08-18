"""퀴즈 게임 - 프로그램 진입점.

실행:  python3 main.py
"""

from quiz_game import QuizGame


def main():
    """QuizGame 객체를 생성하고 프로그램의 메뉴 반복을 시작한다."""
    # 생성자에서 기본값을 준비하고 저장 데이터를 불러옴
    game = QuizGame()

    # 메뉴 반복을 시작해 사용자의 선택을 처리함
    game.run()


if __name__ == "__main__":
    # 이 파일을 직접 실행했을 때만 게임을 시작함
    main()
