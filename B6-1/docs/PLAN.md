# B6-1 기획서 — 입시 학원 고객관리 DB

## 1. 주제 선정

**입시 학원 고객관리(CRM) 데이터베이스**

학원은 "학생을 가르치는 곳"이지만, 운영 관점에서는 **학부모가 고객**이고
**상담이 영업 활동**이며 **결제가 매출**이다. 이 세 축을 테이블로 나눠 관리한다.

### 왜 이 주제인가
- 학생 / 학부모 / 선생님이 자연스럽게 **서로 다른 개체**로 분리된다.
- "학부모 1명 - 자녀 여러 명", "선생님 1명 - 담당 학생 여러 명"처럼
  **1:N 관계가 억지 없이 2개 이상** 나온다.
- 상담 건수, 선생님별 담당 인원, 미납 학부모처럼 **실무형 집계 요구**가 명확하다.

### 이 DB로 답하고 싶은 질문
1. 담당 선생님별로 학생이 몇 명씩 배정돼 있나? (업무량 균형)
2. 등록만 하고 **상담을 한 번도 못 받은 학생**은 누구인가? (관리 누락)
3. 이번 달 매출과 미납 학생은? (수금)

---

## 2. 사용 DB

| 항목 | 선택 | 이유 |
|---|---|---|
| DBMS | **SQLite 3.45.3** | 파일 1개 = DB 1개. 서버 실행 불필요, 제출물에 `.db` 파일을 그대로 넣을 수 있음 |
| 실행 도구 | `sqlite3` CLI | 결과를 텍스트로 바로 저장할 수 있어 캡처 자료 만들기 쉬움 |

> SQLite는 FK가 **기본으로 꺼져 있으므로** 모든 스크립트 첫 줄에
> `PRAGMA foreign_keys = ON;` 을 넣는다. 이게 없으면 FK 제약이 동작하지 않는다.

DB 고유 문법을 쓰는 곳은 쿼리에 주석으로 명시한다.
(예: `AUTOINCREMENT`, 날짜 포맷 함수 `strftime`)

---

## 3. ERD (텍스트)

```
  teacher                        parent
  ┌──────────────┐               ┌──────────────┐
  │ id      (PK) │               │ id      (PK) │
  │ name         │               │ name         │
  │ subject      │               │ phone (UQ)   │
  │ phone        │               │ email        │
  │ hired_at     │               │ registered_at│
  └──────┬───────┘               └──────┬───────┘
         │ 1                            │ 1
         │                              │
         │ N                            │ N
         └──────────┐      ┌────────────┘
                    ▼      ▼
                  student
                  ┌────────────────────┐
                  │ id            (PK) │
                  │ name               │
                  │ school             │
                  │ grade              │
                  │ target_univ        │
                  │ status             │
                  │ enrolled_at        │
                  │ parent_id     (FK) │──→ parent.id
                  │ teacher_id    (FK) │──→ teacher.id
                  └───┬────────────┬───┘
                  1   │            │   1
                      │            │
                  N   ▼            ▼   N
            consultation        payment
            ┌──────────────┐    ┌──────────────┐
            │ id      (PK) │    │ id      (PK) │
            │ student_id FK│    │ student_id FK│
            │ teacher_id FK│    │ amount       │
            │ consulted_at │    │ pay_month    │
            │ type         │    │ paid_at      │
            │ memo         │    │ method       │
            │ next_action  │    └──────────────┘
            └──────────────┘
```

### 1:N 관계 목록 (요구: 2개 이상 → **5개**)

| # | 관계 | 1쪽 | N쪽 | FK 위치 | 의미 |
|---|---|---|---|---|---|
| 1 | 학부모-자녀 | `parent` | `student` | `student.parent_id` | 학부모 1명이 자녀 여러 명을 등록할 수 있다 |
| 2 | 담당-학생 | `teacher` | `student` | `student.teacher_id` | 선생님 1명이 학생 여러 명을 담당한다 |
| 3 | 학생-상담 | `student` | `consultation` | `consultation.student_id` | 학생 1명에게 상담 기록이 여러 건 쌓인다 |
| 4 | 상담자-상담 | `teacher` | `consultation` | `consultation.teacher_id` | 선생님 1명이 상담을 여러 건 진행한다 |
| 5 | 학생-결제 | `student` | `payment` | `payment.student_id` | 학생 1명이 매월 결제한다 |

> **FK는 항상 N쪽에 둔다.** 반대로 `parent`에 `student_id`를 두면
> 자녀가 2명인 학부모를 표현할 수 없다.

---

## 4. 테이블 상세 설계

### 4.1 `teacher` — 선생님

| 컬럼 | 타입 | 제약 | 설명 |
|---|---|---|---|
| `id` | INTEGER | PK, AUTOINCREMENT | 선생님 번호 |
| `name` | TEXT | **NOT NULL** | 이름 |
| `subject` | TEXT | NOT NULL | 담당 과목 (국어/수학/영어/탐구) |
| `phone` | TEXT | **UNIQUE** | 연락처 |
| `hired_at` | DATE | NOT NULL | 입사일 |

