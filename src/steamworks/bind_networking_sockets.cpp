// ISteamNetworkingSockets: ADR 0001 connection/message scope + .docs/api/types.md (identity, info, message)
#include <cstdint>
#include <limits>
#include <string>
#include <tuple>
#include <vector>

#include <steam/steam_api.h>

#include <nanobind/operators.h>
#include <nanobind/stl/string.h>
#include <nanobind/stl/tuple.h>
#include <nanobind/stl/vector.h>

#include "bindings.h"
#include "callback_struct.h"
#include "interface.h"

using namespace nb::literals;
using Sockets = Interface<ISteamNetworkingSockets>;

// Owns one received message until release(); GC releases a forgotten one (leak safety net).
struct Message {
    SteamNetworkingMessage_t *ptr;
    uint64_t generation;

    explicit Message(SteamNetworkingMessage_t *p) : ptr(p), generation(g_interface_generation) {}
    Message(Message &&o) noexcept : ptr(o.ptr), generation(o.generation) { o.ptr = nullptr; }
    Message(const Message &) = delete;
    Message &operator=(const Message &) = delete;
    Message &operator=(Message &&) = delete;
    // After shutdown() the SDK's release hook may be gone: leak rather than crash.
    ~Message() {
        if (ptr && generation == g_interface_generation) ptr->Release();
    }

    SteamNetworkingMessage_t *get() const {
        if (!ptr) throw nb::value_error("SteamNetworkingMessage used after release()");
        if (generation != g_interface_generation)
            throw std::runtime_error("SteamNetworkingMessage used after shutdown()");
        return ptr;
    }
};

// SDK returns -1 for an invalid handle; the list cannot carry it, so it becomes empty (types.md).
template <class F>
static std::vector<Message> receive(int max_messages, F &&call) {
    if (max_messages < 0) throw nb::value_error("max_messages must be >= 0");
    std::vector<SteamNetworkingMessage_t *> buf(static_cast<size_t>(max_messages));
    int n = call(buf.data(), max_messages);
    std::vector<Message> out;
    if (n > 0) {
        out.reserve(static_cast<size_t>(n));
        for (int i = 0; i < n; ++i) out.emplace_back(buf[i]);
    }
    return out;
}

static const SteamNetworkingConfigValue_t *options_ptr(const std::vector<SteamNetworkingConfigValue_t> &o) {
    return o.empty() ? nullptr : o.data();
}

