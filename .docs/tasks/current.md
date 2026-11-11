# 현재 작업

> 작업 상태가 바뀔 때마다 갱신한다. "지금 뭐 해야 돼?"의 답은 여기의 **다음 할 일**. 전체 작업 목록은 [backlog.md](backlog.md).

## 진행 중
없음. ADR 0001 확정 완료, 구현 전 API 명세 단계로 넘어가기 직전.

## 최근 완료 (2026-11-11)
- [ADR 0001](../adr/0001-binding-approach.md) accepted, 미결 없음:
  - 바인딩: nanobind C++ 확장 모듈(stable ABI `cp312-abi3`, `nanobind.stubgen`)
  - 플랫폼: SDK와 같은 범위, 현재 Windows(64비트) 기준
  - SDK 1.65 고정. `steamworks_sdk/` = 원본 전체(작업용), `sdk/` = 빌드 플랫폼 DLL·lib만
  - 연결: `ISteamNetworkingSockets`(listen socket + `ConnectP2P`), 연결 상태는 Sockets 기준
  - 이름: snake_case(`_t`·`I`·`k_E` 제거 규칙)
  - 초기화: `SteamAPI_InitEx`
  - 실행 시 DLL: 빌드 시 `.pyd` 옆으로 복사
  - **동작은 SDK 함수와 최대한 같게** (이름만 변환)
- SDK 1.65 배치 완료(`steamworks_sdk/`, `sdk/steam_api64.dll`·`.lib`), zip 삭제.
- 빌드 환경 확인: Visual Studio Community 2022(17.14) + MSVC 14.44 + Windows SDK 설치됨, `cl` 컴파일·실행 확인. CMake는 미설치(scikit-build-core가 빌드 시 PyPI `cmake` 사용).

## 다음 할 일
backlog 1 — **API 명세**를 `.docs/api/`에 Q 단위로 결정. **1번 콜백·CallResult API부터.**
- 시작 전 확인: ADR 0001 초기 범위 표의 "파이썬 `init()`은 실패 시 예외"가 "동작은 SDK와 같게" 원칙과 충돌(SDK `InitEx`는 `ESteamAPIInitResult` + 메시지를 반환). 어느 쪽으로 할지 결정 필요.
