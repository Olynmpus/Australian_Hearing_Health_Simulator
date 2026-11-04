"""Currency conversion using experiment-defined exchange rates."""
import math

def convert_to_aud(amount, currency_conversion):
    """Convert an amount in the source currency into AUD."""

    if (
        isinstance(amount, bool)
        or not isinstance(amount, (int, float))
        or not math.isfinite(amount)
        or amount < 0
    ):
        raise ValueError("Amount must be a non-negative number.")

    if not isinstance(currency_conversion, dict):
        raise ValueError("Currency conversion settings must be a dictionary.")

    rate = currency_conversion.get("aud_per_unit")

    if (
        isinstance(rate, bool)
        or not isinstance(rate, (int, float))
        or not math.isfinite(rate)
        or rate <= 0
    ):
        raise ValueError("Conversion rate must be a positive number.")

    return amount * rate
