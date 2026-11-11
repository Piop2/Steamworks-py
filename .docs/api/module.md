# Q4. 모듈 구조 — 결정됨 (2026-11-11)

```
src/steamworks/
  __init__.py      # _native 재노출만 (로직 없음)
  _native.*.pyd    # nanobind 확장 (cp312-abi3)
  _native.pyi      # nanobind.stubgen 생성, 커밋
  steam_api64.dll  # 빌드 시 복사, 커밋 안 함
  py.typed
```
- **평평한 네임스페이스**: SDK가 전역 네임스페이스이므로 `steamworks.X` 하나로 노출. 하위 모듈로 나누지 않는다.
- **얇은 래퍼 없음**: `__init__.py`는 `from ._native import *` 수준. 파이썬 쪽 편의 로직은 두지 않는다(ADR "바인딩은 얇게").
- **인터페이스 접근자**: SDK 전역 함수 `SteamMatchmaking()` → `steamworks.steam_matchmaking()` (함수 snake_case). 반환 타입은 인터페이스 클래스 `SteamMatchmaking`(`I` 제거) 또는 `None`([errors.md](errors.md)). 클래스와 접근자 이름이 대소문자로 구분된다.
- 수명주기 함수: `init_ex()`, `shutdown()`, `restart_app_if_necessary(app_id)`, `run_callbacks()`.
- 인터페이스 객체는 직접 생성 불가(접근자로만).
