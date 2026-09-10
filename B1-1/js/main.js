/* =========================================================
   포트폴리오 인터랙션
   전체 구조: "사용자 이벤트 → 상태 변경 → 화면(DOM) 업데이트"
   ========================================================= */

const GITHUB_USER = "Dong-tak";
const CONTACT_EMAIL = "lonu6325@naver.com";

// Projects 섹션에 보여주지 않을 저장소
// - Dong-tak: GitHub 프로필 소개용 저장소라 작업물이 아님
// - portfolio: 이 사이트를 옮기기 전에 쓰던 저장소
const EXCLUDED_REPOS = ["Dong-tak", "portfolio"];

// Formspree 엔드포인트를 넣으면 메일 앱을 열지 않고 서버로 직접 전송한다.
// (formspree.io 에서 폼을 만들면 "https://formspree.io/f/xxxxxxxx" 형태의 주소를 준다)
const FORMSPREE_ENDPOINT = "https://formspree.io/f/mzebybqj";
const SCROLL_TOP_THRESHOLD = 300; // 스크롤 탑 버튼이 나타나는 지점(px)
const NAV_SCROLL_THRESHOLD = 60;  // 네비게이션 배경이 바뀌는 지점(px)
const OBSERVER_THRESHOLD = 0.2;   // 스크롤 애니메이션 임계값

/* ---------------------------------------------------------
   1. 다크 모드
   이벤트: 토글 버튼 click
   상태:   theme ("light" | "dark") + localStorage
   렌더링: <html data-theme> 속성 → CSS 변수 전체 교체
   --------------------------------------------------------- */
const themeToggle = document.querySelector("#themeToggle");

const applyTheme = (theme) => {
  document.documentElement.dataset.theme = theme;
  themeToggle.textContent = theme === "dark" ? "☀️" : "🌙";
  localStorage.setItem("theme", theme);
};

// 시작 시점의 테마 결정: 저장된 값 > 시스템 설정 > light
const savedTheme = localStorage.getItem("theme");
const prefersDark = window.matchMedia("(prefers-color-scheme: dark)").matches;
applyTheme(savedTheme ?? (prefersDark ? "dark" : "light"));

themeToggle.addEventListener("click", () => {
  const next = document.documentElement.dataset.theme === "dark" ? "light" : "dark";
  applyTheme(next);
});

/* ---------------------------------------------------------
   2. 햄버거 메뉴
   이벤트: 버튼 click / 메뉴 링크 click
   상태:   열림 여부 (.active 클래스)
   --------------------------------------------------------- */
const hamburger = document.querySelector("#hamburger");
const navMenu = document.querySelector("#navMenu");

const closeMenu = () => {
  navMenu.classList.remove("active");
  hamburger.classList.remove("active");
  hamburger.setAttribute("aria-expanded", "false");
};

hamburger.addEventListener("click", () => {
  const isOpen = navMenu.classList.toggle("active");
  hamburger.classList.toggle("active", isOpen);
  hamburger.setAttribute("aria-expanded", String(isOpen));
});

// 메뉴 항목을 누르면 이동과 동시에 메뉴를 닫는다 (부드러운 스크롤은 CSS scroll-behavior 담당)
document.querySelectorAll(".nav__link").forEach((link) => {
  link.addEventListener("click", closeMenu);
});

/* ---------------------------------------------------------
   3. 스크롤 이벤트: 네비게이션 배경 + 스크롤 탑 버튼
   --------------------------------------------------------- */
const header = document.querySelector("#header");
const toTop = document.querySelector("#toTop");

window.addEventListener("scroll", () => {
  const y = window.scrollY;
  header.classList.toggle("scrolled", y > NAV_SCROLL_THRESHOLD);
  toTop.classList.toggle("show", y > SCROLL_TOP_THRESHOLD);
});

toTop.addEventListener("click", () => {
  window.scrollTo({ top: 0, behavior: "smooth" });
});

