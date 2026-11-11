// ISteamMatchmaking: ADR 0001 lobby scope + .docs/api/scope.md (search, joinable)
#include <steam/steam_api.h>

#include "bindings.h"
#include "callback_struct.h"
#include "interface.h"

using namespace nb::literals;
using MM = Interface<ISteamMatchmaking>;

static void bind_enums(nb::module_ &m) {
    nb::enum_<ELobbyType>(m, "LobbyType", nb::is_arithmetic(), "로비 공개 범위 (SDK `ELobbyType`).")
        .value("PRIVATE", k_ELobbyTypePrivate)
        .value("FRIENDS_ONLY", k_ELobbyTypeFriendsOnly)
        .value("PUBLIC", k_ELobbyTypePublic)
        .value("INVISIBLE", k_ELobbyTypeInvisible)
        .value("PRIVATE_UNIQUE", k_ELobbyTypePrivateUnique);
    nb::enum_<ELobbyComparison>(m, "LobbyComparison", nb::is_arithmetic(),
                                "로비 검색 필터 비교 방식 (SDK `ELobbyComparison`).")
        .value("EQUAL_TO_OR_LESS_THAN", k_ELobbyComparisonEqualToOrLessThan)
        .value("LESS_THAN", k_ELobbyComparisonLessThan)
        .value("EQUAL", k_ELobbyComparisonEqual)
        .value("GREATER_THAN", k_ELobbyComparisonGreaterThan)
        .value("EQUAL_TO_OR_GREATER_THAN", k_ELobbyComparisonEqualToOrGreaterThan)
        .value("NOT_EQUAL", k_ELobbyComparisonNotEqual);
    nb::enum_<ELobbyDistanceFilter>(m, "LobbyDistanceFilter", nb::is_arithmetic(),
                                    "로비 검색 거리 (SDK `ELobbyDistanceFilter`).")
        .value("CLOSE", k_ELobbyDistanceFilterClose)
        .value("DEFAULT", k_ELobbyDistanceFilterDefault)
        .value("FAR", k_ELobbyDistanceFilterFar)
        .value("WORLDWIDE", k_ELobbyDistanceFilterWorldwide);
    nb::enum_<EChatMemberStateChange>(
        m, "ChatMemberStateChange", nb::is_flag(), nb::is_arithmetic(),
        "로비 멤버 상태 변화 비트 플래그 (SDK `EChatMemberStateChange`, IntFlag).\n\n"
        "`ChatMemberStateChange(update.chat_member_state_change)`로 감싸면 조합값도 표현되고 "
        "`ChatMemberStateChange.LEFT in flags`로 검사할 수 있다.")
        .value("ENTERED", k_EChatMemberStateChangeEntered)
        .value("LEFT", k_EChatMemberStateChangeLeft)
        .value("DISCONNECTED", k_EChatMemberStateChangeDisconnected)
        .value("KICKED", k_EChatMemberStateChangeKicked)
        .value("BANNED", k_EChatMemberStateChangeBanned);
    nb::enum_<EChatRoomEnterResponse>(m, "ChatRoomEnterResponse", nb::is_arithmetic(),
                                      "로비 입장 응답 (SDK `EChatRoomEnterResponse`).")
        .value("SUCCESS", k_EChatRoomEnterResponseSuccess)
        .value("DOESNT_EXIST", k_EChatRoomEnterResponseDoesntExist)
        .value("NOT_ALLOWED", k_EChatRoomEnterResponseNotAllowed)
        .value("FULL", k_EChatRoomEnterResponseFull)
        .value("ERROR", k_EChatRoomEnterResponseError)
        .value("BANNED", k_EChatRoomEnterResponseBanned)
        .value("LIMITED", k_EChatRoomEnterResponseLimited)
        .value("CLAN_DISABLED", k_EChatRoomEnterResponseClanDisabled)
        .value("COMMUNITY_BAN", k_EChatRoomEnterResponseCommunityBan)
        .value("MEMBER_BLOCKED_YOU", k_EChatRoomEnterResponseMemberBlockedYou)
        .value("YOU_BLOCKED_MEMBER", k_EChatRoomEnterResponseYouBlockedMember)
        .value("RATELIMIT_EXCEEDED", k_EChatRoomEnterResponseRatelimitExceeded);
}

