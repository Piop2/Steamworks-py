// Lifecycle: SteamAPI_InitEx / Shutdown / RestartAppIfNecessary / RunCallbacks (steam_api.h)
#include <cstring>

#include <nanobind/stl/pair.h>

#include <steam/steam_api.h>

#include "bindings.h"

namespace nb = nanobind;
using namespace nb::literals;

void bind_lifecycle(nb::module_ &m) {
    // GIL is held in all of these: run_callbacks() will dispatch into Python (backlog 4).
    m.def(
        "init_ex",
        []() -> std::pair<ESteamAPIInitResult, nb::str> {
            SteamErrMsg msg = {};
            ESteamAPIInitResult result = SteamAPI_InitEx(&msg);
            // "replace": a malformed message must not raise.
            PyObject *text = PyUnicode_DecodeUTF8(msg, (Py_ssize_t)strnlen(msg, sizeof(msg)), "replace");
            if (!text) throw nb::python_error();
            return {result, nb::steal<nb::str>(text)};
        });
    m.def("shutdown", &SteamAPI_Shutdown);
    m.def("restart_app_if_necessary", &SteamAPI_RestartAppIfNecessary, "app_id"_a);
    m.def("run_callbacks", &SteamAPI_RunCallbacks);
}
