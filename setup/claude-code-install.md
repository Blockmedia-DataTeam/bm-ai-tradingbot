# Claude Code 설치

> 최종 확인일: 2026-09-23
> 공식 문서: https://code.claude.com/docs/en/setup

설치 명령과 요금제는 바뀝니다. 영상 화면과 다르면 이 문서가 맞습니다. 이 문서와 공식 문서가 다르면 공식 문서가 맞습니다.

## 오늘 터미널에서 할 일은 두 가지

설치 명령 붙여넣기, 로그인. 끝입니다.

## 1. 터미널 열기

- 맥: Spotlight에서 "터미널" 검색
- 윈도우: 시작 메뉴에서 "PowerShell" 검색. WSL 없이 됩니다

## 2. 설치

맥
```
curl -fsSL https://claude.ai/install.sh | bash
```

윈도우 PowerShell
```
irm https://claude.ai/install.ps1 | iex
```

## 3. 실행과 로그인

봇 폴더를 만들고 그 안에서 실행합니다. 폴더 위치와 이름 규칙은 `prerequisites.md` 6절.

```
mkdir ~/tradingbot
cd ~/tradingbot
claude
```

첫 실행 때 브라우저가 열리고 로그인을 요구합니다. Claude 구독 계정으로 로그인하면 끝입니다.

## 4. 요금제

클로드 Pro 이상 구독 계정으로 로그인한다. 요금은 공식 요금 페이지에서 확인.

Claude Code는 봇을 "만들 때" 쓰는 도구입니다. 봇이 24시간 돌면서 AI 판단을 받는 데 쓰는 Anthropic API는 별도이고 8화 전까지 필요 없습니다. `prerequisites.md` 3번 참고.

## 막힐 때

- `claude` 명령을 찾을 수 없다고 나오면 터미널을 닫고 다시 엽니다
- 로그인 창이 안 열리면 터미널에 표시된 주소를 브라우저에 직접 붙여넣습니다
- 그 외는 공식 문서의 Troubleshooting 항목
