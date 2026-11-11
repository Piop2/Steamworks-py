import enum
import re
from pathlib import Path

import pytest

import steamworks
from steamworks import AccountType, CSteamID, Result, SteamAPIInitResult, Universe

HEADERS = Path(__file__).resolve().parents[1] / "steamworks_sdk" / "public" / "steam"

ENUMS: list[tuple[type[enum.IntEnum], str, str]] = [
    (Result, "EResult", "steamclientpublic.h"),
    (SteamAPIInitResult, "ESteamAPIInitResult", "steam_api.h"),
    (Universe, "EUniverse", "steamuniverse.h"),
    (AccountType, "EAccountType", "steamclientpublic.h"),
]

GABE = 76561197960287930  # account 22202, instance 1, individual, public


def _snake(name: str) -> str:
    name = re.sub(r"([A-Z]+)([A-Z][a-z])", r"\1_\2", name)
    return re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", name).upper()


def _header_values(sdk_enum: str, header: str) -> dict[str, int]:
    text = (HEADERS / header).read_text(encoding="utf-8", errors="replace")
    match = re.search(rf"^enum {sdk_enum}\s*\{{(.*?)^\}};", text, re.DOTALL | re.MULTILINE)
    assert match is not None
    body = re.sub(r"//[^\n]*", "", match.group(1))
    values: dict[str, int] = {}
    next_value = 0
    for name, value in re.findall(
        rf"\b(k_{sdk_enum}\w*)\s*(?:=\s*(-?\d+))?\s*(?:,|$)", body, re.MULTILINE
    ):
        current = int(value) if value else next_value
        values[_snake(name[len(f"k_{sdk_enum}") :].lstrip("_"))] = current
        next_value = current + 1
    return values


@pytest.mark.skipif(not HEADERS.exists(), reason="Steamworks SDK headers not found")
@pytest.mark.parametrize(("py_enum", "sdk_enum", "header"), ENUMS)
def test_enum_matches_sdk_header(py_enum: type[enum.IntEnum], sdk_enum: str, header: str) -> None:
    assert {m.name: m.value for m in py_enum} == _header_values(sdk_enum, header)


def test_enums_are_int_enums() -> None:
    assert issubclass(Result, enum.IntEnum)
    ok: int = Result.OK
    assert ok == 1
    assert Result(31) is Result.IP_NOT_FOUND
    assert SteamAPIInitResult(2) is SteamAPIInitResult.NO_STEAM_CLIENT


def test_steam_id_from_uint64() -> None:
    sid = CSteamID(GABE)
    assert sid.convert_to_uint64() == GABE
    assert sid.get_account_id() == 22202
    assert sid.get_un_account_instance() == 1
    assert sid.get_e_universe() == Universe.PUBLIC
    assert sid.get_e_account_type() == AccountType.INDIVIDUAL
    assert sid.is_valid()
    assert sid.b_individual_account()
    assert not sid.is_lobby()


def test_steam_id_default_is_invalid() -> None:
    sid = CSteamID()
    assert sid.convert_to_uint64() == 0
    assert not sid.is_valid()


def test_steam_id_constructors_agree() -> None:
    three = CSteamID(22202, Universe.PUBLIC, AccountType.INDIVIDUAL)
    four = CSteamID(22202, 1, Universe.PUBLIC, AccountType.INDIVIDUAL)
    assert three == four == CSteamID(GABE)


def test_steam_id_equality_and_hash() -> None:
    a, b = CSteamID(GABE), CSteamID(GABE)
    assert a == b
    assert (a != b) is False
    assert hash(a) == hash(b)
    assert {a: 1}[b] == 1
    assert CSteamID(GABE) != CSteamID(GABE + 1)
    assert CSteamID(GABE) < CSteamID(GABE + 1)
    assert CSteamID(GABE + 1) > CSteamID(GABE)


def test_steam_id_not_equal_to_int() -> None:
    assert CSteamID(GABE) != GABE


def test_steam_id_is_mutable_like_sdk() -> None:
    sid = CSteamID()
    sid.set_from_uint64(GABE)
    assert sid == CSteamID(GABE)
    sid.clear()
    assert not sid.is_valid()


@pytest.mark.parametrize("bad", [-1, 2**64])
def test_steam_id_rejects_out_of_range(bad: int) -> None:
    with pytest.raises(TypeError):
        CSteamID(bad)


def test_steam_id_repr() -> None:
    assert repr(CSteamID(GABE)) == f"CSteamID({GABE})"


def test_invalid_handle_constants() -> None:
    assert steamworks.API_CALL_INVALID == 0
    assert steamworks.H_STEAM_NET_CONNECTION_INVALID == 0
    assert steamworks.H_STEAM_LISTEN_SOCKET_INVALID == 0
    assert steamworks.H_STEAM_NET_POLL_GROUP_INVALID == 0
