# Q6. 개발 환경 세부 — 결정됨 (2026-11-11)

## `steam_appid.txt`
- SDK는 **프로세스 작업 디렉터리**에서 읽는다(개발 중에만, 배포판은 Steam이 AppID를 준다).
- 내용 `480`. 커밋 금지(gitignore 됨).
- 위치: 이 레포 루트(통합 테스트는 레포 루트에서 `pytest`), MATCHMAKING 루트(게임 실행).
- 통합 테스트는 파일·Steam 클라이언트가 없으면 skip.

## `.pyi` 스텁
- **빌드 때 생성**: CMake `nanobind_add_stub`으로 `src/steamworks/_native.pyi` 생성. 생성 전에 DLL을 `.pyd` 옆에 복사해야 import 가능.
- 커밋한다. 바인딩을 바꾸면 빌드 → 스텁 diff가 같은 커밋에 들어가야 한다.
- 불일치 검사: 별도 테스트 없이 **빌드 후 `git status`에 스텁 변경이 남으면 커밋 누락**. CI 구성 시 `git diff --exit-code src/steamworks/_native.pyi`로 검사.
- mypy(strict)는 이 스텁 기준.
