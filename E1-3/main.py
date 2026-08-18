"""Mini NPU Simulator

MAC(Multiply-Accumulate) 연산으로 패턴이 Cross인지 X인지 판별하고,
크기별 연산 시간을 측정해 O(N^2) 를 실측으로 확인하는 콘솔 프로그램.

[구조]
  이 파일 하나로 전체 프로그램을 구현한다. (design.md D1 결정)
  섹션 순서 = 구현 순서(design.md 7장) 와 동일하다.

[실행]
  python3 main.py

[직접 구현할 것]  아래 TODO 12개 (design.md 3장 컴포넌트 설계 기준)
  mac, decide, normalize_label, make_pattern(보너스C2),
  read_matrix, parse_row,
  load_data, extract_size, check_size,
  measure, make_pattern_1d/mac_1d(보너스C1),
  print_case_result, print_perf_table, print_summary,
  run_mode1, run_mode2

[사전 확인된 사실 — docs/requirements-checklist.md G절 참고]
  - data.json 의 모든 값은 float
  - expected 는 '+'/'x', filter 키는 'cross'/'x' (서로 다른 표기)
  - 6개 패턴 중 3개가 epsilon 없이는 UNDECIDED (버그 아님, 의도된 결과)
"""

import json
import time


EPSILON = 1e-9
DATA_FILE = "data.json"


# ============================================================
# 1부. MAC 연산 (요구사항 B5)
# ============================================================

def mac(pattern, filter_grid):
    """TODO 1 — 위치별 곱셈 후 전체 합산을 반환한다.

    [입력] pattern, filter_grid : 같은 크기의 2차원 리스트
    [출력] float 총합

    [검증 — 명세 3x3 예시]
        cross = [[0,1,0],[1,1,1],[0,1,0]]
        xf    = [[1,0,1],[0,1,0],[1,0,1]]
        mac(cross, cross) == 5
        mac(cross, xf)    == 1

    [주의] NumPy 등 외부 라이브러리 금지. 이중 for문으로 직접 구현.
    [참고] study-notes.md 필수 1 (2차원 리스트 인덱싱)
    """
    total = 0.0
    for i in range(len(pattern)):
        for j in range(len(pattern[i])):
            total += pattern[i][j] * filter_grid[i][j]
    return total


def decide(score_cross, score_x, epsilon=EPSILON):
    """TODO 2 — 두 점수를 비교해 "Cross" / "X" / "UNDECIDED" 를 반환한다.

    [규칙 — 명세 6장]
        abs(score_cross - score_x) < epsilon  →  "UNDECIDED"
        score_cross > score_x                 →  "Cross"
        그 외                                  →  "X"

    [참고] study-notes.md 필수 2 (부동소수점, epsilon)
    """
    if abs(score_cross - score_x) < epsilon:
        return "UNDECIDED"
    if score_cross > score_x:
        return "Cross"
    return "X"


def normalize_label(raw_label):
    """TODO 3 — 원본 라벨을 표준 라벨("Cross"/"X")로 변환한다.

    [매핑 — design.md D2, 명세 4장]
        '+'     → 'Cross'   (patterns[].expected 에서 나옴)
        'x'     → 'X'       (patterns[].expected 에서 나옴)
        'cross' → 'Cross'   (filters 의 키에서 나옴)
        'x'     → 'X'       (filters 의 키에서 나옴, 위와 같은 매핑)

    [주의] 대소문자가 다를 수 있으니 raw_label.lower() 로 먼저 통일하는 것을 권장.
    [알 수 없는 값이 들어오면] 예외를 일으켜서 호출한 쪽(run_mode2)이
    그 케이스를 FAIL 처리하도록 한다. (design.md D5 예외 처리 배치)

    [권장 구현 방식] if/elif 사슬보다 딕셔너리 매핑을 권장한다.
        LABEL_MAP = {"+": "Cross", "x": "X", "cross": "Cross"}
        return LABEL_MAP[raw_label.lower()]
    왜: 평가 항목4에 "새 라벨(예: 'o')이 추가되면 어떻게 확장하나?"를 묻는다.
    딕셔너리 방식이면 "LABEL_MAP에 한 줄 추가"로 답이 끝나지만,
    if/elif 방식이면 "조건문을 하나 더 추가"라고 답해야 해서 덜 깔끔하다.
    (docs/evaluation-criteria.md 발견사항 2 참고)
    """
    label_map = {"+": "Cross", "x": "X", "cross": "Cross"}
    key = raw_label.lower()
    if key not in label_map:
        raise ValueError(f"알 수 없는 라벨입니다: {raw_label!r}")
    return label_map[key]


