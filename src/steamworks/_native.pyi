"""Steamworks SDK 1.65 native bindings"""

from collections.abc import Callable
import enum
from typing import Generic, TypeVar, overload


class Result(enum.IntEnum):
    NONE = 0

    OK = 1

    FAIL = 2

    NO_CONNECTION = 3

    INVALID_PASSWORD = 5

    LOGGED_IN_ELSEWHERE = 6

    INVALID_PROTOCOL_VER = 7

    INVALID_PARAM = 8

    FILE_NOT_FOUND = 9

    BUSY = 10

    INVALID_STATE = 11

    INVALID_NAME = 12

    INVALID_EMAIL = 13

    DUPLICATE_NAME = 14

    ACCESS_DENIED = 15

    TIMEOUT = 16

    BANNED = 17

    ACCOUNT_NOT_FOUND = 18

    INVALID_STEAM_ID = 19

    SERVICE_UNAVAILABLE = 20

    NOT_LOGGED_ON = 21

    PENDING = 22

    ENCRYPTION_FAILURE = 23

    INSUFFICIENT_PRIVILEGE = 24

    LIMIT_EXCEEDED = 25

    REVOKED = 26

    EXPIRED = 27

    ALREADY_REDEEMED = 28

    DUPLICATE_REQUEST = 29

    ALREADY_OWNED = 30

    IP_NOT_FOUND = 31

    PERSIST_FAILED = 32

    LOCKING_FAILED = 33

    LOGON_SESSION_REPLACED = 34

    CONNECT_FAILED = 35

    HANDSHAKE_FAILED = 36

    IO_FAILURE = 37

    REMOTE_DISCONNECT = 38

    SHOPPING_CART_NOT_FOUND = 39

    BLOCKED = 40

    IGNORED = 41

    NO_MATCH = 42

    ACCOUNT_DISABLED = 43

    SERVICE_READ_ONLY = 44

    ACCOUNT_NOT_FEATURED = 45

    ADMINISTRATOR_OK = 46

    CONTENT_VERSION = 47

    TRY_ANOTHER_CM = 48

    PASSWORD_REQUIRED_TO_KICK_SESSION = 49

    ALREADY_LOGGED_IN_ELSEWHERE = 50

    SUSPENDED = 51

    CANCELLED = 52

    DATA_CORRUPTION = 53

    DISK_FULL = 54

    REMOTE_CALL_FAILED = 55

    PASSWORD_UNSET = 56

    EXTERNAL_ACCOUNT_UNLINKED = 57

    PSN_TICKET_INVALID = 58

    EXTERNAL_ACCOUNT_ALREADY_LINKED = 59

    REMOTE_FILE_CONFLICT = 60

    ILLEGAL_PASSWORD = 61

    SAME_AS_PREVIOUS_VALUE = 62

    ACCOUNT_LOGON_DENIED = 63

    CANNOT_USE_OLD_PASSWORD = 64

    INVALID_LOGIN_AUTH_CODE = 65

    ACCOUNT_LOGON_DENIED_NO_MAIL = 66

    HARDWARE_NOT_CAPABLE_OF_IPT = 67

    IPT_INIT_ERROR = 68

    PARENTAL_CONTROL_RESTRICTED = 69

    FACEBOOK_QUERY_ERROR = 70

    EXPIRED_LOGIN_AUTH_CODE = 71

    IP_LOGIN_RESTRICTION_FAILED = 72

    ACCOUNT_LOCKED_DOWN = 73

    ACCOUNT_LOGON_DENIED_VERIFIED_EMAIL_REQUIRED = 74

    NO_MATCHING_URL = 75

    BAD_RESPONSE = 76

    REQUIRE_PASSWORD_RE_ENTRY = 77

    VALUE_OUT_OF_RANGE = 78

    UNEXPECTED_ERROR = 79

    DISABLED = 80

    INVALID_CEG_SUBMISSION = 81

    RESTRICTED_DEVICE = 82

    REGION_LOCKED = 83

    RATE_LIMIT_EXCEEDED = 84

    ACCOUNT_LOGIN_DENIED_NEED_TWO_FACTOR = 85

    ITEM_DELETED = 86

    ACCOUNT_LOGIN_DENIED_THROTTLE = 87

    TWO_FACTOR_CODE_MISMATCH = 88

    TWO_FACTOR_ACTIVATION_CODE_MISMATCH = 89

    ACCOUNT_ASSOCIATED_TO_MULTIPLE_PARTNERS = 90

    NOT_MODIFIED = 91

    NO_MOBILE_DEVICE = 92

    TIME_NOT_SYNCED = 93

    SMS_CODE_FAILED = 94

    ACCOUNT_LIMIT_EXCEEDED = 95

    ACCOUNT_ACTIVITY_LIMIT_EXCEEDED = 96

    PHONE_ACTIVITY_LIMIT_EXCEEDED = 97

    REFUND_TO_WALLET = 98

    EMAIL_SEND_FAILURE = 99

    NOT_SETTLED = 100

    NEED_CAPTCHA = 101

    GSLT_DENIED = 102

    GS_OWNER_DENIED = 103

    INVALID_ITEM_TYPE = 104

    IP_BANNED = 105

    GSLT_EXPIRED = 106

    INSUFFICIENT_FUNDS = 107

    TOO_MANY_PENDING = 108

    NO_SITE_LICENSES_FOUND = 109

    WG_NETWORK_SEND_EXCEEDED = 110

    ACCOUNT_NOT_FRIENDS = 111

    LIMITED_USER_ACCOUNT = 112

    CANT_REMOVE_ITEM = 113

    ACCOUNT_DELETED = 114

    EXISTING_USER_CANCELLED_LICENSE = 115

    COMMUNITY_COOLDOWN = 116

    NO_LAUNCHER_SPECIFIED = 117

    MUST_AGREE_TO_SSA = 118

    LAUNCHER_MIGRATED = 119

    STEAM_REALM_MISMATCH = 120

    INVALID_SIGNATURE = 121

    PARSE_FAILURE = 122

    NO_VERIFIED_PHONE = 123

    INSUFFICIENT_BATTERY = 124

    CHARGER_REQUIRED = 125

    CACHED_CREDENTIAL_INVALID = 126

    NOT_SUPPORTED = 128

    FAMILY_SIZE_LIMIT_EXCEEDED = 129

    OFFLINE_APP_CACHE_INVALID = 130

    TRY_LATER = 131