static void bind_structs(nb::module_ &m) {
    bind_callback_struct<LobbyCreated_t>(m, "LobbyCreated",
                                         "로비 생성 결과 (SDK `LobbyCreated_t`, `create_lobby`의 CallResult).")
        .def_ro("result", &LobbyCreated_t::m_eResult, "`Result.OK`면 성공.")
        .def_ro("steam_id_lobby", &LobbyCreated_t::m_ulSteamIDLobby, "생성된 로비의 SteamID(uint64). 실패하면 0.");

    bind_callback_struct<LobbyEnter_t>(m, "LobbyEnter", "로비 입장 결과 (SDK `LobbyEnter_t`).")
        .def_ro("steam_id_lobby", &LobbyEnter_t::m_ulSteamIDLobby, "입장한 로비의 SteamID(uint64).")
        .def_ro("chat_permissions", &LobbyEnter_t::m_rgfChatPermissions, "현재 사용자의 권한 플래그.")
        .def_ro("locked", &LobbyEnter_t::m_bLocked, "`True`면 초대받은 사용자만 입장 가능.")
        .def_ro("chat_room_enter_response", &LobbyEnter_t::m_EChatRoomEnterResponse,
                "입장 응답 코드(`ChatRoomEnterResponse` 값, uint32).");

    bind_callback_struct<LobbyChatUpdate_t>(m, "LobbyChatUpdate",
                                            "로비 멤버 입장·퇴장 등 상태 변화 (SDK `LobbyChatUpdate_t`).")
        .def_ro("steam_id_lobby", &LobbyChatUpdate_t::m_ulSteamIDLobby, "로비 SteamID(uint64).")
        .def_ro("steam_id_user_changed", &LobbyChatUpdate_t::m_ulSteamIDUserChanged,
                "상태가 바뀐 사용자 SteamID(uint64).")
        .def_ro("steam_id_making_change", &LobbyChatUpdate_t::m_ulSteamIDMakingChange,
                "변화를 일으킨 사용자 SteamID(uint64). 추방 등에서 `steam_id_user_changed`와 다름.")
        .def_ro("chat_member_state_change", &LobbyChatUpdate_t::m_rgfChatMemberStateChange,
                "`ChatMemberStateChange` 비트 조합(uint32).");

    bind_callback_struct<LobbyDataUpdate_t>(m, "LobbyDataUpdate",
                                            "로비 또는 멤버 데이터 변경 (SDK `LobbyDataUpdate_t`).")
        .def_ro("steam_id_lobby", &LobbyDataUpdate_t::m_ulSteamIDLobby, "로비 SteamID(uint64).")
        .def_ro("steam_id_member", &LobbyDataUpdate_t::m_ulSteamIDMember,
                "데이터가 바뀐 멤버 SteamID(uint64). 로비 자체 데이터면 로비 ID와 같음.")
        .def_ro("success", &LobbyDataUpdate_t::m_bSuccess, "변경 성공이면 1(uint8).");

    bind_callback_struct<GameLobbyJoinRequested_t>(
        m, "GameLobbyJoinRequested",
        "오버레이에서 로비 참가를 수락함 (SDK `GameLobbyJoinRequested_t`). 받으면 `join_lobby` 호출.")
        .def_ro("steam_id_lobby", &GameLobbyJoinRequested_t::m_steamIDLobby, "참가할 로비.")
        .def_ro("steam_id_friend", &GameLobbyJoinRequested_t::m_steamIDFriend,
                "참가 경로가 된 친구. 친구를 거치지 않았으면 무효.");

    bind_callback_struct<LobbyMatchList_t>(m, "LobbyMatchList",
                                           "로비 검색 결과 (SDK `LobbyMatchList_t`, `request_lobby_list`의 CallResult).")
        .def_ro("lobbies_matching", &LobbyMatchList_t::m_nLobbiesMatching,
                "찾은 로비 수(uint32). `get_lobby_by_index(0..n-1)`로 조회.");
}