def make_pattern(n, kind):
    """TODO 4 (보너스 C2) — N*N 크기의 Cross 또는 X 패턴을 생성한다.

    [입력] n: 크기, kind: "cross" 또는 "x"
    [출력] n*n 크기의 2차원 리스트 (값은 0 또는 1)

    [Cross 규칙] 가운데 행 전체 = 1, 가운데 열 전체 = 1, 나머지 = 0
    [X 규칙]     두 대각선 = 1, 나머지 = 0
        - 왼쪽위→오른쪽아래 대각선: i번째 행의 i번째 열
        - 오른쪽위→왼쪽아래 대각선: i번째 행의 (n-1-i)번째 열

    [검증] make_pattern(3, "cross") == [[0,1,0],[1,1,1],[0,1,0]]
          make_pattern(3, "x")     == [[1,0,1],[0,1,0],[1,0,1]]

    [쓰이는 곳] 성능 분석의 3x3 데이터, run_mode1 의 예시 확인용
    [참고] study-notes.md 필수 1 (2차원 리스트 "매번 새로 만들기")
    """
    grid = [[0] * n for _ in range(n)]
    mid = n // 2

    if kind == "cross":
        for i in range(n):
            grid[i][mid] = 1
            grid[mid][i] = 1
    elif kind == "x":
        for i in range(n):
            grid[i][i] = 1
            grid[i][n - 1 - i] = 1
    else:
        raise ValueError(f"알 수 없는 패턴 종류입니다: {kind!r}")

    return grid


# ============================================================
# 2부. 모드 1 — 사용자 입력 (요구사항 B2)
# ============================================================

def parse_row(line, n):
    """TODO 5 — 한 줄의 문자열을 길이 n인 float 리스트로 변환한다.

    [입력] line: "0 1 0" 같은 공백구분 문자열, n: 기대하는 개수
    [출력] [0.0, 1.0, 0.0]

    [검증할 것 — 순서대로]
        1) line.split() 의 길이가 n과 다르면 ValueError 발생
        2) 각 조각을 float() 변환. 실패하면 ValueError 발생
           (float() 실패는 자동으로 ValueError 이므로 그대로 두거나 잡아서 다시 던지면 됨)

    [참고] study-notes.md 보조 5 (split, "리스트를 반환한다")
    """
    parts = line.split()
    if len(parts) != n:
        raise ValueError(f"{n}개의 숫자가 필요합니다 (입력: {len(parts)}개)")
    return [float(p) for p in parts]


def read_matrix(label, n):
    """TODO 6 — n줄을 입력받아 n*n 2차원 리스트로 만든다. 검증 실패 시 재입력.

    [흐름]
        1) f"{label} ({n}줄 입력, 공백 구분)" 안내 출력
        2) n번 반복하며 input() 으로 한 줄씩 받고 parse_row() 로 변환
        3) parse_row() 가 ValueError 를 내면:
           "입력 형식 오류: 각 줄에 {n}개의 숫자를 공백으로 구분해 입력하세요."
           출력 후 그 줄부터 다시 입력받는다 (전체를 처음부터 다시 X)

    [요구사항] 행 수/열 수 불일치, 숫자 파싱 실패 모두 이 함수 안에서 처리.
    [참고] utils 스타일의 입력 검증 반복 패턴 — 과제 2의 input_int 와 동일한 구조.
    """
    print(f"{label} ({n}줄 입력, 공백 구분)")
    rows = []
    while len(rows) < n:
        line = input()
        try:
            row = parse_row(line, n)
        except ValueError:
            print(f"입력 형식 오류: 각 줄에 {n}개의 숫자를 공백으로 구분해 입력하세요.")
            continue
        rows.append(row)
    return rows


