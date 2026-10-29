# B3-2 개발기획문서 — AI Git 커밋/PR 자동 생성기

> 분야 AI/SW 기초 · 구분 클라우드와 AI API · 40시간 · 필수
> 한 줄 요약: **`git status` / `git diff`를 AI API에 넘겨 커밋 메시지와 PR 초안을 터미널에 출력하는 Python CLI.**

| 항목 | 내용 |
|---|---|
| 문서 버전 | v1.0 (기획) |
| 작성일 | 2026-10-27 |
| 구현 방식 | **본인이 직접 구현** (이 문서는 설계도이며 구현 코드는 포함하지 않는다) |
| 언어 / 환경 | Python 3.10+ · 터미널 CLI · 웹 화면 없음 |

---

## 1. 프로젝트 개요

### 1.1 배경과 문제

커밋 메시지와 PR 설명은 **변경을 가장 잘 아는 사람이 변경 직후에 써야** 정확한데, 실제로는 귀찮아서
`update`, `fix`, `수정` 같은 정보 없는 문장으로 남기기 쉽다. 그러면 나중에 히스토리를 읽는 사람(미래의 자신 포함)이
"왜 바꿨는지"를 알 수 없다.

### 1.2 해결 방식

변경 사항(`git status`, `git diff`)은 이미 기계가 읽을 수 있는 텍스트다. 이것을 **AI에게 입력으로 주고**,
**우리 팀이 원하는 형식(길이·템플릿·표현 제한)에 맞는 초안**을 받아 사람이 검토하고 적용한다.

```
 ① 변경 수집        ② 전처리            ③ AI 호출          ④ 검증·출력
 git status/diff →  마스킹·분량 제한  →  프롬프트 + API  →  규칙 검사 → 터미널
 (subprocess)       (re)               (requests)         (str/re)
         └────────────── argparse CLI 가 전체를 감싼다 ──────────────┘
```

### 1.3 이 과제의 본질

과제 소개문의 핵심은 이 문장이다.

> API 호출 자체가 아니라 **"어떤 입력을 주느냐"**, 즉 **프롬프트 설계와 결과 품질 제어**가 이번 미션이다.

따라서 개발 시간의 무게중심은 `API 호출(20%)`이 아니라 **`프롬프트 설계 + 검증(40%)`** 에 둔다.

### 1.4 범위

| 포함 (In) | 제외 (Out) — 과제 제약 사항 |
|---|---|
| `git status`, `git diff` 수집 | `git push` 등 원격 반영 |
| 커밋 메시지 초안 출력 | **실제 `git commit` 실행** (초안 출력까지만) |
| PR 제목/본문 초안 출력 | GitHub PR 자동 생성 (API 연동) |
| 길이·템플릿 검증 | 웹 UI, 서버, DB |
| 민감정보 마스킹 / 분량 제한 | 대화형 다회 호출(요청 1~2회 이내) |

---

## 2. 요구사항 매핑표

과제 명세의 요구사항을 **구현 모듈 → 검증 방법**에 1:1로 연결한다. 구현이 끝나면 이 표로 자가 점검한다.

### 2.1 기능 요구사항

| ID | 요구사항 (명세) | 구현 모듈 | 검증 방법 |
|---|---|---|---|
| **R1-1** | Git 초기화된 루트에서 실행 | `git_utils` | `/tmp`에서 실행 시 안내 후 종료(Traceback 없음) |
| **R1-2** | `git status` 결과 수집, 변경 파일 목록 확인 | `git_utils.get_status()` | 변경 파일 수가 로그에 출력됨 |
| **R1-3** | `git diff` 결과 수집 | `git_utils.get_diff()` | diff 줄 수가 로그에 출력됨 |
| **R1-4** | 변경 사항 없으면 안내 후 종료 | `main` | "변경 사항이 없습니다" 출력 + API 호출 0회 |
| **R2-1** | API Key는 환경변수, 하드코딩 금지 | `ai_client` | 키 미설정 시 안내, `grep`으로 소스에 키 없음 확인 |
| **R2-2** | 실행 시 API 호출되어 결과가 터미널에 출력 | `ai_client` | 정상 실행 캡처 |
| **R2-3** | 호출 실패 시 **원인 포함** 메시지 | `ai_client` | 401/404/429/타임아웃/연결 실패 각각 다른 메시지 |
| **R2-4** | `-model` `-temperature` `-max-tokens` 옵션 | `main` (argparse) | 옵션 값이 실제 요청에 반영됨(로그 출력) |
| **R2-5** | 결과물에 **변경 요약**이 함께 출력 (명세 "최종 결과물 1") | `git_utils.summarize_changes` | 파일 수·상태별 개수·+/- 줄 수가 출력됨. **API 호출 증가 없음** |
| **R3-1** | `commit` 명령 → 메시지 출력 | `main`, `prompts` | 정상 실행 캡처 |
| **R3-2** | 제목 1줄 필수, 본문은 선택 | `validators` | 제목 줄 존재 검사 |
| **R3-3** | 본문 포함 시 파일 1~3개 언급 **또는** 핵심 변경 1~2개 불릿 | `prompts`, `validators` | 본문 불릿 수 검사 |
| **R4-1** | `pr` 명령 → 제목/본문 초안 | `main`, `prompts` | 정상 실행 캡처 |
| **R4-2** | 본문에 `Why` / `What` / `How to Test` 헤더 | `validators` | 3개 헤더 존재 검사 |
| **R4-3** | 각 섹션에 불릿 1개 이상 | `validators` | 섹션별 `- ` 개수 검사 |
| **R4-4** | PR 제목 1줄 | `validators` | 줄바꿈 없음 검사 |
| **R5-1** | 커밋 제목 50자 권장 / **최대 72자** | `validators` | `len()` 검사 |
| **R5-2** | PR 제목 **최대 80자** | `validators` | `len()` 검사 |
| **R5-3** | 검증 후 **재생성 또는 후처리 중 택1** | `main` | §6에서 "재생성"으로 확정 |
| **R5-4** | 최종 출력은 구분선/헤더로 구획 | `main` | 출력 형식 §4.4 |
| **R6-1** | GitHub push, 커밋 히스토리·브랜치 흐름 | git 운영 | §9 브랜치 전략 |
| **R6-2** | README: 설치·키 설정·사용 예·출력 예·보안 또는 비용 | `README.md` | §10 체크리스트 |

