"""Steamworks SDK 1.65 native bindings"""

from collections.abc import Buffer, Callable, Sequence
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

class LobbyType(enum.IntEnum):
    """로비 공개 범위 (SDK `ELobbyType`)."""

    PRIVATE = 0

    FRIENDS_ONLY = 1

    PUBLIC = 2

    INVISIBLE = 3

    PRIVATE_UNIQUE = 4

class LobbyComparison(enum.IntEnum):
    """로비 검색 필터 비교 방식 (SDK `ELobbyComparison`)."""

    EQUAL_TO_OR_LESS_THAN = -2

    LESS_THAN = -1

    EQUAL = 0

    GREATER_THAN = 1

    EQUAL_TO_OR_GREATER_THAN = 2

    NOT_EQUAL = 3

class LobbyDistanceFilter(enum.IntEnum):
    """로비 검색 거리 (SDK `ELobbyDistanceFilter`)."""

    CLOSE = 0

    DEFAULT = 1

    FAR = 2

    WORLDWIDE = 3

class ChatMemberStateChange(enum.IntFlag):
    """
    로비 멤버 상태 변화 비트 플래그 (SDK `EChatMemberStateChange`, IntFlag).

    `ChatMemberStateChange(update.chat_member_state_change)`로 감싸면 조합값도 표현되고 `ChatMemberStateChange.LEFT in flags`로 검사할 수 있다.
    """

    ENTERED = 1

    LEFT = 2

    DISCONNECTED = 4

    KICKED = 8

    BANNED = 16

class ChatRoomEnterResponse(enum.IntEnum):
    """로비 입장 응답 (SDK `EChatRoomEnterResponse`)."""

    SUCCESS = 1

    DOESNT_EXIST = 2

    NOT_ALLOWED = 3

    FULL = 4

    ERROR = 5

    BANNED = 6

    LIMITED = 7

    CLAN_DISABLED = 8

    COMMUNITY_BAN = 9

    MEMBER_BLOCKED_YOU = 10

    YOU_BLOCKED_MEMBER = 11

    RATELIMIT_EXCEEDED = 15

class LobbyCreated:
    """로비 생성 결과 (SDK `LobbyCreated_t`, `create_lobby`의 CallResult)."""

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
        """입장 응답 코드(`ChatRoomEnterResponse` 값, uint32)."""

class LobbyChatUpdate:
    """로비 멤버 입장·퇴장 등 상태 변화 (SDK `LobbyChatUpdate_t`)."""

    @property
    def steam_id_lobby(self) -> int:
        """로비 SteamID(uint64)."""

    @property
    def steam_id_user_changed(self) -> int:
        """상태가 바뀐 사용자 SteamID(uint64)."""

    @property
    def steam_id_making_change(self) -> int:
        """변화를 일으킨 사용자 SteamID(uint64). 추방 등에서 `steam_id_user_changed`와 다름."""

    @property
    def chat_member_state_change(self) -> int:
        """`ChatMemberStateChange` 비트 조합(uint32)."""

class LobbyDataUpdate:
    """로비 또는 멤버 데이터 변경 (SDK `LobbyDataUpdate_t`)."""

    @property
    def steam_id_lobby(self) -> int:
        """로비 SteamID(uint64)."""

    @property
    def steam_id_member(self) -> int:
        """데이터가 바뀐 멤버 SteamID(uint64). 로비 자체 데이터면 로비 ID와 같음."""

    @property
    def success(self) -> int:
        """변경 성공이면 1(uint8)."""

class GameLobbyJoinRequested:
    """
    오버레이에서 로비 참가를 수락함 (SDK `GameLobbyJoinRequested_t`). 받으면 `join_lobby` 호출.
    """

    @property
    def steam_id_lobby(self) -> CSteamID:
        """참가할 로비."""

    @property
    def steam_id_friend(self) -> CSteamID:
        """참가 경로가 된 친구. 친구를 거치지 않았으면 무효."""

