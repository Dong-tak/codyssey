/* =========================================================
   주요 프로젝트 데이터
   카드를 클릭하면 각 프로젝트의 Notion 상세 페이지로 이동한다.
   ========================================================= */

const PROJECTS = [
  {
    emoji: "📝",
    title: "SuitdiO — AI 논리 에디터",
    org: "SuitdiO",
    period: "2024.06 – 2024.12",
    role: "Co-Founder · 기획 & 프론트엔드",
    summary:
      "AI와 시각적 보드를 활용해 생각을 구조화하고, 더 빠르고 정확한 전략 수립과 소통을 돕는 논리 에디터입니다. 외부 렌더링 라이브러리 없이 Canvas 2D API로 보드의 화살표·노드·마인드맵을 직접 구현했습니다.",
    tags: ["React", "TypeScript", "Redux", "Canvas 2D API", "WebSocket"],
    url: "https://rigorous-dinghy-ea8.notion.site/SuitdiO-AI-b553acd8e6c083f5908c0150d9cd8c26",
  },
  {
    emoji: "🔖",
    title: "마일퀘 — 마케터를 위한 스크랩 서비스",
    org: "팬로즈",
    period: "2024.08 – 2024.10",
    role: "Co-Founder · 기획 & 프론트엔드",
    summary:
      "마케터의 반복적인 리서치·레퍼런스 수집 업무를 간편한 스크랩과 자동 아카이빙으로 덜어주는 유틸리티 서비스입니다. 화면 요구사항정의서 작성과 프론트엔드 구현을 담당했습니다.",
    tags: ["React", "TypeScript", "반응형 3단계", "크롬 익스텐션 연동"],
    url: "https://rigorous-dinghy-ea8.notion.site/3933acd8e6c081019ba5d980200f0dee",
  },
  {
    emoji: "⚽",
    title: "축구관 — 해외축구 단체관람 서비스",
    org: "축구관",
    period: "2023.10 – 2024.05",
    role: "대표 · 서비스 총괄",
    summary:
      "일반 술집을 경기 당일 하루 동안 축구펍으로 전환해, 양 팀 팬이 함께 관람하도록 만든 오프라인 서비스입니다. 유료 행사 9회 운영, 누적 모집 450석, 팬 커뮤니티 21,639명 접점을 확보했습니다.",
    tags: ["서비스 기획", "오프라인 운영", "제휴", "MVP 검증"],
    url: "https://rigorous-dinghy-ea8.notion.site/3923acd8e6c08198b59bc03ea25e1a91",
  },
  {
    emoji: "🍼",
    title: "잠시맘 — 아이돌봄 서비스",
    org: "멋쟁이사자처럼 스타트업 스쿨 · Oblet",
    period: "2022",
    role: "Co-Founder · Product Manager",
    summary:
      "멋쟁이사자처럼 스타트업 스쿨에서 진행한 아이돌봄 서비스 프로젝트입니다. 2022년 10월 스타트업 스쿨 Best MVP 로 선정되었습니다.",
    tags: ["제품 기획", "MVP"],
    url: "https://rigorous-dinghy-ea8.notion.site/Dorte-s-c123acd8e6c083d480b2818bdf11f80e",
  },
];