### 2.2 제약 사항

| 제약 | 대응 |
|---|---|
| 1회 실행당 API 요청 **1~2회 이내** | `commit`/`pr` 각 **1회**, 검증 실패 시 재생성 **최대 1회** → 상한 2회. **호출 횟수를 로그로 출력** |
| 민감정보 보호: (A) 마스킹 또는 (B) 분량 제한 중 1개 이상을 `-safe-mode`로 제공 | **A와 B 둘 다 구현** (§7) |
| Git 연동은 `status`, `diff` 범위 | `git branch --show-current`는 PR 예시 출력(`현재 브랜치`)에 필요 → **허용 범위 해석은 §11 미결사항 참고** |
| 생성물은 정답이 아니며 사용자가 검토 | 출력 하단에 "초안입니다. 검토 후 적용하세요" 문구 |

---

## 3. 기술 결정

### 3.1 결정 요약

| 항목 | 결정 | 이유 |
|---|---|---|
| HTTP 클라이언트 | **`requests`로 REST 직접 호출** | 과제 목표 1이 "REST로 연동하는 **전체 흐름**(요청 구성·응답 처리·예외 대응)을 설명"이라서, SDK가 감춰주는 부분을 직접 보는 게 학습 목적에 맞다 |
| Git 연동 | `subprocess.run([...], capture_output=True, text=True, check=False)` | 표준 라이브러리. 리스트 인자로 셸 인젝션 방지 |
| CLI | `argparse` 서브커맨드 (`commit`, `pr`) | 표준 라이브러리. 의존성 0 |
| 마스킹 | `re` | 표준 라이브러리 |
| 외부 의존성 | **`requests` 1개** | 최소 의존성 |
| 기본 모델 | **`claude-haiku-4-5`** (옵션으로 변경 가능) | 아래 3.2 참고 |

### 3.2 ⚠️ `temperature` 모델 제약 (설계에 영향)

과제는 `temperature`를 CLI 옵션으로 요구하는데, **최신 Claude 모델(Opus 5.5 / Sonnet 5.5 등)은 `temperature`를
기본값이 아닌 값으로 보내면 400 에러**를 낸다. 반면 `claude-haiku-4-5`는 `temperature` 0.0~1.0을 받는다.

| 후보 | `temperature` | 가격(입력/출력 per 1M tok) | 판단 |
|---|---|---|---|
| **`claude-haiku-4-5`** | ✅ 사용 가능 | $1 / $5 | **기본값으로 채택** |
| `claude-sonnet-4-6` | ✅ 사용 가능 | $3 / $15 | 품질 비교용 `--model`로 선택 |
| `claude-opus-5-5` 등 최신 | ❌ 400 | $4 / $20 | `--model`로 쓸 수는 있으나 temperature 옵션은 무시/경고 필요 |

> **이게 README에 들어갈 좋은 학습 포인트다.** "옵션을 받아서 그대로 보내는 것"과
> "모델이 그 옵션을 지원하는지 확인하는 것"은 다르다는 걸 실제 400 에러로 겪은 기록을 남긴다.

### 3.3 API 제공자 — 미결 (§11 참고)

