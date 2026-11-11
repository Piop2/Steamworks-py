# 현재 작업

> 작업 상태가 바뀔 때마다 갱신한다. "지금 뭐 해야 돼?"의 답은 여기의 **다음 할 일**. 전체 작업 목록은 [backlog.md](backlog.md).

## 진행 중
없음. backlog 2(기본 타입·상수) 완료, 3(수명주기) 구현 전 보고 단계.

## 최근 완료 (2026-11-11)
- **backlog 2 기본 타입·상수**: `bind_types.cpp`
  - IntEnum `Result`(130), `SteamAPIInitResult`(4), `Universe`(6, `MAX` 포함), `AccountType`(12). SDK 헤더에서 생성, `tests/test_types.py`가 헤더와 교차 검사.
  - `CSteamID`: 생성자 4종 + 헤더에 정의된 public 메서드 전부(기계적 snake_case) + `==`/`!=`/`<`/`>`·`__hash__`·`__repr__`. 선언만 있고 정의 없는 `Render`·`SetFromString`·`SetFromStringStrict`·문자열 생성자·`BValidExternalSteamID`는 제외(링크 불가).
  - 상수: `API_CALL_INVALID`, `H_STEAM_NET_CONNECTION_INVALID`, `H_STEAM_LISTEN_SOCKET_INVALID`, `H_STEAM_NET_POLL_GROUP_INVALID`.
  - 생성 스텁 `_native.pyi`는 ruff 대상에서 제외. `__eq__`/`__ne__` 스텁은 `nb::sig`로 `object` 인자.
  - 확인: pytest 17 passed, ruff check/format, mypy(strict) 통과.
- **backlog 1 빌드 골격**: scikit-build-core + CMake + nanobind(`cp312-abi3`), DLL `.pyd` 옆 복사, `nanobind_add_stub`. SDK 경로 변수 `STEAMWORKS_SDK_DIR`/`STEAMWORKS_LIB_DIR`.
- API 명세 Q1–Q6 결정: [callbacks](../api/callbacks.md) · [types](../api/types.md) · [errors](../api/errors.md) · [module](../api/module.md) · [scope](../api/scope.md) · [dev-env](../api/dev-env.md).

## 다음 할 일 — backlog 3 수명주기 (구현 전 보고, 승인 대기)
### 범위
| 파이썬 | SDK (`steam_api.h`) | 반환 |
|---|---|---|
| `init_ex() -> tuple[SteamAPIInitResult, str]` | `SteamAPI_InitEx(SteamErrMsg*)` (`SteamErrMsg` = `char[1024]`) | 결과 + 영어 오류 메시지(성공 시 빈 문자열) |
| `shutdown() -> None` | `SteamAPI_Shutdown()` | |
| `restart_app_if_necessary(app_id: int) -> bool` | `SteamAPI_RestartAppIfNecessary(uint32)` | `True`면 게임은 즉시 종료해야 함(SDK와 같음) |
| `run_callbacks() -> None` | `SteamAPI_RunCallbacks()` | |

### 접근 방식
- `bind_lifecycle.cpp` 신설(`bind_types.cpp`와 같은 패턴), `bindings.h`에 `bind_lifecycle` 선언, `_native.cpp`에서 호출.
- 모두 SDK 그대로 통과(1:1). `init_ex`만 출력 인자 → 튜플([types.md](../api/types.md) 출력 인자 규칙).
- 오류 메시지는 `PyUnicode_DecodeUTF8(..., "replace")`로 변환(잘못된 바이트가 있어도 예외 없이).
- 모든 함수는 GIL을 쥔 채 실행([errors.md](../api/errors.md)). 이후 콜백 디스패치(backlog 4)가 `run_callbacks()` 안에서 파이썬을 부르기 때문.
- pytest marker `integration` 등록 + 기본 제외(`addopts = "-m 'not integration'"`). backlog 8에서 시나리오를 더 붙인다.

### 수정할 파일
- 신규: `src/steamworks/bind_lifecycle.cpp`, `tests/test_lifecycle.py`
- 수정: `src/steamworks/bindings.h`, `src/steamworks/_native.cpp`, `CMakeLists.txt`(소스 추가), `src/steamworks/_native.pyi`(재생성), `pyproject.toml`(marker), `.docs/tasks/*`

### 테스트
- 단위(Steam 불필요): 반환 형태가 `(SteamAPIInitResult, str)`인지, 실패면 메시지가 비어 있지 않은지. 성공했으면 `shutdown()`. `run_callbacks()`·`shutdown()`을 init 전에 불러도 안전한지.
- 통합(`-m integration`, Steam 클라이언트 + 레포 루트 `steam_appid.txt`=480): `init_ex()`가 `OK`, `run_callbacks()` 몇 번, `shutdown()`.

### 엣지 케이스·결정 필요
1. **인터페이스 접근자 `None` 처리를 backlog 5로 옮길 것을 제안**: 접근자는 첫 인터페이스(`SteamUser`)와 함께 생긴다. 지금 만들면 쓰는 곳 없는 코드가 된다. "shutdown 후 보관 객체 → `RuntimeError`"([errors.md](../api/errors.md))도 함께 5로.
2. **단위 테스트 결과가 환경에 따라 다름**: 개발 PC에서 Steam이 켜져 있고 `steam_appid.txt`가 있으면 `init_ex()`가 성공한다. → 결과값을 고정하지 않고 형태와 성공/실패별 조건만 검사하고, 성공 시 반드시 `shutdown()`(fixture).
3. **`restart_app_if_necessary`는 단위 테스트에서 호출하지 않는다**: `steam_appid.txt`가 없으면 실제로 Steam을 통해 앱 재실행을 시도할 수 있다(부작용). 통합 테스트에서만 `steam_appid.txt`가 있을 때 `False`인지 확인.
4. **프로세스 전역 상태**: SDK 초기화는 프로세스 단위라 테스트 간에 새지 않도록 fixture로 `shutdown()` 보장.
5. **`init_ex` 중복 호출·init 전 `shutdown`·init 전 `run_callbacks`**: SDK에 그대로 전달(안전하게 처리됨). 바인딩이 막지 않는다.
6. `SteamAPI_IsSteamRunning`, `SteamAPI_ReleaseCurrentThreadMemory` 등 나머지 `steam_api.h` 함수는 범위 밖.
- 미확인: MATCHMAKING venv에서 `pip install -e extern/Steamworks-py` 빌드(backlog 9).
