import gc
import subprocess
import sys
import weakref

import pytest

import steamworks
from steamworks import API_CALL_INVALID, Callback, CallResult, LobbyCreated, LobbyEnter


class Handler:
    def __call__(self, *args: object) -> None:
        pass


def test_callback_registers_on_construction() -> None:
    cb = Callback(LobbyEnter, Handler())
    assert cb.is_registered()
    cb.unregister()
    assert not cb.is_registered()


def test_callback_reregister_and_double_unregister() -> None:
    cb = Callback(LobbyEnter, Handler())
    cb.register(Handler())  # SDK: unregister then register with the new handler
    assert cb.is_registered()
    cb.unregister()
    cb.unregister()
    assert not cb.is_registered()
    cb.register(Handler())
    assert cb.is_registered()
    cb.unregister()


def test_unknown_type_rejected() -> None:
    with pytest.raises(TypeError):
        Callback(int, Handler())
    with pytest.raises(TypeError):
        CallResult(steamworks.CSteamID)


def test_library_holds_registered_callback() -> None:
    handler = Handler()
    ref = weakref.ref(handler)
    Callback(LobbyEnter, handler)
    del handler
    gc.collect()
    alive = ref()
    assert alive is not None  # still registered, so kept alive without a user reference
    (cb,) = [o for o in gc.get_referrers(alive) if isinstance(o, Callback)]
    assert cb.is_registered()
    cb.unregister()


def test_unregistered_callback_cycle_is_collected() -> None:
    class Owner:
        def __init__(self) -> None:
            self.cb = Callback(LobbyEnter, self.on_enter)  # Owner -> cb -> bound method -> Owner

        def on_enter(self, data: LobbyEnter) -> None:
            pass

    owner = Owner()
    ref = weakref.ref(owner)
    owner.cb.unregister()
    del owner
    steamworks.run_callbacks()  # drops references released during/after dispatch
    gc.collect()
    assert ref() is None


def test_call_result_inactive_states() -> None:
    cr = CallResult(LobbyCreated)
    assert not cr.is_active()
    cr.set(API_CALL_INVALID, Handler())
    assert not cr.is_active()
    cr.cancel()
    assert not cr.is_active()


def test_call_result_set_and_cancel() -> None:
    cr = CallResult(LobbyCreated)
    cr.set(12345, Handler())  # never completes: no such API call
    assert cr.is_active()
    cr.set(67890, Handler())  # SDK: previous call cancelled
    assert cr.is_active()
    cr.cancel()
    assert not cr.is_active()


def test_generic_subscript() -> None:
    assert Callback[LobbyEnter] is not None
    assert CallResult[LobbyCreated] is not None


def test_struct_fields() -> None:
    for name in ("result", "steam_id_lobby"):
        assert hasattr(LobbyCreated, name)
    for name in ("steam_id_lobby", "chat_permissions", "locked", "chat_room_enter_response"):
        assert hasattr(LobbyEnter, name)


def test_docstrings_present() -> None:
    for obj in (
        Callback,
        CallResult,
        LobbyCreated,
        LobbyEnter,
        steamworks.run_callbacks,
        steamworks.init_ex,
    ):
        assert obj.__doc__


def test_exit_with_live_registrations_is_clean() -> None:
    code = (
        "import steamworks as s\n"
        "s.Callback(s.LobbyEnter, print)\n"
        "s.CallResult(s.LobbyCreated).set(1, lambda d, f: None)\n"
    )
    proc = subprocess.run(
        [sys.executable, "-c", code], check=False, capture_output=True, text=True, timeout=60
    )
    assert proc.returncode == 0, proc.stderr
    assert "leaked" not in proc.stderr
