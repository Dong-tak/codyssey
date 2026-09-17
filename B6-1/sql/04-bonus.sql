-- =====================================================================
-- B6-1 : 입시 학원 고객관리 DB
-- 파일 : 04-bonus.sql  (보너스 과제 3종)
-- 실행 : sqlite3 academy.db < sql/04-bonus.sql > results/04-bonus-output.txt
-- ---------------------------------------------------------------------
-- B1. 같은 요구를 JOIN / 서브쿼리 두 방식으로 풀고 비교
-- B2. 데이터 정합성 일부러 깨뜨려 보기 (에러 4종 재현)
-- B3. 미니 리포트 - 이 DB로 뽑는 핵심 지표 3개
--
-- [전제] 03-queries.sql 까지 실행한 상태의 DB를 대상으로 한다.
-- =====================================================================

PRAGMA foreign_keys = ON;

.headers on
.mode column
-- [SQLite 전용] 에러가 나도 멈추지 말고 계속 진행 (B2에서 일부러 에러를 낸다)
.bail off


.print ''
.print '###################################################################'
.print '#  B1. 같은 요구를 두 방식으로 풀기                               #'
.print '#      요구: "상담을 한 번도 받지 못한 학생을 찾아라"             #'
.print '###################################################################'

.print ''
.print '--- 방식 1: LEFT JOIN + IS NULL ------------------------------------'
-- 학생 전체를 왼쪽에 놓고 상담을 붙인 뒤, 붙지 않은(=NULL) 행만 남긴다.
SELECT s.id, s.name AS 학생, s.school AS 학교
FROM student s
LEFT JOIN consultation c ON s.id = c.student_id
WHERE c.id IS NULL
ORDER BY s.id;

.print ''
.print '--- 방식 2: NOT IN 서브쿼리 ----------------------------------------'
-- 상담 기록에 등장하는 학생 번호 목록을 먼저 만들고, 거기 없는 학생을 찾는다.
SELECT s.id, s.name AS 학생, s.school AS 학교
FROM student s
WHERE s.id NOT IN (SELECT student_id FROM consultation)
ORDER BY s.id;

.print ''
.print '--- 방식 3: NOT EXISTS 서브쿼리 ------------------------------------'
-- 학생 한 명마다 "이 학생의 상담이 존재하는가?"를 묻고, 없으면 통과시킨다.
SELECT s.id, s.name AS 학생, s.school AS 학교
FROM student s
WHERE NOT EXISTS (SELECT 1 FROM consultation c WHERE c.student_id = s.id)
ORDER BY s.id;

.print ''
.print '--- [함정 실증] NOT IN 은 목록에 NULL 이 섞이면 결과가 통째로 빈다 ---'
-- 위 3개는 결과가 같았다. 하지만 서브쿼리가 보는 컬럼에 NULL 이 들어갈 수 있으면
-- NOT IN 만 조용히 무너진다. student_id 는 NOT NULL 이라 안전했지만,
-- teacher_id 는 NULL 을 허용하므로 여기서 차이가 드러난다.
--
-- 이유: NOT IN 은 내부적으로 (t.id <> v1 AND t.id <> v2 AND ...) 로 풀린다.
--       v 중 하나가 NULL 이면 그 비교는 TRUE 도 FALSE 도 아닌 UNKNOWN 이 되고,
--       AND 로 묶인 전체가 절대 TRUE 가 될 수 없어 결과가 0행이 된다.

.print '(준비) 함정을 재현하려고 담당 미배정 학생을 한 명 만든다'
-- 03-queries.sql 의 Q15 를 이미 돌렸든 아니든 같은 상태에서 출발하도록 맞춘다.
UPDATE student SET teacher_id = NULL WHERE name = '배시윤';
SELECT COUNT(*) AS 담당미배정학생수 FROM student WHERE teacher_id IS NULL;

.print '(A) NOT IN + NULL 이 섞인 목록  -> 결과가 0행으로 사라진다'
SELECT t.id, t.name AS 담당학생없는선생님
FROM teacher t
WHERE t.id NOT IN (SELECT teacher_id FROM student);