### 4.2 `parent` — 학부모 (= 고객)

| 컬럼 | 타입 | 제약 | 설명 |
|---|---|---|---|
| `id` | INTEGER | PK, AUTOINCREMENT | 학부모 번호 |
| `name` | TEXT | **NOT NULL** | 이름 |
| `phone` | TEXT | **NOT NULL, UNIQUE** | 연락처. 학원 고객 식별의 핵심이라 중복 금지 |
| `email` | TEXT | | 이메일 (선택) |
| `registered_at` | DATE | NOT NULL | 최초 문의일 |

### 4.3 `student` — 학생

| 컬럼 | 타입 | 제약 | 설명 |
|---|---|---|---|
| `id` | INTEGER | PK, AUTOINCREMENT | 학생 번호 |
| `name` | TEXT | **NOT NULL** | 이름 |
| `school` | TEXT | NOT NULL | 재학 고등학교 |
| `grade` | INTEGER | NOT NULL, CHECK 1~3 | 학년 |
| `target_univ` | TEXT | | 목표 대학 (미정일 수 있어 NULL 허용) |
| `status` | TEXT | NOT NULL, DEFAULT '재원' | 재원 / 휴원 / 퇴원 |
| `enrolled_at` | DATE | NOT NULL | 등록일 |
| `parent_id` | INTEGER | NOT NULL, **FK → parent.id** | 보호자 |
| `teacher_id` | INTEGER | **FK → teacher.id** | 담당 선생님 (미배정이면 NULL) |

> `teacher_id`만 NULL을 허용한 이유: 등록 직후에는 담당이 아직 안 정해질 수 있다.
> 반대로 `parent_id`는 결제 주체라 **반드시 있어야 하므로** NOT NULL.

### 4.4 `consultation` — 상담 기록

| 컬럼 | 타입 | 제약 | 설명 |
|---|---|---|---|
| `id` | INTEGER | PK, AUTOINCREMENT | 상담 번호 |
| `student_id` | INTEGER | NOT NULL, **FK → student.id** | 대상 학생 |
| `teacher_id` | INTEGER | NOT NULL, **FK → teacher.id** | 상담한 선생님 |
| `consulted_at` | DATE | NOT NULL | 상담일 |
| `type` | TEXT | NOT NULL | 입학상담 / 정기상담 / 성적상담 / 진로상담 |
| `memo` | TEXT | | 상담 내용 |
| `next_action` | TEXT | | 후속 조치. **NULL이면 "아직 조치 미정"** |

### 4.5 `payment` — 결제 내역

| 컬럼 | 타입 | 제약 | 설명 |
|---|---|---|---|
| `id` | INTEGER | PK, AUTOINCREMENT | 결제 번호 |
| `student_id` | INTEGER | NOT NULL, **FK → student.id** | 대상 학생 |
| `amount` | INTEGER | NOT NULL | 금액(원) |
| `pay_month` | TEXT | NOT NULL | 수강 월 (`2026-09`) |
| `paid_at` | DATE | | **NULL이면 미납** |
| `method` | TEXT | | 카드 / 계좌이체 / 현금 |

> `paid_at IS NULL` 하나로 미납을 표현한다. 별도 `is_paid` 플래그를 두면
> 두 값이 어긋날 수 있어서(납부일은 있는데 플래그는 false) 한 컬럼으로 통일했다.

---

## 5. 샘플 데이터 계획 (테이블당 10행 이상)

| 테이블 | 행 수 | 구성 방향 |
|---|---|---|
| `teacher` | 10 | 국어·수학·영어·탐구 과목이 섞이도록 |
| `parent` | 12 | 자녀 2명인 학부모를 2~3명 포함 (1:N 증명용) |
| `student` | 15 | 1~3학년 분포, `status`에 휴원/퇴원 각 1명 이상, **담당 미배정(NULL) 1명** |
| `consultation` | 25 | **상담 0건인 학생을 2명 남긴다** (LEFT JOIN 쿼리용) |
| `payment` | 30 | `paid_at IS NULL`인 미납 3~4건 포함 |

> **입력 순서 (FK 때문에 반드시 지킴)**
> `teacher` → `parent` → `student` → `consultation` → `payment`
> 부모 테이블이 먼저 채워져야 자식 테이블 INSERT가 통과한다.

---

## 6. 핵심 쿼리 16개 설계 (요구: 15개 이상)

### 기본 조회 (요구 4개 이상 → 4개)

| # | 쿼리 | 확인 내용 | 사용 문법 |
|---|---|---|---|
| Q1 | 고3 재원생 목록 | 조건 필터 | `WHERE` |
| Q2 | 특정 고등학교 학생 검색 | 부분 문자열 검색 | `WHERE ... LIKE` |
| Q3 | 최근 등록한 학생 5명 | 정렬 + 상위 N | `ORDER BY DESC`, `LIMIT` |
| Q4 | 후속 조치가 안 정해진 상담 건 | NULL 판정 | `WHERE ... IS NULL` |

### 조인 (요구 4개 이상, INNER 2+ / LEFT 1+ → INNER 3 + LEFT 2)

