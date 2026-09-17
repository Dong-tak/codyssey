-- =====================================================================
-- B6-1 : 입시 학원 고객관리 DB
-- 파일 : 03-queries.sql  (핵심 쿼리 18개)
-- 실행 : sqlite3 academy.db < sql/03-queries.sql > results/03-queries-output.txt
-- ---------------------------------------------------------------------
-- 범주별 개수 (과제 요구 15개 → 실제 18개)
--   기본 조회   4  : Q1~Q4      (WHERE / LIKE / ORDER BY+LIMIT / IS NULL)
--   조인        5  : Q5~Q9      (INNER 3 + LEFT 2)
--   집계        4  : Q10~Q13    (COUNT 2 / SUM 1 / AVG 1, 전부 GROUP BY)
--   서브쿼리    1  : Q14
--   수정·삭제   2  : Q15~Q16    (UPDATE / DELETE)
--   인덱스      2  : Q17~Q18    (CREATE INDEX + 적용 이유)
--
-- [주의] Q15, Q16 은 데이터를 변경한다.
--        처음부터 다시 돌리려면 01-schema.sql → 02-seed.sql 을 먼저 실행할 것.
-- =====================================================================

PRAGMA foreign_keys = ON;

-- [SQLite 전용] 출력 서식. 다른 DBMS에서는 이 3줄을 지우면 된다.
.headers on
.mode column


.print ''
.print '###################################################################'
.print '#  [A] 기본 조회 4개                                              #'
.print '###################################################################'

.print ''
.print '--- Q1. 수능을 앞둔 고3 재원생 명단 (조건 필터) -------------------'
-- 확인 내용: 두 조건을 AND 로 묶어 "고3이면서 아직 다니는" 학생만 추린다.
SELECT id, name AS 이름, school AS 학교, target_univ AS 목표대학
FROM student
WHERE grade = 3
  AND status = '재원'
ORDER BY name;

.print ''
.print '--- Q2. 교명에 "여고"가 들어가는 학교의 학생 검색 (부분 일치) -----'
-- 확인 내용: LIKE 와 와일드카드 % 로 정확한 값을 몰라도 검색이 되는지 본다.
SELECT name AS 이름, school AS 학교, grade AS 학년
FROM student
WHERE school LIKE '%여고%'
ORDER BY school;

.print ''
.print '--- Q3. 가장 최근에 등록한 학생 5명 (정렬 + 상위 N) ---------------'
-- 확인 내용: 신규 고객 유입을 보기 위해 등록일 내림차순 상위 5건만 자른다.
SELECT name AS 이름, school AS 학교, enrolled_at AS 등록일
FROM student
ORDER BY enrolled_at DESC
LIMIT 5;

.print ''
.print '--- Q4. 후속 조치가 아직 정해지지 않은 상담 건 (NULL 판정) --------'
-- 확인 내용: NULL 은 = 로 못 찾는다. IS NULL 로만 걸러진다. 관리 누락 탐지용.
SELECT id, student_id AS 학생번호, consulted_at AS 상담일, type AS 유형, memo AS 내용
FROM consultation
WHERE next_action IS NULL
ORDER BY consulted_at;


.print ''
.print '###################################################################'
.print '#  [B] 조인 5개  (INNER 3 / LEFT 2)                               #'
.print '###################################################################'

.print ''
.print '--- Q5. [INNER JOIN x2] 학생 - 보호자 연락처 - 담당 선생님 통합 명단 ---'
-- 확인 내용: 3개 테이블에 흩어진 정보를 한 줄로 합친다. 상담 전화 돌릴 때 쓰는 화면.
SELECT s.name    AS 학생,
       s.grade   AS 학년,
       p.name    AS 보호자,
       p.phone   AS 보호자연락처,
       t.name    AS 담당교사,
       t.subject AS 담당과목
FROM student s
INNER JOIN parent  p ON s.parent_id  = p.id
INNER JOIN teacher t ON s.teacher_id = t.id
ORDER BY s.grade DESC, s.name;

.print ''
.print '--- Q6. [INNER JOIN x2] 최근 상담 기록 상세 (누가 / 누구를 / 언제) ---'
-- 확인 내용: consultation 에는 id 만 있다. 사람 이름을 붙여야 읽을 수 있는 기록이 된다.
SELECT c.consulted_at AS 상담일,
       s.name         AS 학생,
       t.name         AS 상담교사,
       c.type         AS 유형,
       c.next_action  AS 후속조치
