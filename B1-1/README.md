# 🎯 김동탁 포트폴리오

> **Codyssey B1-1** — 나를 소개하는 웹페이지 처음부터 만들기 (웹 기초와 프론트엔드)

순수 **HTML / CSS / JavaScript**만으로 만든 반응형 포트폴리오 웹사이트입니다.
React·Vue·jQuery·Bootstrap 같은 외부 라이브러리를 전혀 사용하지 않았습니다.

- **배포 URL**: https://dong-tak.github.io/codyssey/B1-1/
- **저장소**: https://github.com/Dong-tak/codyssey (`B1-1/` 디렉터리)

---

## 1. 프로젝트 개요

프레임워크를 쓰기 전에 브라우저가 실제로 어떻게 동작하는지 이해하는 것을 목표로 만들었습니다.
화면을 예쁘게 그리는 것보다 **"사용자 이벤트 → 상태 변경 → DOM 업데이트"** 라는 흐름이
코드에 명확히 드러나도록 구조를 잡는 데 중점을 두었습니다.

이 흐름은 React의 상태-렌더링 모델과 같은 구조이며, 이 프로젝트는 그 기초를
라이브러리 없이 직접 구현해 본 결과물입니다.

---

## 2. 사용 기술

| 구분 | 내용 |
|---|---|
| **마크업** | HTML5 시맨틱 태그 (`header`, `nav`, `main`, `section`, `article`, `footer`) |
| **스타일** | CSS3 — CSS 변수(`:root`), Flexbox, Grid, 미디어 쿼리, 트랜지션 |
| **스크립트** | Vanilla JavaScript (ES6+) — `const`/`let`, 화살표 함수, 템플릿 리터럴, 구조분해 할당, `map`/`filter`/`forEach` |
| **비동기** | `fetch` + `async/await` + `try/catch` |
| **브라우저 API** | Intersection Observer, localStorage, matchMedia |
| **외부 연동** | GitHub REST API (`/users/{user}/repos`) |
| **배포** | GitHub Pages |

> 외부 라이브러리 의존성이 **0개**입니다. `npm install` 없이 `index.html`만 열면 동작합니다.

---

## 3. 실행 방법

### 로컬에서 실행

```bash
git clone https://github.com/Dong-tak/codyssey.git
cd codyssey/B1-1
python3 -m http.server 5500
```

브라우저에서 `http://localhost:5500` 접속

VS Code를 쓴다면 **Live Server** 확장을 설치하고 `index.html`에서 우클릭 → *Open with Live Server*

> `file://`로 직접 열어도 화면은 보이지만, GitHub API 호출이 브라우저 보안 정책에 막힐 수 있어
> 로컬 서버로 여는 것을 권장합니다.

---

## 4. 기능 목록

### 섹션 구성

| 섹션 | 내용 |
|---|---|
| **Hero** | 타이핑 효과가 적용된 이름, 좌우명, CTA 버튼 2개 |
| **About** | 프로필 이미지, 자기소개, 경력 타임라인 4건 |
| **Skills** | Frontend / Language / Tools 3개 카테고리 |
| **Projects** | GitHub API로 실시간 조회한 저장소 카드 (언어별 필터 포함) |
| **Contact** | 문의 폼 (유효성 검사 + 메일 전송) |
| **Footer** | 저작권, GitHub · Product Hunt · Email 링크 |

### 인터랙션

| 기능 | 동작 | 기준값 |
|---|---|---|
| **햄버거 메뉴** | 모바일에서 버튼 클릭 시 메뉴 열림/닫힘, 메뉴 선택 시 자동으로 닫힘 | 768px 미만에서 노출 |
| **부드러운 스크롤** | 네비게이션 클릭 시 해당 섹션으로 부드럽게 이동 | `scroll-behavior: smooth` |
| **네비게이션 배경 전환** | 스크롤 시 헤더에 배경색과 그림자 적용 | **60px** 이상 |
| **스크롤 탑 버튼** | 우측 하단 버튼 노출, 클릭 시 최상단 이동 | **300px** 이상 |
| **스크롤 애니메이션** | 섹션과 카드가 화면에 들어오면 페이드인 | Intersection Observer **threshold 0.2** |
| **다크 모드** | 토글 시 테마 전환, 새로고침해도 유지 | localStorage 저장 |

### 상태 관리 흐름 (이벤트 → 상태 → 렌더링)

이 프로젝트에는 다음 4가지 "상태 → 렌더링" 흐름이 있습니다.

| # | 이벤트 | 상태 변경 | 화면 변화 |
|---|---|---|---|
| 1 | 다크 모드 버튼 `click` | `theme` = light ↔ dark (localStorage 저장) | `<html data-theme>` 변경 → CSS 변수 전체 교체 |
| 2 | 페이지 로드 / 재시도 `click` | `loading` → `success` \| `error` \| `empty` | Projects 섹션이 스피너 / 카드 목록 / 에러+재시도 / 빈 상태 메시지로 전환 |
| 3 | 폼 `input`, `submit` | 각 필드의 유효성 상태 | 필드 아래 에러 메시지 표시·숨김, 테두리 색 변경 |
| 4 | 필터 버튼 `click` | `currentFilter` = 선택한 언어 | `filter()`로 걸러낸 카드만 다시 렌더링 |

### API 상태 처리

GitHub API 응답에 따라 Projects 섹션이 4가지 상태로 나뉩니다.

