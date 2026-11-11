# 현재 작업

> 작업 상태가 바뀔 때마다 갱신한다. "지금 뭐 해야 돼?"의 답은 여기의 **다음 할 일**. 전체 작업 목록은 [backlog.md](backlog.md).

## 진행 중
없음. backlog 1(빌드 골격) 완료, 2(기본 타입·상수) 구현 전 보고 단계.

## 최근 완료 (2026-11-11)
- API 명세 Q1–Q6 결정: [callbacks](../api/callbacks.md) · [types](../api/types.md) · [errors](../api/errors.md) · [module](../api/module.md) · [scope](../api/scope.md) · [dev-env](../api/dev-env.md). 구현 순서 승인.
- **빌드 골격**: scikit-build-core + CMake + nanobind(`STABLE_ABI`, `cp312-abi3`). 빈 `steamworks._native`, `steam_api64.dll`을 `.pyd` 옆으로 복사·설치, `nanobind_add_stub`으로 `_native.pyi` 생성, `py.typed`.
  - 확인: `pip install -e ".[dev]"` 빌드 성공, pytest 2 passed, ruff check/format, mypy(strict) 통과. SDK lib 경로가 틀리면 CMake가 경로를 알려주며 중단.
  - SDK 경로 변수: `STEAMWORKS_SDK_DIR`(헤더), `STEAMWORKS_LIB_DIR`(lib·DLL). 64비트 Windows 외에는 CMake에서 거부.

## 다음 할 일
backlog 2 — **기본 타입·상수**(`Result`·`SteamAPIInitResult` 등 IntEnum, `CSteamID`, 핸들 무효값 상수) 구현 전 보고(접근 방식·수정 파일·엣지 케이스) 작성 → 승인.
- 미확인: MATCHMAKING venv에서 `pip install -e extern/Steamworks-py` 빌드(backlog 9에서 확인).
