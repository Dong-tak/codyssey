"""Mini NPU Simulator

MAC(Multiply-Accumulate) 연산으로 2차원 패턴이 십자가(Cross)인지 X인지 판별함.
크기별 연산 시간을 측정해 O(N^2) 경향을 실측으로 확인함.

실행: python3 main.py
"""

import json
import time


# 두 점수의 차이가 이 값보다 작으면 같은 값으로 간주함
EPSILON = 1e-9

# 필터와 패턴이 들어있는 데이터 파일 이름
DATA_FILE = 'data.json'


# ============================================================
# 0부. 데이터 구조
# ============================================================

def create_grid(n, fill=0.0):
    """모든 칸이 fill 값인 n x n 격자를 만들어 반환함."""
    # 반복문으로 매 행을 새로 만들어야 각 행이 독립된 리스트가 됨.
    # [[fill] * n] * n 으로 만들면 같은 행 하나를 n번 참조하게 되어
    # 한 칸만 바꿔도 모든 행이 함께 바뀜.
    return [[fill] * n for _ in range(n)]


def get_cell(grid, row, col):
    """격자에서 (row, col) 위치의 값을 읽어 반환함.

    값을 읽는 곳은 사실상 mac() 의 이중 루프 안뿐인데, 거기서 이 함수를 쓰면
    칸마다 함수 호출이 두 번씩 늘어 1.7~2.2배 느려짐. 이 과제는 연산 시간
    측정이 목적이라 측정값이 흐려지므로 mac() 안에서는 직접 인덱싱을 씀.
    """
    return grid[row][col]


def set_cell(grid, row, col, value):
    """격자의 (row, col) 위치에 값을 저장함."""
    grid[row][col] = value


def print_section(title):
    """화면을 단계별로 구분하는 헤더를 출력함."""
    print()
    print('#' + '-' * 41)
    print(f'# {title}')
    print('#' + '-' * 41)


# ============================================================
# 1부. MAC 연산과 판정
# ============================================================

def mac(pattern, filter_grid):
    """패턴과 필터를 위치별로 곱해 모두 더한 값을 반환함."""
    # 누적할 그릇을 실수 0으로 준비함
    total = 0.0

    # 바깥 반복문이 행을, 안쪽 반복문이 열을 훑음.
    # 모든 칸을 한 번씩 방문하므로 총 연산 횟수는 N * N 이 됨.
    for i in range(len(pattern)):
        for j in range(len(pattern[i])):
            # 같은 위치의 두 값을 곱해서 누적함.
            # 겹치는 자리가 많을수록 총합이 커지므로 이 값이 곧 유사도가 됨.
            total += pattern[i][j] * filter_grid[i][j]

    return total


def decide(score_cross, score_x, epsilon=EPSILON):
    """두 점수를 비교해 'Cross', 'X', 'UNDECIDED' 중 하나를 반환함."""
    # 차이가 허용오차보다 작으면 우열을 가릴 수 없다고 판단함.
    # 모든 값이 실수라 계산 순서만 달라도 1e-16 수준의 오차가 생기는데,
    # 이 검사가 없으면 그 오차의 부호가 판정을 좌우하게 됨.
    if abs(score_cross - score_x) < epsilon:
        return 'UNDECIDED'

    # 오차 범위를 벗어난 진짜 차이가 있을 때만 높은 쪽으로 판정함
    if score_cross > score_x:
        return 'Cross'

    return 'X'


def normalize_label(raw_label):
    """서로 다른 표기의 라벨을 표준 라벨('Cross' 또는 'X')로 바꿔 반환함."""
    # 같은 개념을 데이터마다 다르게 부름.
    # expected 는 '+' 와 'x' 를 쓰고, filters 의 키는 'cross' 와 'x' 를 씀.
    # 딕셔너리로 둔 이유는 새 라벨이 생겨도 여기 한 줄만 추가하면 되기 때문임.
    label_map = {'+': 'Cross', 'x': 'X', 'cross': 'Cross'}

    # 대소문자 차이를 없애고 매핑을 찾음
    key = raw_label.lower()

    # 등록되지 않은 라벨이면 예외를 던져서 부른 쪽이 그 케이스만
    # 실패 처리하도록 넘김. 여기서 임의로 결정하지 않음.
    if key not in label_map:
        raise ValueError(f'알 수 없는 라벨입니다: {raw_label!r}')

    return label_map[key]