static void bind_enums(nb::module_ &m) {
    // FinWait/Linger/Dead are internal ("will not be returned by any API") and excluded.
    nb::enum_<ESteamNetworkingConnectionState>(m, "SteamNetworkingConnectionState", nb::is_arithmetic(),
                                               "연결 상태 (SDK `ESteamNetworkingConnectionState`).")
        .value("NONE", k_ESteamNetworkingConnectionState_None)
        .value("CONNECTING", k_ESteamNetworkingConnectionState_Connecting)
        .value("FINDING_ROUTE", k_ESteamNetworkingConnectionState_FindingRoute)
        .value("CONNECTED", k_ESteamNetworkingConnectionState_Connected)
        .value("CLOSED_BY_PEER", k_ESteamNetworkingConnectionState_ClosedByPeer)
        .value("PROBLEM_DETECTED_LOCALLY", k_ESteamNetworkingConnectionState_ProblemDetectedLocally);

    nb::enum_<ESteamNetConnectionEnd>(
        m, "SteamNetConnectionEnd", nb::is_arithmetic(),
        "연결 종료 사유 (SDK `ESteamNetConnectionEnd`). `*_MIN`/`*_MAX`는 범위 경계.\n\n"
        "앱이 `close_connection`에 넘기는 사유는 `APP_MIN`..`APP_MAX`(정상) 또는 "
        "`APP_EXCEPTION_MIN`..`APP_EXCEPTION_MAX`(비정상) 범위의 정수.")
        .value("INVALID", k_ESteamNetConnectionEnd_Invalid)
        .value("APP_MIN", k_ESteamNetConnectionEnd_App_Min)
        .value("APP_GENERIC", k_ESteamNetConnectionEnd_App_Generic)
        .value("APP_MAX", k_ESteamNetConnectionEnd_App_Max)
        .value("APP_EXCEPTION_MIN", k_ESteamNetConnectionEnd_AppException_Min)
        .value("APP_EXCEPTION_GENERIC", k_ESteamNetConnectionEnd_AppException_Generic)
        .value("APP_EXCEPTION_MAX", k_ESteamNetConnectionEnd_AppException_Max)
        .value("LOCAL_MIN", k_ESteamNetConnectionEnd_Local_Min)
        .value("LOCAL_OFFLINE_MODE", k_ESteamNetConnectionEnd_Local_OfflineMode)
        .value("LOCAL_MANY_RELAY_CONNECTIVITY", k_ESteamNetConnectionEnd_Local_ManyRelayConnectivity)
        .value("LOCAL_HOSTED_SERVER_PRIMARY_RELAY", k_ESteamNetConnectionEnd_Local_HostedServerPrimaryRelay)
        .value("LOCAL_NETWORK_CONFIG", k_ESteamNetConnectionEnd_Local_NetworkConfig)
        .value("LOCAL_RIGHTS", k_ESteamNetConnectionEnd_Local_Rights)
        .value("LOCAL_P2P_ICE_NO_PUBLIC_ADDRESSES", k_ESteamNetConnectionEnd_Local_P2P_ICE_NoPublicAddresses)
        .value("LOCAL_MAX", k_ESteamNetConnectionEnd_Local_Max)
        .value("REMOTE_MIN", k_ESteamNetConnectionEnd_Remote_Min)
        .value("REMOTE_TIMEOUT", k_ESteamNetConnectionEnd_Remote_Timeout)
        .value("REMOTE_BAD_CRYPT", k_ESteamNetConnectionEnd_Remote_BadCrypt)
        .value("REMOTE_BAD_CERT", k_ESteamNetConnectionEnd_Remote_BadCert)
        .value("REMOTE_BAD_PROTOCOL_VERSION", k_ESteamNetConnectionEnd_Remote_BadProtocolVersion)
        .value("REMOTE_P2P_ICE_NO_PUBLIC_ADDRESSES", k_ESteamNetConnectionEnd_Remote_P2P_ICE_NoPublicAddresses)
        .value("REMOTE_MAX", k_ESteamNetConnectionEnd_Remote_Max)
        .value("MISC_MIN", k_ESteamNetConnectionEnd_Misc_Min)
        .value("MISC_GENERIC", k_ESteamNetConnectionEnd_Misc_Generic)
        .value("MISC_INTERNAL_ERROR", k_ESteamNetConnectionEnd_Misc_InternalError)
        .value("MISC_TIMEOUT", k_ESteamNetConnectionEnd_Misc_Timeout)
        .value("MISC_STEAM_CONNECTIVITY", k_ESteamNetConnectionEnd_Misc_SteamConnectivity)
        .value("MISC_NO_RELAY_SESSIONS_TO_CLIENT", k_ESteamNetConnectionEnd_Misc_NoRelaySessionsToClient)
        .value("MISC_P2P_RENDEZVOUS", k_ESteamNetConnectionEnd_Misc_P2P_Rendezvous)
        .value("MISC_P2P_NAT_FIREWALL", k_ESteamNetConnectionEnd_Misc_P2P_NAT_Firewall)
        .value("MISC_PEER_SENT_NO_CONNECTION", k_ESteamNetConnectionEnd_Misc_PeerSentNoConnection)
        .value("MISC_MAX", k_ESteamNetConnectionEnd_Misc_Max);

    // Named SteamNetworkingConfig: "SteamNetworkingConfigValue" is the struct (types.md).
    nb::enum_<ESteamNetworkingConfigValue>(
        m, "SteamNetworkingConfig", nb::is_arithmetic(),
        "연결 설정 항목 (SDK `ESteamNetworkingConfigValue`). `SteamNetworkingConfigValue.set_*`에 쓴다.\n\n"
        "구조체 `SteamNetworkingConfigValue`와 이름이 겹쳐 `Value`를 뺐다. 각 항목의 타입·범위는 SDK 헤더 주석 참조.")
        .value("INVALID", k_ESteamNetworkingConfig_Invalid)
        .value("TIMEOUT_INITIAL", k_ESteamNetworkingConfig_TimeoutInitial)
        .value("TIMEOUT_CONNECTED", k_ESteamNetworkingConfig_TimeoutConnected)
        .value("SEND_BUFFER_SIZE", k_ESteamNetworkingConfig_SendBufferSize)
        .value("RECV_BUFFER_SIZE", k_ESteamNetworkingConfig_RecvBufferSize)
        .value("RECV_BUFFER_MESSAGES", k_ESteamNetworkingConfig_RecvBufferMessages)
        .value("RECV_MAX_MESSAGE_SIZE", k_ESteamNetworkingConfig_RecvMaxMessageSize)
        .value("RECV_MAX_SEGMENTS_PER_PACKET", k_ESteamNetworkingConfig_RecvMaxSegmentsPerPacket)
        .value("CONNECTION_USER_DATA", k_ESteamNetworkingConfig_ConnectionUserData)
        .value("SEND_RATE_MIN", k_ESteamNetworkingConfig_SendRateMin)
        .value("SEND_RATE_MAX", k_ESteamNetworkingConfig_SendRateMax)
        .value("NAGLE_TIME", k_ESteamNetworkingConfig_NagleTime)
        .value("IP_ALLOW_WITHOUT_AUTH", k_ESteamNetworkingConfig_IP_AllowWithoutAuth)
        .value("IP_LOCAL_HOST_ALLOW_WITHOUT_AUTH", k_ESteamNetworkingConfig_IPLocalHost_AllowWithoutAuth)
        .value("MTU_PACKET_SIZE", k_ESteamNetworkingConfig_MTU_PacketSize)
        .value("MTU_DATA_SIZE", k_ESteamNetworkingConfig_MTU_DataSize)
        .value("UNENCRYPTED", k_ESteamNetworkingConfig_Unencrypted)
        .value("SYMMETRIC_CONNECT", k_ESteamNetworkingConfig_SymmetricConnect)
        .value("LOCAL_VIRTUAL_PORT", k_ESteamNetworkingConfig_LocalVirtualPort)
        .value("DUAL_WIFI_ENABLE", k_ESteamNetworkingConfig_DualWifi_Enable)
        .value("ENABLE_DIAGNOSTICS_UI", k_ESteamNetworkingConfig_EnableDiagnosticsUI)
        .value("SEND_TIME_SINCE_PREVIOUS_PACKET", k_ESteamNetworkingConfig_SendTimeSincePreviousPacket)
        .value("FAKE_PACKET_LOSS_SEND", k_ESteamNetworkingConfig_FakePacketLoss_Send)
        .value("FAKE_PACKET_LOSS_RECV", k_ESteamNetworkingConfig_FakePacketLoss_Recv)
        .value("FAKE_PACKET_LAG_SEND", k_ESteamNetworkingConfig_FakePacketLag_Send)
        .value("FAKE_PACKET_LAG_RECV", k_ESteamNetworkingConfig_FakePacketLag_Recv)
        .value("FAKE_PACKET_JITTER_SEND_AVG", k_ESteamNetworkingConfig_FakePacketJitter_Send_Avg)
        .value("FAKE_PACKET_JITTER_SEND_MAX", k_ESteamNetworkingConfig_FakePacketJitter_Send_Max)
        .value("FAKE_PACKET_JITTER_SEND_PCT", k_ESteamNetworkingConfig_FakePacketJitter_Send_Pct)
        .value("FAKE_PACKET_JITTER_RECV_AVG", k_ESteamNetworkingConfig_FakePacketJitter_Recv_Avg)
        .value("FAKE_PACKET_JITTER_RECV_MAX", k_ESteamNetworkingConfig_FakePacketJitter_Recv_Max)
        .value("FAKE_PACKET_JITTER_RECV_PCT", k_ESteamNetworkingConfig_FakePacketJitter_Recv_Pct)
        .value("FAKE_PACKET_REORDER_SEND", k_ESteamNetworkingConfig_FakePacketReorder_Send)
        .value("FAKE_PACKET_REORDER_RECV", k_ESteamNetworkingConfig_FakePacketReorder_Recv)
        .value("FAKE_PACKET_REORDER_TIME", k_ESteamNetworkingConfig_FakePacketReorder_Time)
        .value("FAKE_PACKET_DUP_SEND", k_ESteamNetworkingConfig_FakePacketDup_Send)
        .value("FAKE_PACKET_DUP_RECV", k_ESteamNetworkingConfig_FakePacketDup_Recv)
        .value("FAKE_PACKET_DUP_TIME_MAX", k_ESteamNetworkingConfig_FakePacketDup_TimeMax)
        .value("PACKET_TRACE_MAX_BYTES", k_ESteamNetworkingConfig_PacketTraceMaxBytes)
        .value("FAKE_RATE_LIMIT_SEND_RATE", k_ESteamNetworkingConfig_FakeRateLimit_Send_Rate)
        .value("FAKE_RATE_LIMIT_SEND_BURST", k_ESteamNetworkingConfig_FakeRateLimit_Send_Burst)
        .value("FAKE_RATE_LIMIT_RECV_RATE", k_ESteamNetworkingConfig_FakeRateLimit_Recv_Rate)
        .value("FAKE_RATE_LIMIT_RECV_BURST", k_ESteamNetworkingConfig_FakeRateLimit_Recv_Burst)
        .value("OUT_OF_ORDER_CORRECTION_WINDOW_MICROSECONDS",
               k_ESteamNetworkingConfig_OutOfOrderCorrectionWindowMicroseconds)
        .value("CALLBACK_CONNECTION_STATUS_CHANGED", k_ESteamNetworkingConfig_Callback_ConnectionStatusChanged)
        .value("CALLBACK_AUTH_STATUS_CHANGED", k_ESteamNetworkingConfig_Callback_AuthStatusChanged)
        .value("CALLBACK_RELAY_NETWORK_STATUS_CHANGED", k_ESteamNetworkingConfig_Callback_RelayNetworkStatusChanged)
        .value("CALLBACK_MESSAGES_SESSION_REQUEST", k_ESteamNetworkingConfig_Callback_MessagesSessionRequest)
        .value("CALLBACK_MESSAGES_SESSION_FAILED", k_ESteamNetworkingConfig_Callback_MessagesSessionFailed)
        .value("CALLBACK_CREATE_CONNECTION_SIGNALING", k_ESteamNetworkingConfig_Callback_CreateConnectionSignaling)
        .value("CALLBACK_FAKE_IP_RESULT", k_ESteamNetworkingConfig_Callback_FakeIPResult)
        .value("P2P_STUN_SERVER_LIST", k_ESteamNetworkingConfig_P2P_STUN_ServerList)
        .value("P2P_TRANSPORT_ICE_ENABLE", k_ESteamNetworkingConfig_P2P_Transport_ICE_Enable)
        .value("P2P_TRANSPORT_ICE_PENALTY", k_ESteamNetworkingConfig_P2P_Transport_ICE_Penalty)
        .value("P2P_TRANSPORT_SDR_PENALTY", k_ESteamNetworkingConfig_P2P_Transport_SDR_Penalty)
        .value("P2P_TURN_SERVER_LIST", k_ESteamNetworkingConfig_P2P_TURN_ServerList)
        .value("P2P_TURN_USER_LIST", k_ESteamNetworkingConfig_P2P_TURN_UserList)
        .value("P2P_TURN_PASS_LIST", k_ESteamNetworkingConfig_P2P_TURN_PassList)
        .value("P2P_TRANSPORT_ICE_IMPLEMENTATION", k_ESteamNetworkingConfig_P2P_Transport_ICE_Implementation)
        .value("SDR_CLIENT_CONSECUTITIVE_PING_TIMEOUTS_FAIL_INITIAL",
               k_ESteamNetworkingConfig_SDRClient_ConsecutitivePingTimeoutsFailInitial)
        .value("SDR_CLIENT_CONSECUTITIVE_PING_TIMEOUTS_FAIL",
               k_ESteamNetworkingConfig_SDRClient_ConsecutitivePingTimeoutsFail)
        .value("SDR_CLIENT_MIN_PINGS_BEFORE_PING_ACCURATE",
               k_ESteamNetworkingConfig_SDRClient_MinPingsBeforePingAccurate)
        .value("SDR_CLIENT_SINGLE_SOCKET", k_ESteamNetworkingConfig_SDRClient_SingleSocket)
        .value("SDR_CLIENT_FORCE_RELAY_CLUSTER", k_ESteamNetworkingConfig_SDRClient_ForceRelayCluster)
        .value("SDR_CLIENT_DEV_TICKET", k_ESteamNetworkingConfig_SDRClient_DevTicket)
        .value("SDR_CLIENT_FORCE_PROXY_ADDR", k_ESteamNetworkingConfig_SDRClient_ForceProxyAddr)
        .value("SDR_CLIENT_FAKE_CLUSTER_PING", k_ESteamNetworkingConfig_SDRClient_FakeClusterPing)
        .value("SDR_CLIENT_LIMIT_PING_PROBES_TO_NEAREST_N",
               k_ESteamNetworkingConfig_SDRClient_LimitPingProbesToNearestN)
        .value("LOG_LEVEL_ACK_RTT", k_ESteamNetworkingConfig_LogLevel_AckRTT)
        .value("LOG_LEVEL_PACKET_DECODE", k_ESteamNetworkingConfig_LogLevel_PacketDecode)
        .value("LOG_LEVEL_MESSAGE", k_ESteamNetworkingConfig_LogLevel_Message)
        .value("LOG_LEVEL_PACKET_GAPS", k_ESteamNetworkingConfig_LogLevel_PacketGaps)
        .value("LOG_LEVEL_P2P_RENDEZVOUS", k_ESteamNetworkingConfig_LogLevel_P2PRendezvous)
        .value("LOG_LEVEL_SDR_RELAY_PINGS", k_ESteamNetworkingConfig_LogLevel_SDRRelayPings)
        .value("ECN", k_ESteamNetworkingConfig_ECN)
        .value("SDR_CLIENT_ENABLE_TOS_PROBES", k_ESteamNetworkingConfig_SDRClient_EnableTOSProbes);
}