class LobbyMatchList:
    """로비 검색 결과 (SDK `LobbyMatchList_t`, `request_lobby_list`의 CallResult)."""

    @property
    def lobbies_matching(self) -> int:
        """찾은 로비 수(uint32). `get_lobby_by_index(0..n-1)`로 조회."""

class SteamMatchmaking:
    """
    SDK `ISteamMatchmaking` 인터페이스. `steam_matchmaking()`로만 얻는다.

    `shutdown()` 이후 보관해 둔 객체의 메서드를 호출하면 `RuntimeError`.
    """

    def create_lobby(self, lobby_type: LobbyType, max_members: int) -> int:
        """
        로비를 만들고 입장한다 (SDK `CreateLobby`). 반환한 호출 ID를 `CallResult(LobbyCreated)`에 넘긴다.

        `LobbyEnter` 콜백도 온다. 실패하면 `API_CALL_INVALID`.
        """

    def join_lobby(self, steam_id_lobby: CSteamID) -> int:
        """로비에 입장한다 (SDK `JoinLobby`). 반환한 호출 ID를 `CallResult(LobbyEnter)`에 넘긴다."""

    def leave_lobby(self, steam_id_lobby: CSteamID) -> None:
        """로비에서 나간다 (SDK `LeaveLobby`)."""

    def get_num_lobby_members(self, steam_id_lobby: CSteamID) -> int:
        """로비 멤버 수 (SDK `GetNumLobbyMembers`). 입장한 로비만 알 수 있다."""

    def get_lobby_member_by_index(self, steam_id_lobby: CSteamID, member: int) -> CSteamID:
        """
        멤버 SteamID (SDK `GetLobbyMemberByIndex`). `get_num_lobby_members` 직후 0..n-1로 호출.
        """

    def get_lobby_data(self, steam_id_lobby: CSteamID, key: str) -> str:
        """로비 데이터 값 (SDK `GetLobbyData`). 없으면 빈 문자열."""

    def set_lobby_data(self, steam_id_lobby: CSteamID, key: str, value: str) -> bool:
        """로비 데이터를 설정한다 (SDK `SetLobbyData`). 방장만 가능. 멤버에게 `LobbyDataUpdate`가 간다."""

    def delete_lobby_data(self, steam_id_lobby: CSteamID, key: str) -> bool:
        """로비 데이터를 지운다 (SDK `DeleteLobbyData`). 방장만 가능."""

    def get_lobby_owner(self, steam_id_lobby: CSteamID) -> CSteamID:
        """방장 SteamID (SDK `GetLobbyOwner`). 입장한 로비만 알 수 있다."""

    def set_lobby_joinable(self, steam_id_lobby: CSteamID, lobby_joinable: bool) -> bool:
        """새 입장 허용 여부를 바꾼다 (SDK `SetLobbyJoinable`). 방장만 가능."""

    def get_lobby_member_limit(self, steam_id_lobby: CSteamID) -> int:
        """최대 인원 (SDK `GetLobbyMemberLimit`). 모르면 0."""

    def request_lobby_list(self) -> int:
        """
        로비를 검색한다 (SDK `RequestLobbyList`). 반환한 호출 ID를 `CallResult(LobbyMatchList)`에 넘긴다.

        필터는 이 호출 전에 추가하며, 호출마다 초기화된다.
        """

    def get_lobby_by_index(self, lobby: int) -> CSteamID:
        """검색 결과의 로비 SteamID (SDK `GetLobbyByIndex`). 범위 밖이면 무효 ID."""

    def add_request_lobby_list_string_filter(self, key_to_match: str, value_to_match: str, comparison_type: LobbyComparison) -> None:
        """문자열 로비 데이터 필터 (SDK `AddRequestLobbyListStringFilter`)."""

    def add_request_lobby_list_numerical_filter(self, key_to_match: str, value_to_match: int, comparison_type: LobbyComparison) -> None:
        """숫자 로비 데이터 필터 (SDK `AddRequestLobbyListNumericalFilter`)."""

    def add_request_lobby_list_filter_slots_available(self, slots_available: int) -> None:
        """빈자리 수 필터 (SDK `AddRequestLobbyListFilterSlotsAvailable`)."""

    def add_request_lobby_list_distance_filter(self, lobby_distance_filter: LobbyDistanceFilter) -> None:
        """검색 거리 필터 (SDK `AddRequestLobbyListDistanceFilter`)."""

    def add_request_lobby_list_result_count_filter(self, max_results: int) -> None:
        """최대 결과 수 (SDK `AddRequestLobbyListResultCountFilter`)."""