/* ---------------------------------------------------------
   4. 스크롤 애니메이션 (Intersection Observer)
   화면에 20% 이상 들어오면 .visible 을 붙여 나타나게 한다.
   --------------------------------------------------------- */
const observer = new IntersectionObserver(
  (entries) => {
    entries.forEach((entry) => {
      if (entry.isIntersecting) {
        entry.target.classList.add("visible");
        observer.unobserve(entry.target); // 한 번 나타나면 더 볼 필요 없다
      }
    });
  },
  { threshold: OBSERVER_THRESHOLD }
);

document.querySelectorAll(".section").forEach((el) => observer.observe(el));

/* ---------------------------------------------------------
   5. Work: 주요 프로젝트 카드
   각 카드는 해당 프로젝트의 Notion 상세 페이지로 연결된다.
   데이터는 projects-data.js 에 분리해 두고 map() 으로 카드를 만든다.
   --------------------------------------------------------- */
const workList = document.querySelector("#workList");

workList.innerHTML = PROJECTS.map(({ emoji, title, org, period, role, summary, tags, url }) => `
  <a class="work-card" href="${url}" target="_blank" rel="noopener">
    <div class="work-card__head">
      <span class="work-card__emoji" aria-hidden="true">${emoji}</span>
      <span class="work-card__period">${period}</span>
    </div>
    <h3>${title}</h3>
    <p class="work-card__meta">${org} &middot; ${role}</p>
    <p class="work-card__summary">${summary}</p>
    <ul class="work-card__tags">
      ${tags.map((tag) => `<li>${tag}</li>`).join("")}
    </ul>
    <span class="work-card__more">Notion에서 자세히 보기 ↗</span>
  </a>
`).join("");

/* ---------------------------------------------------------
   6. Projects: GitHub API 연동
   이벤트: 페이지 로드 / 재시도 버튼 click / 필터 버튼 click
   상태:   state 객체 하나 { status, repos, filter, error }
   렌더링: setState() 가 항상 render() 를 호출하고,
           render() 는 state.status 만 보고 화면을 결정한다
   --------------------------------------------------------- */
const projectsEl = document.querySelector("#projectList");
const stateEl = document.querySelector("#projectsState");
const filtersEl = document.querySelector("#filters");

// 이 섹션이 기억해야 할 것을 객체 하나에 모았다.
// 변수 여러 개로 흩어 두면 "지금 화면이 어떤 상태인지"를 한눈에 볼 수 없고,
// 상태를 바꿔 놓고 화면 갱신을 빠뜨리는 실수가 생긴다.
const state = {
  status: "loading", // "loading" | "success" | "empty" | "error"
  repos: [],         // API 로 받아온 원본 데이터 (필터 적용 전)
  filter: "All",     // 현재 선택된 언어
  error: "",         // status 가 "error" 일 때 보여줄 메시지
};

// 상태를 바꾸는 유일한 통로.
// 여기서만 화면을 다시 그리므로 "상태가 바뀌면 화면도 반드시 바뀐다"가 보장된다.
const setState = (patch) => {
  Object.assign(state, patch);
  render();
};

const showState = (html) => {
  stateEl.hidden = false;
  stateEl.innerHTML = html;
  projectsEl.innerHTML = "";
  filtersEl.hidden = true;
};

const renderCards = (repos) => {
  // map: 데이터 배열 → HTML 카드 문자열
  // 카드 전체를 <a> 로 만들어, 어디를 눌러도 해당 GitHub 저장소로 이동하게 한다
  projectsEl.innerHTML = repos
    .map(({ name, description, html_url, language, stargazers_count }) => `
      <a class="project-card" href="${html_url}" target="_blank" rel="noopener">
        <h3>${name}</h3>
        <p class="project-card__desc">${description ?? "설명이 없는 저장소입니다."}</p>
        <div class="project-card__meta">
          ${language ? `<span class="project-card__lang">${language}</span>` : ""}
          <span>⭐ ${stargazers_count}</span>
        </div>
        <span class="project-card__more">GitHub에서 보기 ↗</span>
      </a>
    `)
    .join("");

  // 카드에도 등장 애니메이션 적용
  document.querySelectorAll(".project-card").forEach((card) => observer.observe(card));
};