static void bind_constants(nb::module_ &m) {
    m.attr("STEAM_NETWORKING_SEND_UNRELIABLE") = k_nSteamNetworkingSend_Unreliable;
    m.attr("STEAM_NETWORKING_SEND_NO_NAGLE") = k_nSteamNetworkingSend_NoNagle;
    m.attr("STEAM_NETWORKING_SEND_UNRELIABLE_NO_NAGLE") = k_nSteamNetworkingSend_UnreliableNoNagle;
    m.attr("STEAM_NETWORKING_SEND_NO_DELAY") = k_nSteamNetworkingSend_NoDelay;
    m.attr("STEAM_NETWORKING_SEND_UNRELIABLE_NO_DELAY") = k_nSteamNetworkingSend_UnreliableNoDelay;
    m.attr("STEAM_NETWORKING_SEND_RELIABLE") = k_nSteamNetworkingSend_Reliable;
    m.attr("STEAM_NETWORKING_SEND_RELIABLE_NO_NAGLE") = k_nSteamNetworkingSend_ReliableNoNagle;
    m.attr("STEAM_NETWORKING_SEND_USE_CURRENT_THREAD") = k_nSteamNetworkingSend_UseCurrentThread;
    m.attr("STEAM_NETWORKING_SEND_AUTO_RESTART_BROKEN_SESSION") = k_nSteamNetworkingSend_AutoRestartBrokenSession;

    m.attr("STEAM_NETWORK_CONNECTION_INFO_FLAGS_UNAUTHENTICATED") = k_nSteamNetworkConnectionInfoFlags_Unauthenticated;
    m.attr("STEAM_NETWORK_CONNECTION_INFO_FLAGS_UNENCRYPTED") = k_nSteamNetworkConnectionInfoFlags_Unencrypted;
    m.attr("STEAM_NETWORK_CONNECTION_INFO_FLAGS_LOOPBACK_BUFFERS") = k_nSteamNetworkConnectionInfoFlags_LoopbackBuffers;
    m.attr("STEAM_NETWORK_CONNECTION_INFO_FLAGS_FAST") = k_nSteamNetworkConnectionInfoFlags_Fast;
    m.attr("STEAM_NETWORK_CONNECTION_INFO_FLAGS_RELAYED") = k_nSteamNetworkConnectionInfoFlags_Relayed;
    m.attr("STEAM_NETWORK_CONNECTION_INFO_FLAGS_DUAL_WIFI") = k_nSteamNetworkConnectionInfoFlags_DualWifi;
}

