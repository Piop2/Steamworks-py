import sys
import time
import uuid
from collections.abc import Callable
from pathlib import Path
from typing import Any

import pytest

import steamworks
from steamworks import (
    Callback,
    CallResult,
    ChatRoomEnterResponse,
    CSteamID,
    GameLobbyJoinRequested,
    LobbyChatUpdate,
    LobbyComparison,
    LobbyCreated,
    LobbyDataUpdate,
    LobbyDistanceFilter,
    LobbyEnter,
    LobbyMatchList,
    LobbyType,
    Result,
)

APP_ID_FILE = Path(__file__).resolve().parents[1] / "steam_appid.txt"
# AppID 480 is shared by everyone: tag our lobby with a per-run key so search finds only ours.
SALT_KEY = f"steamworks_py_test_{uuid.uuid4().hex}"


def _pump(done: Callable[[], bool], timeout: float = 10.0) -> None:
    deadline = time.monotonic() + timeout
    while not done():
        assert time.monotonic() < deadline, "timed out waiting for Steam callback"
        steamworks.run_callbacks()
        time.sleep(0.05)


def test_accessor_none_before_init() -> None:
    assert steamworks.steam_matchmaking() is None


def test_interface_not_constructible() -> None:
    with pytest.raises(TypeError):
        steamworks.SteamMatchmaking()


@pytest.mark.parametrize("struct", [LobbyChatUpdate, LobbyDataUpdate, GameLobbyJoinRequested])
def test_new_callback_structs_register(struct: Any) -> None:
    cb = Callback(struct, lambda data: None)
    assert cb.is_registered()
    cb.unregister()


def test_lobby_match_list_call_result() -> None:
    assert not CallResult(LobbyMatchList).is_active()


@pytest.mark.integration
def test_lobby_with_steam(monkeypatch: pytest.MonkeyPatch) -> None:
    if not APP_ID_FILE.exists():
        pytest.skip("steam_appid.txt missing")
    code, message = steamworks.init_ex()
    assert code == steamworks.SteamAPIInitResult.OK, message
    user, mm = steamworks.steam_user(), steamworks.steam_matchmaking()
    assert user is not None and mm is not None
    me = user.get_steam_id()

    entered: list[LobbyEnter] = []
    updates: list[LobbyDataUpdate] = []
    created: list[tuple[LobbyCreated, bool]] = []
    callbacks: list[Callback[Any]] = [
        Callback(LobbyEnter, entered.append),
        Callback(LobbyDataUpdate, updates.append),
    ]
    lobby: CSteamID | None = None
    try:
        cr = CallResult(LobbyCreated)
        cr.set(mm.create_lobby(LobbyType.PUBLIC, 4), lambda d, io: created.append((d, io)))
        _pump(lambda: bool(created and entered))

        data, io_failure = created[0]
        assert not io_failure and data.result == Result.OK
        lobby = CSteamID(data.steam_id_lobby)
        assert entered[0].steam_id_lobby == data.steam_id_lobby
        assert entered[0].chat_room_enter_response == ChatRoomEnterResponse.SUCCESS

        assert mm.get_lobby_owner(lobby) == me
        assert mm.get_num_lobby_members(lobby) == 1
        assert mm.get_lobby_member_by_index(lobby, 0) == me
        assert mm.get_lobby_member_limit(lobby) == 4

        assert mm.set_lobby_data(lobby, SALT_KEY, "1")
        assert mm.get_lobby_data(lobby, SALT_KEY) == "1"
        _pump(lambda: any(u.steam_id_lobby == data.steam_id_lobby for u in updates))

        # Search for our own lobby by the salt key; the backend may need a moment to index it.
        found: list[CSteamID] = []
        matches: list[LobbyMatchList] = []
        for _ in range(5):
            mm.add_request_lobby_list_string_filter(SALT_KEY, "1", LobbyComparison.EQUAL)
            mm.add_request_lobby_list_distance_filter(LobbyDistanceFilter.WORLDWIDE)
            mm.add_request_lobby_list_filter_slots_available(1)
            mm.add_request_lobby_list_result_count_filter(10)
            matches.clear()
            search = CallResult(LobbyMatchList)
            search.set(mm.request_lobby_list(), lambda d, io: matches.append(d))
            _pump(lambda: bool(matches))
            found = [mm.get_lobby_by_index(i) for i in range(matches[0].lobbies_matching)]
            if lobby in found:
                break
            time.sleep(1)
        assert found == [lobby]

        assert mm.set_lobby_joinable(lobby, False)
        assert mm.set_lobby_joinable(lobby, True)

        # Handler exceptions go to sys.unraisablehook and do not escape run_callbacks().
        # Keep only the type: holding the traceback would keep the binding objects alive at exit.
        raised: list[type[BaseException]] = []
        monkeypatch.setattr(sys, "unraisablehook", lambda a: raised.append(type(a.exc_value)))

        def boom(_: LobbyDataUpdate) -> None:
            raise ValueError("handler failure")

        callbacks.append(Callback(LobbyDataUpdate, boom))
        assert mm.delete_lobby_data(lobby, SALT_KEY)
        assert mm.get_lobby_data(lobby, SALT_KEY) == ""
        _pump(lambda: bool(raised))
        assert raised[0] is ValueError
    finally:
        if lobby is not None:
            mm.leave_lobby(lobby)
        for cb in callbacks:
            cb.unregister()
        steamworks.shutdown()
