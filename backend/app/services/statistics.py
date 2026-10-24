PERCENT_SCALE = 100
MEDIAN_PERCENT = 50
LOWER_QUARTILE_PERCENT = 25
UPPER_QUARTILE_PERCENT = 75


def round_half_even_div(numerator: int, denominator: int) -> int:
    if denominator <= 0:
        raise ValueError("Denominator must be positive.")
    quotient, remainder = divmod(numerator, denominator)
    doubled_remainder = remainder * 2
    if doubled_remainder > denominator or (doubled_remainder == denominator and quotient % 2):
        return quotient + 1
    return quotient


def percentile(sorted_values: list[int], percent: int) -> int:
    if not sorted_values:
        raise ValueError("Percentiles require at least one value.")
    if not 0 <= percent <= PERCENT_SCALE:
        raise ValueError("Percent must be between 0 and 100.")
    final_index = len(sorted_values) - 1
    index, remainder = divmod(percent * final_index, PERCENT_SCALE)
    lower = sorted_values[index]
    upper = sorted_values[min(index + 1, final_index)]
    return round_half_even_div(
        lower * PERCENT_SCALE + (upper - lower) * remainder,
        PERCENT_SCALE,
    )


def median(sorted_values: list[int]) -> int:
    return percentile(sorted_values, MEDIAN_PERCENT)
