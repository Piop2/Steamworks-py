// ISteamNetworkingUtils: .docs/api/scope.md (InitRelayNetworkAccess)
#include <steam/steam_api.h>

#include "bindings.h"
#include "interface.h"

using Utils = Interface<ISteamNetworkingUtils>;

void bind_networking_utils(nb::module_ &m) {
    nb::class_<Utils>(m, "SteamNetworkingUtils",
                      "SDK `ISteamNetworkingUtils` 인터페이스. `steam_networking_utils()`로만 얻는다.\n\n"
                      "`shutdown()` 이후 보관해 둔 객체의 메서드를 호출하면 `RuntimeError`.")
        .def(
            "init_relay_network_access", [](const Utils &u) { u.get()->InitRelayNetworkAccess(); },
            "릴레이 네트워크 접근을 미리 준비한다 (SDK `InitRelayNetworkAccess`). 비동기, 반환값 없음.\n\n"
            "P2P 연결 직전이 아니라 시작 시 호출해 두면 첫 연결 지연이 줄어든다.");

    m.def(
        "steam_networking_utils", [] { return wrap_interface(SteamNetworkingUtils()); },
        "`SteamNetworkingUtils` 인터페이스를 얻는다 (SDK `SteamNetworkingUtils()`). "
        "`init_ex()` 전이거나 실패했으면 `None`.");
}