def steam_matchmaking() -> SteamMatchmaking | None:
    """
    `SteamMatchmaking` 인터페이스를 얻는다 (SDK `SteamMatchmaking()`). `init_ex()` 전이거나 실패했으면 `None`.
    """

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

class SteamNetworkingConnectionState(enum.IntEnum):
    """연결 상태 (SDK `ESteamNetworkingConnectionState`)."""

    NONE = 0

    CONNECTING = 1

    FINDING_ROUTE = 2

    CONNECTED = 3

    CLOSED_BY_PEER = 4

    PROBLEM_DETECTED_LOCALLY = 5

class SteamNetConnectionEnd(enum.IntEnum):
    """
    연결 종료 사유 (SDK `ESteamNetConnectionEnd`). `*_MIN`/`*_MAX`는 범위 경계.

    앱이 `close_connection`에 넘기는 사유는 `APP_MIN`..`APP_MAX`(정상) 또는 `APP_EXCEPTION_MIN`..`APP_EXCEPTION_MAX`(비정상) 범위의 정수.
    """

    INVALID = 0

    APP_MIN = 1000

    APP_GENERIC = 1000

    APP_MAX = 1999

    APP_EXCEPTION_MIN = 2000

    APP_EXCEPTION_GENERIC = 2000

    APP_EXCEPTION_MAX = 2999

    LOCAL_MIN = 3000

    LOCAL_OFFLINE_MODE = 3001

    LOCAL_MANY_RELAY_CONNECTIVITY = 3002

    LOCAL_HOSTED_SERVER_PRIMARY_RELAY = 3003

    LOCAL_NETWORK_CONFIG = 3004

    LOCAL_RIGHTS = 3005

    LOCAL_P2P_ICE_NO_PUBLIC_ADDRESSES = 3006

    LOCAL_MAX = 3999

    REMOTE_MIN = 4000

    REMOTE_TIMEOUT = 4001

    REMOTE_BAD_CRYPT = 4002

    REMOTE_BAD_CERT = 4003

    REMOTE_BAD_PROTOCOL_VERSION = 4006

    REMOTE_P2P_ICE_NO_PUBLIC_ADDRESSES = 4007

    REMOTE_MAX = 4999

    MISC_MIN = 5000

    MISC_GENERIC = 5001

    MISC_INTERNAL_ERROR = 5002

    MISC_TIMEOUT = 5003

    MISC_STEAM_CONNECTIVITY = 5005

    MISC_NO_RELAY_SESSIONS_TO_CLIENT = 5006

    MISC_P2P_RENDEZVOUS = 5008

    MISC_P2P_NAT_FIREWALL = 5009

    MISC_PEER_SENT_NO_CONNECTION = 5010

    MISC_MAX = 5999