.print '(B) NOT EXISTS 로 같은 질문  -> NULL 과 무관하게 정상 동작'
SELECT t.id, t.name AS 담당학생없는선생님
FROM teacher t
WHERE NOT EXISTS (SELECT 1 FROM student s WHERE s.teacher_id = t.id);

.print '(C) NOT IN 을 고치려면 서브쿼리에서 NULL 을 먼저 걸러야 한다'
SELECT t.id, t.name AS 담당학생없는선생님
FROM teacher t
WHERE t.id NOT IN (SELECT teacher_id FROM student WHERE teacher_id IS NOT NULL);

.print '(정리) 담당을 다시 배정해 원래 상태로 되돌린다'
UPDATE student SET teacher_id = (SELECT id FROM teacher WHERE name = '임수빈')
WHERE teacher_id IS NULL;

.print ''
.print '--- 세 방식의 실행계획 비교 ----------------------------------------'
-- [SQLite 전용] EXPLAIN QUERY PLAN
.print '[LEFT JOIN]'
EXPLAIN QUERY PLAN
SELECT s.id FROM student s LEFT JOIN consultation c ON s.id = c.student_id WHERE c.id IS NULL;
.print '[NOT IN]'
EXPLAIN QUERY PLAN
SELECT s.id FROM student s WHERE s.id NOT IN (SELECT student_id FROM consultation);
.print '[NOT EXISTS]'
EXPLAIN QUERY PLAN
SELECT s.id FROM student s WHERE NOT EXISTS (SELECT 1 FROM consultation c WHERE c.student_id = s.id);


.print ''
.print '###################################################################'
.print '#  B2. 데이터 정합성 일부러 깨뜨려 보기                           #'
.print '#      아래 5개는 전부 "실패해야 정상"이다.                       #'
.print '###################################################################'

.print ''
.print '--- [실패 예상 1] 존재하지 않는 학부모(id=999)로 학생 등록 ---------'
-- 기대 에러: FOREIGN KEY constraint failed
-- 원인: parent 테이블에 999번이 없는데 student.parent_id 가 그걸 가리키려 함
-- 해결: 학부모를 먼저 INSERT 하고, 그때 생성된 id 를 parent_id 로 넣는다
INSERT INTO student (name, school, grade, status, enrolled_at, parent_id, teacher_id)
VALUES ('유령학생', '없는고', 3, '재원', '2026-09-17', 999, 1);

.print ''
.print '--- [실패 예상 2] 이미 등록된 전화번호로 학부모 추가 ---------------'
-- 기대 에러: UNIQUE constraint failed: parent.phone
-- 원인: 같은 번호가 두 명의 고객이 되면 누구인지 식별할 수 없다
-- 해결: 기존 고객인지 먼저 조회하고, 맞으면 INSERT 가 아니라 UPDATE 를 한다
INSERT INTO parent (name, phone, email, registered_at)
VALUES ('중복고객', '010-2001-1101', NULL, '2026-09-17');

.print ''
.print '--- [실패 예상 3] 이름 없이 학생 등록 ------------------------------'
-- 기대 에러: NOT NULL constraint failed: student.name
-- 원인: 이름 없는 학생은 데이터로서 의미가 없다
-- 해결: 이름을 필수 입력값으로 받는다
INSERT INTO student (name, school, grade, status, enrolled_at, parent_id)
VALUES (NULL, '한영고', 2, '재원', '2026-09-17', 1);

.print ''
.print '--- [실패 예상 4] 자녀가 남아 있는 학부모 삭제 ---------------------'
-- 기대 에러: FOREIGN KEY constraint failed
-- 원인: student 가 아직 그 parent_id 를 가리키고 있다 (고아 데이터 방지)
-- 해결: 자녀를 먼저 처리(삭제 또는 다른 보호자로 이전)한 뒤 학부모를 지운다
DELETE FROM parent WHERE id = 1;