| # | 쿼리 | 확인 내용 | 종류 |
|---|---|---|---|
| Q5 | 학생 + 보호자 연락처 + 담당 선생님 한눈에 | 3개 테이블 결합 | `INNER JOIN` ×2 |
| Q6 | 상담 기록 상세 (누가 누구를 언제) | 기록에 이름 붙이기 | `INNER JOIN` ×2 |
| Q7 | 자녀가 2명 이상인 학부모 | 같은 부모를 공유하는 학생 | `INNER JOIN` + `GROUP BY` |
| Q8 | **상담을 한 번도 안 받은 학생** | 관리 누락 탐지 | `LEFT JOIN` + `IS NULL` |
| Q9 | 담당 선생님 미배정 학생 포함 전체 명단 | 짝이 없어도 다 보기 | `LEFT JOIN` |

### 집계 (요구 3개 이상, COUNT/SUM/AVG 중 2개 + GROUP BY → 4개)

| # | 쿼리 | 확인 내용 | 함수 |
|---|---|---|---|
| Q10 | 선생님별 담당 학생 수 랭킹 | 업무량 분포 | `COUNT` + `GROUP BY` + `ORDER BY` |
| Q11 | 월별 상담 건수 추이 | 영업 활동량 | `COUNT` + `GROUP BY` |
| Q12 | 학생별 총 납부액 (10만원 이상만) | 매출 기여도 | `SUM` + `GROUP BY` + `HAVING` |
| Q13 | 학년별 평균 납부액 | 학년별 객단가 | `AVG` + `GROUP BY` |

### 서브쿼리 (요구 1개 이상 → 1개)

| # | 쿼리 | 확인 내용 |
|---|---|---|
| Q14 | 평균보다 상담을 많이 받은 학생 | 집계 결과를 다시 조건으로 사용 |

### 수정 및 삭제 (요구 2개 → 2개)

| # | 쿼리 | 확인 내용 |
|---|---|---|
| Q15 | 특정 학생을 '휴원'으로 변경 + 담당 재배정 | `UPDATE` |
| Q16 | 퇴원생의 미납(취소) 결제 건 삭제 | `DELETE` |

### 인덱스 (요구 1개 이상 → 2개)

| # | 쿼리 | 적용 이유 |
|---|---|---|
| Q17 | `CREATE INDEX idx_consultation_student ON consultation(student_id)` | 상담 조회는 거의 항상 "이 학생의 상담"이라 `student_id`로 필터·조인한다 |
| Q18 | `CREATE INDEX idx_payment_month ON payment(pay_month)` | 월별 매출 집계에서 매번 `pay_month`로 묶기 때문 |

> **총 18개** — 요구 15개를 충족한다.

---

## 7. 보너스 과제 계획

1. **같은 요구를 JOIN과 서브쿼리 두 방식으로**
   "상담을 한 번도 안 받은 학생"을 `LEFT JOIN + IS NULL`(Q8)과
   `NOT IN (SELECT ...)` 두 가지로 작성하고, `NOT IN`은 서브쿼리 결과에
   NULL이 하나라도 있으면 **결과가 통째로 비는** 함정이 있다는 점을 기록한다.

2. **정합성 일부러 깨뜨리기**
   - 존재하지 않는 `parent_id`로 학생 INSERT → FK 에러
   - 이미 있는 `phone`으로 학부모 INSERT → UNIQUE 에러
   - `name` 없이 학생 INSERT → NOT NULL 에러
   - 자녀가 남아 있는 `parent` 삭제 시도 → FK 에러
   각각 에러 메시지와 올바른 해결 방법을 기록한다.

3. **미니 리포트 — 핵심 지표 3개**
   - 지표①: **선생님별 담당 학생 수** (업무량 균형)
   - 지표②: **월별 상담 건수 추이** (영업 활동량)
   - 지표③: **미납 학생 목록과 미납 총액** (수금 리스크)

---

## 8. 제출물 구성

```
B6-1/
├── sql/
│   ├── 01-schema.sql       # CREATE TABLE + 제약조건 + 인덱스
│   ├── 02-seed.sql         # 샘플 데이터 INSERT
│   ├── 03-queries.sql      # 핵심 쿼리 18개 (각 쿼리 위에 한 줄 설명)
│   └── 04-bonus.sql        # 보너스 과제 (정합성 위반 시도 + 미니 리포트)
├── results/                # 실행 결과 캡처 (텍스트 + 스크린샷)
│   ├── 03-queries-output.txt
│   └── ...
├── docs/
│   ├── PLAN.md             # 이 문서
│   ├── CHECKLIST.md        # 요구사항 체크리스트
│   └── erd.png             # (선택) ERD 이미지
└── README.md               # 개념 정리 + 설계 의도 + 실행 방법
```

### 실행 방법

```bash
cd B6-1
sqlite3 academy.db < sql/01-schema.sql
sqlite3 academy.db < sql/02-seed.sql
sqlite3 academy.db < sql/03-queries.sql > results/03-queries-output.txt
```