class SteamNetworkingConfig(enum.IntEnum):
    """
    연결 설정 항목 (SDK `ESteamNetworkingConfigValue`). `SteamNetworkingConfigValue.set_*`에 쓴다.

    구조체 `SteamNetworkingConfigValue`와 이름이 겹쳐 `Value`를 뺐다. 각 항목의 타입·범위는 SDK 헤더 주석 참조.
    """

    INVALID = 0

    TIMEOUT_INITIAL = 24

    TIMEOUT_CONNECTED = 25

    SEND_BUFFER_SIZE = 9

    RECV_BUFFER_SIZE = 47

    RECV_BUFFER_MESSAGES = 48

    RECV_MAX_MESSAGE_SIZE = 49

    RECV_MAX_SEGMENTS_PER_PACKET = 50

    CONNECTION_USER_DATA = 40

    SEND_RATE_MIN = 10

    SEND_RATE_MAX = 11

    NAGLE_TIME = 12

    IP_ALLOW_WITHOUT_AUTH = 23

    IP_LOCAL_HOST_ALLOW_WITHOUT_AUTH = 52

    MTU_PACKET_SIZE = 32

    MTU_DATA_SIZE = 33

    UNENCRYPTED = 34

    SYMMETRIC_CONNECT = 37

    LOCAL_VIRTUAL_PORT = 38

    DUAL_WIFI_ENABLE = 39

    ENABLE_DIAGNOSTICS_UI = 46

    SEND_TIME_SINCE_PREVIOUS_PACKET = 59

    FAKE_PACKET_LOSS_SEND = 2

    FAKE_PACKET_LOSS_RECV = 3

    FAKE_PACKET_LAG_SEND = 4

    FAKE_PACKET_LAG_RECV = 5

    FAKE_PACKET_JITTER_SEND_AVG = 53

    FAKE_PACKET_JITTER_SEND_MAX = 54

    FAKE_PACKET_JITTER_SEND_PCT = 55

    FAKE_PACKET_JITTER_RECV_AVG = 56

    FAKE_PACKET_JITTER_RECV_MAX = 57

    FAKE_PACKET_JITTER_RECV_PCT = 58

    FAKE_PACKET_REORDER_SEND = 6

    FAKE_PACKET_REORDER_RECV = 7

    FAKE_PACKET_REORDER_TIME = 8

    FAKE_PACKET_DUP_SEND = 26

    FAKE_PACKET_DUP_RECV = 27

    FAKE_PACKET_DUP_TIME_MAX = 28

    PACKET_TRACE_MAX_BYTES = 41

    FAKE_RATE_LIMIT_SEND_RATE = 42

    FAKE_RATE_LIMIT_SEND_BURST = 43

    FAKE_RATE_LIMIT_RECV_RATE = 44

    FAKE_RATE_LIMIT_RECV_BURST = 45

    OUT_OF_ORDER_CORRECTION_WINDOW_MICROSECONDS = 51

    CALLBACK_CONNECTION_STATUS_CHANGED = 201

    CALLBACK_AUTH_STATUS_CHANGED = 202

    CALLBACK_RELAY_NETWORK_STATUS_CHANGED = 203

    CALLBACK_MESSAGES_SESSION_REQUEST = 204

    CALLBACK_MESSAGES_SESSION_FAILED = 205

    CALLBACK_CREATE_CONNECTION_SIGNALING = 206

    CALLBACK_FAKE_IP_RESULT = 207

    P2P_STUN_SERVER_LIST = 103

    P2P_TRANSPORT_ICE_ENABLE = 104

    P2P_TRANSPORT_ICE_PENALTY = 105

    P2P_TRANSPORT_SDR_PENALTY = 106

    P2P_TURN_SERVER_LIST = 107

    P2P_TURN_USER_LIST = 108

    P2P_TURN_PASS_LIST = 109

    P2P_TRANSPORT_ICE_IMPLEMENTATION = 110

    SDR_CLIENT_CONSECUTITIVE_PING_TIMEOUTS_FAIL_INITIAL = 19

    SDR_CLIENT_CONSECUTITIVE_PING_TIMEOUTS_FAIL = 20

    SDR_CLIENT_MIN_PINGS_BEFORE_PING_ACCURATE = 21

    SDR_CLIENT_SINGLE_SOCKET = 22

    SDR_CLIENT_FORCE_RELAY_CLUSTER = 29

    SDR_CLIENT_DEV_TICKET = 30

    SDR_CLIENT_FORCE_PROXY_ADDR = 31

    SDR_CLIENT_FAKE_CLUSTER_PING = 36

    SDR_CLIENT_LIMIT_PING_PROBES_TO_NEAREST_N = 60

    LOG_LEVEL_ACK_RTT = 13

    LOG_LEVEL_PACKET_DECODE = 14

    LOG_LEVEL_MESSAGE = 15

    LOG_LEVEL_PACKET_GAPS = 16

    LOG_LEVEL_P2P_RENDEZVOUS = 17

    LOG_LEVEL_SDR_RELAY_PINGS = 18

    ECN = 999

    SDR_CLIENT_ENABLE_TOS_PROBES = 998