static void bind_value_types(nb::module_ &m) {
    nb::class_<SteamNetworkingIdentity> identity(
        m, "SteamNetworkingIdentity",
        "연결 상대 식별자 (SDK `SteamNetworkingIdentity`). 초기 범위는 SteamID 형식만.\n\n"
        "SDK처럼 가변이라 해시할 수 없다. dict 키가 필요하면 `get_steam_id64()`를 쓴다.");
    identity
        .def(
            "__init__",
            [](SteamNetworkingIdentity *p) {
                new (p) SteamNetworkingIdentity();
                p->Clear();
            },
            "무효(빈) 식별자를 만든다.")
        .def("clear", &SteamNetworkingIdentity::Clear, "무효 상태로 되돌린다 (SDK `Clear`).")
        .def("is_invalid", &SteamNetworkingIdentity::IsInvalid,
             "무효 형식이면 `True` (SDK `IsInvalid`). SteamID 자체의 유효성은 보지 않는다.")
        .def("set_steam_id", &SteamNetworkingIdentity::SetSteamID, "steam_id"_a,
             "SteamID로 설정한다 (SDK `SetSteamID`).")
        .def("get_steam_id", &SteamNetworkingIdentity::GetSteamID,
             "SteamID (SDK `GetSteamID`). SteamID 형식이 아니면 무효 `CSteamID`.")
        .def("set_steam_id64", &SteamNetworkingIdentity::SetSteamID64, "steam_id"_a,
             "64비트 SteamID로 설정한다 (SDK `SetSteamID64`).")
        .def("get_steam_id64", &SteamNetworkingIdentity::GetSteamID64,
             "64비트 SteamID (SDK `GetSteamID64`). SteamID 형식이 아니면 0.")
        .def(nb::self == nb::self, nb::sig("def __eq__(self, arg: object, /) -> bool"))
        .def("__repr__", [](const SteamNetworkingIdentity &i) -> std::string {
            // SDK ToString goes through SteamNetworkingUtils() (NULL before init), so format here.
            if (i.m_eType == k_ESteamNetworkingIdentityType_Invalid) return "SteamNetworkingIdentity()";
            if (i.m_eType == k_ESteamNetworkingIdentityType_SteamID)
                return "SteamNetworkingIdentity(steam_id64=" + std::to_string(i.GetSteamID64()) + ")";
            return "SteamNetworkingIdentity(type=" + std::to_string(int(i.m_eType)) + ")";
        });
    identity.attr("__hash__") = nb::none();

    nb::class_<SteamNetworkingConfigValue_t>(
        m, "SteamNetworkingConfigValue",
        "연결 설정 값 하나 (SDK `SteamNetworkingConfigValue_t`). `create_listen_socket_p2p`·`connect_p2p`의 "
        "`options`에 넘긴다.\n\n문자열·포인터 값(`SetString`/`SetPtr`)은 범위 밖.")
        .def(
            "__init__",
            [](SteamNetworkingConfigValue_t *p) {
                new (p) SteamNetworkingConfigValue_t();
                p->SetInt32(k_ESteamNetworkingConfig_Invalid, 0);
            },
            "빈 설정(`SteamNetworkingConfig.INVALID`)을 만든다.")
        .def("set_int32", &SteamNetworkingConfigValue_t::SetInt32, "val"_a, "data"_a,
             "int32 설정 (SDK `SetInt32`).")
        .def("set_int64", &SteamNetworkingConfigValue_t::SetInt64, "val"_a, "data"_a,
             "int64 설정 (SDK `SetInt64`).")
        .def("set_float", &SteamNetworkingConfigValue_t::SetFloat, "val"_a, "data"_a,
             "float 설정 (SDK `SetFloat`).");

    // Excluded (not needed for P2P): m_addrRemote, m_idPOPRemote, m_idPOPRelay, padding/reserved.
    nb::class_<SteamNetConnectionInfo_t>(m, "SteamNetConnectionInfo",
                                         "연결 정보 (SDK `SteamNetConnectionInfo_t`, 읽기 전용 값).")
        .def_prop_ro(
            "identity_remote", [](const SteamNetConnectionInfo_t &i) { return i.m_identityRemote; },
            "상대 식별자(복사본).")
        .def_ro("user_data", &SteamNetConnectionInfo_t::m_nUserData, "연결 사용자 데이터(int64).")
        .def_ro("listen_socket", &SteamNetConnectionInfo_t::m_hListenSocket,
                "이 연결을 받은 listen socket. 내가 건 연결이면 `H_STEAM_LISTEN_SOCKET_INVALID`.")
        .def_ro("state", &SteamNetConnectionInfo_t::m_eState, "현재 상태.")
        .def_ro("end_reason", &SteamNetConnectionInfo_t::m_eEndReason,
                "종료 사유(`SteamNetConnectionEnd` 값 또는 앱 정의 정수, int).")
        .def_prop_ro(
            "end_debug", [](const SteamNetConnectionInfo_t &i) { return decode_utf8(i.m_szEndDebug); },
            "종료 사유 설명(디버그용).")
        .def_prop_ro(
            "connection_description",
            [](const SteamNetConnectionInfo_t &i) { return decode_utf8(i.m_szConnectionDescription); },
            "연결 설명(디버그용).")
        .def_ro("flags", &SteamNetConnectionInfo_t::m_nFlags, "`STEAM_NETWORK_CONNECTION_INFO_FLAGS_*` 조합(int).");

    // Excluded (send-side or internal): m_nUserData, m_idxLane, m_pfnFreeData, m_pfnRelease; m_pData/m_cbSize -> get_data().
    nb::class_<Message>(m, "SteamNetworkingMessage",
                        "받은 메시지 (SDK `SteamNetworkingMessage_t`). 수신 함수로만 얻는다.\n\n"
                        "다 쓰면 `release()`를 호출한다(SDK `Release`). 해제 후 접근은 `ValueError`, "
                        "`shutdown()` 후 접근은 `RuntimeError`. 호출을 잊으면 GC 때 해제된다.")
        .def("get_data", [](const Message &msg) {
                 auto *p = msg.get();
                 return nb::bytes(p->m_pData, static_cast<size_t>(p->m_cbSize));
             },
             "본문 복사본.")
        .def(
            "release",
            [](Message &msg) {
                msg.get()->Release();
                msg.ptr = nullptr;
            },
            "메시지를 해제한다 (SDK `Release`).")
        .def_prop_ro(
            "conn", [](const Message &msg) { return msg.get()->m_conn; }, "보낸 연결 핸들.")
        .def_prop_ro(
            "identity_peer", [](const Message &msg) { return msg.get()->m_identityPeer; }, "보낸 상대(복사본).")
        .def_prop_ro(
            "message_number", [](const Message &msg) { return msg.get()->m_nMessageNumber; },
            "연결 안에서의 메시지 번호(int64).")
        .def_prop_ro(
            "flags", [](const Message &msg) { return msg.get()->m_nFlags; },
            "보낼 때 쓴 `STEAM_NETWORKING_SEND_*` 플래그.")
        .def_prop_ro(
            "channel", [](const Message &msg) { return msg.get()->m_nChannel; }, "채널(연결형에서는 미사용).")
        .def_prop_ro(
            "conn_user_data", [](const Message &msg) { return msg.get()->m_nConnUserData; },
            "수신 시점의 연결 사용자 데이터(int64).")
        .def_prop_ro(
            "time_received", [](const Message &msg) { return msg.get()->m_usecTimeReceived; },
            "수신 시각(마이크로초, `SteamNetworkingMicroseconds`).");

    bind_callback_struct<SteamNetConnectionStatusChangedCallback_t>(
        m, "SteamNetConnectionStatusChangedCallback",
        "연결 상태 변화 (SDK `SteamNetConnectionStatusChangedCallback_t`).\n\n"
        "호스트는 `CONNECTING`을 받으면 `accept_connection`, 끊김(`CLOSED_BY_PEER`/`PROBLEM_DETECTED_LOCALLY`)이면 "
        "`close_connection`으로 정리한다.")
        .def_ro("conn", &SteamNetConnectionStatusChangedCallback_t::m_hConn, "연결 핸들.")
        .def_prop_ro(
            "info", [](const SteamNetConnectionStatusChangedCallback_t &c) { return c.m_info; },
            "현재 연결 정보(현재 상태는 `info.state`).")
        .def_ro("old_state", &SteamNetConnectionStatusChangedCallback_t::m_eOldState, "이전 상태.");
}

