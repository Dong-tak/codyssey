# 제출 증거 안내

## 저장소

- GitHub: https://github.com/Dong-tak/quiz-game-practice
- 실행 환경: Python 3.10 이상, Apple Git 2.50.1, macOS arm64
- 확인 기록: 터미널 캡처는 Python 3.12.7, 자동 검증 로그는 Python 3.14.3에서 수행

## 기록 파일

- [개발 환경](../logs/00-environment.log)
- [초기 저장소 설정](../logs/01-init.log)
- [실제 퀴즈 플레이와 최고 점수 저장](../logs/04-play-quiz.log)
- [점수·퀴즈 추가·목록 테스트](../logs/05-features.log)
- [입력·영속성·예외 처리 통합 검증](../logs/06-persistence.log)
- [clone/push/pull 실습](../logs/07-clone-pull.log)
- [Git 필수 명령 7종 확인](../logs/09-git-commands.log)

## 제출 화면 증거

### 기능 및 개발 환경

- [개발 환경](screenshots/env-python-git.png)
- [메인 메뉴](screenshots/menu.png)
- [퀴즈 추가와 범위 밖 입력 검증](screenshots/add-quiz.png)
- [추가된 퀴즈 목록](screenshots/list.png)
- [퀴즈 문제와 선택지](screenshots/play-question.png)
- [오답 판정과 퀴즈 결과](screenshots/play.png)
- [최고 점수](screenshots/score.png)
- [Git 브랜치·병합 그래프](screenshots/git-graph.png)
- [clone/push/pull 실습 기록 화면](screenshots/clone-pull.png)

### 트러블슈팅

- [선택지 반복 출력 오류](screenshots/troubleshooting-choice-repeat.png)
- [선택지 반복 출력 원인 코드](screenshots/troubleshooting-display-bug-code.png)
- [선택지 출력 수정 코드](screenshots/troubleshooting-display-fixed-code.png)
- [선택지 정상 출력 결과](screenshots/troubleshooting-choice-fixed-output.png)

## 제출 화면 캡처 결과

이미지를 임의로 생성하지 않고 실제 터미널과 VS Code 화면을 캡처했다.

### 1. 개발 환경

터미널에서 다음 명령을 실행해 Python과 Git 버전, Git 사용자 설정을 확인했다.

```bash
python3 --version
git --version
git config --get user.name
```

[화면 증거](screenshots/env-python-git.png)

### 2. 메뉴·퀴즈 추가·목록

`python3 main.py`를 실행하고 메뉴 화면, 2번 퀴즈 추가 결과,
3번 목록에 추가된 문제가 표시되는 화면을 캡처했다. 정답 번호로 5를
입력했을 때 1~4 범위 오류를 안내하고 다시 입력받는 것도 확인할 수 있다.

- [메인 메뉴](screenshots/menu.png)
- [퀴즈 추가와 입력 검증](screenshots/add-quiz.png)
- [퀴즈 목록](screenshots/list.png)

### 3. 퀴즈 플레이·점수

1번에서 문제를 풀고 오답과 정답 문구, 최종 결과가 표시되는 화면과
4번 최고 점수 화면을 캡처했다.

- [퀴즈 문제와 선택지](screenshots/play-question.png)
- [오답 판정과 최종 결과](screenshots/play.png)
- [최고 점수](screenshots/score.png)

### 4. Git 브랜치·병합·커밋

다음 명령의 결과를 캡처했다.

```bash
git log --oneline --graph --decorate --all
```

그래프에서 `feature/play-quiz`와 `Merge: feature/play-quiz 병합`, 10개 이상의
의미 있는 커밋을 확인할 수 있다.

[화면 증거](screenshots/git-graph.png)

### 5. clone/pull 실습

`logs/07-clone-pull.log`를 VS Code에서 열어 clone, clone 폴더의 commit/push,
기존 폴더의 fast-forward pull 기록을 확인했다. 화면에 모두 들어오지 않는
세부 출력은 전체 로그에서 확인할 수 있다.

- [화면 증거](screenshots/clone-pull.png)
- [clone/pull 전체 로그](../logs/07-clone-pull.log)
