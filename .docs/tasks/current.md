# 현재 작업

> 작업 상태가 바뀔 때마다 갱신한다. "지금 뭐 해야 돼?"의 답은 여기의 **다음 할 일**. 전체 작업 목록은 [backlog.md](backlog.md).

## 진행 중
**사용자 결정 대기**: [backlog.md](backlog.md) 구현 우선순위 승인 + 1번(빌드 골격) 구현 전 보고(아래) 승인.

## 최근 완료 (2026-11-11)
- [ADR 0001](../adr/0001-binding-approach.md) accepted. `init_ex()`는 SDK와 같게 `(ESteamAPIInitResult, str)` 반환으로 문구 수정.
- API 명세 Q1–Q6 전부 추천안으로 결정: [callbacks](../api/callbacks.md) · [types](../api/types.md) · [errors](../api/errors.md) · [module](../api/module.md) · [scope](../api/scope.md) · [dev-env](../api/dev-env.md)
- SDK 1.65 배치, 빌드 환경(VS 2022 + MSVC 14.44) 확인.

## 다음 할 일 — backlog 1 빌드 골격 (구현 전 보고)
### 접근 방식
- `pyproject.toml` 빌드 백엔드를 setuptools → scikit-build-core. 빌드 의존성: `scikit-build-core`, `nanobind`. CMake는 scikit-build-core가 PyPI `cmake`로 확보.
- `wheel.py-api = "cp312"`로 abi3 휠. `nanobind_add_module(_native STABLE_ABI NB_STATIC ...)`.
- `CMakeLists.txt`: `STEAMWORKS_SDK_DIR`(기본 `steamworks_sdk`)에서 헤더 `public/`, `STEAMWORKS_LIB_DIR`(기본 `sdk`)에서 `steam_api64.lib` 링크. 빌드 후 `steam_api64.dll`을 `.pyd` 옆으로 복사·설치. 이어서 `nanobind_add_stub`으로 `_native.pyi` 생성.
- `_native`는 빈 모듈(SDK 헤더 include + 링크만 확인). `__init__.py`는 `from ._native import *`.
### 수정할 파일
- 수정: `pyproject.toml`, `src/steamworks/__init__.py`, `tests/test_smoke.py`(`_native` import 확인 추가), `.gitignore`(필요 시), `README.md`(빌드 전제), ADR 0001 "빌드" 줄(헤더/lib 경로 분리 문구)
- 신규: `CMakeLists.txt`, `src/steamworks/_native.cpp`(위치는 `src/cpp/`도 가능 — 제안: `src/steamworks/_native.cpp`), `src/steamworks/py.typed`, `src/steamworks/_native.pyi`(생성물, 커밋)
### 엣지 케이스
- SDK 없음(`steamworks_sdk/public` 또는 `sdk/steam_api64.lib` 누락) → CMake가 경로를 알려주는 `FATAL_ERROR`.
- 32비트 Python → CMake에서 거부(현재 win64만).
- editable 설치(`pip install -e .`): scikit-build-core는 C++ 변경 시 재설치 필요. DLL이 실제 `.pyd` 위치 옆에 있어야 함(설치 경로 기준 복사).
- 스텁 생성은 모듈 import가 필요 → DLL 복사가 스텁 생성보다 먼저.
- `requires-python >=3.13` 유지, 휠 태그는 `cp312-abi3`(3.13에서 설치 가능).
- MATCHMAKING venv에서 `pip install -e extern/Steamworks-py` 시 SDK 기본 경로가 서브모듈 기준으로 잡혀야 함(CMake에서 소스 디렉터리 기준 상대경로).
