from collections.abc import Iterator
from pathlib import Path

import pytest

import steamworks

APP_ID_FILE = Path(__file__).resolve().parents[1] / "steam_appid.txt"


@pytest.fixture
def init_result() -> Iterator[tuple[steamworks.SteamAPIInitResult, str]]:
    result = steamworks.init_ex()
    yield result
    if result[0] == steamworks.SteamAPIInitResult.OK:
        steamworks.shutdown()


def test_init_ex_shape(init_result: tuple[steamworks.SteamAPIInitResult, str]) -> None:
    # Outcome depends on whether Steam is running here, so check shape only.
    code, message = init_result
    assert isinstance(code, steamworks.SteamAPIInitResult)
    assert isinstance(message, str)
    if code == steamworks.SteamAPIInitResult.OK:
        steamworks.run_callbacks()
    else:
        assert message


def test_calls_before_init_are_safe() -> None:
    steamworks.run_callbacks()
    steamworks.shutdown()


@pytest.mark.integration
def test_lifecycle_with_steam() -> None:
    if not APP_ID_FILE.exists():
        pytest.skip("steam_appid.txt missing")
    assert steamworks.restart_app_if_necessary(480) is False
    code, message = steamworks.init_ex()
    assert code == steamworks.SteamAPIInitResult.OK, message
    assert message == ""
    try:
        for _ in range(5):
            steamworks.run_callbacks()
    finally:
        steamworks.shutdown()
