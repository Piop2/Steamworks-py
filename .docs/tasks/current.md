# 현재 작업

> 작업 상태가 바뀔 때마다 갱신한다. "지금 뭐 해야 돼?"의 답은 여기의 **다음 할 일**. 전체 작업 목록은 [backlog.md](backlog.md).

## 진행 중
없음. backlog 3(수명주기) 완료, 4(콜백 디스패치) 구현 전 보고 단계.

## 최근 완료 (2026-11-11)
- **backlog 3 수명주기**: `bind_lifecycle.cpp`
  - `init_ex() -> tuple[SteamAPIInitResult, str]`(오류 메시지는 UTF-8 `replace` 디코드), `shutdown`, `restart_app_if_necessary(app_id)`, `run_callbacks`. 모두 SDK 1:1, GIL 유지.
  - 결정: 인터페이스 접근자 `None` 처리·shutdown 후 `RuntimeError`는 backlog 5로 이동. init 전/중복 호출은 바인딩이 막지 않음. `restart_app_if_necessary`는 통합 테스트에서만 호출.
  - pytest marker `integration` 등록, 기본 제외(`-m 'not integration'`).
  - 확인: pytest 19 passed(1 deselected), ruff check/format, mypy(strict) 통과. 통합 테스트는 `steam_appid.txt` 없어 미실행.
- **backlog 2 기본 타입·상수**: `bind_types.cpp` — enum 4종, `CSteamID`, 핸들 무효값 상수.
- **backlog 1 빌드 골격**: scikit-build-core + CMake + nanobind(`cp312-abi3`).
- API 명세 Q1–Q6 결정: [callbacks](../api/callbacks.md) · [types](../api/types.md) · [errors](../api/errors.md) · [module](../api/module.md) · [scope](../api/scope.md) · [dev-env](../api/dev-env.md).

## 다음 할 일 — backlog 4 콜백 디스패치
[callbacks.md](../api/callbacks.md) 기준으로 `Callback`·`CallResult`, 등록 유지, 핸들러 예외 → unraisablehook의 접근 방식·수정 파일·엣지 케이스를 보고하고 승인받는다.
- 미확인: 통합 테스트(`pytest -m integration`, Steam 실행 + 레포 루트 `steam_appid.txt`=480) 수동 실행.
- 미확인: MATCHMAKING venv에서 `pip install -e extern/Steamworks-py` 빌드(backlog 9).
