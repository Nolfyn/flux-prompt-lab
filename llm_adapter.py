import os
import requests
from dotenv import load_dotenv
from typing import List, Dict

load_dotenv()

LLM_API_URL = os.getenv("LLM_API_URL", "")
LLM_API_KEY = os.getenv("LLM_API_KEY", "")


def slider_to_temp(slider: int) -> float:
    """Преобразует значение слайдера (0-10) в температуру для LLM."""
    if slider <= 2:
        return 0.2
    if slider <= 5:
        return 0.5
    if slider <= 8:
        return 0.8
    return 1.0


def expand_prompt(idea: str, slider: int = 5) -> List[Dict]:
    """Запрос к LLM для расширения идеи в несколько вариантов промптов."""
    temperature = slider_to_temp(slider)
    payload = {
        "model": "deepseek/deepseek-chat-v3-0324:free",
        "prompt": (
            f"Expand the following idea into three different, descriptive,\n"
            f"real-language style prompts for Stable Diffusion: {idea}"
        ),
        "temperature": temperature,
        "max_tokens": 400,
    }
    headers = {
        "Authorization": f"Bearer {LLM_API_KEY}",
        "Content-Type": "application/json",
    }

    try:
        response = requests.post(LLM_API_URL, json=payload, headers=headers,
                                 timeout=15)
        response.raise_for_status()
        result = response.json()
        return result if isinstance(result, list) else []
    except requests.exceptions.RequestException as e:
        print(f"Ошибка запроса к LLM: {e}")
        return []
