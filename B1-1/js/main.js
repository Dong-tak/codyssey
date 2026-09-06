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
const FORMSPREE_ENDPOINT = "";
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
   5. Work: 주요 프로젝트 카드 + 상세 모달
   이벤트: 카드 click → 모달 열기 / 닫기 버튼·배경·ESC → 닫기
   상태:   열려 있는 프로젝트 id
   렌더링: projects-data.js 의 데이터로 모달 내용을 채운다
   --------------------------------------------------------- */
const workList = document.querySelector("#workList");
const modal = document.querySelector("#modal");
const modalBody = document.querySelector("#modalBody");

let lastFocused = null; // 모달을 닫은 뒤 원래 있던 버튼으로 초점을 되돌리기 위해

// 카드 목록 렌더링
workList.innerHTML = PROJECTS.map(({ id, emoji, title, period, role, summary, tags }) => `
  <article class="work-card" data-id="${id}" tabindex="0" role="button"
           aria-label="${title} 상세 보기">
    <span class="work-card__emoji" aria-hidden="true">${emoji}</span>
    <h3>${title}</h3>
    <p class="work-card__meta">${period} &middot; ${role}</p>
    <p class="work-card__summary">${summary}</p>
    <ul class="work-card__tags">
      ${tags.map((tag) => `<li>${tag}</li>`).join("")}
    </ul>
    <span class="work-card__more">자세히 보기 →</span>
  </article>
`).join("");

const openModal = (id) => {
  const project = PROJECTS.find((item) => item.id === id);
  if (!project) return;

  const { emoji, title, period, role, team, summary, metrics, links, sections } = project;

  modalBody.innerHTML = `
    <p class="modal__emoji" aria-hidden="true">${emoji}</p>
    <h2 id="modalTitle">${title}</h2>
    <p class="modal__summary">${summary}</p>

    <dl class="modal__info">
      <div><dt>기간</dt><dd>${period}</dd></div>
      <div><dt>역할</dt><dd>${role}</dd></div>
      <div><dt>팀</dt><dd>${team}</dd></div>
    </dl>

    ${metrics ? `
      <ul class="modal__metrics">
        ${metrics.map(({ label, value }) => `
          <li><strong>${value}</strong><span>${label}</span></li>
        `).join("")}
      </ul>` : ""}

    ${sections.map(({ heading, body }) => `
      <section class="modal__section">
        <h3>${heading}</h3>
        ${body.map((paragraph) => `<p>${paragraph}</p>`).join("")}
      </section>
    `).join("")}

    ${links.length > 0 ? `
      <div class="modal__links">
        ${links.map(({ label, url }) => `
          <a href="${url}" target="_blank" rel="noopener" class="btn btn--ghost">${label} ↗</a>
        `).join("")}
      </div>` : ""}
  `;

  lastFocused = document.activeElement;
  modal.hidden = false;
  document.body.classList.add("modal-open"); // 뒤 배경 스크롤 잠금
  document.querySelector("#modalClose").focus();
};

const closeModal = () => {
  modal.hidden = true;
  document.body.classList.remove("modal-open");
  modalBody.scrollTop = 0;
  if (lastFocused) lastFocused.focus();
};

// 카드가 여러 개라 부모에 이벤트를 한 번만 건다 (이벤트 위임)
workList.addEventListener("click", (event) => {
  const card = event.target.closest(".work-card");
  if (card) openModal(card.dataset.id);
});

// 키보드로도 열 수 있게 (Enter / Space)
workList.addEventListener("keydown", (event) => {
  if (event.key !== "Enter" && event.key !== " ") return;
  const card = event.target.closest(".work-card");
  if (!card) return;
  event.preventDefault();
  openModal(card.dataset.id);
});

// 닫기 버튼과 배경 클릭 모두 data-close 속성으로 처리
modal.addEventListener("click", (event) => {
  if (event.target.hasAttribute("data-close")) closeModal();
});

