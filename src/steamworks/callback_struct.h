// Callback dispatch: .docs/api/callbacks.md, .docs/api/errors.md
#pragma once

#include <memory>
#include <unordered_map>

#include <nanobind/nanobind.h>

#include <steam/steam_api.h>

namespace nb = nanobind;

using Converter = nb::object (*)(void *);

class CallbackIface {
public:
    virtual ~CallbackIface() = default;
    virtual void reg() = 0;
    virtual void unreg() = 0;
    virtual bool registered() const = 0;
};

class CallResultIface {
public:
    virtual ~CallResultIface() = default;
    virtual void set(SteamAPICall_t api_call) = 0;
    virtual void cancel() = 0;
    virtual bool active() const = 0;
};

// Python-facing objects. The library holds a strong reference while registered/active (Q1-2).
struct Callback {
    PyObject *self = nullptr;
    nb::object handler;
    std::unique_ptr<CallbackIface> impl;
    bool held = false;
};

struct CallResult {
    PyObject *self = nullptr;
    nb::object handler;
    std::unique_ptr<CallResultIface> impl;
    bool held = false;
};

void dispatch_callback(Callback *owner, void *data, Converter convert);
void dispatch_call_result(CallResult *owner, void *data, bool io_failure, Converter convert);

struct CallbackType {
    std::unique_ptr<CallbackIface> (*make_callback)(Callback *);
    std::unique_ptr<CallResultIface> (*make_call_result)(CallResult *);
};

// Keyed by the bound Python struct class.
std::unordered_map<PyObject *, CallbackType> &callback_types();

// Drops references released during dispatch; called after SteamAPI_RunCallbacks returns
// so no C++ callback object is destroyed while the SDK is still dispatching to it.
void release_deferred();

template <class T>
nb::object convert_struct(void *p) {
    return nb::cast(*static_cast<T *>(p), nb::rv_policy::copy);
}

template <class T>
class CallbackImpl final : public CallbackIface {
    // STEAM_CALLBACK_MANUAL; the SDK has no public IsRegistered, so read its flag.
    struct Cb : CCallbackManual<CallbackImpl, T, false> {
        bool registered() const {
            return (this->m_nCallbackFlags & CCallbackBase::k_ECallbackFlagsRegistered) != 0;
        }
    };

public:
    explicit CallbackImpl(Callback *owner) : owner_(owner) {}
    void reg() override { cb_.Register(this, &CallbackImpl::on); }
    void unreg() override { cb_.Unregister(); }
    bool registered() const override { return cb_.registered(); }

private:
    void on(T *p) { dispatch_callback(owner_, p, &convert_struct<T>); }
    Callback *owner_;
    Cb cb_;
};

template <class T>
class CallResultImpl final : public CallResultIface {
public:
    explicit CallResultImpl(CallResult *owner) : owner_(owner) {}
    void set(SteamAPICall_t api_call) override { cr_.Set(api_call, this, &CallResultImpl::on); }
    void cancel() override { cr_.Cancel(); }
    bool active() const override { return cr_.IsActive(); }

private:
    void on(T *p, bool io_failure) { dispatch_call_result(owner_, p, io_failure, &convert_struct<T>); }
    CallResult *owner_;
    CCallResult<CallResultImpl, T> cr_;
};

// Binds a callback struct as a read-only value class usable with Callback/CallResult.
template <class T>
nb::class_<T> bind_callback_struct(nb::module_ &m, const char *name, const char *doc) {
    nb::class_<T> cls(m, name, doc);
    callback_types()[cls.ptr()] = CallbackType{
        [](Callback *o) -> std::unique_ptr<CallbackIface> { return std::make_unique<CallbackImpl<T>>(o); },
        [](CallResult *o) -> std::unique_ptr<CallResultIface> { return std::make_unique<CallResultImpl<T>>(o); },
    };
    return cls;
}
