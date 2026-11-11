# Q2. 타입 매핑 — 결정됨 (2026-11-11)

원칙: SDK 선언 타입을 그대로 따른다. 이름은 ADR 0001 이름 규칙.

| SDK | 파이썬 | 비고 |
|---|---|---|
| 정수 typedef(`uint32`, `int64`, `uint64` 등) | `int` | |
| `bool` | `bool` | |
| `const char*` 입력/출력 | `str` (UTF-8) | |
| `const void* pData, uint32 cbData` 입력 | `bytes` (버퍼 프로토콜 허용) | 길이는 자동 |
| `SteamAPICall_t` | `int` | `CallResult.set`에 그대로 전달. 무효값 상수 `API_CALL_INVALID` |
| `HSteamNetConnection`, `HSteamListenSocket`, `HSteamNetPollGroup` | `int` | 무효값은 모듈 상수(아래) |
| `CSteamID` | `CSteamID` 클래스 | SDK 헤더에 정의된 public 메서드 전부(기계적 snake_case: `BGameServerAccount` → `b_game_server_account`) + 비교 연산자(`==`/`!=`/`<`/`>`, SDK와 같음)·`__hash__`·`__repr__`. 생성자 4종. 선언만 있고 정의가 없는 `Render`·`SetFromString`·문자열 생성자 등은 제외. **SDK처럼 가변**이라 dict 키로 쓴 뒤 바꾸면 조회가 깨진다. `k_steamIDNil`은 노출하지 않음(`CSteamID()`와 같음) |
| `SteamNetworkingIdentity` | 클래스 | `set_steam_id()`, `get_steam_id()` 등 필요분 |
| `SteamNetworkingConfigValue_t*` 배열 | `Sequence[SteamNetworkingConfigValue]` | 초기 범위에선 빈 목록만 쓰여도 시그니처는 SDK 그대로 |
| `SteamNetConnectionInfo_t` 등 출력 구조체 | 파이썬 값 객체(읽기 전용) | |
| enum (`EResult` 등) | `enum.IntEnum` | `EResult` → `Result.OK`. 구조체 필드가 `uint32`로 선언된 enum 값과 비교 가능해야 해서 IntEnum. **예외: 비트 플래그 enum은 `enum.IntFlag`**(조합값 표현, 결정 2026-11-11). 예: `EChatMemberStateChange` → `ChatMemberStateChange` |
| `#define`/`const` 상수 | 모듈 상수 UPPER_SNAKE | `k_` 접두사의 `k_`/헝가리안 제거: `k_nSteamNetworkingSend_Reliable` → `STEAM_NETWORKING_SEND_RELIABLE`, `k_HSteamNetConnection_Invalid` → `H_STEAM_NET_CONNECTION_INVALID` |

## 출력 인자 (`T* pOut…`)
- **반환값 뒤에 튜플로 붙인다.** 순서는 선언 순서.
- 예: `SendMessageToConnection(...) -> EResult` + `int64* pOutMessageNumber` → `(Result, int)`
- 예: `GetConnectionInfo(conn, pInfo) -> bool` → `(bool, SteamNetConnectionInfo)`. `False`일 때 구조체 값은 SDK처럼 의미 없음.
- 예: `SteamAPI_InitEx(SteamErrMsg*)` → `init_ex() -> (SteamAPIInitResult, str)`

## 콜백 구조체 필드
- `m_` + 헝가리안 접두사 제거 후 snake_case: `m_ulSteamIDLobby` → `steam_id_lobby`, `m_bLocked` → `locked`, `m_EChatRoomEnterResponse` → `chat_room_enter_response`.
- **필드 타입은 선언 그대로**: `uint64` SteamID 필드는 `int`(필요하면 `CSteamID(x)`), `uint32` enum 필드는 `int`.
- 읽기 전용, 콜백 호출 동안만이 아니라 계속 유효(값 복사).

## `SteamNetworkingMessage_t`
- 수신 함수는 `list[SteamNetworkingMessage]` 반환: `receive_messages_on_poll_group(group, max_messages)`. SDK의 `int` 반환(개수)은 리스트 길이로 대체.
- 메시지 객체는 SDK 포인터를 감싼다. 필드: `conn`, `identity_peer`, `message_number`, `flags`, `channel`, `conn_user_data`, `time_received` 등 필요분.
- 본문: `get_data() -> bytes` (**복사**). 무복사(memoryview)는 해제 후 접근 위험이 있어 쓰지 않는다.
- **`release()`를 SDK처럼 명시적으로 호출한다.** 해제 후 접근은 `ValueError`. 호출을 잊은 경우 GC 시 해제(누수 방지용 안전망, 동작 변화 아님).