class SteamAPIInitResult(enum.IntEnum):
    OK = 0

    FAILED_GENERIC = 1

    NO_STEAM_CLIENT = 2

    VERSION_MISMATCH = 3

class Universe(enum.IntEnum):
    INVALID = 0

    PUBLIC = 1

    BETA = 2

    INTERNAL = 3

    DEV = 4

    MAX = 5

class AccountType(enum.IntEnum):
    INVALID = 0

    INDIVIDUAL = 1

    MULTISEAT = 2

    GAME_SERVER = 3

    ANON_GAME_SERVER = 4

    PENDING = 5

    CONTENT_SERVER = 6

    CLAN = 7

    CHAT = 8

    CONSOLE_USER = 9

    ANON_USER = 10

    MAX = 11

class CSteamID:
    @overload
    def __init__(self) -> None: ...

    @overload
    def __init__(self, steam_id: int) -> None: ...

    @overload
    def __init__(self, account_id: int, universe: Universe, account_type: AccountType) -> None: ...

    @overload
    def __init__(self, account_id: int, account_instance: int, universe: Universe, account_type: AccountType) -> None: ...

    def set(self, account_id: int, universe: Universe, account_type: AccountType) -> None: ...

    def instanced_set(self, account_id: int, instance: int, universe: Universe, account_type: AccountType) -> None: ...

    def full_set(self, identifier: int, universe: Universe, account_type: AccountType) -> None: ...

    def set_from_uint64(self, steam_id: int) -> None: ...

    def clear(self) -> None: ...

    def convert_to_uint64(self) -> int: ...

    def get_static_account_key(self) -> int: ...

    def create_blank_anon_logon(self, universe: Universe) -> None: ...

    def create_blank_anon_user_logon(self, universe: Universe) -> None: ...

    def b_blank_anon_account(self) -> bool: ...

    def b_game_server_account(self) -> bool: ...

    def b_persistent_game_server_account(self) -> bool: ...

    def b_anon_game_server_account(self) -> bool: ...

    def b_content_server_account(self) -> bool: ...

    def b_clan_account(self) -> bool: ...

    def b_chat_account(self) -> bool: ...

    def is_lobby(self) -> bool: ...

    def b_individual_account(self) -> bool: ...

    def b_anon_account(self) -> bool: ...

    def b_anon_user_account(self) -> bool: ...

    def b_console_user_account(self) -> bool: ...

    def set_account_id(self, account_id: int) -> None: ...

    def set_account_instance(self, instance: int) -> None: ...

    def get_account_id(self) -> int: ...

    def get_un_account_instance(self) -> int: ...

    def get_e_account_type(self) -> AccountType: ...

    def get_e_universe(self) -> Universe: ...

    def set_e_universe(self, universe: Universe) -> None: ...

    def is_valid(self) -> bool: ...

    def __eq__(self, arg: object, /) -> bool: ...

    def __ne__(self, arg: object, /) -> bool: ...

    def __lt__(self, arg: CSteamID, /) -> bool: ...

    def __gt__(self, arg: CSteamID, /) -> bool: ...

    def __hash__(self) -> int: ...

    def __repr__(self) -> str: ...

