import gc
import sys
import time
from collections.abc import Callable
from pathlib import Path

import pytest

import steamworks
from steamworks import (
    Callback,
    CSteamID,
    Result,
    SteamNetConnectionEnd,
    SteamNetConnectionStatusChangedCallback,
    SteamNetworkingConfig,
    SteamNetworkingConfigValue,
    SteamNetworkingConnectionState,
    SteamNetworkingIdentity,
)

APP_ID_FILE = Path(__file__).resolve().parents[1] / "steam_appid.txt"
GABE = 76561197960287930
VIRTUAL_PORT = 7
State = SteamNetworkingConnectionState


def _pump(done: Callable[[], bool], timeout: float = 20.0) -> None:
    deadline = time.monotonic() + timeout
    while not done():
        assert time.monotonic() < deadline, "timed out waiting for Steam"
        steamworks.run_callbacks()
        time.sleep(0.02)


def test_accessors_none_before_init() -> None:
    assert steamworks.steam_networking_sockets() is None
    assert steamworks.steam_networking_utils() is None


@pytest.mark.parametrize(
    "cls",
    [
        steamworks.SteamNetworkingSockets,
        steamworks.SteamNetworkingUtils,
        steamworks.SteamNetworkingMessage,
        steamworks.SteamNetConnectionInfo,
    ],
)
def test_not_constructible(cls: type) -> None:
    with pytest.raises(TypeError):
        cls()


def test_identity_default_is_invalid() -> None:
    identity = SteamNetworkingIdentity()
    assert identity.is_invalid()
    assert identity.get_steam_id64() == 0
    assert not identity.get_steam_id().is_valid()
    assert repr(identity) == "SteamNetworkingIdentity()"


def test_identity_steam_id() -> None:
    a = SteamNetworkingIdentity()
    a.set_steam_id(CSteamID(GABE))
    assert not a.is_invalid()
    assert a.get_steam_id() == CSteamID(GABE)
    assert a.get_steam_id64() == GABE
    assert repr(a) == f"SteamNetworkingIdentity(steam_id64={GABE})"

    b = SteamNetworkingIdentity()
    b.set_steam_id64(GABE)
    assert a == b
    assert (a != b) is False
    b.set_steam_id64(GABE + 1)
    assert a != b
    assert a != GABE

    a.clear()
    assert a.is_invalid()


def test_identity_is_unhashable() -> None:
    with pytest.raises(TypeError):
        hash(SteamNetworkingIdentity())


def test_config_value_setters() -> None:
    value = SteamNetworkingConfigValue()
    value.set_int32(SteamNetworkingConfig.TIMEOUT_INITIAL, 5000)
    value.set_int64(SteamNetworkingConfig.CONNECTION_USER_DATA, 2**40)
    value.set_float(SteamNetworkingConfig.FAKE_PACKET_LOSS_SEND, 0.5)
    with pytest.raises(TypeError):
        value.set_int32(SteamNetworkingConfig.TIMEOUT_INITIAL, "5000")  # type: ignore[arg-type]


def test_enum_aliases() -> None:
    # Alias members share a value; compare as int (mypy sees distinct literals).
    assert int(SteamNetConnectionEnd.APP_GENERIC) == int(SteamNetConnectionEnd.APP_MIN) == 1000


def test_send_flag_constants() -> None:
    assert steamworks.STEAM_NETWORKING_SEND_UNRELIABLE == 0
    assert steamworks.STEAM_NETWORKING_SEND_NO_NAGLE == 1
    assert steamworks.STEAM_NETWORKING_SEND_UNRELIABLE_NO_NAGLE == 1
    assert steamworks.STEAM_NETWORKING_SEND_NO_DELAY == 4
    assert steamworks.STEAM_NETWORKING_SEND_UNRELIABLE_NO_DELAY == 5
    assert steamworks.STEAM_NETWORKING_SEND_RELIABLE == 8
    assert steamworks.STEAM_NETWORKING_SEND_RELIABLE_NO_NAGLE == 9
    assert steamworks.STEAM_NETWORKING_SEND_USE_CURRENT_THREAD == 16
    assert steamworks.STEAM_NETWORKING_SEND_AUTO_RESTART_BROKEN_SESSION == 32
    assert steamworks.STEAM_NETWORK_CONNECTION_INFO_FLAGS_RELAYED == 16


def test_status_changed_callback_registers() -> None:
    cb = Callback(SteamNetConnectionStatusChangedCallback, lambda data: None)
    assert cb.is_registered()
    cb.unregister()


