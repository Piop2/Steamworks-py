# Steamworks-py

Steamworks SDK Python 바인딩. MATCHMAKING의 서브모듈(`extern/Steamworks-py`)로 쓰인다. 개요·환경: [README.md](README.md)

## 결정 기록 (ADR)
- [0001 바인딩 방식과 초기 범위](.docs/adr/0001-binding-approach.md) — nanobind C++ 확장 모듈, 필요한 범위부터 (accepted)

## 규칙
- 설계는 사용자가 한다. 구현 전 접근 방식·수정 파일·엣지 케이스를 보고하고 승인받는다.
- **이 레포 전용 venv(`.venv`)에서 작업.** 시스템 Python 사용 금지.
- Steamworks SDK 바이너리/헤더, `steam_appid.txt` 커밋 금지 (`steamworks_sdk/`에 배치, gitignore).
- 타입 힌트, ruff/mypy(strict) 통과. 테스트를 약화/삭제해서 통과시키지 않는다.

## 커밋/푸시 (필수 준수)
- 커밋 메시지·PR 설명에 `Co-Authored-By` 등 AI 공동 작성자/기여자 표기, "Generated with Claude Code" 문구를 넣지 않는다.
- 커밋 작성자는 사용자(git user) 본인만 되도록 한다.
- 변경은 이 레포에서 커밋·푸시한 뒤, MATCHMAKING에서 서브모듈 포인터를 커밋한다.