void bind_networking_sockets(nb::module_ &m) {
    bind_enums(m);
    bind_constants(m);
    bind_value_types(m);

    nb::class_<Sockets>(m, "SteamNetworkingSockets",
                        "SDK `ISteamNetworkingSockets` 인터페이스. `steam_networking_sockets()`로만 얻는다.\n\n"
                        "`shutdown()` 이후 보관해 둔 객체의 메서드를 호출하면 `RuntimeError`.")
        .def(
            "create_listen_socket_p2p",
            [](const Sockets &s, int local_virtual_port, const std::vector<SteamNetworkingConfigValue_t> &options) {
                return s.get()->CreateListenSocketP2P(local_virtual_port, static_cast<int>(options.size()),
                                                      options_ptr(options));
            },
            "local_virtual_port"_a, "options"_a,
            "P2P 접속을 받는 listen socket을 연다 (SDK `CreateListenSocketP2P`). 실패하면 "
            "`H_STEAM_LISTEN_SOCKET_INVALID`.\n\n먼저 `init_relay_network_access()`를 호출해 두면 첫 연결이 빠르다.")
        .def(
            "close_listen_socket", [](const Sockets &s, HSteamListenSocket socket) { return s.get()->CloseListenSocket(socket); },
            "socket"_a, "listen socket을 닫는다 (SDK `CloseListenSocket`). 이 소켓으로 받은 연결도 끊긴다.")
        .def(
            "connect_p2p",
            [](const Sockets &s, const SteamNetworkingIdentity &identity_remote, int remote_virtual_port,
               const std::vector<SteamNetworkingConfigValue_t> &options) {
                return s.get()->ConnectP2P(identity_remote, remote_virtual_port, static_cast<int>(options.size()),
                                           options_ptr(options));
            },
            "identity_remote"_a, "remote_virtual_port"_a, "options"_a,
            "상대의 P2P listen socket에 접속한다 (SDK `ConnectP2P`). 실패하면 `H_STEAM_NET_CONNECTION_INVALID`.\n\n"
            "결과는 `SteamNetConnectionStatusChangedCallback`으로 온다.")
        .def(
            "accept_connection", [](const Sockets &s, HSteamNetConnection conn) { return s.get()->AcceptConnection(conn); },
            "conn"_a, "들어온 연결을 수락한다 (SDK `AcceptConnection`). `CONNECTING` 상태 콜백에서 호출.")
        .def(
            "close_connection",
            [](const Sockets &s, HSteamNetConnection peer, int reason, const char *debug, bool enable_linger) {
                return s.get()->CloseConnection(peer, reason, debug, enable_linger);
            },
            "peer"_a, "reason"_a, "debug"_a, "enable_linger"_a,
            "연결을 닫고 핸들을 해제한다 (SDK `CloseConnection`). `reason`은 `SteamNetConnectionEnd.APP_*` 범위.\n\n"
            "`enable_linger=True`면 보낼 신뢰 메시지를 다 보낸 뒤 닫는다.")
        .def(
            "get_connection_info",
            [](const Sockets &s, HSteamNetConnection conn) {
                SteamNetConnectionInfo_t info{};
                bool ok = s.get()->GetConnectionInfo(conn, &info);
                return std::make_tuple(ok, info);
            },
            "conn"_a, "연결 정보 (SDK `GetConnectionInfo`). 무효 핸들이면 `(False, 의미 없는 값)`.")
        .def(
            "send_message_to_connection",
            [](const Sockets &s, HSteamNetConnection conn, nb::handle data, int send_flags) {
                ISteamNetworkingSockets *api = s.get();
                Py_buffer view;
                if (PyObject_GetBuffer(data.ptr(), &view, PyBUF_SIMPLE) != 0) throw nb::python_error();
                if (view.len > static_cast<Py_ssize_t>(std::numeric_limits<uint32>::max())) {
                    PyBuffer_Release(&view);
                    throw nb::value_error("data too large");
                }
                int64 message_number = 0;
                EResult r = api->SendMessageToConnection(conn, view.buf, static_cast<uint32>(view.len), send_flags,
                                                         &message_number);
                PyBuffer_Release(&view);
                return std::make_tuple(r, message_number);
            },
            "conn"_a, "data"_a, "send_flags"_a,
            nb::sig("def send_message_to_connection(self, conn: int, data: collections.abc.Buffer, "
                    "send_flags: int) -> tuple[Result, int]"),
            "메시지를 보낸다 (SDK `SendMessageToConnection`). `(Result, 메시지 번호)`. 실패하면 번호는 0.\n\n"
            "`send_flags`는 `STEAM_NETWORKING_SEND_*`.")
        .def(
            "receive_messages_on_connection",
            [](const Sockets &s, HSteamNetConnection conn, int max_messages) {
                ISteamNetworkingSockets *api = s.get();
                return receive(max_messages, [&](SteamNetworkingMessage_t **out, int n) {
                    return api->ReceiveMessagesOnConnection(conn, out, n);
                });
            },
            "conn"_a, "max_messages"_a,
            "연결에서 메시지를 최대 `max_messages`개 받는다 (SDK `ReceiveMessagesOnConnection`).\n\n"
            "무효 핸들이면 빈 리스트. 음수면 `ValueError`. 받은 메시지는 `release()`한다.")
        .def(
            "create_poll_group", [](const Sockets &s) { return s.get()->CreatePollGroup(); },
            "poll group을 만든다 (SDK `CreatePollGroup`). 여러 연결의 메시지를 한 번에 받는 데 쓴다.")
        .def(
            "destroy_poll_group",
            [](const Sockets &s, HSteamNetPollGroup poll_group) { return s.get()->DestroyPollGroup(poll_group); },
            "poll_group"_a, "poll group을 없앤다 (SDK `DestroyPollGroup`). 속한 연결은 그룹에서 빠진다.")
        .def(
            "set_connection_poll_group",
            [](const Sockets &s, HSteamNetConnection conn, HSteamNetPollGroup poll_group) {
                return s.get()->SetConnectionPollGroup(conn, poll_group);
            },
            "conn"_a, "poll_group"_a,
            "연결을 poll group에 넣는다 (SDK `SetConnectionPollGroup`). `H_STEAM_NET_POLL_GROUP_INVALID`면 뺀다.")
        .def(
            "receive_messages_on_poll_group",
            [](const Sockets &s, HSteamNetPollGroup poll_group, int max_messages) {
                ISteamNetworkingSockets *api = s.get();
                return receive(max_messages, [&](SteamNetworkingMessage_t **out, int n) {
                    return api->ReceiveMessagesOnPollGroup(poll_group, out, n);
                });
            },
            "poll_group"_a, "max_messages"_a,
            "poll group에서 메시지를 최대 `max_messages`개 받는다 (SDK `ReceiveMessagesOnPollGroup`).\n\n"
            "무효 핸들이면 빈 리스트. 음수면 `ValueError`. 받은 메시지는 `release()`한다.");

    m.def(
        "steam_networking_sockets", [] { return wrap_interface(SteamNetworkingSockets()); },
        "`SteamNetworkingSockets` 인터페이스를 얻는다 (SDK `SteamNetworkingSockets()`). "
        "`init_ex()` 전이거나 실패했으면 `None`.");
}
