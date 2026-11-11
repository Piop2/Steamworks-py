# Backlog — 구현 우선순위 (승인됨 2026-11-11)

원칙: 구현은 [ADR 0001](../adr/0001-binding-approach.md)과 [API 명세](../api/)를 따르고 **동작은 SDK 함수와 최대한 같게** 한다. 각 항목은 구현 전 접근 방식·수정 파일·엣지 케이스를 보고하고 승인받는다.

## 완료
- ~~API 명세~~ (2026-11-11): [callbacks](../api/callbacks.md) · [types](../api/types.md) · [errors](../api/errors.md) · [module](../api/module.md) · [scope](../api/scope.md) · [dev-env](../api/dev-env.md)

## 구현 순서
순서 기준: 아래 단계가 위 단계 위에 쌓이고, Steam 없이 검증 가능한 것부터.

| # | 작업 | 내용 | 검증 |
|---|---|---|---|
| 1 | ~~**빌드 골격**~~ (완료 2026-11-11) | scikit-build-core 전환, `CMakeLists.txt`(헤더 `steamworks_sdk/public`, lib·DLL `sdk/`), nanobind abi3 빈 `_native`, DLL 복사, `nanobind_add_stub`, `py.typed`. ADR "빌드" 줄의 SDK 경로 문구 정리 | `pip install -e .` 후 import 테스트, mypy |
| 2 | ~~**기본 타입·상수**~~ (완료 2026-11-11) | `Result`·`SteamAPIInitResult` 등 enum(IntEnum), `CSteamID`, 핸들 무효값 상수 | 단위 테스트(Steam 불필요) |
| 3 | **수명주기** | `init_ex`, `shutdown`, `restart_app_if_necessary`, `run_callbacks`, 인터페이스 접근자 `None` 처리 | Steam 없음 → `init_ex` 실패 결과 반환 확인 / 통합 |
| 4 | **콜백 디스패치** | `Callback`, `CallResult`, 등록 유지, 핸들러 예외 → unraisablehook | 등록·해제 상태 단위 테스트, 실제 수신은 통합 |
| 5 | **`SteamUser` / `SteamFriends`** | 초기 범위 함수 | 통합 |
| 6 | **`SteamMatchmaking`** | 로비 생성·참가·데이터 + 콜백 5종 + 로비 검색·`SetLobbyJoinable`([scope](../api/scope.md)) | 통합 |
| 7 | **`SteamNetworkingSockets` / `SteamNetworkingUtils`** | listen socket·연결·poll group·메시지(`SteamNetworkingMessage`), `SteamNetworkingIdentity`, 상태 변경 콜백, `init_relay_network_access` | 통합 |
| 8 | **통합 테스트 정리** | AppID 480, pytest marker(기본 skip), 2인 P2P 연결 시나리오 | 수동 2클라이언트 |
| 9 | **MATCHMAKING 연동** | 서브모듈 푸시 → 포인터 커밋, MATCHMAKING venv 설치 확인 | MATCHMAKING에서 import |
| 10 | Linux/macOS (나중) | rpath `$ORIGIN`, 플랫폼별 `sdk/` | — |

스텁(`.pyi`)은 1에서 빌드 단계에 넣으므로 별도 항목 없음(각 단계 커밋에 스텁 diff 포함).
