// Interface wrappers: .docs/api/errors.md (None before init, RuntimeError after shutdown)
#pragma once

#include <cstdint>
#include <cstring>
#include <optional>
#include <stdexcept>

#include <nanobind/nanobind.h>
#include <nanobind/stl/optional.h>

namespace nb = nanobind;

// Bumped by shutdown(). A generation, not a pointer check: re-init may return the same address.
inline uint64_t g_interface_generation = 0;

template <class T>
struct Interface {
    T *ptr;
    uint64_t generation;

    T *get() const {
        if (generation != g_interface_generation)
            throw std::runtime_error("Steam interface used after shutdown(); get it again from its accessor");
        return ptr;
    }
};

template <class T>
std::optional<Interface<T>> wrap_interface(T *p) {
    if (!p) return std::nullopt;
    return Interface<T>{p, g_interface_generation};
}

// SDK strings are UTF-8; "replace" so a malformed one never raises. NULL -> "".
inline nb::str decode_utf8(const char *s) {
    if (!s) return nb::str("");
    PyObject *text = PyUnicode_DecodeUTF8(s, (Py_ssize_t)std::strlen(s), "replace");
    if (!text) throw nb::python_error();
    return nb::steal<nb::str>(text);
}
