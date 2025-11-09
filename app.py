import gradio as gr
from typing import Dict
from lora_store import load_loras
import llm_adapter
from selector import select_lora
import storage

LORAS = load_loras("loras.json")


def _inject_lora_token(prompt_text: str, lora_id: str, weight: float) -> str:
    """Вставляет токен LORA в текст промпта."""
    token = f"<lora:{lora_id}:{weight}>"
    if "{LORA_TOKEN}" in prompt_text:
        return prompt_text.replace("{LORA_TOKEN}", token)
    return f"{prompt_text} {token}"


def generate_handler(idea: str, slider: int):
    """Обработчик нажатия кнопки «Сгенерировать»."""
    variants = llm_adapter.expand_prompt(idea, slider, n_variants=3) or []
    processed = []
    for i, v in enumerate(variants):
        label = v.get("variant") or f"variant_{i + 1}"
        prompt_text = v.get("prompt", "").strip()
        neg_text = v.get("negative_prompt", "").strip()
        processed.append(
            {
                "label": label,
                "prompt": prompt_text,
                "negative_prompt": neg_text,
            }
        )

    sel = select_lora(idea, LORAS, slider=slider, llm_fallback=True)
    lora_id = sel.get("lora_id")
    lora_name = sel.get("lora_name") or ""
    weight = sel.get("weight") if sel.get("weight") is not None else ""

    labels = []
    prompt_map = {}
    neg_map = {}
    for v in processed:
        label = v["label"]
        final_prompt = v["prompt"]
        if lora_id and weight != "":
            final_prompt = _inject_lora_token(final_prompt, lora_id, weight)
        labels.append(label)
        prompt_map[label] = final_prompt
        neg_map[label] = v["negative_prompt"]
    return (
        labels,
        prompt_map,
        neg_map,
        lora_name,
        (weight if weight != "" else ""),
    )


def on_variant_select(selected_label: str, prompt_map: Dict, neg_map: Dict):
    """Возвращает выбранный промпт и negative_prompt для редактирования."""
    if not selected_label:
        return "", ""
    return prompt_map.get(selected_label, ""), neg_map.get(selected_label, "")


def save_prompt_handler(
    prompt_text: str, negative_prompt: str, lora_name: str, weight, name: str
):
    """Сохраняет промпт через storage.save_prompt."""
    record = {
        "name": name or "untitled",
        "prompt": prompt_text,
        "negative_prompt": negative_prompt,
        "lora_name": lora_name,
        "weight": weight,
    }
    saved_id = storage.save_prompt(record)
    return f"Сохранено: {saved_id}"


# --- Gradio UI ---
with gr.Blocks() as demo:
    gr.Markdown("# Flux Prompt Lab — идея → промпт + LORA")

    with gr.Row():
        with gr.Column(scale=2):
            idea_input = gr.Textbox(
                label="Ваша идея",
                placeholder="Например: киберпанк, дождливая улица с неоном",
                lines=2,
            )
            slider = gr.Slider(
                minimum=0,
                maximum=10,
                step=1,
                label="Креативность (0 = строго по идее, 10 = креативно)",
                value=5,
            )
            generate_btn = gr.Button("Сгенерировать")

            save_name = gr.Textbox(
                label="Имя для сохранения",
                placeholder="Например: Cyberpunk city v1",
            )
            save_btn = gr.Button("Сохранить промпт")

        with gr.Column(scale=3):
            gr.Markdown("### Варианты")
            variants_dropdown = gr.Dropdown(
                label="Варианты", choices=[], interactive=True
            )
            prompt_editor = gr.Textbox(label="Промпт (редактируемый)", lines=6)
            negative_editor = gr.Textbox(
                label="Negative prompt (редактируемый)", lines=3
            )
            lora_info = gr.Textbox(label="Выбранная LORA", interactive=False)
            weight_info = gr.Textbox(
                label="Рекомендованный вес", interactive=False
            )
            status = gr.Textbox(label="Статус", interactive=False)

    prompt_map_state = gr.State({})
    neg_map_state = gr.State({})

    generate_btn.click(
        fn=generate_handler,
        inputs=[idea_input, slider],
        outputs=[
            variants_dropdown,
            prompt_map_state,
            neg_map_state,
            lora_info,
            weight_info,
        ],
    )
    variants_dropdown.change(
        fn=on_variant_select,
        inputs=[variants_dropdown, prompt_map_state, neg_map_state],
        outputs=[prompt_editor, negative_editor],
    )

    save_btn.click(
        fn=save_prompt_handler,
        inputs=[
            prompt_editor,
            negative_editor,
            lora_info,
            weight_info,
            save_name,
        ],
        outputs=[status],
    )

if __name__ == "__main__":
    demo.launch()
