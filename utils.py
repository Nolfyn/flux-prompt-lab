def slider_to_weight_hint(slider: int, default_weight: float) -> float:
    """Привязка слайдера креативности к весу LORA."""

    if slider <= 2:
        weight = default_weight + 0.3
    elif slider <= 5:
        weight = default_weight + 0.1
    elif slider <= 8:
        weight = default_weight - 0.1
    else:
        weight = default_weight - 0.3
    weight = max(0.05, min(0.95, weight))
    return round(weight, 2)