def make_pattern(n, kind):
    """n x n 크기의 십자가 또는 X 패턴을 만들어 반환함."""
    # 0으로 채운 빈 격자에서 시작해 필요한 칸만 1로 바꿈
    grid = create_grid(n, 0.0)

    # 가운데 줄의 위치를 구함
    mid = n // 2

    if kind == 'cross':
        for i in range(n):
            # 가운데 열을 세로로 채움
            set_cell(grid, i, mid, 1.0)
            # 가운데 행을 가로로 채움
            set_cell(grid, mid, i, 1.0)

    elif kind == 'x':
        for i in range(n):
            # 왼쪽 위에서 오른쪽 아래로 내려가는 대각선
            set_cell(grid, i, i, 1.0)
            # 오른쪽 위에서 왼쪽 아래로 내려가는 대각선
            set_cell(grid, i, n - 1 - i, 1.0)

    else:
        raise ValueError(f'알 수 없는 패턴 종류입니다: {kind!r}')

    return grid


# ============================================================
# 2부. 모드 1 (사용자 입력)
# ============================================================

def parse_row(line, n):
    """한 줄의 문자열을 숫자 n개짜리 리스트로 바꿔 반환함."""
    # split() 은 공백을 기준으로 쪼갠 '리스트'를 돌려줌.
    # 인자 없이 쓰면 앞뒤 공백 제거와 연속 공백 처리가 함께 됨.
    parts = line.split()

    # 숫자 개수가 맞지 않으면 열 개수 불일치이므로 예외를 던짐
    if len(parts) != n:
        raise ValueError(f'{n}개의 숫자가 필요합니다 (입력: {len(parts)}개)')

    # 조각이 숫자가 아니면 float() 이 스스로 ValueError 를 냄
    return [float(p) for p in parts]


def read_matrix(label, n):
    """n줄을 입력받아 n x n 격자로 만들어 반환함. 잘못된 줄은 다시 받음."""
    print(f'{label} ({n}줄 입력, 공백 구분)')

    # 완성된 행만 담으므로, 실패한 줄은 개수에 포함되지 않음
    rows = []

    # 필요한 행 수를 채울 때까지 계속 받음
    while len(rows) < n:
        line = input()

        try:
            row = parse_row(line, n)
        except ValueError:
            # 안내만 하고 다음 반복으로 넘어감.
            # 전체를 처음부터 다시 받지 않고 실패한 그 줄만 다시 받게 됨.
            print(f'입력 형식 오류: 각 줄에 {n}개의 숫자를 공백으로 구분해 입력하세요.')
            continue

        rows.append(row)

    return rows


def run_mode1():
    """필터 두 개와 패턴을 직접 입력받아 어느 쪽에 가까운지 판정함."""
    # 1단계: 비교 기준이 될 필터 두 개를 받음
    print_section('[1] 필터 입력')
    filter_a = read_matrix('필터 A', 3)
    print()
    filter_b = read_matrix('필터 B', 3)
    print()
    print('필터 A, B 저장 완료')

    # 2단계: 판별 대상이 될 패턴을 받음
    print_section('[2] 패턴 입력')
    pattern = read_matrix('패턴', 3)

    # 3단계: 같은 패턴을 두 필터에 각각 통과시켜 점수를 냄
    score_a = mac(pattern, filter_a)
    score_b = mac(pattern, filter_b)

    # 두 점수를 견줘 판정을 냄
    verdict = decide(score_a, score_b)

    print_section('[3] MAC 결과')
    print(f'A 점수: {score_a}')
    print(f'B 점수: {score_b}')

    # 연산 시간은 화면 출력과 섞이지 않게 따로 측정함
    avg_ms = measure(pattern, filter_a)
    print(f'연산 시간(평균/10회): {avg_ms:.3f} ms')

    if verdict == 'UNDECIDED':
        # 이 모드는 사용자가 즉석에서 필터를 넣는 것이라 정답이 없음.
        # 그래서 동점은 실패가 아니라 '가릴 수 없음'이라는 결과로만 알림.
        print(f'판정: 판정 불가 (|A-B| < {EPSILON})')
    else:
        # 내부 표준 라벨을 이 모드의 표시 이름으로 바꿔서 보여줌
        display_map = {'Cross': 'A', 'X': 'B'}
        print(f'판정: {display_map[verdict]}')

    # 4단계: 방금 사용한 3x3 크기의 연산 성능을 표로 정리함
    print_section('[4] 성능 분석 (3x3, 평균/10회)')
    print_perf_table([(3, avg_ms, 3 * 3)])


