"""게임 전체를 관리하는 QuizGame 클래스."""

import json
import os
import random

from default_quizzes import get_default_quizzes
from quiz import Quiz
from utils import input_int, input_text

# 데이터 파일은 실행 위치와 무관하게 프로젝트 루트를 가리키도록 절대 경로로 만든다.
STATE_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "state.json")


class QuizGame:
    """퀴즈 목록과 최고 점수를 들고 게임 흐름을 관리한다."""

    def __init__(self):
        self.quizzes = get_default_quizzes()
        self.best_score = 0
        self.has_played = False
        self.load()

    def show_menu(self):
        """메뉴 화면을 출력한다."""
        print()
        print("=" * 40)
        print("        퀴즈 게임")
        print("=" * 40)
        print("1. 퀴즈 풀기")
        print("2. 퀴즈 추가")
        print("3. 퀴즈 목록")
        print("4. 점수 확인")
        print("5. 종료")
        print("=" * 40)

    def run(self):
        """메인 루프. 메뉴를 반복 출력하며 선택을 처리한다."""
        try:
            while True:
                self.show_menu()
                choice = input_int("선택: ", 1, 5)

                if choice == 1:
                    self.play_quiz()
                elif choice == 2:
                    self.add_quiz()
                elif choice == 3:
                    self.list_quizzes()
                elif choice == 4:
                    self.check_score()
                elif choice == 5:
                    print("게임을 종료합니다.")
                    break
        except (KeyboardInterrupt, EOFError):
            print("\n입력이 중단되어 게임을 안전하게 종료합니다.")
        finally:
            self.save()

    def play_quiz(self):
        """퀴즈를 출제하고 채점한다."""
        if not self.quizzes:
            print("등록된 퀴즈가 없습니다.")
            return

        total_quizzes = len(self.quizzes)
        print(f"총 {total_quizzes}개의 퀴즈가 등록되어 있습니다.")

        quiz_count = input_int(
            f"몇 문제를 푸시겠습니까? (1-{total_quizzes}): ",
            1,
            total_quizzes,
        )

        selected_quizzes = random.sample(
            self.quizzes,
            quiz_count,
        )

        score = 0

        for number, quiz in enumerate(selected_quizzes, start=1):
            quiz.display(number)

            user_answer = input_int(
                "정답 입력: ",
                1,
                len(quiz.choices),
            )

            if quiz.is_correct(user_answer):
                print("정답입니다!")
                score += 1
            else:
                print(
                    f"오답입니다. 정답은 "
                    f"[ {quiz.answer}] 번 {quiz.get_answer_text()}입니다."
                )

        print("=" * 40)
        print(f"{quiz_count}문제 중 {score}문제 정답")
        print("=" * 40)

        self.has_played = True

        if score > self.best_score:
            self.best_score = score
            print("최고 점수를 갱신했습니다!")

        self.save()

    def add_quiz(self):
        """새 퀴즈를 입력받아 목록에 추가한다."""
        print("\n새로운 퀴즈를 추가합니다.")

        question = input_text("문제를 입력하세요: ")
        choices = []

        for choice_number in range(1, 5):
            choice = input_text(f"선택지 {choice_number}: ")
            choices.append(choice)

        answer = input_int(
            "정답 번호 (1-4): ",
            1,
            4,
        )

        new_quiz = Quiz(
            question,
            choices,
            answer,
        )

        self.quizzes.append(new_quiz)
        self.save()
        print("퀴즈가 추가되었습니다.")

    def list_quizzes(self):
        """등록된 퀴즈 목록을 출력한다."""
        if not self.quizzes:
            print("\n등록된 퀴즈가 없습니다.")
            return

        print(f"\n등록된 퀴즈 목록 (총 {len(self.quizzes)}개)")
        print("-" * 40)

        for number, quiz in enumerate(self.quizzes, start=1):
            question = " ".join(quiz.question.split())
            print(f"[{number}] {question}")

        print("-" * 40)

    def check_score(self):
        """최고 점수를 출력한다."""

        if not self.has_played:
            print("아직 퀴즈를 풀지 않았습니다.")
            return

        print(f"최고 점수: {self.best_score}점")

    def load(self):
        """state.json 에서 퀴즈와 최고 점수를 불러온다."""
        #   STATE_FILE 을 UTF-8 로 열어 json.load 로 읽고,
        #   quizzes(딕셔너리 리스트)를 Quiz.from_dict 로 객체 리스트로 되돌려
        #   self.quizzes 와 self.best_score 에 반영한다.
        try:
            with open(
                STATE_FILE,
                "r",
                encoding="utf-8",
            ) as file:
                data = json.load(file)

            quiz_data_list = data["quizzes"]
            if not isinstance(quiz_data_list, list):
                raise TypeError("quizzes는 리스트여야 합니다.")

            loaded_quizzes = []

            for quiz_data in quiz_data_list:
                converted_quiz = Quiz.from_dict(quiz_data)
                loaded_quizzes.append(converted_quiz)

            loaded_best_score = data["best_score"]
            loaded_has_played = data.get("has_played", False)

            if (
                not isinstance(loaded_best_score, int)
                or isinstance(loaded_best_score, bool)
                or loaded_best_score < 0
            ):
                raise ValueError("best_score는 0 이상의 정수여야 합니다.")

            if not isinstance(loaded_has_played, bool):
                raise TypeError("has_played는 bool 값이어야 합니다.")

            self.quizzes = loaded_quizzes
            self.best_score = loaded_best_score
            self.has_played = loaded_has_played

        except FileNotFoundError:
            print("저장된 데이터가 없어 기본 퀴즈를 사용합니다.")
        except (
            json.JSONDecodeError,
            UnicodeDecodeError,
            KeyError,
            TypeError,
            ValueError,
        ) as error:
            print(f"저장 데이터가 손상되어 기본 퀴즈를 사용합니다: {error}")
        except OSError as error:
            print(f"데이터를 불러오지 못해 기본 퀴즈를 사용합니다: {error}")

    def save(self):
        """현재 퀴즈 목록과 최고 점수를 state.json 에 저장한다."""

        # 호출 시점: 퀴즈 추가 직후, 점수 갱신 후
        quiz_dicts = []
        for quiz in self.quizzes:
            converted_quiz = quiz.to_dict()
            quiz_dicts.append(converted_quiz)

        save_data = {
            "quizzes": quiz_dicts,
            "best_score": self.best_score,
            "has_played": self.has_played,
        }

        try:
            with open(
                STATE_FILE,
                "w",
                encoding="utf-8",
            ) as file:
                json.dump(
                    save_data,
                    file,
                    ensure_ascii=False,
                    indent=2,
                )

        except OSError as error:  # 파일 읽기·쓰기 관련 예외
            print(f"저장에 실패했습니다: {error}")