def run_mode1():
    """TODO 7 — 사용자 입력(3x3) 모드 전체 흐름.

    [흐름 — 명세 8장 예시 참고]
        1) read_matrix("필터 A", 3)
        2) read_matrix("필터 B", 3)
        3) 저장 확인 메시지 출력
        4) read_matrix("패턴", 3)
        5) mac(패턴, A), mac(패턴, B) 계산
        6) decide() 로 판정 → 화면 표시는 "A" / "B" / "판정 불가"
           (주의: 여기선 Cross/X 가 아니라 A/B 로 표시 — 평가문항 항목1 명시사항)
        7) 점수, 판정 출력
        8) measure() 로 3x3 성능 측정 후 출력 (5부에서 구현)

    [mode1 vs mode2 동점 처리가 다른 이유 — 평가문항 항목3 대비]
    mode1 은 사용자가 그 자리에서 필터 A/B 를 직접 입력하므로 "정답(expected)"
    자체가 없다. 그래서 동점이면 그냥 "판정 불가"라고 보여주고 끝난다 — PASS/FAIL
    개념이 없는 단순 결과 표시다. 반면 mode2 는 data.json 의 expected 와 비교해
    검증하는 것이 목적이므로, 동점(UNDECIDED)은 어떤 expected 와도 일치할 수
    없어 항상 FAIL 로 집계되어야 한다. 두 모드는 "목적"이 다르므로(즉석 계산 vs
    정답 대조 검증) 동점을 다루는 의미도 다르다.
    """
    filter_a = read_matrix("필터 A", 3)
    filter_b = read_matrix("필터 B", 3)
    print("필터 A, B 저장 완료")

    pattern = read_matrix("패턴", 3)

    score_a = mac(pattern, filter_a)
    score_b = mac(pattern, filter_b)

    verdict = decide(score_a, score_b)
    display_map = {"Cross": "A", "X": "B", "UNDECIDED": "판정 불가"}
    display_verdict = display_map[verdict]

    print(f"A 점수: {score_a}")
    print(f"B 점수: {score_b}")
    print(f"판정: {display_verdict}")

    avg_ms = measure(pattern, filter_a)
    print(f"연산 시간(평균/10회): {avg_ms:.3f} ms")


# ============================================================
# 3부. 모드 2 — data.json 분석 (요구사항 B3, B4)
# ============================================================

def load_data(path):
    """TODO 8 — JSON 파일을 읽어 딕셔너리로 반환한다.

    [처리할 예외]
        FileNotFoundError → 안내 메시지 출력 후 None 반환
        json.JSONDecodeError → 안내 메시지 출력 후 None 반환

    [호출하는 쪽] run_mode2 에서 None이 반환되면 모드 선택으로 복귀해야 함.
    """
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"오류: {path} 파일을 찾을 수 없습니다.")
        return None
    except json.JSONDecodeError as e:
        print(f"오류: {path} 파일이 올바른 JSON 형식이 아닙니다. ({e})")
        return None


def extract_size(pattern_key):
    """TODO 9 — "size_13_2" 형태의 키에서 크기 13을 정수로 추출한다.

    [힌트] pattern_key.split("_") 을 하면 몇 번째가 크기인지 확인해볼 것.
    [검증] extract_size("size_13_2") == 13
          extract_size("size_5_1")  == 5

    [참고] study-notes.md 보조 5 (split, "리스트를 반환한다")
    """
    parts = pattern_key.split("_")
    return int(parts[1])


def check_size(pattern_grid, filter_grid):
    """TODO 10 — 패턴과 필터의 크기(행 수, 각 행의 열 수)가 일치하는지 확인한다.

    [출력] True / False

    [쓰이는 곳] run_mode2 에서 False 이면 그 케이스만 FAIL 처리하고
    (raise 하지 않고) 다음 케이스로 넘어가야 한다 — 프로그램이 죽으면 안 됨.
    """
    if len(pattern_grid) != len(filter_grid):
        return False
    for pattern_row, filter_row in zip(pattern_grid, filter_grid):
        if len(pattern_row) != len(filter_row):
            return False
    return True