# ============================================================
# 3부. 모드 2 (data.json 분석)
# ============================================================

def load_data(path):
    """JSON 파일을 읽어 딕셔너리로 반환함. 실패하면 None 을 반환함."""
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)

    except FileNotFoundError:
        # 파일이 없어도 프로그램을 끝내지 않고 부른 쪽에 상황만 알림
        print(f'오류: {path} 파일을 찾을 수 없습니다.')
        return None

    except json.JSONDecodeError as e:
        # 파일은 있지만 내용이 깨진 경우도 같은 방식으로 처리함
        print(f'오류: {path} 파일이 올바른 JSON 형식이 아닙니다. ({e})')
        return None


def extract_size(pattern_key):
    """'size_13_2' 같은 키에서 크기 숫자만 뽑아 정수로 반환함."""
    # 밑줄로 쪼개면 ['size', '13', '2'] 가 되므로 가운데가 크기임
    parts = pattern_key.split('_')

    # 쪼갠 결과는 문자열이라 정수로 바꿔야 필터 키를 만들 때 쓸 수 있음
    return int(parts[1])


def check_size(pattern_grid, filter_grid):
    """패턴과 필터의 크기가 같은지 검사해 True 또는 False 를 반환함."""
    # 먼저 행 수가 같은지 봄
    if len(pattern_grid) != len(filter_grid):
        return False

    # 행 수가 같아도 각 행의 길이가 다를 수 있어 열 수까지 확인함
    for pattern_row, filter_row in zip(pattern_grid, filter_grid):
        if len(pattern_row) != len(filter_row):
            return False

    return True


