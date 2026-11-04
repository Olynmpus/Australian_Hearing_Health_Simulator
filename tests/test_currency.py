import pytest

from src.currency import convert_to_aud


def test_converts_usd_to_aud():
    settings = {"aud_per_unit": 1.52}

    assert convert_to_aud(100, settings) == 152.0


def test_converts_aud_to_aud():
    settings = {"aud_per_unit": 1.0}

    assert convert_to_aud(100, settings) == 100.0


def test_zero_amount_is_valid():
    settings = {"aud_per_unit": 1.52}

    assert convert_to_aud(0, settings) == 0.0


@pytest.mark.parametrize("amount", [-1, float("nan"), float("inf"), True, "100"])
def test_rejects_invalid_amount(amount):
    settings = {"aud_per_unit": 1.52}

    with pytest.raises(ValueError):
        convert_to_aud(amount, settings)


@pytest.mark.parametrize("rate", [0, -1, float("nan"), float("inf"), True, "1.52"])
def test_rejects_invalid_conversion_rate(rate):
    settings = {"aud_per_unit": rate}

    with pytest.raises(ValueError):
        convert_to_aud(100, settings)


def test_rejects_invalid_settings():
    with pytest.raises(ValueError):
        convert_to_aud(100, None)