| 상태 | 화면 |
|---|---|
| **로딩** | 회전 스피너 + "프로젝트를 불러오는 중..." |
| **성공** | 저장소 카드 그리드 + 언어별 필터 버튼 |
| **에러** | "프로젝트를 불러올 수 없습니다" + 실패 사유 + **[다시 시도]** 버튼 |
| **빈 데이터** | "표시할 프로젝트가 없습니다" |

> **레이트 리밋 대응**: GitHub API는 인증 없이 호출하면 시간당 60회 제한이 있습니다.
> 403 응답을 별도로 감지해 *"GitHub API 요청 한도를 초과했습니다"* 라는 안내를 보여줍니다.

### 폼 유효성 검사

- 이름 / 이메일 / 메시지 **필수값 검증**
- **이메일 형식 검증** (정규식)
- 에러 메시지가 **각 입력 필드 바로 아래** 표시되고, 입력하는 동안 실시간으로 사라짐
- `event.preventDefault()`로 기본 제출 차단 후 전송 처리

**메일 전송 방식**: 기본은 `mailto:`로 방문자의 메일 앱을 열어 `lonu6325@naver.com`으로 보냅니다.
`js/main.js`의 `FORMSPREE_ENDPOINT` 상수에 Formspree 주소를 넣으면 메일 앱을 거치지 않고
서버로 직접 전송되도록 전환됩니다.

---

## 5. 파일 구조

```
portfolio/
├── index.html          # 전체 마크업 (시맨틱 태그 기반)
├── css/
│   └── style.css       # 스타일 · CSS 변수 · 다크모드 · 반응형
├── js/
│   └── main.js         # 인터랙션 · API 연동 · 폼 검증
├── images/
│   └── profile.png     # 프로필 이미지
└── README.md
```

### `js/main.js` 구성

기능별로 7개 블록으로 나눠 작성했습니다.

| 블록 | 역할 |
|---|---|
| 1. 다크 모드 | 테마 적용 · localStorage 저장 · 시스템 설정 감지 |
| 2. 햄버거 메뉴 | 메뉴 토글, 링크 클릭 시 자동 닫힘 |
| 3. 스크롤 이벤트 | 네비게이션 배경 전환, 스크롤 탑 버튼 |
| 4. 스크롤 애니메이션 | Intersection Observer |
| 5. Projects | GitHub API 호출, 상태별 렌더링, 언어 필터 |
| 6. Contact 폼 | 유효성 검사, 메일 전송 |
| 7. 타이핑 효과 | Hero 이름 한 글자씩 출력 |

---

## 6. 반응형 설계

**모바일 퍼스트**로 작성했습니다. 기본 스타일이 모바일이고, 화면이 넓어질 때 `min-width`로 확장합니다.

| 화면 | 브레이크포인트 | 레이아웃 |
|---|---|---|
| 모바일 | 기본 (~767px) | 네비게이션 숨김 + 햄버거 버튼, 1단 배치 |
| 태블릿 | **768px** 이상 | 햄버거 숨김 + 가로 메뉴, About 2단, Skills 3열 |
| 데스크톱 | **1024px** 이상 | 섹션 여백 확대, 본문 크기 조정 |

Projects 카드는 브레이크포인트와 무관하게
`grid-template-columns: repeat(auto-fit, minmax(260px, 1fr))`로 화면 폭에 맞춰 자동 배치됩니다.

---

## 7. 구현하며 배운 것

### Flexbox와 Grid를 나눠 쓴 기준

- **네비게이션 → Flexbox**: 로고와 메뉴를 양 끝으로 밀어내는 **1차원 배치**라서 `justify-content: space-between` 한 줄이면 충분합니다.
- **Projects 카드 → Grid**: 개수가 API 응답에 따라 달라지는 **2차원 배치**입니다. `auto-fit` + `minmax`를 쓰면 미디어 쿼리 없이도 화면 폭에 따라 열 개수가 자동으로 바뀝니다.

정리하면 **한 방향으로 나열하면 Flexbox, 행과 열을 함께 다루면 Grid**를 선택했습니다.

### id 중복으로 생겼던 버그

`<section id="projects">` 안에 `<div id="projects">`를 두는 실수를 했습니다.
`querySelector("#projects")`가 안쪽 div가 아니라 **바깥 section을 잡으면서**,
로딩 상태를 렌더링할 때 `innerHTML = ""`가 섹션 전체를 지워버렸습니다.

id는 문서 전체에서 유일해야 한다는 규칙을 어기면 이렇게 조용히 엉뚱한 요소가 선택된다는 걸
직접 겪었고, 안쪽 div를 `#projectList`로 바꿔 해결했습니다.

### 힌트를 0이 아니라 h로 받은 이유 (폼 검증 설계)

정답 선택지가 1~4번뿐이면 `0`은 "허용 범위 밖의 잘못된 입력"으로 안내해야 하는 값입니다.
검증 규칙과 기능 트리거가 같은 값을 쓰면 둘 중 하나는 반드시 망가집니다.

---

## 8. 실행 화면

> 아래에 스크린샷을 첨부합니다. (데스크톱 / 모바일 / 다크 모드)

| 데스크톱 | 모바일 | 다크 모드 |
|---|---|---|
| _(첨부 예정)_ | _(첨부 예정)_ | _(첨부 예정)_ |
