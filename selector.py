import re
from typing import List, Dict, Optional

from utils import slider_to_weight_hint

_TOKEN_RE = re.compile(r"[a-z0-9\-]+")


def _tokens_from_text(text: str) -> List[str]:
    """Перерабатывает входящий промпт в нормализированные токены."""

    return list(set(_TOKEN_RE.findall(text.lower())))


def select_lora_by_tags(idea_text: str, loras: List[Dict]) -> Optional[Dict]:
    """Выбор LORA на основании тегов."""

    tokens = set(_tokens_from_text(idea_text))
    best_lora = None
    best_score = 0

    for lora in loras:
        lora_tags = set(t.lower() for t in lora.get("tags", []))
        score = len(tokens & lora_tags)
        if score > best_score:
            best_score = score
            best_lora = lora

    return best_lora


def select_lora(
    idea_text: str,
    loras: List[Dict],
    slider: int = 5,
    llm_fallback: bool = True,
) -> Dict:
    """Основная функция выбора LORA."""

    # Вариант 1: выбор на основании тегов.
    best_lora = select_lora_by_tags(idea_text, loras)
    if best_lora:
        weight = slider_to_weight_hint(
            slider, best_lora.get("default_weight", 0.5)
        )
        return {
            "lora_id": best_lora.get("id"),
            "lora_name": best_lora.get("name"),
            "weight": round(weight, 2),
            "method": "tags",
            "score": len(best_lora.get("tags", [])),
        }

    # Вариант 2: выбор при помощи LLM.
    if llm_fallback:
        # Поменять на корректный вызов
        selected_lora = {
            "selected_lora": "aidmaFluxProUltra-FLUX-v0.1",
            "suggested_weight": 0.5,
        }
        lora_id = selected_lora.get("selected_lora")
        suggested_weight = selected_lora.get("suggested_weight", 0.5)
        matched_lora = next(
            (lora for lora in loras if lora["id"] == lora_id), None
        )
        if matched_lora:
            return {
                "lora_id": matched_lora["id"],
                "lora_name": matched_lora["name"],
                "weight": round(suggested_weight, 2),
                "method": "llm",
                "score": 0,
            }
    return {
        "lora_id": None,
        "lora_name": None,
        "weight": None,
        "method": "none",
        "score": 0,
    }
