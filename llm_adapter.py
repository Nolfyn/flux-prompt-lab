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

    # Validate input
    if not idea or not idea.strip():
        print("Warning: Empty or whitespace-only idea provided")
        return []

    # Rate limiting
    current_time = time.time()
    time_since_last_call = current_time - _last_call_time
    if time_since_last_call < MIN_CALL_INTERVAL:
        wait_time = MIN_CALL_INTERVAL - time_since_last_call
        time.sleep(wait_time)
    _last_call_time = time.time()

    temperature = slider_to_temp(slider)
    # Strip the idea to ensure clean input
    idea = idea.strip()
    payload = {
        "model": "deepseek/deepseek-r1-0528:free",
        "messages": [
            {
                "role": "user",
                "content": (
                    f"Expand the following idea into three different, descriptive, long,\n"
                    f"real-language style prompts for Stable Diffusion (Flux model): {idea}.\n"
                    f"Only offer the three prompts in your response, without any other text."
                ),
            }
        ],
        "temperature": temperature,
        "max_tokens": 1000,
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
                message = choices[0].get("message", {})
                content = message.get("content", "")
                
                # Check for finish_reason to see if response was cut off
                finish_reason = choices[0].get("finish_reason", "")
                if finish_reason == "length":
                    print("Warning: Response was truncated due to token limit")
                
                # Strip whitespace and check if content is actually present
                content = content.strip() if content else ""
                if content:
                    # Return as a list with a dict to match expected format
                    return [{"prompt": content}]
                else:
                    print(f"Warning: Empty content in response. Finish reason: {finish_reason}")
                    print(f"Response structure: {result}")
                    return []
            else:
                print(f"Warning: Empty choices array in response: {result}")
                return []
        
        # Fallback for other formats
        if isinstance(result, list):
            return result
        
        # If we get here, the response format is unexpected
        print(f"Warning: Unexpected response format: {type(result)}")
        print(f"Response: {result}")
        return []
    except requests.exceptions.RequestException as e:
        print(f"Ошибка запроса к LLM: {e}")
        if hasattr(e, 'response') and e.response is not None:
            try:
                error_detail = e.response.json()
                print(f"Error details: {error_detail}")
            except:
                print(f"Error response text: {e.response.text}")
        return []
    except Exception as e:
        print(f"Unexpected error in expand_prompt: {e}")
        return []
