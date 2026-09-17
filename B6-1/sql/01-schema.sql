-- =====================================================================
-- B6-1 : 입시 학원 고객관리 DB
-- 파일 : 01-schema.sql  (스키마 생성 스크립트)
-- DBMS : SQLite 3.45.3
-- 실행 : sqlite3 academy.db < sql/01-schema.sql
-- ---------------------------------------------------------------------
-- 테이블 5개 / 1:N 관계 5개
--   parent  1 : N student        (student.parent_id)
--   teacher 1 : N student        (student.teacher_id)
--   student 1 : N consultation   (consultation.student_id)
--   teacher 1 : N consultation   (consultation.teacher_id)
--   student 1 : N payment        (payment.student_id)
--
-- FK는 항상 N쪽(자식)에 둔다.
-- 예) parent 에 student_id 를 두면 자녀가 2명인 학부모를 표현할 수 없다.
-- =====================================================================

-- [SQLite 전용] SQLite는 외래키 제약이 기본 OFF 이므로 접속할 때마다 켜야 한다.
-- 이 줄이 없으면 없는 값을 참조하는 INSERT 가 그냥 통과해 버린다.
PRAGMA foreign_keys = ON;

-- 재실행 가능하도록 자식 테이블부터 역순으로 제거한다.
-- (부모를 먼저 지우면 FK 때문에 막힌다)
DROP TABLE IF EXISTS payment;
DROP TABLE IF EXISTS consultation;
DROP TABLE IF EXISTS student;
DROP TABLE IF EXISTS parent;
DROP TABLE IF EXISTS teacher;


-- ---------------------------------------------------------------------
-- 1) teacher : 선생님
-- ---------------------------------------------------------------------
CREATE TABLE teacher (
    -- [SQLite 전용] AUTOINCREMENT. MySQL은 AUTO_INCREMENT, PostgreSQL은 SERIAL
    id        INTEGER PRIMARY KEY AUTOINCREMENT,
    name      TEXT    NOT NULL,                  -- 이름은 반드시 있어야 한다
    subject   TEXT    NOT NULL,                  -- 국어 / 수학 / 영어 / 탐구
    phone     TEXT    NOT NULL UNIQUE,           -- 연락처 중복 금지
    hired_at  DATE    NOT NULL                   -- 입사일
);


-- ---------------------------------------------------------------------
-- 2) parent : 학부모 (= 학원의 실제 고객, 결제 주체)
-- ---------------------------------------------------------------------
CREATE TABLE parent (
    id             INTEGER PRIMARY KEY AUTOINCREMENT,
    name           TEXT    NOT NULL,
    -- 학원에서 고객을 식별하는 기준값이라 중복되면 안 된다.
    phone          TEXT    NOT NULL UNIQUE,
    email          TEXT,                          -- 선택 항목이라 NULL 허용
    registered_at  DATE    NOT NULL               -- 최초 문의일
);


-- ---------------------------------------------------------------------
-- 3) student : 학생
--    parent / teacher 두 부모를 갖는 N쪽 테이블
-- ---------------------------------------------------------------------
CREATE TABLE student (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    name         TEXT    NOT NULL,
    school       TEXT    NOT NULL,
    grade        INTEGER NOT NULL CHECK (grade BETWEEN 1 AND 3),
    target_univ  TEXT,                            -- 목표 대학 미정 가능 → NULL 허용
    -- 재원 / 휴원 / 퇴원. 값이 비면 관리가 안 되므로 기본값을 준다.
    status       TEXT    NOT NULL DEFAULT '재원'
                 CHECK (status IN ('재원', '휴원', '퇴원')),
    enrolled_at  DATE    NOT NULL,

    -- 보호자는 결제 주체이므로 반드시 있어야 한다 → NOT NULL
    parent_id    INTEGER NOT NULL,
    -- 담당 선생님은 등록 직후 미배정일 수 있다 → NULL 허용
    teacher_id   INTEGER,

    FOREIGN KEY (parent_id)  REFERENCES parent(id),
    FOREIGN KEY (teacher_id) REFERENCES teacher(id)
);


-- ---------------------------------------------------------------------
-- 4) consultation : 상담 기록 (학원의 영업 활동 로그)
-- ---------------------------------------------------------------------
CREATE TABLE consultation (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id    INTEGER NOT NULL,               -- 누구를
    teacher_id    INTEGER NOT NULL,               -- 누가
    consulted_at  DATE    NOT NULL,               -- 언제
    type          TEXT    NOT NULL
                  CHECK (type IN ('입학상담', '정기상담', '성적상담', '진로상담')),
    memo          TEXT,
    -- 후속 조치. NULL 이면 "아직 조치가 정해지지 않음" 을 뜻한다.
    next_action   TEXT,

    FOREIGN KEY (student_id) REFERENCES student(id),
    FOREIGN KEY (teacher_id) REFERENCES teacher(id)
);


-- ---------------------------------------------------------------------
-- 5) payment : 결제 내역
-- ---------------------------------------------------------------------
CREATE TABLE payment (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id  INTEGER NOT NULL,
    amount      INTEGER NOT NULL CHECK (amount > 0),   -- 수강료(원)
    pay_month   TEXT    NOT NULL,                      -- 수강 월 'YYYY-MM'
    -- 납부일. NULL 이면 미납.
    -- is_paid 같은 별도 플래그를 두면 두 값이 어긋날 수 있어 한 컬럼으로 통일했다.
    paid_at     DATE,
    method      TEXT CHECK (method IN ('카드', '계좌이체', '현금')),

    FOREIGN KEY (student_id) REFERENCES student(id),
    -- 같은 학생의 같은 달 청구서가 두 번 생기지 않도록 복합 UNIQUE
    UNIQUE (student_id, pay_month)
);
