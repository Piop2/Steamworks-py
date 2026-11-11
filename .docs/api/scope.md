# Q5. 초기 범위 보완 — 결정됨 (2026-11-11)

ADR 0001 초기 범위에 아래를 **추가**한다. MATCHMAKING `network`/`steam` 명세에서 더 필요해지면 그때 넓힌다.

| 영역 | 추가 API | 용도 |
|---|---|---|
| 로비 검색 | `RequestLobbyList` + CallResult `LobbyMatchList_t`, `GetLobbyByIndex`, `AddRequestLobbyListStringFilter`, `AddRequestLobbyListNumericalFilter`, `AddRequestLobbyListFilterSlotsAvailable`, `AddRequestLobbyListResultCountFilter`, `AddRequestLobbyListDistanceFilter` | 빈자리 있는 방 찾기 |
| 입장 차단 | `SetLobbyJoinable`, `GetLobbyMemberLimit` | 32/32 최종 흐름 중 새 입장 막기 |
| 릴레이 | `ISteamNetworkingUtils`(`SteamNetworkingUtils`): `InitRelayNetworkAccess` | P2P 연결 지연 줄이기(SDK 권장, `CreateListenSocketP2P` 주석) |
| 보조 타입 | `CSteamID`, `SteamNetworkingIdentity`, `SteamNetConnectionInfo_t`, `SteamNetworkingConfigValue_t` | [types.md](types.md) |

이 표를 ADR 0001 초기 범위 표의 보완으로 본다(ADR 본문은 그대로, 여기서 참조).