이전 `gpt_api` 실습은 **Codyssey 제공 프록시**(`https://copa.codyssey.kr/v1`, OpenAI 호환 형식)를 썼다.
이번 과제의 "AI API Key"가 **Anthropic 직접 키**인지 **Codyssey 프록시 키**인지에 따라 요청 형식이 다르다.

| | Anthropic 직접 | Codyssey 프록시 (OpenAI 호환) |
|---|---|---|
| 엔드포인트 | `POST https://api.anthropic.com/v1/messages` | `POST https://copa.codyssey.kr/v1/chat/completions` |
| 인증 헤더 | `x-api-key` + `anthropic-version: 2023-06-01` | `Authorization: Bearer <키>` |
| system 위치 | **최상위 `system` 필드** | `messages` 안의 `role: "system"` |
| 응답에서 텍스트 | `content[0].text` | `choices[0].message.content` |

**설계 대응**: 제공자 차이를 **`ai_client.py` 한 파일에 가둔다.** 나머지 모듈은 `call_ai(system, user, model, temperature, max_tokens) -> str`
하나만 알면 되므로, 제공자가 바뀌어도 이 파일만 고친다.

---

## 4. 시스템 설계

### 4.1 모듈 구성

```
B3-2/
├── main.py            CLI 진입점. 파이프라인 오케스트레이션
├── git_utils.py       git status / diff / branch 수집
├── sanitizer.py       민감정보 마스킹 + diff 분량 제한
├── prompts.py         system 프롬프트 상수, user 프롬프트 조립
├── ai_client.py       REST 호출, 응답 파싱, 예외 → 사용자 메시지 변환
├── validators.py      커밋/PR 규칙 검사
├── tests/             assert 기반 자가 검증 (sanitizer, validators)
├── logs/              실행 증거 로그
├── docs/PLAN.md       이 문서
├── README.md
├── .gitignore         .env, __pycache__ 제외
└── requirements.txt   requests
```

> 모듈을 6개로 나누는 이유: **각 모듈이 한 가지만** 하면, API 키 없이도 `git_utils` / `sanitizer` / `validators`를
> 단독으로 테스트할 수 있다. 막히는 지점이 "AI"가 아니라 "git이 비어 있음" 같은 사소한 곳이 대부분이기 때문이다.

### 4.2 모듈별 인터페이스 (시그니처만, 본문은 직접 구현)

```python
# git_utils.py
def run_git(args: list[str]) -> str: ...        # 실패 시 RuntimeError(원인 포함)
def is_git_repo() -> bool: ...
def get_status() -> list[str]: ...              # porcelain 줄 목록
def get_diff() -> str: ...                      # 스테이징 전 + 후 합본
def get_branch() -> str: ...
def summarize_changes(status: list[str], diff: str) -> dict: ...   # 파일 수, 수정/추가/삭제 개수, +/- 줄 수 (로컬 계산)

# sanitizer.py
def mask(text: str) -> str: ...                 # 정규식 마스킹
def limit_diff(diff: str, max_files: int, max_lines: int) -> tuple[str, bool]: ...  # (잘린 diff, 잘렸는지)

# prompts.py
COMMIT_SYSTEM: str
PR_SYSTEM: str
def build_user_prompt(status: list[str], diff: str, branch: str | None) -> str: ...

# ai_client.py
def call_ai(system: str, user: str, model: str, temperature: float, max_tokens: int) -> AiResult: ...
# AiResult: text, input_tokens, output_tokens, stop_reason
# 실패 시 AiError(사용자에게 보여줄 메시지)

# validators.py
def validate_commit(text: str) -> list[str]: ...    # 위반 목록(빈 리스트면 통과)
def validate_pr(title: str, body: str) -> list[str]: ...
def split_pr(text: str) -> tuple[str, str]: ...    # (제목, 본문)

# main.py
def main() -> int: ...                          # 종료 코드 반환
```

### 4.3 데이터 흐름

```
main
 ├─ is_git_repo()?  ── 아니오 → [ERROR] 안내, exit 1
 ├─ get_status(), get_diff()
 ├─ 둘 다 비었나?   ── 예 → [INFO] 변경 사항 없음, exit 0   (API 호출 0회)
 ├─ summarize_changes()   로컬 계산이라 API 호출 아님
 ├─ (--safe-mode) mask(), limit_diff()
 ├─ build_user_prompt()
 ├─ 키 확인          ── 없음 → [ERROR] 안내, exit 1
 ├─ call_ai()  ◀── 호출 1회차
 ├─ validate_*()
 │     └─ 위반 있음 → 위반 내용을 프롬프트에 덧붙여 call_ai() ◀── 호출 2회차 (최대 1회)
 └─ 구획된 출력, 호출 횟수·토큰 로그
```

### 4.4 CLI 명세

```bash
python main.py commit [옵션]     # 커밋 메시지 초안
python main.py pr     [옵션]     # PR 제목/본문 초안
```

