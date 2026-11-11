# 현재 작업

> 작업 상태가 바뀔 때마다 갱신한다. "지금 뭐 해야 돼?"의 답은 여기의 **다음 할 일**. 전체 작업 목록은 [backlog.md](backlog.md).

## 진행 중
없음. backlog 6 완료, 7(`SteamNetworkingSockets`/`Utils`) 구현 전 보고 단계.

## 최근 완료 (2026-11-11)
- **backlog 6 `SteamMatchmaking`**: `bind_matchmaking.cpp`
  - `steam_matchmaking()`, 로비 생성·참가·나가기, 멤버·방장 조회, 로비 데이터 get/set/delete, `set_lobby_joinable`, `get_lobby_member_limit`, 검색(`request_lobby_list`, `get_lobby_by_index`, 필터 5종). SDK 1:1, `Interface<T>` 재사용.
  - enum(IntEnum): `LobbyType`, `LobbyComparison`, `LobbyDistanceFilter`, `ChatRoomEnterResponse`(결정: 추가). `ChatMemberStateChange`는 **IntFlag**(결정: 비트 플래그 enum은 IntFlag, [types.md](../api/types.md) 반영). stubgen이 IntFlag 내부 속성을 써서 mypy가 깨지므로 `stubgen_patterns.txt`(`PATTERN_FILE`)로 제거.
  - `test_overlay_invite.py`: 실제 친구 공개 로비를 만들고 그 ID로 초대 창을 연다(초대 실제 전송 가능). 창 유지 시간 `STEAMWORKS_OVERLAY_SECONDS`(기본 6초), 창 닫으면 종료.
  - 구조체 추가: `LobbyChatUpdate`, `LobbyDataUpdate`, `GameLobbyJoinRequested`(필드 `CSteamID`), `LobbyMatchList`.
  - `test_types.py` 헤더 파서 16진수 값 지원.
  - 통합(결정: 실행별 salt 키로 공개 로비 태그 → 검색으로 내 로비만 찾기): 생성·`LobbyEnter` 수신·방장/멤버/한도·데이터·`LobbyDataUpdate` 수신·검색·joinable·핸들러 예외 → `sys.unraisablehook` 확인. **backlog 4 미확인 항목(실제 수신·예외 경로) 해결.**
  - 확인: pytest 45 passed, integration 4 passed, ruff check/format, mypy(strict) 통과.
- **backlog 5 `SteamUser`/`SteamFriends`**: `interface.h`, `bind_user.cpp`, `bind_friends.cpp`
  - 접근자 `steam_user()`/`steam_friends() -> X | None`, `get_steam_id`, `get_persona_name`, `get_friend_persona_name`, `activate_game_overlay_invite_dialog`.
  - `Interface<T>{ptr, generation}` + 전역 세대 카운터(`shutdown()`마다 증가) → shutdown 후 보관 객체 호출 시 `RuntimeError`. 직접 생성 → `TypeError`. 문자열은 UTF-8 `replace`, NULL → `""`.
  - 보고서 엣지 케이스 1–3 기본안대로, 4(`BLoggedOn`) 추가 안 함.
  - 확인: pytest 33 passed, ruff check/format, mypy(strict) 통과. 통합 테스트 2 passed(AppID 480). 수동 확인: 재초기화 후 이전 객체 `RuntimeError`·새 객체 정상, 모르는 ID 이름 `"[unknown]"`, `shutdown()` 중복 후 접근자 `None`. `activate_game_overlay_invite_dialog`: `tests/test_overlay_invite.py`(integration, ctypes Win32+OpenGL 빈 창)로 초대 오버레이 표시 확인 — 무효 로비 ID로도 창은 열림.
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

## 다음 할 일 — backlog 7 `SteamNetworkingSockets` / `SteamNetworkingUtils`
- ADR 0001 연결·메시지 범위 + [scope.md](../api/scope.md) `init_relay_network_access`, [types.md](../api/types.md) `SteamNetworkingIdentity`·`SteamNetworkingMessage`·`SteamNetConnectionInfo`의 접근 방식·수정 파일·엣지 케이스를 보고하고 승인받는다.
- 2클라이언트 시나리오(남의 로비 `join_lobby`, `LobbyChatUpdate`, `GameLobbyJoinRequested`)는 backlog 8.
- 미확인: MATCHMAKING venv에서 `pip install -e extern/Steamworks-py` 빌드(backlog 9).
- 미적용: backlog 2 기본 타입(`Result`, `CSteamID` 등)은 docstring 없음.
