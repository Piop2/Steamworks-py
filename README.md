# Steamworks-py

Steamworks SDK를 Python에 1:1 바인딩하는 패키지. (현재 골격만 있음. 바인딩: nanobind C++ 확장 모듈, [ADR 0001](.docs/adr/0001-binding-approach.md))

## 개발 환경 (이 레포 전용 venv)

```powershell
py -3.13 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -c "import sys; print(sys.prefix)"   # 이 레포의 .venv를 가리키는지 확인
python -m pip install -e ".[dev]"
pytest
```

## 본 프로젝트(MATCHMAKING)에서 사용

MATCHMAKING의 venv를 활성화한 뒤: `pip install -e extern/Steamworks-py`

Steamworks SDK(**1.65**)는 라이선스상 커밋하지 않는다.
- `steamworks_sdk/`: SDK zip의 `sdk/` 원본 전체 (작업용, gitignore)
- `sdk/`: 빌드할 플랫폼의 DLL·lib만 (win64: `steam_api64.dll`, `steam_api64.lib`)
