# ADR 0001: Steamworks-py 바인딩 방식과 초기 범위

- 상태: accepted
- 날짜: 2026-11-11
- 결정자: 사용자

## 맥락
MATCHMAKING ADR 0002로 네트워킹은 Steam Lobby + Steam Networking(호스트 권한 P2P)으로 간다. 이 레포(MATCHMAKING에서는 서브모듈 `extern/Steamworks-py`)는 패키지 골격만 있고, 바인딩 방식과 빌드 백엔드가 미정이었다. 배포는 Nuitka 예정(MATCHMAKING backlog 14).

## 선택지
### A. ctypes + SDK flat API (`steam_api_flat.h`)
- 장점: 표준 라이브러리만 사용, 컴파일러 불필요. 순수 Python이라 mypy/pytest가 그대로 적용됨.
- 단점: 구조체 레이아웃·플랫폼별 패킹을 손으로 맞춰야 하며 틀리면 조용한 메모리 오류. 콜백은 수동 디스패치.
### B. cffi (ABI 모드)
- 장점: C 선언을 헤더 형태로 기술.
- 단점: 외부 의존성 추가. ABI 모드는 레이아웃 검증이 없어 A의 위험이 그대로 남음.
### C. C++ 확장 모듈 (pybind11 / nanobind / Cython)
- 장점: 구조체·시그니처를 컴파일러가 보장. SDK의 `CCallResult`/`STEAM_CALLBACK`을 그대로 사용. 호출 성능.
- 단점: MSVC 필요, 플랫폼별 빌드 체인, Nuitka 번들 대상(.pyd) 추가.
- 하위 선택: pybind11(자료 많음, 버전별 재빌드, 외부 stubgen) / **nanobind**(stable ABI, stubgen 내장) / Cython(`.pxd` 재선언, 스텁 수작업).

## 결정
**C: nanobind로 SDK C++ 인터페이스를 직접 바인딩한다.** 범위는 SDK 전체가 아니라 게임에 필요한 것부터 시작하고, 필요할 때 넓힌다.

nanobind를 고른 이유: stable ABI(abi3, Python 3.12+)로 Python 버전이 올라가도 재빌드가 필요 없고, `nanobind.stubgen`으로 mypy용 `.pyi`를 생성할 수 있어 C의 주요 단점(버전별 빌드, 스텁 관리)이 줄어든다.

### 지원 플랫폼
- 목표 범위는 Steamworks SDK가 지원하는 플랫폼과 같다(Windows, Linux, macOS).
- **현재는 Windows(64비트) 기준으로 개발·검증한다.** 다른 플랫폼을 막는 설계(Windows 전용 API를 바인딩 코어에 섞기 등)는 하지 않되, 빌드·테스트는 Windows부터.

### SDK 버전
- **Steamworks SDK 1.65**(2026-07-23)로 고정한다. 버전을 올릴 때는 이 ADR과 README를 함께 갱신한다.

### SDK 배치 (모두 커밋 금지)
| 폴더 | 내용 | 용도 |
|---|---|---|
| `steamworks_sdk/` | SDK 원본 전체(zip의 `sdk/`를 그대로 풀어 둠) | 작업용 참조(헤더 등). gitignore |
| `sdk/` | **빌드할 플랫폼의 DLL·lib만** (현재 win64: `steam_api64.dll`, `steam_api64.lib`) | 빌드·실행용. `steam_api*` 패턴으로 ignore |

### 연결 방식
- **`ISteamNetworkingSockets`(연결형)를 쓴다.** SDK 예제(Spacewar)와 같은 정석 구조: 호스트가 `CreateListenSocketP2P`로 받고, 클라이언트가 `ConnectP2P`로 접속한다. 호스트는 일반 클라이언트이므로 `SteamGameServerNetworkingSockets`가 아니라 `SteamNetworkingSockets()`를 쓴다.
- 역할 분리: **연결 상태(접속·끊김)는 Sockets가 기준**, 로비는 방 찾기·입장·메타데이터만 맡는다.
- `ISteamNetworkingMessages`는 쓰지 않는다(SDK 설명상 UDP 코드 이식용).

### 이름 규칙 (파이썬 쪽)
PEP 8에 맞춰 snake_case로 기계적으로 변환한다. SDK 이름과의 대응은 아래 규칙으로 유지한다.

| 대상 | 규칙 | 예 |
|---|---|---|
| 함수·메서드 | snake_case | `CreateLobby` → `create_lobby`, `ConnectP2P` → `connect_p2p` |
| 구조체·콜백 타입 | `_t` 제거, PascalCase 유지 | `LobbyCreated_t` → `LobbyCreated` |
| enum | `k_E` 접두사·타입명 제거, `Enum` 멤버(UPPER_SNAKE) | `k_ELobbyTypePublic` → `LobbyType.PUBLIC` |
| 인터페이스 클래스 | `I` 제거 | `ISteamMatchmaking` → `SteamMatchmaking` |

