// ISteamUser (initial scope: .docs/api/scope.md)
#include <steam/steam_api.h>

#include "bindings.h"
#include "interface.h"

using User = Interface<ISteamUser>;

void bind_user(nb::module_ &m) {
    nb::class_<User>(m, "SteamUser",
                     "SDK `ISteamUser` 인터페이스. `steam_user()`로만 얻는다.\n\n"
                     "`shutdown()` 이후 보관해 둔 객체의 메서드를 호출하면 `RuntimeError`.")
        .def(
            "get_steam_id", [](const User &u) { return u.get()->GetSteamID(); },
            "현재 로그인한 사용자의 SteamID (SDK `ISteamUser::GetSteamID`).");

    m.def(
        "steam_user", [] { return wrap_interface(SteamUser()); },
        "`SteamUser` 인터페이스를 얻는다 (SDK `SteamUser()`). `init_ex()` 전이거나 실패했으면 `None`.");
}