STEAM_NETWORKING_SEND_UNRELIABLE: int = 0

STEAM_NETWORKING_SEND_NO_NAGLE: int = 1

STEAM_NETWORKING_SEND_UNRELIABLE_NO_NAGLE: int = 1

STEAM_NETWORKING_SEND_NO_DELAY: int = 4

STEAM_NETWORKING_SEND_UNRELIABLE_NO_DELAY: int = 5

STEAM_NETWORKING_SEND_RELIABLE: int = 8

STEAM_NETWORKING_SEND_RELIABLE_NO_NAGLE: int = 9

STEAM_NETWORKING_SEND_USE_CURRENT_THREAD: int = 16

STEAM_NETWORKING_SEND_AUTO_RESTART_BROKEN_SESSION: int = 32

STEAM_NETWORK_CONNECTION_INFO_FLAGS_UNAUTHENTICATED: int = 1

STEAM_NETWORK_CONNECTION_INFO_FLAGS_UNENCRYPTED: int = 2

STEAM_NETWORK_CONNECTION_INFO_FLAGS_LOOPBACK_BUFFERS: int = 4

STEAM_NETWORK_CONNECTION_INFO_FLAGS_FAST: int = 8

STEAM_NETWORK_CONNECTION_INFO_FLAGS_RELAYED: int = 16

STEAM_NETWORK_CONNECTION_INFO_FLAGS_DUAL_WIFI: int = 32

class SteamNetworkingIdentity:
    """
    연결 상대 식별자 (SDK `SteamNetworkingIdentity`). 초기 범위는 SteamID 형식만.

    SDK처럼 가변이라 해시할 수 없다. dict 키가 필요하면 `get_steam_id64()`를 쓴다.
    """

    def __init__(self) -> None:
        """무효(빈) 식별자를 만든다."""

    def clear(self) -> None:
        """무효 상태로 되돌린다 (SDK `Clear`)."""

    def is_invalid(self) -> bool:
        """무효 형식이면 `True` (SDK `IsInvalid`). SteamID 자체의 유효성은 보지 않는다."""

    def set_steam_id(self, steam_id: CSteamID) -> None:
        """SteamID로 설정한다 (SDK `SetSteamID`)."""

    def get_steam_id(self) -> CSteamID:
        """SteamID (SDK `GetSteamID`). SteamID 형식이 아니면 무효 `CSteamID`."""

    def set_steam_id64(self, steam_id: int) -> None:
        """64비트 SteamID로 설정한다 (SDK `SetSteamID64`)."""

    def get_steam_id64(self) -> int:
        """64비트 SteamID (SDK `GetSteamID64`). SteamID 형식이 아니면 0."""

    def __eq__(self, arg: object, /) -> bool: ...

    def __repr__(self) -> str: ...

    __hash__ = None  # type: ignore[assignment]

class SteamNetworkingConfigValue:
    """
    연결 설정 값 하나 (SDK `SteamNetworkingConfigValue_t`). `create_listen_socket_p2p`·`connect_p2p`의 `options`에 넘긴다.

    문자열·포인터 값(`SetString`/`SetPtr`)은 범위 밖.
    """

    def __init__(self) -> None:
        """빈 설정(`SteamNetworkingConfig.INVALID`)을 만든다."""

    def set_int32(self, val: SteamNetworkingConfig, data: int) -> None:
        """int32 설정 (SDK `SetInt32`)."""

    def set_int64(self, val: SteamNetworkingConfig, data: int) -> None:
        """int64 설정 (SDK `SetInt64`)."""

    def set_float(self, val: SteamNetworkingConfig, data: float) -> None:
        """float 설정 (SDK `SetFloat`)."""