def run_mode2():
    """TODO 11 — data.json 분석 모드 전체 흐름.

    [흐름 — 명세 8장 예시, design.md 4장 참고]
        1) load_data(DATA_FILE) — 실패하면 안내 후 return
        2) filters 의 각 키(cross/x)를 normalize_label 로 정규화해 딕셔너리로 정리
           예: {"Cross": [[...]], "X": [[...]]}  (size_5, size_13, size_25 각각)
           "size_5  필터 로드 완료 (Cross, X)" 같은 메시지 출력
        3) results = []  ← 케이스별 결과를 담을 리스트 (총/통과/실패 집계용)
        4) patterns 의 각 (키, 값) 에 대해 반복:
             a) try 블록으로 감싸기 (한 케이스 실패가 전체를 멈추면 안 됨 — B3 요구사항)
             b) extract_size(키) 로 N 추출
             c) 해당 size_N 필터(Cross, X) 선택
             d) check_size() 로 크기 확인 → 불일치면 결과를 FAIL 로 기록, continue
             e) mac(입력, Cross필터), mac(입력, X필터) 계산
             f) decide() 로 판정
             g) normalize_label(값["expected"]) 로 정답 정규화
             h) 판정 == 정답 이면 PASS, 아니면 FAIL → results 에 기록
             i) print_case_result() 로 케이스별 출력 (6부에서 구현)
             j) except 블록: 예외가 나면 그 케이스를 FAIL 로 기록하고 원인 메시지 출력
        5) 성능 분석: 3, 5, 13, 25 크기에 대해 measure() 호출 후 print_perf_table()
        6) print_summary(results) 로 총/통과/실패 요약 출력

    [핵심] 4번 루프 안의 각 케이스는 독립적으로 실패할 수 있어야 한다.
    """
    data = load_data(DATA_FILE)
    if data is None:
        return

    # filters 정규화: {"size_5": {"Cross": [[...]], "X": [[...]]}, ...}
    filters_by_size = {}
    for size_key, raw_filters in data["filters"].items():
        normalized = {}
        for raw_label, grid in raw_filters.items():
            normalized[normalize_label(raw_label)] = grid
        filters_by_size[size_key] = normalized
        labels = ", ".join(normalized.keys())
        print(f"✓ {size_key} 필터 로드 완료 ({labels})")

    results = []

    for case_id, case in data["patterns"].items():
        try:
            n = extract_size(case_id)
            size_key = f"size_{n}"
            filters = filters_by_size[size_key]
            cross_filter = filters["Cross"]
            x_filter = filters["X"]

            pattern = case["input"]

            if not check_size(pattern, cross_filter):
                results.append({
                    "case_id": case_id,
                    "status": "FAIL",
                    "reason": f"필터({size_key})와 패턴의 크기가 일치하지 않습니다.",
                })
                print(f"--- {case_id} ---")
                print(f"FAIL: 필터({size_key})와 패턴 크기 불일치")
                continue

            score_cross = mac(pattern, cross_filter)
            score_x = mac(pattern, x_filter)
            verdict = decide(score_cross, score_x)
            expected = normalize_label(case["expected"])

            status = "PASS" if verdict == expected else "FAIL"
            print_case_result(case_id, score_cross, score_x, verdict, expected, status)

            reason = "" if status == "PASS" else "동점(UNDECIDED) 처리 규칙에 따라 FAIL" if verdict == "UNDECIDED" else f"판정({verdict})이 expected({expected})와 다름"
            results.append({"case_id": case_id, "status": status, "reason": reason})

        except Exception as e:
            results.append({
                "case_id": case_id,
                "status": "FAIL",
                "reason": f"처리 중 오류 발생: {e}",
            })
            print(f"--- {case_id} ---")
            print(f"FAIL: 처리 중 오류 발생 ({e})")

    print()
    print("=" * 40)
    print("성능 분석 (평균/10회)")
    print("=" * 40)
    perf_rows = []
    for n in [3, 5, 13, 25]:
        p = make_pattern(n, "cross")
        f = make_pattern(n, "x")
        avg_ms = measure(p, f)
        perf_rows.append((n, avg_ms, n * n))
    print_perf_table(perf_rows)

    print()
    print("=" * 40)
    print("결과 요약")
    print("=" * 40)
    print_summary(results)


# ============================================================
# 4부. 성능 분석 (요구사항 B1, B8)
# ============================================================

def measure(pattern, filter_grid, repeat=10):
    """TODO 12 — MAC 연산을 repeat번 반복 측정해 평균 시간(ms)을 반환한다.

    [규칙]
        - time.perf_counter() 사용
        - 측정 구간은 mac() 호출 단 한 줄만 (print, 파일 I/O 제외)
        - repeat번 재서 평균을 ms 단위로 반환

    [검증 방법] 크기를 3→25로 늘려가며 호출해보고, 값이 대체로 커지는지 확인.
                (작은 크기에서는 오버헤드 때문에 이론(N²)과 정확히 비례하지 않을 수 있음
                 — study-notes.md 필수 4 참고. 정상이다.)

    [참고] study-notes.md 필수 3 (perf_counter, 10회 평균, I/O 제외)
    """
    times = []
    for _ in range(repeat):
        start = time.perf_counter()
        mac(pattern, filter_grid)
        times.append(time.perf_counter() - start)
    return (sum(times) / len(times)) * 1000


