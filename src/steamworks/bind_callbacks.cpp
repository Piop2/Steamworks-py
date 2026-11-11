// Callback / CallResult: .docs/api/callbacks.md
#include <exception>
#include <new>
#include <unordered_set>
#include <vector>

#include <nanobind/typing.h>

#include "bindings.h"
#include "callback_struct.h"

using namespace nb::literals;

std::unordered_map<PyObject *, CallbackType> &callback_types() {
    static auto *types = new std::unordered_map<PyObject *, CallbackType>();  // leaked: outlives interpreter teardown
    return *types;
}

static std::vector<nb::object> &deferred() {
    static auto *v = new std::vector<nb::object>();
    return *v;
}

void release_deferred() {
    std::vector<nb::object> drop;
    drop.swap(deferred());
}

static const CallbackType &lookup(nb::handle type) {
    auto it = callback_types().find(type.ptr());
    if (it == callback_types().end()) throw nb::type_error("not a Steam callback struct type");
    return it->second;
}

template <class O>
static std::unordered_set<O *> &held_set() {
    static auto *s = new std::unordered_set<O *>();
    return *s;
}

template <class O>
static void hold(O &o) {
    if (!o.held) {
        o.held = true;
        held_set<O>().insert(&o);
        Py_INCREF(o.self);
    }
}

template <class O>
static void release(O &o) {
    if (o.held) {
        o.held = false;
        held_set<O>().erase(&o);
        deferred().push_back(nb::steal(o.self));
    }
}

// At interpreter exit, unregister what is still held, as SDK objects do in their destructors.
static void release_all() {
    for (Callback *o : std::vector<Callback *>(held_set<Callback>().begin(), held_set<Callback>().end())) {
        o->impl->unreg();
        release(*o);
    }
    for (CallResult *o : std::vector<CallResult *>(held_set<CallResult>().begin(), held_set<CallResult>().end())) {
        o->impl->cancel();
        release(*o);
    }
    release_deferred();
}

// Python exceptions must not cross into the SDK: report via sys.unraisablehook and continue.
template <class F>
static void guarded(nb::handle ctx, F &&f) {
    try {
        f();
    } catch (nb::python_error &e) {
        e.restore();
        PyErr_WriteUnraisable(ctx.ptr());
    } catch (const std::exception &e) {
        PyErr_SetString(PyExc_RuntimeError, e.what());
        PyErr_WriteUnraisable(ctx.ptr());
    }
}

void dispatch_callback(Callback *o, void *data, Converter convert) {
    nb::object handler = o->handler;  // the handler may call register() with another one
    guarded(handler, [&] { handler(convert(data)); });
}

void dispatch_call_result(CallResult *o, void *data, bool io_failure, Converter convert) {
    nb::object handler = o->handler;
    guarded(handler, [&] { handler(convert(data), io_failure); });
    if (!o->impl->active()) release(*o);  // still active if the handler chained set()
}

// GC support so handler <-> Callback reference cycles are collected after unregister().
template <class O>
static int tp_traverse(PyObject *self, visitproc visit, void *arg) {
    Py_VISIT(Py_TYPE(self));
    if (!nb::inst_ready(self)) return 0;
    Py_VISIT(nb::inst_ptr<O>(self)->handler.ptr());
    return 0;
}

template <class O>
static int tp_clear(PyObject *self) {
    nb::inst_ptr<O>(self)->handler.reset();
    return 0;
}

static PyType_Slot callback_slots[] = {
    {Py_tp_traverse, (void *)tp_traverse<Callback>},
    {Py_tp_clear, (void *)tp_clear<Callback>},
    {0, nullptr},
};

static PyType_Slot call_result_slots[] = {
    {Py_tp_traverse, (void *)tp_traverse<CallResult>},
    {Py_tp_clear, (void *)tp_clear<CallResult>},
    {0, nullptr},
};

