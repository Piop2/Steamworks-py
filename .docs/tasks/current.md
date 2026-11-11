# 현재 작업

> 작업 상태가 바뀔 때마다 갱신한다. "지금 뭐 해야 돼?"의 답은 여기의 **다음 할 일**. 전체 작업 목록은 [backlog.md](backlog.md).

## 진행 중
없음. backlog 4(콜백 디스패치) 완료, 5(`SteamUser`/`SteamFriends`) 구현 전 보고 단계.

## 최근 완료 (2026-11-11)
- **backlog 4 콜백 디스패치**: `callback_struct.h`, `bind_callbacks.cpp`, `bind_matchmaking.cpp`
  - `Callback[T]`(`register`/`unregister`/`is_registered`), `CallResult[T]`(`set`/`cancel`/`is_active`). SDK `CCallbackManual`/`CCallResult` 템플릿을 구조체 타입마다 감쌈. 구조체 바인딩 헬퍼 `bind_callback_struct<T>`.
  - 등록·활성 동안 라이브러리가 참조 유지. 해제는 `run_callbacks()` 끝에서 지연 처리(디스패치 중 C++ 객체 소멸 방지). GC 지원(`tp_traverse`/`tp_clear`)으로 핸들러↔객체 순환 수거. 인터프리터 종료 시 `atexit`에서 남은 등록 해제(nanobind 누수 경고 없음).
  - 핸들러 예외 → `PyErr_WriteUnraisable`.
  - 결정 A: `LobbyCreated`·`LobbyEnter` 구조체를 미리 바인딩. 결정 B: 실제 수신·예외 경로는 backlog 6 통합 테스트(로비 생성)에서 검증.
  - IDE 힌트: 공개 API docstring(한국어) + `nb::sig` 제네릭 시그니처, 스텁에 `_T`(`INCLUDE_PRIVATE`). MSVC `/utf-8`. 수명주기 함수에도 docstring 추가.
  - 확인: pytest 30 passed(1 deselected), ruff check/format, mypy(strict) 통과.
- **backlog 3 수명주기**: `bind_lifecycle.cpp`
  - `init_ex() -> tuple[SteamAPIInitResult, str]`(오류 메시지는 UTF-8 `replace` 디코드), `shutdown`, `restart_app_if_necessary(app_id)`, `run_callbacks`. 모두 SDK 1:1, GIL 유지.
  - 결정: 인터페이스 접근자 `None` 처리·shutdown 후 `RuntimeError`는 backlog 5로 이동. init 전/중복 호출은 바인딩이 막지 않음. `restart_app_if_necessary`는 통합 테스트에서만 호출.
  - pytest marker `integration` 등록, 기본 제외(`-m 'not integration'`).
  - 확인: pytest 19 passed(1 deselected), ruff check/format, mypy(strict) 통과. 통합 테스트(AppID 480) 통과.
- **backlog 2 기본 타입·상수**: `bind_types.cpp` — enum 4종, `CSteamID`, 핸들 무효값 상수.
- **backlog 1 빌드 골격**: scikit-build-core + CMake + nanobind(`cp312-abi3`).
- API 명세 Q1–Q6 결정: [callbacks](../api/callbacks.md) · [types](../api/types.md) · [errors](../api/errors.md) · [module](../api/module.md) · [scope](../api/scope.md) · [dev-env](../api/dev-env.md).

## 다음 할 일 — backlog 5 `SteamUser` / `SteamFriends`
[scope.md](../api/scope.md) 초기 범위 함수 + 인터페이스 접근자 `None` 처리·shutdown 후 보관 객체 `RuntimeError`의 접근 방식·수정 파일·엣지 케이스를 보고하고 승인받는다.
- 미확인: 콜백 실제 수신·핸들러 예외 → unraisablehook (backlog 6 통합 테스트).
- 미확인: MATCHMAKING venv에서 `pip install -e extern/Steamworks-py` 빌드(backlog 9).
- 미적용: backlog 2 기본 타입(`Result`, `CSteamID` 등)은 docstring 없음.