.print ''
.print '--- [실패 예상 5] 학년에 4를 입력 -----------------------------------'
-- 기대 에러: CHECK constraint failed
-- 원인: 고등학교 학년은 1~3 뿐이다. 타입만 INTEGER 로 두면 4도 들어간다
-- 해결: CHECK (grade BETWEEN 1 AND 3) 로 도메인을 좁힌다
INSERT INTO student (name, school, grade, status, enrolled_at, parent_id)
VALUES ('사학년', '한영고', 4, '재원', '2026-09-17', 1);

.print ''
.print '--- [검증] 위 5건이 전부 막혔으므로 행 수는 그대로여야 한다 --------'
SELECT (SELECT COUNT(*) FROM student) AS 학생수,
       (SELECT COUNT(*) FROM parent)  AS 학부모수;


.print ''
.print '###################################################################'
.print '#  B3. 미니 리포트 - 핵심 지표 3개                                #'
.print '###################################################################'

.print ''
.print '--- 지표 1. 선생님별 업무 현황 (담당 학생 수 + 상담 건수) ----------'
-- 쓰임새: 담당은 많은데 상담이 적은 선생님 = 관리 공백. 재배정 판단 근거.
SELECT t.name    AS 선생님,
       t.subject AS 과목,
       (SELECT COUNT(*) FROM student s      WHERE s.teacher_id = t.id) AS 담당학생수,
       (SELECT COUNT(*) FROM consultation c WHERE c.teacher_id = t.id) AS 상담건수
FROM teacher t
ORDER BY 담당학생수 DESC, 상담건수 DESC;

.print ''
.print '--- 지표 2. 월별 상담 활동량 추이 (유형별 분해) --------------------'
-- 쓰임새: 신규 유입(입학상담)과 기존 관리(정기/성적/진로)의 비중 변화를 본다.
SELECT SUBSTR(consulted_at, 1, 7) AS 월,
       COUNT(*) AS 전체,
       SUM(CASE WHEN type = '입학상담' THEN 1 ELSE 0 END) AS 입학상담,
       SUM(CASE WHEN type = '정기상담' THEN 1 ELSE 0 END) AS 정기상담,
       SUM(CASE WHEN type = '성적상담' THEN 1 ELSE 0 END) AS 성적상담,
       SUM(CASE WHEN type = '진로상담' THEN 1 ELSE 0 END) AS 진로상담
FROM consultation
GROUP BY 월
ORDER BY 월;

.print ''
.print '--- 지표 3-1. 미납 학생 목록 (수금 대상) ---------------------------'
-- 쓰임새: 보호자 연락처까지 붙여서 그대로 전화 돌릴 수 있는 형태로 뽑는다.
SELECT s.name  AS 학생,
       s.status AS 상태,
       p.name  AS 보호자,
       p.phone AS 연락처,
       pm.pay_month AS 미납월,
       pm.amount    AS 미납액
FROM payment pm
INNER JOIN student s ON pm.student_id = s.id
INNER JOIN parent  p ON s.parent_id   = p.id
WHERE pm.paid_at IS NULL
ORDER BY pm.pay_month, s.name;

.print ''
.print '--- 지표 3-2. 월별 청구 / 수납 / 미납 요약 -------------------------'
-- 쓰임새: 한 줄로 보는 수금 현황. 미납률이 이번 달의 리스크 지표다.
SELECT pay_month AS 월,
       COUNT(*)                                                   AS 청구건수,
       SUM(amount)                                                AS 청구총액,
       SUM(CASE WHEN paid_at IS NOT NULL THEN amount ELSE 0 END)   AS 수납액,
       SUM(CASE WHEN paid_at IS NULL     THEN amount ELSE 0 END)   AS 미납액,
       ROUND(SUM(CASE WHEN paid_at IS NULL THEN amount ELSE 0 END) * 100.0
             / SUM(amount), 1)                                     AS 미납률
FROM payment
GROUP BY pay_month
ORDER BY pay_month;

.print ''
.print '=================== 보너스 과제 실행 완료 ========================='
