from property_sim.main import (
    main,
)


def test_main_returns_none() -> None:
    result = main()
    assert result is None
