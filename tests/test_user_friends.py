from pathlib import Path

import pytest

import steamworks

APP_ID_FILE = Path(__file__).resolve().parents[1] / "steam_appid.txt"


def test_accessors_none_before_init() -> None:
    assert steamworks.steam_user() is None
    assert steamworks.steam_friends() is None


@pytest.mark.parametrize("cls", [steamworks.SteamUser, steamworks.SteamFriends])
def test_interfaces_not_constructible(cls: type) -> None:
    with pytest.raises(TypeError):
        cls()


@pytest.mark.integration
def test_user_friends_with_steam() -> None:
    if not APP_ID_FILE.exists():
        pytest.skip("steam_appid.txt missing")
    code, message = steamworks.init_ex()
    assert code == steamworks.SteamAPIInitResult.OK, message
    try:
        user = steamworks.steam_user()
        friends = steamworks.steam_friends()
        assert user is not None and friends is not None
        me = user.get_steam_id()
        assert me.is_valid() and me.get_e_account_type() == steamworks.AccountType.INDIVIDUAL
        name = friends.get_persona_name()
        assert name
        assert friends.get_friend_persona_name(me) == name
    finally:
        steamworks.shutdown()
    with pytest.raises(RuntimeError):
        user.get_steam_id()
    with pytest.raises(RuntimeError):
        friends.get_persona_name()
    assert steamworks.steam_user() is None
    assert steamworks.steam_friends() is None