def run_mode2():
    """data.json 의 모든 케이스를 판정하고 정답과 대조해 집계함."""
    # 파일을 못 읽으면 더 진행할 수 없으므로 여기서 끝냄
    data = load_data(DATA_FILE)
    if data is None:
        return

    # 1단계: 필터의 원본 키를 표준 라벨로 바꿔 크기별로 정리함.
    # 이후 로직은 'cross' 나 '+' 같은 원본 표기를 몰라도 됨.
    print_section('[1] 필터 로드')
    filters_by_size = {}

    for size_key, raw_filters in data['filters'].items():
        normalized = {}

        for raw_label, grid in raw_filters.items():
            normalized[normalize_label(raw_label)] = grid

        filters_by_size[size_key] = normalized
        labels = ', '.join(normalized.keys())
        print(f'✓ {size_key} 필터 로드 완료 ({labels})')

    # 2단계: 패턴을 하나씩 판정함
    print_section('[2] 패턴 분석 (라벨 정규화 적용)')

    # 케이스별 결과를 모아 마지막에 총계를 냄
    results = []

    for case_id, case in data['patterns'].items():
        # 한 케이스가 실패해도 나머지 검증이 멈추면 안 되므로
        # 케이스 단위로 예외를 감쌈
        try:
            # 키에서 크기를 뽑아 같은 크기의 필터를 찾음
            n = extract_size(case_id)
            size_key = f'size_{n}'
            filters = filters_by_size[size_key]
            cross_filter = filters['Cross']
            x_filter = filters['X']

            pattern = case['input']

            # 크기가 어긋나면 계산 자체가 성립하지 않으므로
            # 이 케이스만 실패로 적고 다음으로 넘어감
            if not check_size(pattern, cross_filter):
                results.append({
                    'case_id': case_id,
                    'status': 'FAIL',
                    'reason': f'필터({size_key})와 패턴의 크기가 일치하지 않습니다.',
                })
                print(f'--- {case_id} ---')
                print(f'FAIL: 필터({size_key})와 패턴 크기 불일치')
                continue

            # 같은 패턴을 두 필터에 각각 통과시켜 점수를 냄
            score_cross = mac(pattern, cross_filter)
            score_x = mac(pattern, x_filter)
            verdict = decide(score_cross, score_x)

            # 정답도 같은 표준 라벨로 바꿔야 서로 비교할 수 있음
            expected = normalize_label(case['expected'])

            # 이 모드는 대조할 정답이 있으므로 통과와 실패를 가림.
            # 판정이 UNDECIDED 면 어떤 정답과도 같을 수 없어 실패가 됨.
            status = 'PASS' if verdict == expected else 'FAIL'
            print_case_result(case_id, score_cross, score_x, verdict, expected, status)

            # 실패한 이유를 나중에 요약에 쓰려고 문장으로 남김
            if status == 'PASS':
                reason = ''
            elif verdict == 'UNDECIDED':
                reason = '동점(UNDECIDED) 처리 규칙에 따라 FAIL'
            else:
                reason = f'판정({verdict})이 expected({expected})와 다름'

            results.append({
                'case_id': case_id,
                'status': status,
                'reason': reason,
            })

        except Exception as e:
            # 예상 못한 문제도 그 케이스만 실패로 적고 계속 진행함
            results.append({
                'case_id': case_id,
                'status': 'FAIL',
                'reason': f'처리 중 오류 발생: {e}',
            })
            print(f'--- {case_id} ---')
            print(f'FAIL: 처리 중 오류 발생 ({e})')

    # 3단계: 크기별 연산 시간을 잼.
    # 측정용 패턴은 직접 만들어 쓰므로 data.json 에 3x3 이 없어도 잴 수 있음.
    print_section('[3] 성능 분석 (평균/10회)')
    perf_rows = []
    perf_rows_1d = []

    for n in [3, 5, 13, 25]:
        p = make_pattern(n, 'cross')
        f = make_pattern(n, 'x')

        # 같은 입력으로 두 방식을 각각 재서 나중에 견줌
        perf_rows.append((n, measure(p, f), n * n))
        perf_rows_1d.append((n, measure_1d(p, f), n * n))

    print_perf_table(perf_rows)

    print_section('[3-1] 보너스: 1차원 배열 최적화 전/후 비교')
    print_perf_compare(perf_rows, perf_rows_1d)

    # 4단계: 모아둔 결과로 총계와 실패 목록을 냄
    print_section('[4] 결과 요약')
    print_summary(results)


# ============================================================
# 4부. 성능 측정
# ============================================================

def measure(pattern, filter_grid, repeat=10):
    """MAC 연산을 여러 번 반복해 평균 시간을 밀리초로 반환함."""
    times = []

    for _ in range(repeat):
        # 시작 시각을 찍음. perf_counter 는 경과 시간 전용이라
        # 시스템 시계가 바뀌어도 영향을 받지 않음.
        start = time.perf_counter()

        # 측정 구간에는 연산 호출만 둠.
        # 출력이나 파일 읽기가 섞이면 그 시간이 연산 시간을 덮어버려
        # 크기와 시간의 관계가 보이지 않게 됨.
        mac(pattern, filter_grid)

        times.append(time.perf_counter() - start)

    # 한 번만 재면 그 순간의 시스템 상황에 따라 크게 흔들리므로
    # 여러 번 재서 평균을 냄. 초 단위라서 1000을 곱해 밀리초로 바꿈.
    return (sum(times) / len(times)) * 1000


def to_1d(grid):
    """2차원 격자를 길이 N*N 의 1차원 리스트로 펴서 반환함."""
    flat = []

    # 행을 순서대로 이어붙여 한 줄로 만듦
    for row in grid:
        for value in row:
            flat.append(value)

    return flat