| 옵션 | 타입 | 기본값 | 설명 |
|---|---|---|---|
| `--model` | str | `claude-haiku-4-5` | 사용할 모델 |
| `--temperature` | float | `0.3` | 낮을수록 일관됨. 커밋 메시지는 창의성보다 일관성이 중요 |
| `--max-tokens` | int | `1024` | 출력 상한. 너무 작으면 PR 본문이 중간에 잘림 |
| `--safe-mode` | flag | off | 마스킹 + 분량 제한 켬 |

> **명세 표기 주의**: 과제는 `-model` 처럼 **하이픈 1개**로 예시했지만, `argparse` 관례는 **`--model`(하이픈 2개)** 이다.
> 두 형태를 모두 허용(`parser.add_argument("-model", "--model", ...)`)해서 명세와 관례를 둘 다 만족시킨다.

### 4.5 출력 형식

명세 예시(`[INFO]` / `[DONE]` / `--- ... ---`)를 따른다.

```
[INFO] Git status 수집 완료: 3개 파일 변경 감지
[INFO] Git diff 수집 완료: 128줄
[INFO] AI API 요청 중... (model=claude-haiku-4-5, temperature=0.3, max_tokens=1024)
[INFO] API 호출 1회 · 입력 1,842 / 출력 187 토큰
[DONE] 커밋 메시지 생성 완료

--- Change Summary ---
변경 파일 3개 (수정 2 · 추가 1) · +128 / -34 줄
  M  main.py
  M  git_utils.py
  ?? sanitizer.py
----------------------

--- Commit Message ---
feat: Git 변경 사항 기반 커밋 메시지 자동 생성 기능 추가

- git diff 결과를 수집해 AI 입력 컨텍스트로 전달
- 커밋 메시지 템플릿 생성 규칙 적용
----------------------
※ AI가 만든 초안입니다. 검토 후 적용하세요.
```

PR은 `--- Change Summary ---` 다음에 `--- PR Title ---` / `--- PR Body ---` 구획으로 나눈다.

> **변경 요약은 AI가 아니라 로컬에서 계산한다.** `git status` 줄 수와 diff 텍스트의 `+`/`-` 줄을 세면 되므로
> API 호출이 늘지 않고(1~2회 제약 유지), AI가 숫자를 지어낼 위험도 없다. 명세의 "변경 요약"을 이렇게 충족한다.

### 4.6 오류 시나리오와 종료 코드

원칙: **사용자에게 Traceback을 보여주지 않는다.** 한 줄 원인 + 해결 힌트 + 비정상 종료 코드.

| 상황 | 감지 방법 | 사용자 메시지 | 종료 코드 |
|---|---|---|---|
| git 저장소 아님 | `git`의 returncode `128` | `[ERROR] Git 저장소가 아닙니다. 프로젝트 루트에서 실행하세요.` | 1 |
| 변경 없음 | status·diff 모두 빈 문자열 | `[INFO] 변경 사항이 없습니다. ... 종료합니다.` | **0** (오류 아님) |
| API 키 없음 | `os.environ.get` → `None` | `[ERROR] AI_API_KEY 환경변수가 설정되지 않았습니다.` + `export` 예시 | 1 |
| 인증 실패 | HTTP **401** | `[ERROR] API 인증 실패(401): 키를 확인하세요.` | 1 |
| 모델 없음 | HTTP **404** | `[ERROR] 모델을 찾을 수 없습니다(404): <모델명>` | 1 |
| 요청 형식/파라미터 | HTTP **400** | `[ERROR] 요청 오류(400): <서버 메시지>` ← `temperature` 미지원 모델이 여기 | 1 |
| 호출 한도 초과 | HTTP **429** | `[ERROR] 요청 한도 초과(429): 잠시 후 다시 시도하세요.` | 1 |
| 서버 오류 | HTTP **500/529** | `[ERROR] AI 서버 오류(<코드>): 잠시 후 다시 시도하세요.` | 1 |
| 시간 초과 | `requests.Timeout` | `[ERROR] 요청 시간 초과(60초).` | 1 |
| 네트워크 끊김 | `requests.ConnectionError` | `[ERROR] 네트워크에 연결할 수 없습니다.` | 1 |
| 응답이 잘림 | `stop_reason == "max_tokens"` | `[WARN] 응답이 max_tokens에서 잘렸습니다. --max-tokens를 늘리세요.` | 계속 진행 |

> 서버 에러 응답은 JSON이며 `error.message`에 **이유가 한 줄로** 들어 있다. 이를 그대로 덧붙이면 가장 친절하다.

---

## 5. 프롬프트 설계

### 5.1 역할 분리

| 구분 | 넣는 내용 | 성격 |
|---|---|---|
| **`system`** | 역할, **출력 형식 규칙**, 금지 사항, 예시 1개 | 매번 같음 (불변) |
| **`user`** | 브랜치명, `git status` 목록, (마스킹·절단된) `git diff` | 매번 다름 (가변) |

