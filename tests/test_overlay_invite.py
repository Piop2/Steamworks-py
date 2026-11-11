"""Steam 오버레이 초대 창 통합 테스트 (Windows 전용, 추가 패키지 없음, 수동 육안 확인).

오버레이는 OpenGL/D3D의 화면 출력을 가로채 그리므로 GDI 창이 아니라 OpenGL 창이 필요하다.
user32/gdi32/opengl32를 ctypes로 불러 빈 창을 띄우고 매 프레임 SwapBuffers + run_callbacks.
실행 중 초대 창이 뜨는지 눈으로 확인한다: pytest -m integration tests/test_overlay_invite.py
"""

import ctypes
import time
from ctypes import wintypes
from pathlib import Path

import pytest

import steamworks

APP_ID_FILE = Path(__file__).resolve().parents[1] / "steam_appid.txt"
SECONDS = 6.0
INVITE_AFTER = 2.0

user32 = ctypes.WinDLL("user32", use_last_error=True)
gdi32 = ctypes.WinDLL("gdi32", use_last_error=True)
opengl32 = ctypes.WinDLL("opengl32", use_last_error=True)
kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)

LRESULT = ctypes.c_ssize_t
HGLRC = wintypes.HANDLE
WNDPROC = ctypes.WINFUNCTYPE(
    LRESULT, wintypes.HWND, wintypes.UINT, wintypes.WPARAM, wintypes.LPARAM
)

CS_OWNDC = 0x20
WS_OVERLAPPEDWINDOW_VISIBLE = 0x00CF0000 | 0x10000000
CW_USEDEFAULT = -0x80000000
WM_DESTROY = 0x0002
WM_QUIT = 0x0012
PM_REMOVE = 0x0001
PFD_FLAGS = 0x04 | 0x20 | 0x01  # DRAW_TO_WINDOW | SUPPORT_OPENGL | DOUBLEBUFFER
GL_COLOR_BUFFER_BIT = 0x4000


class WNDCLASSW(ctypes.Structure):
    _fields_ = [
        ("style", wintypes.UINT),
        ("lpfnWndProc", WNDPROC),
        ("cbClsExtra", ctypes.c_int),
        ("cbWndExtra", ctypes.c_int),
        ("hInstance", wintypes.HINSTANCE),
        ("hIcon", wintypes.HICON),
        ("hCursor", wintypes.HANDLE),
        ("hbrBackground", wintypes.HBRUSH),
        ("lpszMenuName", wintypes.LPCWSTR),
        ("lpszClassName", wintypes.LPCWSTR),
    ]


class PIXELFORMATDESCRIPTOR(ctypes.Structure):
    _fields_ = [
        ("nSize", wintypes.WORD),
        ("nVersion", wintypes.WORD),
        ("dwFlags", wintypes.DWORD),
        ("iPixelType", ctypes.c_ubyte),
        ("cColorBits", ctypes.c_ubyte),
        *[(f"_b{i}", ctypes.c_ubyte) for i in range(15)],  # shifts/accum/depth/stencil/aux...
        ("iLayerType", ctypes.c_ubyte),
        ("bReserved", ctypes.c_ubyte),
        ("dwLayerMask", wintypes.DWORD),
        ("dwVisibleMask", wintypes.DWORD),
        ("dwDamageMask", wintypes.DWORD),
    ]


