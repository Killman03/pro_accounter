USD_KGS_RATE = 88.0


def kgs_to_usd(value_kgs: float) -> float:
    return round(float(value_kgs) / USD_KGS_RATE, 2)
