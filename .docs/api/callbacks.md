# Q1. 콜백·CallResult 수신 방식 — 결정됨 (2026-11-11)

전제(ADR 0001): `run_callbacks()` 호출 스레드에서 실행, 콜백 구조체는 파이썬 값으로 변환, 파이썬 예외는 C++ 경계를 넘기지 않음.

## Q1-1. 브로드캐스트 콜백 (`STEAM_CALLBACK` / `CCallback` 대응)
객체 단위 등록. 생성 = 등록.
```python
cb = steamworks.Callback(LobbyEnter, on_enter)   # on_enter(data: LobbyEnter) -> None
cb.unregister()        # CCallback::Unregister
cb.register(on_enter)  # 다시 등록
cb.is_registered()
```

## Q1-2. 등록 수명 (SDK와 다른 유일한 지점)
- SDK는 객체 소멸 시 해제. 파이썬은 GC 시점이 비결정적이라 그대로 따르지 않는다.
- **라이브러리가 `unregister()` 전까지 등록을 붙잡아 둔다. 해제는 명시적으로만.**
- `shutdown()` 후에도 등록 객체는 유효하되 콜백이 오지 않는다(SDK와 같음).

## Q1-3. 같은 타입에 핸들러 여러 개
- 허용(`Callback` 객체 여러 개). 호출 순서는 보장하지 않는다(SDK와 같음).

## Q1-4. CallResult (`CCallResult` 대응)
```python
cr = steamworks.CallResult(LobbyCreated)
cr.set(api_call, on_created)   # on_created(data: LobbyCreated, io_failure: bool) -> None
cr.cancel()
cr.is_active()
```
- 결과는 1회. 받은 뒤 자동 비활성(SDK와 같음).
- 활성 중 `set` 재호출 시 이전 호출은 취소(SDK와 같음).
- 활성 중인 `CallResult`도 라이브러리가 결과 수신·`cancel()`까지 붙잡아 둔다(Q1-2와 같은 이유).

## Q1-5. 다른 Q로 넘긴 항목
- `api_call` 핸들 타입 → [types.md](types.md)
- 핸들러 예외 처리 → [errors.md](errors.md)
- 게임서버 콜백(`STEAM_GAMESERVER_CALLBACK`)은 범위 밖.
