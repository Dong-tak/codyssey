class Quiz:
    """퀴즈 한 문제.

    question : 문제 내용 (str)
    choices  : 선택지 4개 (list)
    answer   : 정답 번호 1~4 (int)  ※ 인덱스 0~3 이 아니라 사람이 보는 번호
    """

    def __init__(self, question, choices, answer):
        self.question = question
        self.choices = choices
        self.answer = answer

    def is_correct(self, user_answer): #입력한 번호가 정답인지 판단한다.
        return user_answer == self.answer

    def display(self, number): #문제와 선택지를 화면에 출력한다.
        print("-"*40,"\n")
        print(f"[문제 {number}]")
        print(self.question)
        print()

        for choice_number, choices in enumerate(self.choices, start=1):
            print(f"[{choice_number}]{choices}")
        print("-"*40,"\n")

    def get_answer_text(self): #play_quiz 에서 오답일 때 정답을 알려줄 때
        answer_index = self.answer-1
        return self.choices[answer_index]

    def to_dict(self):# JSON 저장용 딕셔너리로 변환한다.
        #쓰이는 곳: QuizGame.save
        # json.dump 는 Quiz 객체를 저장할 줄 모르므로,
        # 저장 가능한 자료형(dict, list, str, int)으로 바꿔주는 역할이다.
        return {"question":self.question,"choices":self.choices,"answer":self.answer}

    @staticmethod
    def from_dict(quiz_data): # to_dict 의 반대 방향. dict 를 받아 Quiz(...) 를 만들어 반환한다.
        #data는 JSON 파일 자체가 아니라 파일에서 읽어낸 퀴즈 한 문제의 딕셔너리
        if not isinstance(quiz_data, dict):
            raise TypeError("퀴즈 데이터는 딕셔너리여야 합니다.")

        question = quiz_data["question"]
        choices = quiz_data["choices"]
        answer = quiz_data["answer"]

        if not isinstance(question, str) or not question.strip():
            raise ValueError("문제는 비어 있지 않은 문자열이어야 합니다.")

        if (
            not isinstance(choices, list)
            or len(choices) != 4
            or not all(isinstance(choice, str) and choice.strip() for choice in choices)
        ):
            raise ValueError("선택지는 비어 있지 않은 문자열 4개여야 합니다.")

        if (
            not isinstance(answer, int)
            or isinstance(answer, bool)
            or not 1 <= answer <= 4
        ):
            raise ValueError("정답은 1부터 4까지의 정수여야 합니다.")

        return Quiz(
            question,
            choices,
            answer,
        )