class SteamNetConnectionInfo:
    """연결 정보 (SDK `SteamNetConnectionInfo_t`, 읽기 전용 값)."""

    @property
    def identity_remote(self) -> SteamNetworkingIdentity:
        """상대 식별자(복사본)."""

    @property
    def user_data(self) -> int:
        """연결 사용자 데이터(int64)."""

    @property
    def listen_socket(self) -> int:
        """이 연결을 받은 listen socket. 내가 건 연결이면 `H_STEAM_LISTEN_SOCKET_INVALID`."""

    @property
    def state(self) -> SteamNetworkingConnectionState:
        """현재 상태."""

    @property
    def end_reason(self) -> int:
        """종료 사유(`SteamNetConnectionEnd` 값 또는 앱 정의 정수, int)."""

    @property
    def end_debug(self) -> str:
        """종료 사유 설명(디버그용)."""

    @property
    def connection_description(self) -> str:
        """연결 설명(디버그용)."""

    @property
    def flags(self) -> int:
        """`STEAM_NETWORK_CONNECTION_INFO_FLAGS_*` 조합(int)."""

class SteamNetworkingMessage:
    """
    받은 메시지 (SDK `SteamNetworkingMessage_t`). 수신 함수로만 얻는다.

    다 쓰면 `release()`를 호출한다(SDK `Release`). 해제 후 접근은 `ValueError`, `shutdown()` 후 접근은 `RuntimeError`. 호출을 잊으면 GC 때 해제된다.
    """

    def get_data(self) -> bytes:
        """본문 복사본."""

    def release(self) -> None:
        """메시지를 해제한다 (SDK `Release`)."""

    @property
    def conn(self) -> int:
        """보낸 연결 핸들."""

    @property
    def identity_peer(self) -> SteamNetworkingIdentity:
        """보낸 상대(복사본)."""

    @property
    def message_number(self) -> int:
        """연결 안에서의 메시지 번호(int64)."""

    @property
    def flags(self) -> int:
        """보낼 때 쓴 `STEAM_NETWORKING_SEND_*` 플래그."""

    @property
    def channel(self) -> int:
        """채널(연결형에서는 미사용)."""

    @property
    def conn_user_data(self) -> int:
        """수신 시점의 연결 사용자 데이터(int64)."""

    @property
    def time_received(self) -> int:
        """수신 시각(마이크로초, `SteamNetworkingMicroseconds`)."""

class SteamNetConnectionStatusChangedCallback:
    """
    연결 상태 변화 (SDK `SteamNetConnectionStatusChangedCallback_t`).

    호스트는 `CONNECTING`을 받으면 `accept_connection`, 끊김(`CLOSED_BY_PEER`/`PROBLEM_DETECTED_LOCALLY`)이면 `close_connection`으로 정리한다.
    """

    @property
    def conn(self) -> int:
        """연결 핸들."""

    @property
    def info(self) -> SteamNetConnectionInfo:
        """현재 연결 정보(현재 상태는 `info.state`)."""

    @property
    def old_state(self) -> SteamNetworkingConnectionState:
        """이전 상태."""

