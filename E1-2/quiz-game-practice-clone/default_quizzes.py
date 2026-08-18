"""state.json 이 없을 때 사용할 기본 퀴즈 데이터."""

from quiz import Quiz


def get_default_quizzes():

    # 이 함수가 별도 파일에 있는 이유:
    #   퀴즈는 앞으로 계속 늘리고 고칠 데이터이고, quiz_game.py 의 로직은
    #   거의 안 바뀐다. 변경 빈도가 다른 것을 분리해 둔 것.
    return [
    Quiz(
        "수강(학번, 과목코드, 학생이름) 테이블의 기본키가 (학번, 과목코드)일 때, "
        "학번 → 학생이름 관계가 존재한다. 이 부분 함수 종속을 제거하기 위해 필요한 정규형은?",
        ["제1정규형", "제2정규형", "제3정규형", "BCNF"],
        2,
    ),
    Quiz(
        """고객별 주문 건수를 구한 뒤, 주문이 3건 이상인 고객만 조회하려고 한다.
다음 SQL의 빈칸에 들어갈 절은?

SELECT customer_id, COUNT(*)
FROM orders
GROUP BY customer_id
( 빈칸 ) COUNT(*) >= 3;""",
        ["WHERE", "HAVING", "ORDER BY", "DISTINCT"],
        2,
    ),
    Quiz(
        "사원 테이블의 모든 사원을 조회하되, 부서가 배정되지 않은 사원도 결과에 포함하고 "
        "부서명은 NULL로 표시하려고 한다. 가장 알맞은 조인은?",
        ["INNER JOIN", "LEFT OUTER JOIN", "RIGHT OUTER JOIN", "CROSS JOIN"],
        2,
    ),
    Quiz(
        """판매수수료 값이 다음과 같을 때 COUNT(판매수수료)의 결과는?

100, NULL, 0, 50""",
        ["2", "3", "4", "오류 발생"],
        2,
    ),
    Quiz(
        "하나의 거래에서 출금 처리 후 입금 처리 전에 오류가 발생하여 ROLLBACK을 실행했다. "
        "두 작업이 모두 취소되어야 한다는 특성과 가장 관련 깊은 것은?",
        ["원자성(Atomicity)", "고립성(Isolation)", "일관성(Consistency)", "지속성(Durability)"],
        1,
    ),
]
