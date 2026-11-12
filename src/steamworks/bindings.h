#pragma once

#include <nanobind/nanobind.h>

void bind_types(nanobind::module_ &m);
void bind_lifecycle(nanobind::module_ &m);
void bind_callbacks(nanobind::module_ &m);
void bind_matchmaking(nanobind::module_ &m);
void bind_user(nanobind::module_ &m);
void bind_friends(nanobind::module_ &m);
void bind_networking_sockets(nanobind::module_ &m);
void bind_networking_utils(nanobind::module_ &m);
