# (1) 베이스 이미지: 태그를 고정해 재현성 확보 + alpine으로 경량화
FROM nginx:1.27-alpine

# (2) 이미지 메타데이터: 누가/무엇을 위해 만든 이미지인지 이미지 자체에 기록
LABEL org.opencontainers.image.title="my-web"
LABEL org.opencontainers.image.description="nginx 기반 정적 웹 커스텀 이미지 (개발 워크스테이션 과제)"
LABEL org.opencontainers.image.version="1.0"

# (3) 환경변수: 설정을 코드에서 분리 (docker run -e 로 덮어쓰기 가능)
ENV APP_ENV=dev

# (4) 정적 콘텐츠 교체: 베이스 이미지의 기본 페이지를 내 페이지로 덮어씀
COPY index.html /usr/share/nginx/html/index.html

# (5) 문서화 목적의 포트 선언 (실제 매핑은 docker run -p 로 수행)
EXPOSE 80

# (6) 헬스체크: 컨테이너가 "살아있음"이 아니라 "정상 응답함"을 스스로 점검
HEALTHCHECK --interval=10s --timeout=3s --start-period=5s --retries=3 \
  CMD wget -qO- http://localhost/ > /dev/null || exit 1