@pytest.mark.integration
def test_networking_with_steam(monkeypatch: pytest.MonkeyPatch) -> None:
    if not APP_ID_FILE.exists():
        pytest.skip("steam_appid.txt missing")
    code, message = steamworks.init_ex()
    assert code == steamworks.SteamAPIInitResult.OK, message

    # Any handler failure (e.g. an enum value the binding cannot convert) must fail the test.
    raised: list[str] = []
    monkeypatch.setattr(sys, "unraisablehook", lambda a: raised.append(repr(a.exc_value)))

    events: list[SteamNetConnectionStatusChangedCallback] = []
    cb = Callback(SteamNetConnectionStatusChangedCallback, events.append)
    listen = steamworks.H_STEAM_LISTEN_SOCKET_INVALID
    group = steamworks.H_STEAM_NET_POLL_GROUP_INVALID
    try:
        user, utils = steamworks.steam_user(), steamworks.steam_networking_utils()
        sockets = steamworks.steam_networking_sockets()
        assert user is not None and utils is not None and sockets is not None
        utils.init_relay_network_access()

        # Invalid handles: SDK failure values, no exceptions.
        bad = steamworks.H_STEAM_NET_CONNECTION_INVALID
        ok, info = sockets.get_connection_info(bad)
        assert not ok and info.state == State.NONE
        assert sockets.receive_messages_on_connection(bad, 8) == []
        assert (
            sockets.receive_messages_on_poll_group(steamworks.H_STEAM_NET_POLL_GROUP_INVALID, 8)
            == []
        )
        result, number = sockets.send_message_to_connection(
            bad, b"x", steamworks.STEAM_NETWORKING_SEND_RELIABLE
        )
        assert result != Result.OK and number == 0
        assert sockets.accept_connection(bad) != Result.OK
        assert not sockets.close_connection(bad, 0, "", False)
        assert not sockets.close_listen_socket(steamworks.H_STEAM_LISTEN_SOCKET_INVALID)
        assert not sockets.destroy_poll_group(steamworks.H_STEAM_NET_POLL_GROUP_INVALID)
        with pytest.raises(ValueError):
            sockets.receive_messages_on_connection(bad, -1)

        timeout = SteamNetworkingConfigValue()
        timeout.set_int32(SteamNetworkingConfig.TIMEOUT_INITIAL, 15000)
        listen = sockets.create_listen_socket_p2p(VIRTUAL_PORT, [timeout])
        assert listen != steamworks.H_STEAM_LISTEN_SOCKET_INVALID
        group = sockets.create_poll_group()
        assert group != steamworks.H_STEAM_NET_POLL_GROUP_INVALID

        # Connect to ourselves: host side (listen_socket set) and client side in one process.
        me = SteamNetworkingIdentity()
        me.set_steam_id(user.get_steam_id())
        client = sockets.connect_p2p(me, VIRTUAL_PORT, [])
        assert client != steamworks.H_STEAM_NET_CONNECTION_INVALID

        def incoming() -> list[SteamNetConnectionStatusChangedCallback]:
            return [e for e in events if e.info.listen_socket == listen and e.conn != client]

        _pump(lambda: any(e.info.state == State.CONNECTING for e in incoming()))
        server = incoming()[0].conn
        assert incoming()[0].info.identity_remote == me
        assert sockets.accept_connection(server) == Result.OK
        assert sockets.set_connection_poll_group(server, group)

        def connected(conn: int) -> bool:
            return any(e.conn == conn and e.info.state == State.CONNECTED for e in events)

        _pump(lambda: connected(client) and connected(server))
        ok, info = sockets.get_connection_info(client)
        assert ok and info.state == State.CONNECTED
        assert info.listen_socket == steamworks.H_STEAM_LISTEN_SOCKET_INVALID
        assert info.identity_remote == me
        assert isinstance(info.connection_description, str)

        reliable = steamworks.STEAM_NETWORKING_SEND_RELIABLE
        for payload in (b"hello", bytearray(b"world"), memoryview(b"!!")):
            result, number = sockets.send_message_to_connection(client, payload, reliable)
            assert result == Result.OK and number > 0
        received: list[steamworks.SteamNetworkingMessage] = []

        def got_three() -> bool:
            received.extend(sockets.receive_messages_on_poll_group(group, 8))
            return len(received) >= 3

        _pump(got_three)
        assert [m.get_data() for m in received] == [b"hello", b"world", b"!!"]
        first = received[0]
        assert first.conn == server
        assert first.identity_peer == me
        assert first.flags & reliable
        assert first.message_number > 0 and first.time_received > 0
        for m in received:
            m.release()
        with pytest.raises(ValueError):
            first.get_data()
        with pytest.raises(ValueError):
            first.release()

        # Server -> client, read on the connection; one message left for GC, one held across shutdown.
        for payload in (b"gc", b"held"):
            assert sockets.send_message_to_connection(server, payload, reliable)[0] == Result.OK
        back: list[steamworks.SteamNetworkingMessage] = []

        def got_two() -> bool:
            back.extend(sockets.receive_messages_on_connection(client, 8))
            return len(back) >= 2

        _pump(got_two)
        assert back[0].get_data() == b"gc"
        held = back.pop()
        back.clear()
        gc.collect()

        assert sockets.close_connection(client, SteamNetConnectionEnd.APP_GENERIC, "bye", False)
        _pump(
            lambda: any(e.conn == server and e.info.state == State.CLOSED_BY_PEER for e in events)
        )
        closed = next(
            e for e in events if e.conn == server and e.info.state == State.CLOSED_BY_PEER
        )
        assert closed.info.end_reason == SteamNetConnectionEnd.APP_GENERIC
        assert closed.info.end_debug == "bye"
        assert sockets.close_connection(server, 0, "", False)
        assert raised == []
    finally:
        cb.unregister()
        s = steamworks.steam_networking_sockets()
        if s is not None:
            s.close_listen_socket(listen)
            s.destroy_poll_group(group)
        steamworks.shutdown()

    with pytest.raises(RuntimeError):
        held.get_data()
    with pytest.raises(RuntimeError):
        held.release()
    del held  # GC after shutdown must not call into the SDK
    gc.collect()