### 5.2 형식을 강제하는 3가지 기법

1. **숫자로 못 박기** — "짧게" ❌ → "제목은 50자 이내, 절대 72자 초과 금지" ✅
2. **금지사항 명시** — "코드 블록(백틱 3개로 감싸는 형식)·인사말·설명 문장 없이 메시지 본문만 출력"
3. **예시 1개 제시(few-shot)** — 가장 효과가 크다. 단, 예시 내용을 그대로 베끼지 않도록 "형식만 참고" 명시

### 5.3 `commit` 프롬프트 규칙 초안

- 제목 1줄: `type: 설명`, type ∈ {feat, fix, docs, refactor, test, chore}
- 제목은 50자 이내(최대 72자), 마침표로 끝내지 않음, **명령형 한국어**
- 제목 다음 빈 줄, 이후 본문(선택)
- 본문은 `- ` 불릿 1~2개로 **핵심 변경**만, 또는 변경 파일 1~3개 언급
- "왜 바꿨는지"를 diff에서 추론 가능한 만큼만 쓰고, **추측으로 사실을 지어내지 않는다**
- 출력은 메시지 텍스트만

### 5.4 `pr` 프롬프트 규칙 초안

- 첫 줄: 제목 (80자 이내, 1줄)
- 빈 줄 후 본문, 헤더는 **정확히** `## Why` / `## What` / `## How to Test`
- 각 섹션에 `- ` 불릿 1개 이상
- How to Test는 **실제로 실행 가능한 명령**으로 (예: `python main.py commit`)

### 5.5 diff가 AI 입력으로 부적합한 경우

| 케이스 | 문제 | 처리 |
|---|---|---|
| **새로 만든 파일(untracked)** | `git status`엔 `??`로 보이지만 `git diff`에는 **내용이 안 나옴** | 파일명만 "새 파일" 목록으로 전달 |
| **`git add`한 변경(staged)** | `git diff`에 안 나옴 | `git diff --cached`를 함께 수집해 합침 |
| **바이너리 파일** (예: `.db`, 이미지) | `Binary files differ` 한 줄뿐 | 그대로 두되 "바이너리 변경" 으로 요약됨 |
| **diff가 너무 큼** | 비용·품질 저하 | `limit_diff`로 절단 후 "일부만 전송" 사실을 프롬프트에 명시 |

### 5.6 프롬프트 개선 기록 계획

과제의 평가 포인트는 "품질을 제어한 경험"이다. 프롬프트를 **버전으로 관리**하고 개선 이유를 남긴다.

| 버전 | 변경 | 관찰 기대 |
|---|---|---|
| v1 | 규칙 없이 "커밋 메시지 써줘" | 제목이 길고 형식이 제각각 |
| v2 | 길이·형식 규칙 추가 | 형식은 맞으나 코드 블록이 섞임 |
| v3 | 금지사항 + 예시 1개 | 안정 |

→ `logs/`에 v1/v2/v3 출력을 나란히 저장해 README의 근거로 쓴다.

---

## 6. 출력 검증 정책 (R5-3: 재생성으로 확정)

### 6.1 검증 규칙

| 대상 | 규칙 | 심각도 |
|---|---|---|
| 커밋 제목 | 존재, 1줄 | 오류 |
| 커밋 제목 길이 | ≤ 50 권장 / **> 72 오류** | 50 초과 경고, 72 초과 오류 |
| 커밋 제목 끝 | 마침표 금지 | 경고 |
| 커밋 본문(있다면) | 불릿 1개 이상 **또는** 파일 언급 | 오류 |
| 공통 | 코드 블록(백틱 3개) 포함 금지 | 오류 |
| PR 제목 | 존재, 1줄, **≤ 80자** | 오류 |
| PR 본문 | `## Why` `## What` `## How to Test` **3개 모두** | 오류 |
| PR 섹션 | 섹션마다 `- ` 불릿 ≥ 1 | 오류 |

### 6.2 실패 시 정책 — "재생성 최대 1회" 선택

| 선택지 | 장점 | 단점 |
|---|---|---|
| 후처리(잘라내기 등) | API 호출 1회 유지 | 제목을 자르면 문장이 어색해짐. **섹션 누락은 후처리로 못 고침** |
| **재생성 (채택)** | 의미가 온전한 결과 | 호출 최대 2회 |

**채택 이유**: PR 섹션 누락 같은 **구조적 오류는 후처리로 해결할 수 없다.** 또한 과제 제약(1회 실행당 1~2회)이
재생성 1회를 정확히 허용한다.

**동작**
1. 1회차 결과 검증
2. 오류가 있으면, 위반 내용을 목록으로 만들어 `user` 프롬프트에 덧붙여 **딱 1회** 재요청
   (예: "이전 출력의 제목이 83자였다. 72자 이내로 다시 작성하라.")