class SteamNetworkingSockets:
    """
    SDK `ISteamNetworkingSockets` 인터페이스. `steam_networking_sockets()`로만 얻는다.

    `shutdown()` 이후 보관해 둔 객체의 메서드를 호출하면 `RuntimeError`.
    """

    def create_listen_socket_p2p(self, local_virtual_port: int, options: Sequence[SteamNetworkingConfigValue]) -> int:
        """
        P2P 접속을 받는 listen socket을 연다 (SDK `CreateListenSocketP2P`). 실패하면 `H_STEAM_LISTEN_SOCKET_INVALID`.

        먼저 `init_relay_network_access()`를 호출해 두면 첫 연결이 빠르다.
        """

    def close_listen_socket(self, socket: int) -> bool:
        """listen socket을 닫는다 (SDK `CloseListenSocket`). 이 소켓으로 받은 연결도 끊긴다."""

    def connect_p2p(self, identity_remote: SteamNetworkingIdentity, remote_virtual_port: int, options: Sequence[SteamNetworkingConfigValue]) -> int:
        """
        상대의 P2P listen socket에 접속한다 (SDK `ConnectP2P`). 실패하면 `H_STEAM_NET_CONNECTION_INVALID`.

        결과는 `SteamNetConnectionStatusChangedCallback`으로 온다.
        """

    def accept_connection(self, conn: int) -> Result:
        """들어온 연결을 수락한다 (SDK `AcceptConnection`). `CONNECTING` 상태 콜백에서 호출."""

    def close_connection(self, peer: int, reason: int, debug: str, enable_linger: bool) -> bool:
        """
        연결을 닫고 핸들을 해제한다 (SDK `CloseConnection`). `reason`은 `SteamNetConnectionEnd.APP_*` 범위.

        `enable_linger=True`면 보낼 신뢰 메시지를 다 보낸 뒤 닫는다.
        """

    def get_connection_info(self, conn: int) -> tuple[bool, SteamNetConnectionInfo]:
        """연결 정보 (SDK `GetConnectionInfo`). 무효 핸들이면 `(False, 의미 없는 값)`."""

    def send_message_to_connection(self, conn: int, data: Buffer, send_flags: int) -> tuple[Result, int]:
        """
        메시지를 보낸다 (SDK `SendMessageToConnection`). `(Result, 메시지 번호)`. 실패하면 번호는 0.

        `send_flags`는 `STEAM_NETWORKING_SEND_*`.
        """

    def receive_messages_on_connection(self, conn: int, max_messages: int) -> list[SteamNetworkingMessage]:
        """
        연결에서 메시지를 최대 `max_messages`개 받는다 (SDK `ReceiveMessagesOnConnection`).

        무효 핸들이면 빈 리스트. 음수면 `ValueError`. 받은 메시지는 `release()`한다.
        """

    def create_poll_group(self) -> int:
        """poll group을 만든다 (SDK `CreatePollGroup`). 여러 연결의 메시지를 한 번에 받는 데 쓴다."""

    def destroy_poll_group(self, poll_group: int) -> bool:
        """poll group을 없앤다 (SDK `DestroyPollGroup`). 속한 연결은 그룹에서 빠진다."""

    def set_connection_poll_group(self, conn: int, poll_group: int) -> bool:
        """
        연결을 poll group에 넣는다 (SDK `SetConnectionPollGroup`). `H_STEAM_NET_POLL_GROUP_INVALID`면 뺀다.
        """

    def receive_messages_on_poll_group(self, poll_group: int, max_messages: int) -> list[SteamNetworkingMessage]:
        """
        poll group에서 메시지를 최대 `max_messages`개 받는다 (SDK `ReceiveMessagesOnPollGroup`).

        무효 핸들이면 빈 리스트. 음수면 `ValueError`. 받은 메시지는 `release()`한다.
        """

def steam_networking_sockets() -> SteamNetworkingSockets | None:
    """
    `SteamNetworkingSockets` 인터페이스를 얻는다 (SDK `SteamNetworkingSockets()`). `init_ex()` 전이거나 실패했으면 `None`.
    """

class SteamNetworkingUtils:
    """
    SDK `ISteamNetworkingUtils` 인터페이스. `steam_networking_utils()`로만 얻는다.

    `shutdown()` 이후 보관해 둔 객체의 메서드를 호출하면 `RuntimeError`.
    """

    def init_relay_network_access(self) -> None:
        """
        릴레이 네트워크 접근을 미리 준비한다 (SDK `InitRelayNetworkAccess`). 비동기, 반환값 없음.

        P2P 연결 직전이 아니라 시작 시 호출해 두면 첫 연결 지연이 줄어든다.
        """

def steam_networking_utils() -> SteamNetworkingUtils | None:
    """
    `SteamNetworkingUtils` 인터페이스를 얻는다 (SDK `SteamNetworkingUtils()`). `init_ex()` 전이거나 실패했으면 `None`.
    """