user32.DefWindowProcW.argtypes = [wintypes.HWND, wintypes.UINT, wintypes.WPARAM, wintypes.LPARAM]
user32.DefWindowProcW.restype = LRESULT
user32.CreateWindowExW.argtypes = [
    wintypes.DWORD, wintypes.LPCWSTR, wintypes.LPCWSTR, wintypes.DWORD,
    ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int,
    wintypes.HWND, wintypes.HMENU, wintypes.HINSTANCE, wintypes.LPVOID,
]  # fmt: skip
user32.CreateWindowExW.restype = wintypes.HWND
user32.GetDC.argtypes = [wintypes.HWND]
user32.GetDC.restype = wintypes.HDC
user32.PeekMessageW.argtypes = [
    ctypes.POINTER(wintypes.MSG), wintypes.HWND, wintypes.UINT, wintypes.UINT, wintypes.UINT,
]  # fmt: skip
user32.DestroyWindow.argtypes = [wintypes.HWND]
kernel32.GetModuleHandleW.restype = wintypes.HMODULE
gdi32.ChoosePixelFormat.argtypes = [wintypes.HDC, ctypes.POINTER(PIXELFORMATDESCRIPTOR)]
gdi32.SetPixelFormat.argtypes = [wintypes.HDC, ctypes.c_int, ctypes.POINTER(PIXELFORMATDESCRIPTOR)]
gdi32.SwapBuffers.argtypes = [wintypes.HDC]
opengl32.wglCreateContext.argtypes = [wintypes.HDC]
opengl32.wglCreateContext.restype = HGLRC
opengl32.wglMakeCurrent.argtypes = [wintypes.HDC, HGLRC]
opengl32.wglDeleteContext.argtypes = [HGLRC]
opengl32.glClearColor.argtypes = [ctypes.c_float] * 4


def _wnd_proc(hwnd: int, msg: int, wparam: int, lparam: int) -> int:
    if msg == WM_DESTROY:
        user32.PostQuitMessage(0)
        return 0
    return int(user32.DefWindowProcW(hwnd, msg, wparam, lparam))


wnd_proc = WNDPROC(_wnd_proc)  # module-level: must outlive the window


@pytest.mark.integration
def test_overlay_invite_dialog() -> None:
    if not APP_ID_FILE.exists():
        pytest.skip("steam_appid.txt missing")
    code, message = steamworks.init_ex()  # must precede window creation so the overlay can hook
    assert code == steamworks.SteamAPIInitResult.OK, message
    friends = steamworks.steam_friends()
    assert friends is not None

    hinst = kernel32.GetModuleHandleW(None)
    wc = WNDCLASSW(
        style=CS_OWNDC, lpfnWndProc=wnd_proc, hInstance=hinst, lpszClassName="SteamOverlayTest"
    )
    if not user32.RegisterClassW(ctypes.byref(wc)):
        raise ctypes.WinError(ctypes.get_last_error())
    hwnd = user32.CreateWindowExW(
        0, "SteamOverlayTest", "Steam overlay test", WS_OVERLAPPEDWINDOW_VISIBLE,
        CW_USEDEFAULT, CW_USEDEFAULT, 1280, 720, None, None, hinst, None,
    )  # fmt: skip
    if not hwnd:
        raise ctypes.WinError(ctypes.get_last_error())
    hdc = user32.GetDC(hwnd)
    pfd = PIXELFORMATDESCRIPTOR(nSize=ctypes.sizeof(PIXELFORMATDESCRIPTOR), nVersion=1)
    pfd.dwFlags, pfd.cColorBits = PFD_FLAGS, 32
    gdi32.SetPixelFormat(hdc, gdi32.ChoosePixelFormat(hdc, ctypes.byref(pfd)), ctypes.byref(pfd))
    hglrc = opengl32.wglCreateContext(hdc)
    opengl32.wglMakeCurrent(hdc, hglrc)
    opengl32.glClearColor(0.1, 0.1, 0.15, 1.0)
    user32.SetForegroundWindow(hwnd)

    msg = wintypes.MSG()
    start = time.monotonic()
    invited = False
    try:
        while time.monotonic() - start < SECONDS:
            while user32.PeekMessageW(ctypes.byref(msg), None, 0, 0, PM_REMOVE):
                if msg.message == WM_QUIT:
                    break
                user32.TranslateMessage(ctypes.byref(msg))
                user32.DispatchMessageW(ctypes.byref(msg))
            if not invited and time.monotonic() - start >= INVITE_AFTER:
                # No lobby yet (backlog 6): an invalid lobby ID still opens the dialog.
                friends.activate_game_overlay_invite_dialog(steamworks.CSteamID())
                invited = True
            opengl32.glClear(GL_COLOR_BUFFER_BIT)
            gdi32.SwapBuffers(hdc)
            steamworks.run_callbacks()
            time.sleep(1 / 60)
    finally:
        opengl32.wglMakeCurrent(None, None)
        opengl32.wglDeleteContext(hglrc)
        user32.DestroyWindow(hwnd)
        steamworks.shutdown()

    assert invited