3. 2회차 결과도 오류면 **포기하고 그대로 출력 + `[WARN]`으로 위반 항목 표시** (무한 재시도 금지)

---

## 7. 보안·민감정보 (`--safe-mode`)

명세는 (A) 마스킹 **또는** (B) 분량 제한 중 1개 이상을 요구한다. **둘 다 구현**하고, 켜고 끈 결과를 비교해 보너스 3의 근거로 삼는다.

### 7.1 (A) 마스킹 규칙

| 대상 | 정규식 방향 | 치환 |
|---|---|---|
| Anthropic 키 | `sk-ant-` + 영숫자/`_-` 20자 이상 | `[MASKED_API_KEY]` |
| OpenAI 형태 키 | `sk-` + 영숫자 20자 이상 | `[MASKED_API_KEY]` |
| 이메일 | `local@domain.tld` | `[MASKED_EMAIL]` |
| 휴대전화 | `01X-XXXX-XXXX` (하이픈 선택) | `[MASKED_PHONE]` |
| `KEY=값` 형태 | `(API_KEY\|SECRET\|TOKEN\|PASSWORD)\s*[=:]\s*\S+` | 값만 `[MASKED]` |

> **원칙: "오탐은 허용하되 누락은 허용하지 않는다."** 주석 속 예시 이메일까지 가려져도 괜찮다. 키가 새는 것보다 낫다.
> 이 원칙을 README에 명시한다.

### 7.2 (B) 분량 제한

| 기준 | 값 |
|---|---|
| 최대 파일 수 | **10개** |
| 최대 줄 수 | **200줄** (전체 diff 기준) |
| 초과 시 | 앞에서부터 자르고, 프롬프트에 `※ 총 N줄 중 200줄만 전송됨` 명시 |

분량 제한은 **비용 절감 효과**도 있다.

### 7.3 safe-mode와 무관한 기본 방어

| 항목 | 대응 |
|---|---|
| API 키 하드코딩 | 금지. 환경변수만. `.env`는 `.gitignore` |
| 로그에 키 출력 | 금지. 키 존재 여부만 `설정됨/미설정`으로 표시 |
| `.env`·`*.pem` 등 파일의 diff | safe-mode와 무관하게 **파일명 패턴으로 제외하는 방안 검토**(§11) |

---

## 8. 테스트 계획

### 8.1 단위 테스트 (API 키 불필요, `assert`로 자가 검증)

| 대상 | 케이스 |
|---|---|
| `sanitizer.mask` | 키/이메일/전화 마스킹됨 · **정상 문장은 그대로**(오탐 없음) |
| `sanitizer.limit_diff` | 500줄 → 200줄 이하 · 절단 여부 플래그 · 짧은 입력은 그대로 |
| `validators.validate_commit` | 73자 제목 오류 · 50 초과 경고 · 마침표 경고 · 코드 블록 오류 |
| `validators.validate_pr` | 섹션 누락 오류 · 불릿 없는 섹션 오류 · 81자 제목 오류 |
| `git_utils` | `/tmp`에서 `is_git_repo()` False · staged만 있어도 변경 감지 |

### 8.2 통합/수동 시나리오 (증거 로그로 남김)

| # | 시나리오 | 기대 결과 | 증명하는 것 |
|---|---|---|---|
| T1 | 정상 `commit` | 구획된 출력 + 호출 1회 로그 | R2-2, R3-1 |
| T2 | 정상 `pr` | 3개 섹션 포함 | R4-1~3 |
| T3 | 변경 없음 | 안내 후 종료, **호출 0회** | R1-4 |
| T4 | git 폴더 아님 | 한 줄 안내, Traceback 없음, 종료 코드 1 | R1-1 |
| T5 | 키 미설정 | 안내 + `export` 예시 | R2-1 |
| T6 | 키를 `wrong`으로 | 401 메시지 | R2-3 |
| T7 | `--model claude-xxx` | 404 메시지 | R2-3 |
| T8 | 최신 모델 + `--temperature 0.7` | 400 메시지(미지원) | §3.2 |
| T9 | `--temperature 0.0` vs `1.0` 각 3회 | 0.0은 거의 동일, 1.0은 표현이 다양 | **과제 목표 2** |
| T10 | `--max-tokens 50` | `[WARN]` 잘림 경고 | **과제 목표 2** |
| T11 | PR + `--max-tokens 100` | 섹션 누락 → 재생성 → 결과 | R5-3 |
| T12 | `--safe-mode` OFF vs ON (키/이메일 포함 diff) | ON에서 `[MASKED_*]` | 보너스 3 |
| T13 | 새 파일만 추가한 상태 | 파일명이 "새 파일"로 전달 | §5.5 |

### 8.3 일부러 깨뜨려 보기 (Red Team)

