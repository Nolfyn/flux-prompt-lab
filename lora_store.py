import json
from typing import List, Dict


def load_loras(path: str = 'loras.json'):
    """Загружает LORA из файла loras.json."""

    with open(path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    for item in data:
        item['tags'] = [t.lower() for t in item.get('tags', [])]
    return data


def list_loras(loras: List[Dict]):
    """Возвращает название всех LORA."""

    return [lora['name'] for lora in loras]


def get_lora(loras: List[Dict], lora_id: str):
    """Получает словарь LORA по id."""

    for lora in loras:
        if lora['id'] == lora_id:
            return lora
    return None


def search_loras_by_tags(loras: List[Dict], idea_tags: List[str]):
    """Поиск LORA по тегам."""

    matched_loras = []
    for lora in loras:
        lora_tags = set(lora['tags'])
        common_tags = lora_tags.intersection(set(idea_tags))
        if common_tags:
            matched_loras.append(lora)
    return matched_loras
