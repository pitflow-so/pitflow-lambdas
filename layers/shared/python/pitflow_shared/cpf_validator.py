import re


def validate_cpf(cpf: str) -> bool:
    if not cpf:
        return False

    digits = re.sub(r"\D", "", cpf)

    if len(digits) != 11:
        return False

    if digits == digits[0] * 11:
        return False

    first_digit = _calculate_digit(digits[:9], 10)
    second_digit = _calculate_digit(digits[:9] + str(first_digit), 11)

    return digits[-2:] == f"{first_digit}{second_digit}"


def _calculate_digit(digits: str, initial_weight: int) -> int:
    total = sum(int(digit) * weight for digit, weight in zip(digits, range(initial_weight, 1, -1)))
    remainder = (total * 10) % 11

    if remainder == 10:
        return 0

    return remainder
