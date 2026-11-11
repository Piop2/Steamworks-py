// ISteamMatchmaking callback structs (backlog 6 adds the interface functions)
#include "bindings.h"
#include "callback_struct.h"

void bind_matchmaking(nb::module_ &m) {
    bind_callback_struct<LobbyCreated_t>(m, "LobbyCreated",
                                         "로비 생성 결과 (SDK `LobbyCreated_t`, `CreateLobby`의 CallResult).")
        .def_ro("result", &LobbyCreated_t::m_eResult, "`Result.OK`면 성공.")
        .def_ro("steam_id_lobby", &LobbyCreated_t::m_ulSteamIDLobby, "생성된 로비의 SteamID(uint64). 실패하면 0.");

    bind_callback_struct<LobbyEnter_t>(m, "LobbyEnter", "로비 입장 결과 (SDK `LobbyEnter_t`).")
        .def_ro("steam_id_lobby", &LobbyEnter_t::m_ulSteamIDLobby, "입장한 로비의 SteamID(uint64).")
        .def_ro("chat_permissions", &LobbyEnter_t::m_rgfChatPermissions, "현재 사용자의 권한 플래그.")
        .def_ro("locked", &LobbyEnter_t::m_bLocked, "`True`면 초대받은 사용자만 입장 가능.")
        .def_ro("chat_room_enter_response", &LobbyEnter_t::m_EChatRoomEnterResponse,
                "입장 응답 코드(SDK `EChatRoomEnterResponse` 값, uint32).");
}