document.addEventListener("keydown", (event) => {
  if (event.key === "Escape" && !modal.hidden) closeModal();
});

/* ---------------------------------------------------------
   6. Projects: GitHub API 연동
   이벤트: 페이지 로드 / 재시도 버튼 click / 필터 버튼 click
   상태:   loading → success | error | empty,  그리고 선택된 언어
   렌더링: 상태에 따라 Projects 섹션 내용을 통째로 교체
   --------------------------------------------------------- */
const projectsEl = document.querySelector("#projectList");
const stateEl = document.querySelector("#projectsState");
const filtersEl = document.querySelector("#filters");

let allRepos = [];          // API 로 받아온 원본 데이터
let currentFilter = "All";  // 현재 선택된 언어 필터

const showState = (html) => {
  stateEl.hidden = false;
  stateEl.innerHTML = html;
  projectsEl.innerHTML = "";
  filtersEl.hidden = true;
};

const renderCards = (repos) => {
  // map: 데이터 배열 → HTML 카드 문자열
  projectsEl.innerHTML = repos
    .map(({ name, description, html_url, language, stargazers_count }) => `
      <article class="project-card">
        <h3><a href="${html_url}" target="_blank" rel="noopener">${name}</a></h3>
        <p class="project-card__desc">${description ?? "설명이 없는 저장소입니다."}</p>
        <div class="project-card__meta">
          ${language ? `<span class="project-card__lang">${language}</span>` : ""}
          <span>⭐ ${stargazers_count}</span>
        </div>
      </article>
    `)
    .join("");

  // 카드에도 등장 애니메이션 적용
  document.querySelectorAll(".project-card").forEach((card) => observer.observe(card));
};

const renderFilters = () => {
  // 중복 없는 언어 목록 만들기 (language 가 null 인 저장소는 제외)
  const languages = ["All", ...new Set(allRepos.map((r) => r.language).filter(Boolean))];

  filtersEl.hidden = false;
  filtersEl.innerHTML = languages
    .map((lang) => `
      <button type="button" class="filter-btn ${lang === currentFilter ? "active" : ""}"
              data-lang="${lang}">${lang}</button>
    `)
    .join("");
};

const applyFilter = () => {
  // filter: 선택된 언어에 해당하는 저장소만 남긴다
  const filtered = currentFilter === "All"
    ? allRepos
    : allRepos.filter((repo) => repo.language === currentFilter);

  if (filtered.length === 0) {
    projectsEl.innerHTML = `<p class="state">해당 언어의 프로젝트가 없습니다.</p>`;
    return;
  }
  renderCards(filtered);
};

// 필터 버튼은 동적으로 만들어지므로, 부모에 한 번만 이벤트를 건다 (이벤트 위임)
filtersEl.addEventListener("click", (event) => {
  const button = event.target.closest(".filter-btn");
  if (!button) return;

  currentFilter = button.dataset.lang;
  renderFilters();
  applyFilter();
});

const loadProjects = async () => {
  // [상태: 로딩]
  showState(`<div class="spinner" aria-hidden="true"></div><p>프로젝트를 불러오는 중...</p>`);

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
    allRepos = repos.filter(
      (repo) => !repo.fork && !EXCLUDED_REPOS.includes(repo.name)
    );

    // [상태: 빈 데이터]
    if (allRepos.length === 0) {
      showState(`<p>표시할 프로젝트가 없습니다.</p>`);
      return;
    }

    // [상태: 성공]
    stateEl.hidden = true;
    renderFilters();
    applyFilter();

  } catch (error) {
    // [상태: 에러] — 재시도 버튼을 함께 보여준다
    showState(`
      <p>프로젝트를 불러올 수 없습니다.</p>
      <p style="font-size:0.85rem">${error.message}</p>
      <button type="button" class="btn btn--ghost" id="retryBtn">다시 시도</button>
    `);
    document.querySelector("#retryBtn").addEventListener("click", loadProjects);
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