- diff에 `sk-ant-api03-...` 가짜 키를 넣고 `--safe-mode` 없이 실행 → **프롬프트에 그대로 들어가는지 확인** (위험성 증명)
- 같은 입력에 `--safe-mode` → 가려지는지 확인
- 이 두 결과를 **README의 보안 섹션 근거**로 쓴다.

---

## 9. 일정과 Git 운영

### 9.1 5일 개발 일정 (학습 가이드와 연동)

| 일 | 개발 | 학습 | 완료 증거 |
|---|---|---|---|
| **1** | `git_utils` | `subprocess` 사이클 | `/tmp`에서 안내 후 종료, 변경 파일 수 정확 |
| **2** | `main` CLI 뼈대 | `argparse` 사이클 | `commit`/`pr` + 옵션 4개가 값으로 출력 |
| **3** | `ai_client` | `requests`+예외 사이클 | 401/404/타임아웃 각각 다른 메시지 |
| **4** | `sanitizer`, `validators` | `re` + `assert` | 단위 테스트 통과, T9/T10 캡처 |
| **5** | `prompts` 개선 + 통합 + README | 프롬프트 설계 | T1~T13 로그, README 완성 |

### 9.2 브랜치 전략 (R6-1: "커밋 히스토리와 브랜치 작업 흐름 확인")

```
main
 ├─ feature/git-collector     git_utils
 ├─ feature/cli               main.py, argparse
 ├─ feature/ai-client         ai_client
 ├─ feature/safe-mode         sanitizer
 ├─ feature/validators        validators
 ├─ feature/prompts           prompts (v1→v3)
 └─ docs/readme               README, logs
```

- 기능마다 브랜치 → `main`으로 머지 (최소 3개 이상 머지 기록)
- **한 커밋 = 한 의도.** 모듈 하나를 완성할 때마다 커밋
- 완성 후 **이 도구로 자기 자신의 커밋 메시지를 생성**해 본다 → README의 "실제 사용 예시"로 활용 (보너스 1과 연결)

### 9.3 커밋 컨벤션 (본인 리포지토리 기존 스타일 유지)

```
Add: git 변경 사항 수집 모듈
Fix: git 저장소가 아닐 때 Traceback 대신 안내 출력
Docs: README 보안 섹션 추가
```

---

## 10. 산출물과 README 계획

### 10.1 제출물

| # | 산출물 | 위치 |
|---|---|---|
| 1 | 동작하는 CLI (단일 실행으로 끝까지 동작) | `main.py` 외 |
| 2 | GitHub 리포지토리 (push, 히스토리, 브랜치) | `Dong-tak/codyssey` `B3-2/` |
| 3 | 사용 가이드 | `README.md` |

### 10.2 README 목차 (요구: 설치·키·사용 예·출력 예·보안 또는 비용 중 1개 이상)

1. 소개 (한 줄 + 동작 흐름 그림)
2. 설치 (`python3 --version`, `pip install -r requirements.txt`)
3. 환경변수 설정 (macOS/Linux `export`, 영구 설정은 `~/.zshrc`, **키를 코드/커밋에 넣지 말 것**)
4. 사용법: `commit` / `pr` / 옵션 표
5. **출력 예시** (실제 실행 결과 그대로)
6. 오류 대응 표 (§4.6)
7. **파라미터 가이드**: `temperature` / `max_tokens`가 결과에 준 영향 (T9, T10 실측)
8. **프롬프트 설계**: v1→v3 개선 기록
9. **보안·민감정보**: safe-mode ON/OFF 비교 (T12)
10. **비용·호출 제한**: 1회 실행 호출 횟수, 토큰 사용량
11. 한계와 주의 (AI 출력은 초안, untracked 파일 등)

### 10.3 비용 추정 (가정치)

`claude-haiku-4-5` 기준 단가 입력 $1 / 출력 $5 (per 1M 토큰).
diff 200줄 ≈ 입력 4,000토큰, 출력 500토큰으로 **가정**하면 1회 약 `$0.004 + $0.0025 ≈ $0.007` (1센트 미만).
실제 값은 응답의 `usage`로 측정해 README에 **실측치로 교체**한다.

---

## 11. 미결 사항과 리스크

| # | 항목 | 현황 | 결정 필요 시점 |
|---|---|---|---|
| **Q1** | **API 제공자**: Anthropic 직접 키 vs Codyssey 프록시 키 | **미확정.** 과제 안내/수령한 키로 확인 필요 | **Day 3 시작 전** (`ai_client` 작성 전) |
| Q2 | 환경변수 이름 | 명세 예시는 `AI_API_KEY` → **그대로 채택**. 제공자별 대체 변수는 지원하지 않음 | 확정 |
| Q3 | `git branch --show-current`가 "status/diff 범위"에 해당하는가 | 명세의 PR 출력 예시에 `현재 브랜치`가 있어 **필요**. 읽기 전용 조회이므로 허용으로 해석 | 확정(README에 해석 명시) |
| Q4 | `.env` 등 민감 **파일 자체**를 diff에서 제외할지 | 제외 패턴을 두면 safe-mode의 안전성이 올라감 | Day 4 |
| Q5 | `--safe-mode` 기본값 | 명세는 "옵션으로 제공"이므로 **기본 OFF**, README에서 ON 권장 안내 | 확정 |

