# Q3. 에러 정책 — 결정됨 (2026-11-11)

원칙: SDK가 실패를 반환값으로 알리면 바인딩도 반환값으로. 예외 변환은 MATCHMAKING `steam` 어댑터에서.

| 상황 | 동작 |
|---|---|
| SDK 함수 실패 | `bool`/`EResult`/무효 핸들 그대로 반환. 예외 없음 |
| `init_ex()` 실패 | `(SteamAPIInitResult, str)` 반환. 예외 없음 |
| `init` 전 인터페이스 접근자 호출 | SDK처럼 NULL → **`None` 반환** (`steam_matchmaking() -> SteamMatchmaking \| None`) |
| 해제된 인터페이스 객체로 메서드 호출 (`shutdown` 후 보관해 둔 객체) | SDK에선 미정의 동작 → 바인딩이 막는다: `RuntimeError`. 프로세스 크래시 방지용, 유일한 예외 발생 지점 |
| `shutdown()` 중복 호출 | SDK에 그대로 전달(SDK가 안전하게 처리) |
| 인자 타입 오류 | nanobind 기본 `TypeError` (SDK 실패가 아니라 파이썬 호출 오류) |
| 콜백·CallResult 핸들러 안의 파이썬 예외 | **`sys.unraisablehook`으로 보고**(`PyErr_WriteUnraisable`) 후 다음 콜백 계속 디스패치. `run_callbacks()`는 예외를 던지지 않는다 |
| 해제된 `SteamNetworkingMessage` 접근 | `ValueError` ([types.md](types.md)) |

- GIL: `run_callbacks()`와 모든 호출은 GIL을 쥔 채 실행(콜백이 같은 스레드에서 파이썬을 부르므로). 블로킹 SDK 호출은 초기 범위에 없음.
