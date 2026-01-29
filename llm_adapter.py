import os
import requests
import time
from dotenv import load_dotenv
from typing import List, Dict

load_dotenv()

LLM_API_URL = os.getenv("LLM_API_URL", "")
LLM_API_KEY = os.getenv("LLM_API_KEY", "")

# Rate limiting
MIN_CALL_INTERVAL = float(os.getenv("MIN_CALL_INTERVAL", "2.0"))
_last_call_time = 0.0


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
    global _last_call_time

    # Rate limiting
    current_time = time.time()
    time_since_last_call = current_time - _last_call_time
    if time_since_last_call < MIN_CALL_INTERVAL:
        wait_time = MIN_CALL_INTERVAL - time_since_last_call
        time.sleep(wait_time)
    _last_call_time = time.time()

    temperature = slider_to_temp(slider)
    payload = {
        "model": "deepseek/deepseek-r1-0528:free",
        "messages": [
            {
                "role": "user",
                "content": (
                    f"Expand the following idea into three different, descriptive,\n"
                    f"real-language style prompts for Stable Diffusion: {idea}"
                ),
            }
        ],
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
        
        # OpenRouter returns OpenAI-compatible format with 'choices' array
        if isinstance(result, dict) and "choices" in result:
            choices = result["choices"]
            if choices and len(choices) > 0:
                # Extract content from the first choice
                content = choices[0].get("message", {}).get("content", "")
                # Return as a list with a dict to match expected format
                return [{"prompt": content}] if content else []
        
        # Fallback for other formats
        return result if isinstance(result, list) else []
    except requests.exceptions.RequestException as e:
        print(f"Ошибка запроса к LLM: {e}")
        return []