### 초기 범위
| 영역 | SDK API | 용도 |
|---|---|---|
| 수명주기 | `SteamAPI_InitEx`, `SteamAPI_Shutdown`, `SteamAPI_RestartAppIfNecessary` | 초기화·종료. `InitEx`는 인터페이스 버전을 검증하고 `ESteamAPIInitResult`+메시지를 준다(SDK 권장, 새 프로젝트용). 파이썬 `init()`은 실패 시 결과 코드·메시지를 담은 예외 |
| 콜백 | `SteamAPI_RunCallbacks`, `CCallResult`, `STEAM_CALLBACK` | 콜백·CallResult 수신 |
| 사용자 | `ISteamUser` (`GetSteamID`) | 내 SteamID |
| 친구 | `ISteamFriends` (`GetPersonaName`, `GetFriendPersonaName`, `ActivateGameOverlayInviteDialog`) | 이름 표시·초대 |
| 로비 | `ISteamMatchmaking` (Create/Join/Leave, 멤버 조회, 로비 데이터, `GetLobbyOwner`) + 콜백 `LobbyCreated_t`, `LobbyEnter_t`, `LobbyChatUpdate_t`, `LobbyDataUpdate_t`, `GameLobbyJoinRequested_t` | 방 생성·참가·인원 변화·호스트 판정 |
| 연결·메시지 | `ISteamNetworkingSockets` (`CreateListenSocketP2P`, `CloseListenSocket`, `ConnectP2P`, `AcceptConnection`, `CloseConnection`, `GetConnectionInfo`, `SendMessageToConnection`, `CreatePollGroup`, `DestroyPollGroup`, `SetConnectionPollGroup`, `ReceiveMessagesOnPollGroup`, `ReceiveMessagesOnConnection`) + `SteamNetworkingMessage_t::Release` + 콜백 `SteamNetConnectionStatusChangedCallback_t` | 호스트(listen socket)↔클라이언트(ConnectP2P) 연결과 메시지 |

범위 밖(필요 시 추가): 업적/통계, 클라우드, 워크숍, 인벤토리, `ISteamNetworkingMessages`(비연결형 메시지).

### 구현 원칙
- **바인딩은 얇게("1:1").** SDK 인터페이스 단위로 노출하고, 그 이상의 추상화는 MATCHMAKING의 `steam` 어댑터 레이어에서 한다.
- **빌드**: scikit-build-core + CMake + nanobind. stable ABI(`cp312-abi3`) 휠로 빌드한다. SDK 경로는 CMake 변수로 받고 기본값은 `steamworks_sdk/`.
- **DLL은 패키지 안에 둔다.** 빌드·설치 시 CMake가 `sdk/`의 DLL(win64: `steam_api64.dll`)을 `.pyd`와 같은 폴더(`steamworks/`)로 복사한다. Python 3.8+는 확장 모듈과 같은 폴더의 의존 DLL을 자동으로 찾으므로 별도 로드 코드는 없다(작업 디렉터리·PATH 의존 금지, MATCHMAKING backlog 14와 일치). Linux 지원 시 rpath `$ORIGIN`으로 같은 규칙을 맞춘다.
- **콜백 펌프는 호출자가 돌린다.** 라이브러리는 스레드를 만들지 않는다. 게임은 프레임마다 `run_callbacks()`(= `SteamAPI_RunCallbacks`)를 호출한다. 파이썬 콜백은 이 호출 안에서 같은 스레드로 실행되며, 파이썬 예외는 C++ 경계를 넘기지 않고 처리한다.
- **콜백 구조체는 파이썬 값으로 변환**해 넘긴다(C++ 포인터를 파이썬에 노출하지 않음).
- **타입 스텁**: `nanobind.stubgen`으로 `.pyi`를 생성해 커밋하고, mypy(strict)는 이 스텁 기준으로 통과해야 한다.
- **테스트**: 빌드된 모듈만 있으면 되는 테스트(import, 스텁·노출 API 확인)와, Steam 클라이언트가 필요한 통합 테스트(pytest marker로 분리, 기본은 skip)로 나눈다.
- 개발용 AppID는 480(Spacewar)을 쓴다. `steam_appid.txt`는 커밋하지 않는다.

## 결과 / 영향
- **MSVC Build Tools(C++ 워크로드) 설치가 전제**다. 빌드에도 SDK 헤더·`.lib`가 필요하므로 SDK 없이는 패키지를 설치할 수 없다(CI 구성 시 SDK 배치 방법 필요).
- `pyproject.toml`의 빌드 백엔드를 setuptools에서 scikit-build-core로 바꾼다. 빌드 의존성: nanobind, scikit-build-core, CMake.
- Nuitka 배포 시 확장 모듈(.pyd)과 `steam_api64.dll`을 함께 번들한다.
- SDK 버전을 하나로 고정하고 README에 적는다. 구조체·시그니처 불일치는 컴파일 단계에서 드러난다.

## 미결
없음.
