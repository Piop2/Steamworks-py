// Lifecycle: SteamAPI_InitEx / Shutdown / RestartAppIfNecessary / RunCallbacks (steam_api.h)
#include <cstring>

#include <nanobind/stl/pair.h>

#include <steam/steam_api.h>

#include "bindings.h"
#include "callback_struct.h"

using namespace nb::literals;

void bind_lifecycle(nb::module_ &m) {
    // GIL is held in all of these: run_callbacks() dispatches into Python.
    m.def(
        "init_ex",
        []() -> std::pair<ESteamAPIInitResult, nb::str> {
            SteamErrMsg msg = {};
            ESteamAPIInitResult result = SteamAPI_InitEx(&msg);
            // "replace": a malformed message must not raise.
            PyObject *text = PyUnicode_DecodeUTF8(msg, (Py_ssize_t)strnlen(msg, sizeof(msg)), "replace");
            if (!text) throw nb::python_error();
            return {result, nb::steal<nb::str>(text)};
        },
        "Steam API를 초기화한다 (SDK `SteamAPI_InitEx`).\n\n"
        "실행 중인 Steam 클라이언트에 연결한다. `(결과, 오류 메시지)`를 반환하며 성공하면\n"
        "`SteamAPIInitResult.OK`와 빈 문자열. 실패해도 예외를 던지지 않는다.");
    m.def("shutdown", &SteamAPI_Shutdown, "Steam API를 종료한다 (SDK `SteamAPI_Shutdown`). 중복 호출해도 안전.");
    m.def("restart_app_if_necessary", &SteamAPI_RestartAppIfNecessary, "app_id"_a,
          "Steam을 거치지 않고 실행됐으면 Steam으로 다시 실행한다 (SDK `SteamAPI_RestartAppIfNecessary`).\n\n"
          "`True`면 Steam이 게임을 다시 띄우므로 게임은 즉시 종료해야 한다. `init_ex()` 전에 호출한다.");
    m.def(
        "run_callbacks",
        [] {
            SteamAPI_RunCallbacks();
            release_deferred();
        },
        "대기 중인 콜백·CallResult 핸들러를 이 스레드에서 실행한다 (SDK `SteamAPI_RunCallbacks`).\n\n"
        "게임 루프에서 매 프레임 호출한다. 핸들러 예외는 `sys.unraisablehook`으로 보고되고 전파되지 않는다.");
}
