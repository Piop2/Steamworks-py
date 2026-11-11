def test_importable() -> None:
    import steamworks

    assert steamworks.__name__ == "steamworks"


def test_native_importable() -> None:
    from steamworks import _native

    assert _native.__name__ == "steamworks._native"
