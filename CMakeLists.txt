cmake_minimum_required(VERSION 3.26)
project(steamworks_py LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# SDK는 커밋하지 않는다(ADR 0001). 헤더는 SDK 원본, lib·DLL은 sdk/.
set(STEAMWORKS_SDK_DIR "${CMAKE_CURRENT_SOURCE_DIR}/steamworks_sdk" CACHE PATH "Steamworks SDK root (contains public/)")
set(STEAMWORKS_LIB_DIR "${CMAKE_CURRENT_SOURCE_DIR}/sdk" CACHE PATH "Directory with steam_api lib and DLL")

if(NOT CMAKE_SIZEOF_VOID_P EQUAL 8)
  message(FATAL_ERROR "Only 64-bit builds are supported.")
endif()
if(NOT WIN32)
  message(FATAL_ERROR "Only Windows is supported for now (backlog 10: Linux/macOS).")
endif()

set(STEAM_INCLUDE_DIR "${STEAMWORKS_SDK_DIR}/public")
set(STEAM_LIB "${STEAMWORKS_LIB_DIR}/steam_api64.lib")
set(STEAM_DLL "${STEAMWORKS_LIB_DIR}/steam_api64.dll")
foreach(path IN ITEMS "${STEAM_INCLUDE_DIR}/steam/steam_api.h" "${STEAM_LIB}" "${STEAM_DLL}")
  if(NOT EXISTS "${path}")
    message(FATAL_ERROR "Steamworks SDK file not found: ${path}\n"
      "Place SDK 1.65 as described in README (steamworks_sdk/, sdk/) "
      "or set STEAMWORKS_SDK_DIR / STEAMWORKS_LIB_DIR.")
  endif()
endforeach()

find_package(Python 3.12 REQUIRED COMPONENTS Interpreter Development.Module ${SKBUILD_SABI_COMPONENT})
find_package(nanobind CONFIG REQUIRED)

nanobind_add_module(_native STABLE_ABI NB_STATIC
  src/steamworks/_native.cpp
  src/steamworks/bind_types.cpp
  src/steamworks/bind_lifecycle.cpp
  src/steamworks/bind_callbacks.cpp
  src/steamworks/bind_matchmaking.cpp
  src/steamworks/bind_user.cpp
  src/steamworks/bind_friends.cpp
  src/steamworks/bind_networking_sockets.cpp
  src/steamworks/bind_networking_utils.cpp)
target_include_directories(_native PRIVATE "${STEAM_INCLUDE_DIR}")
target_compile_options(_native PRIVATE /utf-8)  # docstrings are UTF-8 (Korean)
target_link_libraries(_native PRIVATE "${STEAM_LIB}")

# Python은 확장 모듈과 같은 폴더의 의존 DLL을 찾는다. 스텁 생성 시 import에도 필요.
add_custom_command(TARGET _native POST_BUILD
  COMMAND "${CMAKE_COMMAND}" -E copy_if_different "${STEAM_DLL}" "$<TARGET_FILE_DIR:_native>")

nanobind_add_stub(_native_stub
  MODULE _native
  INCLUDE_PRIVATE
  PATTERN_FILE "${CMAKE_CURRENT_SOURCE_DIR}/stubgen_patterns.txt"
  OUTPUT "${CMAKE_CURRENT_SOURCE_DIR}/src/steamworks/_native.pyi"
  PYTHON_PATH "$<TARGET_FILE_DIR:_native>"
  DEPENDS _native)

install(TARGETS _native LIBRARY DESTINATION steamworks)
install(FILES "${STEAM_DLL}" DESTINATION steamworks)