### 리스크

| 리스크 | 가능성 | 영향 | 대응 |
|---|---|---|---|
| `temperature`가 모델 미지원으로 400 | 높음(최신 모델 선택 시) | 중 | 기본 모델을 `claude-haiku-4-5`로, 400 메시지에 원인 안내 |
| 새 파일/staged 변경이 diff에서 누락 → "변경 없음" 오판 | **높음** | **높음** | status가 비어있지 않으면 diff가 비어도 진행, `--cached` 병합 |
| 한글이 `\xed\x95...`로 깨짐 | 중 | 높음 | `text=True`(필요 시 `encoding="utf-8"`) |
| AI가 코드 블록/인사말을 섞어 출력 | 높음 | 중 | 금지 규칙 + 검증 + 재생성 1회 |
| 응답이 `max_tokens`에서 잘림 | 중 | 중 | `stop_reason` 확인 후 경고 |
| 호출 횟수 초과(재시도 루프) | 낮음 | 중 | 재생성 **상한 1회 하드코딩**, 호출 카운터 로그 |
| 키가 커밋에 섞임 | 낮음 | **치명** | `.gitignore`, 커밋 전 `git diff --cached` 확인 |
| 직접 구현 경험이 부족한 모듈(`subprocess`/`argparse`/`requests`) | 높음 | 중 | 학습 사이클 병행(§9.1), 모듈 단위 선 구현 |

---

## 12. 완료 기준 (Definition of Done)

- [ ] `python main.py commit` / `python main.py pr` 가 **단일 실행으로 끝까지** 동작
- [ ] 변경 없음 · 키 없음 · 키 오류 · 모델 오류 · 타임아웃 · git 아님이 **전부 Traceback 없이** 안내됨
- [ ] `--model` `--temperature` `--max-tokens` `--safe-mode` 가 모두 동작
- [ ] 커밋 제목 ≤72자, PR 제목 ≤80자, PR 3섹션+불릿이 **검증으로 보장**됨
- [ ] 1회 실행 API 호출 ≤2회, 호출 횟수가 로그에 출력됨
- [ ] `grep -r "sk-" .` 에 실제 키가 **없음**
- [ ] README에 설치·키 설정·사용 예·출력 예·보안(또는 비용)이 있고, **문서만 보고 실행 가능**
- [ ] GitHub에 push, **브랜치 3개 이상 머지** 기록
- [ ] T1~T13 증거 로그 존재

### 과제 목표 자가 점검 (말로 설명할 수 있는가)

| # | 설명해야 할 것 | 근거 자료 |
|---|---|---|
| 1 | REST 연동의 전체 흐름(요청 구성·응답 처리·예외 대응) | §3, §4.6 / T5~T8 |
| 2 | `temperature`·`max_tokens`가 결과 품질에 주는 영향 | T9, T10 실측 |
| 3 | git status/diff 결과를 프로그램 입력으로 연결하는 방식 | §4.3, §5.5 |
| 4 | 양식과 변경 맥락으로 프롬프트를 구성하는 원리 | §5 (v1→v3) |
| 5 | 생성 결과를 길이·템플릿 규칙으로 검증하고 다듬는 이유 | §6, T11 |

---

## 13. 보너스 과제 계획 (선택)

| # | 보너스 | 접근 | 증빙 |
|---|---|---|---|
| 1 | 실제 리포지토리에 적용해 PR 1건 | 이 `codyssey` 리포지토리의 다른 과제(예: B6-1 README 개선)에 변경을 만들고, 본 도구로 커밋/PR 초안 생성 후 실제 PR 작성 | PR 링크 + "AI 초안 → 최종 PR" 변경점 5~10줄 |
| 2 | 커밋/PR 컨벤션 커스터마이징 | 기존 커밋 스타일(`Add:`/`Fix:`…) 분석 → `--convention` 옵션 또는 설정 파일로 prefix·템플릿 교체 | 컨벤션 문서 + 적용 전/후 비교 1회 |
| 3 | 안전 모드 고도화 | 마스킹 규칙 확장, 파일/줄 제한을 옵션으로 조정 가능하게 | 정책(숫자 기준 포함) + ON/OFF 비교 |

> **우선순위**: 필수 요구사항(§12) 완료 → 보너스 3 (이미 §7에서 대부분 구현) → 보너스 1 → 보너스 2.
