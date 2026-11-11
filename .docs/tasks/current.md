# 현재 작업

> 작업 상태가 바뀔 때마다 갱신한다. "지금 뭐 해야 돼?"의 답은 여기의 **다음 할 일**. 전체 작업 목록은 [backlog.md](backlog.md).

## 진행 중
없음. backlog 2(기본 타입·상수) 완료, 3(수명주기) 구현 전 보고 단계.

## 최근 완료 (2026-11-11)
- **backlog 2 기본 타입·상수**: `bind_types.cpp`
  - IntEnum `Result`(130), `SteamAPIInitResult`(4), `Universe`(6, `MAX` 포함), `AccountType`(12). SDK 헤더에서 생성, `tests/test_types.py`가 헤더와 교차 검사.
  - `CSteamID`: 생성자 4종 + 헤더에 정의된 public 메서드 전부(기계적 snake_case) + `==`/`!=`/`<`/`>`·`__hash__`·`__repr__`. 선언만 있고 정의 없는 `Render`·`SetFromString`·`SetFromStringStrict`·문자열 생성자·`BValidExternalSteamID`는 제외(링크 불가).
  - 상수: `API_CALL_INVALID`, `H_STEAM_NET_CONNECTION_INVALID`, `H_STEAM_LISTEN_SOCKET_INVALID`, `H_STEAM_NET_POLL_GROUP_INVALID`.
  - 생성 스텁 `_native.pyi`는 ruff 대상에서 제외. `__eq__`/`__ne__` 스텁은 `nb::sig`로 `object` 인자.
  - 확인: pytest 17 passed, ruff check/format, mypy(strict) 통과.
- **backlog 1 빌드 골격**: scikit-build-core + CMake + nanobind(`cp312-abi3`), DLL `.pyd` 옆 복사, `nanobind_add_stub`. SDK 경로 변수 `STEAMWORKS_SDK_DIR`/`STEAMWORKS_LIB_DIR`.
- API 명세 Q1–Q6 결정: [callbacks](../api/callbacks.md) · [types](../api/types.md) · [errors](../api/errors.md) · [module](../api/module.md) · [scope](../api/scope.md) · [dev-env](../api/dev-env.md).

## 다음 할 일
backlog 3 — **수명주기**(`init_ex`, `shutdown`, `restart_app_if_necessary`, `run_callbacks`, 인터페이스 접근자 `None` 처리) 구현 전 보고 작성 → 승인.
- 미확인: MATCHMAKING venv에서 `pip install -e extern/Steamworks-py` 빌드(backlog 9).