void bind_matchmaking(nb::module_ &m) {
    bind_enums(m);
    bind_structs(m);

    nb::class_<MM>(m, "SteamMatchmaking",
                   "SDK `ISteamMatchmaking` 인터페이스. `steam_matchmaking()`로만 얻는다.\n\n"
                   "`shutdown()` 이후 보관해 둔 객체의 메서드를 호출하면 `RuntimeError`.")
        .def(
            "create_lobby",
            [](const MM &s, ELobbyType lobby_type, int max_members) {
                return s.get()->CreateLobby(lobby_type, max_members);
            },
            "lobby_type"_a, "max_members"_a,
            "로비를 만들고 입장한다 (SDK `CreateLobby`). 반환한 호출 ID를 `CallResult(LobbyCreated)`에 넘긴다.\n\n"
            "`LobbyEnter` 콜백도 온다. 실패하면 `API_CALL_INVALID`.")
        .def(
            "join_lobby", [](const MM &s, CSteamID steam_id_lobby) { return s.get()->JoinLobby(steam_id_lobby); },
            "steam_id_lobby"_a,
            "로비에 입장한다 (SDK `JoinLobby`). 반환한 호출 ID를 `CallResult(LobbyEnter)`에 넘긴다.")
        .def(
            "leave_lobby", [](const MM &s, CSteamID steam_id_lobby) { s.get()->LeaveLobby(steam_id_lobby); },
            "steam_id_lobby"_a, "로비에서 나간다 (SDK `LeaveLobby`).")
        .def(
            "get_num_lobby_members",
            [](const MM &s, CSteamID steam_id_lobby) { return s.get()->GetNumLobbyMembers(steam_id_lobby); },
            "steam_id_lobby"_a, "로비 멤버 수 (SDK `GetNumLobbyMembers`). 입장한 로비만 알 수 있다.")
        .def(
            "get_lobby_member_by_index",
            [](const MM &s, CSteamID steam_id_lobby, int member) {
                return s.get()->GetLobbyMemberByIndex(steam_id_lobby, member);
            },
            "steam_id_lobby"_a, "member"_a,
            "멤버 SteamID (SDK `GetLobbyMemberByIndex`). `get_num_lobby_members` 직후 0..n-1로 호출.")
        .def(
            "get_lobby_data",
            [](const MM &s, CSteamID steam_id_lobby, const char *key) {
                return decode_utf8(s.get()->GetLobbyData(steam_id_lobby, key));
            },
            "steam_id_lobby"_a, "key"_a, "로비 데이터 값 (SDK `GetLobbyData`). 없으면 빈 문자열.")
        .def(
            "set_lobby_data",
            [](const MM &s, CSteamID steam_id_lobby, const char *key, const char *value) {
                return s.get()->SetLobbyData(steam_id_lobby, key, value);
            },
            "steam_id_lobby"_a, "key"_a, "value"_a,
            "로비 데이터를 설정한다 (SDK `SetLobbyData`). 방장만 가능. 멤버에게 `LobbyDataUpdate`가 간다.")
        .def(
            "delete_lobby_data",
            [](const MM &s, CSteamID steam_id_lobby, const char *key) {
                return s.get()->DeleteLobbyData(steam_id_lobby, key);
            },
            "steam_id_lobby"_a, "key"_a, "로비 데이터를 지운다 (SDK `DeleteLobbyData`). 방장만 가능.")
        .def(
            "get_lobby_owner",
            [](const MM &s, CSteamID steam_id_lobby) { return s.get()->GetLobbyOwner(steam_id_lobby); },
            "steam_id_lobby"_a, "방장 SteamID (SDK `GetLobbyOwner`). 입장한 로비만 알 수 있다.")
        .def(
            "set_lobby_joinable",
            [](const MM &s, CSteamID steam_id_lobby, bool lobby_joinable) {
                return s.get()->SetLobbyJoinable(steam_id_lobby, lobby_joinable);
            },
            "steam_id_lobby"_a, "lobby_joinable"_a,
            "새 입장 허용 여부를 바꾼다 (SDK `SetLobbyJoinable`). 방장만 가능.")
        .def(
            "get_lobby_member_limit",
            [](const MM &s, CSteamID steam_id_lobby) { return s.get()->GetLobbyMemberLimit(steam_id_lobby); },
            "steam_id_lobby"_a, "최대 인원 (SDK `GetLobbyMemberLimit`). 모르면 0.")
        .def(
            "request_lobby_list", [](const MM &s) { return s.get()->RequestLobbyList(); },
            "로비를 검색한다 (SDK `RequestLobbyList`). 반환한 호출 ID를 `CallResult(LobbyMatchList)`에 넘긴다.\n\n"
            "필터는 이 호출 전에 추가하며, 호출마다 초기화된다.")
        .def(
            "get_lobby_by_index", [](const MM &s, int lobby) { return s.get()->GetLobbyByIndex(lobby); }, "lobby"_a,
            "검색 결과의 로비 SteamID (SDK `GetLobbyByIndex`). 범위 밖이면 무효 ID.")
        .def(
            "add_request_lobby_list_string_filter",
            [](const MM &s, const char *key_to_match, const char *value_to_match, ELobbyComparison comparison_type) {
                s.get()->AddRequestLobbyListStringFilter(key_to_match, value_to_match, comparison_type);
            },
            "key_to_match"_a, "value_to_match"_a, "comparison_type"_a,
            "문자열 로비 데이터 필터 (SDK `AddRequestLobbyListStringFilter`).")
        .def(
            "add_request_lobby_list_numerical_filter",
            [](const MM &s, const char *key_to_match, int value_to_match, ELobbyComparison comparison_type) {
                s.get()->AddRequestLobbyListNumericalFilter(key_to_match, value_to_match, comparison_type);
            },
            "key_to_match"_a, "value_to_match"_a, "comparison_type"_a,
            "숫자 로비 데이터 필터 (SDK `AddRequestLobbyListNumericalFilter`).")
        .def(
            "add_request_lobby_list_filter_slots_available",
            [](const MM &s, int slots_available) { s.get()->AddRequestLobbyListFilterSlotsAvailable(slots_available); },
            "slots_available"_a, "빈자리 수 필터 (SDK `AddRequestLobbyListFilterSlotsAvailable`).")
        .def(
            "add_request_lobby_list_distance_filter",
            [](const MM &s, ELobbyDistanceFilter lobby_distance_filter) {
                s.get()->AddRequestLobbyListDistanceFilter(lobby_distance_filter);
            },
            "lobby_distance_filter"_a, "검색 거리 필터 (SDK `AddRequestLobbyListDistanceFilter`).")
        .def(
            "add_request_lobby_list_result_count_filter",
            [](const MM &s, int max_results) { s.get()->AddRequestLobbyListResultCountFilter(max_results); },
            "max_results"_a, "최대 결과 수 (SDK `AddRequestLobbyListResultCountFilter`).");

    m.def(
        "steam_matchmaking", [] { return wrap_interface(SteamMatchmaking()); },
        "`SteamMatchmaking` 인터페이스를 얻는다 (SDK `SteamMatchmaking()`). `init_ex()` 전이거나 실패했으면 `None`.");
}