API_CALL_INVALID: int = 0

H_STEAM_NET_CONNECTION_INVALID: int = 0

H_STEAM_LISTEN_SOCKET_INVALID: int = 0

H_STEAM_NET_POLL_GROUP_INVALID: int = 0

def init_ex() -> tuple[SteamAPIInitResult, str]:
    """
    Steam API를 초기화한다 (SDK `SteamAPI_InitEx`).

    실행 중인 Steam 클라이언트에 연결한다. `(결과, 오류 메시지)`를 반환하며 성공하면
    `SteamAPIInitResult.OK`와 빈 문자열. 실패해도 예외를 던지지 않는다.
    """

def shutdown() -> None:
    """
    Steam API를 종료한다 (SDK `SteamAPI_Shutdown`). 중복 호출해도 안전.

    이전에 얻은 인터페이스 객체는 무효가 되어 메서드 호출 시 `RuntimeError`.
    """

def restart_app_if_necessary(app_id: int) -> bool:
    """
    Steam을 거치지 않고 실행됐으면 Steam으로 다시 실행한다 (SDK `SteamAPI_RestartAppIfNecessary`).

    `True`면 Steam이 게임을 다시 띄우므로 게임은 즉시 종료해야 한다. `init_ex()` 전에 호출한다.
    """

def run_callbacks() -> None:
    """
    대기 중인 콜백·CallResult 핸들러를 이 스레드에서 실행한다 (SDK `SteamAPI_RunCallbacks`).

    게임 루프에서 매 프레임 호출한다. 핸들러 예외는 `sys.unraisablehook`으로 보고되고 전파되지 않는다.
    """

_T = TypeVar("_T")

class Callback(Generic[_T]):
    """
    브로드캐스트 콜백 등록 (SDK `CCallback` / `STEAM_CALLBACK`).

    생성하면 바로 등록된다. `unregister()` 전까지 라이브러리가 객체를 붙잡아 두므로
    변수에 보관하지 않아도 해제되지 않는다. 핸들러는 `run_callbacks()` 안에서 호출되며,
    핸들러 예외는 `sys.unraisablehook`으로 보고된다.

        cb = Callback(LobbyEnter, on_enter)  # on_enter(data: LobbyEnter) -> None
    """

    def __init__(self, callback_type: type[_T], handler: Callable[[_T], None]) -> None:
        """`callback_type` 콜백을 `handler`로 등록한다. 콜백 구조체 타입이 아니면 `TypeError`."""

    def register(self, handler: Callable[[_T], None]) -> None:
        """다시 등록한다 (SDK `CCallback::Register`). 이미 등록돼 있으면 해제 후 `handler`로 교체한다."""

    def unregister(self) -> None:
        """등록을 해제한다 (SDK `CCallback::Unregister`). 이후 라이브러리는 객체를 붙잡지 않는다."""

    def is_registered(self) -> bool:
        """등록돼 있으면 `True`."""