void bind_callbacks(nb::module_ &m) {
    m.attr("_T") = nb::type_var("_T");
    nb::module_::import_("atexit").attr("register")(nb::cpp_function(&release_all));

    nb::class_<Callback>(m, "Callback", nb::is_generic(), nb::type_slots(callback_slots),
                         nb::sig("class Callback(typing.Generic[_T])"),
                         "브로드캐스트 콜백 등록 (SDK `CCallback` / `STEAM_CALLBACK`).\n\n"
                         "생성하면 바로 등록된다. `unregister()` 전까지 라이브러리가 객체를 붙잡아 두므로\n"
                         "변수에 보관하지 않아도 해제되지 않는다. 핸들러는 `run_callbacks()` 안에서 호출되며,\n"
                         "핸들러 예외는 `sys.unraisablehook`으로 보고된다.\n\n"
                         "    cb = Callback(LobbyEnter, on_enter)  # on_enter(data: LobbyEnter) -> None")
        .def(
            "__init__",
            [](nb::pointer_and_handle<Callback> ph, nb::handle callback_type, nb::object handler) {
                const CallbackType &t = lookup(callback_type);
                Callback *o = new (ph.p) Callback();
                o->self = ph.h.ptr();
                o->handler = std::move(handler);
                o->impl = t.make_callback(o);
                o->impl->reg();
                hold(*o);
            },
            "callback_type"_a, "handler"_a,
            nb::sig("def __init__(self, callback_type: type[_T], handler: collections.abc.Callable[[_T], None]) -> None"),
            "`callback_type` 콜백을 `handler`로 등록한다. 콜백 구조체 타입이 아니면 `TypeError`.")
        .def(
            "register",
            [](Callback &o, nb::object handler) {
                o.handler = std::move(handler);
                o.impl->reg();
                hold(o);
            },
            "handler"_a, nb::sig("def register(self, handler: collections.abc.Callable[[_T], None]) -> None"),
            "다시 등록한다 (SDK `CCallback::Register`). 이미 등록돼 있으면 해제 후 `handler`로 교체한다.")
        .def(
            "unregister",
            [](Callback &o) {
                o.impl->unreg();
                release(o);
            },
            "등록을 해제한다 (SDK `CCallback::Unregister`). 이후 라이브러리는 객체를 붙잡지 않는다.")
        .def("is_registered", [](const Callback &o) { return o.impl->registered(); }, "등록돼 있으면 `True`.");

    nb::class_<CallResult>(m, "CallResult", nb::is_generic(), nb::type_slots(call_result_slots),
                           nb::sig("class CallResult(typing.Generic[_T])"),
                           "비동기 API 호출 결과 수신 (SDK `CCallResult`).\n\n"
                           "결과는 1회만 오고, 받으면 자동으로 비활성이 된다. 활성 동안 라이브러리가 객체를\n"
                           "붙잡아 둔다. 핸들러는 `run_callbacks()` 안에서 호출되며 예외는 `sys.unraisablehook`으로 보고된다.\n\n"
                           "    cr = CallResult(LobbyCreated)\n"
                           "    cr.set(api_call, on_created)  # on_created(data: LobbyCreated, io_failure: bool) -> None")
        .def(
            "__init__",
            [](nb::pointer_and_handle<CallResult> ph, nb::handle callback_type) {
                const CallbackType &t = lookup(callback_type);
                CallResult *o = new (ph.p) CallResult();
                o->self = ph.h.ptr();
                o->impl = t.make_call_result(o);
            },
            "callback_type"_a, nb::sig("def __init__(self, callback_type: type[_T]) -> None"),
            "`callback_type` 결과를 받을 객체를 만든다(비활성). 콜백 구조체 타입이 아니면 `TypeError`.")
        .def(
            "set",
            [](CallResult &o, SteamAPICall_t api_call, nb::object handler) {
                o.handler = std::move(handler);
                o.impl->set(api_call);
                if (o.impl->active())
                    hold(o);
                else
                    release(o);
            },
            "api_call"_a, "handler"_a,
            nb::sig("def set(self, api_call: int, handler: collections.abc.Callable[[_T, bool], None]) -> None"),
            "`api_call` 결과를 `handler(data, io_failure)`로 받는다 (SDK `CCallResult::Set`).\n"
            "활성 중이면 이전 호출은 취소된다. `API_CALL_INVALID`면 비활성으로 남는다.")
        .def(
            "cancel",
            [](CallResult &o) {
                o.impl->cancel();
                release(o);
            },
            "대기 중인 결과 수신을 취소한다 (SDK `CCallResult::Cancel`).")
        .def("is_active", [](const CallResult &o) { return o.impl->active(); }, "결과를 기다리는 중이면 `True`.");
}