const renderFilters = () => {
  // 중복 없는 언어 목록 만들기 (language 가 null 인 저장소는 제외)
  const languages = ["All", ...new Set(state.repos.map((r) => r.language).filter(Boolean))];

  filtersEl.hidden = false;
  filtersEl.innerHTML = languages
    .map((lang) => `
      <button type="button" class="filter-btn ${lang === state.filter ? "active" : ""}"
              data-lang="${lang}">${lang}</button>
    `)
    .join("");
};

// 상태 하나만 보고 화면 전체를 결정한다.
// 이 함수 밖에서는 Projects 섹션의 DOM 을 건드리지 않는다.
const render = () => {
  if (state.status === "loading") {
    showState(`<div class="spinner" aria-hidden="true"></div><p>프로젝트를 불러오는 중...</p>`);
    return;
  }

  if (state.status === "error") {
    showState(`
      <p>프로젝트를 불러올 수 없습니다.</p>
      <p class="state__detail">${state.error}</p>
      <button type="button" class="btn btn--ghost" id="retryBtn">다시 시도</button>
    `);
    return;
  }

  if (state.status === "empty") {
    showState(`<p>표시할 프로젝트가 없습니다.</p>`);
    return;
  }

  // status === "success"
  stateEl.hidden = true;
  renderFilters();

  // filter: 선택된 언어에 해당하는 저장소만 남긴다
  const visible = state.filter === "All"
    ? state.repos
    : state.repos.filter((repo) => repo.language === state.filter);

  if (visible.length === 0) {
    projectsEl.innerHTML = `<p class="state">해당 언어의 프로젝트가 없습니다.</p>`;
    return;
  }
  renderCards(visible);
};

// 필터 버튼과 재시도 버튼은 매번 새로 그려지므로,
// 부모에 한 번만 이벤트를 걸어 둔다 (이벤트 위임)
filtersEl.addEventListener("click", (event) => {
  const button = event.target.closest(".filter-btn");
  if (!button) return;
  setState({ filter: button.dataset.lang });
});

stateEl.addEventListener("click", (event) => {
  if (event.target.id === "retryBtn") loadProjects();
});

const loadProjects = async () => {
  setState({ status: "loading" });

  try {
    const response = await fetch(`https://api.github.com/users/${GITHUB_USER}/repos?sort=updated&per_page=100`);

    // fetch 는 404/403 에도 예외를 던지지 않으므로 직접 확인해야 한다
    if (!response.ok) {
      const reason = response.status === 403
        ? "GitHub API 요청 한도를 초과했습니다. 잠시 후 다시 시도해주세요."
        : `요청에 실패했습니다. (HTTP ${response.status})`;
      throw new Error(reason);
    }

    const repos = await response.json();

    // 포크한 저장소와 목록에서 감출 저장소를 걸러낸다
    const visibleRepos = repos.filter(
      (repo) => !repo.fork && !EXCLUDED_REPOS.includes(repo.name)
    );

    setState({
      status: visibleRepos.length === 0 ? "empty" : "success",
      repos: visibleRepos,
    });

  } catch (error) {
    setState({ status: "error", error: error.message });
  }
};

loadProjects();

/* ---------------------------------------------------------
   7. Contact 폼 유효성 검사
   이벤트: submit / input
   상태:   각 필드의 유효 여부
   렌더링: 에러 메시지 표시·숨김, 성공 메시지
   --------------------------------------------------------- */
const form = document.querySelector("#contactForm");
const successMsg = document.querySelector("#formSuccess");

const EMAIL_PATTERN = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