# --- 보너스 C1: 1차원 배열 최적화 (선택 구현) -------------------

def to_1d(grid):
    """TODO 13 (보너스 C1) — 2차원 리스트를 길이 N*N인 1차원 리스트로 변환한다.

    [입력] [[1,2],[3,4]]
    [출력] [1,2,3,4]  (행을 순서대로 이어붙임)

    [힌트] 이중 for문으로 하나씩 append 하거나, 리스트 컴프리헨션으로 한 줄에.
    """
    pass


def mac_1d(pattern_1d, filter_1d):
    """TODO 14 (보너스 C1) — 1차원 배열 버전의 MAC 연산.

    [입력] to_1d() 로 변환된 두 1차원 리스트 (길이가 같음)
    [출력] float 총합

    [비교 목적] mac() 과 결과가 같아야 하며(같은 값 검증), 실행 시간만 비교한다.
    [최적화 전/후 비교 방법] measure() 를 mac 버전과 mac_1d 버전 각각에 대해
    실행해 같은 크기·같은 반복 횟수로 성능 표를 두 개 만들어 비교한다.
    """
    pass


# ============================================================
# 5부. 출력 함수
# ============================================================

def print_case_result(case_id, score_cross, score_x, verdict, expected, result):
    """TODO 15 — 케이스 하나의 결과를 명세 8장 형식으로 출력한다.

    [형식 예시]
        --- size_5_1 ---
        Cross 점수: 1.0
        X 점수: 5.0
        판정: X | expected: X | PASS
    """
    print(f"--- {case_id} ---")
    print(f"Cross 점수: {score_cross}")
    print(f"X 점수: {score_x}")
    print(f"판정: {verdict} | expected: {expected} | {result}")


def print_perf_table(rows):
    """TODO 16 — 크기/평균시간/연산횟수 표를 출력한다.

    [입력] rows: [(3, 0.010, 9), (5, 0.031, 25), (13, 0.187, 169), (25, 0.682, 625)] 형태
    [형식 예시 — 명세 8장]
        크기       평균 시간(ms)    연산 횟수
        -------------------------------------
        3×3            0.010           9
        5×5            0.031           25
    """
    print(f"{'크기':<10}{'평균 시간(ms)':<18}{'연산 횟수'}")
    print("-" * 40)
    for n, avg_ms, op_count in rows:
        print(f"{n}×{n:<8}{avg_ms:<18.3f}{op_count}")


def print_summary(results):
    """TODO 17 — 전체 테스트 수/통과 수/실패 수와 실패 목록을 출력한다.

    [입력] results: [{"case_id": "size_5_1", "status": "PASS"/"FAIL", "reason": "..."}, ...]
    [형식 예시 — 명세 8장]
        총 테스트: 8개
        통과: 7개
        실패: 1개

        실패 케이스:
        - size_13_1: 동점(UNDECIDED) 처리 규칙에 따라 FAIL
    """
    total = len(results)
    passed = [r for r in results if r["status"] == "PASS"]
    failed = [r for r in results if r["status"] == "FAIL"]

    print(f"총 테스트: {total}개")
    print(f"통과: {len(passed)}개")
    print(f"실패: {len(failed)}개")

    if failed:
        print()
        print("실패 케이스:")
        for r in failed:
            print(f"- {r['case_id']}: {r['reason']}")


# ============================================================
# 6부. 실행 흐름 (요구사항 B10)
# ============================================================

def main():
    """TODO 18 — 모드를 선택받아 run_mode1 또는 run_mode2 를 호출한다.

    [흐름]
        1) 제목 출력: "=== Mini NPU Simulator ==="
        2) 모드 선택 메뉴 출력 (1: 사용자 입력, 2: data.json 분석)
        3) 입력값에 따라 run_mode1() 또는 run_mode2() 호출
        4) 잘못된 입력이면 안내 후 재입력 (과제 2 의 input_int 패턴 재사용 가능)
    """
    print("=== Mini NPU Simulator ===")
    print()
    print("[모드 선택]")
    print("1. 사용자 입력 (3x3)")
    print("2. data.json 분석")

    while True:
        choice = input("선택: ").strip()
        if choice == "1":
            run_mode1()
            break
        elif choice == "2":
            run_mode2()
            break
        else:
            print("잘못된 입력입니다. 1 또는 2를 입력하세요.")


if __name__ == "__main__":
    main()