FROM consultation c
INNER JOIN student s ON c.student_id = s.id
INNER JOIN teacher t ON c.teacher_id = t.id
ORDER BY c.consulted_at DESC
LIMIT 10;

.print ''
.print '--- Q7. [INNER JOIN] 자녀를 2명 이상 보낸 학부모 (1:N 실증) -------'
-- 확인 내용: 같은 parent_id 를 공유하는 학생이 여러 명 = 1:N 이 실제로 성립함을 보인다.
SELECT p.name  AS 보호자,
       p.phone AS 연락처,
       COUNT(s.id)                AS 자녀수,
       GROUP_CONCAT(s.name, ', ') AS 자녀명  -- [SQLite/MySQL] 표준은 STRING_AGG
FROM parent p
INNER JOIN student s ON p.id = s.parent_id
GROUP BY p.id, p.name, p.phone
HAVING COUNT(s.id) >= 2
ORDER BY 자녀수 DESC;

.print ''
.print '--- Q8. [LEFT JOIN + IS NULL] 상담을 한 번도 받지 못한 학생 -------'
-- 확인 내용: 등록만 하고 관리에서 빠진 학생을 찾는다. INNER JOIN 이면 아예 안 나온다.
SELECT s.id, s.name AS 학생, s.school AS 학교, s.enrolled_at AS 등록일
FROM student s
LEFT JOIN consultation c ON s.id = c.student_id
WHERE c.id IS NULL          -- 짝이 없었다는 뜻
ORDER BY s.enrolled_at;

.print ''
.print '--- Q9. [LEFT JOIN] 담당 학생이 0명인 선생님까지 포함한 배정 현황 --'
-- 확인 내용: 업무량 균형 점검. 배정 0명인 선생님도 빠지지 않고 나와야 한다.
SELECT t.name    AS 선생님,
       t.subject AS 과목,
       COUNT(s.id) AS 담당학생수
FROM teacher t
LEFT JOIN student s ON t.id = s.teacher_id
GROUP BY t.id, t.name, t.subject
ORDER BY 담당학생수 DESC, t.name;


.print ''
.print '###################################################################'
.print '#  [C] 집계 4개  (COUNT / SUM / AVG + GROUP BY)                   #'
.print '###################################################################'

.print ''
.print '--- Q10. [COUNT] 선생님별 상담 진행 건수 랭킹 ---------------------'
-- 확인 내용: 누가 실제로 상담을 많이 뛰었는지. 담당 배정 수와는 다른 지표다.
SELECT t.name AS 선생님,
       t.subject AS 과목,
       COUNT(c.id) AS 상담건수
FROM consultation c
INNER JOIN teacher t ON c.teacher_id = t.id
GROUP BY t.id, t.name, t.subject
ORDER BY 상담건수 DESC
LIMIT 5;

.print ''
.print '--- Q11. [COUNT] 월별 상담 건수 추이 ------------------------------'
-- 확인 내용: 학원의 영업 활동량이 달마다 어떻게 변했는지 본다.
SELECT SUBSTR(consulted_at, 1, 7) AS 상담월,   -- 'YYYY-MM-DD' 앞 7글자
       COUNT(*) AS 상담건수
FROM consultation
GROUP BY 상담월
ORDER BY 상담월;

.print ''
.print '--- Q12. [SUM + HAVING] 총 납부액 100만원 이상인 학생 -------------'
-- 확인 내용: 매출 기여도 상위 고객. WHERE 로는 못 거른다(집계 후 조건이라 HAVING).
SELECT s.name AS 학생,
       COUNT(pm.id) AS 결제건수,
       SUM(pm.amount) AS 총납부액
FROM payment pm
INNER JOIN student s ON pm.student_id = s.id
WHERE pm.paid_at IS NOT NULL          -- 묶기 전: 실제 납부된 건만
GROUP BY s.id, s.name
HAVING SUM(pm.amount) >= 1000000      -- 묶은 후: 그룹 조건
ORDER BY 총납부액 DESC;

.print ''
.print '--- Q13. [AVG] 학년별 1인당 평균 납부액 (객단가) ------------------'
-- 확인 내용: 어느 학년이 매출에 가장 크게 기여하는지 본다.
SELECT s.grade AS 학년,
       COUNT(DISTINCT s.id) AS 학생수,
       AVG(pm.amount) AS 건당평균납부액,
       SUM(pm.amount) AS 학년총액
FROM student s
INNER JOIN payment pm ON s.id = pm.student_id
WHERE pm.paid_at IS NOT NULL
GROUP BY s.grade
ORDER BY s.grade;


