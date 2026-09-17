# B6-1 작업 로그

작업일: 2026-09-17 · DB: SQLite · 산출물: SQL 4개 파일 / 쿼리 18개 / 로그 8개

각 단계의 **실제 명령과 출력**은 [`logs/`](../logs) 에 그대로 저장돼 있다.
이 문서는 그 로그를 순서대로 엮고, **막혔던 지점과 어떻게 고쳤는지**를 기록한 것이다.

---

## 작업 순서 한눈에 보기

| 단계 | 한 일 | 증거 로그 |
|---|---|---|
| 1 | 환경 확인 (sqlite3 / DBeaver) | [`01-environment.log`](../logs/01-environment.log) |
| 2 | 주제 선정 · ERD 설계 · 체크리스트 작성 | [`PLAN.md`](PLAN.md) · [`CHECKLIST.md`](CHECKLIST.md) |
| 3 | 스키마 생성 (테이블 5개) | [`02-schema-build.log`](../logs/02-schema-build.log) |
| 4 | 샘플 데이터 입력 (93행) | [`03-seed-load.log`](../logs/03-seed-load.log) |
| 5 | 설계 의도대로 데이터가 들어갔는지 검증 | [`04-data-gaps-verify.log`](../logs/04-data-gaps-verify.log) |
| 6 | 핵심 쿼리 18개 실행 | [`05-queries-run.log`](../logs/05-queries-run.log) |
| 7 | 인덱스가 실제로 쓰이는지 실행계획 확인 | [`06-index-explain.log`](../logs/06-index-explain.log) |
| 8 | 보너스 3종 실행 | [`07-bonus-run.log`](../logs/07-bonus-run.log) |
| 9 | 처음부터 재현되는지 최종 확인 | [`08-reproducibility.log`](../logs/08-reproducibility.log) |

---

## 1. 환경 확인

```
$ which -a sqlite3
/opt/anaconda3/bin/sqlite3
/usr/bin/sqlite3

$ sqlite3 --version
3.45.3 2024-04-15 ...
```

`sqlite3` 가 **두 군데** 있다. anaconda 쪽(3.45.3)과 시스템 쪽(3.51.0)이고,
어느 셸에서 실행하느냐에 따라 PATH 우선순위가 달라 버전이 다르게 잡힌다.
이 과제에서 쓰는 문법은 두 버전 모두 지원하므로 그대로 진행했다.

DB 선택은 **SQLite**. 파일 1개가 곧 DB라서 서버를 띄울 필요가 없고,
제출할 때 `.db` 파일을 그대로 넘길 수 있다.

### 여기서 처음 안 것

```
$ sqlite3 academy.db "PRAGMA foreign_keys;"
0
```

**SQLite는 외래키 제약이 기본으로 꺼져 있다.**
이걸 모르고 넘어갔으면 "FK가 실제로 동작해야 한다"는 요구사항을 못 지킬 뻔했다.
없는 `parent_id` 로 학생을 등록해도 그냥 통과해 버리기 때문이다.
그래서 **모든 스크립트 첫 줄**에 넣었다.

```sql
PRAGMA foreign_keys = ON;
```

---

## 2. 설계 — FK를 어디에 둘지

주제는 **입시 학원 고객관리**. 학생·학부모·선생님을 각각 다른 테이블로 나눴다.

가장 오래 고민한 건 **FK의 위치**였다. 결론은 규칙 하나로 정리된다.

> **FK는 항상 N쪽(많은 쪽)에 둔다.**

학부모 1명이 자녀를 여러 명 보낼 수 있으므로 **1(parent) : N(student)** 이고,
FK는 `student.parent_id` 가 된다. 반대로 `parent` 에 `student_id` 를 두면
**자녀가 2명인 학부모를 표현할 수 없다.** 실제로 이 DB에는 자녀 2명인 학부모가 3명 있다.

### NULL 허용 여부를 나눈 기준

| 컬럼 | NULL | 이유 |
|---|---|---|
| `student.parent_id` | ❌ | 보호자는 결제 주체라 없으면 청구가 불가능 |
| `student.teacher_id` | ✅ | 등록 직후에는 담당이 아직 안 정해질 수 있음 |
| `consultation.next_action` | ✅ | NULL 자체가 "후속 조치 미정" 이라는 의미 |
| `payment.paid_at` | ✅ | NULL 자체가 "미납" 이라는 의미 |

`is_paid` 같은 별도 플래그를 두지 않은 이유는 **두 값이 어긋날 수 있어서**다.
(납부일은 들어갔는데 플래그는 `false` 로 남는 경우) 컬럼 하나로 통일했다.

---

## 3. 샘플 데이터에 일부러 "구멍"을 남긴 이유

처음엔 데이터를 깔끔하게 채우려 했는데, 그러면 문제가 생긴다.

**모든 학생에게 담당 선생님과 상담 기록이 다 있으면
`LEFT JOIN` 을 써도 `INNER JOIN` 과 결과가 똑같다.**
그러면 왜 LEFT를 썼는지 증명할 방법이 없다.

