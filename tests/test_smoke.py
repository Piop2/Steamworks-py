def test_importable() -> None:
    import steamworks

    assert steamworks.__name__ == "steamworks"