.print ''
.print '###################################################################'
.print '#  [D] 서브쿼리 1개                                               #'
.print '###################################################################'

.print ''
.print '--- Q14. [서브쿼리] 평균보다 상담을 많이 받은 학생 ----------------'
-- 확인 내용: 전체 평균 상담 횟수를 먼저 구하고, 그 값을 다시 조건으로 쓴다.
SELECT s.name AS 학생,
       COUNT(c.id) AS 상담건수
FROM student s
INNER JOIN consultation c ON s.id = c.student_id
GROUP BY s.id, s.name
HAVING COUNT(c.id) > (
         -- 상담 기록이 있는 학생 1인당 평균 상담 횟수
         SELECT COUNT(*) * 1.0 / COUNT(DISTINCT student_id) FROM consultation
       )
ORDER BY 상담건수 DESC, s.name;


.print ''
.print '###################################################################'
.print '#  [E] 데이터 수정 및 삭제 2개                                    #'
.print '###################################################################'

.print ''
.print '--- Q15. [UPDATE] 담당 미배정 학생에게 담당 선생님 배정 -----------'
-- 확인 내용: UPDATE 전에 같은 WHERE 로 SELECT 를 먼저 돌려 대상이 맞는지 확인한다.
.print '(변경 전)'
SELECT id, name AS 이름, teacher_id AS 담당교사번호 FROM student WHERE teacher_id IS NULL;

UPDATE student
SET teacher_id = (SELECT id FROM teacher WHERE name = '임수빈')
WHERE teacher_id IS NULL;

.print '(변경 후)'
SELECT s.id, s.name AS 이름, t.name AS 담당교사
FROM student s INNER JOIN teacher t ON s.teacher_id = t.id
WHERE s.name = '배시윤';

.print ''
.print '--- Q16. [DELETE] 퇴원생의 미납 청구 건 삭제 (청구 취소) ----------'
-- 확인 내용: 퇴원했는데 남아 있는 미납 청구서는 유효하지 않으므로 지운다.
.print '(삭제 전 - 삭제 대상)'
SELECT pm.id, s.name AS 학생, s.status AS 상태, pm.pay_month AS 수강월, pm.amount AS 금액
FROM payment pm INNER JOIN student s ON pm.student_id = s.id
WHERE s.status = '퇴원' AND pm.paid_at IS NULL;

DELETE FROM payment
WHERE paid_at IS NULL
  AND student_id IN (SELECT id FROM student WHERE status = '퇴원');

.print '(삭제 후 - 남은 미납 건 전체)'
SELECT pm.id, s.name AS 학생, s.status AS 상태, pm.pay_month AS 수강월, pm.amount AS 금액
FROM payment pm INNER JOIN student s ON pm.student_id = s.id
WHERE pm.paid_at IS NULL
ORDER BY pm.pay_month;


.print ''
.print '###################################################################'
.print '#  [F] 인덱스 2개                                                 #'
.print '###################################################################'

.print ''
.print '--- Q17. 상담 테이블의 student_id 인덱스 --------------------------'
-- 적용 이유: 상담 조회는 거의 항상 "이 학생의 상담"이라 student_id 로 필터·조인한다(Q6/Q8/Q14).
CREATE INDEX IF NOT EXISTS idx_consultation_student ON consultation(student_id);

.print ''
.print '--- Q18. 결제 테이블의 pay_month 인덱스 ---------------------------'
-- 적용 이유: 월별 매출 집계에서 매번 pay_month 로 묶고 거르기 때문(월말 정산 쿼리).
CREATE INDEX IF NOT EXISTS idx_payment_month ON payment(pay_month);

.print ''
.print '--- 생성된 인덱스 확인 --------------------------------------------'
-- [SQLite 전용] 인덱스 목록 조회. MySQL은 SHOW INDEX, PostgreSQL은 \di
SELECT name AS 인덱스명, tbl_name AS 대상테이블
FROM sqlite_master
WHERE type = 'index' AND name LIKE 'idx_%';

.print ''
.print '--- 인덱스가 실제로 쓰이는지 실행계획으로 확인 ---------------------'
-- [SQLite 전용] EXPLAIN QUERY PLAN. "USING INDEX idx_..." 가 보이면 인덱스를 탄 것.
EXPLAIN QUERY PLAN
SELECT * FROM consultation WHERE student_id = 1;

EXPLAIN QUERY PLAN
SELECT pay_month, SUM(amount) FROM payment GROUP BY pay_month;

.print ''
.print '=================== 쿼리 18개 실행 완료 ==========================='
