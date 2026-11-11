// ISteamFriends (initial scope: .docs/api/scope.md)
#include <steam/steam_api.h>

#include "bindings.h"
#include "interface.h"

using namespace nb::literals;
using Friends = Interface<ISteamFriends>;

void bind_friends(nb::module_ &m) {
    nb::class_<Friends>(m, "SteamFriends",
                        "SDK `ISteamFriends` 인터페이스. `steam_friends()`로만 얻는다.\n\n"
                        "`shutdown()` 이후 보관해 둔 객체의 메서드를 호출하면 `RuntimeError`.")
        .def(
            "get_persona_name", [](const Friends &f) { return decode_utf8(f.get()->GetPersonaName()); },
            "현재 사용자의 표시 이름 (SDK `ISteamFriends::GetPersonaName`).")
        .def(
            "get_friend_persona_name",
            [](const Friends &f, CSteamID steam_id_friend) {
                return decode_utf8(f.get()->GetFriendPersonaName(steam_id_friend));
            },
            "steam_id_friend"_a,
            "다른 사용자의 표시 이름 (SDK `ISteamFriends::GetFriendPersonaName`).\n\n"
            "모르는 사용자면 SDK처럼 `\"\"` 또는 `\"[unknown]\"`.")
        .def(
            "activate_game_overlay_invite_dialog",
            [](const Friends &f, CSteamID steam_id_lobby) { f.get()->ActivateGameOverlayInviteDialog(steam_id_lobby); },
            "steam_id_lobby"_a,
            "로비 초대 오버레이를 연다 (SDK `ISteamFriends::ActivateGameOverlayInviteDialog`).");

    m.def(
        "steam_friends", [] { return wrap_interface(SteamFriends()); },
        "`SteamFriends` 인터페이스를 얻는다 (SDK `SteamFriends()`). `init_ex()` 전이거나 실패했으면 `None`.");
}
