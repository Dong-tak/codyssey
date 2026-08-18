"""퀴즈 한 문제의 데이터와 행동을 정의하는 Quiz 클래스."""


class Quiz:
    """문제, 선택지 4개와 정답 번호를 표현한다.

    question: 문제 내용
    choices: 선택지 4개가 들어 있는 리스트
    answer: 사용자가 보는 기준과 같은 1부터 4까지의 정답 번호
    """

    # ------------------------------------------------------------------
    # 퀴즈 데이터 설정
    # ------------------------------------------------------------------

    def __init__(self, question, choices, answer):
        """문제 하나를 구성하는 문제·선택지·정답을 저장한다."""
        # 전달받은 세 값을 Quiz 객체의 상태로 보관함
        self.question = question
        self.choices = choices
        self.answer = answer

    # ------------------------------------------------------------------
    # 문제 출력과 정답 판정
    # ------------------------------------------------------------------

    def is_correct(self, user_answer):
        """사용자가 입력한 번호가 정답 번호와 같은지 반환한다."""
        # 사용자 답과 이 문제의 정답을 비교해 True 또는 False를 반환함
        return user_answer == self.answer

    def display(self, number):
        """문제 번호, 문제 내용과 객관식 선택지를 화면에 출력한다."""
        # 구분선과 문제 번호·내용을 출력함
        print("-" * 40)
        print()
        print(f"[문제 {number}]")
        print(self.question)
        print()

        # 선택지를 하나씩 꺼내 1부터 시작하는 번호와 함께 출력함
        for choice_number, choice in enumerate(self.choices, start=1):
            print(f"[{choice_number}] {choice}")

        # 한 문제의 출력이 끝났음을 구분선으로 표시함
        print("-" * 40)
        print()

    def get_answer_text(self):
        """1부터 시작하는 정답 번호에 해당하는 선택지 문구를 반환한다."""
        # 화면용 정답 번호를 0부터 시작하는 리스트 인덱스로 바꿈
        answer_index = self.answer - 1

        # 계산한 위치의 선택지 문구를 반환함
        return self.choices[answer_index]

    # ------------------------------------------------------------------
    # JSON 저장 형식 변환
    # ------------------------------------------------------------------

    def to_dict(self):
        """Quiz 객체를 JSON으로 저장할 수 있는 딕셔너리로 변환한다."""
        # 객체의 속성을 JSON이 처리할 수 있는 기본 자료형으로 묶어 반환함
        return {
            "question": self.question,
            "choices": self.choices,
            "answer": self.answer,
        }

    @staticmethod
    def from_dict(quiz_data):
        """딕셔너리의 구조와 값을 검사한 뒤 Quiz 객체로 복원한다."""
        # 퀴즈 하나가 이름-값 구조인 딕셔너리인지 확인함
        if not isinstance(quiz_data, dict):
            raise TypeError("퀴즈 데이터는 딕셔너리여야 합니다.")

        # 필수 필드 세 개를 꺼냄. 키가 없으면 KeyError가 발생함
        question = quiz_data["question"]
        choices = quiz_data["choices"]
        answer = quiz_data["answer"]

        # 문제 내용이 비어 있지 않은 문자열인지 확인함
        if not isinstance(question, str) or not question.strip():
            raise ValueError("문제는 비어 있지 않은 문자열이어야 합니다.")

        # 선택지가 비어 있지 않은 문자열 4개로 구성됐는지 확인함
        if (
            not isinstance(choices, list)
            or len(choices) != 4
            or not all(isinstance(choice, str) and choice.strip() for choice in choices)
        ):
            raise ValueError("선택지는 비어 있지 않은 문자열 4개여야 합니다.")

        # 정답이 bool이 아닌 1~4 범위의 정수인지 확인함
        if (
            not isinstance(answer, int)
            or isinstance(answer, bool)
            or not 1 <= answer <= 4
        ):
            raise ValueError("정답은 1부터 4까지의 정수여야 합니다.")

        # 모든 검증을 통과한 값으로 새 Quiz 객체를 만들어 반환함
        return Quiz(
            question,
            choices,
            answer,
        )