// 필드 하나를 검사해서, 문제가 있으면 메시지를 돌려준다 (없으면 빈 문자열)
const validateField = (field) => {
  const value = field.value.trim();

  if (value === "") {
    // 한국어 조사가 어색해지지 않도록 문장을 통째로 정해둔다
    const messages = {
      name: "이름을 입력해주세요.",
      email: "이메일을 입력해주세요.",
      message: "메시지를 입력해주세요.",
    };
    return messages[field.id];
  }
  if (field.id === "email" && !EMAIL_PATTERN.test(value)) {
    return "올바른 이메일 형식이 아닙니다.";
  }
  return "";
};

const showFieldError = (field, message) => {
  document.querySelector(`#${field.id}Error`).textContent = message;
  field.classList.toggle("invalid", message !== "");
};

const fields = [...form.querySelectorAll("input, textarea")];

// 입력하는 동안 실시간으로 에러를 지워준다
fields.forEach((field) => {
  field.addEventListener("input", () => showFieldError(field, validateField(field)));
});

// 메일 앱을 열어 전송하는 방식 (별도 서비스 가입 없이 동작)
const sendByMailto = ({ name, email, message }) => {
  const subject = encodeURIComponent(`[포트폴리오 문의] ${name}님`);
  const body = encodeURIComponent(`보낸 사람: ${name} (${email})\n\n${message}`);
  window.location.href = `mailto:${CONTACT_EMAIL}?subject=${subject}&body=${body}`;
};

// Formspree 로 서버 전송하는 방식 (엔드포인트가 설정되어 있을 때만 사용)
const sendByFormspree = async (data) => {
  const response = await fetch(FORMSPREE_ENDPOINT, {
    method: "POST",
    headers: { "Content-Type": "application/json", Accept: "application/json" },
    body: JSON.stringify(data),
  });
  if (!response.ok) throw new Error(`전송 실패 (HTTP ${response.status})`);
};

const submitButton = form.querySelector("button[type='submit']");

form.addEventListener("submit", async (event) => {
  event.preventDefault(); // 기본 제출(새로고침) 막기

  // 모든 필드를 검사하고, 하나라도 문제가 있으면 제출하지 않는다
  const errors = fields.map((field) => {
    const message = validateField(field);
    showFieldError(field, message);
    return message;
  });

  if (errors.some((message) => message !== "")) {
    successMsg.hidden = true;
    return;
  }

  const data = {
    name: document.querySelector("#name").value.trim(),
    email: document.querySelector("#email").value.trim(),
    message: document.querySelector("#message").value.trim(),
  };

  // 엔드포인트가 설정되어 있으면 서버 전송, 아니면 메일 앱으로 넘긴다
  if (FORMSPREE_ENDPOINT === "") {
    sendByMailto(data);
    successMsg.textContent = "✅ 메일 앱이 열렸습니다. 보내기를 눌러 전송을 완료해주세요.";
    successMsg.hidden = false;
    form.reset();
    return;
  }

  submitButton.disabled = true;
  submitButton.textContent = "전송 중...";

  try {
    await sendByFormspree(data);
    successMsg.textContent = "✅ 메시지가 전송되었습니다. 감사합니다!";
    successMsg.hidden = false;
    form.reset();
  } catch (error) {
    // 서버 전송이 실패하면 메일 앱으로라도 보낼 수 있게 안내한다
    successMsg.textContent = `⚠️ ${error.message} — ${CONTACT_EMAIL} 로 직접 보내주세요.`;
    successMsg.hidden = false;
  } finally {
    submitButton.disabled = false;
    submitButton.textContent = "보내기";
  }
});

/* ---------------------------------------------------------
   8. Hero 타이핑 효과 (보너스)
   --------------------------------------------------------- */
const typingEl = document.querySelector("#typing");
const TYPING_TEXT = "김동탁";
let charIndex = 0;

const type = () => {
  if (charIndex <= TYPING_TEXT.length) {
    typingEl.textContent = TYPING_TEXT.slice(0, charIndex);
    charIndex += 1;
    setTimeout(type, 140);
  }
};

type();
