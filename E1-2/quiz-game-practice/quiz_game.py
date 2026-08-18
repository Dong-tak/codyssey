"""게임 전체를 관리하는 QuizGame 클래스."""

import json
import os
import random

from default_quizzes import get_default_quizzes
from quiz import Quiz
from utils import input_int, input_text

# 실행 위치와 무관하게 프로젝트 루트를 가리키는 절대 경로를 만듦
STATE_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "state.json")


class QuizGame:
    """퀴즈 목록, 게임 진행, 점수와 파일 저장을 모두 조율한다."""

    # ------------------------------------------------------------------
    # 초기 상태 설정
    # ------------------------------------------------------------------

    def __init__(self):
        """기본 상태를 만든 뒤 state.json의 저장 데이터를 불러온다."""
        # 저장 파일이 없어도 실행할 수 있는 기본 상태를 먼저 만듦
        self.quizzes = get_default_quizzes()
        self.best_score = 0
        self.has_played = False

        # 저장 데이터가 정상이면 기본 상태를 저장된 상태로 교체함
        self.load()

    # ------------------------------------------------------------------
    # 메뉴 출력과 프로그램 실행
    # ------------------------------------------------------------------

    def show_menu(self):
        """사용자가 선택할 수 있는 메인 메뉴를 화면에 출력한다."""
        # 제목, 기능 번호, 종료 번호를 하나의 메뉴 화면으로 출력함
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
        """메뉴 선택을 반복 처리하고 종료할 때 현재 상태를 저장한다.

        Ctrl+C 또는 EOF가 발생해도 오류 화면을 남기지 않고 안전하게
        종료하며, 정상·중단 여부와 관계없이 finally에서 save()를 호출한다.
        """
        try:
            # 종료 메뉴를 선택할 때까지 메뉴 출력과 입력을 반복함
            while True:
                self.show_menu()
                choice = input_int("선택: ", 1, 5)

                # 입력한 번호에 해당하는 기능 메서드를 호출함
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

        # 입력 도중 어디서 중단돼도 오류 화면 없이 루프를 끝냄
        except (KeyboardInterrupt, EOFError):
            print("\n입력이 중단되어 게임을 안전하게 종료합니다.")

        # 정상 종료와 중단 종료 모두에서 현재 상태를 저장함
        finally:
            self.save()

    # ------------------------------------------------------------------
    # 퀴즈 게임 기능
    # ------------------------------------------------------------------

    def play_quiz(self):
        """선택한 개수만큼 무작위로 출제하고 채점과 최고 점수를 저장한다."""
        # 출제할 문제가 없으면 안내하고 기능을 끝냄
        if not self.quizzes:
            print("등록된 퀴즈가 없습니다.")
            return

        # 전체 문제 수 안에서 사용자가 풀 문제 수를 입력받음
        total_quizzes = len(self.quizzes)
        print(f"총 {total_quizzes}개의 퀴즈가 등록되어 있습니다.")

        quiz_count = input_int(
            f"몇 문제를 푸시겠습니까? (1-{total_quizzes}): ",
            1,
            total_quizzes,
        )

        # 원본 목록을 바꾸지 않고 입력받은 개수만큼 무작위로 뽑음
        selected_quizzes = random.sample(
            self.quizzes,
            quiz_count,
        )

        # 선택된 문제를 차례로 출력하고 답을 받아 정답 수를 누적함
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
                    f"[{quiz.answer}] {quiz.get_answer_text()}입니다."
                )

        # 이번 플레이의 최종 점수를 화면에 출력함
        print("=" * 40)
        print(f"{quiz_count}문제 중 {score}문제 정답")
        print("=" * 40)

        # 응시 상태를 기록하고 기존 기록보다 높으면 최고 점수를 바꿈
        self.has_played = True

        if score > self.best_score:
            self.best_score = score
            print("최고 점수를 갱신했습니다!")

        # 변경된 응시 상태와 최고 점수를 파일에 저장함
        self.save()

    def add_quiz(self):
        """문제·선택지 4개·정답 번호를 입력받아 새 퀴즈로 저장한다."""
        # 추가 화면을 알리고 문제 내용을 입력받음
        print("\n새로운 퀴즈를 추가합니다.")

        question = input_text("문제를 입력하세요: ")
        choices = []

        # 비어 있지 않은 선택지 4개를 차례로 입력받아 리스트에 모음
        for choice_number in range(1, 5):
            choice = input_text(f"선택지 {choice_number}: ")
            choices.append(choice)

        # 1~4 범위의 정답 번호를 입력받음
        answer = input_int(
            "정답 번호 (1-4): ",
            1,
            4,
        )

        # 입력값으로 새 Quiz 객체를 만들고 게임의 목록에 추가함
        new_quiz = Quiz(
            question,
            choices,
            answer,
        )

        self.quizzes.append(new_quiz)

        # 추가 결과를 즉시 저장하고 완료 메시지를 출력함
        self.save()
        print("퀴즈가 추가되었습니다.")

    def list_quizzes(self):
        """등록된 모든 문제를 번호와 함께 한 줄씩 출력한다."""
        # 등록된 문제가 없으면 안내하고 기능을 끝냄
        if not self.quizzes:
            print("\n등록된 퀴즈가 없습니다.")
            return

        # 전체 개수와 목록 시작 구분선을 출력함
        print(f"\n등록된 퀴즈 목록 (총 {len(self.quizzes)}개)")
        print("-" * 40)

        # 줄바꿈과 연속 공백을 한 칸으로 바꿔 문제를 한 줄씩 출력함
        for number, quiz in enumerate(self.quizzes, start=1):
            question = " ".join(quiz.question.split())
            print(f"[{number}] {question}")

        # 목록 출력이 끝났음을 구분선으로 표시함
        print("-" * 40)

    def check_score(self):
        """응시 여부를 확인한 뒤 지금까지의 최고 점수를 출력한다."""
        # 아직 한 번도 풀지 않았다면 점수 대신 상태를 안내함
        if not self.has_played:
            print("아직 퀴즈를 풀지 않았습니다.")
            return

        # 응시 기록이 있으면 저장된 최고 점수를 출력함
        print(f"최고 점수: {self.best_score}점")

    # ------------------------------------------------------------------
    # JSON 파일 저장과 불러오기
    # ------------------------------------------------------------------

    def load(self):
        """state.json을 읽어 퀴즈 객체, 최고 점수와 응시 상태를 복원한다.

        파일이 없으면 기본 퀴즈를 유지한다. JSON 문법이나 저장 데이터의
        자료형·범위가 잘못된 경우에도 기본 상태를 유지해 실행을 계속한다.
        """
        try:
            # state.json을 UTF-8 읽기 모드로 열어 딕셔너리로 읽음
            with open(
                STATE_FILE,
                "r",
                encoding="utf-8",
            ) as file:
                data = json.load(file)

            # 최상위 quizzes가 여러 문제를 담는 리스트인지 확인함
            quiz_data_list = data["quizzes"]
            if not isinstance(quiz_data_list, list):
                raise TypeError("quizzes는 리스트여야 합니다.")

            # 각 딕셔너리를 검증된 Quiz 객체로 복원해 임시 목록에 모음
            loaded_quizzes = []

            for quiz_data in quiz_data_list:
                converted_quiz = Quiz.from_dict(quiz_data)
                loaded_quizzes.append(converted_quiz)

            # 게임 전체 상태인 최고 점수와 응시 여부를 임시로 꺼냄
            loaded_best_score = data["best_score"]
            loaded_has_played = data.get("has_played", False)

            # 최고 점수가 bool이 아닌 0 이상의 정수인지 확인함
            if (
                not isinstance(loaded_best_score, int)
                or isinstance(loaded_best_score, bool)
                or loaded_best_score < 0
            ):
                raise ValueError("best_score는 0 이상의 정수여야 합니다.")

            # 응시 여부가 True 또는 False인지 확인함
            if not isinstance(loaded_has_played, bool):
                raise TypeError("has_played는 bool 값이어야 합니다.")

            # 모든 검증이 끝난 뒤에만 기본 상태를 저장 데이터로 교체함
            self.quizzes = loaded_quizzes
            self.best_score = loaded_best_score
            self.has_played = loaded_has_played

        # 파일 없음은 첫 실행으로 보고 생성자에서 만든 기본값을 유지함
        except FileNotFoundError:
            print("저장된 데이터가 없어 기본 퀴즈를 사용합니다.")

        # JSON 문법·인코딩·구조·값이 잘못돼도 기본값으로 계속 실행함
        except (
            json.JSONDecodeError,
            UnicodeDecodeError,
            KeyError,
            TypeError,
            ValueError,
        ) as error:
            print(f"저장 데이터가 손상되어 기본 퀴즈를 사용합니다: {error}")

        # 권한이나 경로 같은 운영체제 오류도 안내하고 기본값을 유지함
        except OSError as error:
            print(f"데이터를 불러오지 못해 기본 퀴즈를 사용합니다: {error}")

    def save(self):
        """현재 퀴즈, 최고 점수와 응시 상태를 state.json에 저장한다."""
        # 각 Quiz 객체를 JSON이 저장할 수 있는 딕셔너리로 변환함
        quiz_dicts = []
        for quiz in self.quizzes:
            converted_quiz = quiz.to_dict()
            quiz_dicts.append(converted_quiz)

        # 문제 목록과 게임 전체 상태를 하나의 최상위 딕셔너리로 묶음
        save_data = {
            "quizzes": quiz_dicts,
            "best_score": self.best_score,
            "has_played": self.has_played,
        }

        try:
            # UTF-8 쓰기 모드로 열어 한글이 보이는 JSON으로 기록함
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

        # 권한·경로·디스크 같은 쓰기 실패를 잡아 사용자에게 알림
        except OSError as error:
            print(f"저장에 실패했습니다: {error}")