그래서 의도적으로 빈자리를 남겼고, 실제로 차이가 나는지 확인했다.

```
$ INNER JOIN 으로 학생 명단
14
$ LEFT JOIN 으로 학생 명단
15
```

**14 vs 15.** 담당 미배정 학생 1명(배시윤)이 INNER JOIN에서 탈락했다.
이게 LEFT JOIN을 쓴 이유 그 자체다.

심어둔 구멍 전체는 [`04-data-gaps-verify.log`](../logs/04-data-gaps-verify.log) 에 있다.

---

## 4. 막혔던 지점 3가지

실제로 문제가 됐고 고친 것만 적는다.

### 문제 1 — 출력 열 너비를 고정했더니 인덱스명이 잘렸다

`03-queries.sql` 에 `.width 14` 를 넣어 열 너비를 고정했더니 결과가 이렇게 나왔다.

```
인덱스명            대상테이블
--------------  --------------
idx_consultati  consultation
on_student

idx_payment_mo  payment
nth
```

`idx_consultation_student` 가 두 줄로 쪼개졌다. 인덱스를 만들었다는 **증거 자료로
쓸 수 없는 출력**이다.

**원인**: `.width` 로 고정하면 값이 길어도 그 폭에 맞춰 잘린다.
**해결**: `.width` 줄을 제거했다. `.mode column` 만 두면 sqlite3가 내용 길이에 맞춰
자동으로 폭을 잡는다.

```bash
sed -i '' '/^\.width 14/d' sql/03-queries.sql
```

### 문제 2 — `NOT IN` 함정 실증이 재현되지 않았다 ⭐

보너스 B1에서 "`NOT IN` 은 서브쿼리 결과에 NULL이 섞이면 결과가 통째로 빈다" 를
보여주려고 이렇게 썼다.

```sql
-- 결과가 0행이 될 것으로 기대
SELECT t.name FROM teacher t
WHERE t.id NOT IN (SELECT teacher_id FROM student);
```

그런데 **1행이 나왔다.** 주석에는 "0행으로 사라진다" 라고 써 놨는데 실제로는 아니었다.

**원인**: `04-bonus.sql` 은 `03-queries.sql` 다음에 실행된다.
그런데 `03-queries.sql` 의 **Q15(`UPDATE`)가 담당 미배정 학생에게 선생님을 배정**해서,
그 시점엔 `student.teacher_id` 에 **NULL이 하나도 남아 있지 않았다.**
NULL이 없으니 함정도 발동하지 않은 것이다.

설명과 실제 출력이 다른 자료는 증거로서 가치가 없으므로, 실행 순서와 무관하게
재현되도록 **데모 구간에서 NULL을 직접 만들었다가 되돌리는** 방식으로 고쳤다.

```sql
.print '(준비) 함정을 재현하려고 담당 미배정 학생을 한 명 만든다'
UPDATE student SET teacher_id = NULL WHERE name = '배시윤';

-- (A) NOT IN        -> 0행
-- (B) NOT EXISTS    -> 2행 (정상)
-- (C) NOT IN + IS NOT NULL 필터 -> 2행 (정상)

.print '(정리) 담당을 다시 배정해 원래 상태로 되돌린다'
UPDATE student SET teacher_id = (SELECT id FROM teacher WHERE name='임수빈')
WHERE teacher_id IS NULL;
```

수정 후 결과:

```
(A) NOT IN + NULL 이 섞인 목록  -> 결과가 0행으로 사라진다
                                      ← 아무것도 안 나옴
(B) NOT EXISTS 로 같은 질문  -> NULL 과 무관하게 정상 동작
id  담당학생없는선생님
--  ---------
8   임수빈
10  한가람
```

**왜 0행이 되나**: `NOT IN` 은 내부적으로
`(t.id <> v1 AND t.id <> v2 AND ...)` 로 풀린다.
`v` 중 하나가 `NULL` 이면 그 비교는 TRUE도 FALSE도 아닌 **UNKNOWN** 이 되고,
`AND` 로 묶인 전체가 **절대 TRUE가 될 수 없어** 모든 행이 탈락한다.
**에러도 안 나고 결과만 조용히 빈다.** 그래서 가장 찾기 어려운 버그다.

> 배운 것: "없는 것 찾기" 는 `LEFT JOIN + IS NULL` 이나 `NOT EXISTS` 를 쓴다.

### 문제 3 — 로그를 캡처했더니 Q15의 "(변경 전)" 이 비어 있었다

로그 05를 만들려고 `03-queries.sql` 을 다시 돌렸더니 Q15 출력이 이렇게 나왔다.

```
--- Q15. [UPDATE] 담당 미배정 학생에게 담당 선생님 배정 ---
(변경 전)
(변경 후)
id  이름   담당교사
15  배시윤  임수빈
```

`(변경 전)` 이 비었다. 이미 앞선 실행에서 Q15가 배정을 끝낸 DB였기 때문이다.

**원인**: `03-queries.sql` 은 `UPDATE` 와 `DELETE` 를 포함하므로 **멱등하지 않다.**
두 번 돌리면 결과가 달라진다.