def mac_1d(pattern_1d, filter_1d):
    """1차원으로 편 두 리스트로 MAC 연산을 해 결과를 반환함."""
    total = 0.0

    # 2차원 방식은 행 리스트를 꺼낸 뒤 다시 열을 찾아야 하지만
    # 여기서는 인덱스 한 번으로 값에 바로 닿음.
    for i in range(len(pattern_1d)):
        total += pattern_1d[i] * filter_1d[i]

    return total


def measure_1d(pattern, filter_grid, repeat=10):
    """1차원 방식의 MAC 연산 평균 시간을 밀리초로 반환함."""
    # 변환은 측정 구간 밖에서 미리 해둠.
    # 비교 대상은 연산 자체이므로 변환 비용이 섞이면 공정하지 않음.
    pattern_1d = to_1d(pattern)
    filter_1d = to_1d(filter_grid)

    times = []

    for _ in range(repeat):
        start = time.perf_counter()
        mac_1d(pattern_1d, filter_1d)
        times.append(time.perf_counter() - start)

    return (sum(times) / len(times)) * 1000


# ============================================================
# 5부. 출력
# ============================================================

def print_case_result(case_id, score_cross, score_x, verdict, expected, result):
    """케이스 하나의 점수와 판정, 통과 여부를 출력함."""
    print(f'--- {case_id} ---')
    print(f'Cross 점수: {score_cross}')
    print(f'X 점수: {score_x}')
    print(f'판정: {verdict} | expected: {expected} | {result}')


def print_perf_table(rows):
    """크기별 평균 시간과 연산 횟수를 표로 출력함."""
    print(f'{"크기":<10}{"평균 시간(ms)":<18}{"연산 횟수"}')
    print('-' * 40)

    # 연산 횟수를 함께 보여줘야 시간 증가가 N*N 과 맞물리는지 볼 수 있음
    for n, avg_ms, op_count in rows:
        print(f'{n}×{n:<8}{avg_ms:<18.4f}{op_count}')


def print_perf_compare(rows_2d, rows_1d):
    """2차원 방식과 1차원 방식의 측정 결과를 나란히 비교해 출력함."""
    print(f'{"크기":<10}{"2차원(ms)":<15}{"1차원(ms)":<15}{"개선율"}')
    print('-' * 50)

    # 같은 크기끼리 짝지어 얼마나 줄었는지 비율로 보여줌
    for (n, t2, _), (_, t1, _) in zip(rows_2d, rows_1d):
        improve = (t2 - t1) / t2 * 100 if t2 > 0 else 0.0
        print(f'{n}×{n:<8}{t2:<15.4f}{t1:<15.4f}{improve:+.1f}%')


def print_summary(results):
    """전체 결과를 세어 통과와 실패 수를 내고 실패 목록을 출력함."""
    total = len(results)

    # 상태별로 갈라서 개수를 셈
    passed = [r for r in results if r['status'] == 'PASS']
    failed = [r for r in results if r['status'] == 'FAIL']

    print(f'총 테스트: {total}개')
    print(f'통과: {len(passed)}개')
    print(f'실패: {len(failed)}개')

    # 실패가 있을 때만 어떤 케이스가 왜 실패했는지 이어서 보여줌
    if failed:
        print()
        print('실패 케이스:')
        for r in failed:
            print(f'- {r["case_id"]}: {r["reason"]}')


# ============================================================
# 6부. 실행 흐름
# ============================================================

def main():
    """모드를 선택받아 해당 모드를 실행함."""
    print('=== Mini NPU Simulator ===')
    print()
    print('[모드 선택]')
    print('1. 사용자 입력 (3x3)')
    print('2. data.json 분석')

    # 올바른 번호가 들어올 때까지 반복해서 물음
    while True:
        choice = input('선택: ').strip()

        if choice == '1':
            run_mode1()
            break
        elif choice == '2':
            run_mode2()
            break
        else:
            print('잘못된 입력입니다. 1 또는 2를 입력하세요.')


if __name__ == '__main__':
    # 이 파일을 직접 실행했을 때만 프로그램을 시작함
    main()
