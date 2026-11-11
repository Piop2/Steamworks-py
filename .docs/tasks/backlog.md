# Backlog — 해야 할 작업 (순서 제안, 확정 아님)

원칙: 명세 먼저, 코드는 명세가 정리된 뒤. 구현은 [ADR 0001](../adr/0001-binding-approach.md)을 따르고 **동작은 SDK 함수와 최대한 같게** 한다.

1. **API 명세** (`.docs/api/`, 사용자 결정) — 구조에 영향이 큰 순서:
   1. 콜백·CallResult를 파이썬에서 받는 방식 (`STEAM_CALLBACK` 브로드캐스트 / `CCallResult` 호출 결과, 등록·해제, 핸들러 여러 개 허용 여부)
   2. 타입 매핑 (`CSteamID`, 연결·소켓·poll group 핸들, `SteamNetworkingMessage_t` 복사 vs 무복사, 문자열, `EResult`)
   3. 에러 정책 (`bool`/`EResult` 반환 유지 여부, `init` 전 호출·중복 `shutdown`, 콜백 내 파이썬 예외 처리)
   4. 모듈 구조 (`steamworks._native` + 래퍼 여부, 인터페이스 접근자 `SteamMatchmaking()` 대응 방식)
   5. 초기 범위 보완 — MATCHMAKING `network`/`steam` 명세와 함께: 로비 검색(`RequestLobbyList`·필터·`LobbyMatchList_t`), `SetLobbyJoinable`(32/32 입장 차단), `ISteamNetworkingUtils::InitRelayNetworkAccess`
   6. 개발 환경 세부 (`steam_appid.txt` 위치, `.pyi` 재생성 시점·불일치 검사)
2. **빌드 골격** — `pyproject.toml`을 scikit-build-core로 전환, `CMakeLists.txt`(헤더 `steamworks_sdk/public`, lib `sdk/`, DLL을 `.pyd` 옆으로 복사), nanobind abi3 빈 모듈 + import 테스트. ADR "빌드" 줄의 SDK 경로(헤더/lib 분리) 문구 정리.
3. **수명주기** — `init_ex`, `shutdown`, `restart_app_if_necessary`, `run_callbacks`.
4. **콜백 디스패치 기반** — 1-1 명세대로 `STEAM_CALLBACK`/`CCallResult` → 파이썬.
5. **`ISteamUser` / `ISteamFriends`** — 초기 범위 함수.
6. **`ISteamMatchmaking`** — 로비 함수 + 콜백(`LobbyCreated`, `LobbyEnter`, `LobbyChatUpdate`, `LobbyDataUpdate`, `GameLobbyJoinRequested`).
7. **`ISteamNetworkingSockets`** — listen socket·연결·poll group·메시지 + `SteamNetConnectionStatusChangedCallback`.
8. **타입 스텁** — `nanobind.stubgen`으로 `.pyi` 생성·커밋, mypy(strict) 통과.
9. **통합 테스트** — Steam 클라이언트 + AppID 480, pytest marker로 분리(기본 skip). 2인 P2P 연결 확인.
10. **MATCHMAKING 연동** — 서브모듈 푸시 → MATCHMAKING 포인터 커밋, MATCHMAKING venv에 설치 확인.
11. **Linux/macOS** (나중) — rpath `$ORIGIN`, 플랫폼별 `sdk/` DLL·lib.