**해결**: 로그를 캡처하기 전에 `01-schema.sql` → `02-seed.sql` 로 DB를 초기화했다.
스크립트 헤더와 로그에도 이 사실을 명시했다.

> 배운 것: 데이터를 바꾸는 스크립트는 **"몇 번 돌려도 같은가"** 를 따로 확인해야 한다.
> `01-schema.sql` 은 `DROP TABLE IF EXISTS` 로 시작하므로 몇 번이든 다시 돌릴 수 있다.

---

## 5. 인덱스는 "만들었다" 로 끝내지 않았다

`CREATE INDEX` 를 썼다고 끝이 아니라, 옵티마이저가 **실제로 그 인덱스를 타는지**
`EXPLAIN QUERY PLAN` 으로 확인했다.

```
[인덱스 있음]
`--SEARCH consultation USING INDEX idx_consultation_student (student_id=?)

[인덱스 없음 - DROP 후]
`--SCAN consultation
```

`SEARCH ... USING INDEX` 와 `SCAN` 의 차이가 곧 색인을 타는지 전부 훑는지의 차이다.
집계용 인덱스도 확인했다.

```
`--SCAN payment USING INDEX idx_payment_month
```

이미 정렬된 인덱스를 읽으므로 `GROUP BY` 의 정렬 비용이 없어진다.

전체 비교는 [`06-index-explain.log`](../logs/06-index-explain.log) 에 있다.

> 인덱스는 공짜가 아니다. 읽기는 빨라지지만 `INSERT`/`UPDATE` 마다 색인도 갱신해야 해서
> **쓰기는 느려진다.** 값 종류가 적은 컬럼(`status` 같은)에 걸면 효과가 거의 없고,
> PK/UNIQUE에는 이미 인덱스가 자동 생성된다.

---

## 6. 정합성을 일부러 깨뜨려 봤다

제약조건이 "선언만 돼 있는지" 아니면 "실제로 막는지" 는 다른 문제다. 5가지를 시도했다.

```
FOREIGN KEY constraint failed              ← 없는 학부모(999)로 학생 등록
UNIQUE constraint failed: parent.phone     ← 이미 쓰는 전화번호로 학부모 추가
NOT NULL constraint failed: student.name   ← 이름 없이 학생 등록
FOREIGN KEY constraint failed              ← 자녀가 남은 학부모 삭제
CHECK constraint failed: grade BETWEEN 1 AND 3  ← 학년에 4 입력
```

**5건 전부 막혔고**, 시도 후에도 행 수는 그대로였다 (학생 15 / 학부모 12).

앞의 두 FK 에러는 **`PRAGMA foreign_keys = ON;` 이 있어야만 발생한다.**
이 줄을 빼고 돌리면 유령 학생이 그대로 들어간다.

---

## 7. 최종 재현성 확인

DB 파일을 지우고 처음부터 4개 스크립트를 순서대로 돌렸다.

| 스크립트 | 종료 코드 |
|---|---|
| `01-schema.sql` | 0 |
| `02-seed.sql` | 0 |
| `03-queries.sql` | 0 |
| `04-bonus.sql` | **1** ← B2의 의도적 제약 위반 5건 때문. 정상 |

`results/` 전체에서 `error` 를 검색하면 **5건만** 나오고, 전부 `04-bonus.sql` 의
의도된 위반이다. `03-queries-output.txt` 에는 에러가 **한 건도 없다.**

최종 DB 상태에서 `payment` 가 시드(31행)보다 1행 적은 **30행**인 이유는
Q16 `DELETE` 가 퇴원생의 미납 청구 1건을 지웠기 때문이다. 의도된 동작이다.

---

## 8. 이 과제에서 남는 것

| 처음 생각 | 실제로 배운 것 |
|---|---|
| FK는 아무 데나 걸면 되는 줄 | **FK는 항상 N쪽에.** 1쪽에 걸면 여러 개를 표현 못 한다 |
| 제약조건은 선언하면 동작하는 줄 | SQLite는 **FK가 기본 OFF**. 켜야 동작한다 |
| `NOT IN` 과 `NOT EXISTS` 는 같은 줄 | **NULL 하나로 `NOT IN` 은 조용히 무너진다** |
| 인덱스는 만들면 쓰이는 줄 | `EXPLAIN QUERY PLAN` 으로 **확인해야** 안다 |
| 데이터는 깔끔할수록 좋은 줄 | **빈자리가 있어야 LEFT JOIN 을 증명**할 수 있다 |
| SQL은 적은 순서대로 도는 줄 | `FROM → WHERE → GROUP BY → HAVING → SELECT → ORDER BY` |

가장 크게 남은 건 **문제 2**다.
결과가 나왔다고 맞는 게 아니라, **내가 쓴 설명과 실제 출력이 같은지**를
따로 확인해야 한다는 것. 그때 `NOT IN` 이 1행을 뱉는 걸 그냥 넘겼으면
"NULL이 있으면 0행이 된다" 는 **틀린 설명이 그대로 제출될 뻔했다.**
