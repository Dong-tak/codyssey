# B6-1 미션 체크리스트

과제 명세의 **4. 기능 요구 사항**과 **7. 제약 사항**을 1:1로 옮긴 표다.
각 항목을 끝낼 때마다 `[ ]` → `[x]` 로 바꾸고, 증거 위치를 적는다.

---

## 1. DB 환경 준비

- [x] 로컬 DB 준비 (**SQLite 3.45.3** — `/opt/anaconda3/bin/sqlite3`)
- [x] SQL 실행 도구 확인 (`sqlite3` CLI)
- [x] `PRAGMA foreign_keys = ON;` 을 모든 스크립트 첫 줄에 넣기
      *(SQLite는 FK가 기본 OFF → 없으면 FK 제약이 동작하지 않음)*
- [x] DB 고유 문법(`AUTOINCREMENT`, `strftime`)에 주석 표기

## 2. 데이터 모델(스키마) 설계

- [x] 테이블 **4개 이상** → `teacher`, `parent`, `student`, `consultation`, `payment` (**5개**)
- [x] 모든 테이블에 PK 존재
- [x] FK **2개 이상**으로 1:N 관계 구성 → **1:N 5개**
  - [x] `student.parent_id` → `parent.id`
  - [x] `student.teacher_id` → `teacher.id`
  - [x] `consultation.student_id` → `student.id`
  - [x] `consultation.teacher_id` → `teacher.id`
  - [x] `payment.student_id` → `student.id`
- [x] 컬럼 타입을 의미에 맞게 선택 (`TEXT` / `INTEGER` / `DATE`)
- [x] 테이블·컬럼 이름이 역할을 드러냄 (`enrolled_at`, `consulted_at`, `pay_month`)

## 3. 제약조건 적용

- [x] `NOT NULL` 1개 이상 → `student.name`, `parent.phone` 등 다수
- [x] `UNIQUE` 1개 이상 → `parent.phone`, `teacher.phone`
- [x] FK가 **실제로 동작** (없는 값 참조가 막히는지 직접 확인)
- [x] `CHECK` (선택) → `student.grade BETWEEN 1 AND 3`
- [x] `DEFAULT` (선택) → `student.status DEFAULT '재원'`

## 4. 샘플 데이터 준비

- [x] `teacher` 10행 이상
- [x] `parent` 10행 이상 (**자녀 2명인 학부모 포함** — 1:N 증명)
- [x] `student` 10행 이상 (휴원/퇴원 각 1명, 담당 미배정 NULL 1명)
- [x] `consultation` 10행 이상 (**상담 0건인 학생을 2명 남길 것** — LEFT JOIN용)
- [x] `payment` 10행 이상 (`paid_at IS NULL` 미납 건 포함)
- [x] FK 연결이 실제 관계를 갖도록 입력
- [x] **입력 순서**: `teacher` → `parent` → `student` → `consultation` → `payment`

## 5. 핵심 SQL 쿼리 15개 이상

| 범주 | 요구 | 계획 | 상태 |
|---|---|---|---|
| 기본 조회 (`WHERE`/`ORDER BY`/`LIMIT`) | 4개 이상 | Q1~Q4 (4개) | [x] |
| 조인 | 4개 이상 | Q5~Q9 (5개) | [x] |
| └ `INNER JOIN` | 2개 이상 | Q5, Q6, Q7 (3개) | [x] |
| └ `LEFT JOIN` | 1개 이상 | Q8, Q9 (2개) | [x] |
| 집계 (`GROUP BY` + 함수 2종 이상) | 3개 이상 | Q10~Q13 (4개) | [x] |
| └ `COUNT` | | Q10, Q11 | [x] |
| └ `SUM` | | Q12 | [x] |
| └ `AVG` | | Q13 | [x] |
| 서브쿼리 | 1개 이상 | Q14 (1개) | [x] |
| `UPDATE` / `DELETE` | 2개 이상 | Q15, Q16 (2개) | [x] |
| `CREATE INDEX` + 이유 1줄 | 1개 이상 | Q17, Q18 (2개) | [x] |
| **합계** | **15개 이상** | **18개** | [x] |

## 6. 결과 확인 자료

- [x] 쿼리마다 실행 결과 확보
- [x] 쿼리마다 **"무엇을 확인하는 쿼리인지" 한 줄 설명** 주석
- [x] 결과를 텍스트 파일 또는 스크린샷으로 `results/` 에 저장

## 7. 제출물 구성

- [x] 스키마 생성 SQL 1개 — `sql/01-schema.sql`
- [x] 샘플 데이터 INSERT SQL 1개 — `sql/02-seed.sql`
- [x] 쿼리 15개 SQL 1개 — `sql/03-queries.sql`
- [x] 실행 결과 폴더 1개 — `results/`
- [x] (추가) 실습 증거 로그 8개 — `logs/`
- [x] (추가) 작업 로그 — `docs/WORKLOG.md`
- [x] (선택) ERD 이미지 1개 — `docs/erd.png` (dbdiagram.io 로 생성)

---

## 보너스 과제

- [x] **B1.** 같은 요구를 `JOIN` / 서브쿼리 두 방식으로 풀고 차이 비교
      (`NOT IN` + NULL 함정 기록)
- [x] **B2.** 정합성 일부러 깨뜨리기 — FK / UNIQUE / NOT NULL 에러 4종 재현 후
      에러 메시지와 해결 방법 기록
- [x] **B3.** 미니 리포트 — 핵심 지표 3개
  - [x] 선생님별 담당 학생 수
  - [x] 월별 상담 건수 추이
  - [x] 미납 학생 목록 + 미납 총액

---

## 제약 사항 준수 확인

- [x] 백엔드 프레임워크 미사용 (Spring / Django / Express 없음)
- [x] 로컬 실행 가능한 DB만 사용 (SQLite)
- [x] **뷰(View) / 프로시저 / 트리거 사용하지 않음**
- [x] 정규화 이론을 과도하게 파지 않음 — "관계가 자연스럽고 쿼리가 잘 나오는 구조"에 집중
- [x] 가급적 표준 SQL 범위, DB 고유 문법은 주석 표기

---

## 과제 목표 자가 점검 (말로 설명할 수 있는가)

- [ ] DB가 엑셀과 뭐가 다른지, 왜 테이블로 나눠 저장하는지
- [ ] PK/FK가 무엇이고 1:N이 데이터를 어떻게 연결하는지
- [ ] `SELECT` / `INSERT` / `UPDATE` / `DELETE`를 언제 쓰는지
- [ ] `JOIN`과 `GROUP BY`로 연결된 데이터를 한 번에 뽑는 방법
- [ ] 검색 / 정렬 / 집계 / 랭킹 요구를 SQL로 푸는 방법
- [ ] 인덱스가 왜 필요하고 어떤 컬럼에 적용하면 좋은지

---

## 작업 순서

1. [ ] `sql/01-schema.sql` 작성 → 실행해서 테이블 5개 생성 확인
2. [ ] FK 동작 확인 (없는 값 참조가 막히는지)
3. [ ] `sql/02-seed.sql` 작성 → 테이블당 10행 이상 확인
4. [ ] `sql/03-queries.sql` 작성 (18개, 각 쿼리에 설명 주석)
5. [ ] 실행 결과를 `results/` 에 저장
6. [ ] `sql/04-bonus.sql` 작성 + 결과 저장
7. [ ] (선택) dbdiagram.io 로 ERD 이미지 생성
8. [ ] `README.md` 작성 (설계 의도 · 개념 정리 · 실행 방법)
