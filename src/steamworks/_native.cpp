#include <nanobind/nanobind.h>

#include "bindings.h"

NB_MODULE(_native, m) {
    m.doc() = "Steamworks SDK 1.65 native bindings";
    bind_types(m);
    bind_lifecycle(m);
    bind_callbacks(m);
    bind_matchmaking(m);
    bind_user(m);
    bind_friends(m);
    bind_networking_sockets(m);
    bind_networking_utils(m);
}
