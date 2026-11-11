# ADR 0001: Steamworks-py 바인딩 방식과 초기 범위

- 상태: proposed (초안, 사용자 승인 대기)
- 날짜: 2026-11-11
- 결정자: 사용자

## 맥락
MATCHMAKING ADR 0002로 네트워킹은 Steam Lobby + Steam Networking(호스트 권한 P2P)으로 간다. 이 레포(MATCHMAKING에서는 서브모듈 `extern/Steamworks-py`)는 패키지 골격만 있고, 바인딩 방식과 빌드 백엔드가 미정이다. Windows 개발 환경에 MSVC Build Tools가 없어 네이티브 빌드가 보류된 상태다(MATCHMAKING `.docs/architecture/environment.md`). 배포는 Nuitka 예정(MATCHMAKING backlog 14).

## 선택지
### A. ctypes + SDK flat API (`steam_api_flat.h`)
- 장점: 표준 라이브러리만 사용, 컴파일러 불필요. 빌드 산출물 없이 `steam_api64.dll`만 동봉. 순수 Python이라 mypy/pytest가 그대로 적용됨.
- 단점: 구조체 레이아웃·플랫폼별 패킹을 직접 맞춰야 함. 콜백은 수동 디스패치로 처리해야 함. 호출 오버헤드가 상대적으로 큼(로비/메시지 빈도에서는 문제 없을 것으로 예상).
### B. cffi (ABI 모드)
- 장점: C 선언을 헤더 형태로 기술.
- 단점: 외부 의존성 추가. ABI 모드의 이점이 ctypes 대비 작음.
### C. pybind11 / Cython (C++ 인터페이스 직접 바인딩)
- 장점: C++ 클래스·콜백을 자연스럽게 감쌈, 호출 성능.
- 단점: MSVC 필요, 플랫폼별 빌드 체인, Nuitka 번들링 복잡도 증가.

## 결정
**A: ctypes + flat API.** 범위는 SDK 전체가 아니라 게임에 필요한 것부터 시작하고, 필요할 때 넓힌다.

### 초기 범위
| 영역 | flat API | 용도 |
|---|---|---|
| 수명주기 | `SteamAPI_InitFlat`(또는 `SteamAPI_Init`), `SteamAPI_Shutdown`, `SteamAPI_RestartAppIfNecessary` | 초기화·종료 |
| 콜백 | `SteamAPI_ManualDispatch_Init` / `_RunFrame` / `_GetNextCallback` / `_FreeLastCallback` / `_GetAPICallResult` | 콜백·CallResult 수신 |
| 사용자 | `ISteamUser` (`GetSteamID`) | 내 SteamID |
| 친구 | `ISteamFriends` (`GetPersonaName`, `GetFriendPersonaName`, `ActivateGameOverlayInviteDialog`) | 이름 표시·초대 |
| 로비 | `ISteamMatchmaking` (Create/Join/Leave, 멤버 조회, 로비 데이터, `GetLobbyOwner`) + 콜백 `LobbyCreated_t`, `LobbyEnter_t`, `LobbyChatUpdate_t`, `LobbyDataUpdate_t`, `GameLobbyJoinRequested_t` | 방 생성·참가·인원 변화·호스트 판정 |
| 메시지 | `ISteamNetworkingMessages` (`SendMessageToUser`, `ReceiveMessagesOnChannel`, `AcceptSessionWithUser`, `CloseSessionWithUser`) + 콜백 `SteamNetworkingMessagesSessionRequest_t`, `SteamNetworkingMessagesSessionFailed_t` | 호스트↔클라이언트 메시지 |

범위 밖(필요 시 추가): 업적/통계, 클라우드, 워크숍, 인벤토리, `ISteamNetworkingSockets`(연결 기반 소켓).

### 구현 원칙
- **이름은 flat API를 따른다**("1:1"). 인터페이스별 모듈(예: `steamworks.matchmaking`)에 flat 함수를 얇게 감싸고, 그 이상의 추상화는 MATCHMAKING의 `steam` 어댑터 레이어에서 한다.
- **DLL 로드 경로는 명시적으로 지정한다**(상대경로·작업 디렉터리 의존 금지, MATCHMAKING backlog 14와 일치).
- **콜백 펌프는 호출자가 돌린다.** 라이브러리는 스레드를 만들지 않는다. 게임은 프레임마다 `run_callbacks()`를 호출한다.
- **구조체 패킹**: 콜백 구조체는 Windows에서 8바이트, Linux/macOS에서 4바이트(`VALVE_CALLBACK_PACK_*`). `ctypes.Structure._pack_`을 플랫폼별로 설정한다. 각 구조체는 SDK 헤더의 `sizeof`와 맞는지 테스트로 검증한다.
- **함수 시그니처는 `argtypes`/`restype`를 전부 선언한다**(64비트 포인터 잘림 방지).
- **테스트**: DLL이 없어도 돌아가는 테스트(구조체 크기·시그니처 선언)와, Steam 클라이언트 + SDK가 필요한 통합 테스트(pytest marker로 분리, 기본은 skip)로 나눈다.
- 개발용 AppID는 480(Spacewar)을 쓴다. `steam_appid.txt`는 커밋하지 않는다.

## 결과 / 영향
- MSVC 없이 진행할 수 있다. MATCHMAKING environment.md의 "네이티브 빌드 (보류)" 절은 이 ADR을 가리킨다.
- 서브모듈 `pyproject.toml`은 순수 Python 패키지로 유지한다(setuptools, 의존성 없음).
- SDK 버전이 올라가면 flat API 접근자 이름(예: `SteamAPI_SteamMatchmaking_v009`)의 버전 접미사가 바뀔 수 있다. SDK 버전을 하나로 고정하고 README에 적는다.
- 콜백 구조체 정의가 SDK 헤더와 어긋나면 메모리 오류가 나므로, 크기 검증 테스트를 필수로 둔다.

## 미결
1. 지원 플랫폼: Windows만으로 시작할지, Linux/macOS도 초기부터 포함할지.
2. 고정할 SDK 버전.
3. 메시지 전송에 `ISteamNetworkingMessages`(비연결형)만 쓸지, 32명 규모에서 `ISteamNetworkingSockets`(연결형)가 필요할지 — `network` Protocol 명세 시 함께 판단.