class CallResult(Generic[_T]):
    """
    비동기 API 호출 결과 수신 (SDK `CCallResult`).

    결과는 1회만 오고, 받으면 자동으로 비활성이 된다. 활성 동안 라이브러리가 객체를
    붙잡아 둔다. 핸들러는 `run_callbacks()` 안에서 호출되며 예외는 `sys.unraisablehook`으로 보고된다.

        cr = CallResult(LobbyCreated)
        cr.set(api_call, on_created)  # on_created(data: LobbyCreated, io_failure: bool) -> None
    """

    def __init__(self, callback_type: type[_T]) -> None:
        """`callback_type` 결과를 받을 객체를 만든다(비활성). 콜백 구조체 타입이 아니면 `TypeError`."""

    def set(self, api_call: int, handler: Callable[[_T, bool], None]) -> None:
        """
        `api_call` 결과를 `handler(data, io_failure)`로 받는다 (SDK `CCallResult::Set`).
        활성 중이면 이전 호출은 취소된다. `API_CALL_INVALID`면 비활성으로 남는다.
        """

    def cancel(self) -> None:
        """대기 중인 결과 수신을 취소한다 (SDK `CCallResult::Cancel`)."""

    def is_active(self) -> bool:
        """결과를 기다리는 중이면 `True`."""

class LobbyCreated:
    """로비 생성 결과 (SDK `LobbyCreated_t`, `CreateLobby`의 CallResult)."""

    @property
    def result(self) -> Result:
        """`Result.OK`면 성공."""

    @property
    def steam_id_lobby(self) -> int:
        """생성된 로비의 SteamID(uint64). 실패하면 0."""

class LobbyEnter:
    """로비 입장 결과 (SDK `LobbyEnter_t`)."""

    @property
    def steam_id_lobby(self) -> int:
        """입장한 로비의 SteamID(uint64)."""

    @property
    def chat_permissions(self) -> int:
        """현재 사용자의 권한 플래그."""

    @property
    def locked(self) -> bool:
        """`True`면 초대받은 사용자만 입장 가능."""

    @property
    def chat_room_enter_response(self) -> int:
        """입장 응답 코드(SDK `EChatRoomEnterResponse` 값, uint32)."""

class SteamUser:
    """
    SDK `ISteamUser` 인터페이스. `steam_user()`로만 얻는다.

    `shutdown()` 이후 보관해 둔 객체의 메서드를 호출하면 `RuntimeError`.
    """

    def get_steam_id(self) -> CSteamID:
        """현재 로그인한 사용자의 SteamID (SDK `ISteamUser::GetSteamID`)."""

def steam_user() -> SteamUser | None:
    """
    `SteamUser` 인터페이스를 얻는다 (SDK `SteamUser()`). `init_ex()` 전이거나 실패했으면 `None`.
    """

class SteamFriends:
    """
    SDK `ISteamFriends` 인터페이스. `steam_friends()`로만 얻는다.

    `shutdown()` 이후 보관해 둔 객체의 메서드를 호출하면 `RuntimeError`.
    """

    def get_persona_name(self) -> str:
        """현재 사용자의 표시 이름 (SDK `ISteamFriends::GetPersonaName`)."""

    def get_friend_persona_name(self, steam_id_friend: CSteamID) -> str:
        """
        다른 사용자의 표시 이름 (SDK `ISteamFriends::GetFriendPersonaName`).

        모르는 사용자면 SDK처럼 `""` 또는 `"[unknown]"`.
        """

    def activate_game_overlay_invite_dialog(self, steam_id_lobby: CSteamID) -> None:
        """로비 초대 오버레이를 연다 (SDK `ISteamFriends::ActivateGameOverlayInviteDialog`)."""

def steam_friends() -> SteamFriends | None:
    """
    `SteamFriends` 인터페이스를 얻는다 (SDK `SteamFriends()`). `init_ex()` 전이거나 실패했으면 `None`.
    """
